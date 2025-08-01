#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
缠论分析数据API v2
基于最新的缠论v2核心模块（形态学+动力学），提供完整的缠论分析服务
支持多级别分析、动力学分析、买卖点识别等高级功能
"""

import sys
import os
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union
import logging

# 添加项目路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

# 导入缠论v2核心组件
from chan_theory_v2.core.chan_engine import ChanEngine, ChanAnalysisResult, AnalysisLevel, quick_analyze, multi_level_analyze
from chan_theory_v2.models.enums import TimeLevel, BiDirection, SegDirection, ZhongShuType
from chan_theory_v2.models.dynamics import BuySellPointType, BackChi, DynamicsConfig
from chan_theory_v2.config.chan_config import ChanConfig
from database.db_handler import get_db_handler

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ChanDataAPIv2:
    """缠论数据API v2 - 基于最新缠论引擎的完整分析服务"""
    
    def __init__(self):
        """初始化API"""
        self.db_handler = get_db_handler()
        self.db = self.db_handler.db
        
        # 初始化缠论引擎
        self.chan_engine = ChanEngine()
        
        logger.info("🚀 缠论数据API v2初始化完成")
    
    def get_symbols_list(self, query: str = "") -> List[Dict[str, str]]:
        """获取股票列表"""
        try:
            collection = self.db["infrastructure_stock_basic"]
            
            # 构建搜索条件
            search_filter = {"ts_code": {"$exists": True}, "name": {"$exists": True}}
            
            if query and query.strip():
                # 支持按股票代码或名称搜索
                query = query.strip().upper()
                search_filter["$or"] = [
                    {"ts_code": {"$regex": query, "$options": "i"}},
                    {"name": {"$regex": query, "$options": "i"}}
                ]
                logger.info(f"🔍 搜索股票: {query}")
            
            cursor = collection.find(
                search_filter,
                {"ts_code": 1, "name": 1, "_id": 0}
            ).limit(100)  # 搜索时限制100个结果
            
            stocks = []
            for doc in cursor:
                stocks.append({
                    "value": doc.get("ts_code", ""),
                    "label": f"{doc.get('ts_code', '')} - {doc.get('name', '')}",
                    "name": doc.get("name", "")
                })
            
            logger.info(f"📋 获取到 {len(stocks)} 个股票{'（搜索结果）' if query else ''}")
            return stocks
            
        except Exception as e:
            logger.error(f"❌ 获取股票列表失败: {e}")
            return []
    
    def analyze_symbol_complete(self, 
                              symbol: str, 
                              timeframe: str = "daily", 
                              days: int = 90,
                              analysis_level: str = "complete") -> Dict[str, Any]:
        """
        完整的缠论分析
        
        Args:
            symbol: 股票代码
            timeframe: 时间级别 ("5min", "30min", "daily")
            days: 分析天数
            analysis_level: 分析级别 ("basic", "standard", "advanced", "complete")
            
        Returns:
            完整的分析结果
        """
        try:
            logger.info(f"🔍 开始缠论v2分析 {symbol} ({timeframe}, {days}天, {analysis_level}级别)")
            
            # 获取数据
            time_level = self._get_time_level(timeframe)
            data = self._fetch_stock_data(symbol, time_level, days)
            
            if not data:
                logger.warning(f"⚠️ 无法获取 {symbol} 的数据")
                return self._generate_empty_result(symbol, timeframe)
            
            # 设置分析级别
            level_mapping = {
                "basic": AnalysisLevel.BASIC,
                "standard": AnalysisLevel.STANDARD,
                "advanced": AnalysisLevel.ADVANCED,
                "complete": AnalysisLevel.COMPLETE
            }
            analysis_level_enum = level_mapping.get(analysis_level, AnalysisLevel.COMPLETE)
            
            # 执行缠论分析
            result = self.chan_engine.analyze(
                data=data,
                symbol=symbol,
                time_level=time_level,
                analysis_level=analysis_level_enum
            )
            
            # 转换为前端标准格式
            frontend_data = self._convert_to_frontend_format(result, timeframe, days)
            
            logger.info(f"✅ {symbol} 缠论v2分析完成")
            return frontend_data
            
        except Exception as e:
            logger.error(f"❌ 分析 {symbol} 失败: {e}")
            import traceback
            traceback.print_exc()
            return self._generate_empty_result(symbol, timeframe)
    
    def analyze_multi_level(self, 
                          symbol: str, 
                          levels: List[str] = ["daily", "30min", "5min"],
                          days: int = 90) -> Dict[str, Any]:
        """
        多级别缠论分析
        
        Args:
            symbol: 股票代码
            levels: 分析级别列表
            days: 分析天数
            
        Returns:
            多级别分析结果
        """
        try:
            logger.info(f"🔍 开始多级别缠论分析 {symbol} ({levels}, {days}天)")
            
            # 准备多级别数据
            level_data = {}
            for level_str in levels:
                time_level = self._get_time_level(level_str)
                data = self._fetch_stock_data(symbol, time_level, days)
                if data:
                    level_data[time_level] = data
                    logger.info(f"✅ {level_str}数据: {len(data)} 条")
                else:
                    logger.warning(f"⚠️ 无法获取{level_str}数据")
            
            if not level_data:
                logger.warning(f"⚠️ 无任何级别数据可用于 {symbol}")
                return self._generate_empty_multi_level_result(symbol, levels)
            
            # 执行多级别分析
            results = self.chan_engine.analyze_multi_level(level_data, symbol)
            
            # 转换为前端格式
            frontend_data = self._convert_multi_level_to_frontend(results, symbol, levels, days)
            
            logger.info(f"✅ {symbol} 多级别分析完成，共{len(results)}个级别")
            return frontend_data
            
        except Exception as e:
            logger.error(f"❌ 多级别分析 {symbol} 失败: {e}")
            import traceback
            traceback.print_exc()
            return self._generate_empty_multi_level_result(symbol, levels)
    
    def get_trading_signals(self, symbol: str, timeframe: str = "daily", days: int = 30) -> Dict[str, Any]:
        """
        获取交易信号
        
        Args:
            symbol: 股票代码
            timeframe: 时间级别
            days: 分析天数
            
        Returns:
            交易信号数据
        """
        try:
            logger.info(f"🎯 获取交易信号 {symbol} ({timeframe}, {days}天)")
            
            # 执行标准分析（包含动力学）
            time_level = self._get_time_level(timeframe)
            data = self._fetch_stock_data(symbol, time_level, days)
            
            if not data:
                return {"signals": [], "summary": {"total": 0, "buy": 0, "sell": 0}}
            
            result = self.chan_engine.analyze(
                data=data,
                symbol=symbol,
                time_level=time_level,
                analysis_level=AnalysisLevel.STANDARD
            )
            
            # 获取交易信号
            signals = self.chan_engine.get_trading_signals(result)
            
            # 转换为前端格式
            frontend_signals = self._convert_signals_to_frontend(signals)
            
            logger.info(f"✅ 获取到 {len(signals['signals'])} 个交易信号")
            return frontend_signals
            
        except Exception as e:
            logger.error(f"❌ 获取交易信号失败: {e}")
            return {"signals": [], "summary": {"total": 0, "buy": 0, "sell": 0}}
    
    def _fetch_stock_data(self, symbol: str, time_level: TimeLevel, days: int) -> List[Dict]:
        """获取股票数据"""
        try:
            # 根据时间级别选择集合
            collection_mapping = {
                TimeLevel.MIN_5: "stock_kline_5min",
                TimeLevel.MIN_30: "stock_kline_30min", 
                TimeLevel.DAILY: "stock_kline_daily"
            }
            
            collection_name = collection_mapping.get(time_level, "stock_kline_daily")
            collection = self.db[collection_name]
            
            # 构建查询
            query = {"ts_code": symbol}
            
            # 计算数据量（根据级别调整）
            if time_level == TimeLevel.MIN_5:
                limit = days * 48  # 5分钟: 每天约48个数据点
            elif time_level == TimeLevel.MIN_30:
                limit = days * 8   # 30分钟: 每天约8个数据点
            else:
                limit = days       # 日线: 每天1个数据点
            
            # 获取数据
            if time_level == TimeLevel.DAILY:
                # 添加日期范围限制，获取最近的数据
                from datetime import datetime, timedelta
                end_date = datetime.now()
                start_date = end_date - timedelta(days=days)
                
                # 将日期转换为字符串格式，与数据库中的格式匹配
                end_date_str = end_date.strftime('%Y%m%d')
                start_date_str = start_date.strftime('%Y%m%d')
                
                # 确保使用字符串格式的日期进行查询，与数据库中的格式匹配
                query.update({
                    'trade_date': {
                        '$gte': start_date_str,
                        '$lte': end_date_str
                    }
                })
                
                # 按日期升序排序，获取指定日期范围内的数据
                cursor = collection.find(query).sort("trade_date", 1)
                logger.info(f"📅 日K查询范围: {start_date_str} 至 {end_date_str}")
            else:
                cursor = collection.find(query).sort("trade_time", -1).limit(limit)
                
            raw_data = list(cursor)
            
            if time_level != TimeLevel.DAILY:
                raw_data.reverse()  # 分钟数据转为升序
            
            # 转换数据格式
            converted_data = self._convert_data_format(raw_data, time_level)
            
            logger.info(f"📊 获取 {symbol} {time_level.value} 数据: {len(converted_data)} 条")
            return converted_data
            
        except Exception as e:
            logger.error(f"❌ 获取数据失败: {e}")
            return []
    
    def _convert_data_format(self, raw_data: List[Dict], time_level: TimeLevel) -> List[Dict]:
        """转换数据格式"""
        converted_data = []
        
        for item in raw_data:
            try:
                # 处理时间戳
                if time_level == TimeLevel.DAILY:
                    trade_date_str = str(item['trade_date'])
                    timestamp = datetime.strptime(trade_date_str, '%Y%m%d')
                else:
                    trade_time_str = str(item['trade_time'])
                    timestamp = datetime.strptime(trade_time_str, '%Y-%m-%d %H:%M:%S')
                
                converted_item = {
                    'timestamp': timestamp,
                    'open': float(item['open']),
                    'high': float(item['high']),
                    'low': float(item['low']),
                    'close': float(item['close']),
                    'volume': int(float(item.get('vol', item.get('volume', 1)))),
                    'amount': float(item.get('amount', 0)),
                    'symbol': item['ts_code']
                }
                
                # 验证数据有效性
                if all(converted_item[k] > 0 for k in ['open', 'high', 'low', 'close']):
                    converted_data.append(converted_item)
                    
            except Exception as e:
                logger.warning(f"转换数据点失败: {e}")
                continue
        
        return converted_data
    
    def _convert_to_frontend_format(self, result: ChanAnalysisResult, timeframe: str, days: int) -> Dict[str, Any]:
        """转换分析结果为前端格式"""
        
        # 获取统计信息
        stats = result.get_statistics()
        
        # 1. K线数据
        kline_data = self._convert_klines_to_echarts(result.processed_klines)
        
        # 2. 分型数据
        fenxing_data = self._convert_fenxings_to_echarts(result.fenxings)
        
        # 3. 笔数据
        bi_data = self._convert_bis_to_echarts(result.bis)
        
        # 4. 线段数据
        seg_data = self._convert_segs_to_echarts(result.segs)
        
        # 5. 中枢数据
        zhongshu_data = self._convert_zhongshus_to_echarts(result.zhongshus)
        
        # 6. 买卖点数据
        signal_data = self._convert_buy_sell_points_to_echarts(result.buy_sell_points)
        
        # 7. 背驰分析数据
        backchi_data = self._convert_backchi_to_echarts(result.backchi_analyses)
        
        # 8. MACD数据（基于处理后的K线计算）
        macd_data = self._calculate_macd_from_klines(result.processed_klines, kline_data.get("categories", []))
        
        # 构建完整的前端数据结构
        frontend_data = {
            # 基础元信息
            "meta": {
                "symbol": result.symbol,
                "timeframe": timeframe,
                "analysis_level": result.analysis_level.value,
                "analysis_time": result.analysis_time.isoformat(),
                "data_range": {
                    "days": days,
                    "start_date": (datetime.now() - timedelta(days=days)).isoformat(),
                    "end_date": datetime.now().isoformat()
                },
                "data_count": stats['processed_klines_count']
            },
            
            # 图表数据 - ECharts标准格式
            "chart_data": {
                # K线数据
                "kline": kline_data,
                
                # 技术指标
                "indicators": {
                    "macd": macd_data
                },
                
                # 缠论结构
                "chan_structures": {
                    "fenxing": fenxing_data,    # 分型点
                    "bi": bi_data,              # 笔
                    "seg": seg_data,            # 线段
                    "zhongshu": zhongshu_data   # 中枢
                },
                
                # 动力学分析
                "dynamics": {
                    "buy_sell_points": signal_data,  # 买卖点
                    "backchi": backchi_data          # 背驰分析
                }
            },
            
            # 分析摘要
            "analysis": {
                "summary": {
                    "klines_original": stats['klines_count'],
                    "klines_processed": stats['processed_klines_count'],
                    "fenxing_count": stats['fenxings_count'],
                    "bi_count": stats['bis_count'],
                    "seg_count": stats['segs_count'],
                    "zhongshu_count": stats['zhongshus_count'],
                    "backchi_count": stats['backchi_count'],
                    "buy_sell_points_count": stats['buy_sell_points_count'],
                    "buy_points_count": stats['buy_points_count'],
                    "sell_points_count": stats['sell_points_count']
                },
                
                # 综合评估
                "evaluation": {
                    "trend_direction": result.trend_direction,
                    "trend_strength": result.trend_strength,
                    "risk_level": result.risk_level,
                    "confidence_score": result.confidence_score,
                    "recommended_action": result.recommended_action,
                    "entry_price": result.entry_price,
                    "stop_loss": result.stop_loss,
                    "take_profit": result.take_profit
                },
                
                # 最新信号
                "latest_signals": [
                    {
                        "type": str(point.point_type),
                        "price": point.price,
                        "timestamp": point.timestamp.isoformat(),
                        "reliability": point.reliability,
                        "strength": point.strength
                    }
                    for point in result.get_latest_signals(5)
                ]
            },
            
            # 图表配置
            "chart_config": {
                "colors": {
                    "up_candle": "#ef5150",      # 红色K线
                    "down_candle": "#26a69a",    # 绿色K线
                    "fenxing_top": "#f44336",    # 顶分型-红色
                    "fenxing_bottom": "#4caf50", # 底分型-绿色
                    "bi_up": "#e91e63",          # 上笔-粉色
                    "bi_down": "#2196f3",        # 下笔-蓝色
                    "seg_up": "#ff5722",         # 上线段-橙红色
                    "seg_down": "#3f51b5",       # 下线段-靛蓝色
                    "zhongshu": "#ff9800",       # 中枢-橙色
                    "buy_point": "#4caf50",      # 买点-绿色
                    "sell_point": "#f44336",     # 卖点-红色
                    "backchi": "#9c27b0"         # 背驰-紫色
                }
            }
        }
        
        return frontend_data
    
    def _convert_klines_to_echarts(self, klines) -> Dict[str, Any]:
        """转换K线数据为ECharts格式"""
        if not klines or len(klines) == 0:
            return {"categories": [], "values": [], "volumes": []}
        
        categories = []  # 时间轴
        values = []     # K线数据 [open, close, low, high]
        volumes = []    # 成交量
        
        for kline in klines:
            try:
                # 格式化时间
                if hasattr(kline.timestamp, 'strftime'):
                    timestamp = kline.timestamp.strftime('%Y-%m-%d %H:%M')
                else:
                    timestamp = str(kline.timestamp)
                
                categories.append(timestamp)
                
                # K线数据 [open, close, low, high]
                values.append([
                    float(kline.open),
                    float(kline.close),
                    float(kline.low),
                    float(kline.high)
                ])
                
                volumes.append(float(kline.volume))
                
            except Exception as e:
                logger.warning(f"转换K线数据点失败: {e}")
                continue
        
        return {
            "categories": categories,  # X轴时间
            "values": values,         # K线数据
            "volumes": volumes        # 成交量
        }
    
    def _convert_fenxings_to_echarts(self, fenxings) -> List[Dict[str, Any]]:
        """转换分型数据为ECharts标记格式"""
        if not fenxings or len(fenxings) == 0:
            return []
        
        fenxing_points = []
        
        for fenxing in fenxings:
            try:
                timestamp = fenxing.timestamp.strftime('%Y-%m-%d %H:%M')
                
                fenxing_points.append({
                    "name": f"{'顶' if fenxing.is_top else '底'}分型",
                    "coord": [timestamp, float(fenxing.price)],
                    "value": float(fenxing.price),
                    "type": "top" if fenxing.is_top else "bottom",
                    "direction": "up" if fenxing.is_top else "down",
                    "strength": float(fenxing.strength),
                    "confirmed": bool(fenxing.is_confirmed),
                    "symbol": "triangle",
                    "symbolSize": 8,
                    "itemStyle": {
                        "color": "#f44336" if fenxing.is_top else "#4caf50"
                    }
                })
            except Exception as e:
                logger.warning(f"转换分型数据失败: {e}")
                continue
        
        return fenxing_points
    
    def _convert_bis_to_echarts(self, bis) -> List[Dict[str, Any]]:
        """转换笔数据为ECharts线条格式"""
        if not bis or len(bis) == 0:
            return []
        
        bi_lines = []
        
        for idx, bi in enumerate(bis):
            try:
                start_time = bi.start_time.strftime('%Y-%m-%d %H:%M')
                end_time = bi.end_time.strftime('%Y-%m-%d %H:%M')
                
                bi_lines.append({
                    "id": f"bi_{idx}",
                    "name": f"{'上' if bi.is_up else '下'}笔",
                    "coords": [
                        [start_time, float(bi.start_price)],
                        [end_time, float(bi.end_price)]
                    ],
                    "direction": bi.direction.value,
                    "amplitude": float(bi.amplitude),
                    "strength": float(bi.strength),
                    "duration": bi.duration,
                    "lineStyle": {
                        "color": "#e91e63" if bi.is_up else "#2196f3",
                        "width": 2
                    }
                })
            except Exception as e:
                logger.warning(f"转换笔数据失败: {e}")
                continue
        
        return bi_lines
    
    def _convert_segs_to_echarts(self, segs) -> List[Dict[str, Any]]:
        """转换线段数据为ECharts线条格式"""
        if not segs or len(segs) == 0:
            return []
        
        seg_lines = []
        
        for idx, seg in enumerate(segs):
            try:
                start_time = seg.start_time.strftime('%Y-%m-%d %H:%M')
                end_time = seg.end_time.strftime('%Y-%m-%d %H:%M')
                
                seg_lines.append({
                    "id": f"seg_{idx}",
                    "name": f"{'上' if seg.is_up else '下'}线段",
                    "coords": [
                        [start_time, float(seg.start_price)],
                        [end_time, float(seg.end_price)]
                    ],
                    "direction": seg.direction.value,
                    "amplitude": float(seg.amplitude),
                    "strength": float(seg.strength),
                    "integrity": float(seg.integrity),
                    "bi_count": seg.bi_count,
                    "duration": seg.duration,
                    "lineStyle": {
                        "color": "#ff5722" if seg.is_up else "#3f51b5",
                        "width": 3
                    }
                })
            except Exception as e:
                logger.warning(f"转换线段数据失败: {e}")
                continue
        
        return seg_lines
    
    def _convert_zhongshus_to_echarts(self, zhongshus) -> List[Dict[str, Any]]:
        """转换中枢数据为ECharts区域格式"""
        if not zhongshus or len(zhongshus) == 0:
            return []
        
        zhongshu_areas = []
        
        for idx, zs in enumerate(zhongshus):
            try:
                start_time = zs.start_time.strftime('%Y-%m-%d %H:%M')
                end_time = zs.end_time.strftime('%Y-%m-%d %H:%M')
                
                zhongshu_areas.append({
                    "id": f"zs_{idx}",
                    "name": f"中枢{idx+1}",
                    "coords": [
                        [start_time, float(zs.low)],    # 左下角
                        [end_time, float(zs.high)]      # 右上角
                    ],
                    "high": float(zs.high),
                    "low": float(zs.low),
                    "center": float(zs.center),
                    "strength": float(zs.strength),
                    "stability": float(zs.stability),
                    "seg_count": zs.seg_count,
                    "extend_count": zs.extend_count,
                    "is_active": zs.is_active,
                    "itemStyle": {
                        "color": "rgba(255, 152, 0, 0.2)",  # 半透明橙色
                        "borderColor": "#ff9800",
                        "borderWidth": 1
                    }
                })
            except Exception as e:
                logger.warning(f"转换中枢数据失败: {e}")
                continue
        
        return zhongshu_areas
    
    def _convert_buy_sell_points_to_echarts(self, buy_sell_points) -> List[Dict[str, Any]]:
        """转换买卖点数据为ECharts标记格式"""
        if not buy_sell_points:
            return []
        
        signal_marks = []
        
        for idx, point in enumerate(buy_sell_points):
            try:
                timestamp = point.timestamp.strftime('%Y-%m-%d %H:%M')
                
                signal_marks.append({
                    "id": f"signal_{idx}",
                    "name": str(point.point_type),
                    "coord": [timestamp, float(point.price)],
                    "value": float(point.price),
                    "type": "buy" if point.point_type.is_buy() else "sell",
                    "point_level": point.point_type.get_level(),  # 1, 2, 3类
                    "strength": float(point.strength),
                    "reliability": float(point.reliability),
                    "confirmed_higher": point.confirmed_by_higher_level,
                    "confirmed_lower": point.confirmed_by_lower_level,
                    "symbol": "arrow",
                    "symbolSize": 12,
                    "symbolRotate": 90 if point.point_type.is_buy() else -90,
                    "itemStyle": {
                        "color": "#4caf50" if point.point_type.is_buy() else "#f44336"
                    }
                })
            except Exception as e:
                logger.warning(f"转换买卖点数据失败: {e}")
                continue
        
        return signal_marks
    
    def _convert_backchi_to_echarts(self, backchi_analyses) -> List[Dict[str, Any]]:
        """转换背驰分析数据为ECharts标记格式"""
        if not backchi_analyses:
            return []
        
        backchi_marks = []
        
        for idx, backchi in enumerate(backchi_analyses):
            try:
                if not backchi.is_valid_backchi():
                    continue
                
                timestamp = backchi.current_seg.end_time.strftime('%Y-%m-%d %H:%M')
                
                backchi_marks.append({
                    "id": f"backchi_{idx}",
                    "name": str(backchi.backchi_type),
                    "coord": [timestamp, float(backchi.current_seg.end_price)],
                    "value": float(backchi.current_seg.end_price),
                    "type": "top" if backchi.backchi_type == BackChi.TOP_BACKCHI else "bottom",
                    "reliability": float(backchi.reliability),
                    "strength_ratio": float(backchi.strength_ratio),
                    "macd_divergence": float(backchi.macd_divergence),
                    "symbol": "diamond",
                    "symbolSize": 10,
                    "itemStyle": {
                        "color": "#9c27b0"  # 紫色
                    }
                })
            except Exception as e:
                logger.warning(f"转换背驰数据失败: {e}")
                continue
        
        return backchi_marks
    
    def _calculate_macd_from_klines(self, klines, categories: List[str]) -> Dict[str, List]:
        """基于K线数据计算MACD指标"""
        try:
            if not klines or len(klines) == 0 or len(categories) == 0:
                return {"dif": [], "dea": [], "macd": []}
            
            # 提取收盘价
            close_prices = [float(kline.close) for kline in klines]
            
            if len(close_prices) < 26:  # MACD需要至少26个数据点
                return {"dif": [], "dea": [], "macd": []}
            
            # MACD参数
            fast_period = 12
            slow_period = 26
            signal_period = 9
            
            # 计算EMA
            def calculate_ema(values, period):
                multiplier = 2.0 / (period + 1)
                ema = [sum(values[:period]) / period]  # 初始值使用简单平均
                
                for i in range(period, len(values)):
                    ema.append((values[i] * multiplier) + (ema[-1] * (1 - multiplier)))
                
                return [0.0] * (period - 1) + ema
            
            # 计算EMA12和EMA26
            ema12 = calculate_ema(close_prices, fast_period)
            ema26 = calculate_ema(close_prices, slow_period)
            
            # 计算DIF线
            dif = [ema12[i] - ema26[i] for i in range(len(ema12))]
            
            # 计算DEA线
            dea = calculate_ema(dif[slow_period-1:], signal_period)
            dea = [0.0] * (slow_period - 1) + dea
            
            # 计算MACD柱
            macd = [(dif[i] - dea[i]) * 2 for i in range(len(dif))]
            
            # 保留精度并对齐数据长度
            min_length = min(len(categories), len(dif), len(dea), len(macd))
            
            return {
                "dif": [round(dif[i], 6) for i in range(min_length)],
                "dea": [round(dea[i], 6) for i in range(min_length)],
                "macd": [round(macd[i], 6) for i in range(min_length)]
            }
            
        except Exception as e:
            logger.error(f"计算MACD失败: {e}")
            return {"dif": [], "dea": [], "macd": []}
    
    def _convert_multi_level_to_frontend(self, results: Dict[TimeLevel, ChanAnalysisResult], 
                                       symbol: str, levels: List[str], days: int) -> Dict[str, Any]:
        """转换多级别分析结果为前端格式"""
        
        multi_level_data = {
            "meta": {
                "symbol": symbol,
                "levels": levels,
                "analysis_time": datetime.now().isoformat(),
                "days": days
            },
            "results": {},
            "comparison": {
                "level_consistency": {},
                "signal_confirmation": {},
                "trend_alignment": {}
            }
        }
        
        # 转换各级别结果
        for time_level, result in results.items():
            level_str = time_level.value
            
            # 获取基础数据（简化版，避免重复大量K线数据）
            stats = result.get_statistics()
            
            multi_level_data["results"][level_str] = {
                "meta": {
                    "level": level_str,
                    "analysis_level": result.analysis_level.value,
                    "data_count": stats['processed_klines_count']
                },
                
                "structures": {
                    "fenxing_count": stats['fenxings_count'],
                    "bi_count": stats['bis_count'],
                    "seg_count": stats['segs_count'],
                    "zhongshu_count": stats['zhongshus_count']
                },
                
                "dynamics": {
                    "backchi_count": stats['backchi_count'],
                    "buy_sell_points_count": stats['buy_sell_points_count'],
                    "buy_points_count": stats['buy_points_count'],
                    "sell_points_count": stats['sell_points_count']
                },
                
                "evaluation": {
                    "trend_direction": result.trend_direction,
                    "trend_strength": result.trend_strength,
                    "risk_level": result.risk_level,
                    "confidence_score": result.confidence_score,
                    "recommended_action": result.recommended_action,
                    "level_consistency_score": result.level_consistency_score
                },
                
                "latest_signals": [
                    {
                        "type": str(point.point_type),
                        "price": point.price,
                        "timestamp": point.timestamp.isoformat(),
                        "reliability": point.reliability
                    }
                    for point in result.get_latest_signals(3)
                ]
            }
            
            # 级别一致性分析
            multi_level_data["comparison"]["level_consistency"][level_str] = result.level_consistency_score
        
        # 计算级别间信号确认
        self._analyze_signal_confirmation(multi_level_data, results)
        
        return multi_level_data
    
    def _analyze_signal_confirmation(self, multi_level_data: Dict, results: Dict[TimeLevel, ChanAnalysisResult]):
        """分析级别间信号确认"""
        try:
            # 获取所有级别的最新信号
            all_signals = {}
            for time_level, result in results.items():
                latest_signals = result.get_latest_signals(3)
                all_signals[time_level.value] = [
                    {
                        "type": str(point.point_type),
                        "timestamp": point.timestamp,
                        "reliability": point.reliability
                    }
                    for point in latest_signals
                ]
            
            # 计算信号一致性
            signal_confirmation = {}
            level_names = list(all_signals.keys())
            
            for i, level1 in enumerate(level_names):
                for level2 in level_names[i+1:]:
                    key = f"{level1}_vs_{level2}"
                    signal_confirmation[key] = self._calculate_signal_similarity(
                        all_signals[level1], all_signals[level2]
                    )
            
            multi_level_data["comparison"]["signal_confirmation"] = signal_confirmation
            
        except Exception as e:
            logger.warning(f"分析信号确认失败: {e}")
    
    def _calculate_signal_similarity(self, signals1: List[Dict], signals2: List[Dict]) -> float:
        """计算两个级别信号的相似度"""
        if not signals1 or not signals2:
            return 0.0
        
        # 简化的相似度计算：基于信号类型和时间接近度
        similarity_score = 0.0
        matches = 0
        
        for sig1 in signals1:
            for sig2 in signals2:
                # 类型匹配
                if sig1["type"] == sig2["type"]:
                    # 时间接近（7天内）
                    time_diff = abs((sig1["timestamp"] - sig2["timestamp"]).total_seconds())
                    if time_diff < 7 * 24 * 3600:  # 7天
                        similarity_score += min(sig1["reliability"], sig2["reliability"])
                        matches += 1
        
        return similarity_score / max(matches, 1)
    
    def _convert_signals_to_frontend(self, signals: Dict[str, Any]) -> Dict[str, Any]:
        """转换交易信号为前端格式"""
        
        frontend_signals = {
            "signals": [],
            "summary": signals.get("summary", {}),
            "timestamp": signals.get("timestamp", datetime.now()).isoformat() if hasattr(signals.get("timestamp"), 'isoformat') else str(signals.get("timestamp", datetime.now()))
        }
        
        for signal in signals.get("signals", []):
            try:
                frontend_signal = {
                    "type": signal.get("type"),
                    "point_type": signal.get("point_type", signal.get("type")),
                    "price": signal.get("price"),
                    "timestamp": signal.get("timestamp").isoformat() if hasattr(signal.get("timestamp"), 'isoformat') else str(signal.get("timestamp")),
                    "reliability": signal.get("reliability"),
                    "strength": signal.get("strength", 0.0),
                    "confirmed": signal.get("confirmed", False)
                }
                
                # 处理背驰信号的特殊字段
                if signal.get("type") == "backchi":
                    frontend_signal.update({
                        "backchi_type": signal.get("backchi_type"),
                        "strength_ratio": signal.get("strength_ratio")
                    })
                
                frontend_signals["signals"].append(frontend_signal)
                
            except Exception as e:
                logger.warning(f"转换信号数据失败: {e}")
                continue
        
        return frontend_signals
    
    def _get_time_level(self, timeframe: str) -> TimeLevel:
        """获取时间级别枚举"""
        mapping = {
            "5min": TimeLevel.MIN_5,
            "30min": TimeLevel.MIN_30,
            "daily": TimeLevel.DAILY
        }
        return mapping.get(timeframe, TimeLevel.DAILY)
    
    def _generate_empty_result(self, symbol: str, timeframe: str) -> Dict[str, Any]:
        """生成空的分析结果"""
        return {
            "meta": {
                "symbol": symbol,
                "timeframe": timeframe,
                "analysis_level": "complete",
                "analysis_time": datetime.now().isoformat(),
                "data_range": {"days": 0, "start_date": "", "end_date": ""},
                "data_count": 0
            },
            "chart_data": {
                "kline": {"categories": [], "values": [], "volumes": []},
                "indicators": {"macd": {"dif": [], "dea": [], "macd": []}},
                "chan_structures": {"fenxing": [], "bi": [], "seg": [], "zhongshu": []},
                "dynamics": {"buy_sell_points": [], "backchi": []}
            },
            "analysis": {
                "summary": {
                    "klines_original": 0, "klines_processed": 0,
                    "fenxing_count": 0, "bi_count": 0, "seg_count": 0, "zhongshu_count": 0,
                    "backchi_count": 0, "buy_sell_points_count": 0
                },
                "evaluation": {
                    "trend_direction": None, "trend_strength": 0.0,
                    "risk_level": 0.0, "confidence_score": 0.0,
                    "recommended_action": "wait"
                },
                "latest_signals": []
            },
            "chart_config": {
                "colors": {
                    "up_candle": "#ef5150", "down_candle": "#26a69a",
                    "fenxing_top": "#f44336", "fenxing_bottom": "#4caf50",
                    "bi_up": "#e91e63", "bi_down": "#2196f3",
                    "seg_up": "#ff5722", "seg_down": "#3f51b5",
                    "zhongshu": "#ff9800", "buy_point": "#4caf50", "sell_point": "#f44336"
                }
            }
        }
    
    def _generate_empty_multi_level_result(self, symbol: str, levels: List[str]) -> Dict[str, Any]:
        """生成空的多级别分析结果"""
        return {
            "meta": {
                "symbol": symbol,
                "levels": levels,
                "analysis_time": datetime.now().isoformat(),
                "days": 0
            },
            "results": {},
            "comparison": {
                "level_consistency": {},
                "signal_confirmation": {},
                "trend_alignment": {}
            }
        }
    
    def save_analysis_to_json(self, symbol: str, timeframe: str = "daily", 
                            days: int = 90, analysis_level: str = "complete",
                            output_file: str = None) -> str:
        """分析股票并保存为JSON文件"""
        # 执行分析
        data = self.analyze_symbol_complete(symbol, timeframe, days, analysis_level)
        
        # 生成文件名
        if not output_file:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = f"chan_v2_data_{symbol}_{timeframe}_{analysis_level}_{timestamp}.json"
        
        # 保存到文件
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2, default=str)
            
            logger.info(f"✅ 缠论v2分析数据已保存到: {output_file}")
            return output_file
            
        except Exception as e:
            logger.error(f"❌ 保存文件失败: {e}")
            return ""


# 创建全局API实例
chan_api_v2 = ChanDataAPIv2()

if __name__ == '__main__':
    # 命令行使用示例
    import argparse
    
    parser = argparse.ArgumentParser(description='缠论数据API v2')
    parser.add_argument('--symbol', '-s', required=True, help='股票代码')
    parser.add_argument('--timeframe', '-t', default='daily', choices=['5min', '30min', 'daily'], help='时间级别')
    parser.add_argument('--days', '-d', type=int, default=90, help='分析天数')
    parser.add_argument('--level', '-l', default='complete', choices=['basic', 'standard', 'advanced', 'complete'], help='分析级别')
    parser.add_argument('--output', '-o', help='输出文件名')
    parser.add_argument('--multi-level', '-m', action='store_true', help='多级别分析')
    
    args = parser.parse_args()
    
    print(f"🔍 缠论v2分析 {args.symbol} ({args.timeframe}, {args.days}天, {args.level}级别)")
    
    if args.multi_level:
        # 多级别分析
        data = chan_api_v2.analyze_multi_level(args.symbol, ["daily", "30min", "5min"], args.days)
        output_file = args.output or f"chan_v2_multi_level_{args.symbol}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2, default=str)
            
        print(f"🎉 多级别分析完成！数据已保存到: {output_file}")
    else:
        # 单级别分析
        output_file = chan_api_v2.save_analysis_to_json(
            args.symbol, args.timeframe, args.days, args.level, args.output
        )
        
        if output_file:
            print(f"🎉 分析完成！数据已保存到: {output_file}")
            print(f"📊 基于最新缠论v2引擎（形态学+动力学）的完整分析")
        else:
            print("❌ 分析失败")