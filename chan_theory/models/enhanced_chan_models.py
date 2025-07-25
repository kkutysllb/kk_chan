#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强型缠论数据模型
基于技术方案优化的缠论数据结构
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any, Union
from enum import Enum
import pandas as pd
import numpy as np

# 导入基础模型
try:
    from .chan_theory_models import TrendLevel, FenXingType, TrendDirection
except ImportError:
    # 定义基础枚举
    class TrendLevel(str, Enum):
        MIN1 = "1min"
        MIN5 = "5min"
        MIN30 = "30min"
        DAILY = "daily"
        WEEKLY = "weekly"
    
    class FenXingType(str, Enum):
        TOP = "top"
        BOTTOM = "bottom"
    
    class TrendDirection(str, Enum):
        UP = "up"
        DOWN = "down"
        SIDEWAYS = "sideways"

@dataclass
class EnhancedFenXing:
    """
    增强型分型
    在基础分型基础上添加智能分析特征
    """
    timestamp: datetime
    price: float
    fenxing_type: FenXingType
    index: int
    
    # 增强特征
    strength: float = 0.0                    # 分型强度 (0-1)
    confidence: float = 0.0                  # 置信度 (0-1)
    volume_confirmation: bool = False        # 成交量确认
    position_in_trend: str = "unknown"       # 在趋势中的位置
    next_target: Optional[float] = None      # 下一个目标位
    support_resistance: float = 0.0          # 支撑/阻力位强度
    
    # 技术指标确认
    macd_confirmation: bool = False          # MACD确认
    rsi_confirmation: bool = False           # RSI确认
    bollinger_confirmation: bool = False     # 布林带确认
    
    # 机器学习评分
    ml_probability: float = 0.0              # ML模型预测概率
    feature_importance: Dict[str, float] = field(default_factory=dict)
    
    # 历史统计
    historical_success_rate: float = 0.0    # 历史成功率
    avg_holding_period: int = 0              # 平均持有周期
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'timestamp': self.timestamp.isoformat(),
            'price': self.price,
            'fenxing_type': self.fenxing_type.value,
            'index': self.index,
            'strength': self.strength,
            'confidence': self.confidence,
            'volume_confirmation': self.volume_confirmation,
            'position_in_trend': self.position_in_trend,
            'next_target': self.next_target,
            'support_resistance': self.support_resistance,
            'macd_confirmation': self.macd_confirmation,
            'rsi_confirmation': self.rsi_confirmation,
            'bollinger_confirmation': self.bollinger_confirmation,
            'ml_probability': self.ml_probability,
            'feature_importance': self.feature_importance,
            'historical_success_rate': self.historical_success_rate,
            'avg_holding_period': self.avg_holding_period
        }

@dataclass
class IntelligentBi:
    """
    智能笔
    集成多重验证和概率评估的笔结构
    """
    start_fenxing: EnhancedFenXing
    end_fenxing: EnhancedFenXing
    direction: TrendDirection
    
    # 基础属性
    strength: float = 0.0                    # 笔的强度
    purity: float = 0.0                      # 笔的纯度
    duration: int = 0                        # 持续时间(K线数)
    price_change: float = 0.0                # 价格变化
    price_change_pct: float = 0.0           # 价格变化百分比
    
    # 成交量分析
    volume_pattern: str = "normal"           # 成交量模式
    volume_confirmation: bool = False        # 成交量确认
    avg_volume_ratio: float = 1.0           # 平均成交量比率
    
    # 技术指标分析
    macd_divergence: bool = False            # MACD背离
    rsi_divergence: bool = False             # RSI背离
    momentum_confirmation: bool = False      # 动量确认
    
    # 机器学习评估
    validity_probability: float = 0.0        # 有效性概率
    break_probability: float = 0.0           # 突破概率
    ml_features: Dict[str, float] = field(default_factory=dict)
    
    # 市场环境
    market_regime: str = "normal"            # 市场状态
    volatility_level: str = "medium"         # 波动率水平
    
    @property
    def start_price(self) -> float:
        return self.start_fenxing.price
    
    @property
    def end_price(self) -> float:
        return self.end_fenxing.price
    
    @property
    def start_time(self) -> datetime:
        return self.start_fenxing.timestamp
    
    @property
    def end_time(self) -> datetime:
        return self.end_fenxing.timestamp
    
    @property
    def amplitude(self) -> float:
        return abs(self.end_price - self.start_price)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'start_fenxing': self.start_fenxing.to_dict(),
            'end_fenxing': self.end_fenxing.to_dict(),
            'direction': self.direction.value,
            'strength': self.strength,
            'purity': self.purity,
            'duration': self.duration,
            'price_change': self.price_change,
            'price_change_pct': self.price_change_pct,
            'volume_pattern': self.volume_pattern,
            'volume_confirmation': self.volume_confirmation,
            'avg_volume_ratio': self.avg_volume_ratio,
            'macd_divergence': self.macd_divergence,
            'rsi_divergence': self.rsi_divergence,
            'momentum_confirmation': self.momentum_confirmation,
            'validity_probability': self.validity_probability,
            'break_probability': self.break_probability,
            'ml_features': self.ml_features,
            'market_regime': self.market_regime,
            'volatility_level': self.volatility_level,
            'start_price': self.start_price,
            'end_price': self.end_price,
            'amplitude': self.amplitude
        }

