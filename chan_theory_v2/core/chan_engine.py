#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
缠论分析引擎 - 整合形态学和动力学分析
基于缠中说禅理论的完整实现，提供一站式缠论分析服务

核心功能：
1. 形态学分析：K线处理、分型识别、笔构建、线段构建、中枢构建
2. 动力学分析：MACD背驰、一二三类买卖点、多级别递归关系
3. 综合分析：走势预测、交易信号生成、风险评估
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple, Any, Union
from enum import Enum

# 形态学模块
from models.kline import KLine, KLineList
from models.fenxing import FenXing, FenXingList
from models.bi import Bi, BiList, BiBuilder, BiConfig
from models.seg import Seg, SegList, SegBuilder, SegConfig
from models.zhongshu import ZhongShu, ZhongShuList, ZhongShuBuilder, ZhongShuConfig
from models.enums import TimeLevel, BiDirection, SegDirection, ZhongShuType

# 动力学模块
from models.dynamics import (
    DynamicsAnalyzer, MultiLevelDynamicsAnalyzer, 
    BackChiAnalysis, BuySellPoint, BuySellPointType, BackChi,
    DynamicsConfig, MultiLevelAnalysis
)
# 缠论买卖点分析器
from models.chan_buy_sell_points import ChanBuySellPointAnalyzer, MultiLevelContext

# 核心处理器
from core.kline_processor import KlineProcessor
from config.chan_config import ChanConfig


class AnalysisLevel(Enum):
    """分析级别枚举"""
    BASIC = "basic"           # 基础分析：只做形态学
    STANDARD = "standard"     # 标准分析：形态学 + 动力学
    ADVANCED = "advanced"     # 高级分析：多级别递归关系
    COMPLETE = "complete"     # 完整分析：所有功能 + 预测


