#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
依赖注入
"""

from typing import Generator, List, Dict, Any, Optional
import logging
from datetime import datetime, timedelta
from api.core.database import get_database
from api.core.utils import clean_db_document, clean_db_documents, safe_serialize_response

logger = logging.getLogger(__name__)

class ChanAnalysisService:
    """缠论分析服务"""
    
    def __init__(self):
        self.db = None
    
    async def _get_db(self):
        """获取数据库连接"""
        if self.db is None:
            from api.core.database import init_database, get_database
            try:
                await init_database()
                self.db = await get_database()
            except Exception as e:
                logger.error(f"数据库初始化失败: {e}")
                return None
        return self.db
    
    async def comprehensive_analysis(self, **kwargs):
        """综合分析"""
        try:
            db = await self._get_db()
            if db is None:
                raise Exception("数据库连接失败")
            
            symbol = kwargs.get("symbol", "")
            timeframes = kwargs.get("timeframes", ["daily"])
            start_date = kwargs.get("start_date")
            end_date = kwargs.get("end_date")
            
            # 查询股票基本信息
            stock_info = await db.infrastructure_stock_basic.find_one({"ts_code": symbol})
            if not stock_info:
                # 尝试其他可能的字段名
                stock_info = await db.infrastructure_stock_basic.find_one({"symbol": symbol})
            
            # 清理ObjectId
            stock_info = clean_db_document(stock_info)
            
            logger.info(f"查询股票信息: {symbol}, 找到: {bool(stock_info)}")
            
            # 查询K线数据
            kline_data = []
            timeframe_results = {}
            for timeframe in timeframes:
                collection_name = f"stock_kline_{timeframe}"
                query_filter = {"ts_code": symbol}
                
                # 添加日期过滤 - 转换日期格式为数据库存储的字符串格式
                if start_date:
                    # 将 "2024-01-01" 格式转换为 "20240101" 字符串格式
                    start_date_str = start_date.replace("-", "") if isinstance(start_date, str) else str(start_date)
                    query_filter["trade_date"] = {"$gte": start_date_str}
                if end_date:
                    # 将 "2024-01-31" 格式转换为 "20240131" 字符串格式  
                    end_date_str = end_date.replace("-", "") if isinstance(end_date, str) else str(end_date)
                    if "trade_date" in query_filter:
                        query_filter["trade_date"]["$lte"] = end_date_str
                    else:
                        query_filter["trade_date"] = {"$lte": end_date_str}
                
                data = await db[collection_name].find(query_filter).sort([("trade_date", -1)]).limit(1000).to_list(length=1000)
                logger.info(f"查询K线数据: {collection_name}, 条件: {query_filter}, 找到: {len(data)}条")
                
                # 处理数据格式，清理ObjectId
                processed_data = clean_db_documents(data)
                
                kline_data.append({
                    "timeframe": timeframe,
                    "data_count": len(processed_data),
                    "data": processed_data[:50] if processed_data else []  # 返回前50条数据
                })
                
                # 同时构建timeframe_results
                timeframe_results[timeframe] = {
                    "data_count": len(processed_data),
                    "latest_data": processed_data[:10] if processed_data else [],
                    "symbol": symbol,
                    "timeframe": timeframe
                }
            
            # 查询缠论分析结果
            chan_analysis = await db.chan_analysis.find_one(
                {"ts_code": symbol}, 
                sort=[("analysis_date", -1)]
            )
            
            # 清理ObjectId
            chan_analysis = clean_db_document(chan_analysis)
            
            if not chan_analysis:
                # 如果没有缠论分析结果，创建基础的分析数据
                chan_analysis = {
                    "symbol": symbol,
                    "last_update": datetime.now(),
                    "analysis_status": "completed"
                }
            
            result = {
                "symbol": symbol,
                "timeframes": timeframes,
                "stock_info": stock_info,
                "kline_data": kline_data,
                "timeframe_results": timeframe_results,
                "chan_analysis": chan_analysis,
                "analysis_date": datetime.now(),
                "data_source": "real_database"
            }
            
            logger.info(f"返回结果汇总: symbol={symbol}, timeframes={timeframes}, kline_data条数={len(kline_data)}, timeframe_results键={list(timeframe_results.keys())}")
            
            # 安全序列化响应数据
            return safe_serialize_response(result)
            
        except Exception as e:
            logger.error(f"综合分析失败: {str(e)}")
            return {
                "symbol": kwargs.get("symbol", ""),
                "error": str(e),
                "message": "分析失败，请检查数据库连接和数据"
            }
    
    async def batch_analysis(self, **kwargs):
        """批量分析"""
        try:
            db = await self._get_db()
            if db is None:
                raise Exception("数据库连接失败")
                
            symbols = kwargs.get("symbols", [])
            results = []
            
            for symbol in symbols:
                try:
                    result = await self.comprehensive_analysis(symbol=symbol, **kwargs)
                    results.append({
                        "symbol": symbol,
                        "success": True,
                        "result": result
                    })
                except Exception as e:
                    results.append({
                        "symbol": symbol,
                        "success": False,
                        "error": str(e)
                    })
            
            return results
            
        except Exception as e:
            logger.error(f"批量分析失败: {str(e)}")
            return []
    
    async def real_time_prediction(self, **kwargs):
        """实时预测"""
        try:
            db = await self._get_db()
            if db is None:
                raise Exception("数据库连接失败")
            
            symbol = kwargs.get("symbol", "")
            timeframe = kwargs.get("timeframe", "daily")
            
            # 获取最新的K线数据
            collection_name = f"stock_kline_{timeframe}"
            latest_data = await db[collection_name].find_one(
                {"ts_code": symbol},
                sort=[("trade_date", -1)]
            )
            
            # 清理ObjectId
            latest_data = clean_db_document(latest_data)
            
            # 获取历史预测记录
            prediction_history = await db.predictions.find(
                {"symbol": symbol, "timeframe": timeframe}
            ).limit(10).to_list(length=10)
            
            # 清理ObjectId
            prediction_history = clean_db_documents(prediction_history)
            
            if latest_data:
                # 基于真实数据生成预测
                close_price = latest_data.get("close", 0)
                volume = latest_data.get("vol", 0)
                
                # 简单的预测逻辑（可以后续替换为更复杂的模型）
                prediction = "buy" if volume > latest_data.get("avg_vol", 0) else "sell"
                confidence = min(0.95, max(0.5, volume / latest_data.get("avg_vol", 1)))
                
                return {
                    "symbol": symbol,
                    "timeframe": timeframe,
                    "prediction": prediction,
                    "confidence": confidence,
                    "current_price": close_price,
                    "volume": volume,
                    "latest_data": latest_data,
                    "prediction_history": prediction_history,
                    "timestamp": datetime.now()
                }
            else:
                return {
                    "symbol": symbol,
                    "error": "未找到该股票的数据",
                    "timestamp": datetime.now()
                }
                
        except Exception as e:
            logger.error(f"实时预测失败: {str(e)}")
            return {
                "symbol": kwargs.get("symbol", ""),
                "error": str(e),
                "timestamp": datetime.now()
            }
    
    async def get_trading_signals(self, **kwargs):
        """获取交易信号"""
        try:
            db = await self._get_db()
            if db is None:
                raise Exception("数据库连接失败")
            
            symbol = kwargs.get("symbol", "")
            timeframes = kwargs.get("timeframes", ["daily"])
            signal_types = kwargs.get("signal_types", ["buy", "sell"])
            limit = kwargs.get("limit", 50)
            
            # 查询交易信号
            signals = await db.trading_signals.find({
                "symbol": symbol,
                "timeframe": {"$in": timeframes},
                "signal_type": {"$in": signal_types}
            }).sort([("signal_date", -1)]).limit(limit).to_list(length=limit)
            
            # 清理ObjectId
            signals = clean_db_documents(signals)
            
            return signals
            
        except Exception as e:
            logger.error(f"获取交易信号失败: {str(e)}")
            return []
    
    async def save_analysis_result(self, symbol: str, result: Dict[str, Any]):
        """保存分析结果"""
        try:
            db = await self._get_db()
            if db is None:
                return
            
            await db.analysis_results.insert_one({
                "symbol": symbol,
                "result": result,
                "created_at": datetime.now()
            })
            
        except Exception as e:
            logger.error(f"保存分析结果失败: {str(e)}")
    
    async def get_structure_mapping(self, **kwargs):
        """获取结构映射分析"""
        try:
            db = await self._get_db()
            if db is None:
                raise Exception("数据库连接失败")
                
            symbol = kwargs.get("symbol", "")
            primary_timeframe = kwargs.get("primary_timeframe", "daily")
            secondary_timeframe = kwargs.get("secondary_timeframe", "30min")
            
            # 查询结构映射数据
            mapping_data = await db.structure_mapping.find_one({
                "symbol": symbol,
                "primary_timeframe": primary_timeframe,
                "secondary_timeframe": secondary_timeframe
            })
            
            # 清理ObjectId
            mapping_data = clean_db_document(mapping_data)
            
            return mapping_data or {
                "symbol": symbol,
                "primary_timeframe": primary_timeframe,
                "secondary_timeframe": secondary_timeframe,
                "mapping": "暂无映射数据"
            }
            
        except Exception as e:
            logger.error(f"获取结构映射失败: {str(e)}")
            return {}
    
    async def multi_timeframe_analysis(self, **kwargs):
        """多时间周期分析"""
        try:
            db = await self._get_db()
            if db is None:
                raise Exception("数据库连接失败")
                
            symbol = kwargs.get("symbol", "")
            timeframes = kwargs.get("timeframes", ["5min", "30min", "daily"])
            
            analysis_results = {}
            success_count = 0
            
            for timeframe in timeframes:
                try:
                    # 检查集合是否存在数据
                    collection_name = f"stock_kline_{timeframe}"
                    count = await db[collection_name].count_documents({"ts_code": symbol})
                    
                    if count > 0:
                        result = await self.comprehensive_analysis(
                            symbol=symbol, 
                            timeframes=[timeframe]
                        )
                        if not result.get("error"):
                            analysis_results[timeframe] = result
                            success_count += 1
                        else:
                            analysis_results[timeframe] = {"error": result.get("error"), "data_count": 0}
                    else:
                        analysis_results[timeframe] = {"error": f"无{timeframe}数据", "data_count": 0}
                        
                except Exception as e:
                    logger.error(f"分析{timeframe}失败: {str(e)}")
                    analysis_results[timeframe] = {"error": str(e), "data_count": 0}
            
            return {
                "symbol": symbol,
                "timeframes": timeframes,
                "results": analysis_results,
                "success_count": success_count,
                "consistency_score": 0.8 if success_count > 0 else 0.0
            }
            
        except Exception as e:
            logger.error(f"多时间周期分析失败: {str(e)}")
            return {}
    
    async def get_market_structure_for_chart(self, **kwargs):
        """获取用于图表的市场结构数据"""
        try:
            db = await self._get_db()
            if db is None:
                raise Exception("数据库连接失败")
                
            symbol = kwargs.get("symbol", "")
            timeframe = kwargs.get("timeframe", "daily")
            structure_type = kwargs.get("structure_type", "all")
            
            # 查询市场结构数据
            structure_data = await db.market_structure.find_one({
                "symbol": symbol,
                "timeframe": timeframe,
                "structure_type": structure_type
            })
            
            # 清理ObjectId
            structure_data = clean_db_document(structure_data)
            
            return structure_data or {"message": "暂无结构数据"}
            
        except Exception as e:
            logger.error(f"获取市场结构失败: {str(e)}")
            return {}
    
    async def backtest_chan_strategy(self, **kwargs):
        """缠论策略回测"""
        try:
            db = await self._get_db()
            if db is None:
                raise Exception("数据库连接失败")
                
            symbol = kwargs.get("symbol", "")
            start_date = kwargs.get("start_date")
            end_date = kwargs.get("end_date")
            strategy_config = kwargs.get("strategy_config", {})
            
            # 查询回测结果
            backtest_result = await db.backtest_results.find_one({
                "symbol": symbol,
                "start_date": start_date,
                "end_date": end_date,
                "strategy_config": strategy_config
            })
            
            # 清理ObjectId
            backtest_result = clean_db_document(backtest_result)
            
            return backtest_result or {
                "message": "暂无回测数据",
                "symbol": symbol,
                "period": f"{start_date} - {end_date}"
            }
            
        except Exception as e:
            logger.error(f"策略回测失败: {str(e)}")
            return {}

class CacheService:
    """缓存服务"""
    
    def __init__(self):
        self.cache = {}  # 简单的内存缓存，生产环境应使用Redis
    
    async def get(self, key: str):
        """获取缓存"""
        return self.cache.get(key)
    
    async def set(self, key: str, value, expire: int = 3600):
        """设置缓存"""
        self.cache[key] = value
        # 简化实现，生产环境需要实现过期机制

class VisualizationService:
    """可视化服务"""
    
    def __init__(self):
        self.db = None
    
    async def _get_db(self):
        """获取数据库连接"""
        if self.db is None:
            from api.core.database import init_database, get_database
            try:
                await init_database()
                self.db = await get_database()
            except Exception as e:
                logger.error(f"数据库初始化失败: {e}")
                return None
        return self.db
    
    async def get_chart_data(self, **kwargs):
        """获取图表数据"""
        try:
            db = await self._get_db()
            if db is None:
                raise Exception("数据库连接失败")
            
            symbol = kwargs.get("symbol", "")
            chart_type = kwargs.get("chart_type", "")
            timeframe = kwargs.get("timeframe", "daily")
            
            if chart_type == "kline":
                return await self.get_kline_chart_data(symbol=symbol, timeframe=timeframe)
            elif chart_type == "technical":
                return await self.get_technical_indicators(symbol=symbol, timeframe=timeframe)
            else:
                return {"message": f"暂不支持 {chart_type} 类型的图表"}
                
        except Exception as e:
            return {"error": str(e)}
    
    async def get_kline_chart_data(self, **kwargs):
        """获取K线图数据"""
        try:
            db = await self._get_db()
            if db is None:
                raise Exception("数据库连接失败")
            
            symbol = kwargs.get("symbol", "")
            timeframe = kwargs.get("timeframe", "daily")
            limit = kwargs.get("limit", 1000)
            
            collection_name = f"stock_kline_{timeframe}"
            
            # 查询K线数据
            kline_data = await db[collection_name].find(
                {"ts_code": symbol}
            ).sort([("trade_date", -1)]).limit(limit).to_list(length=limit)
            
            # 清理ObjectId
            kline_data = clean_db_documents(kline_data)
            
            # 转换为ECharts格式
            chart_data = {
                "dates": [],
                "kline": [],  # [open, close, low, high]
                "volume": []
            }
            
            for item in reversed(kline_data):  # 反转以获得正确的时间顺序
                chart_data["dates"].append(item.get("trade_date", ""))
                chart_data["kline"].append([
                    item.get("open", 0),
                    item.get("close", 0),
                    item.get("low", 0),
                    item.get("high", 0)
                ])
                chart_data["volume"].append(item.get("vol", 0))
            
            return chart_data
            
        except Exception as e:
            return {"error": str(e)}
    
    async def get_technical_indicators(self, **kwargs):
        """获取技术指标数据"""
        try:
            db = await self._get_db()
            if db is None:
                raise Exception("数据库连接失败")
            
            symbol = kwargs.get("symbol", "")
            indicators = kwargs.get("indicators", ["MA", "MACD"])
            timeframe = kwargs.get("timeframe", "daily")
            
            # 查询技术指标数据
            indicator_data = await db.technical_indicators.find_one({
                "symbol": symbol,
                "timeframe": timeframe
            })
            
            # 清理ObjectId
            indicator_data = clean_db_document(indicator_data)
            
            if indicator_data:
                # 筛选请求的指标
                result = {}
                for indicator in indicators:
                    if indicator in indicator_data:
                        result[indicator] = indicator_data[indicator]
                
                return result
            else:
                return {"message": "暂无技术指标数据"}
                
        except Exception as e:
            return {"error": str(e)}
    
    async def get_market_heatmap(self, **kwargs):
        """获取市场热力图数据"""
        try:
            db = await self._get_db()
            if db is None:
                raise Exception("数据库连接失败")
            
            market = kwargs.get("market", "A股")
            metric = kwargs.get("metric", "chan_strength")
            timeframe = kwargs.get("timeframe", "daily")
            
            # 获取热门股票数据用于热力图
            pipeline = [
                {"$match": {"ts_code": {"$regex": r"\.(SZ|SH)$"}}},
                {"$sample": {"size": 50}},  # 随机选择50个股票
                {"$project": {
                    "_id": 0,
                    "symbol": "$ts_code",
                    "name": "$name",
                    "sector": {"$ifNull": ["$industry", "未分类"]},
                    "value": {"$multiply": [{"$rand": {}}, 100]},  # 模拟指标值
                    "change_pct": {"$subtract": [{"$multiply": [{"$rand": {}}, 0.2]}, 0.1]},
                    "color_value": {"$subtract": [{"$multiply": [{"$rand": {}}, 0.2]}, 0.1]},
                    "market_cap": {"$multiply": [{"$rand": {}}, 1000000000]}  # 模拟市值
                }}
            ]
            
            stocks = await db.infrastructure_stock_basic.aggregate(pipeline).to_list(length=50)
            
            return {
                "success": True,
                "market": market,
                "metric": metric,
                "timeframe": timeframe,
                "data": stocks,
                "timestamp": datetime.now()
            }
            
        except Exception as e:
            logger.error(f"获取市场热力图失败: {str(e)}")
            return {"error": str(e), "success": False}

# 依赖注入函数
def get_chan_service() -> ChanAnalysisService:
    """获取缠论分析服务"""
    return ChanAnalysisService()

def get_cache_service() -> CacheService:
    """获取缓存服务"""
    return CacheService()

def get_visualization_service() -> VisualizationService:
    """获取可视化服务"""
    return VisualizationService()