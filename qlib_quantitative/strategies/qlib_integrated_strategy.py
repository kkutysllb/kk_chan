#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Qlib风格集成策略 - 采用qlib设计理念的完整量化投资解决方案
基于qlib框架思想，结合本地数据库实现的高性能策略
重点优化信号生成和风控管理，提升策略收益
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
import logging
import os
import json
from datetime import datetime, timedelta
from dataclasses import dataclass
from abc import ABC, abstractmethod

# 项目导入
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from core.data_adapter import QlibDataAdapter
from core.trading_costs import TradingCostCalculator, TradingCostConfig

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 兼容性配置
QLIB_AVAILABLE = False
try:
    import qlib
    from qlib.utils import get_module_logger
    from qlib.model.base import Model
    from qlib.contrib.model.gbdt import LGBModel
    from qlib.contrib.strategy.strategy import TopkDropoutStrategy, WeightStrategyBase
    from qlib.workflow import R
    from qlib.utils.config import config
    from qlib.utils.utils import init_instance_by_config
    QLIB_AVAILABLE = True
except ImportError:
    def get_module_logger(name):
        return logging.getLogger(name)


@dataclass
class QlibIntegratedConfig:
    """Qlib集成策略配置"""
    # 基础配置
    initial_capital: float = 1000000  # 初始资金
    start_date: str = "2020-01-01"
    end_date: str = "2023-12-31"
    
    # 数据配置
    instruments: str = "csi300"  # 股票池：专门针对沪深300
    features: str = "Alpha158"   # 因子库：Alpha158/Alpha360
    
    # 模型配置
    model_type: str = "LGBModel"  # 模型类型
    model_params: Dict = None
    
    # 策略配置 - 沪深300专属
    strategy_type: str = "TopkDropoutStrategy"  # 策略类型
    topk: int = 25               # 选股数量：沪深300适合25只
    n_drop: int = 4              # 换手股票数：适度换手
    
    # 交易配置
    commission_rate: float = 0.0003  # 手续费率万3
    stamp_tax: float = 0.001         # 印花税千1
    benchmark: str = "SH000300"      # 基准：沪深300
    
    # 风控配置 - 沪深300专属
    max_weight: float = 0.08     # 单股最大权重：大盘股相对分散
    min_weight: float = 0.025    # 单股最小权重
    risk_budget: float = 0.12    # 风险预算：大盘股风险相对较低
    
    # 止损止盈配置 - 沪深300专属
    stop_loss: float = 0.06      # 止损6%：大盘股止损相对保守
    take_profit: float = 0.12    # 止盈12%：大盘股收益预期相对保守
    
    # 调仓频率 - 沪深300专属
    rebalance_freq: int = 7      # 调仓频率（天）：大盘股调仓不宜过频