@dataclass
class AdvancedXianDuan:
    """
    高级线段
    集成多层次分析的线段结构
    """
    constituent_bis: List[IntelligentBi]
    direction: TrendDirection
    level: TrendLevel
    
    # 基础属性
    start_time: datetime = None
    end_time: datetime = None
    start_price: float = 0.0
    end_price: float = 0.0
    
    # 结构特征
    bi_count: int = 0                        # 包含的笔数量
    structure_integrity: float = 0.0         # 结构完整性
    trend_consistency: float = 0.0           # 趋势一致性
    
    # 强度分析
    momentum_strength: float = 0.0           # 动量强度
    volume_support: float = 0.0              # 成交量支持度
    breakout_potential: float = 0.0          # 突破潜力
    
    # 技术确认
    moving_average_alignment: bool = False   # 均线排列确认
    indicator_confluence: int = 0            # 指标汇聚数量
    
    # 机器学习评估
    classification_confidence: float = 0.0   # 分类置信度
    regression_target: float = 0.0           # 回归目标价位
    feature_vector: List[float] = field(default_factory=list)
    
    def __post_init__(self):
        """初始化后处理"""
        if self.constituent_bis:
            self.bi_count = len(self.constituent_bis)
            self.start_time = self.constituent_bis[0].start_time
            self.end_time = self.constituent_bis[-1].end_time
            self.start_price = self.constituent_bis[0].start_price
            self.end_price = self.constituent_bis[-1].end_price
    
    @property
    def duration_days(self) -> float:
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds() / 86400
        return 0
    
    @property
    def total_amplitude(self) -> float:
        return abs(self.end_price - self.start_price)
    
    @property
    def price_change_pct(self) -> float:
        if self.start_price > 0:
            return ((self.end_price - self.start_price) / self.start_price) * 100
        return 0
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'constituent_bis': [bi.to_dict() for bi in self.constituent_bis],
            'direction': self.direction.value,
            'level': self.level.value,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'start_price': self.start_price,
            'end_price': self.end_price,
            'bi_count': self.bi_count,
            'structure_integrity': self.structure_integrity,
            'trend_consistency': self.trend_consistency,
            'momentum_strength': self.momentum_strength,
            'volume_support': self.volume_support,
            'breakout_potential': self.breakout_potential,
            'moving_average_alignment': self.moving_average_alignment,
            'indicator_confluence': self.indicator_confluence,
            'classification_confidence': self.classification_confidence,
            'regression_target': self.regression_target,
            'duration_days': self.duration_days,
            'total_amplitude': self.total_amplitude,
            'price_change_pct': self.price_change_pct
        }

