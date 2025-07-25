#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
缓存管理
"""

import redis.asyncio as redis
import json
import logging
from typing import Optional, Any

logger = logging.getLogger(__name__)

# 全局Redis连接
redis_client: Optional[redis.Redis] = None

async def init_cache():
    """初始化缓存连接"""
    global redis_client
    
    try:
        # 连接Redis
        redis_client = redis.from_url("redis://localhost:6379/0")
        
        # 测试连接
        await redis_client.ping()
        logger.info("✅ Redis连接成功")
        
    except Exception as e:
        logger.error(f"❌ Redis连接失败: {str(e)}")
        # 使用内存缓存模拟
        redis_client = None

async def get_cache():
    """获取缓存客户端"""
    return redis_client

async def close_cache():
    """关闭缓存连接"""
    global redis_client
    if redis_client:
        await redis_client.close()
        logger.info("✅ Redis连接已关闭")