@dataclass
class ChanAnalysisResult:
    """缠论分析结果"""
    # 基础信息
    symbol: str
    time_level: TimeLevel
    analysis_time: datetime = field(default_factory=datetime.now)
    analysis_level: AnalysisLevel = AnalysisLevel.STANDARD
    
    # 形态学结果
    klines: KLineList = field(default_factory=KLineList)
    processed_klines: KLineList = field(default_factory=KLineList)
    fenxings: FenXingList = field(default_factory=FenXingList)
    bis: BiList = field(default_factory=BiList)
    segs: SegList = field(default_factory=SegList)
    zhongshus: ZhongShuList = field(default_factory=ZhongShuList)
    
    # 动力学结果
    backchi_analyses: List[BackChiAnalysis] = field(default_factory=list)
    buy_sell_points: List[BuySellPoint] = field(default_factory=list)
    
    # 多级别分析结果
    multi_level_results: Dict[TimeLevel, 'ChanAnalysisResult'] = field(default_factory=dict)
    level_consistency_score: float = 0.0
    
    # 综合评估
    trend_direction: Optional[str] = None    # "up", "down", "consolidation"
    trend_strength: float = 0.0              # 趋势强度 0-1
    risk_level: float = 0.0                  # 风险等级 0-1
    confidence_score: float = 0.0            # 分析可信度 0-1
    
    # 交易建议
    recommended_action: Optional[str] = None  # "buy", "sell", "hold", "wait"
    entry_price: Optional[float] = None
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取分析统计信息"""
        return {
            'symbol': self.symbol,
            'time_level': self.time_level.value,
            'analysis_level': self.analysis_level.value,
            'klines_count': len(self.klines),
            'processed_klines_count': len(self.processed_klines),
            'fenxings_count': len(self.fenxings),
            'bis_count': len(self.bis),
            'segs_count': len(self.segs),
            'zhongshus_count': len(self.zhongshus),
            'backchi_count': len(self.backchi_analyses),
            'buy_sell_points_count': len(self.buy_sell_points),
            'buy_points_count': len([p for p in self.buy_sell_points if p.point_type.is_buy()]),
            'sell_points_count': len([p for p in self.buy_sell_points if p.point_type.is_sell()]),
            'trend_direction': self.trend_direction,
            'trend_strength': self.trend_strength,
            'risk_level': self.risk_level,
            'confidence_score': self.confidence_score,
            'recommended_action': self.recommended_action
        }
    
    def get_latest_signals(self, count: int = 5) -> List[BuySellPoint]:
        """获取最新的买卖点信号"""
        sorted_points = sorted(self.buy_sell_points, key=lambda x: x.timestamp, reverse=True)
        return sorted_points[:count]
    
    def get_active_zhongshus(self) -> List[ZhongShu]:
        """获取活跃中枢"""
        return [zs for zs in self.zhongshus if not zs.is_finished]
    
    def has_valid_signals(self) -> bool:
        """是否有有效的交易信号"""
        return (len(self.buy_sell_points) > 0 and 
                any(p.reliability > 0.5 for p in self.buy_sell_points))


class ChanEngine:
    """
    缠论分析引擎
    整合形态学和动力学分析，提供完整的缠论分析服务
    """
    
    def __init__(self, 
                 chan_config: Optional[ChanConfig] = None,
                 dynamics_config: Optional[DynamicsConfig] = None):
        """
        初始化缠论引擎
        
        Args:
            chan_config: 缠论基础配置
            dynamics_config: 动力学分析配置
        """
        self.chan_config = chan_config or ChanConfig()
        self.dynamics_config = dynamics_config or DynamicsConfig()
        
        # 初始化处理器
        self.kline_processor = KlineProcessor(self.chan_config)
        self.bi_builder = BiBuilder(BiConfig())
        self.seg_builder = SegBuilder(SegConfig())
        self.zhongshu_builder = ZhongShuBuilder(ZhongShuConfig())
        
        # 初始化动力学分析器
        dynamics_config = self.dynamics_config.to_dict()
        self.dynamics_analyzer = DynamicsAnalyzer(dynamics_config)
        self.multi_level_analyzer = MultiLevelDynamicsAnalyzer(dynamics_config)
        
        # 初始化缠论买卖点分析器
        self.chan_bsp_analyzer = ChanBuySellPointAnalyzer()
        
        # 分析历史缓存
        self._analysis_cache: Dict[str, ChanAnalysisResult] = {}
    
    def analyze(self, 
               data: Union[List[Dict], KLineList],
               symbol: str,
               time_level: TimeLevel,
               analysis_level: AnalysisLevel = AnalysisLevel.STANDARD) -> ChanAnalysisResult:
        """
        执行缠论分析
        
        Args:
            data: K线数据或KLineList对象
            symbol: 股票代码
            time_level: 时间级别
            analysis_level: 分析级别
            
        Returns:
            分析结果
        """
        # 创建结果对象
        result = ChanAnalysisResult(
            symbol=symbol,
            time_level=time_level,
            analysis_level=analysis_level
        )
        
        # 数据预处理
        if isinstance(data, list):
            result.klines = KLineList.from_mongo_data(data, time_level)
        else:
            result.klines = data
        
        if len(result.klines) < 10:
            raise ValueError(f"数据量不足：需要至少10条K线，当前只有{len(result.klines)}条")
        
        # 执行形态学分析
        self._perform_morphology_analysis(result)
        
        # 根据分析级别执行相应分析
        if analysis_level in [AnalysisLevel.STANDARD, AnalysisLevel.ADVANCED, AnalysisLevel.COMPLETE]:
            self._perform_dynamics_analysis(result)
        
        if analysis_level in [AnalysisLevel.ADVANCED, AnalysisLevel.COMPLETE]:
            # 多级别分析需要额外数据，这里暂时跳过
            pass
        
        if analysis_level == AnalysisLevel.COMPLETE:
            self._perform_comprehensive_analysis(result)
        
        # 缓存结果
        cache_key = f"{symbol}_{time_level.value}_{analysis_level.value}"
        self._analysis_cache[cache_key] = result
        
        return result
    
    def analyze_multi_level(self,
                          level_data: Dict[TimeLevel, Union[List[Dict], KLineList]],
                          symbol: str) -> Dict[TimeLevel, ChanAnalysisResult]:
        """
        多级别分析
        
        Args:
            level_data: 各级别的K线数据
            symbol: 股票代码
            
        Returns:
            各级别的分析结果
        """
        results = {}
        
        # 单独分析各个级别
        for level, data in level_data.items():
            try:
                result = self.analyze(data, symbol, level, AnalysisLevel.STANDARD)
                results[level] = result
            except Exception as e:
                print(f"⚠️ {level.value}级别分析失败: {e}")
                continue
        
        # 多级别买卖点分析
        if len(results) >= 2:
            self._perform_multi_level_bsp_analysis(results)
            self._analyze_multi_level_relations(results)
        
        return results
    
    def _perform_multi_level_bsp_analysis(self, results: Dict[TimeLevel, ChanAnalysisResult]) -> None:
        """执行多级别买卖点分析"""
        try:
            # 构建多级别上下文
            contexts = {}
            for level, result in results.items():
                contexts[level] = MultiLevelContext(
                    time_level=level,
                    klines=result.processed_klines,
                    bis=result.bis,
                    segs=result.segs,
                    zhongshus=result.zhongshus
                )
            
            # 执行多级别买卖点分析
            all_bsp = self.chan_bsp_analyzer.analyze_multi_level_bsp(contexts)
            
            # 更新各级别的买卖点结果
            for level, bsp_list in all_bsp.items():
                if level in results:
                    results[level].buy_sell_points = bsp_list
                    
        except Exception as e:
            print(f"⚠️ 多级别买卖点分析失败: {e}")
    
    def get_trading_signals(self, result: ChanAnalysisResult) -> Dict[str, Any]:
        """
        生成交易信号
        
        Args:
            result: 分析结果
            
        Returns:
            交易信号信息
        """
        signals = {
            'symbol': result.symbol,
            'timestamp': datetime.now(),
            'signals': [],
            'summary': {
                'total_signals': 0,
                'buy_signals': 0,
                'sell_signals': 0,
                'high_confidence_signals': 0
            }
        }
        
        # 处理买卖点信号
        for point in result.buy_sell_points:
            if point.reliability >= self.dynamics_config.min_reliability:
                signal = {
                    'type': 'buy' if point.point_type.is_buy() else 'sell',
                    'point_type': str(point.point_type),
                    'price': point.price,
                    'timestamp': point.timestamp,
                    'reliability': point.reliability,
                    'strength': point.strength,
                    'confirmed': point.confirmed_by_higher_level or point.confirmed_by_lower_level
                }
                signals['signals'].append(signal)
                
                # 统计
                signals['summary']['total_signals'] += 1
                if point.point_type.is_buy():
                    signals['summary']['buy_signals'] += 1
                else:
                    signals['summary']['sell_signals'] += 1
                
                if point.reliability > 0.7:
                    signals['summary']['high_confidence_signals'] += 1
        
        # 处理背驰信号
        for backchi in result.backchi_analyses:
            if backchi.is_valid_backchi():
                signal = {
                    'type': 'backchi',
                    'backchi_type': str(backchi.backchi_type),
                    'reliability': backchi.reliability,
                    'current_strength': backchi.current_strength
                }
                signals['signals'].append(signal)
                signals['summary']['total_signals'] += 1
        
        return signals
    
    def _perform_morphology_analysis(self, result: ChanAnalysisResult) -> None:
        """执行形态学分析"""
        # K线处理和分型识别
        processed_klines, fenxings = self.kline_processor.process_klines(result.klines)
        result.processed_klines = processed_klines  # KlineProcessor已返回KLineList
        result.fenxings = fenxings  # KlineProcessor已返回FenXingList
        
        # 构建笔
        if len(fenxings) >= 2:
            bis = self.bi_builder.build_from_fenxings(fenxings.fenxings)  # 传递fenxing列表
            result.bis = BiList(bis)
        
        # 构建线段
        if len(result.bis) >= 3:
            segs = self.seg_builder.build_from_bis(result.bis.bis)
            result.segs = SegList(segs, result.time_level)
        
        # 构建中枢
        if len(result.segs) >= 3:
            zhongshus = self.zhongshu_builder.build_from_segs(result.segs.segs)
            result.zhongshus = ZhongShuList(zhongshus)
    
    def _perform_dynamics_analysis(self, result: ChanAnalysisResult) -> None:
        """执行动力学分析"""
        if len(result.processed_klines) < 20:
            return
        
        # 背驰分析
        result.backchi_analyses = self.dynamics_analyzer.analyze_simple_backchi(
            result.processed_klines
        )
        
        # 缠论买卖点识别：使用独立的缠论分析器
        context = MultiLevelContext(
            time_level=result.time_level,
            klines=result.processed_klines,
            bis=result.bis,
            segs=result.segs,
            zhongshus=result.zhongshus
        )
        
        # 单级别买卖点分析
        bsp_results = self.chan_bsp_analyzer.analyze_multi_level_bsp({
            result.time_level: context
        })
        
        result.buy_sell_points = bsp_results.get(result.time_level, [])
    
    def _perform_comprehensive_analysis(self, result: ChanAnalysisResult) -> None:
        """执行综合分析"""
        # 趋势方向判断
        result.trend_direction = self._determine_trend_direction(result)
        
        # 趋势强度计算
        result.trend_strength = self._calculate_trend_strength(result)
        
        # 风险评估
        result.risk_level = self._assess_risk_level(result)
        
        # 可信度评分
        result.confidence_score = self._calculate_confidence_score(result)
        
        # 交易建议
        self._generate_trading_recommendation(result)
    
    def _determine_trend_direction(self, result: ChanAnalysisResult) -> str:
        """判断趋势方向"""
        if len(result.segs) < 2:
            return "consolidation"
        
        # 获取最近的线段
        recent_segs = result.segs.segs[-3:] if len(result.segs) >= 3 else result.segs.segs
        
        up_segs = [seg for seg in recent_segs if seg.is_up]
        down_segs = [seg for seg in recent_segs if seg.is_down]
        
        if len(up_segs) > len(down_segs):
            return "up"
        elif len(down_segs) > len(up_segs):
            return "down"
        else:
            return "consolidation"
    
    def _calculate_trend_strength(self, result: ChanAnalysisResult) -> float:
        """计算趋势强度"""
        if len(result.segs) == 0:
            return 0.0
        
        # 基于线段强度和方向一致性
        avg_strength = sum(seg.strength for seg in result.segs) / len(result.segs)
        
        # 方向一致性
        if result.trend_direction == "consolidation":
            direction_consistency = 0.5
        else:
            target_direction = SegDirection.UP if result.trend_direction == "up" else SegDirection.DOWN
            consistent_segs = [seg for seg in result.segs if seg.direction == target_direction]
            direction_consistency = len(consistent_segs) / len(result.segs)
        
        return (avg_strength * 0.6 + direction_consistency * 0.4)
    
    def _assess_risk_level(self, result: ChanAnalysisResult) -> float:
        """评估风险等级"""
        risk_factors = []
        
        # 背驰风险
        valid_backchis = [b for b in result.backchi_analyses if b.is_valid_backchi()]
        if valid_backchis:
            avg_backchi_reliability = sum(b.reliability for b in valid_backchis) / len(valid_backchis)
            risk_factors.append(avg_backchi_reliability)
        
        # 中枢稳定性风险
        if result.zhongshus:
            avg_stability = sum(zs.stability for zs in result.zhongshus) / len(result.zhongshus)
            risk_factors.append(1.0 - avg_stability)
        
        # 趋势强度风险
        risk_factors.append(1.0 - result.trend_strength)
        
        return sum(risk_factors) / len(risk_factors) if risk_factors else 0.5
    
    def _calculate_confidence_score(self, result: ChanAnalysisResult) -> float:
        """计算分析可信度"""
        confidence_factors = []
        
        # 数据量充足性
        data_adequacy = min(1.0, len(result.processed_klines) / 100)
        confidence_factors.append(data_adequacy)
        
        # 结构完整性
        structure_completeness = 0.0
        if len(result.fenxings) > 0:
            structure_completeness += 0.2
        if len(result.bis) > 0:
            structure_completeness += 0.2  
        if len(result.segs) > 0:
            structure_completeness += 0.3
        if len(result.zhongshus) > 0:
            structure_completeness += 0.3
        confidence_factors.append(structure_completeness)
        
        # 信号质量
        if result.buy_sell_points:
            avg_signal_reliability = sum(p.reliability for p in result.buy_sell_points) / len(result.buy_sell_points)
            confidence_factors.append(avg_signal_reliability)
        else:
            confidence_factors.append(0.5)
        
        return sum(confidence_factors) / len(confidence_factors)
    
    def _generate_trading_recommendation(self, result: ChanAnalysisResult) -> None:
        """生成交易建议"""
        # 基于买卖点和趋势方向生成建议
        latest_points = result.get_latest_signals(3)
        
        if not latest_points:
            result.recommended_action = "wait"
            return
        
        latest_point = latest_points[0]
        
        if (latest_point.point_type.is_buy() and 
            latest_point.reliability > 0.6 and
            result.trend_direction in ["up", "consolidation"]):
            result.recommended_action = "buy"
            result.entry_price = latest_point.price
            
            # 设置止损和止盈
            if result.zhongshus:
                latest_zhongshu = result.zhongshus[-1]
                result.stop_loss = latest_zhongshu.low * 0.98
                result.take_profit = latest_point.price * 1.1
            
        elif (latest_point.point_type.is_sell() and 
              latest_point.reliability > 0.6 and
              result.trend_direction in ["down", "consolidation"]):
            result.recommended_action = "sell"
            result.entry_price = latest_point.price
            
            # 设置止损和止盈
            if result.zhongshus:
                latest_zhongshu = result.zhongshus[-1]
                result.stop_loss = latest_zhongshu.high * 1.02
                result.take_profit = latest_point.price * 0.9
        else:
            result.recommended_action = "hold"
    
    def _analyze_multi_level_relations(self, results: Dict[TimeLevel, ChanAnalysisResult]) -> None:
        """分析多级别关系和买卖点确认"""
        if len(results) < 2:
            return
            
        # 按时间级别排序（日线 > 30分钟 > 5分钟）
        sorted_levels = sorted(results.keys(), key=lambda x: {
            TimeLevel.DAILY: 3,
            TimeLevel.MIN_30: 2, 
            TimeLevel.MIN_5: 1
        }.get(x, 0), reverse=True)
        
        # 进行多级别买卖点确认
        for i in range(len(sorted_levels) - 1):
            higher_level = sorted_levels[i]
            lower_level = sorted_levels[i + 1]
            
            higher_result = results[higher_level]
            lower_result = results[lower_level]
            
            # 用高级别确认低级别买卖点
            self._confirm_buy_sell_points_across_levels(higher_result, lower_result, True)
            
            # 用低级别确认高级别买卖点
            self._confirm_buy_sell_points_across_levels(lower_result, higher_result, False)
            
        # 计算级别一致性得分
        self._calculate_level_consistency_scores(results)
    
    def _confirm_buy_sell_points_across_levels(self, 
                                             confirming_result: ChanAnalysisResult,
                                             target_result: ChanAnalysisResult,
                                             is_higher_level_confirm: bool) -> None:
        """跨级别买卖点确认"""
        time_window = timedelta(days=7)  # 7天时间窗口
        
        for target_point in target_result.buy_sell_points:
            for confirm_point in confirming_result.buy_sell_points:
                # 检查时间接近和信号方向一致
                time_diff = abs((target_point.timestamp - confirm_point.timestamp).total_seconds())
                is_same_direction = (target_point.point_type.is_buy() == confirm_point.point_type.is_buy())
                
                if time_diff <= time_window.total_seconds() and is_same_direction:
                    if is_higher_level_confirm:
                        target_point.confirmed_by_higher_level = True
                        # 高级别确认提升可靠度
                        target_point.reliability = min(target_point.reliability + 0.2, 1.0)
                    else:
                        target_point.confirmed_by_lower_level = True
                        # 低级别确认适度提升可靠度
                        target_point.reliability = min(target_point.reliability + 0.1, 1.0)
    
    def _calculate_level_consistency_scores(self, results: Dict[TimeLevel, ChanAnalysisResult]) -> None:
        """计算级别一致性得分"""
        for level, result in results.items():
            # 统计确认情况
            total_points = len(result.buy_sell_points)
            if total_points == 0:
                result.level_consistency_score = 0.0
                continue
                
            confirmed_points = sum(1 for point in result.buy_sell_points 
                                 if point.confirmed_by_higher_level or point.confirmed_by_lower_level)
            
            result.level_consistency_score = confirmed_points / total_points
    
    def get_analysis_summary(self, result: ChanAnalysisResult) -> str:
        """获取分析摘要"""
        stats = result.get_statistics()
        
        summary = f"""
