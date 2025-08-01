#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
缠论动力学分析模块
实现缠论的动力学原理：背驰分析、MACD辅助判断、一二三类买卖点识别

基于缠中说禅《教你炒股票》系列理论和网络最佳实践
核心功能：
1. MACD背驰分析
2. 一二三类买卖点识别  
3. 多级别动力学关系判定
4. 走势力度计算和比较
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Optional, Tuple, Any
from enum import Enum
import numpy as np
from abc import ABC, abstractmethod

from .enums import TimeLevel, BiDirection, SegDirection, ZhongShuType
from .kline import KLine, KLineList
from .bi import Bi, BiList
from .seg import Seg, SegList  
from .zhongshu import ZhongShu, ZhongShuList


class BackChi(Enum):
    """背驰类型枚举"""
    NONE = "none"              # 无背驰
    TOP_BACKCHI = "top"        # 顶背驰
    BOTTOM_BACKCHI = "bottom"  # 底背驰
    
    def is_backchi(self) -> bool:
        return self != self.NONE
    
    def __str__(self) -> str:
        names = {
            self.NONE: "无背驰",
            self.TOP_BACKCHI: "顶背驰", 
            self.BOTTOM_BACKCHI: "底背驰"
        }
        return names.get(self, self.value)


class BuySellPointType(Enum):
    """买卖点类型枚举"""
    # 买点
    BUY_1 = "1buy"    # 一类买点：跌势转向上涨或盘整的起点
    BUY_2 = "2buy"    # 二类买点：第一类买点后首次次级别回调低点  
    BUY_3 = "3buy"    # 三类买点：次级别走势向上离开中枢后，回试不穿越中枢高点
    
    # 卖点
    SELL_1 = "1sell"  # 一类卖点：涨势转向下跌或盘整的起点
    SELL_2 = "2sell"  # 二类卖点：第一类卖点后首次次级别回调高点
    SELL_3 = "3sell"  # 三类卖点：次级别走势向下离开中枢后，回试不穿越中枢低点
    
    def is_buy(self) -> bool:
        return self in [self.BUY_1, self.BUY_2, self.BUY_3]
    
    def is_sell(self) -> bool:
        return self in [self.SELL_1, self.SELL_2, self.SELL_3]
    
    def get_level(self) -> int:
        return int(self.value[0])
    
    def __str__(self) -> str:
        names = {
            self.BUY_1: "一类买点", self.BUY_2: "二类买点", self.BUY_3: "三类买点",
            self.SELL_1: "一类卖点", self.SELL_2: "二类卖点", self.SELL_3: "三类卖点"
        }
        return names.get(self, self.value)


@dataclass
class MacdData:
    """MACD指标数据"""
    dif: float          # DIF线 (12日EMA - 26日EMA)
    dea: float          # DEA线 (DIF的9日EMA)  
    macd: float         # MACD柱 (DIF - DEA) * 2
    timestamp: datetime
    
    @property
    def is_above_zero(self) -> bool:
        """MACD是否在0轴上方"""
        return self.dif > 0 and self.dea > 0
    
    @property
    def is_golden_cross(self) -> bool:
        """是否为金叉(DIF上穿DEA)"""
        return self.dif > self.dea and self.macd > 0
    
    @property
    def is_death_cross(self) -> bool:
        """是否为死叉(DIF下穿DEA)"""
        return self.dif < self.dea and self.macd < 0


@dataclass
class BuySellPoint:
    """买卖点数据结构"""
    point_type: BuySellPointType
    timestamp: datetime
    price: float
    kline_index: int
    
    # 相关结构信息
    related_zhongshu: Optional[ZhongShu] = None
    related_seg: Optional[Seg] = None
    related_bi: Optional[Bi] = None
    
    # 动力学信息
    macd_data: Optional[MacdData] = None
    backchi_type: BackChi = BackChi.NONE
    strength: float = 0.0           # 买卖点强度
    reliability: float = 0.0        # 可靠度
    
    # 多级别确认
    confirmed_by_higher_level: bool = False
    confirmed_by_lower_level: bool = False
    
    def __str__(self) -> str:
        return f"{self.point_type} @{self.price:.2f} ({self.timestamp.strftime('%Y-%m-%d %H:%M')})"


