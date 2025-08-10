from pymongo import MongoClient, UpdateOne
from pymongo.errors import BulkWriteError, ServerSelectionTimeoutError, ConnectionFailure, NetworkTimeout
import os
from dotenv import load_dotenv
import pandas as pd
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
import pymongo
from pymongo import timeout
import logging
import time
from functools import wraps

load_dotenv()

# 数据库配置
LOCAL_MONGO_URI = "mongodb://root:example@127.0.0.1:27017/quant_analysis?authSource=admin"
DB_NAME = os.getenv("DB_NAME", "quant_analysis")

def retry_on_connection_error(max_retries=3, delay=2):
    """重试装饰器，用于处理数据库连接错误"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except (ConnectionFailure, NetworkTimeout, ServerSelectionTimeoutError, Exception) as e:
                    if attempt == max_retries - 1:
                        raise e
                    logging.warning(f"连接失败 (尝试 {attempt + 1}/{max_retries}): {e}")
                    time.sleep(delay * (attempt + 1))  # 指数退避
            return None
        return wrapper
    return decorator

class DBHandler:
    """本地MongoDB数据库处理器"""
    
    def __init__(self):
        """
        初始化本地数据库连接
        """
        self.logger = self._setup_logger()
        
        # 初始化连接状态
        self.client = None
        self.db = None
        self.local_available = False
        
        # 建立数据库连接
        self._connect_database()
        
    def _setup_logger(self):
        """设置日志记录器"""
        logger = logging.getLogger('DBHandler')
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def _connect_database(self):
        """建立本地数据库连接"""
        try:
            self.logger.info("🏠 连接本地数据库...")
            self.client = MongoClient(
                LOCAL_MONGO_URI,
                serverSelectionTimeoutMS=30000,  # 30秒
                connectTimeoutMS=30000,           # 30秒
                socketTimeoutMS=120000,           # 2分钟
                maxPoolSize=50,                   # 连接池大小
                minPoolSize=10,                   # 最小连接池
                maxIdleTimeMS=60000,              # 空闲超时
                retryWrites=True,
                w=1,
                heartbeatFrequencyMS=30000        # 心跳频率
            )
            # 测试连接
            self.client.admin.command('ismaster')
            self.db = self.client[DB_NAME]
            self.local_available = True
            
            local_info = self.client.server_info()
            print("✅ 本地MongoDB连接成功")
            print(f"📍 本地地址: 127.0.0.1:27017")
            print(f"🔧 本地版本: {local_info['version']}")
            
        except Exception as e:
            print(f"❌ 本地数据库连接失败: {e}")
            print("💡 请确保本地MongoDB容器正在运行:")
            print("   cd database && docker-compose -f docker-compose.single.yml up -d")
            self.local_available = False
            raise Exception("无法连接到本地数据库，请检查本地MongoDB服务")

    def get_collection(self, collection_name):
        """获取本地数据库集合"""
        if self.local_available:
            return self.db[collection_name]
        else:
            raise Exception("本地数据库不可用")
    
    def get_local_collection(self, collection_name):
        """获取本地数据库集合（与 get_collection 相同，保留以兼容）"""
        return self.get_collection(collection_name)

    def find_data(self, collection_name: str, query: Dict, sort: List[tuple] = None, limit: int = None) -> List[Dict]:
        """查询数据库数据
        
        Args:
            collection_name: 集合名称
            query: 查询条件
            sort: 排序条件，格式为[('field', 1/-1)]，1为升序，-1为降序
            limit: 限制返回数量
            
        Returns:
            List[Dict]: 查询结果列表
        """
        try:
            collection = self.get_collection(collection_name)
            cursor = collection.find(query)
            
            # 应用排序
            if sort:
                cursor = cursor.sort(sort)
            
            # 应用限制
            if limit:
                cursor = cursor.limit(limit)
                
            return list(cursor)
        except Exception as e:
            logging.error(f"查询数据失败: {e}")
            return []


    
    def _write_to_local(self, collection_name, updates, batch_size):
        """写入本地数据库的内部方法"""
        if not self.local_available:
            return False, 0, 0
        
        try:
            print(f"🏠 写入本地数据库: {collection_name}")
            collection = self.db[collection_name]
            
            total_upserted = 0
            total_modified = 0
            batch_count = 0
            total_batches = (len(updates) + batch_size - 1) // batch_size
            
            for i in range(0, len(updates), batch_size):
                batch = updates[i:i + batch_size]
                batch_count += 1
                
                try:
                    result = collection.bulk_write(batch, ordered=False)
                    total_upserted += result.upserted_count
                    total_modified += result.modified_count
                    
                    # 显示进度
                    if batch_count % 10 == 0 or batch_count == total_batches:
                        print(f"   📝 进度: {batch_count}/{total_batches} 批次")
                        
                except BulkWriteError as bwe:
                    total_upserted += bwe.details.get('nUpserted', 0)
                    total_modified += bwe.details.get('nModified', 0)
                    error_count = len(bwe.details.get('writeErrors', []))
                    if error_count > 0:
                        logging.warning(f"批次 {batch_count} 部分失败: {error_count} 个错误")
            
            print(f"✅ 本地写入成功: 新增{total_upserted} 更新{total_modified}")
            return True, total_upserted, total_modified
            
        except Exception as e:
            logging.error(f"本地写入失败: {e}")
            return False, 0, 0
    
    def _get_optimal_batch_size(self, data_size, collection_name):
        """根据数据量和集合类型动态调整批次大小"""
        # 基础批次大小
        if data_size > 100000:  # 超过10万条记录
            base_size = 200
        elif data_size > 10000:  # 超过1万条记录
            base_size = 500
        else:
            base_size = 1000
        
        # 根据集合类型调整
        if 'daily' in collection_name.lower():
            return min(base_size, 800)  # 日线数据通常较大
        elif 'basic' in collection_name.lower():
            return min(base_size, 1500)  # 基础信息数据较小
        else:
            return base_size

    def bulk_upsert(self, collection_name, data, unique_keys):
        """批量更新插入数据到本地数据库"""
        if not data:
            print(f"没有数据需要插入或更新到集合 {collection_name}")
            return

        # 准备批量操作
        updates = []
        for item in data:
            filter_query = {key: item[key] for key in unique_keys if key in item}
            updates.append(UpdateOne(filter_query, {'$set': item}, upsert=True))

        # 动态调整批次大小
        batch_size = self._get_optimal_batch_size(len(data), collection_name)
        print(f"📊 数据量: {len(data):,} 条，批次大小: {batch_size}")
        
        # 写入本地数据库
        if not self.local_available:
            logging.error("❌ 本地数据库不可用，无法进行数据采集")
            raise Exception("本地数据库不可用，请检查本地MongoDB服务")

        try:
            success, upserted, modified = self._write_to_local(collection_name, updates, batch_size)
            if success:
                print(f"🎯 数据库写入完成: {collection_name}")
            else:
                logging.error(f"❌ 数据库写入失败: {collection_name}")
                raise Exception("数据库写入失败")
        except Exception as e:
            logging.error(f"❌ 数据库写入失败: {e}")
            raise e

    def __del__(self):
        """安全关闭MongoDB连接"""
        try:
            if hasattr(self, 'client') and self.client is not None:
                self.client.close()
        except (ImportError, AttributeError, TypeError):
            # Python关闭时模块可能已被清理，忽略这些错误
            pass

    def get_kline_data(self, stock_code: str, days: int) -> Optional[pd.DataFrame]:
        """
        获取指定股票的K线数据
        
        Args:
            stock_code (str): 股票代码
            days (int): 获取最近的天数

        Returns:
            Optional[pd.DataFrame]: 包含K线数据的DataFrame，如果无数据则返回None
        """
        try:
            collection = self.db.get_collection('stock_kline_daily')
            
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            query = {
                'ts_code': stock_code,
                'trade_date': {
                    '$gte': start_date,
                    '$lte': end_date
                }
            }
            
            cursor = collection.find(query).sort('trade_date', pymongo.ASCENDING)
            data = list(cursor)
            
            if not data:
                return None
            
            df = pd.DataFrame(data)
            # 确保关键列存在
            required_cols = ['trade_date', 'open', 'high', 'low', 'close', 'vol']
            if not all(col in df.columns for col in required_cols):
                print("❌ K线数据缺少关键列")
                return None

            # 类型转换
            for col in ['open', 'high', 'low', 'close', 'vol']:
                df[col] = pd.to_numeric(df[col])

            return df

        except Exception as e:
            print(f"❌ 从数据库获取K线数据失败: {e}")
            return None

    def get_latest_date_for_code(self, collection_name: str, ts_code: str) -> Optional[datetime]:
        """获取指定代码在指定集合中的最新交易日期"""
        try:
            collection = self.db.get_collection(collection_name)
            latest_record = collection.find_one(
                {'ts_code': ts_code},
                sort=[('trade_date', -1)]
            )
            if latest_record and 'trade_date' in latest_record:
                # 确保返回的是datetime对象
                trade_date = latest_record['trade_date']
                if isinstance(trade_date, str):
                    return datetime.strptime(trade_date, '%Y%m%d')
                return trade_date
            return None
        except Exception as e:
            logging.error(f"在 {collection_name} 中查询 {ts_code} 的最新日期失败: {e}")
            return None

    def get_all_stock_codes(self) -> List[str]:
        """从数据库获取所有股票代码"""
        try:
            # Implementation of get_all_stock_codes method
            # This method needs to be implemented based on your specific requirements
            # For now, it's left empty as the implementation is not provided in the original file or the new code block
            return []
        except Exception as e:
            logging.error(f"从数据库获取所有股票代码失败: {e}")
            return []

# 延迟初始化，避免导入时就创建连接
_db_handler = None

def get_db_handler():
    """获取数据库处理器单例"""
    global _db_handler
    if _db_handler is None:
        _db_handler = DBHandler()
    return _db_handler

def reset_db_handler():
    """重置数据库处理器单例，强制重新初始化"""
    global _db_handler
    if _db_handler is not None:
        try:
            _db_handler.__del__()  # 关闭现有连接
        except:
            pass
    _db_handler = None
    print("🔄 数据库处理器已重置")

def check_database_connection():
    """检查数据库连接"""
    try:
        db_handler = get_db_handler()
        client = db_handler.client # 直接访问 client 属性
        client.server_info()  # 检查连接
        print("✅ 数据库连接成功")
        return True
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        return False