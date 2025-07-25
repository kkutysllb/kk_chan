#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库连接管理
"""

from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# 全局数据库连接
mongo_client: Optional[AsyncIOMotorClient] = None
mongo_db = None

async def init_database():
    """初始化数据库连接"""
    global mongo_client, mongo_db
    
    try:
        # 尝试连接本地数据库
        local_uri = "mongodb://root:example@127.0.0.1:27017/quant_analysis?authSource=admin"
        mongo_client = AsyncIOMotorClient(local_uri)
        mongo_db = mongo_client.quant_analysis
        
        # 测试连接
        await mongo_client.admin.command('ismaster')
        logger.info("✅ MongoDB本地连接成功")
        
    except Exception as local_error:
        logger.warning(f"本地数据库连接失败: {str(local_error)}")
        try:
            # 尝试连接云端数据库
            cloud_uri = "mongodb://root:example@vip.cd.frp.one:48714/quant_analysis?authSource=admin"
            mongo_client = AsyncIOMotorClient(cloud_uri)
            mongo_db = mongo_client.quant_analysis
            
            # 测试连接
            await mongo_client.admin.command('ismaster')
            logger.info("✅ MongoDB云端连接成功")
        except Exception as cloud_error:
            logger.error(f"云端数据库连接失败: {str(cloud_error)}")
            mongo_client = None
            mongo_db = None
            raise Exception("所有数据库连接失败")

async def get_database():
    """获取数据库实例"""
    return mongo_db

async def close_database():
    """关闭数据库连接"""
    global mongo_client
    if mongo_client:
        mongo_client.close()
        logger.info("✅ 数据库连接已关闭")