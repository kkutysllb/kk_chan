#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
缠论多周期分析器
实现多周期联立分析，识别次级趋势与上一级趋势的关系
"""

from datetime import datetime
from typing import Dict, List, Optional, Tuple
import pandas as pd
import numpy as np

import sys
import os

# 添加路径
current_dir = os.path.dirname(os.path.abspath(__file__))
chan_theory_dir = os.path.dirname(current_dir)
sys.path.append(chan_theory_dir)

try:
    from models.chan_theory_models import (
        TrendLevel, FenXing, Bi, XianDuan, ZhongShu, BollingerBands,
        FenXingType, TrendDirection, ChanTheoryConfig
    )
    from analyzers.structure_analyzer import ChanStructureAnalyzer
except ImportError:
    from analysis.chan_theory.models.chan_theory_models import (
        TrendLevel, FenXing, Bi, XianDuan, ZhongShu, BollingerBands,
        FenXingType, TrendDirection, ChanTheoryConfig
    )
    from analysis.chan_theory.analyzers.structure_analyzer import ChanStructureAnalyzer


class MultiTimeframeAnalyzer:
    """多周期缠论分析器"""
    
    def __init__(self, config: ChanTheoryConfig):
        """初始化多周期分析器"""
        self.config = config
        self.structure_analyzers = {}
        
        # 为每个周期创建结构分析器
        for level in TrendLevel:
            self.structure_analyzers[level] = ChanStructureAnalyzer(config, level)
        
        print("🔍 多周期缠论分析器初始化完成")
    
    def analyze_multi_timeframe_trend(self, multi_data: Dict[TrendLevel, pd.DataFrame]) -> Dict[str, any]:
        """
        多周期联立趋势分析
        
        Args:
            multi_data: 多周期数据
            
        Returns:
            多周期分析结果
        """
        print("🔍 开始多周期联立趋势分析...")
        
        # 各周期分析结果
        level_results = {}
        
        # 分析各个周期
        for level, data in multi_data.items():
            if data.empty:
                continue
                
            print(f"\n📊 分析 {level.value} 级别...")
            
            # 确保该周期的分析器存在，如果不存在则创建
            if level not in self.structure_analyzers:
                self.structure_analyzers[level] = ChanStructureAnalyzer(self.config, level)
            
            analyzer = self.structure_analyzers[level]
            
            # 单周期分析
            level_result = analyzer.analyze_single_timeframe(data)
            level_results[level] = level_result
            
            print(f"✅ {level.value} 级别分析完成")
        
        # 多周期联立分析
        multi_analysis = self._perform_multi_timeframe_analysis(level_results)
        
        # 趋势关系分析
        trend_relationships = self._analyze_trend_relationships(level_results)
        
        # 综合评估
        comprehensive_assessment = self._comprehensive_trend_assessment(
            level_results, multi_analysis, trend_relationships
        )
        
        result = {
            'level_results': level_results,
            'multi_analysis': multi_analysis,
            'trend_relationships': trend_relationships,
            'comprehensive_assessment': comprehensive_assessment,
            'analysis_time': datetime.now()
        }
        
        print("✅ 多周期联立趋势分析完成")
        return result
    
    def _perform_multi_timeframe_analysis(self, level_results: Dict[TrendLevel, Dict]) -> Dict[str, any]:
        """执行多周期联立分析"""
        print("🔍 执行多周期联立分析...")
        
        # 趋势方向统计
        trend_directions = {}
        trend_strengths = {}
        zhongshu_levels = {}
        
        for level, result in level_results.items():
            if 'current_trend' in result:
                trend_directions[level] = result['current_trend']
                trend_strengths[level] = result.get('trend_strength', 0.5)
            
            if 'current_zhongshu' in result and result['current_zhongshu']:
                zhongshu_levels[level] = result['current_zhongshu']
        
        # 趋势一致性分析
        trend_consistency = self._calculate_trend_consistency(trend_directions)
        
        # 主导趋势识别
        dominant_trend = self._identify_dominant_trend(trend_directions, trend_strengths)
        
        # 关键支撑阻力位
        key_levels = self._identify_key_levels(level_results)
        
        return {
            'trend_directions': trend_directions,
            'trend_strengths': trend_strengths,
            'trend_consistency': trend_consistency,
            'dominant_trend': dominant_trend,
            'zhongshu_levels': zhongshu_levels,
            'key_support_levels': key_levels['support'],
            'key_resistance_levels': key_levels['resistance']
        }
    
    def _analyze_trend_relationships(self, level_results: Dict[TrendLevel, Dict]) -> Dict[str, any]:
        """
        分析次级趋势与上一级趋势的关系
        
        基于缠论理论：
        1. 次级趋势是对主要趋势的修正
        2. 次级趋势通常持续时间较短，幅度为主要趋势的1/3到2/3
        3. 次级趋势结束后，主要趋势通常会继续
        """
        print("🔍 分析趋势级别关系...")
        
        relationships = {}
        
        # 日线与30分钟的关系
        if TrendLevel.DAILY in level_results and TrendLevel.MIN30 in level_results:
            daily_result = level_results[TrendLevel.DAILY]
            min30_result = level_results[TrendLevel.MIN30]
            
            relationship = self._analyze_trend_pair_relationship(
                daily_result, min30_result, "日线", "30分钟"
            )
            relationships['daily_vs_30min'] = relationship
        
        # 30分钟与5分钟的关系
        if TrendLevel.MIN30 in level_results and TrendLevel.MIN5 in level_results:
            min30_result = level_results[TrendLevel.MIN30]
            min5_result = level_results[TrendLevel.MIN5]
            
            relationship = self._analyze_trend_pair_relationship(
                min30_result, min5_result, "30分钟", "5分钟"
            )
            relationships['30min_vs_5min'] = relationship
        
        # 日线与5分钟的关系
        if TrendLevel.DAILY in level_results and TrendLevel.MIN5 in level_results:
            daily_result = level_results[TrendLevel.DAILY]
            min5_result = level_results[TrendLevel.MIN5]
            
            relationship = self._analyze_trend_pair_relationship(
                daily_result, min5_result, "日线", "5分钟"
            )
            relationships['daily_vs_5min'] = relationship
        
        return relationships
    
    def _analyze_trend_pair_relationship(self, higher_result: Dict, lower_result: Dict, 
                                       higher_name: str, lower_name: str) -> Dict[str, any]:
        """分析两个级别之间的趋势关系"""
        
        higher_trend = higher_result.get('current_trend', TrendDirection.SIDEWAYS)
        lower_trend = lower_result.get('current_trend', TrendDirection.SIDEWAYS)
        
        # 趋势一致性
        is_consistent = higher_trend == lower_trend
        
        # 背离情况
        is_divergent = (higher_trend == TrendDirection.UP and lower_trend == TrendDirection.DOWN) or \
                      (higher_trend == TrendDirection.DOWN and lower_trend == TrendDirection.UP)
        
        # 修正关系
        is_correction = False
        correction_type = None
        
        if higher_trend != TrendDirection.SIDEWAYS and lower_trend != TrendDirection.SIDEWAYS:
            if is_divergent:
                is_correction = True
                if higher_trend == TrendDirection.UP:
                    correction_type = "上升趋势中的回调修正"
                else:
                    correction_type = "下降趋势中的反弹修正"
        
        # 强度对比
        higher_strength = higher_result.get('trend_strength', 0.5)
        lower_strength = lower_result.get('trend_strength', 0.5)
        strength_ratio = lower_strength / higher_strength if higher_strength > 0 else 1.0
        
        # 中枢关系
        zhongshu_relationship = self._analyze_zhongshu_relationship(higher_result, lower_result)
        
        return {
            'higher_level': higher_name,
            'lower_level': lower_name,
            'higher_trend': higher_trend,
            'lower_trend': lower_trend,
            'is_consistent': is_consistent,
            'is_divergent': is_divergent,
            'is_correction': is_correction,
            'correction_type': correction_type,
            'strength_ratio': strength_ratio,
            'zhongshu_relationship': zhongshu_relationship,
            'relationship_quality': self._evaluate_relationship_quality(
                is_consistent, is_correction, strength_ratio
            )
        }
    
    def _analyze_zhongshu_relationship(self, higher_result: Dict, lower_result: Dict) -> Dict[str, any]:
        """分析中枢关系"""
        higher_zhongshu = higher_result.get('current_zhongshu')
        lower_zhongshu = lower_result.get('current_zhongshu')
        
        if not higher_zhongshu or not lower_zhongshu:
            return {'status': 'incomplete', 'description': '缺少中枢数据'}
        
        # 中枢包含关系
        is_contained = (lower_zhongshu.low >= higher_zhongshu.low and 
                       lower_zhongshu.high <= higher_zhongshu.high)
        
        # 中枢重叠关系
        is_overlapping = not (lower_zhongshu.high < higher_zhongshu.low or 
                             lower_zhongshu.low > higher_zhongshu.high)
        
        # 中枢位置关系
        if lower_zhongshu.center > higher_zhongshu.high:
            position = "上方"
        elif lower_zhongshu.center < higher_zhongshu.low:
            position = "下方"
        else:
            position = "内部"
        
        return {
            'is_contained': is_contained,
            'is_overlapping': is_overlapping,
            'position': position,
            'higher_zhongshu_range': higher_zhongshu.range_ratio,
            'lower_zhongshu_range': lower_zhongshu.range_ratio
        }
    
    def _calculate_trend_consistency(self, trend_directions: Dict[TrendLevel, TrendDirection]) -> float:
        """计算多周期趋势一致性"""
        if len(trend_directions) < 2:
            return 0.5
        
        trends = list(trend_directions.values())
        
        # 计算一致的趋势对数
        consistent_pairs = 0
        total_pairs = 0
        
        for i in range(len(trends)):
            for j in range(i + 1, len(trends)):
                total_pairs += 1
                if trends[i] == trends[j]:
                    consistent_pairs += 1
        
        return consistent_pairs / total_pairs if total_pairs > 0 else 0.5
    
    def _identify_dominant_trend(self, trend_directions: Dict[TrendLevel, TrendDirection], 
                               trend_strengths: Dict[TrendLevel, float]) -> TrendDirection:
        """识别主导趋势"""
        if not trend_directions:
            return TrendDirection.SIDEWAYS
        
        # 按级别权重计算（新的多周期分析）
        level_weights = {
            TrendLevel.DAILY: 3.0,      # 日线权重最高
            TrendLevel.MIN30: 2.0,      # 30分钟次之
            TrendLevel.MIN5: 1.0        # 5分钟权重最低
        }
        
        # 使用字符串值作为键，避免枚举实例比较问题
        trend_scores = {
            'up': 0.0,
            'down': 0.0,
            'sideways': 0.0
        }
        
        total_weight = 0.0
        
        for level, trend in trend_directions.items():
            weight = level_weights.get(level, 1.0)
            strength = trend_strengths.get(level, 0.5)
            
            # 获取趋势的字符串值
            if hasattr(trend, 'value'):
                trend_str = trend.value
            elif isinstance(trend, str):
                trend_str = trend
            else:
                print(f"⚠️ 未知的趋势类型: {type(trend)}, 值: {trend}, 使用默认横盘")
                trend_str = 'sideways'
            
            # 确保是有效的趋势值
            if trend_str not in trend_scores:
                print(f"⚠️ 无效的趋势值: {trend_str}, 使用默认横盘")
                trend_str = 'sideways'
            
            # 权重 × 强度
            score = weight * strength
            trend_scores[trend_str] += score
            total_weight += weight
        
        # 归一化
        if total_weight > 0:
            for trend in trend_scores:
                trend_scores[trend] /= total_weight
        
        # 找到得分最高的趋势字符串
        dominant_trend_str = max(trend_scores, key=trend_scores.get)
        
        # 转换回TrendDirection枚举
        trend_mapping = {
            'up': TrendDirection.UP,
            'down': TrendDirection.DOWN,
            'sideways': TrendDirection.SIDEWAYS
        }
        
        return trend_mapping.get(dominant_trend_str, TrendDirection.SIDEWAYS)
    
    def _identify_key_levels(self, level_results: Dict[TrendLevel, Dict]) -> Dict[str, List[float]]:
        """识别关键支撑阻力位"""
        support_levels = []
        resistance_levels = []
        
        for level, result in level_results.items():
            # 从中枢获取关键位
            if 'zhongshu_list' in result:
                for zhongshu in result['zhongshu_list']:
                    support_levels.append(zhongshu.low)
                    resistance_levels.append(zhongshu.high)
            
            # 从分型获取关键位
            if 'fenxing_tops' in result:
                for fenxing in result['fenxing_tops']:
                    resistance_levels.append(fenxing.price)
            
            if 'fenxing_bottoms' in result:
                for fenxing in result['fenxing_bottoms']:
                    support_levels.append(fenxing.price)
        
        # 去重并排序
        support_levels = sorted(list(set(support_levels)))
        resistance_levels = sorted(list(set(resistance_levels)), reverse=True)
        
        return {
            'support': support_levels[:5],      # 取前5个支撑位
            'resistance': resistance_levels[:5] # 取前5个阻力位
        }
    
    def _comprehensive_trend_assessment(self, level_results: Dict, multi_analysis: Dict, 
                                      trend_relationships: Dict) -> Dict[str, any]:
        """综合趋势评估"""
        print("🔍 进行综合趋势评估...")
        
        # 趋势强度评估
        overall_strength = self._calculate_overall_trend_strength(level_results, multi_analysis)
        
        # 趋势可靠性评估
        reliability = self._assess_trend_reliability(trend_relationships)
        
        # 操作建议生成
        operation_suggestion = self._generate_operation_suggestion(
            multi_analysis, trend_relationships, overall_strength, reliability
        )
        
        # 风险等级评估
        risk_level = self._assess_risk_level(overall_strength, reliability, trend_relationships)
        
        return {
            'overall_trend_strength': overall_strength,
            'trend_reliability': reliability,
            'operation_suggestion': operation_suggestion,
            'risk_level': risk_level,
            'confidence_score': (overall_strength + reliability) / 2
        }
    
    def _calculate_overall_trend_strength(self, level_results: Dict, multi_analysis: Dict) -> float:
        """计算整体趋势强度"""
        strengths = []
        
        for level, result in level_results.items():
            if 'trend_strength' in result:
                strengths.append(result['trend_strength'])
        
        if not strengths:
            return 0.5
        
        # 加权平均
        level_weights = [3.0, 2.0, 1.0]  # 日线、30分钟、5分钟权重
        weighted_sum = sum(s * w for s, w in zip(strengths, level_weights[:len(strengths)]))
        total_weight = sum(level_weights[:len(strengths)])
        
        base_strength = weighted_sum / total_weight
        
        # 考虑趋势一致性
        consistency = multi_analysis.get('trend_consistency', 0.5)
        
        return (base_strength * 0.7 + consistency * 0.3)
    
    def _assess_trend_reliability(self, trend_relationships: Dict) -> float:
        """评估趋势可靠性"""
        reliability_scores = []
        
        for relationship in trend_relationships.values():
            quality = relationship.get('relationship_quality', 0.5)
            reliability_scores.append(quality)
        
        return sum(reliability_scores) / len(reliability_scores) if reliability_scores else 0.5
    
    def _evaluate_relationship_quality(self, is_consistent: bool, is_correction: bool, 
                                     strength_ratio: float) -> float:
        """评估趋势关系质量 - 优化版本"""
        score = 0.1  # 基础分数降低，避免过高评分
        
        # 一致性加分
        if is_consistent:
            score += 0.4
        
        # 合理的修正关系加分（更宽松的条件）
        if is_correction and 0.2 <= strength_ratio <= 0.8:
            score += 0.3
        
        # 强度比例合理性（更宽松的范围）
        if 0.3 <= strength_ratio <= 2.0:
            score += 0.2
        
        # 确保有数据就有基础分
        if strength_ratio > 0:
            score += 0.1
        
        return min(score, 1.0)
    
    def _generate_operation_suggestion(self, multi_analysis: Dict, trend_relationships: Dict,
                                     strength: float, reliability: float) -> str:
        """生成操作建议"""
        dominant_trend = multi_analysis.get('dominant_trend', TrendDirection.SIDEWAYS)
        consistency = multi_analysis.get('trend_consistency', 0.5)
        
        if strength > 0.7 and reliability > 0.7:
            if dominant_trend == TrendDirection.UP:
                return "强烈建议买入：多周期上升趋势确立，趋势强度和可靠性都很高"
            elif dominant_trend == TrendDirection.DOWN:
                return "强烈建议卖出：多周期下降趋势确立，趋势强度和可靠性都很高"
            else:
                return "建议观望：横盘整理中，等待方向明确"
        
        elif strength > 0.6 and reliability > 0.6:
            if dominant_trend == TrendDirection.UP:
                return "建议买入：上升趋势较为明确，可适量参与"
            elif dominant_trend == TrendDirection.DOWN:
                return "建议卖出：下降趋势较为明确，建议减仓"
            else:
                return "谨慎观望：趋势不够明确，建议等待"
        
        else:
            return "建议观望：趋势信号不够强烈，建议等待更明确的信号"
    
    def _assess_risk_level(self, strength: float, reliability: float, 
                          trend_relationships: Dict) -> str:
        """评估风险等级"""
        risk_score = 1.0 - (strength + reliability) / 2
        
        # 检查背离情况
        divergence_count = sum(1 for rel in trend_relationships.values() 
                             if rel.get('is_divergent', False))
        
        if divergence_count > 0:
            risk_score += 0.2
        
        if risk_score < 0.3:
            return "低风险"
        elif risk_score < 0.6:
            return "中等风险"
        else:
            return "高风险"