@dataclass  
class BackChiAnalysis:
    """背驰分析结果"""
    backchi_type: BackChi
    current_seg: Seg
    previous_seg: Seg
    zhongshu: ZhongShu
    
    # MACD分析数据
    current_macd_area: float        # 当前段MACD面积
    previous_macd_area: float       # 前一段MACD面积
    macd_divergence: float          # MACD背离度
    
    # 力度分析
    current_strength: float         # 当前段力度
    previous_strength: float        # 前一段力度
    strength_ratio: float           # 力度比值
    
    reliability: float = 0.0        # 背驰可靠度
    
    def is_valid_backchi(self) -> bool:
        """是否为有效背驰"""
        return (self.backchi_type.is_backchi() and 
                self.reliability > 0.6 and
                abs(self.strength_ratio - 1.0) > 0.1)


class MacdCalculator:
    """MACD计算器"""
    
    def __init__(self, fast_period: int = 12, slow_period: int = 26, signal_period: int = 9):
        self.fast_period = fast_period
        self.slow_period = slow_period
        self.signal_period = signal_period
    
    def calculate(self, prices: List[float]) -> List[MacdData]:
        """计算MACD指标"""
        if len(prices) < self.slow_period + self.signal_period:
            return []
        
        # 计算EMA
        fast_ema = self._calculate_ema(prices, self.fast_period)
        slow_ema = self._calculate_ema(prices, self.slow_period)
        
        # 计算DIF
        dif_values = [fast - slow for fast, slow in zip(fast_ema, slow_ema)]
        
        # 计算DEA
        dea_values = self._calculate_ema(dif_values, self.signal_period)
        
        # 计算MACD
        macd_values = [(dif - dea) * 2 for dif, dea in zip(dif_values, dea_values)]
        
        # 构造结果
        result = []
        start_idx = max(self.slow_period, self.signal_period) - 1
        for i in range(start_idx, len(prices)):
            result.append(MacdData(
                dif=dif_values[i],
                dea=dea_values[i], 
                macd=macd_values[i],
                timestamp=datetime.now()  # 实际使用时需要传入对应时间
            ))
        
        return result
    
    def _calculate_ema(self, values: List[float], period: int) -> List[float]:
        """计算指数移动平均"""
        if len(values) < period:
            return []
        
        multiplier = 2.0 / (period + 1)
        ema = [sum(values[:period]) / period]  # 初始值使用简单平均
        
        for i in range(period, len(values)):
            ema.append((values[i] * multiplier) + (ema[-1] * (1 - multiplier)))
        
        # 补充前面的值
        result = [0.0] * (period - 1) + ema
        return result


