#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import argparse
from datetime import datetime
import pandas as pd
import numpy as np
from pymongo import ASCENDING, DESCENDING

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.db_handler import DBHandler

def check_collections():
    db = DBHandler()
    
    # 检查日K线数据
    print('\nstock_kline_daily集合:')
    collection = db.local_db['stock_kline_daily']
    print('总记录数:', collection.count_documents({}))
    print('最早的记录:')
    print(collection.find_one(sort=[('trade_date', 1)]))
    print('最新的记录:')
    print(collection.find_one(sort=[('trade_date', -1)]))
    
    # 检查5分钟和30分钟K线数据
    for collection_name in ['stock_kline_5min', 'stock_kline_30min']:
        print(f'\n{collection_name}集合:')
        collection = db.local_db[collection_name]
        print('总记录数:', collection.count_documents({}))
        print('最早的记录:')
        print(collection.find_one(sort=[('trade_time', 1)]))
        print('最新的记录:')
        print(collection.find_one(sort=[('trade_time', -1)]))

def query_kline_data(collection_name, stock_code=None, start_date=None, end_date=None, limit=10):
    """
    查询指定时间段的K线数据
    
    Args:
        collection_name (str): 集合名称，如'stock_kline_daily', 'stock_kline_5min', 'stock_kline_30min'
        stock_code (str, optional): 股票代码，如'000001.SZ'
        start_date (str, optional): 开始日期，格式为'YYYY-MM-DD'
        end_date (str, optional): 结束日期，格式为'YYYY-MM-DD'
        limit (int, optional): 限制返回的记录数量，默认为10
    """
    db = DBHandler()
    collection = db.local_db[collection_name]
    
    # 构建查询条件
    query = {}
    if stock_code:
        query['ts_code'] = stock_code
    
    # 处理日期条件
    date_field = 'trade_date' if 'daily' in collection_name else 'trade_time'
    if start_date or end_date:
        query[date_field] = {}
        if start_date:
            start_datetime = datetime.strptime(start_date, '%Y-%m-%d')
            query[date_field]['$gte'] = start_datetime
        if end_date:
            end_datetime = datetime.strptime(end_date, '%Y-%m-%d')
            # 如果是结束日期，设置为当天的23:59:59
            if 'daily' not in collection_name:
                end_datetime = datetime.strptime(f"{end_date} 23:59:59", '%Y-%m-%d %H:%M:%S')
            query[date_field]['$lte'] = end_datetime
    
    # 执行查询
    print(f"\n查询条件: {query}")
    cursor = collection.find(query).sort([(date_field, ASCENDING)]).limit(limit)
    results = list(cursor)
    
    # 显示结果
    if not results:
        print("未找到符合条件的数据")
        return None
    
    print(f"找到 {len(results)} 条记录:")
    for i, record in enumerate(results):
        print(f"\n记录 {i+1}:")
        # 格式化输出记录
        for key, value in record.items():
            if key != '_id':  # 排除MongoDB的_id字段
                print(f"  {key}: {value}")
    
    return results

def calculate_macd(df, fast_period=12, slow_period=26, signal_period=9):
    """
    计算MACD指标
    
    Args:
        df (pd.DataFrame): 包含K线数据的DataFrame，必须包含'close'列
        fast_period (int): 快速EMA周期，默认为12
        slow_period (int): 慢速EMA周期，默认为26
        signal_period (int): 信号线周期，默认为9
        
    Returns:
        pd.DataFrame: 包含MACD指标的DataFrame
    """
    if 'close' not in df.columns:
        print("错误: 数据中缺少'close'列")
        return None
    
    # 确保close列是数值类型
    df['close'] = pd.to_numeric(df['close'])
    
    # 计算EMA
    df['ema_fast'] = df['close'].ewm(span=fast_period, adjust=False).mean()
    df['ema_slow'] = df['close'].ewm(span=slow_period, adjust=False).mean()
    
    # 计算DIF (MACD Line)
    df['dif'] = df['ema_fast'] - df['ema_slow']
    
    # 计算DEA (Signal Line)
    df['dea'] = df['dif'].ewm(span=signal_period, adjust=False).mean()
    
    # 计算MACD柱状图 (Histogram)
    df['macd'] = 2 * (df['dif'] - df['dea'])
    
    return df

