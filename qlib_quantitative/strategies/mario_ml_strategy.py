#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Mario机器学习策略 - Abu框架版本
基于原有Mario机器学习中小板增强策略移植到Abu框架

核心特点：
1. 使用LightGBM进行股票预测和选股
2. 基于多因子模型的量化选股
3. 月度调仓策略
4. 特征选择和相关性过滤
5. 中小板股票池
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import logging
from pathlib import Path
import pickle
import warnings
from collections import defaultdict
from dataclasses import dataclass

# 机器学习相关库
import lightgbm as lgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, 
    f1_score, roc_auc_score, precision_recall_curve, auc
)

# Abu框架导入
import abupy as abu
from abupy import AbuFactorBuyBase, AbuFactorSellBase
from abupy import AbuBenchmark, AbuCapital, AbuKLManager
from abupy import AbuMetricsBase

# 本地导入
from ..core.strategy_base import AbuStrategyBase
from ..core.data_adapter import AbuDataAdapter

warnings.filterwarnings("ignore")


@dataclass
class MarioMLConfig:
    """Mario机器学习策略配置"""
    # 基础配置
    initial_capital: float = 1000000  # 初始资金
    stock_num: int = 20              # 持仓股票数量
    rebalance_freq: str = 'monthly'  # 调仓频率
    
    # 模型参数
    correlation_threshold: float = 0.6  # 因子相关性阈值
    model_type: str = 'lightgbm'       # 模型类型
    feature_selection: bool = True      # 是否进行特征选择
    lookback_months: int = 12          # 训练数据回望月数
    min_samples: int = 1000            # 最小训练样本数
    
    # LightGBM参数
    lgb_params: Dict = None
    
    def __post_init__(self):
        if self.lgb_params is None:
            self.lgb_params = {
                'objective': 'binary',
                'metric': 'binary_logloss',
                'boosting_type': 'gbdt',
                'verbose': -1,
                'num_boost_round': 200,
                'learning_rate': 0.1,
                'num_leaves': 31,
                'feature_fraction': 0.9,
                'bagging_fraction': 0.8,
                'bagging_freq': 5,
                'min_child_samples': 20
            }


