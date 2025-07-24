#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
缠论分析核心引擎
整合所有分析器，提供完整的缠论分析能力
专注于分析逻辑和数据生成，输出结构化的可视化数据
"""

import sys
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any
import pandas as pd
from dataclasses import dataclass, asdict
import json

# 添加项目路径
current_dir = os.path.dirname(os.path.abspath(__file__))
chan_theory_dir = os.path.dirname(current_dir)
project_root = os.path.dirname(os.path.dirname(os.path.dirname(chan_theory_dir)))
kk_stock_path = os.path.dirname(project_root)
kk_stock_collector_path = os.path.join(kk_stock_path, 'kk_stock_collector')

sys.path.append(project_root)
sys.path.append(kk_stock_path)
sys.path.append(kk_stock_collector_path)
sys.path.append(chan_theory_dir)

# 尝试不同的导入方式
try:
    from models.chan_theory_models import (
        TrendLevel, FenXingType, TrendDirection, ChanTheoryConfig
    )
    from analyzers.structure_analyzer import ChanStructureAnalyzer
    from analyzers.multi_timeframe_analyzer import MultiTimeframeAnalyzer
    from utils.data_fetcher import ChanDataFetcher
except ImportError:
    # 绝对导入
    from analysis.chan_theory.models.chan_theory_models import (
        TrendLevel, FenXingType, TrendDirection, ChanTheoryConfig
    )
    from analysis.chan_theory.analyzers.structure_analyzer import ChanStructureAnalyzer
    from analysis.chan_theory.analyzers.multi_timeframe_analyzer import MultiTimeframeAnalyzer
    from analysis.chan_theory.utils.data_fetcher import ChanDataFetcher


@dataclass
class TradingSignal:
    """交易信号"""
    signal_type: str          # 信号类型: 'buy' | 'sell'
    signal_level: str         # 信号级别: '1buy' | '2buy' | '3buy' | '1sell' | '2sell' | '3sell'
    timeframe: TrendLevel     # 信号时间级别
    timestamp: datetime       # 信号时间
    price: float             # 信号价格
    strength: float          # 信号强度 (0-1)
    confidence: float        # 置信度 (0-1)
    description: str         # 信号描述
    supporting_levels: List[TrendLevel]  # 支持的时间级别


@dataclass
class VisualizationData:
    """可视化数据结构"""
    # K线数据
    kline_data: Dict[TrendLevel, pd.DataFrame]
    
    # 缠论结构数据
    fenxing_data: Dict[TrendLevel, List[Dict]]
    bi_data: Dict[TrendLevel, List[Dict]]
    xianduan_data: Dict[TrendLevel, List[Dict]]
    zhongshu_data: Dict[TrendLevel, List[Dict]]
    
    # 信号数据
    trading_signals: List[Dict]
    divergence_signals: List[Dict]
    
    # 映射关系数据
    structure_mappings: List[Dict]
    zhongshu_inheritances: List[Dict]
    
    # 技术指标数据
    bollinger_bands: Dict[TrendLevel, Dict]
    
    # 分析结果摘要
    analysis_summary: Dict
    
    # 图表配置
    chart_configs: Dict


class ChanTheoryEngine:
    """缠论分析核心引擎"""
    
    def __init__(self, config: ChanTheoryConfig):
        """初始化缠论引擎"""
        self.config = config
        
        # 数据获取器
        # 初始化数据获取器
        from kk_stock_collector.db_handler import DBHandler
        db_handler = DBHandler()
        self.data_fetcher = ChanDataFetcher(db_handler)
        
        # 各级别结构分析器
        self.structure_analyzers = {}
        for level in TrendLevel:
            self.structure_analyzers[level] = ChanStructureAnalyzer(config, level)
        
        # 多周期分析器
        self.multi_analyzer = MultiTimeframeAnalyzer(config)
        
        # 分析结果缓存
        self._analysis_cache = {}
        self._last_analysis_time = None
        
        print("🚀 缠论分析核心引擎初始化完成")
    
    def analyze_complete(self, symbol: str, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """
        完整缠论分析
        
        Args:
            symbol: 股票代码
            start_date: 开始日期  
            end_date: 结束日期
            
        Returns:
            完整分析结果，包含可视化数据
        """
        print(f"🔍 开始 {symbol} 完整缠论分析...")
        
        # 1. 获取多周期数据
        multi_data = self._fetch_multi_timeframe_data(symbol, start_date, end_date)
        
        if not any(not df.empty for df in multi_data.values()):
            return self._empty_analysis_result(symbol)
        
        # 2. 执行多级别结构分析
        structure_results = self._analyze_multi_level_structures(multi_data)
        
        # 3. 执行映射关系分析
        mapping_results = self._analyze_structure_mappings(structure_results, multi_data)
        
        # 4. 执行信号检测
        signal_results = self._detect_trading_signals(structure_results, multi_data)
        
        # 5. 执行背离分析
        divergence_results = self._analyze_divergences(structure_results, multi_data)
        
        # 6. 生成可视化数据
        visualization_data = self._generate_visualization_data(
            multi_data, structure_results, mapping_results, 
            signal_results, divergence_results
        )
        
        # 7. 生成分析摘要
        analysis_summary = self._generate_analysis_summary(
            structure_results, mapping_results, signal_results, divergence_results
        )
        
        # 8. 构建完整结果
        complete_result = {
            'symbol': symbol,
            'analysis_timeframe': f"{start_date.date()} 至 {end_date.date()}",
            'analysis_timestamp': datetime.now(),
            
            # 核心分析结果
            'structure_results': structure_results,
            'mapping_results': mapping_results,
            'signal_results': signal_results,
            'divergence_results': divergence_results,
            
            # 可视化数据
            'visualization_data': visualization_data,
            
            # 分析摘要
            'analysis_summary': analysis_summary,
            
            # 操作建议
            'operation_advice': self._generate_operation_advice(signal_results, analysis_summary)
        }
        
        print("✅ 完整缠论分析完成")
        return complete_result
    
    def _fetch_multi_timeframe_data(self, symbol: str, start_date: datetime, end_date: datetime) -> Dict[TrendLevel, pd.DataFrame]:
        """获取多周期数据"""
        print("📊 获取多周期K线数据...")
        
        multi_data = {}
        
        for level in TrendLevel:
            try:
                data = self.data_fetcher.get_kline_data(symbol, level, start_date, end_date)
                multi_data[level] = data
                
                if not data.empty:
                    print(f"✅ {level.value}: {len(data)} 条数据")
                else:
                    print(f"⚠️ {level.value}: 无数据")
                    
            except Exception as e:
                print(f"❌ {level.value} 数据获取失败: {e}")
                multi_data[level] = pd.DataFrame()
        
        return multi_data
    
    def _analyze_multi_level_structures(self, multi_data: Dict[TrendLevel, pd.DataFrame]) -> Dict[str, Any]:
        """多级别结构分析"""
        print("🔍 执行多级别结构分析...")
        
        level_results = {}
        
        for level, data in multi_data.items():
            if data.empty:
                continue
                
            print(f"📊 分析 {level.value} 级别结构...")
            analyzer = self.structure_analyzers[level]
            
            try:
                result = analyzer.analyze_single_timeframe(data)
                level_results[level] = result
                
                # 统计结构数量
                fenxing_count = len(result.get('fenxing_tops', [])) + len(result.get('fenxing_bottoms', []))
                bi_count = len(result.get('bi_list', []))
                xd_count = len(result.get('xd_list', []))
                zs_count = len(result.get('zhongshu_list', []))
                
                print(f"  分型: {fenxing_count}, 笔: {bi_count}, 线段: {xd_count}, 中枢: {zs_count}")
                
            except Exception as e:
                print(f"❌ {level.value} 结构分析失败: {e}")
                level_results[level] = self._empty_level_result()
        
        return {
            'level_results': level_results,
            'multi_timeframe_analysis': self.multi_analyzer.analyze_multi_timeframe_trend(multi_data)
        }
    
    def _analyze_structure_mappings(self, structure_results: Dict, multi_data: Dict) -> Dict[str, Any]:
        """结构映射关系分析"""
        print("🔍 分析结构映射关系...")
        
        level_results = structure_results.get('level_results', {})
        
        try:
            # 使用结构映射分析器
            from analyzers.structure_mapping_analysis import StructureMappingAnalyzer
            mapping_analyzer = StructureMappingAnalyzer()
            mapping_analysis = mapping_analyzer.analyze_structure_mappings(self.config.symbol)
            
            return {
                'structure_mappings': mapping_analysis.get('mapping_relationships', {}),
                'zhongshu_inheritances': mapping_analysis.get('zhongshu_inheritance', {}),
                'resonance_analysis': mapping_analysis.get('resonance_analysis', {}),
                'mapping_quality': mapping_analysis.get('mapping_relationships', {}).get('overall_quality', 0.0)
            }
            
        except Exception as e:
            print(f"❌ 映射关系分析失败: {e}")
            return {
                'structure_mappings': {},
                'zhongshu_inheritances': {},
                'resonance_analysis': {},
                'mapping_quality': 0.0
            }
    
    def _detect_trading_signals(self, structure_results: Dict, multi_data: Dict) -> Dict[str, Any]:
        """交易信号检测"""
        print("🔍 检测交易信号...")
        
        all_signals = []
        level_results = structure_results.get('level_results', {})
        
        for level, result in level_results.items():
            if not result:
                continue
                
            # 检测买卖点
            buy_signals = self._detect_buy_signals(level, result, multi_data.get(level))
            sell_signals = self._detect_sell_signals(level, result, multi_data.get(level))
            
            all_signals.extend(buy_signals)
            all_signals.extend(sell_signals)
        
        # 多级别信号验证
        validated_signals = self._validate_multi_level_signals(all_signals)
        
        # 按时间排序
        validated_signals.sort(key=lambda x: x['timestamp'])
        
        return {
            'all_signals': all_signals,
            'validated_signals': validated_signals,
            'signal_summary': self._summarize_signals(validated_signals),
            'current_recommendation': self._get_current_recommendation(validated_signals)
        }
    
    def _detect_buy_signals(self, level: TrendLevel, structure_result: Dict, data: pd.DataFrame) -> List[Dict]:
        """检测买入信号"""
        buy_signals = []
        
        if data is None or data.empty:
            return buy_signals
        
        # 1类买点：趋势背驰后的反转
        first_buy_points = self._detect_first_buy_points(level, structure_result, data)
        buy_signals.extend(first_buy_points)
        
        # 2类买点：中枢震荡后的突破
        second_buy_points = self._detect_second_buy_points(level, structure_result, data)
        buy_signals.extend(second_buy_points)
        
        # 3类买点：中枢内的低位
        third_buy_points = self._detect_third_buy_points(level, structure_result, data)
        buy_signals.extend(third_buy_points)
        
        return buy_signals
    
    def _detect_sell_signals(self, level: TrendLevel, structure_result: Dict, data: pd.DataFrame) -> List[Dict]:
        """检测卖出信号"""
        sell_signals = []
        
        if data is None or data.empty:
            return sell_signals
        
        # 1类卖点：趋势背驰后的反转
        first_sell_points = self._detect_first_sell_points(level, structure_result, data)
        sell_signals.extend(first_sell_points)
        
        # 2类卖点：中枢震荡后的突破
        second_sell_points = self._detect_second_sell_points(level, structure_result, data)
        sell_signals.extend(second_sell_points)
        
        # 3类卖点：中枢内的高位
        third_sell_points = self._detect_third_sell_points(level, structure_result, data)
        sell_signals.extend(third_sell_points)
        
        return sell_signals
    
    def _detect_first_buy_points(self, level: TrendLevel, structure_result: Dict, data: pd.DataFrame) -> List[Dict]:
        """检测一类买点"""
        signals = []
        
        # 查找下跌趋势的背驰点
        zhongshu_list = structure_result.get('zhongshu_list', [])
        bi_list = structure_result.get('bi_list', [])
        
        for i, zs in enumerate(zhongshu_list):
            if hasattr(zs, 'end_time'):
                # 查找中枢后的下跌线段是否背驰
                post_zs_bis = [bi for bi in bi_list if hasattr(bi, 'start_time') and bi.start_time > zs.end_time]
                
                if len(post_zs_bis) >= 2:
                    # 检查是否存在背驰
                    if self._check_divergence(post_zs_bis[-2:], 'down'):
                        signal = {
                            'signal_type': 'buy',
                            'signal_level': '1buy',
                            'timeframe': level,
                            'timestamp': post_zs_bis[-1].end_time if hasattr(post_zs_bis[-1], 'end_time') else datetime.now(),
                            'price': post_zs_bis[-1].end_price if hasattr(post_zs_bis[-1], 'end_price') else 0.0,
                            'strength': 0.8,
                            'confidence': 0.7,
                            'description': f'{level.value}级别一类买点：下跌背驰',
                            'supporting_data': {
                                'zhongshu': asdict(zs) if hasattr(zs, '__dict__') else zs,
                                'divergence_bis': [asdict(bi) if hasattr(bi, '__dict__') else bi for bi in post_zs_bis[-2:]]
                            }
                        }
                        signals.append(signal)
        
        return signals
    
    def _detect_second_buy_points(self, level: TrendLevel, structure_result: Dict, data: pd.DataFrame) -> List[Dict]:
        """检测二类买点"""
        signals = []
        
        zhongshu_list = structure_result.get('zhongshu_list', [])
        
        for zs in zhongshu_list:
            if hasattr(zs, 'low') and hasattr(zs, 'end_time'):
                # 查找向下离开中枢后重新向上的点
                recent_data = data[data.index > zs.end_time] if hasattr(zs, 'end_time') else data.tail(20)
                
                if not recent_data.empty:
                    # 查找最低点后的反转
                    min_idx = recent_data['low'].idxmin()
                    min_price = recent_data.loc[min_idx, 'low']
                    
                    # 检查是否接近中枢下沿
                    if abs(min_price - zs.low) / zs.low < 0.02:  # 2%范围内
                        signal = {
                            'signal_type': 'buy',
                            'signal_level': '2buy',
                            'timeframe': level,
                            'timestamp': min_idx,
                            'price': min_price,
                            'strength': 0.6,
                            'confidence': 0.6,
                            'description': f'{level.value}级别二类买点：中枢下沿回踩',
                            'supporting_data': {
                                'zhongshu': asdict(zs) if hasattr(zs, '__dict__') else zs,
                                'retest_price': min_price
                            }
                        }
                        signals.append(signal)
        
        return signals
    
    def _detect_third_buy_points(self, level: TrendLevel, structure_result: Dict, data: pd.DataFrame) -> List[Dict]:
        """检测三类买点"""
        signals = []
        
        zhongshu_list = structure_result.get('zhongshu_list', [])
        current_time = data.index[-1] if not data.empty else datetime.now()
        
        for zs in zhongshu_list:
            if hasattr(zs, 'low') and hasattr(zs, 'high') and hasattr(zs, 'end_time'):
                # 检查当前价格是否在中枢内
                if zs.end_time > current_time - timedelta(days=30):  # 最近的中枢
                    current_price = data.iloc[-1]['close'] if not data.empty else 0
                    
                    if zs.low <= current_price <= zs.high:
                        # 中枢内的低位买点
                        zs_range = zs.high - zs.low
                        position_in_zs = (current_price - zs.low) / zs_range
                        
                        if position_in_zs < 0.3:  # 在中枢下1/3位置
                            signal = {
                                'signal_type': 'buy',
                                'signal_level': '3buy',
                                'timeframe': level,
                                'timestamp': current_time,
                                'price': current_price,
                                'strength': 0.4,
                                'confidence': 0.5,
                                'description': f'{level.value}级别三类买点：中枢内低位',
                                'supporting_data': {
                                    'zhongshu': asdict(zs) if hasattr(zs, '__dict__') else zs,
                                    'position_ratio': position_in_zs
                                }
                            }
                            signals.append(signal)
        
        return signals
    
    def _detect_first_sell_points(self, level: TrendLevel, structure_result: Dict, data: pd.DataFrame) -> List[Dict]:
        """检测一类卖点"""
        signals = []
        
        zhongshu_list = structure_result.get('zhongshu_list', [])
        bi_list = structure_result.get('bi_list', [])
        
        for i, zs in enumerate(zhongshu_list):
            if hasattr(zs, 'end_time'):
                # 查找中枢后的上涨线段是否背驰
                post_zs_bis = [bi for bi in bi_list if hasattr(bi, 'start_time') and bi.start_time > zs.end_time]
                
                if len(post_zs_bis) >= 2:
                    # 检查是否存在背驰
                    if self._check_divergence(post_zs_bis[-2:], 'up'):
                        signal = {
                            'signal_type': 'sell',
                            'signal_level': '1sell',
                            'timeframe': level,
                            'timestamp': post_zs_bis[-1].end_time if hasattr(post_zs_bis[-1], 'end_time') else datetime.now(),
                            'price': post_zs_bis[-1].end_price if hasattr(post_zs_bis[-1], 'end_price') else 0.0,
                            'strength': 0.8,
                            'confidence': 0.7,
                            'description': f'{level.value}级别一类卖点：上涨背驰',
                            'supporting_data': {
                                'zhongshu': asdict(zs) if hasattr(zs, '__dict__') else zs,
                                'divergence_bis': [asdict(bi) if hasattr(bi, '__dict__') else bi for bi in post_zs_bis[-2:]]
                            }
                        }
                        signals.append(signal)
        
        return signals
    
    def _detect_second_sell_points(self, level: TrendLevel, structure_result: Dict, data: pd.DataFrame) -> List[Dict]:
        """检测二类卖点"""
        signals = []
        
        zhongshu_list = structure_result.get('zhongshu_list', [])
        
        for zs in zhongshu_list:
            if hasattr(zs, 'high') and hasattr(zs, 'end_time'):
                # 查找向上离开中枢后重新向下的点
                recent_data = data[data.index > zs.end_time] if hasattr(zs, 'end_time') else data.tail(20)
                
                if not recent_data.empty:
                    # 查找最高点后的反转
                    max_idx = recent_data['high'].idxmax()
                    max_price = recent_data.loc[max_idx, 'high']
                    
                    # 检查是否接近中枢上沿
                    if abs(max_price - zs.high) / zs.high < 0.02:  # 2%范围内
                        signal = {
                            'signal_type': 'sell',
                            'signal_level': '2sell',
                            'timeframe': level,
                            'timestamp': max_idx,
                            'price': max_price,
                            'strength': 0.6,
                            'confidence': 0.6,
                            'description': f'{level.value}级别二类卖点：中枢上沿回踩',
                            'supporting_data': {
                                'zhongshu': asdict(zs) if hasattr(zs, '__dict__') else zs,
                                'retest_price': max_price
                            }
                        }
                        signals.append(signal)
        
        return signals
    
    def _detect_third_sell_points(self, level: TrendLevel, structure_result: Dict, data: pd.DataFrame) -> List[Dict]:
        """检测三类卖点"""
        signals = []
        
        zhongshu_list = structure_result.get('zhongshu_list', [])
        current_time = data.index[-1] if not data.empty else datetime.now()
        
        for zs in zhongshu_list:
            if hasattr(zs, 'low') and hasattr(zs, 'high') and hasattr(zs, 'end_time'):
                # 检查当前价格是否在中枢内
                if zs.end_time > current_time - timedelta(days=30):  # 最近的中枢
                    current_price = data.iloc[-1]['close'] if not data.empty else 0
                    
                    if zs.low <= current_price <= zs.high:
                        # 中枢内的高位卖点
                        zs_range = zs.high - zs.low
                        position_in_zs = (current_price - zs.low) / zs_range
                        
                        if position_in_zs > 0.7:  # 在中枢上1/3位置
                            signal = {
                                'signal_type': 'sell',
                                'signal_level': '3sell',
                                'timeframe': level,
                                'timestamp': current_time,
                                'price': current_price,
                                'strength': 0.4,
                                'confidence': 0.5,
                                'description': f'{level.value}级别三类卖点：中枢内高位',
                                'supporting_data': {
                                    'zhongshu': asdict(zs) if hasattr(zs, '__dict__') else zs,
                                    'position_ratio': position_in_zs
                                }
                            }
                            signals.append(signal)
        
        return signals
    
    def _check_divergence(self, bis: List, direction: str) -> bool:
        """检查背驰"""
        if len(bis) < 2:
            return False
        
        bi1, bi2 = bis[-2], bis[-1]
        
        # 简化的背驰检查：比较价格幅度和力度
        if direction == 'down':
            # 下跌背驰：价格新低但力度减弱
            price_new_low = getattr(bi2, 'end_price', 0) < getattr(bi1, 'end_price', 0)
            amplitude_weakened = getattr(bi2, 'amplitude', 0) < getattr(bi1, 'amplitude', 0)
            return price_new_low and amplitude_weakened
        else:
            # 上涨背驰：价格新高但力度减弱
            price_new_high = getattr(bi2, 'end_price', 0) > getattr(bi1, 'end_price', 0)
            amplitude_weakened = getattr(bi2, 'amplitude', 0) < getattr(bi1, 'amplitude', 0)
            return price_new_high and amplitude_weakened
    
    def _validate_multi_level_signals(self, all_signals: List[Dict]) -> List[Dict]:
        """多级别信号验证"""
        validated_signals = []
        
        # 按时间分组
        signal_groups = {}
        for signal in all_signals:
            time_key = signal['timestamp'].strftime('%Y-%m-%d')
            if time_key not in signal_groups:
                signal_groups[time_key] = []
            signal_groups[time_key].append(signal)
        
        # 验证每组信号
        for time_key, signals in signal_groups.items():
            if len(signals) > 1:
                # 多级别共振信号
                buy_signals = [s for s in signals if s['signal_type'] == 'buy']
                sell_signals = [s for s in signals if s['signal_type'] == 'sell']
                
                if len(buy_signals) > 1:
                    # 买入共振
                    main_signal = max(buy_signals, key=lambda x: x['strength'])
                    main_signal['confidence'] += 0.2  # 提高置信度
                    main_signal['description'] += f" (多级别共振: {len(buy_signals)}个级别)"
                    main_signal['supporting_levels'] = [s['timeframe'] for s in buy_signals]
                    validated_signals.append(main_signal)
                
                if len(sell_signals) > 1:
                    # 卖出共振
                    main_signal = max(sell_signals, key=lambda x: x['strength'])
                    main_signal['confidence'] += 0.2  # 提高置信度
                    main_signal['description'] += f" (多级别共振: {len(sell_signals)}个级别)"
                    main_signal['supporting_levels'] = [s['timeframe'] for s in sell_signals]
                    validated_signals.append(main_signal)
            else:
                # 单级别信号
                validated_signals.extend(signals)
        
        return validated_signals
    
    def _analyze_divergences(self, structure_results: Dict, multi_data: Dict) -> Dict[str, Any]:
        """背离分析"""
        print("🔍 分析背离信号...")
        
        divergence_signals = []
        level_results = structure_results.get('level_results', {})
        
        # 各级别背离检测
        for level, result in level_results.items():
            if not result:
                continue
            
            # 检测顶背离
            top_divergences = self._detect_top_divergences(level, result, multi_data.get(level))
            divergence_signals.extend(top_divergences)
            
            # 检测底背离
            bottom_divergences = self._detect_bottom_divergences(level, result, multi_data.get(level))
            divergence_signals.extend(bottom_divergences)
        
        return {
            'divergence_signals': divergence_signals,
            'divergence_summary': self._summarize_divergences(divergence_signals)
        }
    
    def _detect_top_divergences(self, level: TrendLevel, structure_result: Dict, data: pd.DataFrame) -> List[Dict]:
        """检测顶背离"""
        divergences = []
        
        if data is None or data.empty:
            return divergences
        
        fenxing_tops = structure_result.get('fenxing_tops', [])
        
        if len(fenxing_tops) >= 2:
            for i in range(1, len(fenxing_tops)):
                current_top = fenxing_tops[i]
                previous_top = fenxing_tops[i-1]
                
                # 检查价格和指标的背离
                if hasattr(current_top, 'price') and hasattr(previous_top, 'price'):
                    price_higher = current_top.price > previous_top.price
                    
                    # 简化的力度比较（实际应该用MACD等指标）
                    current_strength = getattr(current_top, 'strength', 0)
                    previous_strength = getattr(previous_top, 'strength', 0)
                    strength_weaker = current_strength < previous_strength
                    
                    if price_higher and strength_weaker:
                        divergence = {
                            'type': 'top_divergence',
                            'level': level,
                            'timestamp': getattr(current_top, 'timestamp', datetime.now()),
                            'price': current_top.price,
                            'strength': 0.7,
                            'description': f'{level.value}级别顶背离',
                            'supporting_data': {
                                'current_top': asdict(current_top) if hasattr(current_top, '__dict__') else current_top,
                                'previous_top': asdict(previous_top) if hasattr(previous_top, '__dict__') else previous_top
                            }
                        }
                        divergences.append(divergence)
        
        return divergences
    
    def _detect_bottom_divergences(self, level: TrendLevel, structure_result: Dict, data: pd.DataFrame) -> List[Dict]:
        """检测底背离"""
        divergences = []
        
        if data is None or data.empty:
            return divergences
        
        fenxing_bottoms = structure_result.get('fenxing_bottoms', [])
        
        if len(fenxing_bottoms) >= 2:
            for i in range(1, len(fenxing_bottoms)):
                current_bottom = fenxing_bottoms[i]
                previous_bottom = fenxing_bottoms[i-1]
                
                # 检查价格和指标的背离
                if hasattr(current_bottom, 'price') and hasattr(previous_bottom, 'price'):
                    price_lower = current_bottom.price < previous_bottom.price
                    
                    # 简化的力度比较
                    current_strength = getattr(current_bottom, 'strength', 0)
                    previous_strength = getattr(previous_bottom, 'strength', 0)
                    strength_weaker = current_strength < previous_strength
                    
                    if price_lower and strength_weaker:
                        divergence = {
                            'type': 'bottom_divergence',
                            'level': level,
                            'timestamp': getattr(current_bottom, 'timestamp', datetime.now()),
                            'price': current_bottom.price,
                            'strength': 0.7,
                            'description': f'{level.value}级别底背离',
                            'supporting_data': {
                                'current_bottom': asdict(current_bottom) if hasattr(current_bottom, '__dict__') else current_bottom,
                                'previous_bottom': asdict(previous_bottom) if hasattr(previous_bottom, '__dict__') else previous_bottom
                            }
                        }
                        divergences.append(divergence)
        
        return divergences
    
    def _generate_visualization_data(self, multi_data: Dict, structure_results: Dict, 
                                   mapping_results: Dict, signal_results: Dict, 
                                   divergence_results: Dict) -> VisualizationData:
        """生成可视化数据结构"""
        print("📊 生成可视化数据...")
        
        level_results = structure_results.get('level_results', {})
        
        # 转换结构数据为可视化格式
        fenxing_data = {}
        bi_data = {}
        xianduan_data = {}
        zhongshu_data = {}
        bollinger_data = {}
        
        for level, result in level_results.items():
            # 分型数据
            fenxing_data[level] = self._format_fenxing_for_viz(result.get('fenxing_tops', []), result.get('fenxing_bottoms', []))
            
            # 笔数据
            bi_data[level] = self._format_bi_for_viz(result.get('bi_list', []))
            
            # 线段数据
            xianduan_data[level] = self._format_xianduan_for_viz(result.get('xd_list', []))
            
            # 中枢数据
            zhongshu_data[level] = self._format_zhongshu_for_viz(result.get('zhongshu_list', []))
            
            # 布林带数据
            bollinger_data[level] = self._format_bollinger_for_viz(result.get('bollinger_bands'))
        
        # 信号数据
        trading_signals = self._format_signals_for_viz(signal_results.get('validated_signals', []))
        divergence_signals = self._format_divergences_for_viz(divergence_results.get('divergence_signals', []))
        
        # 映射关系数据
        structure_mappings = self._format_mappings_for_viz(mapping_results.get('structure_mappings', {}))
        zhongshu_inheritances = self._format_inheritances_for_viz(mapping_results.get('zhongshu_inheritances', {}))
        
        # 分析摘要
        analysis_summary = self._format_summary_for_viz(structure_results, signal_results, divergence_results)
        
        # 图表配置
        chart_configs = self._generate_chart_configs(multi_data)
        
        return VisualizationData(
            kline_data=multi_data,
            fenxing_data=fenxing_data,
            bi_data=bi_data,
            xianduan_data=xianduan_data,
            zhongshu_data=zhongshu_data,
            trading_signals=trading_signals,
            divergence_signals=divergence_signals,
            structure_mappings=structure_mappings,
            zhongshu_inheritances=zhongshu_inheritances,
            bollinger_bands=bollinger_data,
            analysis_summary=analysis_summary,
            chart_configs=chart_configs
        )
    
    def _format_fenxing_for_viz(self, tops: List, bottoms: List) -> List[Dict]:
        """格式化分型数据供可视化使用"""
        fenxing_viz = []
        
        for top in tops:
            fenxing_viz.append({
                'type': 'top',
                'timestamp': getattr(top, 'timestamp', datetime.now()),
                'price': getattr(top, 'price', 0),
                'strength': getattr(top, 'strength', 0),
                'confirmed': getattr(top, 'confirmed', False)
            })
        
        for bottom in bottoms:
            fenxing_viz.append({
                'type': 'bottom',
                'timestamp': getattr(bottom, 'timestamp', datetime.now()),
                'price': getattr(bottom, 'price', 0),
                'strength': getattr(bottom, 'strength', 0),
                'confirmed': getattr(bottom, 'confirmed', False)
            })
        
        # 按时间排序
        fenxing_viz.sort(key=lambda x: x['timestamp'])
        return fenxing_viz
    
    def _format_bi_for_viz(self, bi_list: List) -> List[Dict]:
        """格式化笔数据供可视化使用"""
        bi_viz = []
        
        for bi in bi_list:
            bi_viz.append({
                'start_time': getattr(bi, 'start_time', datetime.now()),
                'end_time': getattr(bi, 'end_time', datetime.now()),
                'start_price': getattr(bi, 'start_price', 0),
                'end_price': getattr(bi, 'end_price', 0),
                'direction': getattr(bi, 'direction', TrendDirection.SIDEWAYS).value if hasattr(getattr(bi, 'direction', None), 'value') else str(getattr(bi, 'direction', 'unknown')),
                'amplitude': getattr(bi, 'amplitude', 0),
                'length': getattr(bi, 'length', 0)
            })
        
        return bi_viz
    
    def _format_xianduan_for_viz(self, xd_list: List) -> List[Dict]:
        """格式化线段数据供可视化使用"""
        xd_viz = []
        
        for xd in xd_list:
            xd_viz.append({
                'start_time': getattr(xd, 'start_time', datetime.now()),
                'end_time': getattr(xd, 'end_time', datetime.now()),
                'start_price': getattr(xd, 'start_price', 0),
                'end_price': getattr(xd, 'end_price', 0),
                'direction': getattr(xd, 'direction', TrendDirection.SIDEWAYS).value if hasattr(getattr(xd, 'direction', None), 'value') else str(getattr(xd, 'direction', 'unknown')),
                'amplitude': getattr(xd, 'amplitude', 0),
                'bi_count': len(getattr(xd, 'bi_list', []))
            })
        
        return xd_viz
    
    def _format_zhongshu_for_viz(self, zs_list: List) -> List[Dict]:
        """格式化中枢数据供可视化使用"""
        zs_viz = []
        
        for zs in zs_list:
            zs_viz.append({
                'start_time': getattr(zs, 'start_time', datetime.now()),
                'end_time': getattr(zs, 'end_time', datetime.now()),
                'high': getattr(zs, 'high', 0),
                'low': getattr(zs, 'low', 0),
                'center': getattr(zs, 'center', 0),
                'range_ratio': getattr(zs, 'range_ratio', 0),
                'duration_days': getattr(zs, 'duration_days', 0),
                'extend_count': getattr(zs, 'extend_count', 0)
            })
        
        return zs_viz
    
    def _format_bollinger_for_viz(self, bollinger_bands) -> Dict:
        """格式化布林带数据供可视化使用"""
        if not bollinger_bands:
            return {}
        
        return {
            'upper': bollinger_bands.upper.to_dict() if hasattr(bollinger_bands, 'upper') else {},
            'middle': bollinger_bands.middle.to_dict() if hasattr(bollinger_bands, 'middle') else {},
            'lower': bollinger_bands.lower.to_dict() if hasattr(bollinger_bands, 'lower') else {}
        }
    
    def _format_signals_for_viz(self, signals: List[Dict]) -> List[Dict]:
        """格式化信号数据供可视化使用"""
        return [{
            'type': signal['signal_type'],
            'level': signal['signal_level'],
            'timeframe': signal['timeframe'].value,
            'timestamp': signal['timestamp'],
            'price': signal['price'],
            'strength': signal['strength'],
            'confidence': signal['confidence'],
            'description': signal['description']
        } for signal in signals]
    
    def _format_divergences_for_viz(self, divergences: List[Dict]) -> List[Dict]:
        """格式化背离数据供可视化使用"""
        return [{
            'type': div['type'],
            'level': div['level'].value,
            'timestamp': div['timestamp'],
            'price': div['price'],
            'strength': div['strength'],
            'description': div['description']
        } for div in divergences]
    
    def _format_mappings_for_viz(self, mappings: Dict) -> List[Dict]:
        """格式化映射关系数据供可视化使用"""
        # 简化实现
        return []
    
    def _format_inheritances_for_viz(self, inheritances: Dict) -> List[Dict]:
        """格式化中枢继承数据供可视化使用"""
        # 简化实现
        return []
    
    def _format_summary_for_viz(self, structure_results: Dict, signal_results: Dict, divergence_results: Dict) -> Dict:
        """格式化分析摘要供可视化使用"""
        level_results = structure_results.get('level_results', {})
        
        summary = {
            'total_levels': len(level_results),
            'structure_counts': {},
            'signal_counts': {
                'total_signals': len(signal_results.get('validated_signals', [])),
                'buy_signals': len([s for s in signal_results.get('validated_signals', []) if s['signal_type'] == 'buy']),
                'sell_signals': len([s for s in signal_results.get('validated_signals', []) if s['signal_type'] == 'sell'])
            },
            'divergence_counts': {
                'total_divergences': len(divergence_results.get('divergence_signals', [])),
                'top_divergences': len([d for d in divergence_results.get('divergence_signals', []) if d['type'] == 'top_divergence']),
                'bottom_divergences': len([d for d in divergence_results.get('divergence_signals', []) if d['type'] == 'bottom_divergence'])
            }
        }
        
        # 各级别结构统计
        for level, result in level_results.items():
            summary['structure_counts'][level.value] = {
                'fenxing': len(result.get('fenxing_tops', [])) + len(result.get('fenxing_bottoms', [])),
                'bi': len(result.get('bi_list', [])),
                'xianduan': len(result.get('xd_list', [])),
                'zhongshu': len(result.get('zhongshu_list', []))
            }
        
        return summary
    
    def _generate_chart_configs(self, multi_data: Dict) -> Dict:
        """生成图表配置"""
        configs = {
            'timeframes': [level.value for level in multi_data.keys() if not multi_data[level].empty],
            'date_range': {},
            'price_range': {},
            'colors': {
                'up_candle': '#FF6B6B',
                'down_candle': '#4ECDC4',
                'fenxing_top': '#FF4444',
                'fenxing_bottom': '#44FF44',
                'bi': '#FFD93D',
                'xianduan': '#6BCF7F',
                'zhongshu': '#A8E6CF',
                'buy_signal': '#00FF00',
                'sell_signal': '#FF0000'
            }
        }
        
        # 计算各级别的时间和价格范围
        for level, data in multi_data.items():
            if not data.empty:
                configs['date_range'][level.value] = {
                    'start': data.index[0],
                    'end': data.index[-1]
                }
                configs['price_range'][level.value] = {
                    'min': data['low'].min(),
                    'max': data['high'].max()
                }
        
        return configs
    
    def _generate_analysis_summary(self, structure_results: Dict, mapping_results: Dict,
                                 signal_results: Dict, divergence_results: Dict) -> Dict:
        """生成分析摘要"""
        level_results = structure_results.get('level_results', {})
        
        summary = {
            'analysis_quality': self._assess_analysis_quality(level_results),
            'trend_analysis': self._summarize_trends(level_results),
            'signal_analysis': signal_results.get('signal_summary', {}),
            'divergence_analysis': divergence_results.get('divergence_summary', {}),
            'mapping_analysis': {
                'mapping_quality': mapping_results.get('mapping_quality', 0.0),
                'resonance_strength': mapping_results.get('resonance_analysis', {}).get('overall_resonance', 0.0)
            }
        }
        
        return summary
    
    def _assess_analysis_quality(self, level_results: Dict) -> Dict:
        """评估分析质量"""
        if not level_results:
            return {'overall': 0.0, 'details': '无数据'}
        
        quality_scores = []
        details = {}
        
        for level, result in level_results.items():
            # 数据完整性评分
            data_completeness = 1.0 if result else 0.0
            
            # 结构丰富度评分
            structure_richness = min(1.0, (
                len(result.get('fenxing_tops', [])) + 
                len(result.get('fenxing_bottoms', [])) + 
                len(result.get('bi_list', [])) + 
                len(result.get('zhongshu_list', []))
            ) / 20.0)
            
            level_score = (data_completeness + structure_richness) / 2
            quality_scores.append(level_score)
            details[level.value] = level_score
        
        overall_quality = sum(quality_scores) / len(quality_scores)
        
        return {
            'overall': overall_quality,
            'details': details,
            'quality_level': '优秀' if overall_quality > 0.8 else '良好' if overall_quality > 0.6 else '一般' if overall_quality > 0.4 else '较差'
        }
    
    def _summarize_trends(self, level_results: Dict) -> Dict:
        """总结趋势分析"""
        trends = {}
        
        for level, result in level_results.items():
            trend = result.get('current_trend', TrendDirection.SIDEWAYS)
            trend_strength = result.get('trend_strength', 0.5)
            
            trends[level.value] = {
                'direction': trend.value if hasattr(trend, 'value') else str(trend),
                'strength': trend_strength,
                'zhongshu_count': len(result.get('zhongshu_list', []))
            }
        
        # 多级别趋势一致性
        trend_directions = [trends[level]['direction'] for level in trends]
        consistency = len(set(trend_directions)) == 1 if trend_directions else False
        
        return {
            'level_trends': trends,
            'multi_level_consistency': consistency,
            'dominant_trend': max(trends.values(), key=lambda x: x['strength'])['direction'] if trends else 'unknown'
        }
    
    def _summarize_signals(self, signals: List[Dict]) -> Dict:
        """总结信号分析"""
        if not signals:
            return {'total': 0, 'buy': 0, 'sell': 0, 'quality': '无信号'}
        
        buy_count = len([s for s in signals if s['signal_type'] == 'buy'])
        sell_count = len([s for s in signals if s['signal_type'] == 'sell'])
        avg_confidence = sum(s['confidence'] for s in signals) / len(signals)
        
        quality = '信号丰富' if len(signals) > 5 else '信号充足' if len(signals) > 2 else '信号稀少'
        
        return {
            'total': len(signals),
            'buy': buy_count,
            'sell': sell_count,
            'average_confidence': avg_confidence,
            'quality': quality
        }
    
    def _summarize_divergences(self, divergences: List[Dict]) -> Dict:
        """总结背离分析"""
        if not divergences:
            return {'total': 0, 'top': 0, 'bottom': 0}
        
        top_count = len([d for d in divergences if d['type'] == 'top_divergence'])
        bottom_count = len([d for d in divergences if d['type'] == 'bottom_divergence'])
        
        return {
            'total': len(divergences),
            'top': top_count,
            'bottom': bottom_count
        }
    
    def _get_current_recommendation(self, signals: List[Dict]) -> Dict:
        """获取当前操作建议"""
        if not signals:
            return {'action': 'hold', 'reason': '暂无明确信号', 'confidence': 0.5}
        
        # 获取最近的信号
        recent_signals = sorted(signals, key=lambda x: x['timestamp'], reverse=True)[:3]
        
        if not recent_signals:
            return {'action': 'hold', 'reason': '暂无明确信号', 'confidence': 0.5}
        
        latest_signal = recent_signals[0]
        
        # 检查信号一致性
        recent_types = [s['signal_type'] for s in recent_signals]
        consistency = len(set(recent_types))
        
        confidence = latest_signal['confidence']
        if consistency == 1:  # 信号一致
            confidence += 0.2
        
        action = latest_signal['signal_type']
        reason = f"{latest_signal['description']} (置信度: {confidence:.2f})"
        
        return {
            'action': action,
            'reason': reason,
            'confidence': min(confidence, 1.0),
            'signal_level': latest_signal['signal_level'],
            'timeframe': latest_signal['timeframe']
        }
    
    def _generate_operation_advice(self, signal_results: Dict, analysis_summary: Dict) -> Dict:
        """生成操作建议"""
        recommendation = signal_results.get('current_recommendation', {})
        analysis_quality = analysis_summary.get('analysis_quality', {})
        
        # 基于分析质量调整建议可信度
        quality_score = analysis_quality.get('overall', 0.5)
        adjusted_confidence = recommendation.get('confidence', 0.5) * quality_score
        
        # 风险评估
        risk_level = 'high' if adjusted_confidence < 0.4 else 'medium' if adjusted_confidence < 0.7 else 'low'
        
        return {
            'primary_action': recommendation.get('action', 'hold'),
            'confidence_level': adjusted_confidence,
            'risk_level': risk_level,
            'detailed_advice': recommendation.get('reason', ''),
            'supporting_timeframes': recommendation.get('timeframe', ''),
            'caution_notes': self._generate_caution_notes(risk_level, analysis_quality)
        }
    
    def _generate_caution_notes(self, risk_level: str, analysis_quality: Dict) -> List[str]:
        """生成注意事项"""
        notes = []
        
        if risk_level == 'high':
            notes.append("⚠️ 信号强度较弱，建议谨慎操作")
        
        if analysis_quality.get('overall', 0) < 0.6:
            notes.append("⚠️ 分析数据质量一般，建议结合其他分析方法")
        
        notes.append("📈 缠论分析仅供参考，请结合基本面分析")
        notes.append("💰 请控制仓位，设置止损")
        
        return notes
    
    def _empty_analysis_result(self, symbol: str) -> Dict[str, Any]:
        """空分析结果"""
        return {
            'symbol': symbol,
            'analysis_timestamp': datetime.now(),
            'structure_results': {'level_results': {}},
            'mapping_results': {},
            'signal_results': {'validated_signals': [], 'signal_summary': {'total': 0}},
            'divergence_results': {'divergence_signals': []},
            'visualization_data': VisualizationData(
                kline_data={},
                fenxing_data={},
                bi_data={},
                xianduan_data={},
                zhongshu_data={},
                trading_signals=[],
                divergence_signals=[],
                structure_mappings=[],
                zhongshu_inheritances=[],
                bollinger_bands={},
                analysis_summary={'total_levels': 0},
                chart_configs={}
            ),
            'analysis_summary': {'analysis_quality': {'overall': 0.0}},
            'operation_advice': {'primary_action': 'hold', 'confidence_level': 0.0}
        }
    
    def _empty_level_result(self) -> Dict:
        """空级别结果"""
        return {
            'fenxing_tops': [],
            'fenxing_bottoms': [],
            'bi_list': [],
            'xd_list': [],
            'zhongshu_list': [],
            'current_trend': TrendDirection.SIDEWAYS,
            'trend_strength': 0.0
        }
    
    def save_analysis_result(self, result: Dict[str, Any], save_path: str) -> bool:
        """保存分析结果"""
        try:
            # 转换datetime对象为字符串以支持JSON序列化
            serializable_result = self._make_json_serializable(result)
            
            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(serializable_result, f, ensure_ascii=False, indent=2)
            
            print(f"💾 分析结果已保存: {save_path}")
            return True
            
        except Exception as e:
            print(f"❌ 保存分析结果失败: {e}")
            return False
    
    def _make_json_serializable(self, obj):
        """使对象可JSON序列化"""
        if isinstance(obj, dict):
            return {k: self._make_json_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._make_json_serializable(item) for item in obj]
        elif isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, pd.DataFrame):
            return obj.to_dict('records')
        elif hasattr(obj, '__dict__'):
            return self._make_json_serializable(obj.__dict__)
        elif isinstance(obj, (TrendLevel, TrendDirection, FenXingType)):
            return obj.value
        else:
            return obj


# 核心引擎模块，不包含测试逻辑
# 所有测试应该在独立的测试脚本中进行