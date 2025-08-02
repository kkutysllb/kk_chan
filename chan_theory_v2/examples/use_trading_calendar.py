#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
交易日历功能使用示例
展示如何在缠论分析中使用交易日历功能
"""

import sys
import os
import logging
from datetime import datetime, timedelta
import pandas as pd

# 添加项目根目录到系统路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# 导入交易日历功能
from chan_theory_v2.core import (
    get_nearest_trading_date,
    is_trading_day,
    get_trading_dates,
    get_previous_n_trading_days
)

# 导入数据库处理模块
from database.db_handler import DBHandler

# 设置日志级别
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def example_get_kline_with_trading_calendar():
    """
    示例：使用交易日历获取K线数据
    """
    logger.info("=== 示例：使用交易日历获取K线数据 ===")
    
    # 初始化数据库处理器
    db_handler = DBHandler()
    
    # 获取当前日期
    today = datetime.now()
    logger.info(f"当前日期: {today.strftime('%Y-%m-%d')}")
    
    # 获取最近的交易日
    latest_trading_day = get_nearest_trading_date(today, 'backward')
    logger.info(f"最近交易日: {latest_trading_day.strftime('%Y-%m-%d')}")
    
    # 获取30个交易日前的日期
    prev_trading_days = get_previous_n_trading_days(latest_trading_day, 30)
    start_date = prev_trading_days[0] if prev_trading_days else (latest_trading_day - timedelta(days=60))
    logger.info(f"开始日期: {start_date.strftime('%Y-%m-%d')}")
    
    # 获取股票代码（示例使用上证指数）
    stock_code = "000001.SH"
    
    # 获取K线数据
    try:
        # 转换日期格式为字符串
        start_date_str = start_date.strftime('%Y%m%d')
        end_date_str = latest_trading_day.strftime('%Y%m%d')
        
        # 查询K线数据
        kline_data = db_handler.get_kline_data(
            stock_code, 
            start_date=start_date_str, 
            end_date=end_date_str
        )
        
        if kline_data and len(kline_data) > 0:
            # 转换为DataFrame
            df = pd.DataFrame(kline_data)
            logger.info(f"获取到 {len(df)} 条K线数据")
            logger.info(f"数据范围: {df['trade_date'].min()} 至 {df['trade_date'].max()}")
            
            # 显示前5条数据
            logger.info("前5条数据:")
            for i, row in df.head().iterrows():
                logger.info(f"  {row['trade_date']}: 开:{row['open']:.2f} 高:{row['high']:.2f} 低:{row['low']:.2f} 收:{row['close']:.2f} 量:{row['vol']}")
        else:
            logger.warning(f"未获取到 {stock_code} 的K线数据")
    
    except Exception as e:
        logger.error(f"获取K线数据失败: {e}")


def example_date_range_conversion():
    """
    示例：日期范围转换为交易日范围
    """
    logger.info("\n=== 示例：日期范围转换为交易日范围 ===")
    
    # 获取当前日期
    today = datetime.now()
    
    # 获取过去90天的日期
    past_date = today - timedelta(days=90)
    
    logger.info(f"原始日期范围: {past_date.strftime('%Y-%m-%d')} 至 {today.strftime('%Y-%m-%d')}")
    
    # 转换为交易日范围
    start_trading_day = get_nearest_trading_date(past_date, 'forward')
    end_trading_day = get_nearest_trading_date(today, 'backward')
    
    logger.info(f"交易日范围: {start_trading_day.strftime('%Y-%m-%d')} 至 {end_trading_day.strftime('%Y-%m-%d')}")
    
    # 获取这段时间内的所有交易日
    trading_days = get_trading_dates(start_trading_day, end_trading_day)
    
    logger.info(f"期间共有 {len(trading_days)} 个交易日")
    logger.info(f"交易日占比: {len(trading_days) / 90:.2%}")


def example_backtest_period_selection():
    """
    示例：回测周期选择
    """
    logger.info("\n=== 示例：回测周期选择 ===")
    
    # 获取当前日期
    today = datetime.now()
    
    # 定义回测周期（例如：过去1年、2年、3年）
    periods = [
        {"name": "过去1年", "days": 365},
        {"name": "过去2年", "days": 365 * 2},
        {"name": "过去3年", "days": 365 * 3}
    ]
    
    for period in periods:
        # 计算开始日期
        start_date = today - timedelta(days=period["days"])
        
        # 转换为交易日
        start_trading_day = get_nearest_trading_date(start_date, 'forward')
        end_trading_day = get_nearest_trading_date(today, 'backward')
        
        # 获取交易日数量
        trading_days = get_trading_dates(start_trading_day, end_trading_day)
        
        logger.info(f"{period['name']}:")
        logger.info(f"  日历日期范围: {start_date.strftime('%Y-%m-%d')} 至 {today.strftime('%Y-%m-%d')}")
        logger.info(f"  交易日范围: {start_trading_day.strftime('%Y-%m-%d')} 至 {end_trading_day.strftime('%Y-%m-%d')}")
        logger.info(f"  交易日数量: {len(trading_days)}")
        logger.info(f"  交易日占比: {len(trading_days) / period['days']:.2%}")


def example_trading_day_check():
    """
    示例：交易日检查
    """
    logger.info("\n=== 示例：交易日检查 ===")
    
    # 获取当前日期
    today = datetime.now()
    
    # 检查今天是否为交易日
    is_today_trading = is_trading_day(today)
    logger.info(f"今天 {today.strftime('%Y-%m-%d')} 是否为交易日: {is_today_trading}")
    
    # 如果今天不是交易日，获取下一个交易日
    if not is_today_trading:
        next_trading_day = get_nearest_trading_date(today, 'forward')
        logger.info(f"下一个交易日: {next_trading_day.strftime('%Y-%m-%d')}")
    
    # 检查特定日期是否为交易日
    special_dates = [
        "2023-01-01",  # 元旦
        "2023-01-02",  # 元旦后的第一个工作日
        "2023-01-21",  # 春节前
        "2023-01-27",  # 春节期间
        "2023-01-30"   # 春节后
    ]
    
    for date in special_dates:
        is_trading = is_trading_day(date)
        logger.info(f"日期 {date} 是否为交易日: {is_trading}")


def main():
    """
    主函数
    """
    logger.info("开始演示交易日历功能使用示例...")
    
    # 示例：使用交易日历获取K线数据
    example_get_kline_with_trading_calendar()
    
    # 示例：日期范围转换为交易日范围
    example_date_range_conversion()
    
    # 示例：回测周期选择
    example_backtest_period_selection()
    
    # 示例：交易日检查
    example_trading_day_check()
    
    logger.info("交易日历功能使用示例演示完成!")


if __name__ == "__main__":
    main()