#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查数据质量问题
"""

import sys
import os
from datetime import datetime, timedelta

# 添加项目路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from database.db_handler import get_db_handler
from chan_theory_v2.core.trading_calendar import get_nearest_trading_date

def check_data_intervals(symbol="300750.SZ", days=30):
    """检查数据时间间隔"""
    print(f"🔍 检查 {symbol} 数据质量")
    print("="*50)
    
    db_handler = get_db_handler()
    collection = db_handler.get_collection("stock_kline_30min")
    
    # 获取最近交易日
    current_date = datetime.now().date()
    end_trading_date = get_nearest_trading_date(current_date, direction='backward')
    start_date = end_trading_date - timedelta(days=days)
    
    print(f"查询时间范围: {start_date} 到 {end_trading_date}")
    
    # 获取数据
    start_datetime = datetime.combine(start_date, datetime.min.time())
    end_datetime = datetime.combine(end_trading_date, datetime.max.time())
    
    cursor = collection.find({
        "ts_code": symbol,
        "trade_time": {
            "$gte": start_datetime.strftime("%Y-%m-%d %H:%M:%S"),
            "$lte": end_datetime.strftime("%Y-%m-%d %H:%M:%S")
        }
    }).sort("trade_time", 1)
    
    data = list(cursor)
    print(f"获取到 {len(data)} 条数据")
    
    if len(data) < 2:
        print("❌ 数据不足")
        return
    
    # 检查时间间隔
    abnormal_intervals = []
    prev_time = None
    
    for i, doc in enumerate(data):
        try:
            current_time = datetime.strptime(doc['trade_time'], '%Y-%m-%d %H:%M:%S')
            
            if prev_time:
                interval = (current_time - prev_time).total_seconds() / 60  # 分钟
                
                # 30分钟K线，正常间隔应该是30分钟
                if interval > 60:  # 超过1小时认为异常
                    abnormal_intervals.append({
                        'index': i,
                        'prev_time': prev_time,
                        'current_time': current_time,
                        'interval_minutes': interval,
                        'prev_price': data[i-1].get('close', 0),
                        'current_price': doc.get('close', 0)
                    })
            
            prev_time = current_time
            
        except Exception as e:
            print(f"❌ 处理第{i}条数据时出错: {e}")
    
    print(f"\n发现 {len(abnormal_intervals)} 个异常时间间隔:")
    
    for interval in abnormal_intervals[:10]:  # 只显示前10个
        price_change = abs(interval['current_price'] - interval['prev_price']) / interval['prev_price'] * 100
        print(f"  {interval['prev_time']} -> {interval['current_time']}")
        print(f"    间隔: {interval['interval_minutes']:.0f}分钟")
        print(f"    价格: {interval['prev_price']:.2f} -> {interval['current_price']:.2f} ({price_change:.2f}%)")
        print()
    
    if len(abnormal_intervals) > 10:
        print(f"  ...还有 {len(abnormal_intervals) - 10} 个异常间隔")
    
    # 检查最近几天的数据
    print("\n📅 最近5天数据:")
    for doc in data[-20:]:  # 显示最后20条数据
        try:
            time_str = doc['trade_time']
            close_price = doc.get('close', 0)
            volume = doc.get('vol', 0)
            print(f"  {time_str}: 收盘={close_price:.2f}, 成交量={volume}")
        except:
            continue

if __name__ == "__main__":
    check_data_intervals()