class DynamicsAnalyzer:
    """动力学分析器 - 缠论动力学分析的核心类"""
    
    def __init__(self, macd_params: Tuple[int, int, int] = (12, 26, 9)):
        self.macd_calculator = MacdCalculator(*macd_params)
        self.macd_data_cache: Dict[str, List[MacdData]] = {}
    
    def analyze_backchi(self, 
                       segs: SegList, 
                       zhongshus: ZhongShuList,
                       klines: KLineList) -> List[BackChiAnalysis]:
        """
        分析背驰
        
        背驰分析的核心原理：
        1. 必须有中枢作为比较基准
        2. 比较中枢前后两段的力度
        3. 后段力度明显小于前段力度则形成背驰
        """
        if len(segs) < 3 or len(zhongshus) == 0:
            return []
        
        # 计算MACD数据
        close_prices = [kline.close for kline in klines]
        macd_data = self.macd_calculator.calculate(close_prices)
        
        backchi_results = []
        
        for zhongshu in zhongshus:
            # 查找中枢前后的线段
            before_segs = [seg for seg in segs if seg.end_time <= zhongshu.start_time][-2:]
            after_segs = [seg for seg in segs if seg.start_time >= zhongshu.end_time][:2]
            
            if len(before_segs) >= 1 and len(after_segs) >= 1:
                # 比较中枢前后线段的背驰
                for i in range(len(after_segs)):
                    current_seg = after_segs[i]
                    
                    # 选择比较的前段线段
                    if len(before_segs) > 1 and i == 0:
                        previous_seg = before_segs[-1]
                    elif len(before_segs) >= 1:
                        previous_seg = before_segs[-1] 
                    else:
                        continue
                    
                    # 必须是同向线段才能比较
                    if current_seg.direction != previous_seg.direction:
                        continue
                    
                    backchi = self._analyze_seg_backchi(
                        current_seg, previous_seg, zhongshu, macd_data, klines
                    )
                    
                    if backchi and backchi.is_valid_backchi():
                        backchi_results.append(backchi)
        
        return backchi_results
    
    def _analyze_seg_backchi(self, 
                           current_seg: Seg,
                           previous_seg: Seg, 
                           zhongshu: ZhongShu,
                           macd_data: List[MacdData],
                           klines: KLineList) -> Optional[BackChiAnalysis]:
        """分析两个线段之间的背驰"""
        
        # 计算线段对应的MACD面积
        current_macd_area = self._calculate_macd_area(current_seg, macd_data, klines)
        previous_macd_area = self._calculate_macd_area(previous_seg, macd_data, klines)
        
        if current_macd_area == 0 or previous_macd_area == 0:
            return None
        
        # 计算背离度
        macd_divergence = abs(current_macd_area - previous_macd_area) / max(abs(current_macd_area), abs(previous_macd_area))
        
        # 计算线段力度
        current_strength = self._calculate_seg_strength(current_seg)
        previous_strength = self._calculate_seg_strength(previous_seg)
        strength_ratio = current_strength / previous_strength if previous_strength > 0 else 1.0
        
        # 判断背驰类型
        backchi_type = BackChi.NONE
        if current_seg.is_up:
            # 上升线段：价格创新高但MACD面积减小
            if (current_seg.end_price > previous_seg.end_price and 
                current_macd_area < previous_macd_area * 0.8):
                backchi_type = BackChi.TOP_BACKCHI
        else:
            # 下降线段：价格创新低但MACD面积减小  
            if (current_seg.end_price < previous_seg.end_price and
                abs(current_macd_area) < abs(previous_macd_area) * 0.8):
                backchi_type = BackChi.BOTTOM_BACKCHI
        
        # 计算可靠度
        reliability = self._calculate_backchi_reliability(
            current_seg, previous_seg, macd_divergence, strength_ratio
        )
        
        return BackChiAnalysis(
            backchi_type=backchi_type,
            current_seg=current_seg,
            previous_seg=previous_seg,
            zhongshu=zhongshu,
            current_macd_area=current_macd_area,
            previous_macd_area=previous_macd_area,
            macd_divergence=macd_divergence,
            current_strength=current_strength,
            previous_strength=previous_strength,
            strength_ratio=strength_ratio,
            reliability=reliability
        )
    
    def _calculate_macd_area(self, seg: Seg, macd_data: List[MacdData], klines: KLineList) -> float:
        """计算线段对应的MACD面积"""
        if not macd_data:
            return 0.0
        
        # 找到线段对应的K线范围
        start_idx = None
        end_idx = None
        
        for i, kline in enumerate(klines):
            if start_idx is None and kline.timestamp >= seg.start_time:
                start_idx = i
            if kline.timestamp <= seg.end_time:
                end_idx = i
        
        if start_idx is None or end_idx is None or start_idx >= len(macd_data):
            return 0.0
        
        # 计算MACD柱的面积（绝对值之和）
        macd_area = 0.0
        macd_start_idx = max(0, start_idx - len(klines) + len(macd_data))
        macd_end_idx = min(len(macd_data) - 1, end_idx - len(klines) + len(macd_data))
        
        for i in range(macd_start_idx, macd_end_idx + 1):
            if 0 <= i < len(macd_data):
                macd_area += abs(macd_data[i].macd)
        
        return macd_area
    
    def _calculate_seg_strength(self, seg: Seg) -> float:
        """计算线段力度"""
        # 综合考虑价格幅度、时间长度、成交量等因素
        price_amplitude = abs(seg.end_price - seg.start_price) / seg.start_price
        time_factor = 1.0 / max(1, seg.duration)  # 时间越短力度越大
        
        return price_amplitude * time_factor * seg.strength
    
    def _calculate_backchi_reliability(self, 
                                     current_seg: Seg,
                                     previous_seg: Seg, 
                                     macd_divergence: float,
                                     strength_ratio: float) -> float:
        """计算背驰可靠度"""
        reliability = 0.0
        
        # MACD背离度贡献
        reliability += min(macd_divergence * 2, 0.4)
        
        # 力度比值贡献
        strength_factor = abs(1.0 - strength_ratio)
        reliability += min(strength_factor * 2, 0.3)
        
        # 线段质量贡献
        seg_quality = (current_seg.integrity + previous_seg.integrity) / 2
        reliability += seg_quality * 0.3
        
        return min(reliability, 1.0)
    
    def identify_buy_sell_points(self,
                               backchi_analyses: List[BackChiAnalysis],
                               segs: SegList,
                               zhongshus: ZhongShuList,
                               klines: KLineList) -> List[BuySellPoint]:
        """识别一二三类买卖点"""
        buy_sell_points = []
        
        # 1类买卖点：背驰转折点
        for backchi in backchi_analyses:
            if backchi.is_valid_backchi():
                point_type = (BuySellPointType.BUY_1 if backchi.backchi_type == BackChi.BOTTOM_BACKCHI 
                            else BuySellPointType.SELL_1)
                
                point = BuySellPoint(
                    point_type=point_type,
                    timestamp=backchi.current_seg.end_time,
                    price=backchi.current_seg.end_price,
                    kline_index=0,  # 需要实际计算
                    related_zhongshu=backchi.zhongshu,
                    related_seg=backchi.current_seg,
                    backchi_type=backchi.backchi_type,
                    strength=backchi.current_strength,
                    reliability=backchi.reliability
                )
                buy_sell_points.append(point)
        
        # 2类买卖点：第一类买卖点后的回调确认
        buy_sell_points.extend(self._identify_second_buy_sell_points(buy_sell_points, segs, zhongshus))
        
        # 3类买卖点：中枢突破后的回试
        buy_sell_points.extend(self._identify_third_buy_sell_points(segs, zhongshus))
        
        return sorted(buy_sell_points, key=lambda x: x.timestamp)
    
    def _identify_second_buy_sell_points(self, 
                                       first_points: List[BuySellPoint],
                                       segs: SegList,
                                       zhongshus: ZhongShuList) -> List[BuySellPoint]:
        """识别二类买卖点"""
        second_points = []
        
        for first_point in first_points:
            if not first_point.point_type in [BuySellPointType.BUY_1, BuySellPointType.SELL_1]:
                continue
            
            # 查找第一类买卖点后的首次回调
            is_buy_point = first_point.point_type == BuySellPointType.BUY_1
            
            for seg in segs:
                if seg.start_time <= first_point.timestamp:
                    continue
                
                # 找到反向的第一个线段作为回调
                if ((is_buy_point and seg.is_down) or 
                    (not is_buy_point and seg.is_up)):
                    
                    point_type = BuySellPointType.BUY_2 if is_buy_point else BuySellPointType.SELL_2
                    
                    second_point = BuySellPoint(
                        point_type=point_type,
                        timestamp=seg.end_time,
                        price=seg.end_price,
                        kline_index=0,
                        related_seg=seg,
                        related_zhongshu=first_point.related_zhongshu,
                        strength=seg.strength,
                        reliability=0.7  # 二类买卖点相对可靠
                    )
                    second_points.append(second_point)
                    break
        
        return second_points
    
    def _identify_third_buy_sell_points(self, 
                                      segs: SegList,
                                      zhongshus: ZhongShuList) -> List[BuySellPoint]:
        """识别三类买卖点"""
        third_points = []
        
        for zhongshu in zhongshus:
            # 查找突破中枢的线段
            breakout_segs = [seg for seg in segs if seg.start_time >= zhongshu.end_time]
            
            for i, seg in enumerate(breakout_segs[:3]):  # 只看前3个线段
                # 向上突破后的回试
                if (seg.is_up and seg.start_price > zhongshu.high and 
                    i + 1 < len(breakout_segs)):
                    
                    next_seg = breakout_segs[i + 1]
                    if (next_seg.is_down and 
                        next_seg.end_price > zhongshu.high):  # 回试不破中枢上沿
                        
                        third_point = BuySellPoint(
                            point_type=BuySellPointType.BUY_3,
                            timestamp=next_seg.end_time,
                            price=next_seg.end_price,
                            kline_index=0,
                            related_seg=next_seg,
                            related_zhongshu=zhongshu,
                            strength=next_seg.strength,
                            reliability=0.6  # 三类买卖点相对风险较高
                        )
                        third_points.append(third_point)
                
                # 向下突破后的回试
                elif (seg.is_down and seg.start_price < zhongshu.low and
                      i + 1 < len(breakout_segs)):
                    
                    next_seg = breakout_segs[i + 1]
                    if (next_seg.is_up and 
                        next_seg.end_price < zhongshu.low):  # 回试不破中枢下沿
                        
                        third_point = BuySellPoint(
                            point_type=BuySellPointType.SELL_3,
                            timestamp=next_seg.end_time,
                            price=next_seg.end_price,
                            kline_index=0,
                            related_seg=next_seg,
                            related_zhongshu=zhongshu,
                            strength=next_seg.strength,
                            reliability=0.6
                        )
                        third_points.append(third_point)
        
        return third_points