@dataclass
class AdvancedZhongShu:
    """
    高级中枢
    具备智能分析能力的中枢结构
    """
    level: TrendLevel
    start_time: datetime
    end_time: datetime
    high: float
    low: float
    
    # 基础属性
    center: float = 0.0                      # 中枢中心
    range_size: float = 0.0                  # 中枢区间大小
    range_ratio: float = 0.0                 # 区间比率
    
    # 结构特征
    extension_count: int = 0                 # 延伸次数
    breakthrough_attempts: int = 0           # 突破尝试次数
    support_tests: int = 0                   # 支撑测试次数
    resistance_tests: int = 0                # 阻力测试次数
    
    # 成交量分析
    volume_distribution: Dict[str, float] = field(default_factory=dict)
    avg_volume_in_range: float = 0.0         # 区间内平均成交量
    volume_breakout_ratio: float = 0.0       # 突破时成交量比率
    
    # 市场结构分析
    market_structure_type: str = "consolidation"  # 市场结构类型
    consolidation_quality: float = 0.0       # 整理质量
    breakout_direction_bias: str = "neutral" # 突破方向倾向
    
    # 机器学习预测
    next_direction_prob: Dict[str, float] = field(default_factory=dict)
    breakout_probability: float = 0.0        # 突破概率
    breakdown_probability: float = 0.0       # 跌破概率
    continuation_probability: float = 0.0    # 持续概率
    
    # 时间分析
    formation_period: int = 0                # 形成周期
    expected_duration: int = 0               # 预期持续时间
    time_strength: float = 0.0               # 时间强度
    
    def __post_init__(self):
        """初始化后处理"""
        self.center = (self.high + self.low) / 2
        self.range_size = self.high - self.low
        if self.center > 0:
            self.range_ratio = self.range_size / self.center
    
    @property
    def duration_days(self) -> float:
        return (self.end_time - self.start_time).total_seconds() / 86400
    
    @property
    def is_active(self) -> bool:
        """判断中枢是否仍然活跃"""
        return (datetime.now() - self.end_time).total_seconds() < 86400 * 7  # 7天内
    
    def contains_price(self, price: float) -> bool:
        """判断价格是否在中枢范围内"""
        return self.low <= price <= self.high
    
    def distance_from_center(self, price: float) -> float:
        """计算价格距离中枢中心的距离"""
        return abs(price - self.center)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'level': self.level.value,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat(),
            'high': self.high,
            'low': self.low,
            'center': self.center,
            'range_size': self.range_size,
            'range_ratio': self.range_ratio,
            'extension_count': self.extension_count,
            'breakthrough_attempts': self.breakthrough_attempts,
            'support_tests': self.support_tests,
            'resistance_tests': self.resistance_tests,
            'volume_distribution': self.volume_distribution,
            'avg_volume_in_range': self.avg_volume_in_range,
            'volume_breakout_ratio': self.volume_breakout_ratio,
            'market_structure_type': self.market_structure_type,
            'consolidation_quality': self.consolidation_quality,
            'breakout_direction_bias': self.breakout_direction_bias,
            'next_direction_prob': self.next_direction_prob,
            'breakout_probability': self.breakout_probability,
            'breakdown_probability': self.breakdown_probability,
            'continuation_probability': self.continuation_probability,
            'formation_period': self.formation_period,
            'expected_duration': self.expected_duration,
            'time_strength': self.time_strength,
            'duration_days': self.duration_days,
            'is_active': self.is_active
        }

@dataclass
class TradingSignal:
    """
    交易信号
    集成多重确认的交易信号
    """
    signal_type: str                         # 'buy' | 'sell'
    signal_subtype: str                      # '1buy' | '2buy' | '3buy' | '1sell' | '2sell' | '3sell'
    timestamp: datetime
    price: float
    
    # 信号强度
    strength: float = 0.0                    # 信号强度 (0-1)
    confidence: float = 0.0                  # 置信度 (0-1)
    priority: str = "medium"                 # 优先级: low/medium/high
    
    # 确认信息
    chan_confirmation: bool = False          # 缠论确认
    technical_confirmation: bool = False     # 技术指标确认
    volume_confirmation: bool = False        # 成交量确认
    ml_confirmation: bool = False            # 机器学习确认
    
    # 目标和止损
    target_price: Optional[float] = None     # 目标价位
    stop_loss_price: Optional[float] = None  # 止损价位
    risk_reward_ratio: float = 0.0           # 风险收益比
    
    # 持有建议
    suggested_holding_period: int = 0        # 建议持有周期(天)
    position_size_suggestion: float = 0.0    # 建议仓位比例
    
    # 历史统计
    historical_success_rate: float = 0.0     # 历史成功率
    avg_return: float = 0.0                  # 平均收益率
    max_favorable: float = 0.0               # 最大有利变动
    max_adverse: float = 0.0                 # 最大不利变动
    
    # 市场环境
    market_condition: str = "normal"         # 市场环境
    sector_trend: str = "neutral"            # 行业趋势
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'signal_type': self.signal_type,
            'signal_subtype': self.signal_subtype,
            'timestamp': self.timestamp.isoformat(),
            'price': self.price,
            'strength': self.strength,
            'confidence': self.confidence,
            'priority': self.priority,
            'chan_confirmation': self.chan_confirmation,
            'technical_confirmation': self.technical_confirmation,
            'volume_confirmation': self.volume_confirmation,
            'ml_confirmation': self.ml_confirmation,
            'target_price': self.target_price,
            'stop_loss_price': self.stop_loss_price,
            'risk_reward_ratio': self.risk_reward_ratio,
            'suggested_holding_period': self.suggested_holding_period,
            'position_size_suggestion': self.position_size_suggestion,
            'historical_success_rate': self.historical_success_rate,
            'avg_return': self.avg_return,
            'max_favorable': self.max_favorable,
            'max_adverse': self.max_adverse,
            'market_condition': self.market_condition,
            'sector_trend': self.sector_trend
        }

