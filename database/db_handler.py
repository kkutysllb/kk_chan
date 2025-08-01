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
CLOUD_MONGO_URI = "mongodb://root:example@cd-1.frp.one:48714/quant_analysis?authSource=admin"
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
    """双数据库处理器，支持本地+云端同时写入"""
    
    def __init__(self, local_priority=True):
        """
        初始化双数据库连接
        
        Args:
            local_priority: 是否优先使用本地数据库（默认True）
        """
        self.local_priority = local_priority
        self.logger = self._setup_logger()
        
        # 初始化连接状态
        self.cloud_client = None
        self.local_client = None
        self.cloud_db = None
        self.local_db = None
        self.cloud_available = False
        self.local_available = False
        
        # 建立数据库连接
        self._connect_databases()
        
        # 向后兼容 - 保留原有的client和db属性，优先使用本地数据库
        self.client = self.local_client if self.local_available else self.cloud_client
        self.db = self.local_db if self.local_available else self.cloud_db
        
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
    
    def _connect_databases(self):
        """建立数据库连接 - 仅连接本地数据库，不连接云端数据库"""
        # 连接本地数据库（优先）
        try:
            self.logger.info("🏠 连接本地数据库...")
            self.local_client = MongoClient(
                LOCAL_MONGO_URI,
                serverSelectionTimeoutMS=30000,  # 保持30秒
                connectTimeoutMS=30000,           # 保持30秒
                socketTimeoutMS=120000,           # 增加到2分钟
                maxPoolSize=50,                   # 增加连接池大小
                minPoolSize=10,                   # 设置最小连接池
                maxIdleTimeMS=60000,              # 增加空闲超时
                retryWrites=True,
                w=1,
                heartbeatFrequencyMS=30000        # 减少心跳频率
            )
            # 测试连接
            self.local_client.admin.command('ismaster')
            self.local_db = self.local_client[DB_NAME]
            self.local_available = True
            
            local_info = self.local_client.server_info()
            print("✅ 本地MongoDB连接成功")
            print(f"📍 本地地址: 127.0.0.1:27017")
            print(f"🔧 本地版本: {local_info['version']}")
            
        except Exception as e:
            print(f"❌ 本地数据库连接失败: {e}")
            print("💡 请确保本地MongoDB容器正在运行:")
            print("   cd database && docker-compose -f docker-compose.single.yml up -d")
            self.local_available = False
        
        # 跳过云端数据库连接（仅用于API接口分析）
        print("💡 API接口分析模式：跳过云端数据库连接，仅使用本地数据库")
        self.cloud_available = False
        self.cloud_client = None
        self.cloud_db = None
        
        # 连接状态总结
        if self.local_available:
            print("🎯 本地数据库连接成功，数据将仅写入本地数据库")
            print("💡 云端数据库连接已跳过，如需备份请稍后手动同步")
        else:
            print("❌ 本地数据库连接失败")
            raise Exception("无法连接到本地数据库，请检查本地MongoDB服务")

    def get_collection(self, collection_name):
        """获取集合，优先返回本地数据库集合"""
        if self.local_available:
            return self.local_db[collection_name]
        elif self.cloud_available:
            return self.cloud_db[collection_name]
        else:
            raise Exception("没有可用的数据库连接")
    
    def get_cloud_collection(self, collection_name):
        """获取云端数据库集合"""
        if self.cloud_available:
            return self.cloud_db[collection_name]
        return None
    
    def get_local_collection(self, collection_name):
        """获取本地数据库集合"""
        if self.local_available:
            return self.local_db[collection_name]
        return None

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

    def _check_cloud_connection(self):
        """快速检查云端连接状态，避免长时间等待 - API接口分析模式下禁用"""
        return False
    
    def _reconnect_cloud(self):
        """重新连接云端数据库 - API接口分析模式下禁用"""
        print("💡 API接口分析模式：跳过云端数据库重连")
        self.cloud_available = False
        return False

    def _write_to_cloud_with_retry(self, collection_name, updates, batch_size):
        """写入云端数据库的内部方法，带智能重试机制 - API接口分析模式下禁用"""
        print("💡 API接口分析模式：跳过云端数据库写入")
        return False, 0, 0

    @retry_on_connection_error(max_retries=3, delay=2)
    def _write_to_cloud(self, collection_name, updates, batch_size):
        """写入云端数据库的内部方法（保持向后兼容）"""
        return self._write_to_cloud_with_retry(collection_name, updates, batch_size)
    
    def _write_to_local(self, collection_name, updates, batch_size):
        """写入本地数据库的内部方法"""
        if not self.local_available:
            return False, 0, 0
        
        try:
            print(f"🏠 写入本地数据库: {collection_name}")
            local_collection = self.local_db[collection_name]
            
            total_upserted = 0
            total_modified = 0
            batch_count = 0
            total_batches = (len(updates) + batch_size - 1) // batch_size
            
            for i in range(0, len(updates), batch_size):
                batch = updates[i:i + batch_size]
                batch_count += 1
                
                try:
                    result = local_collection.bulk_write(batch, ordered=False)
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
        """批量更新插入数据到本地数据库（云端数据库作为备份）"""
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
        
        local_success = False

        # 只写入本地数据库
        if self.local_available:
            try:
                local_success, local_upserted, local_modified = self._write_to_local(collection_name, updates, batch_size)
            except Exception as e:
                logging.error(f"❌ 本地数据库写入失败: {e}")
                local_success = False
        else:
            # 如果本地数据库不可用，抛出异常
            logging.error("❌ 本地数据库不可用，无法进行数据采集")
            raise Exception("本地数据库不可用，请检查本地MongoDB服务")

        # 总结
        if local_success:
            print(f"🎯 本地数据库写入完成: {collection_name}")
            if self.cloud_available:
                print("💡 云端数据库可用，可通过手动同步进行备份")
            else:
                print("⚠️  云端数据库不可用，请稍后手动同步备份")
        else:
            logging.error(f"❌ 本地数据库写入失败: {collection_name}")
            raise Exception("本地数据库写入失败")

    def manual_sync_to_cloud(self, collection_names=None, start_date=None, end_date=None):
        """
        手动同步本地数据库到云端数据库
        
        Args:
            collection_names: 要同步的集合名称列表，如果为None则同步所有集合
            start_date: 起始日期，格式为'YYYYMMDD'，用于时间序列数据的增量同步
            end_date: 结束日期，格式为'YYYYMMDD'，用于时间序列数据的增量同步
        
        Returns:
            bool: 同步是否成功
        """
        if not self.local_available:
            print("❌ 本地数据库不可用，无法进行同步")
            return False
        
        if not self.cloud_available:
            print("❌ 云端数据库不可用，无法进行同步")
            return False
        
        try:
            # 如果没有指定集合，获取所有集合
            if collection_names is None:
                collection_names = self.local_db.list_collection_names()
                print(f"📋 发现 {len(collection_names)} 个集合需要同步")
            
            sync_success_count = 0
            sync_total_count = len(collection_names)
            
            for collection_name in collection_names:
                print(f"\n🔄 开始同步集合: {collection_name}")
                
                try:
                    # 构建查询条件
                    query = {}
                    if start_date or end_date:
                        date_filter = {}
                        if start_date:
                            date_filter['$gte'] = start_date
                        if end_date:
                            date_filter['$lte'] = end_date
                        
                        # 尝试不同的日期字段名
                        date_fields = ['trade_date', 'cal_date', 'ann_date', 'pub_date']
                        for date_field in date_fields:
                            # 检查集合中是否存在该日期字段
                            sample = self.local_db[collection_name].find_one({date_field: {'$exists': True}})
                            if sample:
                                query[date_field] = date_filter
                                print(f"   📅 使用日期字段: {date_field}")
                                break
                    
                    # 从本地数据库读取数据
                    local_collection = self.local_db[collection_name]
                    cloud_collection = self.cloud_db[collection_name]
                    
                    # 获取数据总数
                    total_docs = local_collection.count_documents(query)
                    if total_docs == 0:
                        print(f"   ⚠️  集合 {collection_name} 没有符合条件的数据")
                        continue
                    
                    print(f"   📊 找到 {total_docs:,} 条数据需要同步")
                    
                    # 批量同步数据
                    batch_size = 1000
                    synced_count = 0
                    
                    cursor = local_collection.find(query)
                    batch = []
                    
                    for doc in cursor:
                        # 移除MongoDB的_id字段，让云端数据库自动生成
                        if '_id' in doc:
                            del doc['_id']
                        batch.append(doc)
                        
                        if len(batch) >= batch_size:
                            # 执行批量插入/更新
                            self._sync_batch_to_cloud(cloud_collection, batch, collection_name)
                            synced_count += len(batch)
                            batch = []
                            
                            # 显示进度
                            progress = (synced_count / total_docs) * 100
                            print(f"   📝 进度: {synced_count:,}/{total_docs:,} ({progress:.1f}%)")
                    
                    # 处理剩余的数据
                    if batch:
                        self._sync_batch_to_cloud(cloud_collection, batch, collection_name)
                        synced_count += len(batch)
                    
                    print(f"   ✅ 集合 {collection_name} 同步完成: {synced_count:,} 条数据")
                    sync_success_count += 1
                    
                except Exception as e:
                    print(f"   ❌ 集合 {collection_name} 同步失败: {e}")
                    logging.error(f"同步集合 {collection_name} 失败: {e}")
            
            # 同步总结
            print(f"\n📊 同步完成: {sync_success_count}/{sync_total_count} 个集合同步成功")
            return sync_success_count == sync_total_count
            
        except Exception as e:
            print(f"❌ 手动同步过程中出现错误: {e}")
            logging.error(f"手动同步失败: {e}")
            return False
    
    def _sync_batch_to_cloud(self, cloud_collection, batch, collection_name):
        """
        将批量数据同步到云端数据库
        
        Args:
            cloud_collection: 云端集合对象
            batch: 要同步的数据批次
            collection_name: 集合名称
        """
        try:
            # 使用insert_many进行批量插入，忽略重复数据
            cloud_collection.insert_many(batch, ordered=False)
        except BulkWriteError as bwe:
            # 处理部分插入成功的情况
            inserted_count = bwe.details.get('nInserted', 0)
            error_count = len(bwe.details.get('writeErrors', []))
            if error_count > 0:
                # 大部分错误可能是重复数据，这是正常的
                logging.debug(f"批次同步部分成功: 插入{inserted_count}条，跳过{error_count}条重复数据")
        except Exception as e:
            logging.error(f"批次同步到云端失败: {e}")
            raise e
    
    def get_sync_status(self):
        """
        获取本地和云端数据库的同步状态
        
        Returns:
            dict: 包含各集合数据量对比的字典
        """
        if not self.local_available or not self.cloud_available:
            print("❌ 本地或云端数据库不可用，无法获取同步状态")
            return {}
        
        try:
            local_collections = self.local_db.list_collection_names()
            cloud_collections = self.cloud_db.list_collection_names()
            
            status = {}
            
            print("📊 数据库同步状态对比:")
            print(f"{'集合名称':<30} {'本地数据量':<15} {'云端数据量':<15} {'状态':<10}")
            print("-" * 70)
            
            for collection_name in sorted(set(local_collections + cloud_collections)):
                local_count = 0
                cloud_count = 0
                
                if collection_name in local_collections:
                    local_count = self.local_db[collection_name].count_documents({})
                
                if collection_name in cloud_collections:
                    cloud_count = self.cloud_db[collection_name].count_documents({})
                
                # 判断同步状态
                if local_count == cloud_count:
                    sync_status = "✅ 同步"
                elif local_count > cloud_count:
                    sync_status = "⚠️  待同步"
                else:
                    sync_status = "❓ 异常"
                
                status[collection_name] = {
                    'local_count': local_count,
                    'cloud_count': cloud_count,
                    'status': sync_status
                }
                
                print(f"{collection_name:<30} {local_count:<15,} {cloud_count:<15,} {sync_status:<10}")
            
            return status
            
        except Exception as e:
            print(f"❌ 获取同步状态失败: {e}")
            logging.error(f"获取同步状态失败: {e}")
            return {}
    
    def __del__(self):
        """安全关闭MongoDB连接"""
        try:
            if hasattr(self, 'cloud_client') and self.cloud_client is not None:
                self.cloud_client.close()
            if hasattr(self, 'local_client') and self.local_client is not None:
                self.local_client.close()
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