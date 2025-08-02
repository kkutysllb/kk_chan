#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速检查数据库股票数据
"""

import sys
import os

# 添加项目路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from database.db_handler import get_db_handler

def quick_check():
    """快速检查数据库"""
    print("🔍 快速检查数据库股票数据")
    print("="*50)
    
    try:
        db_handler = get_db_handler()
        db = db_handler.db
        
        # 列出所有集合
        collections = db.list_collection_names()
        print(f"📋 数据库集合总数: {len(collections)}")
        
        # 查找stock相关集合
        stock_collections = [c for c in collections if 'stock' in c.lower() or 'infrastructure' in c.lower()]
        print(f"📊 股票相关集合: {len(stock_collections)}")
        
        for collection_name in stock_collections:
            count = db[collection_name].count_documents({})
            print(f"   - {collection_name}: {count:,} 条记录")
            
            if count > 0:
                # 显示样本
                sample = db[collection_name].find_one()
                if sample:
                    print(f"     字段: {list(sample.keys())[:10]}")
                    if 'ts_code' in sample and 'name' in sample:
                        print(f"     样本: {sample['ts_code']} - {sample['name']}")
        
        # 专门检查选股器需要的集合
        print(f"\n🎯 检查选股器数据需求:")
        
        target_collection = "infrastructure_stock_basic"
        if target_collection in collections:
            collection = db[target_collection]
            total_count = collection.count_documents({})
            print(f"   {target_collection}: {total_count:,} 条记录")
            
            # 检查筛选条件
            filter_condition = {
                "name": {"$not": {"$regex": "ST|退市|暂停"}},
                "list_status": "L",
            }
            
            filtered_count = collection.count_documents(filter_condition)
            print(f"   符合选股条件: {filtered_count:,} 条记录")
            
            if filtered_count > 0:
                # 显示前5个样本
                samples = list(collection.find(filter_condition).limit(5))
                print(f"   样本股票:")
                for i, doc in enumerate(samples, 1):
                    print(f"     {i}. {doc.get('ts_code')} - {doc.get('name')}")
            else:
                print("   ❌ 没有符合筛选条件的股票")
                
                # 检查数据质量
                print(f"\n   🔧 数据质量检查:")
                total_with_name = collection.count_documents({"name": {"$exists": True, "$ne": None}})
                total_with_status = collection.count_documents({"list_status": {"$exists": True}})
                status_l = collection.count_documents({"list_status": "L"})
                
                print(f"     有名称字段: {total_with_name:,}")
                print(f"     有状态字段: {total_with_status:,}")
                print(f"     状态为L: {status_l:,}")
                
                # 查看ST股票数量
                st_count = collection.count_documents({"name": {"$regex": "ST|退市|暂停"}})
                print(f"     ST/退市股票: {st_count:,}")
                
        else:
            print(f"   ❌ 未找到 {target_collection} 集合")
            
    except Exception as e:
        print(f"❌ 检查失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    quick_check()