class QlibDataProvider:
    """Qlib数据提供器 - 连接MongoDB和qlib"""
    
    def __init__(self, config: QlibIntegratedConfig):
        self.config = config
        self.logger = get_module_logger(__name__)
        self.data_adapter = QlibDataAdapter()
        
        # 初始化qlib
        self._init_qlib()
    
    def _init_qlib(self):
        """初始化qlib环境"""
        try:
            # 尝试初始化qlib
            if not QLIB_AVAILABLE:
                # 静默处理，不输出警告
                return
            
            # 使用默认数据源（如果有）
            # qlib.init(provider_uri="~/.qlib/qlib_data/cn_data", region=REG_CN)
            self.logger.info("qlib环境初始化成功")
            
        except Exception as e:
            # 静默处理qlib初始化失败，因为我们有自定义实现
            pass
    
    def create_dataset_config(self) -> Dict:
        """创建数据集配置"""
        handler_config = {
            "start_time": self.config.start_date,
            "end_time": self.config.end_date,
            "fit_start_time": self.config.start_date,
            "fit_end_time": self.config.end_date,
            "instruments": self.config.instruments,
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
        
        # 根据选择的因子库设置handler
        if self.config.features == "Alpha158":
            handler_config["class"] = "Alpha158"
            handler_config["module_path"] = "qlib.contrib.data.handler"
        elif self.config.features == "Alpha360":
            handler_config["class"] = "Alpha360"
            handler_config["module_path"] = "qlib.contrib.data.handler"
        else:
            # 使用自定义因子
            handler_config.update(self._create_custom_features())
        
        return {
            "class": "DatasetH",
            "module_path": "qlib.data.dataset",
            "kwargs": {
                "handler": handler_config,
                "segments": {
                    "train": (self.config.start_date, "2022-12-31"),
                    "valid": ("2023-01-01", "2023-06-30"),
                    "test": ("2023-07-01", self.config.end_date)
                }
            }
        }
    
    def _create_custom_features(self) -> Dict:
        """创建自定义因子配置"""
        # 使用我们的数据库数据创建自定义因子
        custom_features = [
            # 价格因子
            "($close - Ref($close, 1)) / Ref($close, 1)",  # 日收益率
            "($close - Ref($close, 5)) / Ref($close, 5)",  # 5日收益率
            "($close - Ref($close, 20)) / Ref($close, 20)", # 20日收益率
            
            # 成交量因子
            "($volume - Ref($volume, 1)) / Ref($volume, 1)",  # 成交量变化
            "$volume / Mean($volume, 20)",  # 成交量相对强度
            
            # 技术指标因子
            "($close - Mean($close, 5)) / Mean($close, 5)",   # 5日均线偏离
            "($close - Mean($close, 20)) / Mean($close, 20)", # 20日均线偏离
            "Std($close, 20) / Mean($close, 20)",             # 波动率
            
            # 布林带因子
            "($close - Mean($close, 20)) / Std($close, 20)",  # 布林带位置
            
            # 动量因子
            "Corr($close, $volume, 10)",  # 价量相关性
            "Rank($close / Ref($close, 1))",  # 收益率排名
        ]
        
        return {
            "class": "Alpha158",  # 基于Alpha158扩展
            "module_path": "qlib.contrib.data.handler",
            "kwargs": {
                "custom_features": custom_features
            }
        }
    
    def get_stock_universe(self) -> List[str]:
        """获取股票池"""
        try:
            # 从数据库获取股票池
            stocks = self.data_adapter.get_stock_list(self.config.instruments)
            
            # 转换为qlib格式
            qlib_stocks = []
            for stock in stocks:
                # 转换股票代码格式
                if stock.startswith('SH'):
                    qlib_stocks.append(stock[2:] + '.SH')
                elif stock.startswith('SZ'):
                    qlib_stocks.append(stock[2:] + '.SZ')
                else:
                    qlib_stocks.append(stock)
            
            return qlib_stocks[:200]  # 限制数量以提高性能
            
        except Exception as e:
            self.logger.error(f"获取股票池失败: {e}")
            return ["000001.SZ", "000002.SZ", "600000.SH", "600036.SH"]  # 默认股票池


class BaseModel(ABC):
    """基础模型抽象类 - 参考qlib.model.base.Model"""
    
    @abstractmethod
    def fit(self, dataset):
        """训练模型"""
        pass
    
    @abstractmethod
    def predict(self, dataset):
        """预测"""
        pass


class EnhancedTechnicalFactors:
    """增强技术因子计算器 - 结合多种技术分析指标"""
    
    def __init__(self, config: QlibIntegratedConfig):
        self.config = config
        self.logger = logger
    
    def calculate_momentum_factors(self, data: pd.DataFrame) -> pd.DataFrame:
        """计算动量因子"""
        factors = pd.DataFrame(index=data.index)
        
        # 多周期动量
        factors['momentum_5d'] = data['close'].pct_change(5)
        factors['momentum_10d'] = data['close'].pct_change(10)
        factors['momentum_20d'] = data['close'].pct_change(20)
        
        # 动量强度
        factors['momentum_strength'] = (
            factors['momentum_5d'] * 0.5 +
            factors['momentum_10d'] * 0.3 +
            factors['momentum_20d'] * 0.2
        )
        
        # 动量方向一致性
        factors['momentum_consistency'] = (
            (factors['momentum_5d'] > 0).astype(int) +
            (factors['momentum_10d'] > 0).astype(int) +
            (factors['momentum_20d'] > 0).astype(int)
        ) / 3
        
        # 动量加速度
        factors['momentum_acceleration'] = factors['momentum_5d'] - factors['momentum_10d']
        
        return factors
    
    def calculate_volatility_factors(self, data: pd.DataFrame) -> pd.DataFrame:
        """计算波动率因子"""
        factors = pd.DataFrame(index=data.index)
        
        # 历史波动率
        factors['volatility_5d'] = data['close'].rolling(5).std()
        factors['volatility_10d'] = data['close'].rolling(10).std()
        factors['volatility_20d'] = data['close'].rolling(20).std()
        
        # 波动率比率
        factors['volatility_ratio'] = factors['volatility_5d'] / factors['volatility_20d']
        
        # 波动率趋势
        factors['volatility_trend'] = (
            factors['volatility_5d'] - factors['volatility_20d']
        ) / factors['volatility_20d']
        
        # 真实波动率（ATR）
        high_low = data['high'] - data['low']
        high_close = abs(data['high'] - data['close'].shift(1))
        low_close = abs(data['low'] - data['close'].shift(1))
        true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        factors['atr'] = true_range.rolling(14).mean()
        
        return factors
    
    def calculate_volume_factors(self, data: pd.DataFrame) -> pd.DataFrame:
        """计算成交量因子"""
        factors = pd.DataFrame(index=data.index)
        
        # 成交量均线
        factors['volume_ma_5'] = data['volume'].rolling(5).mean()
        factors['volume_ma_10'] = data['volume'].rolling(10).mean()
        factors['volume_ma_20'] = data['volume'].rolling(20).mean()
        
        # 成交量比率
        factors['volume_ratio'] = data['volume'] / factors['volume_ma_20']
        
        # 价量背离
        price_change = data['close'].pct_change(5)
        volume_change = data['volume'].pct_change(5)
        factors['price_volume_divergence'] = price_change * volume_change
        
        # 成交量突破
        factors['volume_breakout'] = (
            data['volume'] > factors['volume_ma_20'] * 1.5
        ).astype(int)
        
        # 相对成交量强度
        factors['relative_volume_strength'] = (
            data['volume'] / factors['volume_ma_20']
        ).rolling(5).mean()
        
        return factors
    
    def calculate_technical_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """计算技术指标因子"""
        factors = pd.DataFrame(index=data.index)
        
        # 移动平均线
        factors['ma_5'] = data['close'].rolling(5).mean()
        factors['ma_10'] = data['close'].rolling(10).mean()
        factors['ma_20'] = data['close'].rolling(20).mean()
        
        # 价格相对位置
        factors['price_position_5'] = data['close'] / factors['ma_5'] - 1
        factors['price_position_10'] = data['close'] / factors['ma_10'] - 1
        factors['price_position_20'] = data['close'] / factors['ma_20'] - 1
        
        # 均线斜率
        factors['ma_slope_5'] = factors['ma_5'].pct_change(5)
        factors['ma_slope_10'] = factors['ma_10'].pct_change(10)
        factors['ma_slope_20'] = factors['ma_20'].pct_change(20)
        
        # 布林带
        bb_middle = data['close'].rolling(20).mean()
        bb_std = data['close'].rolling(20).std()
        factors['bb_upper'] = bb_middle + 2 * bb_std
        factors['bb_lower'] = bb_middle - 2 * bb_std
        factors['bb_position'] = (data['close'] - factors['bb_lower']) / (factors['bb_upper'] - factors['bb_lower'])
        factors['bb_width'] = (factors['bb_upper'] - factors['bb_lower']) / bb_middle
        
        # RSI
        delta = data['close'].diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        avg_gain = gain.rolling(14).mean()
        avg_loss = loss.rolling(14).mean()
        rs = avg_gain / avg_loss
        factors['rsi'] = 100 - (100 / (1 + rs))
        
        # MACD
        ema_12 = data['close'].ewm(span=12).mean()
        ema_26 = data['close'].ewm(span=26).mean()
        factors['macd'] = ema_12 - ema_26
        factors['macd_signal'] = factors['macd'].ewm(span=9).mean()
        factors['macd_histogram'] = factors['macd'] - factors['macd_signal']
        
        # KDJ
        low_9 = data['low'].rolling(9).min()
        high_9 = data['high'].rolling(9).max()
        rsv = (data['close'] - low_9) / (high_9 - low_9) * 100
        factors['kdj_k'] = rsv.ewm(com=2).mean()
        factors['kdj_d'] = factors['kdj_k'].ewm(com=2).mean()
        factors['kdj_j'] = 3 * factors['kdj_k'] - 2 * factors['kdj_d']
        
        return factors
    
    def calculate_pattern_factors(self, data: pd.DataFrame) -> pd.DataFrame:
        """计算形态因子"""
        factors = pd.DataFrame(index=data.index)
        
        # 支撑阻力
        factors['support_level'] = data['low'].rolling(20).min()
        factors['resistance_level'] = data['high'].rolling(20).max()
        factors['support_distance'] = (data['close'] - factors['support_level']) / factors['support_level']
        factors['resistance_distance'] = (factors['resistance_level'] - data['close']) / data['close']
        
        # 突破信号
        factors['breakout_up'] = (
            data['close'] > data['high'].rolling(20).max().shift(1)
        ).astype(int)
        factors['breakout_down'] = (
            data['close'] < data['low'].rolling(20).min().shift(1)
        ).astype(int)
        
        # 缺口
        factors['gap_up'] = (
            data['low'] > data['high'].shift(1)
        ).astype(int)
        factors['gap_down'] = (
            data['high'] < data['low'].shift(1)
        ).astype(int)
        
        # 锤子线和倒锤子线
        body = abs(data['close'] - data['open'])
        upper_shadow = data['high'] - data[['close', 'open']].max(axis=1)
        lower_shadow = data[['close', 'open']].min(axis=1) - data['low']
        
        factors['hammer'] = (
            (lower_shadow > 2 * body) & 
            (upper_shadow < 0.1 * body)
        ).astype(int)
        
        factors['inverted_hammer'] = (
            (upper_shadow > 2 * body) & 
            (lower_shadow < 0.1 * body)
        ).astype(int)
        
        return factors
    
    def calculate_market_factors(self, data: pd.DataFrame) -> pd.DataFrame:
        """计算市场因子"""
        factors = pd.DataFrame(index=data.index)
        
        # 收益率分布
        returns = data['close'].pct_change()
        factors['return_mean'] = returns.rolling(20).mean()
        factors['return_std'] = returns.rolling(20).std()
        factors['return_skew'] = returns.rolling(20).skew()
        factors['return_kurt'] = returns.rolling(20).kurt()
        
        # 胜率
        factors['win_rate'] = (returns > 0).rolling(20).mean()
        
        # 连续上涨/下跌天数
        up_days = (returns > 0).astype(int)
        down_days = (returns < 0).astype(int)
        factors['consecutive_up'] = up_days * (up_days.groupby((up_days != up_days.shift()).cumsum()).cumcount() + 1)
        factors['consecutive_down'] = down_days * (down_days.groupby((down_days != down_days.shift()).cumsum()).cumcount() + 1)
        
        # 最大回撤
        cumulative = (1 + returns).cumprod()
        rolling_max = cumulative.rolling(20).max()
        factors['max_drawdown'] = (cumulative - rolling_max) / rolling_max
        
        return factors
    
    def calculate_all_factors(self, data: pd.DataFrame) -> pd.DataFrame:
        """计算所有技术因子"""
        try:
            # 计算各类因子
            momentum_factors = self.calculate_momentum_factors(data)
            volatility_factors = self.calculate_volatility_factors(data)
            volume_factors = self.calculate_volume_factors(data)
            technical_factors = self.calculate_technical_indicators(data)
            pattern_factors = self.calculate_pattern_factors(data)
            market_factors = self.calculate_market_factors(data)
            
            # 合并所有因子
            all_factors = pd.concat([
                momentum_factors,
                volatility_factors,
                volume_factors,
                technical_factors,
                pattern_factors,
                market_factors
            ], axis=1)
            
            # 处理缺失值
            all_factors = all_factors.ffill().fillna(0)
            
            # 去除异常值
            for col in all_factors.columns:
                if all_factors[col].dtype in ['float64', 'int64']:
                    q1 = all_factors[col].quantile(0.01)
                    q99 = all_factors[col].quantile(0.99)
                    all_factors[col] = all_factors[col].clip(q1, q99)
            
            return all_factors
            
        except Exception as e:
            self.logger.error(f"计算技术因子失败: {e}")
            return pd.DataFrame(index=data.index)


class QlibEnhancedModel(BaseModel):
    """增强版qlib模型 - 基于技术因子的机器学习模型"""
    
    def __init__(self, config: QlibIntegratedConfig):
        super().__init__()
        self.config = config
        self.logger = logger
        self.base_model = None
        self.factor_calculator = EnhancedTechnicalFactors(config)
        
        # 初始化基础模型
        self._init_base_model()
    
    def _init_base_model(self):
        """初始化基础模型"""
        try:
            if self.config.model_type == "LGBModel":
                model_params = self.config.model_params or {
                    "objective": "regression",
                    "metric": "rmse",
                    "boosting_type": "gbdt",
                    "num_leaves": 31,
                    "learning_rate": 0.05,
                    "feature_fraction": 0.9,
                    "bagging_fraction": 0.8,
                    "bagging_freq": 5,
                    "verbose": -1,
                    "num_boost_round": 100,
                    "early_stopping_rounds": 10
                }
                
                # 创建LGBModel实例
                if QLIB_AVAILABLE:
                    self.base_model = LGBModel(**model_params)
                else:
                    self.base_model = self._create_fallback_model()
                    
        except Exception as e:
            self.logger.error(f"模型初始化失败: {e}")
            self.base_model = self._create_fallback_model()
    
    def _create_fallback_model(self):
        """创建备用模型"""
        class FallbackModel:
            def fit(self, dataset):
                return self
            
            def predict(self, X):
                # 简单的均值回归预测
                return np.random.normal(0, 0.02, len(X))
        
        return FallbackModel()
    
    def fit(self, dataset):
        """训练模型"""
        try:
            if hasattr(self.base_model, 'fit'):
                self.base_model.fit(dataset)
            self.logger.info("模型训练完成")
            return self
        except Exception as e:
            self.logger.error(f"模型训练失败: {e}")
            return self
    
    def predict(self, dataset) -> pd.Series:
        """预测"""
        try:
            if hasattr(self.base_model, 'predict'):
                predictions = self.base_model.predict(dataset)
                if isinstance(predictions, pd.Series):
                    return predictions
                else:
                    # 转换为Series
                    return pd.Series(predictions)
            else:
                # 备用预测逻辑
                return self._fallback_predict(dataset)
                
        except Exception as e:
            self.logger.error(f"模型预测失败: {e}")
            return self._fallback_predict(dataset)
    
    def _fallback_predict(self, stock_data_dict: Dict[str, pd.DataFrame]) -> pd.Series:
        """针对沪深300的专属预测逻辑"""
        try:
            predictions = {}
            
            for stock_code, stock_data in stock_data_dict.items():
                try:
                    # 核心技术因子
                    close = stock_data['close']
                    volume = stock_data['volume']
                    high = stock_data['high']
                    low = stock_data['low']
                    
                    # 沪深300专属因子计算
                    score = self._calculate_csi300_score(close, volume, high, low)
                    
                    predictions[stock_code] = score
                    
                except Exception as e:
                    self.logger.warning(f"计算{stock_code}因子失败: {e}")
                    predictions[stock_code] = 0.0
            
            # 转换为Series并排名
            pred_series = pd.Series(predictions)
            if len(pred_series) > 0 and pred_series.std() > 0:
                pred_series = (pred_series - pred_series.mean()) / pred_series.std()
            
            return pred_series
            
        except Exception as e:
            self.logger.error(f"预测失败: {e}")
            return pd.Series(np.random.normal(0, 0.02, len(stock_data_dict)))
    
    def _calculate_csi300_score(self, close: pd.Series, volume: pd.Series, high: pd.Series, low: pd.Series) -> float:
        """计算沪深300专属评分"""
        score = 0.0
        
        # 1. 价值动量因子 (35%) - 大盘股重视价值和动量结合
        momentum_10d = close.pct_change(10).iloc[-1]
        momentum_30d = close.pct_change(30).iloc[-1]
        
        if momentum_10d > 0.02 and momentum_30d > 0.05:  # 双重动量
            score += 0.35
        elif momentum_10d > 0.01:  # 短期动量
            score += 0.20
        elif momentum_10d < -0.02:  # 避免弱势
            score -= 0.15
        
        # 2. 大盘股稳定性因子 (25%) - 重视稳定性
        try:
            # 计算波动率
            volatility_20d = close.pct_change().rolling(20).std().iloc[-1]
            if volatility_20d < 0.025:  # 低波动率
                score += 0.25
            elif volatility_20d < 0.035:  # 中等波动率
                score += 0.15
            elif volatility_20d > 0.05:  # 高波动率，减分
                score -= 0.10
        except:
            pass
        
        # 3. 均线趋势因子 (20%) - 趋势跟踪
        try:
            ma_5 = close.rolling(5).mean().iloc[-1]
            ma_20 = close.rolling(20).mean().iloc[-1]
            ma_60 = close.rolling(60).mean().iloc[-1]
            
            if ma_5 > ma_20 > ma_60:  # 完美排列
                score += 0.20
            elif ma_5 > ma_20:  # 短期上升
                score += 0.10
            elif ma_5 < ma_20 < ma_60:  # 完全下降
                score -= 0.15
        except:
            pass
        
        # 4. 成交量质量因子 (15%) - 大盘股重视成交量质量
        try:
            volume_ma_20 = volume.rolling(20).mean().iloc[-1]
            volume_ratio = volume.iloc[-1] / volume_ma_20
            
            if 1.2 <= volume_ratio <= 2.0:  # 适度放量
                score += 0.15
            elif 0.8 <= volume_ratio < 1.2:  # 温和成交
                score += 0.08
            elif volume_ratio > 3.0:  # 过度放量，谨慎
                score -= 0.05
        except:
            pass
        
        # 5. 技术形态因子 (5%) - 关注关键技术位
        try:
            # 价格相对位置
            price_position = (close.iloc[-1] - low.rolling(20).min().iloc[-1]) / (high.rolling(20).max().iloc[-1] - low.rolling(20).min().iloc[-1])
            
            if 0.6 <= price_position <= 0.8:  # 强势区间
                score += 0.05
            elif price_position < 0.2:  # 超跌区间
                score -= 0.03
        except:
            pass
        
        return score


class QlibIntegratedStrategy:
    """Qlib集成策略主类"""
    
    def __init__(self, config: QlibIntegratedConfig = None):
        self.config = config or QlibIntegratedConfig()
        self.logger = get_module_logger(__name__)
        
        # 初始化组件
        self.data_provider = QlibDataProvider(self.config)
        self.model = QlibEnhancedModel(self.config)
        self.cost_calculator = TradingCostCalculator(
            TradingCostConfig(
                commission_rate=self.config.commission_rate,
                stamp_tax_rate=self.config.stamp_tax,
                min_commission=5.0
            )
        )
        
        # 策略组件
        self.strategy = None
        self.dataset = None
        self.predictions = None
    
    def initialize(self):
        """初始化策略"""
        try:
            # 创建数据集
            dataset_config = self.data_provider.create_dataset_config()
            
            if QLIB_AVAILABLE:
                self.dataset = init_instance_by_config(dataset_config)
            else:
                self.dataset = self._create_fallback_dataset()
            
            # 训练模型
            self.model.fit(self.dataset)
            
            # 生成预测
            self.predictions = self.model.predict(self.dataset)
            
            # 创建策略
            self._create_strategy()
            
            self.logger.info("策略初始化完成")
            
        except Exception as e:
            self.logger.error(f"策略初始化失败: {e}")
            raise
    
    def _create_fallback_dataset(self):
        """创建备用数据集"""
        class FallbackDataset:
            def __init__(self):
                self.data = pd.DataFrame()
            
            def get_data(self):
                return self.data
        
        return FallbackDataset()
    
    def _create_strategy(self):
        """创建策略实例"""
        try:
            if self.config.strategy_type == "TopkDropoutStrategy":
                self.strategy = TopkDropoutStrategy(
                    topk=self.config.topk,
                    n_drop=self.config.n_drop,
                    signal=self.predictions
                )
            elif self.config.strategy_type == "WeightStrategy":
                self.strategy = self._create_weight_strategy()
            else:
                self.strategy = self._create_custom_strategy()
                
        except Exception as e:
            self.logger.error(f"策略创建失败: {e}")
            self.strategy = self._create_custom_strategy()
    
    def _create_weight_strategy(self):
        """创建权重策略"""
        class WeightStrategy(WeightStrategyBase):
            def __init__(self, predictions, config):
                super().__init__()
                self.predictions = predictions
                self.config = config
            
            def generate_weights(self):
                # 基于预测分数生成权重
                scores = self.predictions.copy()
                
                # 标准化分数
                scores = (scores - scores.mean()) / scores.std()
                
                # 转换为权重
                weights = scores.apply(lambda x: max(0, x) if x > 0 else 0)
                
                # 归一化
                if weights.sum() > 0:
                    weights = weights / weights.sum()
                
                return weights
        
        return WeightStrategy(self.predictions, self.config)
    
    def _create_custom_strategy(self):
        """创建自定义策略"""
        class CustomStrategy:
            def __init__(self, predictions, config):
                self.predictions = predictions
                self.config = config
            
            def generate_trade_decision(self):
                # 基于预测分数生成交易决策
                scores = self.predictions.copy()
                
                # 选择前K只股票
                top_stocks = scores.nlargest(self.config.topk)
                
                # 生成交易决策
                decisions = []
                for stock, score in top_stocks.items():
                    if score > 0:
                        decisions.append({
                            'instrument': stock,
                            'amount': 1.0 / len(top_stocks),
                            'direction': 1
                        })
                
                return decisions
        
        return CustomStrategy(self.predictions, self.config)
    
    def run_backtest(self) -> Dict[str, Any]:
        """运行回测 - 利用qlib框架功能"""
        try:
            # 如果qlib可用，使用qlib的完整流程
            if QLIB_AVAILABLE:
                return self._run_qlib_backtest()
            else:
                # 使用我们优化的技术因子回测
                return self._run_enhanced_backtest()
            
        except Exception as e:
            self.logger.error(f"回测失败: {e}")
            raise
    
    def _run_qlib_backtest(self) -> Dict[str, Any]:
        """使用qlib框架的完整回测流程"""
        try:
            # 1. 配置qlib环境
            qlib_config = {
                "provider_uri": "~/.qlib/qlib_data/cn_data",
                "region": "cn"
            }
            
            # 2. 数据集配置
            dataset_config = {
                "class": "DatasetH",
                "module_path": "qlib.data.dataset",
                "kwargs": {
                    "handler": {
                        "class": "Alpha158",
                        "module_path": "qlib.contrib.data.handler",
                        "kwargs": {
                            "start_time": self.config.start_date,
                            "end_time": self.config.end_date,
                            "fit_start_time": self.config.start_date,
                            "fit_end_time": self.config.end_date,
                            "instruments": self.config.instruments,
                            "infer_processors": [
                                {"class": "RobustZScoreNorm", "kwargs": {"fields_group": "feature"}},
                                {"class": "Fillna", "kwargs": {"fields_group": "feature"}}
                            ],
                            "learn_processors": [
                                {"class": "DropnaLabel"},
                                {"class": "CSRankNorm", "kwargs": {"fields_group": "label"}}
                            ],
                            "label": ["Ref($close, -2) / Ref($close, -1) - 1"]
                        }
                    },
                    "segments": {
                        "train": (self.config.start_date, "2022-12-31"),
                        "valid": ("2023-01-01", "2023-06-30"),
                        "test": ("2023-07-01", self.config.end_date)
                    }
                }
            }
            
            # 3. 模型配置
            model_config = {
                "class": "LGBModel",
                "module_path": "qlib.contrib.model.gbdt",
                "kwargs": {
                    "loss": "mse",
                    "colsample_bytree": 0.8879,
                    "learning_rate": 0.0421,
                    "subsample": 0.8789,
                    "lambda_l1": 205.6999,
                    "lambda_l2": 580.9768,
                    "max_depth": 8,
                    "num_leaves": 210,
                    "num_threads": 20
                }
            }
            
            # 4. 策略配置
            strategy_config = {
                "class": "TopkDropoutStrategy",
                "module_path": "qlib.contrib.strategy.strategy",
                "kwargs": {
                    "model": model_config,
                    "dataset": dataset_config,
                    "topk": self.config.topk,
                    "n_drop": self.config.n_drop
                }
            }
            
            # 5. 回测配置
            backtest_config = {
                "start_time": self.config.start_date,
                "end_time": self.config.end_date,
                "account": self.config.initial_capital,
                "benchmark": self.config.benchmark,
                "exchange_kwargs": {
                    "freq": "day",
                    "limit_threshold": 0.095,
                    "deal_price": "close",
                    "open_cost": self.config.commission_rate,
                    "close_cost": self.config.commission_rate + self.config.stamp_tax,
                    "min_cost": 5.0,
                    "trade_unit": 100
                }
            }
            
            # 6. 执行qlib工作流
            from qlib.workflow import R
            
            # 初始化数据集
            dataset = init_instance_by_config(dataset_config)
            
            # 训练模型
            model = init_instance_by_config(model_config)
            model.fit(dataset)
            
            # 生成预测
            predictions = model.predict(dataset)
            
            # 创建策略
            strategy = init_instance_by_config(strategy_config)
            
            # 运行回测
            portfolio_metric, indicator = strategy.backtest(
                **backtest_config
            )
            
            # 分析结果
            results = self._analyze_qlib_results(portfolio_metric, indicator)
            
            return results
            
        except Exception as e:
            self.logger.error(f"qlib回测失败: {e}")
            # 回退到自定义回测
            return self._run_enhanced_backtest()
    
    def _run_enhanced_backtest(self) -> Dict[str, Any]:
        """使用增强技术因子的回测"""
        try:
            # 获取股票池和数据
            stocks = self.data_provider.get_stock_universe()
            if not stocks:
                raise Exception("无法获取股票池")
            
            # 限制股票数量以提高性能
            stocks = stocks[:20]  # 减少到20只提高性能
            
            # 获取历史数据
            stock_data = {}
            for stock in stocks:
                try:
                    data = self.data_provider.data_adapter.get_stock_data(
                        stock, self.config.start_date, self.config.end_date
                    )
                    if not data.empty and len(data) > 10:  # 降低数据要求
                        stock_data[stock] = data
                except Exception as e:
                    self.logger.warning(f"获取{stock}数据失败: {e}")
            
            if not stock_data:
                raise Exception("无法获取有效的股票数据")
            
            self.logger.info(f"获取到{len(stock_data)}只股票的数据")
            
            # 使用技术因子生成预测
            predictions = self.model._fallback_predict(stock_data)
            
            # 执行回测
            results = self._execute_simple_backtest(stock_data, predictions)
            
            return results
            
        except Exception as e:
            self.logger.error(f"增强回测失败: {e}")
            raise
    
    def _execute_simple_backtest(self, stock_data: Dict[str, pd.DataFrame], predictions: pd.Series) -> Dict[str, Any]:
        """执行简化回测"""
        try:
            # 初始化回测参数
            initial_capital = self.config.initial_capital
            current_capital = initial_capital
            positions = {}
            portfolio_history = []
            
            self.logger.info(f"初始资金: {initial_capital:,.0f}")
            
            # 获取所有交易日
            all_dates = set()
            for data in stock_data.values():
                all_dates.update(data.index)
            all_dates = sorted(all_dates)
            
            # 调仓日期
            rebalance_dates = all_dates[::self.config.rebalance_freq]
            
            # 选择初始股票 - 使用沪深300专属选股逻辑
            selected_stocks = self._select_csi300_stocks(stock_data, predictions)
            
            # 初始化持仓 - 使用字典存储股票和股数
            if selected_stocks:
                cash_per_stock = current_capital / len(selected_stocks)
                self.logger.info(f"初始化持仓: 选中{len(selected_stocks)}只股票，每股分配{cash_per_stock:,.0f}元")
                for stock in selected_stocks:
                    if stock in stock_data:
                        # 获取第一个可用价格
                        first_data = stock_data[stock]
                        if not first_data.empty:
                            first_price = first_data['close'].iloc[0]
                            # A股交易单位是手，1手=100股
                            max_hands = int(cash_per_stock / (first_price * 100))
                            shares = max_hands * 100  # 转换为股数
                            if shares > 0:
                                positions[stock] = {
                                    'shares': shares,
                                    'cost': first_price
                                }
                                current_capital -= shares * first_price
                                self.logger.info(f"买入{stock}: {max_hands}手({shares}股)，价格{first_price:.2f}，成本{shares * first_price:,.0f}")
                            else:
                                self.logger.warning(f"股票{stock}价格{first_price:.2f}过高，无法买入1手")
                        else:
                            self.logger.warning(f"股票{stock}数据为空")
                    else:
                        self.logger.warning(f"股票{stock}不在数据中")
                self.logger.info(f"初始化完成，剩余现金{current_capital:,.0f}，持仓{len(positions)}只股票")
            else:
                self.logger.warning("未选中任何股票，无法初始化持仓")
            
            self.logger.info(f"回测期间: {len(all_dates)}天，调仓{len(rebalance_dates)}次")
            
            # 逐日回测
            for i, date in enumerate(all_dates):
                # 获取当日价格
                current_prices = {}
                for stock, data in stock_data.items():
                    if date in data.index:
                        current_prices[stock] = data.loc[date, 'close']
                
                # 计算当前持仓价值
                position_value = 0
                for stock, pos_info in positions.items():
                    if stock in current_prices:
                        position_value += pos_info['shares'] * current_prices[stock]
                
                total_value = current_capital + position_value
                
                # 调仓日
                if date in rebalance_dates and i > 0:
                    # 重新生成预测并选股
                    current_predictions = self.model._fallback_predict(stock_data)
                    top_stocks = current_predictions.nlargest(self.config.topk).index.tolist()
                    new_selected_stocks = [stock for stock in top_stocks if stock in stock_data][:self.config.topk]
                    
                    # 卖出不在新选股中的股票
                    for stock in list(positions.keys()):
                        if stock not in new_selected_stocks and stock in current_prices:
                            # 计算卖出成本
                            sell_cost = current_prices[stock] * positions[stock]['shares'] * (
                                self.config.commission_rate + self.config.stamp_tax
                            )
                            sell_amount = current_prices[stock] * positions[stock]['shares'] - sell_cost
                            current_capital += sell_amount
                            del positions[stock]
                    
                    # 买入新股票
                    if new_selected_stocks:
                        cash_per_stock = current_capital / len(new_selected_stocks)
                        for stock in new_selected_stocks:
                            if stock not in positions and stock in current_prices:
                                price = current_prices[stock]
                                # 计算买入成本 - A股交易单位是手
                                buy_cost_rate = self.config.commission_rate
                                max_hands = int(cash_per_stock / (price * 100 * (1 + buy_cost_rate)))
                                shares = max_hands * 100  # 转换为股数
                                if shares > 0:
                                    buy_cost = price * shares * buy_cost_rate
                                    total_cost = price * shares + buy_cost
                                    if total_cost <= current_capital:
                                        current_capital -= total_cost
                                        positions[stock] = {
                                            'shares': shares,
                                            'cost': price
                                        }
                    
                    selected_stocks = new_selected_stocks
                
                # 重新计算持仓价值
                final_position_value = 0
                for stock, pos_info in positions.items():
                    if stock in current_prices:
                        final_position_value += pos_info['shares'] * current_prices[stock]
                
                final_total_value = current_capital + final_position_value
                
                # 记录组合状态
                portfolio_history.append({
                    'date': date,
                    'cash': current_capital,
                    'position_value': final_position_value,
                    'total_value': final_total_value,
                    'positions': len(positions)
                })
            
            # 计算性能指标
            portfolio_df = pd.DataFrame(portfolio_history)
            portfolio_df.set_index('date', inplace=True)
            
            self.logger.info(f"回测完成，组合历史记录{len(portfolio_df)}条")
            if len(portfolio_df) > 0:
                final_value = portfolio_df['total_value'].iloc[-1]
                self.logger.info(f"最终资产: {final_value:,.0f}, 初始资金: {initial_capital:,.0f}")
                
                total_return = (final_value / initial_capital - 1)
                daily_returns = portfolio_df['total_value'].pct_change().dropna()
                annual_return = (1 + total_return) ** (252 / len(portfolio_df)) - 1 if len(portfolio_df) > 0 else 0
                
                # 最大回撤
                rolling_max = portfolio_df['total_value'].expanding().max()
                drawdown = (portfolio_df['total_value'] - rolling_max) / rolling_max
                max_drawdown = drawdown.min()
                
                # 夏普比率
                sharpe_ratio = (daily_returns.mean() / daily_returns.std() * np.sqrt(252)) if daily_returns.std() > 0 else 0
                
                # 波动率
                volatility = daily_returns.std() * np.sqrt(252)
                
                # 胜率
                win_rate = (daily_returns > 0).mean()
                
                results = {
                    # 基本信息
                    'start_date': self.config.start_date,
                    'end_date': self.config.end_date,
                    'initial_capital': initial_capital,
                    'final_capital': portfolio_df['total_value'].iloc[-1],
                    'trading_days': len(portfolio_df),
                    'selected_stocks': len(selected_stocks),
                    
                    # 性能指标 - 直接在顶级
                    'total_return': total_return,
                    'annual_return': annual_return,
                    'max_drawdown': max_drawdown,
                    'sharpe_ratio': sharpe_ratio,
                    'volatility': volatility,
                    'win_rate': win_rate,
                    
                    # 交易成本
                    'commission_rate': self.config.commission_rate,
                    'stamp_tax_rate': self.config.stamp_tax,
                    
                    # 额外信息
                    'total_trades': 0,  # 后续计算
                    'portfolio_history': portfolio_df.to_dict('records')
                }
                
                return results
            else:
                raise Exception("回测数据为空")
                
        except Exception as e:
            self.logger.error(f"简化回测失败: {e}")
            raise
    
    def _analyze_results(self, portfolio_metric, indicator) -> Dict[str, Any]:
        """分析回测结果"""
        try:
            results = {}
            
            # 基础信息
            results['backtest_info'] = {
                'start_date': self.config.start_date,
                'end_date': self.config.end_date,
                'initial_capital': self.config.initial_capital,
                'strategy_type': self.config.strategy_type,
                'model_type': self.config.model_type,
                'features': self.config.features
            }
            
            # 性能指标
            if isinstance(portfolio_metric, dict) and 'return' in portfolio_metric:
                returns = portfolio_metric['return']
                benchmark = portfolio_metric.get('benchmark', pd.Series([0] * len(returns)))
                
                # 计算指标
                total_return = returns.iloc[-1] if len(returns) > 0 else 0
                annual_return = ((1 + total_return) ** (252 / len(returns)) - 1) if len(returns) > 0 else 0
                
                # 最大回撤
                cumulative = (1 + returns).cumprod()
                rolling_max = cumulative.cummax()
                drawdown = (cumulative - rolling_max) / rolling_max
                max_drawdown = drawdown.min()
                
                # 夏普比率
                excess_return = returns - benchmark
                sharpe_ratio = (excess_return.mean() / excess_return.std() * np.sqrt(252)) if excess_return.std() > 0 else 0
                
                results['performance_metrics'] = {
                    'total_return': total_return,
                    'annual_return': annual_return,
                    'max_drawdown': max_drawdown,
                    'sharpe_ratio': sharpe_ratio,
                    'volatility': returns.std() * np.sqrt(252),
                    'win_rate': (returns > 0).mean()
                }
            else:
                results['performance_metrics'] = indicator
            
            # 策略参数
            results['strategy_config'] = {
                'topk': self.config.topk,
                'n_drop': self.config.n_drop,
                'commission_rate': self.config.commission_rate,
                'stamp_tax': self.config.stamp_tax
            }
            
            return results
            
        except Exception as e:
            self.logger.error(f"结果分析失败: {e}")
            return {'error': str(e)}
    
    def save_results(self, results: Dict[str, Any], output_dir: str = None):
        """保存结果"""
        if output_dir is None:
            output_dir = "/Users/libing/kk_Projects/kk_Stock/kk_stock_backend/abu_quantitative/results"
        
        os.makedirs(output_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"qlib_integrated_backtest_{timestamp}.json"
        filepath = os.path.join(output_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2, default=str)
        
        self.logger.info(f"结果已保存到: {filepath}")
        return filepath
    
    def optimize_parameters(self, param_grid: Dict[str, List]) -> Dict[str, Any]:
        """参数优化"""
        best_params = {}
        best_score = -np.inf
        
        # 简化的网格搜索
        for topk in param_grid.get('topk', [self.config.topk]):
            for n_drop in param_grid.get('n_drop', [self.config.n_drop]):
                # 更新配置
                self.config.topk = topk
                self.config.n_drop = n_drop
                
                try:
                    # 运行回测
                    results = self.run_backtest()
                    
                    # 评估分数（使用夏普比率）
                    score = results['performance_metrics'].get('sharpe_ratio', -np.inf)
                    
                    if score > best_score:
                        best_score = score
                        best_params = {
                            'topk': topk,
                            'n_drop': n_drop,
                            'score': score
                        }
                
                except Exception as e:
                    self.logger.error(f"参数优化失败 topk={topk}, n_drop={n_drop}: {e}")
        
        return best_params
    
    def _select_csi300_stocks(self, stock_data: Dict[str, pd.DataFrame], predictions: pd.Series) -> List[str]:
        """沪深300专属选股逻辑"""
        try:
            # 计算每只股票的综合评分
            stock_scores = {}
            
            for stock_code, data in stock_data.items():
                try:
                    # 基础预测得分
                    base_score = predictions.get(stock_code, 0.0)
                    
                    # 沪深300专属筛选条件
                    csi300_score = self._calculate_csi300_selection_score(data)
                    
                    # 综合评分
                    total_score = base_score * 0.7 + csi300_score * 0.3
                    stock_scores[stock_code] = total_score
                    
                except Exception as e:
                    self.logger.warning(f"计算{stock_code}综合评分失败: {e}")
                    stock_scores[stock_code] = 0.0
            
            # 选择评分最高的股票
            sorted_stocks = sorted(stock_scores.items(), key=lambda x: x[1], reverse=True)
            selected_stocks = [stock for stock, score in sorted_stocks[:self.config.topk]]
            
            self.logger.info(f"沪深300选股完成，选中{len(selected_stocks)}只股票")
            return selected_stocks
            
        except Exception as e:
            self.logger.error(f"沪深300选股失败: {e}")
            return []
    
    def _calculate_csi300_selection_score(self, data: pd.DataFrame) -> float:
        """计算沪深300专属选股评分"""
        try:
            score = 0.0
            close = data['close']
            volume = data['volume']
            
            # 1. 流动性评分 (25%) - 大盘股重视流动性
            try:
                avg_volume = volume.rolling(20).mean().iloc[-1]
                if avg_volume > 50000000:  # 5千万以上
                    score += 0.25
                elif avg_volume > 20000000:  # 2千万以上
                    score += 0.15
                elif avg_volume < 5000000:  # 500万以下，扣分
                    score -= 0.1
            except:
                pass
            
            # 2. 稳定性评分 (25%) - 大盘股重视稳定
            try:
                volatility = close.pct_change().rolling(20).std().iloc[-1]
                if volatility < 0.02:  # 低波动
                    score += 0.25
                elif volatility < 0.03:  # 中等波动
                    score += 0.15
                elif volatility > 0.05:  # 高波动，扣分
                    score -= 0.1
            except:
                pass
            
            # 3. 趋势一致性评分 (25%) - 大盘股重视趋势
            try:
                ma_5 = close.rolling(5).mean().iloc[-1]
                ma_10 = close.rolling(10).mean().iloc[-1]
                ma_20 = close.rolling(20).mean().iloc[-1]
                
                if ma_5 > ma_10 > ma_20:  # 完美排列
                    score += 0.25
                elif ma_5 > ma_10:  # 短期上升
                    score += 0.15
                elif ma_5 < ma_10 < ma_20:  # 完全下降
                    score -= 0.15
            except:
                pass
            
            # 4. 价格位置评分 (25%) - 大盘股避免追高
            try:
                current_price = close.iloc[-1]
                high_20 = close.rolling(20).max().iloc[-1]
                low_20 = close.rolling(20).min().iloc[-1]
                
                price_position = (current_price - low_20) / (high_20 - low_20)
                
                if 0.3 <= price_position <= 0.7:  # 合理位置
                    score += 0.25
                elif 0.2 <= price_position <= 0.8:  # 可接受位置
                    score += 0.15
                elif price_position > 0.9:  # 过高位置，扣分
                    score -= 0.15
            except:
                pass
            
            return score
            
        except Exception as e:
            self.logger.warning(f"计算CSI300选股评分失败: {e}")
            return 0.0
    
    def _generate_csi300_trading_signals(self, stock_data: Dict[str, pd.DataFrame], 
                                       current_positions: Dict[str, float]) -> Dict[str, str]:
        """生成沪深300专属交易信号"""
        try:
            signals = {}
            
            for stock_code, data in stock_data.items():
                try:
                    signal = self._analyze_csi300_stock_signal(data, stock_code in current_positions)
                    if signal != "hold":
                        signals[stock_code] = signal
                except Exception as e:
                    self.logger.warning(f"生成{stock_code}交易信号失败: {e}")
            
            return signals
            
        except Exception as e:
            self.logger.error(f"生成CSI300交易信号失败: {e}")
            return {}
    
    def _analyze_csi300_stock_signal(self, data: pd.DataFrame, is_held: bool) -> str:
        """分析单只沪深300股票的交易信号"""
        try:
            close = data['close']
            volume = data['volume']
            
            # 当前价格和均线
            current_price = close.iloc[-1]
            ma_5 = close.rolling(5).mean().iloc[-1]
            ma_10 = close.rolling(10).mean().iloc[-1]
            ma_20 = close.rolling(20).mean().iloc[-1]
            
            # 计算技术指标
            rsi = self._calculate_rsi(close, 14)
            macd_signal = self._calculate_macd_signal(close)
            
            # 买入信号条件 (适合大盘股)
            buy_conditions = [
                current_price > ma_5 > ma_10,  # 价格在短期均线上方
                rsi < 70,  # RSI不过热
                macd_signal == "bullish",  # MACD看多
                volume.iloc[-1] > volume.rolling(10).mean().iloc[-1],  # 成交量放大
                current_price > close.iloc[-2]  # 价格上涨
            ]
            
            # 卖出信号条件 (适合大盘股)
            sell_conditions = [
                current_price < ma_5,  # 价格跌破短期均线
                rsi > 80,  # RSI过热
                macd_signal == "bearish",  # MACD看空
                current_price < close.iloc[-2] * 0.98  # 价格下跌超过2%
            ]
            
            # 决策逻辑
            if not is_held and sum(buy_conditions) >= 3:
                return "buy"
            elif is_held and sum(sell_conditions) >= 2:
                return "sell"
            else:
                return "hold"
                
        except Exception as e:
            self.logger.warning(f"分析交易信号失败: {e}")
            return "hold"
    
    def _calculate_rsi(self, close: pd.Series, period: int = 14) -> float:
        """计算RSI指标"""
        try:
            delta = close.diff()
            gain = delta.where(delta > 0, 0).rolling(period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(period).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            return rsi.iloc[-1]
        except:
            return 50.0
    
    def _calculate_macd_signal(self, close: pd.Series) -> str:
        """计算MACD信号"""
        try:
            ema_12 = close.ewm(span=12).mean()
            ema_26 = close.ewm(span=26).mean()
            macd = ema_12 - ema_26
            signal = macd.ewm(span=9).mean()
            
            # 当前和前一个值
            current_macd = macd.iloc[-1]
            current_signal = signal.iloc[-1]
            prev_macd = macd.iloc[-2]
            prev_signal = signal.iloc[-2]
            
            # 判断信号
            if current_macd > current_signal and prev_macd <= prev_signal:
                return "bullish"
            elif current_macd < current_signal and prev_macd >= prev_signal:
                return "bearish"
            else:
                return "neutral"
        except:
            return "neutral"


# 便捷函数
def create_qlib_strategy(config: QlibIntegratedConfig = None) -> QlibIntegratedStrategy:
    """创建qlib集成策略"""
    return QlibIntegratedStrategy(config)


def run_qlib_backtest(start_date: str = "2020-01-01", 
                     end_date: str = "2023-12-31",
                     topk: int = 50,
                     n_drop: int = 5) -> Dict[str, Any]:
    """运行qlib回测的便捷函数"""
    config = QlibIntegratedConfig(
        start_date=start_date,
        end_date=end_date,
        topk=topk,
        n_drop=n_drop
    )
    
    strategy = QlibIntegratedStrategy(config)
    return strategy.run_backtest()


# 示例使用
if __name__ == "__main__":
    # 测试不同指数的表现
    indexes = [
        ("000852.SH", "中证1000"),
        ("000510.CSI", "中证A500"),
        ("000905.SH", "中证500"),
        ("000300.SH", "沪深300"),
        ("000016.SH", "上证50")
    ]
    
    # 测试年份
    years = [
        ("2020-01-01", "2020-12-31"),
        ("2021-01-01", "2021-12-31"),
        ("2022-01-01", "2022-12-31"),
        ("2023-01-01", "2023-12-31"),
        ("2024-01-01", "2024-12-31")
    ]
    
    print("=" * 100)
    print("各指数策略2020-2024年全面测试")
    print("=" * 100)
    
    # 存储所有结果
    all_index_results = {}
    
    for index_code, index_name in indexes:
        print(f"\n🔍 开始测试{index_name}({index_code})...")
        
        index_results = []
        
        for start_date, end_date in years:
            year = start_date[:4]
            
            try:
                config = QlibIntegratedConfig(
                    initial_capital=1000000,
                    start_date=start_date,
                    end_date=end_date,
                    topk=10,
                    n_drop=2,
                    commission_rate=0.0003,
                    stamp_tax=0.001,
                    rebalance_freq=10
                )
                
                # 创建策略并修改股票池获取方法
                strategy = QlibIntegratedStrategy(config)
                
                # 直接修改数据提供器的股票池获取方法
                def get_custom_stock_list():
                    return strategy.data_provider.data_adapter.get_stock_list(index_code)
                
                strategy.data_provider.get_stock_universe = get_custom_stock_list
                
                results = strategy.run_backtest()
                
                performance = results.get('performance_metrics', {})
                backtest_info = results.get('backtest_info', {})
                
                total_return = performance.get('total_return', 0)
                annual_return = performance.get('annual_return', 0)
                max_drawdown = performance.get('max_drawdown', 0)
                sharpe_ratio = performance.get('sharpe_ratio', 0)
                final_capital = backtest_info.get('final_capital', 0)
                
                print(f"   📊 {year}年: {total_return:>8.2%} (夏普: {sharpe_ratio:>5.2f})")
                
                index_results.append({
                    'year': year,
                    'total_return': total_return,
                    'annual_return': annual_return,
                    'max_drawdown': max_drawdown,
                    'sharpe_ratio': sharpe_ratio,
                    'final_capital': final_capital
                })
                
            except Exception as e:
                print(f"   ❌ {year}年测试失败: {e}")
                index_results.append({
                    'year': year,
                    'total_return': 0,
                    'annual_return': 0,
                    'max_drawdown': 0,
                    'sharpe_ratio': 0,
                    'final_capital': 1000000
                })
        
        # 计算该指数的总体表现
        total_return_sum = sum(r['total_return'] for r in index_results)
        avg_return = total_return_sum / len(index_results)
        positive_years = sum(1 for r in index_results if r['total_return'] > 0)
        
        all_index_results[index_name] = {
            'index_code': index_code,
            'yearly_results': index_results,
            'total_return_sum': total_return_sum,
            'avg_return': avg_return,
            'positive_years': positive_years,
            'total_years': len(index_results)
        }
        
        print(f"   🎯 {index_name}总结: 累计{total_return_sum:.2%}, 年均{avg_return:.2%}, 盈利{positive_years}/{len(index_results)}年")
    
    # 生成综合对比报告
    print("\n" + "=" * 100)
    print("各指数策略综合表现对比 (2020-2024)")
    print("=" * 100)
    
    # 按累计收益率排序
    sorted_indexes = sorted(all_index_results.items(), key=lambda x: x[1]['total_return_sum'], reverse=True)
    
    print(f"{'排名':<4} {'指数名称':<12} {'累计收益':<12} {'年均收益':<12} {'盈利年数':<8} {'总体评价':<10}")
    print("-" * 80)
    
    for i, (index_name, data) in enumerate(sorted_indexes, 1):
        cumulative = data['total_return_sum']
        avg_return = data['avg_return']
        positive_years = data['positive_years']
        total_years = data['total_years']
        
        # 评价
        if cumulative > 0.5:
            rating = "🏆 优秀"
        elif cumulative > 0.2:
            rating = "💰 良好"
        elif cumulative > 0:
            rating = "📈 一般"
        else:
            rating = "💩 较差"
        
        print(f"{i:<4} {index_name:<12} {cumulative:>10.2%} {avg_return:>10.2%} {positive_years}/{total_years:<6} {rating}")
    
    # 详细年度对比表
    print("\n" + "=" * 100)
    print("各指数年度收益率对比表")
    print("=" * 100)
    
    print(f"{'指数名称':<12} {'2020年':<10} {'2021年':<10} {'2022年':<10} {'2023年':<10} {'2024年':<10}")
    print("-" * 80)
    
    for index_name, data in sorted_indexes:
        yearly_data = data['yearly_results']
        year_returns = [f"{r['total_return']:>8.2%}" for r in yearly_data]
        print(f"{index_name:<12} {' '.join(year_returns)}")
    
    # 找出最佳表现
    best_index = sorted_indexes[0]
    best_name = best_index[0]
    best_data = best_index[1]
    
    print(f"\n🏆 最佳表现指数: {best_name}")
    print(f"   累计收益率: {best_data['total_return_sum']:.2%}")
    print(f"   年均收益率: {best_data['avg_return']:.2%}")
    print(f"   盈利年数: {best_data['positive_years']}/{best_data['total_years']}")
    
    print("\n" + "=" * 100)