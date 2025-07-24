# -*- coding: utf-8 -*-
"""
Qlib数据适配器
连接MongoDB数据库与Qlib框架的数据接口
基于qlib的DataHandler实现自定义数据源
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any, Union
import logging
import sys
import os

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

# qlib导入
from qlib.data import BaseProvider
# from qlib.data.cache import SimpleDatasetCache
from qlib.log import get_module_logger
from qlib.utils import init_instance_by_config

# 项目导入
from api.db_handler import DBHandler

class QlibDataAdapter(BaseProvider):
    """
    Qlib框架数据适配器
    负责从MongoDB获取数据并转换为Qlib框架可用的格式
    继承自qlib.data.base.BaseProvider
    """
    
    def __init__(self, database_config: Dict[str, Any] = None):
        """
        初始化数据适配器
        
        Args:
            database_config: 数据库配置信息
        """
        super().__init__()
        
        # 初始化数据库连接
        self.db_handler = DBHandler()
        
        # 设置日志
        self.logger = get_module_logger("QlibDataAdapter")
        
        # 数据缓存 (使用MongoDB作为数据源，不需要额外缓存)
        self.cache = None
        
        # tushare字段映射
        self.field_mapping = {
            'open': 'open',
            'high': 'high', 
            'low': 'low',
            'close': 'close',
            'volume': 'vol',  # tushare中是vol
            'amount': 'amount',
            'turnover': 'turnover_rate',
            'pe_ttm': 'pe_ttm',
            'pb': 'pb',
            'ps_ttm': 'ps_ttm',
            'pcf_ttm': 'pcf_ttm',
            'market_cap': 'total_mv',  # tushare中是total_mv
            'circulating_market_cap': 'circ_mv'  # tushare中是circ_mv
        }
    
    def _convert_to_qlib_format(self, stock_code: str) -> str:
        """将tushare格式转换为qlib格式"""
        if '.' in stock_code:
            # tushare格式: 000001.SZ -> qlib格式: SZ000001
            code, market = stock_code.split('.')
            return f"{market}{code}"
        else:
            # 纯数字格式
            if stock_code.startswith('0') or stock_code.startswith('3'):
                return f"SZ{stock_code}"
            elif stock_code.startswith('6'):
                return f"SH{stock_code}"
            else:
                return stock_code
    
    def _convert_from_qlib_format(self, qlib_code: str) -> str:
        """将qlib格式转换为tushare格式"""
        if qlib_code.startswith('SZ'):
            return f"{qlib_code[2:]}.SZ"
        elif qlib_code.startswith('SH'):
            return f"{qlib_code[2:]}.SH"
        else:
            return qlib_code
    
    def _convert_to_tushare_format(self, stock_code: str) -> str:
        """将股票代码转换为tushare格式"""
        if '.' in stock_code:
            return stock_code  # 已经是tushare格式
        else:
            # 纯数字格式转换
            if stock_code.startswith('0') or stock_code.startswith('3'):
                return f"{stock_code}.SZ"
            elif stock_code.startswith('6'):
                return f"{stock_code}.SH"
            else:
                return stock_code
    
    def get_stock_data(self, 
                      symbol: str, 
                      start_date: str = None, 
                      end_date: str = None,
                      fields: List[str] = None) -> pd.DataFrame:
        """
        获取股票行情数据
        
        Args:
            symbol: 股票代码
            start_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期 (YYYY-MM-DD)
            fields: 需要的字段列表
            
        Returns:
            DataFrame: Qlib框架标准格式的股票数据
        """
        try:
            # 转换股票代码为tushare格式
            stock_code = self._convert_from_qlib_format(symbol)
            
            # 默认字段
            if fields is None:
                fields = ['open', 'high', 'low', 'close', 'volume', 'amount']
            
            # 构建查询条件
            query = {
                "ts_code": stock_code,  # tushare使用ts_code
                "trade_date": {         # tushare使用trade_date
                    "$gte": start_date.replace('-', ''),  # tushare日期格式: 20230101
                    "$lte": end_date.replace('-', '')
                }
            }
            
            # 查询数据
            collection_name = "stock_kline_daily"  # 使用实际的集合名
            cursor = self.db_handler.get_collection(collection_name).find(query).sort("trade_date", 1)
            
            # 转换为DataFrame
            data = []
            for doc in cursor:
                row = {}
                # tushare日期格式转换: 20230101 -> 2023-01-01
                date_str = str(doc['trade_date'])
                row['datetime'] = pd.to_datetime(date_str, format='%Y%m%d')
                
                # 映射字段
                for field in fields:
                    if field in self.field_mapping:
                        db_field = self.field_mapping[field]
                        row[field] = doc.get(db_field, np.nan)
                    else:
                        row[field] = doc.get(field, np.nan)
                
                data.append(row)
            
            if not data:
                self.logger.warning(f"未找到股票 {symbol} 的数据")
                return pd.DataFrame()
            
            df = pd.DataFrame(data)
            df.set_index('datetime', inplace=True)
            
            # 数据类型转换
            numeric_fields = ['open', 'high', 'low', 'close', 'volume', 'amount']
            for field in numeric_fields:
                if field in df.columns:
                    df[field] = pd.to_numeric(df[field], errors='coerce')
            
            self.logger.info(f"获取{symbol}数据{len(df)}条")
            return df
            
        except Exception as e:
            self.logger.error(f"获取股票数据失败: {e}")
            return pd.DataFrame()
    
    def get_multi_stock_data(self, symbols: List[str], start_date: str, end_date: str, 
                            fields: List[str] = None) -> pd.DataFrame:
        """获取多只股票数据"""
        all_data = []
        
        for symbol in symbols:
            # 获取单只股票数据
            stock_data = self.get_stock_data(symbol, start_date, end_date, fields)
            
            if not stock_data.empty:
                # 添加股票代码列
                stock_data['instrument'] = symbol
                stock_data.reset_index(inplace=True)
                all_data.append(stock_data)
        
        if not all_data:
            return pd.DataFrame()
        
        # 合并所有数据
        combined_data = pd.concat(all_data, ignore_index=True)
        
        # 设置多层索引
        combined_data.set_index(['instrument', 'datetime'], inplace=True)
        
        return combined_data
    
    def get_factor_data(self, 
                       symbol: str, 
                       start_date: str = None, 
                       end_date: str = None,
                       factors: List[str] = None) -> pd.DataFrame:
        """
        获取因子数据
        
        Args:
            symbol: 股票代码
            start_date: 开始日期
            end_date: 结束日期
            factors: 因子列表
            
        Returns:
            DataFrame: 因子数据
        """
        try:
            # 转换股票代码
            stock_code = self._convert_from_qlib_format(symbol)
            
            # 默认因子
            if factors is None:
                factors = ['pe_ttm', 'pb', 'ps_ttm', 'market_cap']
            
            # 构建查询条件
            query = {
                "code": stock_code,
                "date": {
                    "$gte": start_date,
                    "$lte": end_date
                }
            }
            
            # 查询数据
            collection_name = "stock_factor_pro"
            cursor = self.db_handler.get_collection(collection_name).find(query).sort("date", 1)
            
            # 转换为DataFrame
            data = []
            for doc in cursor:
                row = {}
                row['datetime'] = pd.to_datetime(doc['date'])
                
                # 映射因子字段
                for factor in factors:
                    if factor in self.field_mapping:
                        db_field = self.field_mapping[factor]
                        row[factor] = doc.get(db_field, np.nan)
                    else:
                        row[factor] = doc.get(factor, np.nan)
                
                data.append(row)
            
            if not data:
                return pd.DataFrame()
            
            df = pd.DataFrame(data)
            df.set_index('datetime', inplace=True)
            
            # 数据类型转换
            for factor in factors:
                if factor in df.columns:
                    df[factor] = pd.to_numeric(df[factor], errors='coerce')
            
            return df
            
        except Exception as e:
            self.logger.error(f"获取因子数据失败: {e}")
            return pd.DataFrame()
    
    def get_benchmark_data(self, benchmark: str, start_date: str, end_date: str) -> pd.DataFrame:
        """获取基准指数数据"""
        try:
            # 转换基准代码为tushare格式
            # 中证500: 000905.SH, 沪深300: 000300.SH
            if benchmark == "SH000905":
                tushare_code = "000905.SH"
            elif benchmark == "SH000300":
                tushare_code = "000300.SH"
            else:
                tushare_code = benchmark
            
            # 构建查询条件
            query = {
                "ts_code": tushare_code,
                "trade_date": {
                    "$gte": start_date.replace('-', ''),
                    "$lte": end_date.replace('-', '')
                }
            }
            
            # 查询数据
            collection_name = "index_daily"  # 使用实际的集合名
            cursor = self.db_handler.get_collection(collection_name).find(query).sort("trade_date", 1)
            
            # 转换为DataFrame
            data = []
            for doc in cursor:
                # tushare日期格式转换
                date_str = str(doc['trade_date'])
                row = {
                    'datetime': pd.to_datetime(date_str, format='%Y%m%d'),
                    'open': doc.get('open', np.nan),
                    'high': doc.get('high', np.nan),
                    'low': doc.get('low', np.nan),
                    'close': doc.get('close', np.nan),
                    'volume': doc.get('vol', np.nan),  # tushare指数用vol
                    'amount': doc.get('amount', np.nan)
                }
                data.append(row)
            
            if not data:
                return pd.DataFrame()
            
            df = pd.DataFrame(data)
            df.set_index('datetime', inplace=True)
            
            # 数据类型转换
            numeric_fields = ['open', 'high', 'low', 'close', 'volume', 'amount']
            for field in numeric_fields:
                if field in df.columns:
                    df[field] = pd.to_numeric(df[field], errors='coerce')
            
            return df
            
        except Exception as e:
            self.logger.error(f"获取基准{benchmark}数据失败: {e}")
            return pd.DataFrame()
    
    def get_stock_list(self, market: str = "CSI300") -> List[str]:
        """获取股票列表"""
        try:
            # 从数据库获取成分股（使用index_weight集合）
            collection_name = "index_weight"
            
            # 根据市场类型构建查询条件
            if market == "CSI500" or market == "csi500":
                query = {"index_code": "000905.SH"}
            elif market == "CSI300" or market == "csi300":
                query = {"index_code": "000300.SH"}
            elif market == "CSI1000" or market == "csi1000":
                query = {"index_code": "000852.SH"}
            elif market == "CSIA500" or market == "csia500":
                query = {"index_code": "000510.SH"}
            elif market == "SSE50" or market == "sse50":
                query = {"index_code": "000016.SH"}
            else:
                query = {"index_code": market}
            
            # 获取最新的成分股数据
            pipeline = [
                {"$match": query},
                {"$sort": {"trade_date": -1}},
                {"$group": {
                    "_id": "$con_code",
                    "latest_date": {"$first": "$trade_date"}
                }}
            ]
            
            cursor = self.db_handler.get_collection(collection_name).aggregate(pipeline)
            stocks = []
            
            for doc in cursor:
                stocks.append(doc['_id'])  # con_code就是股票代码
            
            # 转换为qlib格式
            qlib_stocks = [self._convert_to_qlib_format(stock) for stock in stocks]
            
            self.logger.info(f"获取到{len(qlib_stocks)}只{market}成分股")
            return qlib_stocks
            
        except Exception as e:
            self.logger.error(f"获取股票列表失败: {e}")
            return []
    
    def filter_small_cap_stocks(self, date: str, market: str = "CSI500", 
                               count: int = 50) -> List[str]:
        """筛选小市值股票"""
        try:
            # 转换日期格式
            date_str = date.replace('-', '')
            
            # 获取指定日期的所有股票市值数据，排除北交所股票
            query = {
                "trade_date": date_str,
                "total_mv": {"$exists": True, "$ne": None, "$gt": 0},  # tushare中市值字段
                "ts_code": {"$not": {"$regex": r"\.BJ$"}}  # 排除北交所股票（.BJ结尾）
            }
            
            collection_name = "stock_factor_pro"
            cursor = self.db_handler.get_collection(collection_name).find(query)
            
            # 收集市值数据
            market_cap_data = []
            for doc in cursor:
                ts_code = doc['ts_code']
                # 只处理沪深股票
                if ts_code.endswith('.SH') or ts_code.endswith('.SZ'):
                    market_cap_data.append({
                        'code': ts_code,  # tushare格式
                        'market_cap': doc.get('total_mv', 0)
                    })
            
            if not market_cap_data:
                self.logger.warning(f"未找到{date}的市值数据，使用默认股票池")
                return []
            
            # 转换为DataFrame并排序
            df = pd.DataFrame(market_cap_data)
            df = df.sort_values('market_cap', ascending=True)
            
            # 获取前N只小市值股票
            small_cap_stocks = df.head(count)['code'].tolist()
            
            # 转换为qlib格式
            qlib_stocks = [self._convert_to_qlib_format(stock) for stock in small_cap_stocks]
            
            self.logger.info(f"筛选出{len(qlib_stocks)}只小市值股票")
            return qlib_stocks
            
        except Exception as e:
            self.logger.error(f"筛选小市值股票失败: {e}")
            return []
    
    def create_dataset(self, symbols: List[str], start_date: str, end_date: str, 
                      fields: List[str] = None) -> dict:
        """创建qlib数据集"""
        try:
            # 获取多股票数据
            data = self.get_multi_stock_data(symbols, start_date, end_date, fields)
            
            # 返回数据字典格式
            return {
                "data": data,
                "symbols": symbols,
                "start_date": start_date,
                "end_date": end_date,
                "fields": fields
            }
            
        except Exception as e:
            self.logger.error(f"创建数据集失败: {e}")
            return None


# 单例模式
_qlib_adapter = None

def get_qlib_adapter() -> QlibDataAdapter:
    """获取Qlib数据适配器单例"""
    global _qlib_adapter
    if _qlib_adapter is None:
        _qlib_adapter = QlibDataAdapter()
    return _qlib_adapter