def check_macd_anomalies(df, threshold=100):
    """
    检查MACD指标中的异常值
    
    Args:
        df (pd.DataFrame): 包含MACD指标的DataFrame
        threshold (float): MACD柱状图异常阈值，默认为100
        
    Returns:
        list: 异常记录的索引列表
    """
    if 'macd' not in df.columns or 'dif' not in df.columns or 'dea' not in df.columns:
        print("错误: 数据中缺少MACD指标列")
        return []
    
    anomalies = []
    
    # 检查MACD柱状图异常大的值
    macd_anomalies = df[abs(df['macd']) > threshold].index.tolist()
    if macd_anomalies:
        print(f"\n发现 {len(macd_anomalies)} 条MACD柱状图异常记录:")
        for idx in macd_anomalies:
            print(f"  索引 {idx}: MACD = {df.loc[idx, 'macd']:.2f}, DIF = {df.loc[idx, 'dif']:.2f}, DEA = {df.loc[idx, 'dea']:.2f}")
            if 'trade_date' in df.columns:
                print(f"    日期: {df.loc[idx, 'trade_date']}")
            elif 'trade_time' in df.columns:
                print(f"    时间: {df.loc[idx, 'trade_time']}")
        anomalies.extend(macd_anomalies)
    
    # 检查DEA接近于0但DIF异常大的情况
    dea_zero_anomalies = df[(abs(df['dea']) < 0.1) & (abs(df['dif']) > threshold/2)].index.tolist()
    if dea_zero_anomalies:
        print(f"\n发现 {len(dea_zero_anomalies)} 条DEA接近0但DIF异常大的记录:")
        for idx in dea_zero_anomalies:
            if idx not in anomalies:  # 避免重复
                print(f"  索引 {idx}: MACD = {df.loc[idx, 'macd']:.2f}, DIF = {df.loc[idx, 'dif']:.2f}, DEA = {df.loc[idx, 'dea']:.2f}")
                if 'trade_date' in df.columns:
                    print(f"    日期: {df.loc[idx, 'trade_date']}")
                elif 'trade_time' in df.columns:
                    print(f"    时间: {df.loc[idx, 'trade_time']}")
                anomalies.append(idx)
    
    # 检查连续多个MACD值完全相同的情况
    df['macd_diff'] = df['macd'].diff()
    zero_diff_groups = []
    current_group = []
    
    for i, val in enumerate(df['macd_diff'].values):
        if i > 0 and abs(val) < 1e-10:  # 几乎为0
            if not current_group:
                current_group = [i-1, i]
            else:
                current_group.append(i)
        else:
            if len(current_group) > 2:  # 至少3个连续相同值
                zero_diff_groups.append(current_group)
            current_group = []
    
    if current_group and len(current_group) > 2:
        zero_diff_groups.append(current_group)
    
    if zero_diff_groups:
        print(f"\n发现 {len(zero_diff_groups)} 组连续MACD值完全相同的记录:")
        for group in zero_diff_groups:
            print(f"  索引 {group[0]} 到 {group[-1]}: MACD = {df.loc[group[0], 'macd']:.2f}")
            if 'trade_date' in df.columns:
                print(f"    起始日期: {df.loc[group[0], 'trade_date']}")
                print(f"    结束日期: {df.loc[group[-1], 'trade_date']}")
            elif 'trade_time' in df.columns:
                print(f"    起始时间: {df.loc[group[0], 'trade_time']}")
                print(f"    结束时间: {df.loc[group[-1], 'trade_time']}")
            anomalies.extend(group)
    
    return list(set(anomalies))  # 去重

def analyze_kline_data(collection_name, stock_code=None, start_date=None, end_date=None, limit=100):
    """
    分析K线数据并检查MACD指标异常
    
    Args:
        collection_name (str): 集合名称
        stock_code (str, optional): 股票代码
        start_date (str, optional): 开始日期
        end_date (str, optional): 结束日期
        limit (int, optional): 限制返回的记录数量
    """
    # 查询K线数据
    results = query_kline_data(collection_name, stock_code, start_date, end_date, limit)
    if not results:
        return
    
    # 转换为DataFrame
    df = pd.DataFrame(results)
    
    # 确保有close列
    if 'close' not in df.columns:
        print("错误: 数据中缺少'close'列，无法计算MACD")
        return
    
    # 计算MACD指标
    print("\n计算MACD指标...")
    df = calculate_macd(df)
    
    # 检查MACD异常
    print("\n检查MACD异常...")
    anomalies = check_macd_anomalies(df)
    
    if not anomalies:
        print("\n未发现MACD异常")
    else:
        print(f"\n总共发现 {len(anomalies)} 条MACD异常记录")
        
        # 显示MACD统计信息
        print("\nMACD统计信息:")
        print(f"  最小值: {df['macd'].min():.2f}")
        print(f"  最大值: {df['macd'].max():.2f}")
        print(f"  平均值: {df['macd'].mean():.2f}")
        print(f"  标准差: {df['macd'].std():.2f}")
        
        print("\nDIF统计信息:")
        print(f"  最小值: {df['dif'].min():.2f}")
        print(f"  最大值: {df['dif'].max():.2f}")
        print(f"  平均值: {df['dif'].mean():.2f}")
        print(f"  标准差: {df['dif'].std():.2f}")
        
        print("\nDEA统计信息:")
        print(f"  最小值: {df['dea'].min():.2f}")
        print(f"  最大值: {df['dea'].max():.2f}")
        print(f"  平均值: {df['dea'].mean():.2f}")
        print(f"  标准差: {df['dea'].std():.2f}")

def main():
    parser = argparse.ArgumentParser(description='检查和查询K线数据集合')
    parser.add_argument('--action', choices=['check', 'query', 'analyze'], default='check',
                        help='执行的操作: check(检查集合), query(查询数据), analyze(分析MACD)')
    parser.add_argument('--collection', type=str, 
                        help='集合名称: stock_kline_daily, stock_kline_5min, stock_kline_30min')
    parser.add_argument('--code', type=str, help='股票代码，如000001.SZ')
    parser.add_argument('--start', type=str, help='开始日期，格式为YYYY-MM-DD')
    parser.add_argument('--end', type=str, help='结束日期，格式为YYYY-MM-DD')
    parser.add_argument('--limit', type=int, default=100, help='限制返回的记录数量，默认为100')
    
    args = parser.parse_args()
    
    if args.action == 'check':
        check_collections()
    elif args.action == 'query':
        if not args.collection:
            print("错误: 查询操作需要指定集合名称 (--collection)")
            return
        query_kline_data(
            args.collection, 
            args.code, 
            args.start, 
            args.end, 
            args.limit
        )
    elif args.action == 'analyze':
        if not args.collection:
            print("错误: 分析操作需要指定集合名称 (--collection)")
            return
        analyze_kline_data(
            args.collection, 
            args.code, 
            args.start, 
            args.end, 
            args.limit
        )

if __name__ == "__main__":
    main()