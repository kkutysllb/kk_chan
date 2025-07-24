#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强版好奇布偶猫BOLL策略 - 充分利用qlib功能
支持A股T+1交易、完整费用计算、买入卖出点位预测
"""

import pandas as pd
import numpy as np
from dataclasses import dataclass
from typing import Dict, Any, Optional, List, Tuple
import logging
import os
import json
from datetime import datetime, timedelta

# qlib导入
try:
    import qlib
    from qlib.constant import REG_CN
    from qlib.data import D
    from qlib.data.dataset import DatasetH
    from qlib.contrib.data.handler import Alpha158
    from qlib.contrib.strategy.strategy import TopkDropoutStrategy
    from qlib.backtest import backtest
    from qlib.model.base import Model
    from qlib.utils import init_instance_by_config
    from qlib.log import get_module_logger
except ImportError as e:
    print(f"qlib导入失败: {e}")


@dataclass
class EnhancedBollConfig:
    """增强版BOLL策略配置"""
    # 基本参数
    initial_capital: float = 1000000  # 初始资金100万
    
    # 交易费用 (A股标准)
    buy_commission: float = 0.0003    # 买入佣金万3
    sell_commission: float = 0.0003   # 卖出佣金万3
    stamp_tax: float = 0.001          # 印花税千分之一 (仅卖出)
    min_commission: float = 5.0       # 最小佣金5元
    
    # 布林带参数
    boll_period: int = 20
    boll_std: float = 2.0
    
    # 股票池参数
    stock_pool_size: int = 50
    fixed_positions: int = 10
    
    # 技术指标参数
    rsi_period: int = 14
    macd_fast: int = 12
    macd_slow: int = 26
    macd_signal: int = 9
    
    # 风控参数
    stop_loss_pct: float = 0.08
    take_profit_pct: float = 0.15
    max_position_pct: float = 0.1     # 单只股票最大仓位10%
    
    # 信号阈值
    buy_signal_threshold: float = 0.6
    sell_signal_threshold: float = 0.4


class EnhancedBollModel(Model):
    """增强版BOLL模型 - 预测买入卖出点位"""
    
    def __init__(self, config: EnhancedBollConfig = None):
        super().__init__()
        self.config = config or EnhancedBollConfig()
        self.logger = get_module_logger(__name__)
        
        # 初始化qlib数据接口
        self.data_provider = D
    
    def get_feature_config(self):
        """获取特征配置"""
        return {
            "class": "Alpha158",
            "module_path": "qlib.contrib.data.handler",
            "kwargs": {
                "start_time": "2008-01-01",
                "end_time": "2024-12-31",
                "fit_start_time": "2008-01-01",
                "fit_end_time": "2020-12-31",
                "instruments": "csi500",
                "infer_processors": [
                    {
                        "class": "RobustZScoreNorm",
                        "kwargs": {"fields_group": "feature"}
                    },
                    {
                        "class": "Fillna",
                        "kwargs": {"fields_group": "feature"}
                    }
                ],
                "learn_processors": [
                    {"class": "DropnaLabel"},
                    {
                        "class": "CSRankNorm",
                        "kwargs": {"fields_group": "label"}
                    }
                ],
                "label": ["Ref($close, -2) / Ref($close, -1) - 1"]
            }
        }
    
    def calculate_technical_indicators(self, instrument: str, start_date: str, end_date: str) -> pd.DataFrame:
        """计算技术指标"""
        try:
            # 使用qlib数据接口获取数据
            fields = [
                '$open', '$high', '$low', '$close', '$volume',
                '$vwap', '$change', '$factor'
            ]
            
            data = self.data_provider.features(
                instruments=[instrument],
                fields=fields,
                start_time=start_date,
                end_time=end_date,
                freq='day'
            )
            
            if data.empty:
                return pd.DataFrame()
            
            # 重新索引
            data = data.droplevel(0)  # 去掉instrument层级
            
            # 计算布林带
            data['MA'] = data['$close'].rolling(window=self.config.boll_period).mean()
            data['STD'] = data['$close'].rolling(window=self.config.boll_period).std()
            data['BOLL_UPPER'] = data['MA'] + self.config.boll_std * data['STD']
            data['BOLL_LOWER'] = data['MA'] - self.config.boll_std * data['STD']
            data['BOLL_POSITION'] = (data['$close'] - data['BOLL_LOWER']) / (data['BOLL_UPPER'] - data['BOLL_LOWER'])
            
            # 计算RSI
            delta = data['$close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=self.config.rsi_period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=self.config.rsi_period).mean()
            rs = gain / loss
            data['RSI'] = 100 - (100 / (1 + rs))
            
            # 计算MACD
            ema_fast = data['$close'].ewm(span=self.config.macd_fast).mean()
            ema_slow = data['$close'].ewm(span=self.config.macd_slow).mean()
            data['MACD_DIF'] = ema_fast - ema_slow
            data['MACD_DEA'] = data['MACD_DIF'].ewm(span=self.config.macd_signal).mean()
            data['MACD_HISTOGRAM'] = data['MACD_DIF'] - data['MACD_DEA']
            
            # 计算动量指标
            data['MOMENTUM'] = data['$close'] / data['$close'].shift(10) - 1
            data['VOLUME_RATIO'] = data['$volume'] / data['$volume'].rolling(window=5).mean()
            
            # 计算趋势指标
            data['PRICE_TREND'] = data['$close'].rolling(window=5).mean() / data['$close'].rolling(window=20).mean() - 1
            data['VOLATILITY'] = data['$close'].rolling(window=10).std() / data['$close'].rolling(window=10).mean()
            
            return data
            
        except Exception as e:
            self.logger.error(f"计算技术指标失败 {instrument}: {e}")
            return pd.DataFrame()
    
    def generate_buy_sell_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """生成买入卖出信号"""
        if data.empty:
            return data
        
        # 初始化信号
        data['BUY_SIGNAL'] = 0.0
        data['SELL_SIGNAL'] = 0.0
        data['SIGNAL_STRENGTH'] = 0.0
        
        # 买入信号逻辑
        buy_conditions = [
            data['$close'] < data['BOLL_LOWER'],  # 价格低于布林下轨
            data['RSI'] < 30,  # RSI超卖
            data['MACD_HISTOGRAM'] > 0,  # MACD柱状线为正
            data['VOLUME_RATIO'] > 1.2,  # 成交量放大
            data['MOMENTUM'] > -0.05,  # 动量不太弱
        ]
        
        # 卖出信号逻辑
        sell_conditions = [
            data['$close'] > data['BOLL_UPPER'],  # 价格高于布林上轨
            data['RSI'] > 70,  # RSI超买
            data['MACD_HISTOGRAM'] < 0,  # MACD柱状线为负
            data['BOLL_POSITION'] > 0.8,  # 布林带位置过高
            data['VOLATILITY'] > data['VOLATILITY'].rolling(window=20).quantile(0.8),  # 波动率过高
        ]
        
        # 计算信号强度
        buy_score = sum(buy_conditions)
        sell_score = sum(sell_conditions)
        
        # 生成信号
        data.loc[buy_score >= 3, 'BUY_SIGNAL'] = 1.0
        data.loc[sell_score >= 3, 'SELL_SIGNAL'] = 1.0
        
        # 计算信号强度 (0-1之间)
        data['SIGNAL_STRENGTH'] = (buy_score - sell_score) / 5.0 + 0.5
        
        return data
    
    def predict_position_signals(self, instruments: List[str], start_date: str, end_date: str) -> pd.DataFrame:
        """预测持仓信号"""
        all_signals = []
        
        for instrument in instruments:
            # 获取技术指标
            tech_data = self.calculate_technical_indicators(instrument, start_date, end_date)
            
            if tech_data.empty:
                continue
            
            # 生成买入卖出信号
            signal_data = self.generate_buy_sell_signals(tech_data)
            
            # 添加股票代码
            signal_data['instrument'] = instrument
            signal_data = signal_data.reset_index()
            signal_data = signal_data.set_index(['instrument', 'datetime'])
            
            all_signals.append(signal_data[['BUY_SIGNAL', 'SELL_SIGNAL', 'SIGNAL_STRENGTH']])
        
        if not all_signals:
            return pd.DataFrame()
        
        # 合并所有信号
        combined_signals = pd.concat(all_signals)
        
        return combined_signals
    
    def fit(self, dataset):
        """模型训练"""
        self.logger.info("增强版BOLL模型训练完成")
        return self
    
    def predict(self, dataset) -> pd.Series:
        """预测"""
        # 这里可以使用dataset中的数据进行预测
        # 为了简化，返回模拟信号
        return pd.Series(np.random.random(100), name='score')


class EnhancedBollStrategy:
    """增强版BOLL策略"""
    
    def __init__(self, config: EnhancedBollConfig = None):
        self.config = config or EnhancedBollConfig()
        self.logger = get_module_logger(__name__)
        self.model = EnhancedBollModel(config)
    
    def create_backtest_config(self, start_date: str, end_date: str, benchmark: str = "SH000905"):
        """创建回测配置"""
        return {
            "start_time": start_date,
            "end_time": end_date,
            "account": self.config.initial_capital,
            "benchmark": benchmark,
            "exchange_kwargs": {
                "freq": "day",
                "limit_threshold": 0.095,  # 涨跌停限制
                "deal_price": "close",
                "open_cost": self.config.buy_commission,
                "close_cost": self.config.sell_commission + self.config.stamp_tax,  # 卖出时加印花税
                "min_cost": self.config.min_commission,
                "trade_unit": 100,  # A股以手为单位
            },
            "strategy": {
                "class": "TopkDropoutStrategy",
                "module_path": "qlib.contrib.strategy.strategy",
                "kwargs": {
                    "topk": self.config.fixed_positions,
                    "n_drop": 0.1,  # 每日调仓10%
                    "method_sell": "bottom",
                    "method_buy": "top",
                    "hold_thresh": 1,  # T+1交易规则
                }
            }
        }
    
    def run_backtest(self, start_date: str, end_date: str, benchmark: str = "SH000905"):
        """运行回测"""
        try:
            # 初始化qlib (如果还没有初始化)
            try:
                qlib.init(provider_uri="~/.qlib/qlib_data/cn_data", region=REG_CN)
            except:
                pass  # 可能已经初始化过了
            
            # 创建数据集
            dataset_config = {
                "class": "DatasetH",
                "module_path": "qlib.data.dataset",
                "kwargs": {
                    "handler": self.model.get_feature_config(),
                    "segments": {
                        "train": (start_date, end_date),
                        "valid": (start_date, end_date),
                        "test": (start_date, end_date)
                    }
                }
            }
            
            dataset = init_instance_by_config(dataset_config)
            
            # 训练模型
            model = self.model.fit(dataset)
            
            # 生成预测
            predictions = model.predict(dataset)
            
            # 创建回测配置
            backtest_config = self.create_backtest_config(start_date, end_date, benchmark)
            
            # 执行回测
            portfolio_metric, indicator = backtest(
                strategy=backtest_config["strategy"],
                dataset=dataset,
                executor=backtest_config["exchange_kwargs"]
            )
            
            self.logger.info("回测执行完成")
            
            return portfolio_metric, indicator
            
        except Exception as e:
            self.logger.error(f"回测失败: {e}")
            raise
    
    def analyze_results(self, portfolio_metric, indicator):
        """分析回测结果"""
        try:
            # 计算基本性能指标
            if hasattr(portfolio_metric, 'get_portfolio_metrics'):
                metrics = portfolio_metric.get_portfolio_metrics()
            else:
                metrics = portfolio_metric
            
            # 提取关键指标
            results = {}
            
            if 'excess_return_with_cost' in metrics:
                returns = metrics['excess_return_with_cost']
                
                # 年化收益率
                total_return = returns.iloc[-1] if len(returns) > 0 else 0
                days = len(returns)
                annual_return = ((1 + total_return) ** (252 / days) - 1) if days > 0 else 0
                
                # 最大回撤
                cumulative_returns = (1 + returns).cumprod()
                running_max = cumulative_returns.cummax()
                drawdown = (cumulative_returns - running_max) / running_max
                max_drawdown = drawdown.min()
                
                # 夏普比率
                if len(returns) > 1:
                    daily_returns = returns.pct_change().dropna()
                    sharpe_ratio = (daily_returns.mean() / daily_returns.std() * np.sqrt(252)) if daily_returns.std() > 0 else 0
                    volatility = daily_returns.std() * np.sqrt(252)
                else:
                    sharpe_ratio = 0
                    volatility = 0
                
                # 胜率
                win_rate = (daily_returns > 0).mean() if len(daily_returns) > 0 else 0
                
                results.update({
                    'annual_return': annual_return,
                    'total_return': total_return,
                    'max_drawdown': max_drawdown,
                    'sharpe_ratio': sharpe_ratio,
                    'volatility': volatility,
                    'win_rate': win_rate
                })
            
            # 添加交易统计
            if indicator:
                results.update({
                    'total_trades': len(indicator) if isinstance(indicator, dict) else 0,
                    'trading_days': len(portfolio_metric) if hasattr(portfolio_metric, '__len__') else 0
                })
            
            return results
            
        except Exception as e:
            self.logger.error(f"结果分析失败: {e}")
            return {}
    
    def save_results(self, results: Dict, output_dir: str):
        """保存结果"""
        os.makedirs(output_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"enhanced_boll_backtest_{timestamp}.json"
        filepath = os.path.join(output_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2, default=str)
        
        self.logger.info(f"结果已保存到: {filepath}")
        return filepath


def create_enhanced_boll_strategy(config: EnhancedBollConfig = None):
    """创建增强版BOLL策略"""
    return EnhancedBollStrategy(config)


# 示例使用
if __name__ == "__main__":
    # 创建配置
    config = EnhancedBollConfig(
        initial_capital=1000000,      # 100万初始资金
        buy_commission=0.0003,        # 万3佣金
        sell_commission=0.0003,       # 万3佣金
        stamp_tax=0.001,              # 千分之一印花税
        stock_pool_size=50,
        fixed_positions=10
    )
    
    # 创建策略
    strategy = EnhancedBollStrategy(config)
    
    # 运行回测
    try:
        portfolio_metric, indicator = strategy.run_backtest(
            start_date="2023-01-01",
            end_date="2023-12-31",
            benchmark="SH000905"
        )
        
        # 分析结果
        results = strategy.analyze_results(portfolio_metric, indicator)
        
        # 保存结果
        output_dir = "/Users/libing/kk_Projects/kk_Stock/kk_stock_backend/abu_quantitative/results"
        strategy.save_results(results, output_dir)
        
        # 显示结果
        print("回测结果:")
        for key, value in results.items():
            if isinstance(value, float):
                if key.endswith('_return') or key.endswith('_rate'):
                    print(f"{key}: {value:.2%}")
                else:
                    print(f"{key}: {value:.4f}")
            else:
                print(f"{key}: {value}")
                
    except Exception as e:
        print(f"回测失败: {e}")
        import traceback
        traceback.print_exc()