🔍 缠论分析报告 - {stats['symbol']} ({stats['time_level']})
{'='*50}
📊 形态学分析:
  • K线处理: {stats['klines_count']} → {stats['processed_klines_count']} 根
  • 分型识别: {stats['fenxings_count']} 个
  • 笔构建: {stats['bis_count']} 个  
  • 线段构建: {stats['segs_count']} 个
  • 中枢构建: {stats['zhongshus_count']} 个

🎯 动力学分析:
  • 背驰分析: {stats['backchi_count']} 个
  • 买卖点识别: {stats['buy_sell_points_count']} 个
    - 买点: {stats['buy_points_count']} 个
    - 卖点: {stats['sell_points_count']} 个

📈 综合评估:
  • 趋势方向: {stats['trend_direction'] or '未确定'}
  • 趋势强度: {stats['trend_strength']:.1%}
  • 风险等级: {stats['risk_level']:.1%}
  • 可信度: {stats['confidence_score']:.1%}
  • 交易建议: {stats['recommended_action'] or '暂无'}
        """
        
        # 最新信号
        latest_signals = result.get_latest_signals(3)
        if latest_signals:
            summary += "\n🚨 最新交易信号:\n"
            for i, signal in enumerate(latest_signals, 1):
                summary += f"  {i}. {signal.point_type} @{signal.price:.2f} (可靠度:{signal.reliability:.1%})\n"
        
        return summary.strip()
    
    def clear_cache(self) -> None:
        """清空分析缓存"""
        self._analysis_cache.clear()


# 便捷函数
def quick_analyze(data: Union[List[Dict], KLineList], 
                 symbol: str, 
                 time_level: TimeLevel) -> ChanAnalysisResult:
    """快速缠论分析"""
    engine = ChanEngine()
    return engine.analyze(data, symbol, time_level, AnalysisLevel.STANDARD)


def multi_level_analyze(level_data: Dict[TimeLevel, Union[List[Dict], KLineList]], 
                       symbol: str) -> Dict[TimeLevel, ChanAnalysisResult]:
    """多级别缠论分析"""
    engine = ChanEngine()
    return engine.analyze_multi_level(level_data, symbol)