class MarioMLBuyFactor(AbuFactorBuyBase):
    """Mario机器学习买入因子"""
    
    def __init__(self, config: MarioMLConfig = None):
        super().__init__()
        self.config = config or MarioMLConfig()
        self.data_adapter = AbuDataAdapter()
        
        # 策略状态
        self.model = None
        self.selected_features = []
        self.last_rebalance_date = None
        self.current_positions = {}
        self.target_stocks = []
        
        # 因子列表
        self.factor_names = [
            'market_cap', 'pe', 'pb', 'ps', 'pe_ttm', 'ps_ttm',
            'turnover_rate', 'volume_ratio', 'pct_chg', 'vol', 'amount',
            'rsi_6', 'rsi_12', 'rsi_24', 'macd_dif', 'macd_dea', 'macd',
            'kdj_k', 'kdj_d', 'boll_upper', 'boll_lower', 'boll_mid',
            'ma_5', 'ma_10', 'ma_20', 'ma_60', 'circ_mv', 'total_share',
            'float_share', 'close', 'high', 'low', 'roe', 'roa', 'eps',
            'bps', 'revenue_ps', 'ocfps', 'gross_margin', 'profit_margin',
            'debt_ratio', 'asset_turnover', 'netprofit_yoy', 'revenue_yoy'
        ]
        
        # 模型文件路径
        self.model_path = Path(__file__).parent.parent / 'models' / 'mario_ml_model.pkl'
        self.model_path.parent.mkdir(exist_ok=True)
        
    def _init_self(self, **kwargs):
        """初始化买入因子"""
        # 获取股票代码
        self.symbol = self.kl_pd.name if hasattr(self.kl_pd, 'name') else 'unknown'
        
        # 尝试加载已训练的模型
        self._load_model()
        
    def _load_model(self) -> bool:
        """加载模型"""
        try:
            if not self.model_path.exists():
                return False
            
            with open(self.model_path, 'rb') as f:
                model_data = pickle.load(f)
            
            self.model = model_data['model']
            self.selected_features = model_data['selected_features']
            
            return True
            
        except Exception as e:
            return False
            
    def _save_model(self):
        """保存模型"""
        try:
            model_data = {
                'model': self.model,
                'selected_features': self.selected_features,
                'config': self.config
            }
            
            with open(self.model_path, 'wb') as f:
                pickle.dump(model_data, f)
                
        except Exception as e:
            pass
            
    def prepare_training_data(self, end_date: datetime) -> pd.DataFrame:
        """准备训练数据"""
        # 训练数据时间范围：2020-2024年
        start_date = datetime(2020, 1, 1)
        train_end_date = datetime(2024, 6, 30)
        
        # 生成月末日期序列
        date_list = self._generate_month_end_dates(start_date, train_end_date)
        
        all_training_data = []
        
        for i, date in enumerate(date_list[:-1]):
            try:
                # 获取中小板股票池（使用数据适配器）
                stock_list = self.data_adapter.get_stock_list(date)
                
                if len(stock_list) < 100:
                    continue
                
                # 随机采样500只股票
                import random
                if len(stock_list) > 500:
                    stock_list = random.sample(stock_list, 500)
                
                # 获取因子数据
                factor_data = self.data_adapter.get_factor_data(
                    stock_list, self.factor_names, date
                )
                
                # 构建因子DataFrame
                df_factors = self._build_factor_dataframe(factor_data, stock_list)
                
                if df_factors.empty:
                    continue
                
                # 计算下月收益率作为标签
                next_date = date_list[i + 1]
                returns = self._calculate_monthly_returns(stock_list, date, next_date)
                
                if returns.empty:
                    continue
                
                # 合并因子和收益率数据
                df_combined = df_factors.merge(
                    returns, left_index=True, right_index=True, how='inner'
                )
                
                # 构建标签：以收益率中位数为分界
                median_return = df_combined['monthly_return'].median()
                df_combined['label'] = (df_combined['monthly_return'] >= median_return).astype(int)
                
                # 去除收益率列，保留因子和标签
                df_combined = df_combined.drop(columns=['monthly_return'])
                
                all_training_data.append(df_combined)
                
            except Exception as e:
                continue
        
        if not all_training_data:
            return pd.DataFrame()
        
        # 合并所有数据
        training_df = pd.concat(all_training_data, ignore_index=True)
        
        return training_df
        
    def _generate_month_end_dates(self, start_date: datetime, end_date: datetime) -> List[datetime]:
        """生成月末日期序列"""
        dates = []
        current = start_date.replace(day=1)  # 月初
        
        while current <= end_date:
            # 获取月末日期
            if current.month == 12:
                next_month = current.replace(year=current.year + 1, month=1)
            else:
                next_month = current.replace(month=current.month + 1)
            
            month_end = next_month - timedelta(days=1)
            
            if month_end <= end_date:
                dates.append(month_end)
            
            current = next_month
        
        return dates
        
    def _build_factor_dataframe(self, factor_data: Dict[str, pd.DataFrame], 
                               stock_list: List[str]) -> pd.DataFrame:
        """构建因子DataFrame"""
        factor_df = pd.DataFrame(index=stock_list)
        
        for factor_name, df in factor_data.items():
            if not df.empty and len(df.columns) > 0:
                # 取第一行数据（日期维度）
                factor_values = df.iloc[0, :]
                factor_df[factor_name] = factor_values
        
        # 处理缺失值 - 使用中位数填充
        for col in factor_df.columns:
            if factor_df[col].isnull().sum() > 0:
                median_val = factor_df[col].median()
                if not pd.isna(median_val):
                    factor_df[col].fillna(median_val, inplace=True)
        
        # 删除仍然包含过多缺失值的行
        factor_df = factor_df.dropna(thresh=len(factor_df.columns) * 0.6)
        
        return factor_df
        
    def _calculate_monthly_returns(self, stock_list: List[str], 
                                  start_date: datetime, end_date: datetime) -> pd.DataFrame:
        """计算月度收益率"""
        returns_data = []
        
        for stock_code in stock_list:
            try:
                # 获取价格数据
                price_data = self.data_adapter.get_price_data(
                    stock_code, start_date, end_date + timedelta(days=5)
                )
                
                if price_data.empty:
                    continue
                
                # 计算收益率
                start_price = price_data['close'].iloc[0]
                end_price = price_data['close'].iloc[-1]
                
                if start_price and end_price and start_price > 0:
                    monthly_return = (end_price / start_price) - 1
                    returns_data.append({
                        'stock_code': stock_code,
                        'monthly_return': monthly_return
                    })
                    
            except Exception as e:
                continue
        
        if not returns_data:
            return pd.DataFrame()
        
        returns_df = pd.DataFrame(returns_data)
        returns_df.set_index('stock_code', inplace=True)
        
        return returns_df
        
    def feature_selection(self, df: pd.DataFrame) -> List[str]:
        """特征选择"""
        if 'label' not in df.columns:
            return list(df.columns)
        
        # 分离特征和标签
        features = [col for col in df.columns if col != 'label']
        feature_df = df[features]
        
        # 计算相关系数矩阵
        corr_matrix = feature_df.corr()
        
        # 创建图结构存储高度相关的特征对
        graph = defaultdict(list)
        threshold = self.config.correlation_threshold
        
        # 计算缺失值数量
        missing_counts = feature_df.isnull().sum().to_dict()
        
        # 遍历上三角矩阵找到高度相关的特征对
        n = len(features)
        for i in range(n):
            for j in range(i + 1, n):
                col1, col2 = features[i], features[j]
                corr_value = corr_matrix.iloc[i, j]
                
                if not pd.isna(corr_value) and abs(corr_value) > threshold:
                    graph[col1].append(col2)
                    graph[col2].append(col1)
        
        # 使用DFS找到连通分量
        visited = set()
        components = []
        
        def dfs(node, comp):
            visited.add(node)
            comp.append(node)
            for neighbor in graph[node]:
                if neighbor not in visited:
                    dfs(neighbor, comp)
        
        for feature in features:
            if feature not in visited:
                comp = []
                dfs(feature, comp)
                components.append(comp)
        
        # 处理每个连通分量：保留缺失值最少的特征
        selected_features = []
        
        for comp in components:
            if len(comp) == 1:
                selected_features.append(comp[0])
            else:
                comp_sorted = sorted(comp, key=lambda x: (missing_counts[x], x))
                selected_features.append(comp_sorted[0])
        
        return selected_features
        
    def train_model(self, df: pd.DataFrame) -> bool:
        """训练机器学习模型"""
        if df.empty or 'label' not in df.columns:
            return False
        
        # 特征选择
        if self.config.feature_selection:
            self.selected_features = self.feature_selection(df)
        else:
            self.selected_features = [col for col in df.columns if col != 'label']
        
        # 准备训练数据
        X = df[self.selected_features]
        y = df['label']
        
        # 转换数据类型
        for col in X.columns:
            X[col] = pd.to_numeric(X[col], errors='coerce')
        
        # 删除包含NaN的行
        valid_idx = ~(X.isnull().any(axis=1) | y.isnull())
        X = X[valid_idx]
        y = y[valid_idx]
        
        if len(X) < self.config.min_samples:
            return False
        
        try:
            # 创建LightGBM数据集
            lgb_train = lgb.Dataset(X, label=y)
            
            # 训练模型
            self.model = lgb.train(
                self.config.lgb_params,
                lgb_train,
                num_boost_round=self.config.lgb_params['num_boost_round']
            )
            
            # 保存模型
            self._save_model()
            
            return True
            
        except Exception as e:
            return False
            
    def get_stock_selection(self, date: datetime) -> List[str]:
        """获取股票选择"""
        try:
            if self.model is None:
                return []
            
            # 获取候选股票池
            stock_list = self.data_adapter.get_stock_list(date)
            
            if len(stock_list) < 20:
                return []
            
            # 获取因子数据
            factor_data = self.data_adapter.get_factor_data(
                stock_list, self.factor_names, date
            )
            
            # 构建预测数据
            df_factors = self._build_factor_dataframe(factor_data, stock_list)
            
            if df_factors.empty:
                return []
            
            # 确保特征对齐
            missing_features = [f for f in self.selected_features if f not in df_factors.columns]
            if missing_features:
                for feature in missing_features:
                    df_factors[feature] = 0
            
            # 选择模型特征
            X = df_factors[self.selected_features]
            
            # 转换数据类型
            for col in X.columns:
                X[col] = pd.to_numeric(X[col], errors='coerce')
            
            # 删除包含NaN的行
            valid_idx = ~X.isnull().any(axis=1)
            X_valid = X[valid_idx]
            valid_stocks = X_valid.index.tolist()
            
            if len(X_valid) == 0:
                return []
            
            # 模型预测
            predictions = self.model.predict(X_valid)
            
            # 创建预测结果DataFrame
            result_df = pd.DataFrame({
                'stock_code': valid_stocks,
                'prediction_score': predictions
            })
            
            # 按预测分数排序，选择Top N只股票
            result_df = result_df.sort_values('prediction_score', ascending=False)
            selected_stocks = result_df.head(self.config.stock_num)['stock_code'].tolist()
            
            return selected_stocks
            
        except Exception as e:
            return []
            
    def should_rebalance(self, date: datetime) -> bool:
        """判断是否需要调仓"""
        if self.last_rebalance_date is None:
            return True
        
        # 月度调仓
        if self.config.rebalance_freq == 'monthly':
            return date.month != self.last_rebalance_date.month
        
        return False
        
    def fit_month(self, today):
        """Abu框架买入信号判断"""
        if self.today_ind < 30:  # 需要足够的历史数据
            return None
            
        try:
            current_date = self.kl_pd.index[self.today_ind]
            
            # 检查是否需要调仓
            if not self.should_rebalance(current_date):
                return None
                
            # 获取目标股票池
            target_stocks = self.get_stock_selection(current_date)
            
            if not target_stocks:
                return None
                
            # 检查当前股票是否在目标股票池中
            if self.symbol in target_stocks:
                self.last_rebalance_date = current_date
                return self.buy_today()
                
            return None
            
        except Exception as e:
            return None


