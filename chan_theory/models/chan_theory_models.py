#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
缠论数据模型
定义缠论分析中的核心数据结构
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum
import pandas as pd


class TrendLevel(Enum):
    """趋势级别枚举"""
    MIN5 = "5min"          # 5分钟级别
    MIN30 = "30min"        # 30分钟级别
    DAILY = "daily"        # 日线级别


class FenXingType(Enum):
    """分型类型"""
    TOP = "top"           # 顶分型
    BOTTOM = "bottom"     # 底分型


class TrendDirection(Enum):
    """趋势方向"""
    UP = "up"             # 上升
    DOWN = "down"         # 下降
    SIDEWAYS = "sideways" # 横盘


@dataclass
class ChanTheoryConfig:
    """缠论分析配置"""
    symbol: str                           # 股票代码
    start_date: datetime                  # 开始日期
    end_date: datetime                    # 结束日期
    
    # 分型识别参数
    fenxing_window: int = 3              # 分型识别窗口
    fenxing_strength: float = 0.001      # 分型强度阈值（降低提高敏感度）
    min_fenxing_gap: int = 2             # 分型间最小间隔（降低减少限制）
    
    # 笔识别参数
    min_bi_length: int = 3               # 笔的最小长度（K线数）- 降低提高识别率
    bi_strength_threshold: float = 0.005  # 笔的强度阈值 - 降低提高敏感度
    
    # 线段识别参数
    min_xd_bi_count: int = 3             # 线段最少包含的笔数
    xd_break_threshold: float = 0.02     # 线段破坏阈值
    
    # 中枢识别参数
    min_zhongshu_overlap: float = 0.001  # 中枢最小重叠比例（降低提高识别率）
    zhongshu_extend_ratio: float = 0.05   # 中枢扩展比例（降低提高合并率）
    
    # 布林带参数（模拟三线）
    bollinger_period: int = 20           # 布林带周期
    bollinger_std: float = 2.0           # 布林带标准差倍数
    
    # 多周期分析参数
    enable_multi_timeframe: bool = True  # 是否启用多周期分析
    primary_timeframe: TrendLevel = TrendLevel.DAILY  # 主要分析周期
    
    # 分钟级别特殊配置
    minute_levels_enabled: bool = True   # 是否启用分钟级别分析
    minute_bollinger_period: int = 20    # 分钟级别布林带周期
    minute_fenxing_strength: float = 0.0005  # 分钟级别分型强度阈值（更低敏感度）


@dataclass
class FenXing:
    """分型数据结构"""
    index: int                           # 在K线中的索引
    timestamp: datetime                  # 时间戳
    price: float                         # 分型价格
    fenxing_type: FenXingType           # 分型类型
    strength: float                      # 分型强度
    level: TrendLevel                    # 所属级别
    confirmed: bool = False              # 是否确认
    
    def __str__(self):
        return f"{self.fenxing_type.value}分型@{self.price:.2f}({self.timestamp.date()})"


@dataclass
class Bi:
    """笔数据结构"""
    start_fenxing: FenXing              # 起始分型
    end_fenxing: FenXing                # 结束分型
    direction: TrendDirection            # 笔的方向
    length: int                          # 笔的长度（K线数）
    amplitude: float                     # 笔的幅度
    level: TrendLevel                    # 所属级别
    
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
    
    def __str__(self):
        return f"{self.direction.value}笔: {self.start_price:.2f}->{self.end_price:.2f} ({self.amplitude:.2%})"


@dataclass
class XianDuan:
    """线段数据结构"""
    start_fenxing: FenXing              # 起始分型
    end_fenxing: FenXing                # 结束分型
    direction: TrendDirection            # 线段方向
    bi_list: List[Bi]                   # 包含的笔列表
    level: TrendLevel                    # 所属级别
    
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
        return abs(self.end_price - self.start_price) / self.start_price
    
    @property
    def high_price(self) -> float:
        return max(self.start_price, self.end_price)
    
    @property
    def low_price(self) -> float:
        return min(self.start_price, self.end_price)
    
    def __str__(self):
        return f"{self.direction.value}线段: {self.start_price:.2f}->{self.end_price:.2f} ({len(self.bi_list)}笔)"


