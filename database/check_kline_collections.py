#!/usr/bin/env python3
# -*- coding: utf-8 -*-

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

if __name__ == "__main__":
    check_collections()