@dataclass
class MultiLevelAnalysis:
    """多级别分析结果"""
    time_level: TimeLevel
    backchi_analyses: List[BackChiAnalysis] 
    buy_sell_points: List[BuySellPoint]
    
    # 级别间关系
    higher_level_confirmation: bool = False
    lower_level_confirmation: bool = False
    level_consistency_score: float = 0.0


class MultiLevelDynamicsAnalyzer:
    """多级别动力学分析器"""
    
    def __init__(self):
        self.analyzers: Dict[TimeLevel, DynamicsAnalyzer] = {
            TimeLevel.MIN_5: DynamicsAnalyzer(),
            TimeLevel.MIN_30: DynamicsAnalyzer(), 
            TimeLevel.DAILY: DynamicsAnalyzer()
        }
    
    def analyze_multi_level_dynamics(self,
                                   level_data: Dict[TimeLevel, Tuple[SegList, ZhongShuList, KLineList]]
                                   ) -> Dict[TimeLevel, MultiLevelAnalysis]:
        """多级别动力学分析"""
        results = {}
        
        # 单独分析各个级别
        for level, (segs, zhongshus, klines) in level_data.items():
            analyzer = self.analyzers[level]
            
            backchi_analyses = analyzer.analyze_backchi(segs, zhongshus, klines)
            buy_sell_points = analyzer.identify_buy_sell_points(
                backchi_analyses, segs, zhongshus, klines
            )
            
            results[level] = MultiLevelAnalysis(
                time_level=level,
                backchi_analyses=backchi_analyses,
                buy_sell_points=buy_sell_points
            )
        
        # 分析级别间关系
        self._analyze_level_relationships(results)
        
        return results
    
    def _analyze_level_relationships(self, 
                                   results: Dict[TimeLevel, MultiLevelAnalysis]) -> None:
        """分析多级别间的递归关系"""
        levels = [TimeLevel.DAILY, TimeLevel.MIN_30, TimeLevel.MIN_5]
        
        for i, level in enumerate(levels):
            if level not in results:
                continue
            
            current_result = results[level]
            
            # 检查高级别确认
            if i > 0:
                higher_level = levels[i-1]
                if higher_level in results:
                    current_result.higher_level_confirmation = self._check_level_confirmation(
                        results[higher_level], current_result
                    )
            
            # 检查低级别确认  
            if i < len(levels) - 1:
                lower_level = levels[i+1]
                if lower_level in results:
                    current_result.lower_level_confirmation = self._check_level_confirmation(
                        current_result, results[lower_level]
                    )
            
            # 计算级别一致性得分
            current_result.level_consistency_score = self._calculate_consistency_score(
                current_result, results
            )
    
    def _check_level_confirmation(self, 
                                high_level: MultiLevelAnalysis,
                                low_level: MultiLevelAnalysis) -> bool:
        """检查级别间确认关系"""
        # 简化的确认逻辑：同方向的买卖点在时间上相近
        for high_point in high_level.buy_sell_points:
            for low_point in low_level.buy_sell_points:
                if (high_point.point_type.is_buy() == low_point.point_type.is_buy() and
                    abs((high_point.timestamp - low_point.timestamp).total_seconds()) < 86400 * 7):  # 7天内
                    return True
        return False
    
    def _calculate_consistency_score(self, 
                                   current: MultiLevelAnalysis,
                                   all_results: Dict[TimeLevel, MultiLevelAnalysis]) -> float:
        """计算级别一致性得分"""
        score = 0.0
        count = 0
        
        if current.higher_level_confirmation:
            score += 0.4
            count += 1
        
        if current.lower_level_confirmation:
            score += 0.3
            count += 1
        
        # 背驰一致性
        if len(current.backchi_analyses) > 0:
            score += 0.3
            count += 1
        
        return score / max(count, 1)


# 配置类
@dataclass
class DynamicsConfig:
    """动力学分析配置"""
    macd_params: Tuple[int, int, int] = (12, 26, 9)
    backchi_threshold: float = 0.6      # 背驰可靠度阈值
    strength_ratio_threshold: float = 0.1  # 力度比值阈值
    
    # 买卖点识别参数
    buy_sell_point_min_reliability: float = 0.5
    multi_level_confirmation_window_days: int = 7
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'macd_params': self.macd_params,
            'backchi_threshold': self.backchi_threshold,
            'strength_ratio_threshold': self.strength_ratio_threshold,
            'buy_sell_point_min_reliability': self.buy_sell_point_min_reliability,
            'multi_level_confirmation_window_days': self.multi_level_confirmation_window_days
        }