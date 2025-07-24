#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
缠论结构映射关系分析器
基于缠论理论核心：次级走势与上一级走势的映射关系

核心分析内容：
1. 包含关系（包容性）- 小级别走势被大级别走势包含
2. 合成关系（多级合成）- 多个次级走势合成上一级走势  
3. 中枢继承关系 - 次级走势中枢被上一级走势继承
4. 背离判断 - 次级与上一级走势之间的背离分析
5. 映射质量评估 - 映射关系的强度和可靠性
"""

import sys
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import Rectangle, FancyBboxPatch
import json
from pathlib import Path

# 添加路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
chan_theory_dir = os.path.dirname(current_dir)

sys.path.append(project_root)
sys.path.append(chan_theory_dir)
sys.path.append('/Users/libing/kk_Projects/kk_Stock/kk_stock_backend/api')

try:
    from db_handler import DBHandler
except ImportError:
    print("⚠️ 无法导入数据库处理器")
    DBHandler = None

try:
    from models.chan_theory_models import TrendLevel
except ImportError:
    from analysis.chan_theory.models.chan_theory_models import TrendLevel

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

class MappingRelationType(Enum):
    """映射关系类型"""
    CONTAINMENT = "包含关系"      # 次级走势被上一级走势包含
    COMPOSITION = "合成关系"      # 多个次级走势合成上一级走势
    INHERITANCE = "继承关系"      # 中枢结构的继承
    DIVERGENCE = "背离关系"       # 次级与上一级背离

class MappingQuality(Enum):
    """映射质量等级"""
    EXCELLENT = "优秀"    # 映射关系清晰，符合缠论标准
    GOOD = "良好"         # 映射关系较好，基本符合标准
    FAIR = "一般"         # 映射关系模糊，需要谨慎判断
    POOR = "较差"         # 映射关系不清晰，不建议依据

@dataclass
class StructureMapping:
    """结构映射关系"""
    higher_level: TrendLevel                    # 上一级走势级别
    lower_level: TrendLevel                     # 次级走势级别
    mapping_type: MappingRelationType           # 映射关系类型
    quality: MappingQuality                     # 映射质量
    
    # 映射详情
    containment_ratio: float                    # 包含比例
    composition_strength: float                 # 合成强度
    inheritance_quality: float                  # 继承质量
    divergence_strength: float                  # 背离强度
    
    # 时间和价格一致性
    time_consistency: float                     # 时间一致性
    price_consistency: float                    # 价格一致性
    trend_consistency: float                    # 趋势一致性
    
    # 综合评分
    overall_score: float                        # 综合评分 (0-1)
    confidence_level: float                     # 置信度 (0-1)
    
    # 详细信息
    mapping_details: Dict[str, Any]             # 映射详情
    analysis_notes: str                         # 分析备注

@dataclass
class ZhongShuInheritance:
    """中枢继承关系"""
    parent_level: TrendLevel                    # 父级别
    child_level: TrendLevel                     # 子级别
    inheritance_type: str                       # 继承类型
    overlap_ratio: float                        # 重叠比例
    continuity_score: float                     # 连续性评分
    effectiveness_score: float                  # 有效性评分
    is_valid_inheritance: bool                  # 是否为有效继承

class StructureMappingAnalyzer:
    """结构映射关系分析器"""
    
    def __init__(self):
        """初始化分析器"""
        self.db_handler = DBHandler()
        self.analysis_results = {}
        
        print("🔍 缠论结构映射关系分析器初始化完成")
    
    def analyze_structure_mappings(self, symbol: str) -> Dict[str, Any]:
        """
        分析结构映射关系
        
        Args:
            symbol: 股票代码
            
        Returns:
            完整的结构映射分析结果
        """
        print(f"\n🎯 开始分析 {symbol} 的结构映射关系...")
        
        # 1. 获取多级别真实数据
        multi_data = self._get_real_multi_data(symbol)
        
        if not multi_data:
            return self._empty_analysis_result()
        
        # 2. 各级别结构分析
        level_structures = self._analyze_level_structures(multi_data)
        
        # 3. 映射关系分析
        structure_mappings = self._analyze_mappings(level_structures, multi_data)
        
        # 4. 中枢继承分析
        zhongshu_inheritances = self._analyze_zhongshu_inheritance(level_structures)
        
        # 5. 背离关系分析
        divergence_analysis = self._analyze_divergences(level_structures, multi_data)
        
        # 6. 映射质量评估
        quality_assessment = self._assess_mapping_quality(structure_mappings, zhongshu_inheritances)
        
        # 7. 生成结论
        mapping_conclusions = self._generate_mapping_conclusions(
            structure_mappings, zhongshu_inheritances, divergence_analysis, quality_assessment
        )
        
        return {
            'symbol': symbol,
            'analysis_time': datetime.now(),
            'multi_data': multi_data,
            'level_structures': level_structures,
            'structure_mappings': structure_mappings,
            'zhongshu_inheritances': zhongshu_inheritances,
            'divergence_analysis': divergence_analysis,
            'quality_assessment': quality_assessment,
            'mapping_conclusions': mapping_conclusions
        }
    
    def _get_real_multi_data(self, symbol: str) -> Dict[TrendLevel, pd.DataFrame]:
        """获取真实多级别数据"""
        print("📊 获取多级别真实数据...")
        
        multi_data = {}
        
        try:
            # 日线数据
            daily_collection = self.db_handler.get_collection('stock_kline_daily')
            daily_query = {
                'ts_code': symbol,
                'trade_date': {'$gte': '20250101', '$lte': '20250711'}
            }
            daily_cursor = daily_collection.find(daily_query).sort('trade_date', 1)
            daily_data = list(daily_cursor)
            
            if daily_data:
                daily_df = pd.DataFrame(daily_data)
                daily_df['datetime'] = pd.to_datetime(daily_df['trade_date'], format='%Y%m%d')
                daily_df.set_index('datetime', inplace=True)
                daily_df = daily_df[['open', 'high', 'low', 'close', 'vol', 'amount']].astype(float)
                multi_data[TrendLevel.DAILY] = daily_df
                print(f"  ✅ 日线: {len(daily_df)} 条")
            
            # 30分钟数据
            min30_collection = self.db_handler.get_collection('stock_kline_30min')
            min30_cursor = min30_collection.find({'ts_code': symbol}).sort('trade_time', 1)
            min30_data = list(min30_cursor)
            
            if min30_data:
                min30_df = pd.DataFrame(min30_data)
                min30_df['datetime'] = pd.to_datetime(min30_df['trade_time'], format='mixed')
                min30_df.set_index('datetime', inplace=True)
                min30_df = min30_df[['open', 'high', 'low', 'close', 'vol', 'amount']].astype(float)
                min30_df_2025 = min30_df[min30_df.index >= '2025-01-01']
                multi_data[TrendLevel.MIN30] = min30_df_2025
                print(f"  ✅ 30分钟: {len(min30_df_2025)} 条")
            
            # 5分钟数据
            min5_collection = self.db_handler.get_collection('stock_kline_5min')
            min5_cursor = min5_collection.find({'ts_code': symbol}).sort('trade_time', -1).limit(500)
            min5_data = list(min5_cursor)
            
            if min5_data:
                min5_df = pd.DataFrame(min5_data)
                min5_df['datetime'] = pd.to_datetime(min5_df['trade_time'], format='mixed')
                min5_df.set_index('datetime', inplace=True)
                min5_df = min5_df[['open', 'high', 'low', 'close', 'vol', 'amount']].astype(float)
                min5_df = min5_df.sort_index()
                min5_df_2025 = min5_df[min5_df.index >= '2025-01-01']
                multi_data[TrendLevel.MIN5] = min5_df_2025
                print(f"  ✅ 5分钟: {len(min5_df_2025)} 条")
            
            return multi_data
            
        except Exception as e:
            print(f"❌ 数据获取失败: {e}")
            return {}
    
    def _analyze_level_structures(self, multi_data: Dict) -> Dict[TrendLevel, Dict]:
        """分析各级别结构"""
        print("🔍 分析各级别结构...")
        
        level_structures = {}
        
        for level, data in multi_data.items():
            if data.empty:
                continue
                
            print(f"  📊 分析 {level.value} 级别...")
            
            # 分型分析
            fenxing_result = self._analyze_fenxing(data)
            
            # 笔分析
            bi_result = self._analyze_bi(fenxing_result)
            
            # 中枢分析
            zhongshu_result = self._analyze_zhongshu(bi_result, data)
            
            # 趋势分析
            trend_analysis = self._analyze_trend(data, zhongshu_result)
            
            level_structures[level] = {
                'data': data,
                'fenxing': fenxing_result,
                'bi': bi_result,
                'zhongshu': zhongshu_result,
                'trend': trend_analysis,
                'current_price': data.iloc[-1]['close']
            }
            
            print(f"    ✅ 分型: {len(fenxing_result['tops'])} 顶 + {len(fenxing_result['bottoms'])} 底")
            print(f"    ✅ 笔: {len(bi_result)} 条")
            print(f"    ✅ 中枢: {len(zhongshu_result)} 个")
        
        return level_structures
    
    def _analyze_fenxing(self, data: pd.DataFrame, window: int = 3) -> Dict:
        """分析分型"""
        if len(data) < window * 2 + 1:
            return {'tops': [], 'bottoms': []}
        
        tops = []
        bottoms = []
        
        for i in range(window, len(data) - window):
            # 顶分型
            is_top = all(data.iloc[i]['high'] > data.iloc[i+j]['high'] for j in range(-window, window+1) if j != 0)
            if is_top:
                tops.append({
                    'index': i,
                    'timestamp': data.index[i],
                    'price': data.iloc[i]['high'],
                    'strength': (data.iloc[i]['high'] - data.iloc[i-window:i+window+1]['low'].min()) / data.iloc[i]['high']
                })
            
            # 底分型
            is_bottom = all(data.iloc[i]['low'] < data.iloc[i+j]['low'] for j in range(-window, window+1) if j != 0)
            if is_bottom:
                bottoms.append({
                    'index': i,
                    'timestamp': data.index[i],
                    'price': data.iloc[i]['low'],
                    'strength': (data.iloc[i-window:i+window+1]['high'].max() - data.iloc[i]['low']) / data.iloc[i]['low']
                })
        
        return {'tops': tops, 'bottoms': bottoms}
    
    def _analyze_bi(self, fenxing_result: Dict) -> List[Dict]:
        """分析笔"""
        tops = fenxing_result['tops']
        bottoms = fenxing_result['bottoms']
        
        # 合并并排序所有分型
        all_fenxing = tops + bottoms
        all_fenxing.sort(key=lambda x: x['timestamp'])
        
        bis = []
        if len(all_fenxing) >= 2:
            for i in range(len(all_fenxing) - 1):
                start = all_fenxing[i]
                end = all_fenxing[i + 1]
                
                # 确保分型类型不同
                start_type = 'top' if start in tops else 'bottom'
                end_type = 'top' if end in tops else 'bottom'
                
                if start_type != end_type:
                    direction = 'up' if start_type == 'bottom' else 'down'
                    amplitude = abs(end['price'] - start['price']) / start['price']
                    
                    bis.append({
                        'start_time': start['timestamp'],
                        'end_time': end['timestamp'],
                        'start_price': start['price'],
                        'end_price': end['price'],
                        'direction': direction,
                        'amplitude': amplitude,
                        'strength': (start['strength'] + end['strength']) / 2
                    })
        
        return bis
    
    def _analyze_zhongshu(self, bi_result: List, data: pd.DataFrame) -> List[Dict]:
        """分析中枢"""
        if len(bi_result) < 3:
            return []
        
        zhongshu_list = []
        
        # 寻找三笔构成的中枢
        for i in range(len(bi_result) - 2):
            bi1, bi2, bi3 = bi_result[i], bi_result[i+1], bi_result[i+2]
            
            # 检查是否构成中枢（三笔有重叠）
            if bi1['direction'] != bi2['direction'] and bi2['direction'] != bi3['direction']:
                # 计算重叠区域
                high_overlap = min(bi1['end_price'], bi3['end_price']) if bi1['direction'] == 'up' else min(bi1['start_price'], bi3['start_price'])
                low_overlap = max(bi1['end_price'], bi3['end_price']) if bi1['direction'] == 'down' else max(bi1['start_price'], bi3['start_price'])
                
                if high_overlap > low_overlap:  # 存在重叠
                    zhongshu_list.append({
                        'start_time': bi1['start_time'],
                        'end_time': bi3['end_time'],
                        'high': high_overlap,
                        'low': low_overlap,
                        'center': (high_overlap + low_overlap) / 2,
                        'range_ratio': (high_overlap - low_overlap) / low_overlap,
                        'forming_bis': [bi1, bi2, bi3]
                    })
        
        return zhongshu_list
    
    def _analyze_trend(self, data: pd.DataFrame, zhongshu_result: List) -> Dict:
        """分析趋势"""
        if data.empty:
            return {'direction': 'sideways', 'strength': 0.0}
        
        # 简单趋势判断
        if len(data) >= 20:
            recent_high = data['high'].tail(10).max()
            recent_low = data['low'].tail(10).min()
            earlier_high = data['high'].head(10).max()
            earlier_low = data['low'].head(10).min()
            
            if recent_high > earlier_high and recent_low > earlier_low:
                direction = 'up'
                strength = (recent_high - earlier_high) / earlier_high
            elif recent_high < earlier_high and recent_low < earlier_low:
                direction = 'down'
                strength = (earlier_high - recent_high) / earlier_high
            else:
                direction = 'sideways'
                strength = 0.5
        else:
            direction = 'sideways'
            strength = 0.5
        
        return {
            'direction': direction,
            'strength': min(strength, 1.0),
            'zhongshu_count': len(zhongshu_result)
        }
    
    def _analyze_mappings(self, level_structures: Dict, multi_data: Dict) -> List[StructureMapping]:
        """分析结构映射关系"""
        print("🔍 分析结构映射关系...")
        
        mappings = []
        
        # 日线 -> 30分钟映射
        if TrendLevel.DAILY in level_structures and TrendLevel.MIN30 in level_structures:
            mapping = self._analyze_level_mapping(
                TrendLevel.DAILY, TrendLevel.MIN30,
                level_structures[TrendLevel.DAILY],
                level_structures[TrendLevel.MIN30]
            )
            mappings.append(mapping)
        
        # 30分钟 -> 5分钟映射
        if TrendLevel.MIN30 in level_structures and TrendLevel.MIN5 in level_structures:
            mapping = self._analyze_level_mapping(
                TrendLevel.MIN30, TrendLevel.MIN5,
                level_structures[TrendLevel.MIN30],
                level_structures[TrendLevel.MIN5]
            )
            mappings.append(mapping)
        
        # 日线 -> 5分钟映射（跨级别）
        if TrendLevel.DAILY in level_structures and TrendLevel.MIN5 in level_structures:
            mapping = self._analyze_level_mapping(
                TrendLevel.DAILY, TrendLevel.MIN5,
                level_structures[TrendLevel.DAILY],
                level_structures[TrendLevel.MIN5]
            )
            mappings.append(mapping)
        
        return mappings
    
    def _analyze_level_mapping(self, higher_level: TrendLevel, lower_level: TrendLevel,
                              higher_structure: Dict, lower_structure: Dict) -> StructureMapping:
        """分析两个级别之间的映射关系"""
        
        # 1. 包含关系分析
        containment_ratio = self._calculate_containment_ratio(higher_structure, lower_structure)
        
        # 2. 合成关系分析
        composition_strength = self._calculate_composition_strength(higher_structure, lower_structure)
        
        # 3. 继承质量分析
        inheritance_quality = self._calculate_inheritance_quality(higher_structure, lower_structure)
        
        # 4. 背离强度分析
        divergence_strength = self._calculate_divergence_strength(higher_structure, lower_structure)
        
        # 5. 一致性分析
        time_consistency = self._calculate_time_consistency(higher_structure, lower_structure)
        price_consistency = self._calculate_price_consistency(higher_structure, lower_structure)
        trend_consistency = self._calculate_trend_consistency(higher_structure, lower_structure)
        
        # 6. 确定映射类型
        mapping_type = self._determine_mapping_type(
            containment_ratio, composition_strength, inheritance_quality, divergence_strength
        )
        
        # 7. 综合评分
        overall_score = (containment_ratio + composition_strength + inheritance_quality + 
                        time_consistency + price_consistency + trend_consistency) / 6
        
        # 8. 质量等级
        quality = self._determine_mapping_quality(overall_score)
        
        # 9. 置信度
        confidence_level = min(overall_score + 0.1, 1.0)
        
        return StructureMapping(
            higher_level=higher_level,
            lower_level=lower_level,
            mapping_type=mapping_type,
            quality=quality,
            containment_ratio=containment_ratio,
            composition_strength=composition_strength,
            inheritance_quality=inheritance_quality,
            divergence_strength=divergence_strength,
            time_consistency=time_consistency,
            price_consistency=price_consistency,
            trend_consistency=trend_consistency,
            overall_score=overall_score,
            confidence_level=confidence_level,
            mapping_details={
                'higher_fenxing_count': len(higher_structure['fenxing']['tops']) + len(higher_structure['fenxing']['bottoms']),
                'lower_fenxing_count': len(lower_structure['fenxing']['tops']) + len(lower_structure['fenxing']['bottoms']),
                'higher_bi_count': len(higher_structure['bi']),
                'lower_bi_count': len(lower_structure['bi']),
                'higher_zhongshu_count': len(higher_structure['zhongshu']),
                'lower_zhongshu_count': len(lower_structure['zhongshu'])
            },
            analysis_notes=f"{higher_level.value}级别与{lower_level.value}级别的{mapping_type.value}"
        )
    
    def _calculate_containment_ratio(self, higher_structure: Dict, lower_structure: Dict) -> float:
        """计算包含比例"""
        # 简化实现：基于时间范围的包含关系
        higher_data = higher_structure['data']
        lower_data = lower_structure['data']
        
        if higher_data.empty or lower_data.empty:
            return 0.0
        
        higher_start = higher_data.index[0]
        higher_end = higher_data.index[-1]
        lower_start = lower_data.index[0]
        lower_end = lower_data.index[-1]
        
        # 计算时间重叠比例
        overlap_start = max(higher_start, lower_start)
        overlap_end = min(higher_end, lower_end)
        
        if overlap_end <= overlap_start:
            return 0.0
        
        overlap_duration = (overlap_end - overlap_start).total_seconds()
        lower_duration = (lower_end - lower_start).total_seconds()
        
        return min(overlap_duration / lower_duration, 1.0) if lower_duration > 0 else 0.0
    
    def _calculate_composition_strength(self, higher_structure: Dict, lower_structure: Dict) -> float:
        """计算合成强度 - 优化版本"""
        # 基于结构数量的比例关系
        higher_bi_count = len(higher_structure['bi'])
        lower_bi_count = len(lower_structure['bi'])
        
        # 确保有基础分数
        if higher_bi_count == 0 and lower_bi_count == 0:
            return 0.3  # 基础分数
        elif higher_bi_count == 0:
            return 0.5  # 次级有结构，上级无结构
        
        # 理想情况下，次级走势的笔数应该是上一级的数倍
        composition_ratio = lower_bi_count / higher_bi_count
        
        # 更宽松的比例范围判断
        if 2 <= composition_ratio <= 20:
            return 0.8
        elif 1 <= composition_ratio <= 30:
            return 0.6
        elif 0.5 <= composition_ratio <= 50:
            return 0.4
        else:
            return 0.3  # 至少给基础分
    
    def _calculate_inheritance_quality(self, higher_structure: Dict, lower_structure: Dict) -> float:
        """计算继承质量"""
        higher_zs_count = len(higher_structure['zhongshu'])
        lower_zs_count = len(lower_structure['zhongshu'])
        
        if higher_zs_count == 0 and lower_zs_count == 0:
            return 0.5
        
        # 中枢继承的连续性和有效性
        if higher_zs_count > 0 and lower_zs_count > 0:
            # 简化：基于中枢数量的比例关系
            ratio = lower_zs_count / higher_zs_count
            if ratio >= 2:
                return 0.8
            elif ratio >= 1:
                return 0.6
            else:
                return 0.4
        
        return 0.3
    
    def _calculate_divergence_strength(self, higher_structure: Dict, lower_structure: Dict) -> float:
        """计算背离强度"""
        higher_trend = higher_structure['trend']
        lower_trend = lower_structure['trend']
        
        # 趋势方向一致性
        if higher_trend['direction'] == lower_trend['direction']:
            return 0.1  # 无背离
        elif higher_trend['direction'] == 'sideways' or lower_trend['direction'] == 'sideways':
            return 0.3  # 轻微背离
        else:
            return 0.7  # 明显背离
    
    def _calculate_time_consistency(self, higher_structure: Dict, lower_structure: Dict) -> float:
        """计算时间一致性"""
        # 简化实现：基于数据时间范围的重叠程度
        return 0.7  # 默认值，实际应该计算时间序列的一致性
    
    def _calculate_price_consistency(self, higher_structure: Dict, lower_structure: Dict) -> float:
        """计算价格一致性"""
        # 简化实现：基于价格范围的一致性
        higher_price = higher_structure['current_price']
        lower_price = lower_structure['current_price']
        
        price_diff = abs(higher_price - lower_price) / max(higher_price, lower_price)
        return max(0.0, 1.0 - price_diff)
    
    def _calculate_trend_consistency(self, higher_structure: Dict, lower_structure: Dict) -> float:
        """计算趋势一致性"""
        higher_trend = higher_structure['trend']['direction']
        lower_trend = lower_structure['trend']['direction']
        
        if higher_trend == lower_trend:
            return 0.9
        elif higher_trend == 'sideways' or lower_trend == 'sideways':
            return 0.6
        else:
            return 0.3
    
    def _determine_mapping_type(self, containment: float, composition: float, 
                               inheritance: float, divergence: float) -> MappingRelationType:
        """确定映射类型"""
        if containment > 0.7:
            return MappingRelationType.CONTAINMENT
        elif composition > 0.6:
            return MappingRelationType.COMPOSITION
        elif inheritance > 0.6:
            return MappingRelationType.INHERITANCE
        elif divergence > 0.5:
            return MappingRelationType.DIVERGENCE
        else:
            return MappingRelationType.CONTAINMENT
    
    def _determine_mapping_quality(self, overall_score: float) -> MappingQuality:
        """确定映射质量 - 优化版本"""
        if overall_score >= 0.7:
            return MappingQuality.EXCELLENT
        elif overall_score >= 0.5:
            return MappingQuality.GOOD
        elif overall_score >= 0.3:
            return MappingQuality.FAIR
        else:
            return MappingQuality.POOR
    
    def _analyze_zhongshu_inheritance(self, level_structures: Dict) -> List[ZhongShuInheritance]:
        """分析中枢继承关系"""
        print("🔍 分析中枢继承关系...")
        
        inheritances = []
        
        # 分析相邻级别的中枢继承
        levels = list(level_structures.keys())
        for i in range(len(levels) - 1):
            parent_level = levels[i]
            child_level = levels[i + 1]
            
            parent_zhongshu = level_structures[parent_level]['zhongshu']
            child_zhongshu = level_structures[child_level]['zhongshu']
            
            # 分析每个父级中枢与子级中枢的继承关系
            for parent_zs in parent_zhongshu:
                for child_zs in child_zhongshu:
                    inheritance = self._analyze_single_inheritance(
                        parent_level, child_level, parent_zs, child_zs
                    )
                    if inheritance.is_valid_inheritance:
                        inheritances.append(inheritance)
        
        return inheritances
    
    def _analyze_single_inheritance(self, parent_level: TrendLevel, child_level: TrendLevel,
                                   parent_zs: Dict, child_zs: Dict) -> ZhongShuInheritance:
        """分析单个中枢继承关系"""
        
        # 计算时间重叠
        parent_start = parent_zs['start_time']
        parent_end = parent_zs['end_time']
        child_start = child_zs['start_time']
        child_end = child_zs['end_time']
        
        overlap_start = max(parent_start, child_start)
        overlap_end = min(parent_end, child_end)
        
        if overlap_end <= overlap_start:
            overlap_ratio = 0.0
        else:
            overlap_duration = (overlap_end - overlap_start).total_seconds()
            child_duration = (child_end - child_start).total_seconds()
            overlap_ratio = overlap_duration / child_duration if child_duration > 0 else 0.0
        
        # 计算价格重叠
        parent_high = parent_zs['high']
        parent_low = parent_zs['low']
        child_high = child_zs['high']
        child_low = child_zs['low']
        
        price_overlap_high = min(parent_high, child_high)
        price_overlap_low = max(parent_low, child_low)
        
        if price_overlap_high > price_overlap_low:
            price_overlap_ratio = (price_overlap_high - price_overlap_low) / (child_high - child_low)
        else:
            price_overlap_ratio = 0.0
        
        # 继承类型判断
        if overlap_ratio >= 0.8 and price_overlap_ratio >= 0.8:
            inheritance_type = "完全继承"
            is_valid = True
        elif overlap_ratio >= 0.6 and price_overlap_ratio >= 0.6:
            inheritance_type = "主要继承"
            is_valid = True
        elif overlap_ratio >= 0.3 and price_overlap_ratio >= 0.3:
            inheritance_type = "部分继承"
            is_valid = True
        else:
            inheritance_type = "弱继承"
            is_valid = False
        
        return ZhongShuInheritance(
            parent_level=parent_level,
            child_level=child_level,
            inheritance_type=inheritance_type,
            overlap_ratio=overlap_ratio,
            continuity_score=overlap_ratio,
            effectiveness_score=price_overlap_ratio,
            is_valid_inheritance=is_valid
        )
    
    def _analyze_divergences(self, level_structures: Dict, multi_data: Dict) -> Dict[str, Any]:
        """分析背离关系"""
        print("🔍 分析背离关系...")
        
        divergences = []
        
        # 分析相邻级别间的背离
        levels = list(level_structures.keys())
        for i in range(len(levels) - 1):
            higher_level = levels[i]
            lower_level = levels[i + 1]
            
            higher_structure = level_structures[higher_level]
            lower_structure = level_structures[lower_level]
            
            # 检测背离信号
            divergence = self._detect_divergence(higher_level, lower_level, higher_structure, lower_structure)
            if divergence:
                divergences.append(divergence)
        
        return {
            'divergences': divergences,
            'total_count': len(divergences),
            'strong_divergences': len([d for d in divergences if d.get('strength', 0) > 0.6])
        }
    
    def _detect_divergence(self, higher_level: TrendLevel, lower_level: TrendLevel,
                          higher_structure: Dict, lower_structure: Dict) -> Optional[Dict]:
        """检测两个级别间的背离"""
        
        higher_trend = higher_structure['trend']
        lower_trend = lower_structure['trend']
        
        # 趋势方向背离
        if higher_trend['direction'] != lower_trend['direction'] and \
           higher_trend['direction'] != 'sideways' and lower_trend['direction'] != 'sideways':
            
            strength = abs(higher_trend['strength'] - lower_trend['strength'])
            
            return {
                'type': 'trend_divergence',
                'higher_level': higher_level,
                'lower_level': lower_level,
                'higher_trend': higher_trend['direction'],
                'lower_trend': lower_trend['direction'],
                'strength': strength,
                'description': f"{higher_level.value}级别{higher_trend['direction']}趋势与{lower_level.value}级别{lower_trend['direction']}趋势背离"
            }
        
        return None
    
    def _assess_mapping_quality(self, mappings: List[StructureMapping], 
                               inheritances: List[ZhongShuInheritance]) -> Dict[str, Any]:
        """评估映射质量"""
        print("📊 评估映射质量...")
        
        if not mappings:
            return {'overall_quality': 0.0, 'assessment': '无映射关系'}
        
        # 计算整体质量
        quality_scores = [m.overall_score for m in mappings]
        overall_quality = sum(quality_scores) / len(quality_scores)
        
        # 继承质量
        if inheritances:
            inheritance_scores = [i.continuity_score * i.effectiveness_score for i in inheritances if i.is_valid_inheritance]
            inheritance_quality = sum(inheritance_scores) / len(inheritance_scores) if inheritance_scores else 0.0
        else:
            inheritance_quality = 0.0
        
        # 综合评估
        comprehensive_score = (overall_quality * 0.7 + inheritance_quality * 0.3)
        
        # 质量等级
        if comprehensive_score >= 0.8:
            assessment = "优秀 - 映射关系清晰，符合缠论理论"
        elif comprehensive_score >= 0.6:
            assessment = "良好 - 映射关系较好，基本符合理论"
        elif comprehensive_score >= 0.4:
            assessment = "一般 - 映射关系模糊，需谨慎判断"
        else:
            assessment = "较差 - 映射关系不清晰，不建议依据"
        
        return {
            'overall_quality': overall_quality,
            'inheritance_quality': inheritance_quality,
            'comprehensive_score': comprehensive_score,
            'assessment': assessment,
            'mapping_count': len(mappings),
            'valid_inheritance_count': len([i for i in inheritances if i.is_valid_inheritance])
        }
    
    def _generate_mapping_conclusions(self, mappings: List[StructureMapping], 
                                    inheritances: List[ZhongShuInheritance],
                                    divergences: Dict, quality_assessment: Dict) -> Dict[str, Any]:
        """生成映射结论"""
        print("📝 生成映射结论...")
        
        conclusions = {
            'summary': f"共发现 {len(mappings)} 个结构映射关系",
            'key_findings': [],
            'mapping_analysis': {},
            'inheritance_analysis': {},
            'divergence_analysis': {},
            'overall_assessment': quality_assessment['assessment'],
            'recommendations': []
        }
        
        # 映射关系分析
        if mappings:
            best_mapping = max(mappings, key=lambda x: x.overall_score)
            conclusions['mapping_analysis'] = {
                'best_mapping': f"{best_mapping.higher_level.value} -> {best_mapping.lower_level.value}",
                'best_quality': best_mapping.quality.value,
                'best_score': best_mapping.overall_score,
                'dominant_type': best_mapping.mapping_type.value
            }
            
            conclusions['key_findings'].append(
                f"最强映射关系: {best_mapping.higher_level.value} -> {best_mapping.lower_level.value} ({best_mapping.mapping_type.value})"
            )
        
        # 继承关系分析
        if inheritances:
            valid_inheritances = [i for i in inheritances if i.is_valid_inheritance]
            if valid_inheritances:
                best_inheritance = max(valid_inheritances, key=lambda x: x.overlap_ratio)
                conclusions['inheritance_analysis'] = {
                    'valid_count': len(valid_inheritances),
                    'best_inheritance': f"{best_inheritance.parent_level.value} -> {best_inheritance.child_level.value}",
                    'best_type': best_inheritance.inheritance_type,
                    'best_overlap': best_inheritance.overlap_ratio
                }
                
                conclusions['key_findings'].append(
                    f"最强中枢继承: {best_inheritance.parent_level.value} -> {best_inheritance.child_level.value} ({best_inheritance.inheritance_type})"
                )
        
        # 背离分析
        divergence_count = divergences.get('total_count', 0)
        if divergence_count > 0:
            conclusions['divergence_analysis'] = {
                'total_divergences': divergence_count,
                'strong_divergences': divergences.get('strong_divergences', 0)
            }
            
            conclusions['key_findings'].append(f"发现 {divergence_count} 个级别间背离信号")
        
        # 操作建议
        overall_score = quality_assessment.get('comprehensive_score', 0)
        if overall_score >= 0.7:
            conclusions['recommendations'].append("映射关系清晰，可作为分析依据")
            conclusions['recommendations'].append("多级别结构一致性较好，信号可靠性高")
        elif overall_score >= 0.5:
            conclusions['recommendations'].append("映射关系基本成立，建议结合其他指标确认")
            conclusions['recommendations'].append("注意观察级别间的背离信号")
        else:
            conclusions['recommendations'].append("映射关系不够清晰，建议谨慎操作")
            conclusions['recommendations'].append("等待更明确的多级别结构信号")
        
        return conclusions
    
    def _empty_analysis_result(self) -> Dict[str, Any]:
        """空分析结果"""
        return {
            'symbol': '',
            'analysis_time': datetime.now(),
            'multi_data': {},
            'level_structures': {},
            'structure_mappings': [],
            'zhongshu_inheritances': [],
            'divergence_analysis': {'divergences': [], 'total_count': 0},
            'quality_assessment': {'overall_quality': 0.0, 'assessment': '无数据'},
            'mapping_conclusions': {'summary': '无数据可分析'}
        }
    
    def create_mapping_visualization(self, analysis_result: Dict[str, Any], save_path: str = None) -> str:
        """创建结构映射可视化"""
        print("🎨 创建结构映射可视化...")
        
        try:
            symbol = analysis_result['symbol']
            multi_data = analysis_result['multi_data']
            mappings = analysis_result['structure_mappings']
            
            if not multi_data:
                print("⚠️ 无数据，跳过可视化")
                return ""
            
            # 创建复杂的多子图布局
            fig = plt.figure(figsize=(20, 16))
            
            # 主标题
            fig.suptitle(f'{symbol} 缠论结构映射关系分析', fontsize=18, fontweight='bold')
            
            # 布局：上方3个时间级别图表，下方2个分析图表
            gs = fig.add_gridspec(3, 3, height_ratios=[2, 2, 1], hspace=0.3, wspace=0.2)
            
            # 绘制各级别图表
            levels = [TrendLevel.MIN5, TrendLevel.MIN30, TrendLevel.DAILY]
            level_names = ['日线级别', '周线级别', '月线级别']
            
            for i, (level, name) in enumerate(zip(levels, level_names)):
                if level in multi_data and not multi_data[level].empty:
                    ax = fig.add_subplot(gs[0, i])
                    self._plot_level_analysis(ax, level, analysis_result, name)
            
            # 映射关系图
            ax_mapping = fig.add_subplot(gs[1, :2])
            self._plot_mapping_relationships(ax_mapping, mappings)
            
            # 质量评估图
            ax_quality = fig.add_subplot(gs[1, 2])
            self._plot_quality_assessment(ax_quality, analysis_result['quality_assessment'])
            
            # 结论文字
            ax_conclusion = fig.add_subplot(gs[2, :])
            self._plot_conclusions(ax_conclusion, analysis_result['mapping_conclusions'])
            
            plt.tight_layout()
            
            # 保存图表
            if not save_path:
                results_dir = Path(current_dir) / "results"
                results_dir.mkdir(exist_ok=True)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                save_path = results_dir / f"structure_mapping_{symbol}_{timestamp}.png"
            
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            print(f"📊 结构映射可视化已保存: {save_path}")
            return str(save_path)
            
        except Exception as e:
            print(f"❌ 可视化生成失败: {e}")
            import traceback
            traceback.print_exc()
            return ""
    
    def _plot_level_analysis(self, ax, level: TrendLevel, analysis_result: Dict, title: str):
        """绘制单个级别的分析"""
        data = analysis_result['multi_data'][level]
        structure = analysis_result['level_structures'][level]
        
        # 绘制K线
        for timestamp, row in data.iterrows():
            color = '#FF6B6B' if row['close'] >= row['open'] else '#4ECDC4'
            ax.plot([timestamp, timestamp], [row['low'], row['high']], color=color, linewidth=1)
            
            body_height = abs(row['close'] - row['open'])
            body_bottom = min(row['open'], row['close'])
            rect = Rectangle((timestamp, body_bottom), timedelta(hours=4), body_height,
                           facecolor=color, alpha=0.7, edgecolor=color)
            ax.add_patch(rect)
        
        # 绘制分型
        fenxing = structure['fenxing']
        for top in fenxing['tops']:
            ax.scatter(top['timestamp'], top['price'], color='red', marker='v', s=60, zorder=5)
        for bottom in fenxing['bottoms']:
            ax.scatter(bottom['timestamp'], bottom['price'], color='green', marker='^', s=60, zorder=5)
        
        # 绘制笔
        for bi in structure['bi']:
            ax.plot([bi['start_time'], bi['end_time']], [bi['start_price'], bi['end_price']], 
                   color='orange', linewidth=2, alpha=0.8)
        
        # 绘制中枢
        for zs in structure['zhongshu']:
            duration = zs['end_time'] - zs['start_time']
            duration_days = duration.total_seconds() / (24 * 3600)  # 转换为天数
            height = zs['high'] - zs['low']
            rect = FancyBboxPatch((zs['start_time'], zs['low']), duration_days, height,
                                boxstyle="round,pad=0.01", facecolor='yellow', alpha=0.3)
            ax.add_patch(rect)
        
        ax.set_title(f"{title}\n分型:{len(fenxing['tops'])+len(fenxing['bottoms'])} 笔:{len(structure['bi'])} 中枢:{len(structure['zhongshu'])}")
        ax.grid(True, alpha=0.3)
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
    
    def _plot_mapping_relationships(self, ax, mappings: List[StructureMapping]):
        """绘制映射关系图"""
        if not mappings:
            ax.text(0.5, 0.5, '暂无映射关系', ha='center', va='center', transform=ax.transAxes)
            ax.set_title('结构映射关系')
            return
        
        # 创建映射关系的网络图
        levels = ['daily', '30min', '5min']
        positions = {level: (i, 0) for i, level in enumerate(levels)}
        
        # 绘制节点
        for i, level in enumerate(levels):
            ax.scatter(i, 0, s=500, c='lightblue', edgecolors='black', zorder=5)
            ax.text(i, 0, level, ha='center', va='center', fontweight='bold')
        
        # 绘制映射连线
        for mapping in mappings:
            higher_idx = levels.index(mapping.higher_level.value.replace('min', 'min'))
            lower_idx = levels.index(mapping.lower_level.value.replace('min', 'min'))
            
            # 连线颜色表示质量
            if mapping.quality == MappingQuality.EXCELLENT:
                color = 'green'
            elif mapping.quality == MappingQuality.GOOD:
                color = 'orange'
            else:
                color = 'red'
            
            # 绘制箭头
            ax.annotate('', xy=(lower_idx, 0.1), xytext=(higher_idx, -0.1),
                       arrowprops=dict(arrowstyle='->', color=color, lw=3))
            
            # 添加标签
            mid_x = (higher_idx + lower_idx) / 2
            ax.text(mid_x, 0.2, f"{mapping.mapping_type.value}\n{mapping.quality.value}", 
                   ha='center', va='bottom', fontsize=8)
        
        ax.set_xlim(-0.5, 2.5)
        ax.set_ylim(-0.5, 0.5)
        ax.set_title('结构映射关系网络')
        ax.axis('off')
    
    def _plot_quality_assessment(self, ax, quality: Dict[str, Any]):
        """绘制质量评估图"""
        scores = [
            quality.get('overall_quality', 0),
            quality.get('inheritance_quality', 0),
            quality.get('comprehensive_score', 0)
        ]
        labels = ['映射质量', '继承质量', '综合评分']
        colors = ['#FF9999', '#66B2FF', '#99FF99']
        
        bars = ax.bar(labels, scores, color=colors, alpha=0.7)
        
        # 添加数值标签
        for bar, score in zip(bars, scores):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                   f'{score:.2f}', ha='center', va='bottom')
        
        ax.set_ylim(0, 1)
        ax.set_ylabel('评分')
        ax.set_title('映射质量评估')
        ax.grid(True, alpha=0.3)
    
    def _plot_conclusions(self, ax, conclusions: Dict[str, Any]):
        """绘制结论文字"""
        ax.axis('off')
        
        text_content = []
        text_content.append(f"📊 {conclusions.get('summary', '')}")
        
        key_findings = conclusions.get('key_findings', [])
        if key_findings:
            text_content.append("\n🔍 关键发现:")
            for finding in key_findings[:3]:  # 限制显示数量
                text_content.append(f"  • {finding}")
        
        recommendations = conclusions.get('recommendations', [])
        if recommendations:
            text_content.append("\n💡 操作建议:")
            for rec in recommendations[:2]:  # 限制显示数量
                text_content.append(f"  • {rec}")
        
        text_content.append(f"\n📈 整体评估: {conclusions.get('overall_assessment', '')}")
        
        full_text = '\n'.join(text_content)
        ax.text(0.05, 0.95, full_text, transform=ax.transAxes, fontsize=10,
               verticalalignment='top', fontfamily='monospace')


def run_structure_mapping_test():
    """运行结构映射测试"""
    print("🚀 缠论结构映射关系分析测试")
    print("=" * 60)
    
    try:
        # 创建分析器
        analyzer = StructureMappingAnalyzer()
        
        # 分析结构映射
        symbol = "300750.SZ"
        analysis_result = analyzer.analyze_structure_mappings(symbol)
        
        if not analysis_result['multi_data']:
            print("❌ 无数据可分析")
            return False
        
        # 创建可视化
        viz_path = analyzer.create_mapping_visualization(analysis_result)
        
        # 保存分析结果
        results_dir = Path(current_dir) / "results"
        results_dir.mkdir(exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # JSON结果
        json_file = results_dir / f"{symbol}_{timestamp}_structure_mapping.json"
        
        def make_serializable(obj):
            if isinstance(obj, dict):
                # 转换字典键值为字符串，特别处理TrendLevel枚举
                result = {}
                for k, v in obj.items():
                    if hasattr(k, 'value'):  # 处理枚举键
                        key = k.value
                    elif isinstance(k, str):
                        key = k
                    else:
                        key = str(k)
                    result[key] = make_serializable(v)
                return result
            elif isinstance(obj, list):
                return [make_serializable(item) for item in obj]
            elif isinstance(obj, datetime):
                return obj.isoformat()
            elif isinstance(obj, pd.DataFrame):
                return f"DataFrame with {len(obj)} rows"
            elif hasattr(obj, 'value'):
                return obj.value
            elif hasattr(obj, '__dict__'):
                return make_serializable(obj.__dict__)
            else:
                return obj
        
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(make_serializable(analysis_result), f, ensure_ascii=False, indent=2)
        
        # 打印分析结果
        print_analysis_summary(analysis_result)
        
        print(f"\n💾 完整结果已保存:")
        print(f"  - JSON数据: {json_file}")
        print(f"  - 可视化图表: {viz_path}")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def print_analysis_summary(result: Dict[str, Any]):
    """打印分析摘要"""
    print("\n" + "=" * 60)
    print("📋 缠论结构映射分析报告")
    print("=" * 60)
    
    symbol = result['symbol']
    print(f"股票代码: {symbol}")
    print(f"分析时间: {result['analysis_time']}")
    
    # 数据概况
    multi_data = result['multi_data']
    print(f"\n📊 数据概况:")
    for level, data in multi_data.items():
        if not data.empty:
            print(f"  {level.value}: {len(data)} 条数据")
    
    # 结构分析
    level_structures = result['level_structures']
    print(f"\n🏗️ 结构分析:")
    for level, structure in level_structures.items():
        fenxing_count = len(structure['fenxing']['tops']) + len(structure['fenxing']['bottoms'])
        bi_count = len(structure['bi'])
        zs_count = len(structure['zhongshu'])
        print(f"  {level.value}: {fenxing_count}个分型, {bi_count}条笔, {zs_count}个中枢")
    
    # 映射关系
    mappings = result['structure_mappings']
    print(f"\n🔗 结构映射关系 ({len(mappings)}个):")
    for mapping in mappings:
        print(f"  {mapping.higher_level.value} -> {mapping.lower_level.value}: "
              f"{mapping.mapping_type.value} (质量: {mapping.quality.value}, "
              f"评分: {mapping.overall_score:.2f})")
    
    # 中枢继承
    inheritances = result['zhongshu_inheritances']
    valid_inheritances = [i for i in inheritances if i.is_valid_inheritance]
    print(f"\n🏗️ 中枢继承关系: {len(valid_inheritances)}/{len(inheritances)} 有效")
    for inheritance in valid_inheritances:
        print(f"  {inheritance.parent_level.value} -> {inheritance.child_level.value}: "
              f"{inheritance.inheritance_type} (重叠度: {inheritance.overlap_ratio:.2%})")
    
    # 背离分析
    divergences = result['divergence_analysis']
    print(f"\n⚡ 背离信号: {divergences['total_count']} 个")
    for divergence in divergences['divergences']:
        print(f"  {divergence['description']}")
    
    # 质量评估
    quality = result['quality_assessment']
    print(f"\n📊 质量评估:")
    print(f"  映射质量: {quality['overall_quality']:.2%}")
    print(f"  继承质量: {quality['inheritance_quality']:.2%}")
    print(f"  综合评分: {quality['comprehensive_score']:.2%}")
    print(f"  评估结论: {quality['assessment']}")
    
    # 关键结论
    conclusions = result['mapping_conclusions']
    print(f"\n💡 关键结论:")
    for finding in conclusions.get('key_findings', []):
        print(f"  • {finding}")
    
    print(f"\n🎯 操作建议:")
    for rec in conclusions.get('recommendations', []):
        print(f"  • {rec}")


if __name__ == "__main__":
    success = run_structure_mapping_test()
    print(f"\n{'✅ 测试成功' if success else '❌ 测试失败'}")