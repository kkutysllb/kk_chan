#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强型数据管理器
基于技术方案文档的数据访问层优化实现
"""

import asyncio
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import logging
from dataclasses import dataclass
import redis
import pickle
import hashlib
import json
from concurrent.futures import ThreadPoolExecutor
import sys
import os

# 添加项目路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
sys.path.append(project_root)

from database.db_handler import DBHandler
from chan_theory.models.chan_theory_models import TrendLevel

logger = logging.getLogger(__name__)


@dataclass
class CacheConfig:
    """缓存配置"""
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    default_ttl: int = 3600  # 1小时
    analysis_result_ttl: int = 7200  # 2小时
    kline_data_ttl: int = 1800  # 30分钟


class CacheManager:
    """缓存管理器"""
    
    def __init__(self, config: CacheConfig = None):
        self.config = config or CacheConfig()
        self.redis_client = None
        self._init_redis()
    
    def _init_redis(self):
        """初始化Redis连接"""
        try:
            self.redis_client = redis.Redis(
                host=self.config.redis_host,
                port=self.config.redis_port,
                db=self.config.redis_db,
                decode_responses=False  # 保持二进制模式以支持pickle
            )
            # 测试连接
            self.redis_client.ping()
            logger.info("✅ Redis缓存连接成功")
        except Exception as e:
            logger.warning(f"⚠️ Redis连接失败，将使用内存缓存: {e}")
            self.redis_client = None
    
    def _generate_cache_key(self, prefix: str, **kwargs) -> str:
        """生成缓存键"""
        key_parts = [prefix]
        for k, v in sorted(kwargs.items()):
            if isinstance(v, datetime):
                v = v.strftime('%Y%m%d')
            key_parts.append(f"{k}:{v}")
        
        key_string = ":".join(key_parts)
        # 使用MD5哈希避免键过长
        key_hash = hashlib.md5(key_string.encode()).hexdigest()
        return f"chan:{prefix}:{key_hash}"
    
    async def get(self, key: str) -> Optional[Any]:
        """获取缓存数据"""
        if not self.redis_client:
            return None
        
        try:
            data = self.redis_client.get(key)
            if data:
                return pickle.loads(data)
        except Exception as e:
            logger.warning(f"缓存读取失败: {e}")
        
        return None
    
    async def set(self, key: str, value: Any, ttl: int = None) -> bool:
        """设置缓存数据"""
        if not self.redis_client:
            return False
        
        try:
            ttl = ttl or self.config.default_ttl
            serialized_data = pickle.dumps(value)
            self.redis_client.setex(key, ttl, serialized_data)
            return True
        except Exception as e:
            logger.warning(f"缓存写入失败: {e}")
            return False
    
    async def delete(self, pattern: str = None) -> int:
        """删除缓存数据"""
        if not self.redis_client:
            return 0
        
        try:
            if pattern:
                keys = self.redis_client.keys(pattern)
                if keys:
                    return self.redis_client.delete(*keys)
            return 0
        except Exception as e:
            logger.warning(f"缓存删除失败: {e}")
            return 0


class LocalDataFetcher:
    """本地数据获取器"""
    
    def __init__(self, db_handler: DBHandler):
        self.db_handler = db_handler
        self.executor = ThreadPoolExecutor(max_workers=4)
    
    async def fetch_kline_data(self, symbol: str, period: str, 
                              start_date: datetime, end_date: datetime) -> pd.DataFrame:
        """获取K线数据"""
        try:
            # 根据周期选择合适的集合
            collection_map = {
                '1min': 'stock_1min_qfq',
                '5min': 'stock_5min_qfq', 
                '30min': 'stock_30min_qfq',
                'daily': 'stock_daily_qfq'
            }
            
            collection_name = collection_map.get(period, 'stock_daily_qfq')
            
            # 构建查询条件
            query = {
                'ts_code': symbol,
                'trade_date': {
                    '$gte': start_date,
                    '$lte': end_date
                }
            }
            
            # 异步执行数据库查询
            loop = asyncio.get_event_loop()
            data = await loop.run_in_executor(
                self.executor,
                self._fetch_from_db,
                collection_name, query
            )
            
            if data:
                df = pd.DataFrame(data)
                df = self._process_kline_data(df)
                logger.info(f"📊 获取{symbol} {period}数据: {len(df)}条")
                return df
            else:
                logger.warning(f"⚠️ 未找到{symbol} {period}数据")
                return pd.DataFrame()
                
        except Exception as e:
            logger.error(f"❌ 获取K线数据失败: {e}")
            return pd.DataFrame()
    
    def _fetch_from_db(self, collection_name: str, query: Dict) -> List[Dict]:
        """从数据库获取数据"""
        try:
            collection = self.db_handler.get_collection(collection_name)
            cursor = collection.find(query).sort('trade_date', 1)
            return list(cursor)
        except Exception as e:
            logger.error(f"数据库查询失败: {e}")
            return []
    
    def _process_kline_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """处理K线数据"""
        if df.empty:
            return df
        
        # 标准化列名
        column_mapping = {
            'trade_date': 'timestamp',
            'open_qfq': 'open',
            'high_qfq': 'high', 
            'low_qfq': 'low',
            'close_qfq': 'close',
            'vol': 'volume'
        }
        
        # 重命名列
        for old_col, new_col in column_mapping.items():
            if old_col in df.columns:
                df = df.rename(columns={old_col: new_col})
        
        # 确保必要的列存在
        required_cols = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            logger.warning(f"缺少必要列: {missing_cols}")
            return pd.DataFrame()
        
        # 数据类型转换
        numeric_cols = ['open', 'high', 'low', 'close', 'volume']
        for col in numeric_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # 处理时间戳
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df.set_index('timestamp', inplace=True)
        
        # 删除无效数据
        df = df.dropna(subset=['open', 'high', 'low', 'close'])
        
        # 数据验证
        df = df[(df['high'] >= df['low']) & 
                (df['high'] >= df['open']) & 
                (df['high'] >= df['close']) &
                (df['low'] <= df['open']) & 
                (df['low'] <= df['close'])]
        
        return df.sort_index()
    
    async def fetch_financial_data(self, symbol: str) -> Dict:
        """获取财务数据"""
        try:
            query = {'ts_code': symbol}
            
            # 获取基本信息
            basic_info = await asyncio.get_event_loop().run_in_executor(
                self.executor,
                self._fetch_from_db,
                'stock_basic', query
            )
            
            # 获取财务指标
            financial_data = await asyncio.get_event_loop().run_in_executor(
                self.executor,
                self._fetch_from_db,
                'fina_indicator', query
            )
            
            return {
                'basic_info': basic_info[0] if basic_info else {},
                'financial_indicators': financial_data
            }
            
        except Exception as e:
            logger.error(f"获取财务数据失败: {e}")
            return {}
    
    async def fetch_technical_indicators(self, symbol: str, period: str,
                                       start_date: datetime, end_date: datetime) -> Dict:
        """获取技术指标数据"""
        try:
            # 根据周期选择技术指标集合
            indicator_collections = {
                'daily': ['stock_daily_qfq'],  # 日线技术指标已包含在K线数据中
                '30min': ['stock_30min_qfq'],
                '5min': ['stock_5min_qfq']
            }
            
            collections = indicator_collections.get(period, ['stock_daily_qfq'])
            indicators = {}
            
            for collection_name in collections:
                query = {
                    'ts_code': symbol,
                    'trade_date': {
                        '$gte': start_date,
                        '$lte': end_date
                    }
                }
                
                data = await asyncio.get_event_loop().run_in_executor(
                    self.executor,
                    self._fetch_from_db,
                    collection_name, query
                )
                
                if data:
                    df = pd.DataFrame(data)
                    # 提取技术指标列
                    indicator_cols = [col for col in df.columns 
                                    if any(indicator in col.lower() 
                                          for indicator in ['ma', 'ema', 'boll', 'macd', 'rsi', 'kdj'])]
                    
                    if indicator_cols:
                        indicators[collection_name] = df[['trade_date'] + indicator_cols]
            
            return indicators
            
        except Exception as e:
            logger.error(f"获取技术指标失败: {e}")
            return {}


class EnhancedDataManager:
    """增强型数据管理器"""
    
    def __init__(self, cache_config: CacheConfig = None):
        self.db_handler = DBHandler(local_priority=True)
        self.cache_manager = CacheManager(cache_config)
        self.data_fetcher = LocalDataFetcher(self.db_handler)
        
        logger.info("🚀 增强型数据管理器初始化完成")
    
    async def get_kline_data(self, symbol: str, period: str, 
                           start_date: datetime, end_date: datetime) -> pd.DataFrame:
        """获取K线数据 - 优先本地数据库，支持缓存"""
        
        # 生成缓存键
        cache_key = self.cache_manager._generate_cache_key(
            "kline",
            symbol=symbol,
            period=period,
            start_date=start_date,
            end_date=end_date
        )
        
        # 尝试从缓存获取
        cached_data = await self.cache_manager.get(cache_key)
        if cached_data is not None:
            logger.info(f"📋 从缓存获取{symbol} {period}数据")
            return cached_data
        
        # 从数据库获取
        df = await self.data_fetcher.fetch_kline_data(symbol, period, start_date, end_date)
        
        # 缓存结果
        if not df.empty:
            await self.cache_manager.set(
                cache_key, df, 
                ttl=self.cache_manager.config.kline_data_ttl
            )
        
        return df
    
    async def get_financial_data(self, symbol: str) -> Dict:
        """获取财务数据"""
        cache_key = self.cache_manager._generate_cache_key("financial", symbol=symbol)
        
        # 尝试从缓存获取
        cached_data = await self.cache_manager.get(cache_key)
        if cached_data is not None:
            return cached_data
        
        # 从数据库获取
        data = await self.data_fetcher.fetch_financial_data(symbol)
        
        # 缓存结果
        if data:
            await self.cache_manager.set(cache_key, data, ttl=86400)  # 24小时缓存
        
        return data
    
    async def get_technical_indicators(self, symbol: str, period: str,
                                     start_date: datetime, end_date: datetime) -> Dict:
        """获取技术指标数据"""
        cache_key = self.cache_manager._generate_cache_key(
            "indicators",
            symbol=symbol,
            period=period,
            start_date=start_date,
            end_date=end_date
        )
        
        # 尝试从缓存获取
        cached_data = await self.cache_manager.get(cache_key)
        if cached_data is not None:
            return cached_data
        
        # 从数据库获取
        data = await self.data_fetcher.fetch_technical_indicators(symbol, period, start_date, end_date)
        
        # 缓存结果
        if data:
            await self.cache_manager.set(cache_key, data, ttl=3600)  # 1小时缓存
        
        return data
    
    async def cache_analysis_result(self, symbol: str, timeframe: str, 
                                  analysis_date: datetime, result: Dict) -> bool:
        """缓存分析结果"""
        cache_key = self.cache_manager._generate_cache_key(
            "analysis",
            symbol=symbol,
            timeframe=timeframe,
            date=analysis_date
        )
        
        return await self.cache_manager.set(
            cache_key, result,
            ttl=self.cache_manager.config.analysis_result_ttl
        )
    
    async def get_cached_analysis_result(self, symbol: str, timeframe: str,
                                       analysis_date: datetime) -> Optional[Dict]:
        """获取缓存的分析结果"""
        cache_key = self.cache_manager._generate_cache_key(
            "analysis",
            symbol=symbol,
            timeframe=timeframe,
            date=analysis_date
        )
        
        return await self.cache_manager.get(cache_key)
    
    async def batch_get_kline_data(self, requests: List[Dict]) -> Dict[str, pd.DataFrame]:
        """批量获取K线数据"""
        results = {}
        
        # 创建异步任务
        tasks = []
        for req in requests:
            task = self.get_kline_data(
                req['symbol'], req['period'],
                req['start_date'], req['end_date']
            )
            tasks.append((req['symbol'], req['period'], task))
        
        # 并行执行
        for symbol, period, task in tasks:
            try:
                df = await task
                key = f"{symbol}_{period}"
                results[key] = df
            except Exception as e:
                logger.error(f"批量获取{symbol} {period}数据失败: {e}")
                results[f"{symbol}_{period}"] = pd.DataFrame()
        
        return results
    
    async def clear_cache(self, pattern: str = None) -> int:
        """清理缓存"""
        if pattern:
            cache_pattern = f"chan:{pattern}:*"
        else:
            cache_pattern = "chan:*"
        
        deleted_count = await self.cache_manager.delete(cache_pattern)
        logger.info(f"🗑️ 清理缓存: {deleted_count}个键")
        return deleted_count
    
    async def get_cache_stats(self) -> Dict:
        """获取缓存统计信息"""
        if not self.cache_manager.redis_client:
            return {"status": "Redis未连接"}
        
        try:
            info = self.cache_manager.redis_client.info()
            return {
                "connected_clients": info.get("connected_clients", 0),
                "used_memory_human": info.get("used_memory_human", "0B"),
                "keyspace_hits": info.get("keyspace_hits", 0),
                "keyspace_misses": info.get("keyspace_misses", 0),
                "hit_rate": info.get("keyspace_hits", 0) / 
                          max(info.get("keyspace_hits", 0) + info.get("keyspace_misses", 0), 1)
            }
        except Exception as e:
            logger.error(f"获取缓存统计失败: {e}")
            return {"error": str(e)}
    
    def __del__(self):
        """清理资源"""
        if hasattr(self.data_fetcher, 'executor'):
            self.data_fetcher.executor.shutdown(wait=False)