@dataclass
class ZhongShu:
    """中枢数据结构"""
    high: float                          # 中枢上沿
    low: float                           # 中枢下沿
    center: float                        # 中枢中心
    start_time: datetime                 # 开始时间
    end_time: datetime                   # 结束时间
    forming_xd: List[XianDuan]          # 构成中枢的线段
    level: TrendLevel                    # 所属级别
    extend_count: int = 0                # 扩展次数
    
    @property
    def range_ratio(self) -> float:
        """中枢区间比例"""
        return (self.high - self.low) / self.center if self.center > 0 else 0
    
    @property
    def duration_days(self) -> int:
        """中枢持续天数"""
        return (self.end_time - self.start_time).days
    
    def is_price_in_zhongshu(self, price: float) -> bool:
        """判断价格是否在中枢内"""
        return self.low <= price <= self.high
    
    def __str__(self):
        return f"中枢[{self.low:.2f}, {self.high:.2f}] 中心{self.center:.2f}"


@dataclass
class BollingerBands:
    """布林带数据（模拟缠论三线）"""
    upper: pd.Series                     # 上轨（压力线）
    middle: pd.Series                    # 中轨（趋势线）
    lower: pd.Series                     # 下轨（支撑线）
    level: TrendLevel                    # 所属级别
    
    def get_position_ratio(self, price: float, timestamp: datetime) -> float:
        """获取价格在布林带中的位置比例"""
        try:
            upper_val = self.upper.loc[timestamp]
            lower_val = self.lower.loc[timestamp]
            if upper_val > lower_val:
                return (price - lower_val) / (upper_val - lower_val)
            return 0.5
        except:
            return 0.5


@dataclass
class TrendAnalysisResult:
    """趋势分析结果"""
    symbol: str                          # 股票代码
    analysis_time: datetime              # 分析时间
    
    # 各级别分析结果
    level_results: Dict[TrendLevel, Dict[str, Any]]  # 各级别的详细结果
    
    # 多周期联立分析
    primary_trend: TrendDirection        # 主要趋势方向
    secondary_trend: TrendDirection      # 次级趋势方向
    short_term_trend: TrendDirection     # 短期趋势方向
    
    # 关键位置
    key_support_levels: List[float]      # 关键支撑位
    key_resistance_levels: List[float]   # 关键阻力位
    current_zhongshu: Optional[ZhongShu] # 当前中枢
    
    # 趋势强度评估
    trend_strength: float                # 趋势强度 (0-1)
    trend_consistency: float             # 多周期一致性 (0-1)
    
    # 操作建议
    operation_suggestion: str            # 操作建议
    risk_level: str                      # 风险等级
    
    def get_level_summary(self, level: TrendLevel) -> str:
        """获取指定级别的分析摘要"""
        if level not in self.level_results:
            return f"{level.value}级别：无数据"
        
        result = self.level_results[level]
        fenxing_count = result.get('fenxing_count', 0)
        bi_count = result.get('bi_count', 0)
        xd_count = result.get('xd_count', 0)
        zhongshu_count = result.get('zhongshu_count', 0)
        trend = result.get('trend_direction', 'unknown')
        
        return (f"{level.value}级别：{trend}趋势，"
                f"{fenxing_count}个分型，{bi_count}条笔，"
                f"{xd_count}条线段，{zhongshu_count}个中枢")
    
    def __str__(self):
        summary = f"缠论趋势分析 - {self.symbol}\n"
        summary += f"主要趋势：{self.primary_trend.value}\n"
        summary += f"次级趋势：{self.secondary_trend.value}\n"
        summary += f"短期趋势：{self.short_term_trend.value}\n"
        summary += f"趋势强度：{self.trend_strength:.2f}\n"
        summary += f"多周期一致性：{self.trend_consistency:.2f}\n"
        
        for level in TrendLevel:
            summary += f"{self.get_level_summary(level)}\n"
        
        summary += f"操作建议：{self.operation_suggestion}\n"
        summary += f"风险等级：{self.risk_level}"
        
        return summary