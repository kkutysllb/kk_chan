#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
交易日历工具
提供交易日期相关的功能，如获取最近交易日、判断是否为交易日等
"""

import logging
from datetime import datetime, timedelta
from typing import Optional, Union, List, Dict
import sys
import os

# 添加项目根目录到系统路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# 导入数据库处理模块
from database.db_handler import DBHandler

logger = logging.getLogger(__name__)


class TradingCalendar:
    """
    交易日历工具类
    提供交易日期相关的功能，如获取最近交易日、判断是否为交易日等
    """
    
    def __init__(self, db_handler: Optional[DBHandler] = None):
        """
        初始化交易日历工具
        
        Args:
            db_handler: 数据库处理器，如果为None则创建新的实例
        """
        self.db_handler = db_handler or DBHandler()
        self._calendar_cache = {}
        self._cache_expiry = datetime.now()
        
    def get_nearest_trading_date(self, target_date: Union[datetime, str], 
                                direction: str = 'backward') -> Optional[datetime]:
        """
        获取最近的交易日
        
        Args:
            target_date: 目标日期，可以是datetime对象或字符串(格式: 'YYYYMMDD'或'YYYY-MM-DD')
            direction: 查找方向，'backward'表示向前查找，'forward'表示向后查找
            
        Returns:
            最近的交易日，如果未找到则返回None
        """
        # 标准化日期格式
        if isinstance(target_date, str):
            if '-' in target_date:
                target_date = datetime.strptime(target_date, '%Y-%m-%d')
            else:
                target_date = datetime.strptime(target_date, '%Y%m%d')
        
        # 确保target_date只包含日期部分
        target_date = datetime(target_date.year, target_date.month, target_date.day)
        
        # 转换为字符串格式用于查询
        target_date_str = target_date.strftime('%Y%m%d')
        
        # 构建查询条件
        query = {
            'exchange': 'SSE',  # 上海证券交易所
        }
        
        if direction == 'backward':
            # 向前查找（小于等于目标日期的最近交易日）
            query['cal_date'] = {'$lte': target_date_str}
            query['is_open'] = 1
            sort_direction = -1  # 降序
        else:
            # 向后查找（大于等于目标日期的最近交易日）
            query['cal_date'] = {'$gte': target_date_str}
            query['is_open'] = 1
            sort_direction = 1  # 升序
        
        try:
            # 查询交易日历
            calendar_data = self.db_handler.find_data(
                'infrastructure_trading_calendar', 
                query,
                sort=[('cal_date', sort_direction)],
                limit=1
            )
            
            if calendar_data and len(calendar_data) > 0:
                cal_date = calendar_data[0]['cal_date']
                # 确保返回datetime对象
                if isinstance(cal_date, str):
                    return datetime.strptime(cal_date, '%Y%m%d')
                return cal_date
            else:
                logger.warning(f"未找到{target_date_str}附近的交易日")
                return None
                
        except Exception as e:
            logger.error(f"获取最近交易日失败: {e}")
            return None
    
    def is_trading_day(self, date: Union[datetime, str]) -> bool:
        """
        判断指定日期是否为交易日
        
        Args:
            date: 日期，可以是datetime对象或字符串(格式: 'YYYYMMDD'或'YYYY-MM-DD')
            
        Returns:
            是否为交易日
        """
        # 标准化日期格式
        if isinstance(date, str):
            if '-' in date:
                date = datetime.strptime(date, '%Y-%m-%d')
            else:
                date = datetime.strptime(date, '%Y%m%d')
        
        # 确保date只包含日期部分
        date = datetime(date.year, date.month, date.day)
        date_str = date.strftime('%Y%m%d')
        
        try:
            # 查询交易日历
            calendar_data = self.db_handler.find_data(
                'infrastructure_trading_calendar', 
                {
                    'cal_date': date_str,
                    'exchange': 'SSE'
                }
            )
            
            if calendar_data and len(calendar_data) > 0:
                return calendar_data[0].get('is_open', 0) == 1
            else:
                logger.warning(f"未找到日期{date_str}的交易日历数据")
                return False
                
        except Exception as e:
            logger.error(f"判断交易日失败: {e}")
            return False
    
    def get_trading_dates(self, start_date: Union[datetime, str], 
                         end_date: Union[datetime, str]) -> List[datetime]:
        """
        获取指定日期范围内的所有交易日
        
        Args:
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            交易日列表
        """
        # 标准化日期格式
        if isinstance(start_date, str):
            if '-' in start_date:
                start_date = datetime.strptime(start_date, '%Y-%m-%d')
            else:
                start_date = datetime.strptime(start_date, '%Y%m%d')
                
        if isinstance(end_date, str):
            if '-' in end_date:
                end_date = datetime.strptime(end_date, '%Y-%m-%d')
            else:
                end_date = datetime.strptime(end_date, '%Y%m%d')
        
        # 确保只包含日期部分
        start_date = datetime(start_date.year, start_date.month, start_date.day)
        end_date = datetime(end_date.year, end_date.month, end_date.day)
        
        # 转换为字符串格式用于查询
        start_date_str = start_date.strftime('%Y%m%d')
        end_date_str = end_date.strftime('%Y%m%d')
        
        try:
            # 查询交易日历
            calendar_data = self.db_handler.find_data(
                'infrastructure_trading_calendar', 
                {
                    'cal_date': {'$gte': start_date_str, '$lte': end_date_str},
                    'exchange': 'SSE',
                    'is_open': 1
                },
                sort=[('cal_date', 1)]
            )
            
            # 转换为datetime列表
            trading_dates = []
            for item in calendar_data:
                cal_date = item['cal_date']
                if isinstance(cal_date, str):
                    trading_dates.append(datetime.strptime(cal_date, '%Y%m%d'))
                else:
                    trading_dates.append(cal_date)
            
            return trading_dates
                
        except Exception as e:
            logger.error(f"获取交易日列表失败: {e}")
            return []
    
    def get_previous_n_trading_days(self, date: Union[datetime, str], n: int) -> List[datetime]:
        """
        获取指定日期前N个交易日
        
        Args:
            date: 日期
            n: 交易日数量
            
        Returns:
            交易日列表
        """
        # 标准化日期格式
        if isinstance(date, str):
            if '-' in date:
                date = datetime.strptime(date, '%Y-%m-%d')
            else:
                date = datetime.strptime(date, '%Y%m%d')
        
        # 确保date只包含日期部分
        date = datetime(date.year, date.month, date.day)
        date_str = date.strftime('%Y%m%d')
        
        try:
            # 查询交易日历
            calendar_data = self.db_handler.find_data(
                'infrastructure_trading_calendar', 
                {
                    'cal_date': {'$lte': date_str},
                    'exchange': 'SSE',
                    'is_open': 1
                },
                sort=[('cal_date', -1)],
                limit=n
            )
            
            # 转换为datetime列表并按日期升序排序
            trading_dates = []
            for item in calendar_data:
                cal_date = item['cal_date']
                if isinstance(cal_date, str):
                    trading_dates.append(datetime.strptime(cal_date, '%Y%m%d'))
                else:
                    trading_dates.append(cal_date)
            
            return sorted(trading_dates)
                
        except Exception as e:
            logger.error(f"获取前N个交易日失败: {e}")
            return []


# 单例模式，提供全局访问点
_trading_calendar_instance = None

def get_trading_calendar() -> TradingCalendar:
    """
    获取交易日历实例（单例模式）
    
    Returns:
        交易日历实例
    """
    global _trading_calendar_instance
    if _trading_calendar_instance is None:
        _trading_calendar_instance = TradingCalendar()
    return _trading_calendar_instance


def reset_trading_calendar() -> None:
    """
    重置交易日历实例
    """
    global _trading_calendar_instance
    _trading_calendar_instance = None


def get_nearest_trading_date(target_date: Union[datetime, str], 
                           direction: str = 'backward') -> Optional[datetime]:
    """
    获取最近的交易日（便捷函数）
    
    Args:
        target_date: 目标日期
        direction: 查找方向，'backward'表示向前查找，'forward'表示向后查找
        
    Returns:
        最近的交易日
    """
    return get_trading_calendar().get_nearest_trading_date(target_date, direction)


def is_trading_day(date: Union[datetime, str]) -> bool:
    """
    判断指定日期是否为交易日（便捷函数）
    
    Args:
        date: 日期
        
    Returns:
        是否为交易日
    """
    return get_trading_calendar().is_trading_day(date)


def get_trading_dates(start_date: Union[datetime, str], 
                     end_date: Union[datetime, str]) -> List[datetime]:
    """
    获取指定日期范围内的所有交易日（便捷函数）
    
    Args:
        start_date: 开始日期
        end_date: 结束日期
        
    Returns:
        交易日列表
    """
    return get_trading_calendar().get_trading_dates(start_date, end_date)


def get_previous_n_trading_days(date: Union[datetime, str], n: int) -> List[datetime]:
    """
    获取指定日期前N个交易日（便捷函数）
    
    Args:
        date: 日期
        n: 交易日数量
        
    Returns:
        交易日列表
    """
    return get_trading_calendar().get_previous_n_trading_days(date, n)


if __name__ == "__main__":
    # 简单测试
    logging.basicConfig(level=logging.INFO)
    
    # 测试获取最近交易日
    today = datetime.now()
    nearest_trading_day = get_nearest_trading_date(today)
    print(f"今天: {today.strftime('%Y-%m-%d')}")
    print(f"最近交易日: {nearest_trading_day.strftime('%Y-%m-%d') if nearest_trading_day else 'None'}")
    
    # 测试判断是否为交易日
    is_today_trading = is_trading_day(today)
    print(f"今天是否为交易日: {is_today_trading}")
    
    # 测试获取交易日列表
    start = today - timedelta(days=30)
    trading_days = get_trading_dates(start, today)
    print(f"过去30天的交易日数量: {len(trading_days)}")
    
    # 测试获取前N个交易日
    prev_days = get_previous_n_trading_days(today, 5)
    print(f"前5个交易日: {[d.strftime('%Y-%m-%d') for d in prev_days]}")