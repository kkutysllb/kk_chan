#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强型缠论分析引擎
基于技术方案优化的高性能缠论分析核心
集成机器学习、多时间周期分析、实时预测功能
"""

import sys
import os
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import pandas as pd
import numpy as np
from dataclasses import dataclass, asdict
import json
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

# 添加项目路径
current_dir = os.path.dirname(os.path.abspath(__file__))
chan_theory_dir = os.path.dirname(current_dir)
project_root = os.path.dirname(chan_theory_dir)
sys.path.append(project_root)
sys.path.append(chan_theory_dir)

# 导入优化后的模块
from models.enhanced_chan_models import (
    EnhancedFenXing, IntelligentBi, AdvancedXianDuan, 
    AdvancedZhongShu, TradingSignal, ChanAnalysisResult
)
from analyzers.advanced_structure_analyzer import AdvancedStructureAnalyzer
from analyzers.ml_enhanced_analyzer import MLEnhancedAnalyzer
from analyzers.multi_timeframe_analyzer import EnhancedMultiTimeframeAnalyzer
from utils.enhanced_data_manager import EnhancedDataManager
from utils.cache_manager import CacheManager
from utils.performance_monitor import PerformanceMonitor

logger = logging.getLogger(__name__)

class EnhancedChanEngine:
    """
    增强型缠论分析引擎
    
    核心特性：
    1. 多时间周期联立分析
    2. 机器学习增强预测
    3. 实时分析和缓存优化
    4. 结构映射分析
    5. 高性能并行计算
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """初始化增强型缠论引擎"""
        self.config = config or {}
        
        # 初始化核心组件
        self.data_manager = EnhancedDataManager()
        self.cache_manager = CacheManager()
        self.performance_monitor = PerformanceMonitor()
        
        # 分析器组件
        self.structure_analyzer = AdvancedStructureAnalyzer()
        self.ml_analyzer = MLEnhancedAnalyzer()
        self.multi_timeframe_analyzer = EnhancedMultiTimeframeAnalyzer()
        
        # 线程池
        self.executor = ThreadPoolExecutor(max_workers=8)
        
        # 性能统计
        self.analysis_stats = {
            'total_analyses': 0,
            'cache_hits': 0,
            'avg_computation_time': 0,
            'success_rate': 0
        }
        
        logger.info("增强型缠论引擎初始化完成")
    
    async def comprehensive_analysis(
        self,
        symbol: str,
        timeframes: List[str] = None,
        start_date: datetime = None,
        end_date: datetime = None,
        include_ml_prediction: bool = True,
        include_signals: bool = True,
        config: Dict = None
    ) -> Dict[str, Any]:
        """
        全面缠论分析
        
        Args:
            symbol: 股票代码
            timeframes: 时间周期列表
            start_date: 开始日期
            end_date: 结束日期
            include_ml_prediction: 是否包含机器学习预测
            include_signals: 是否生成交易信号
            config: 分析配置
            
        Returns:
            完整的缠论分析结果
        """
        start_time = time.time()
        
        try:
            # 设置默认参数
            timeframes = timeframes or ['daily', '30min', '5min']
            end_date = end_date or datetime.now()
            start_date = start_date or (end_date - timedelta(days=365))
            
            # 检查缓存
            cache_key = self._generate_cache_key(symbol, timeframes, start_date, end_date)
            cached_result = await self.cache_manager.get(cache_key)
            
            if cached_result:
                logger.info(f"从缓存返回分析结果: {symbol}")
                self.analysis_stats['cache_hits'] += 1
                return cached_result
            
            # 并行获取多时间周期数据
            data_tasks = [
                self._get_timeframe_data(symbol, tf, start_date, end_date)
                for tf in timeframes
            ]
            
            timeframe_data = await asyncio.gather(*data_tasks, return_exceptions=True)
            
            # 验证数据完整性
            valid_data = {}
            for i, (tf, data) in enumerate(zip(timeframes, timeframe_data)):
                if not isinstance(data, Exception) and data is not None and len(data) > 0:
                    valid_data[tf] = data
                else:
                    logger.warning(f"无效数据: {symbol} {tf}")
            
            if not valid_data:
                raise ValueError(f"无法获取有效数据: {symbol}")
            
            # 并行执行多时间周期分析
            analysis_tasks = [
                self._analyze_single_timeframe(symbol, tf, data, config)
                for tf, data in valid_data.items()
            ]
            
            timeframe_results = await asyncio.gather(*analysis_tasks, return_exceptions=True)
            
            # 整合分析结果
            comprehensive_result = {
                'symbol': symbol,
                'analysis_date': datetime.now(),
                'timeframes': list(valid_data.keys()),
                'timeframe_results': {},
                'multi_timeframe_analysis': {},
                'trading_signals': [],
                'ml_predictions': {},
                'risk_assessment': {},
                'computation_time': 0,
                'data_quality_score': 0
            }
            
            # 处理单时间周期结果
            for i, (tf, result) in enumerate(zip(valid_data.keys(), timeframe_results)):
                if not isinstance(result, Exception):
                    comprehensive_result['timeframe_results'][tf] = result
                else:
                    logger.error(f"时间周期分析失败 {symbol} {tf}: {result}")
            
            # 多时间周期综合分析
            if len(comprehensive_result['timeframe_results']) > 1:
                comprehensive_result['multi_timeframe_analysis'] = \
                    await self._multi_timeframe_synthesis(comprehensive_result['timeframe_results'])
            
            # 机器学习增强预测
            if include_ml_prediction and len(comprehensive_result['timeframe_results']) > 0:
                comprehensive_result['ml_predictions'] = \
                    await self._ml_enhanced_prediction(symbol, comprehensive_result['timeframe_results'])
            
            # 生成交易信号
            if include_signals:
                comprehensive_result['trading_signals'] = \
                    await self._generate_comprehensive_signals(comprehensive_result)
            
            # 风险评估
            comprehensive_result['risk_assessment'] = \
                await self._assess_risk(comprehensive_result)
            
            # 计算数据质量评分
            comprehensive_result['data_quality_score'] = \
                self._calculate_data_quality_score(valid_data)
            
            # 记录性能指标
            computation_time = time.time() - start_time
            comprehensive_result['computation_time'] = computation_time
            
            # 缓存结果
            await self.cache_manager.set(cache_key, comprehensive_result, expire=3600)
            
            # 更新统计信息
            await self._update_analysis_stats(computation_time, True)
            
            logger.info(f"缠论分析完成: {symbol}, 耗时: {computation_time:.2f}s")
            
            return comprehensive_result
            
        except Exception as e:
            logger.error(f"缠论分析失败 {symbol}: {str(e)}", exc_info=True)
            await self._update_analysis_stats(time.time() - start_time, False)
            raise
    
    async def _get_timeframe_data(
        self,
        symbol: str,
        timeframe: str,
        start_date: datetime,
        end_date: datetime
    ) -> pd.DataFrame:
        """获取指定时间周期的数据"""
        try:
            data = await self.data_manager.get_kline_data(
                symbol=symbol,
                period=timeframe,
                start_date=start_date,
                end_date=end_date
            )
            
            if data is None or len(data) == 0:
                logger.warning(f"无数据: {symbol} {timeframe}")
                return None
            
            # 数据预处理和清洗
            data = self._preprocess_kline_data(data)
            
            return data
            
        except Exception as e:
            logger.error(f"获取数据失败 {symbol} {timeframe}: {str(e)}")
            return None
    
    async def _analyze_single_timeframe(
        self,
        symbol: str,
        timeframe: str,
        data: pd.DataFrame,
        config: Dict = None
    ) -> Dict[str, Any]:
        """分析单个时间周期"""
        try:
            # 基础结构分析
            structure_result = await self.structure_analyzer.analyze_enhanced_structure(
                data=data,
                timeframe=timeframe,
                config=config
            )
            
            # 技术指标分析
            technical_result = await self._analyze_technical_indicators(data, timeframe)
            
            # 合并结果
            timeframe_result = {
                'timeframe': timeframe,
                'data_points': len(data),
                'structure_analysis': structure_result,
                'technical_analysis': technical_result,
                'analysis_timestamp': datetime.now(),
                'data_quality': self._assess_data_quality(data)
            }
            
            return timeframe_result
            
        except Exception as e:
            logger.error(f"单时间周期分析失败 {symbol} {timeframe}: {str(e)}")
            raise
    
    async def _multi_timeframe_synthesis(
        self,
        timeframe_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """多时间周期综合分析"""
        try:
            return await self.multi_timeframe_analyzer.synthesize_analysis(timeframe_results)
            
        except Exception as e:
            logger.error(f"多时间周期综合分析失败: {str(e)}")
            return {}
    
    async def _ml_enhanced_prediction(
        self,
        symbol: str,
        timeframe_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """机器学习增强预测"""
        try:
            return await self.ml_analyzer.predict_buy_sell_points(
                symbol=symbol,
                timeframe_results=timeframe_results
            )
            
        except Exception as e:
            logger.error(f"ML预测失败 {symbol}: {str(e)}")
            return {}
    
    async def _generate_comprehensive_signals(
        self,
        analysis_result: Dict[str, Any]
    ) -> List[TradingSignal]:
        """生成综合交易信号"""
        try:
            signals = []
            
            # 从各时间周期提取信号
            for timeframe, tf_result in analysis_result['timeframe_results'].items():
                tf_signals = await self._extract_timeframe_signals(tf_result, timeframe)
                signals.extend(tf_signals)
            
            # 多时间周期信号确认
            confirmed_signals = await self._confirm_multi_timeframe_signals(
                signals, analysis_result['multi_timeframe_analysis']
            )
            
            # 机器学习信号增强
            if analysis_result.get('ml_predictions'):
                enhanced_signals = await self._enhance_signals_with_ml(
                    confirmed_signals, analysis_result['ml_predictions']
                )
                return enhanced_signals
            
            return confirmed_signals
            
        except Exception as e:
            logger.error(f"生成交易信号失败: {str(e)}")
            return []
    
    async def _assess_risk(self, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """风险评估"""
        try:
            risk_metrics = {
                'overall_risk_level': 'medium',
                'trend_consistency': 0,
                'structure_stability': 0,
                'volatility_risk': 0,
                'signal_reliability': 0,
                'recommendations': []
            }
            
            # 趋势一致性评估
            if analysis_result.get('multi_timeframe_analysis'):
                trend_data = analysis_result['multi_timeframe_analysis'].get('trend_consistency', {})
                risk_metrics['trend_consistency'] = trend_data.get('consistency_score', 0)
            
            # 结构稳定性评估
            structure_scores = []
            for tf_result in analysis_result['timeframe_results'].values():
                if 'structure_analysis' in tf_result:
                    structure_quality = tf_result['structure_analysis'].get('quality_score', 0)
                    structure_scores.append(structure_quality)
            
            if structure_scores:
                risk_metrics['structure_stability'] = np.mean(structure_scores)
            
            # 综合风险等级评估
            overall_score = np.mean([
                risk_metrics['trend_consistency'],
                risk_metrics['structure_stability']
            ])
            
            if overall_score > 0.7:
                risk_metrics['overall_risk_level'] = 'low'
            elif overall_score < 0.3:
                risk_metrics['overall_risk_level'] = 'high'
            
            return risk_metrics
            
        except Exception as e:
            logger.error(f"风险评估失败: {str(e)}")
            return {}
    
    async def batch_analysis(
        self,
        symbols: List[str],
        timeframes: List[str] = None,
        start_date: datetime = None,
        end_date: datetime = None,
        max_concurrent: int = 5
    ) -> List[Dict[str, Any]]:
        """批量缠论分析"""
        try:
            semaphore = asyncio.Semaphore(max_concurrent)
            
            async def analyze_with_semaphore(symbol):
                async with semaphore:
                    try:
                        result = await self.comprehensive_analysis(
                            symbol=symbol,
                            timeframes=timeframes,
                            start_date=start_date,
                            end_date=end_date
                        )
                        result['success'] = True
                        return result
                    except Exception as e:
                        logger.error(f"批量分析失败 {symbol}: {str(e)}")
                        return {
                            'symbol': symbol,
                            'success': False,
                            'error': str(e),
                            'timestamp': datetime.now()
                        }
            
            tasks = [analyze_with_semaphore(symbol) for symbol in symbols]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # 过滤异常结果
            valid_results = []
            for result in results:
                if not isinstance(result, Exception):
                    valid_results.append(result)
                else:
                    logger.error(f"批量分析异常: {result}")
            
            return valid_results
            
        except Exception as e:
            logger.error(f"批量分析失败: {str(e)}")
            return []
    
    async def real_time_prediction(
        self,
        symbol: str,
        timeframe: str = 'daily',
        include_confidence: bool = True
    ) -> Dict[str, Any]:
        """实时预测"""
        try:
            # 获取最新数据
            end_date = datetime.now()
            start_date = end_date - timedelta(days=90)
            
            data = await self._get_timeframe_data(symbol, timeframe, start_date, end_date)
            
            if data is None or len(data) == 0:
                raise ValueError(f"无法获取实时数据: {symbol}")
            
            # 快速结构分析
            structure_result = await self.structure_analyzer.quick_analysis(data, timeframe)
            
            # ML实时预测
            prediction = await self.ml_analyzer.real_time_predict(
                symbol=symbol,
                data=data,
                structure_result=structure_result
            )
            
            if include_confidence:
                prediction['confidence_analysis'] = await self._calculate_prediction_confidence(
                    prediction, structure_result
                )
            
            prediction['timestamp'] = datetime.now()
            prediction['data_freshness'] = (datetime.now() - data.index[-1]).total_seconds() / 3600
            
            return prediction
            
        except Exception as e:
            logger.error(f"实时预测失败 {symbol}: {str(e)}")
            raise
    
    async def get_market_structure_for_chart(
        self,
        symbol: str,
        timeframe: str,
        structure_type: str = 'all'
    ) -> Dict[str, Any]:
        """获取图表专用的市场结构数据"""
        try:
            # 获取缓存的分析结果
            cache_key = f"structure_chart:{symbol}:{timeframe}:{structure_type}"
            cached_data = await self.cache_manager.get(cache_key)
            
            if cached_data:
                return cached_data
            
            # 执行结构分析
            end_date = datetime.now()
            start_date = end_date - timedelta(days=180)
            
            data = await self._get_timeframe_data(symbol, timeframe, start_date, end_date)
            structure_result = await self.structure_analyzer.analyze_enhanced_structure(
                data, timeframe
            )
            
            # 转换为图表格式
            chart_data = await self._convert_structure_to_chart_format(
                structure_result, structure_type
            )
            
            # 缓存结果
            await self.cache_manager.set(cache_key, chart_data, expire=1800)
            
            return chart_data
            
        except Exception as e:
            logger.error(f"获取图表结构数据失败 {symbol}: {str(e)}")
            raise
    
    # 辅助方法
    def _generate_cache_key(self, symbol: str, timeframes: List[str], 
                           start_date: datetime, end_date: datetime) -> str:
        """生成缓存键"""
        tf_str = '_'.join(sorted(timeframes))
        date_str = f"{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}"
        return f"chan_analysis:{symbol}:{tf_str}:{date_str}"
    
    def _preprocess_kline_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """预处理K线数据"""
        # 数据清洗
        data = data.dropna()
        
        # 确保数据类型正确
        numeric_columns = ['open', 'high', 'low', 'close', 'volume']
        for col in numeric_columns:
            if col in data.columns:
                data[col] = pd.to_numeric(data[col], errors='coerce')
        
        # 排序
        data = data.sort_index()
        
        return data
    
    def _calculate_data_quality_score(self, data_dict: Dict[str, pd.DataFrame]) -> float:
        """计算数据质量评分"""
        scores = []
        
        for timeframe, data in data_dict.items():
            if data is not None and len(data) > 0:
                # 完整性评分
                completeness = 1 - (data.isnull().sum().sum() / (len(data) * len(data.columns)))
                
                # 连续性评分
                if len(data) > 1:
                    time_gaps = data.index.to_series().diff().dropna()
                    expected_freq = time_gaps.mode().iloc[0] if len(time_gaps.mode()) > 0 else time_gaps.median()
                    continuity = (time_gaps == expected_freq).mean()
                else:
                    continuity = 1.0
                
                # 合理性评分 (价格数据的基本合理性)
                reasonableness = 1.0
                if 'high' in data.columns and 'low' in data.columns:
                    invalid_hlc = (data['high'] < data['low']).sum()
                    reasonableness = 1 - (invalid_hlc / len(data))
                
                timeframe_score = np.mean([completeness, continuity, reasonableness])
                scores.append(timeframe_score)
        
        return np.mean(scores) if scores else 0.0
    
    async def _update_analysis_stats(self, computation_time: float, success: bool):
        """更新分析统计信息"""
        self.analysis_stats['total_analyses'] += 1
        
        if success:
            # 更新平均计算时间
            current_avg = self.analysis_stats['avg_computation_time']
            total_count = self.analysis_stats['total_analyses']
            
            new_avg = ((current_avg * (total_count - 1)) + computation_time) / total_count
            self.analysis_stats['avg_computation_time'] = new_avg
        
        # 更新成功率
        success_count = self.analysis_stats.get('success_count', 0)
        if success:
            success_count += 1
        
        self.analysis_stats['success_count'] = success_count
        self.analysis_stats['success_rate'] = success_count / self.analysis_stats['total_analyses']
    
    def get_analysis_statistics(self) -> Dict[str, Any]:
        """获取分析统计信息"""
        return self.analysis_stats.copy()
    
    async def __aenter__(self):
        """异步上下文管理器入口"""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        # 清理资源
        if hasattr(self.executor, 'shutdown'):
            self.executor.shutdown(wait=True)
        
        await self.cache_manager.close()
        await self.data_manager.close()