@dataclass
class ChanAnalysisResult:
    """
    缠论分析结果
    完整的分析结果容器
    """
    symbol: str
    timeframe: TrendLevel
    analysis_timestamp: datetime
    
    # 结构分析结果
    fenxings: List[EnhancedFenXing] = field(default_factory=list)
    bis: List[IntelligentBi] = field(default_factory=list)
    xianduan: List[AdvancedXianDuan] = field(default_factory=list)
    zhongshus: List[AdvancedZhongShu] = field(default_factory=list)
    
    # 信号和预测
    trading_signals: List[TradingSignal] = field(default_factory=list)
    ml_predictions: Dict[str, Any] = field(default_factory=dict)
    
    # 质量评估
    analysis_quality: float = 0.0            # 分析质量评分
    data_completeness: float = 0.0           # 数据完整性
    structure_clarity: float = 0.0           # 结构清晰度
    
    # 市场评估
    trend_strength: float = 0.0              # 趋势强度
    trend_direction: TrendDirection = TrendDirection.SIDEWAYS
    market_phase: str = "consolidation"      # 市场阶段
    
    # 统计信息
    total_data_points: int = 0               # 总数据点数
    analysis_period_days: int = 0            # 分析周期天数
    computation_time: float = 0.0            # 计算时间
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'symbol': self.symbol,
            'timeframe': self.timeframe.value,
            'analysis_timestamp': self.analysis_timestamp.isoformat(),
            'fenxings': [fx.to_dict() for fx in self.fenxings],
            'bis': [bi.to_dict() for bi in self.bis],
            'xianduan': [xd.to_dict() for xd in self.xianduan],
            'zhongshus': [zs.to_dict() for zs in self.zhongshus],
            'trading_signals': [signal.to_dict() for signal in self.trading_signals],
            'ml_predictions': self.ml_predictions,
            'analysis_quality': self.analysis_quality,
            'data_completeness': self.data_completeness,
            'structure_clarity': self.structure_clarity,
            'trend_strength': self.trend_strength,
            'trend_direction': self.trend_direction.value,
            'market_phase': self.market_phase,
            'total_data_points': self.total_data_points,
            'analysis_period_days': self.analysis_period_days,
            'computation_time': self.computation_time
        }
    
    def get_summary(self) -> Dict[str, Any]:
        """获取分析摘要"""
        return {
            'symbol': self.symbol,
            'timeframe': self.timeframe.value,
            'analysis_timestamp': self.analysis_timestamp.isoformat(),
            'structure_counts': {
                'fenxings': len(self.fenxings),
                'bis': len(self.bis),
                'xianduan': len(self.xianduan),
                'zhongshus': len(self.zhongshus)
            },
            'signals_count': len(self.trading_signals),
            'trend_info': {
                'direction': self.trend_direction.value,
                'strength': self.trend_strength,
                'market_phase': self.market_phase
            },
            'quality_metrics': {
                'analysis_quality': self.analysis_quality,
                'data_completeness': self.data_completeness,
                'structure_clarity': self.structure_clarity
            },
            'computation_time': self.computation_time
        }

# 配置类
@dataclass
class EnhancedChanConfig:
    """增强型缠论配置"""
    
    # 基础分型配置
    fenxing_window: int = 3
    fenxing_strength_threshold: float = 0.001
    min_fenxing_gap: int = 2
    
    # 笔配置
    min_bi_length: int = 3
    bi_strength_threshold: float = 0.005
    bi_purity_threshold: float = 0.7
    
    # 线段配置
    min_xd_bi_count: int = 3
    xd_break_threshold: float = 0.02
    
    # 中枢配置
    min_zhongshu_overlap: float = 0.001
    zhongshu_extend_ratio: float = 0.05
    
    # 机器学习配置
    enable_ml_enhancement: bool = True
    ml_confidence_threshold: float = 0.6
    feature_importance_threshold: float = 0.05
    
    # 技术指标配置
    enable_indicator_confirmation: bool = True
    macd_params: Dict[str, int] = field(default_factory=lambda: {'fast': 12, 'slow': 26, 'signal': 9})
    rsi_period: int = 14
    bollinger_period: int = 20
    
    # 性能配置
    enable_caching: bool = True
    cache_expire_seconds: int = 3600
    max_concurrent_analysis: int = 5