class MarioMLSellFactor(AbuFactorSellBase):
    """Mario机器学习卖出因子"""
    
    def __init__(self, config: MarioMLConfig = None):
        super().__init__()
        self.config = config or MarioMLConfig()
        
    def _init_self(self, **kwargs):
        """初始化卖出因子"""
        self.symbol = self.kl_pd.name if hasattr(self.kl_pd, 'name') else 'unknown'
        
    def fit_month(self, today):
        """Abu框架卖出信号判断"""
        if not self.read_fit_month(today):
            return None
            
        try:
            current_date = self.kl_pd.index[self.today_ind]
            
            # 月度调仓时卖出（由买入因子控制）
            # 这里主要处理风险控制卖出
            
            # 简单的止损逻辑
            if hasattr(self, 'buy_price') and self.buy_price > 0:
                current_price = self.kl_pd.iloc[self.today_ind]['close']
                pnl_ratio = (current_price - self.buy_price) / self.buy_price
                
                # 止损：亏损超过15%
                if pnl_ratio <= -0.15:
                    return self.sell_today()
                    
                # 止盈：盈利超过30%
                if pnl_ratio >= 0.30:
                    return self.sell_today()
                    
            return None
            
        except Exception as e:
            return None


class AbuMarioMLStrategy(AbuStrategyBase):
    """Abu框架Mario机器学习策略"""
    
    def __init__(self, config: MarioMLConfig = None):
        self.config = config or MarioMLConfig()
        super().__init__()
        
    def setup_buy_factors(self):
        """设置买入因子"""
        return [MarioMLBuyFactor(self.config)]
        
    def setup_sell_factors(self):
        """设置卖出因子"""
        return [MarioMLSellFactor(self.config)]
        
    def setup_position_factors(self):
        """设置仓位管理因子"""
        # 使用等权重仓位管理
        from abupy import AbuFactorAtrNStop, AbuFactorPreAtrNStop
        return [
            AbuFactorAtrNStop(stop_loss_n=0.15, stop_win_n=0.30),
            AbuFactorPreAtrNStop(pre_atr_n=1.0)
        ]
        
    def get_strategy_name(self) -> str:
        """获取策略名称"""
        return "Mario机器学习策略"
        
    def get_strategy_description(self) -> str:
        """获取策略描述"""
        return "基于LightGBM机器学习模型的量化选股策略，使用多因子模型进行股票预测和选股"
        
    def train_strategy_model(self, end_date: datetime = None):
        """训练策略模型"""
        if end_date is None:
            end_date = datetime.now()
            
        # 创建买入因子实例进行训练
        buy_factor = MarioMLBuyFactor(self.config)
        
        # 准备训练数据
        training_data = buy_factor.prepare_training_data(end_date)
        
        if not training_data.empty:
            # 训练模型
            success = buy_factor.train_model(training_data)
            return success
            
        return False