#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库集合检查器
用于查询指定集合的数据总条目、字段信息和时间范围等统计信息
"""

import sys
import os
import json
import argparse
from datetime import datetime
from typing import Dict, List, Any, Optional, Union
from collections import Counter
import pandas as pd

# 添加项目根目录到路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

from database.db_handler import DBHandler


class DatabaseCollectionInspector:
    """数据库集合检查器"""
    
    def __init__(self):
        """初始化检查器"""
        self.db_handler = DBHandler()
        
    def list_all_collections(self) -> List[str]:
        """获取所有集合列表"""
        try:
            collections = self.db_handler.db.list_collection_names()
            return sorted(collections)
        except Exception as e:
            print(f"获取集合列表失败: {e}")
            return []
    
    def get_collection_basic_info(self, collection_name: str) -> Dict[str, Any]:
        """获取集合基本信息"""
        try:
            collection = self.db_handler.get_collection(collection_name)
            
            # 获取集合统计信息
            stats = self.db_handler.db.command("collStats", collection_name)
            
            # 文档总数
            total_count = collection.count_documents({})
            
            basic_info = {
                'collection_name': collection_name,
                'total_documents': total_count,
                'storage_size': stats.get('storageSize', 0),
                'avg_obj_size': stats.get('avgObjSize', 0),
                'total_index_size': stats.get('totalIndexSize', 0),
                'indexes_count': stats.get('nindexes', 0)
            }
            
            return basic_info
            
        except Exception as e:
            print(f"获取集合 {collection_name} 基本信息失败: {e}")
            return {}
    
    def analyze_collection_fields(self, collection_name: str, sample_size: int = 1000) -> Dict[str, Any]:
        """分析集合字段信息"""
        try:
            collection = self.db_handler.get_collection(collection_name)
            
            # 获取样本数据进行字段分析
            sample_docs = list(collection.aggregate([
                {"$sample": {"size": sample_size}},
                {"$limit": sample_size}
            ]))
            
            if not sample_docs:
                return {'error': '集合为空或无法获取样本数据'}
            
            # 分析字段
            field_info = {}
            field_types = Counter()
            
            for doc in sample_docs:
                for field, value in doc.items():
                    if field not in field_info:
                        field_info[field] = {
                            'type': type(value).__name__,
                            'sample_values': [],
                            'null_count': 0,
                            'unique_count': 0
                        }
                    
                    # 记录字段类型
                    field_types[(field, type(value).__name__)] += 1
                    
                    # 记录样本值（最多5个）
                    if len(field_info[field]['sample_values']) < 5:
                        if value is not None and value not in field_info[field]['sample_values']:
                            field_info[field]['sample_values'].append(value)
                    
                    # 统计空值
                    if value is None or value == '' or value == 'None':
                        field_info[field]['null_count'] += 1
            
            # 计算字段统计信息
            for field in field_info:
                # 获取最常见的类型
                field_type_counts = [count for (f, t), count in field_types.items() if f == field]
                field_info[field]['total_samples'] = sum(field_type_counts)
                field_info[field]['null_percentage'] = (field_info[field]['null_count'] / len(sample_docs)) * 100
            
            return {
                'total_fields': len(field_info),
                'sample_size': len(sample_docs),
                'fields': field_info
            }
            
        except Exception as e:
            print(f"分析集合 {collection_name} 字段失败: {e}")
            return {'error': str(e)}
    
    def get_time_range_info(self, collection_name: str, date_fields: List[str] = None) -> Dict[str, Any]:
        """获取集合的时间范围信息"""
        try:
            collection = self.db_handler.get_collection(collection_name)
            
            # 常见的时间字段名
            if date_fields is None:
                date_fields = [
                    'trade_date', 'date', 'timestamp', 'created_at', 'updated_at',
                    'cal_date', 'ann_date', 'f_ann_date', 'end_date', 'start_date'
                ]
            
            time_info = {}
            
            # 检查每个可能的时间字段
            for field in date_fields:
                try:
                    # 检查字段是否存在
                    field_exists = collection.count_documents({field: {"$exists": True, "$ne": None}})
                    
                    if field_exists > 0:
                        # 获取最早和最晚的时间
                        earliest = list(collection.find({field: {"$exists": True, "$ne": None}}).sort(field, 1).limit(1))
                        latest = list(collection.find({field: {"$exists": True, "$ne": None}}).sort(field, -1).limit(1))
                        
                        if earliest and latest:
                            earliest_value = earliest[0][field]
                            latest_value = latest[0][field]
                            
                            time_info[field] = {
                                'earliest': earliest_value,
                                'latest': latest_value,
                                'records_count': field_exists,
                                'data_type': type(earliest_value).__name__
                            }
                            
                            # 如果是字符串格式的日期，尝试解析
                            if isinstance(earliest_value, str):
                                try:
                                    if len(earliest_value) == 8 and earliest_value.isdigit():
                                        # YYYYMMDD格式
                                        earliest_date = datetime.strptime(earliest_value, '%Y%m%d')
                                        latest_date = datetime.strptime(latest_value, '%Y%m%d')
                                        time_info[field]['earliest_parsed'] = earliest_date.strftime('%Y-%m-%d')
                                        time_info[field]['latest_parsed'] = latest_date.strftime('%Y-%m-%d')
                                        time_info[field]['time_span_days'] = (latest_date - earliest_date).days
                                except:
                                    pass
                            
                except Exception as e:
                    continue
            
            return time_info
            
        except Exception as e:
            print(f"获取集合 {collection_name} 时间范围失败: {e}")
            return {'error': str(e)}
    
    def get_sample_documents(self, collection_name: str, limit: int = 5) -> List[Dict]:
        """获取样本文档"""
        try:
            collection = self.db_handler.get_collection(collection_name)
            
            # 获取样本文档
            samples = list(collection.find().limit(limit))
            
            # 转换ObjectId为字符串以便JSON序列化
            for doc in samples:
                if '_id' in doc:
                    doc['_id'] = str(doc['_id'])
            
            return samples
            
        except Exception as e:
            print(f"获取集合 {collection_name} 样本文档失败: {e}")
            return []
    
    def find_financial_fields(self, collection_name: str) -> Dict[str, Any]:
        """查找财务指标相关字段"""
        try:
            collection = self.db_handler.get_collection(collection_name)
            
            # 获取一个样本文档来分析字段
            sample_doc = collection.find_one()
            if not sample_doc:
                return {'error': '集合为空'}
            
            # 财务指标相关关键词
            financial_keywords = [
                'eps', 'roe', 'roa', 'bvps', 'bv', 'pb', 'pe', 'ps',
                'revenue', 'profit', 'income', 'asset', 'debt', 'equity',
                'cash', 'flow', 'margin', 'ratio', 'return', 'growth',
                'dividend', 'earnings', 'book', 'value', 'net', 'gross',
                'total', 'current', 'quick', 'working', 'capital'
            ]
            
            # 查找匹配的字段
            financial_fields = {}
            all_fields = list(sample_doc.keys())
            
            for field in all_fields:
                field_lower = field.lower()
                for keyword in financial_keywords:
                    if keyword in field_lower:
                        # 获取该字段的样本值
                        sample_values = []
                        docs_with_field = list(collection.find(
                            {field: {"$exists": True, "$ne": None}}, 
                            {field: 1}
                        ).limit(5))
                        
                        for doc in docs_with_field:
                            if field in doc and doc[field] is not None:
                                sample_values.append(doc[field])
                        
                        financial_fields[field] = {
                            'matched_keyword': keyword,
                            'sample_values': sample_values[:5],
                            'field_type': type(sample_doc.get(field)).__name__,
                            'has_data': len(sample_values) > 0
                        }
                        break
            
            return {
                'total_fields': len(all_fields),
                'financial_fields_count': len(financial_fields),
                'financial_fields': financial_fields,
                'all_fields_sample': sorted(all_fields)[:50]  # 显示前50个字段
            }
            
        except Exception as e:
            print(f"查找集合 {collection_name} 财务字段失败: {e}")
            return {'error': str(e)}
    
    def get_specific_field_info(self, collection_name: str, field_names: List[str]) -> Dict[str, Any]:
        """获取指定字段的详细信息"""
        try:
            collection = self.db_handler.get_collection(collection_name)
            
            field_info = {}
            
            for field_name in field_names:
                # 检查字段是否存在
                field_exists = collection.count_documents({field_name: {"$exists": True}})
                
                if field_exists > 0:
                    # 获取有值的文档数量
                    non_null_count = collection.count_documents({
                        field_name: {"$exists": True, "$ne": None, "$ne": ""}
                    })
                    
                    # 获取样本值
                    sample_docs = list(collection.find(
                        {field_name: {"$exists": True, "$ne": None}}, 
                        {field_name: 1, "ts_code": 1, "trade_date": 1}
                    ).limit(10))
                    
                    sample_values = []
                    for doc in sample_docs:
                        if field_name in doc:
                            sample_values.append({
                                'value': doc[field_name],
                                'ts_code': doc.get('ts_code', 'N/A'),
                                'trade_date': doc.get('trade_date', 'N/A')
                            })
                    
                    field_info[field_name] = {
                        'exists_count': field_exists,
                        'non_null_count': non_null_count,
                        'null_percentage': ((field_exists - non_null_count) / field_exists * 100) if field_exists > 0 else 0,
                        'sample_values': sample_values
                    }
                else:
                    field_info[field_name] = {
                        'exists': False,
                        'message': '字段不存在'
                    }
            
            return field_info
            
        except Exception as e:
            print(f"获取字段信息失败: {e}")
            return {'error': str(e)}
    
    def inspect_collection(self, collection_name: str, detailed: bool = True) -> Dict[str, Any]:
        """全面检查指定集合"""
        print(f"\n🔍 正在检查集合: {collection_name}")
        
        # 基本信息
        basic_info = self.get_collection_basic_info(collection_name)
        if not basic_info:
            return {'error': f'无法获取集合 {collection_name} 的信息'}
        
        result = {
            'collection_name': collection_name,
            'basic_info': basic_info,
            'inspection_time': datetime.now().isoformat()
        }
        
        if detailed:
            print("  📊 分析字段信息...")
            field_analysis = self.analyze_collection_fields(collection_name)
            result['field_analysis'] = field_analysis
            
            print("  📅 分析时间范围...")
            time_analysis = self.get_time_range_info(collection_name)
            result['time_analysis'] = time_analysis
            
            print("  📄 获取样本文档...")
            samples = self.get_sample_documents(collection_name)
            result['sample_documents'] = samples
        
        return result
    
    def generate_report(self, collection_name: str, detailed: bool = True, 
                       output_file: str = None) -> Dict[str, Any]:
        """生成集合检查报告"""
        
        # 执行检查
        inspection_result = self.inspect_collection(collection_name, detailed)
        
        if 'error' in inspection_result:
            print(f"❌ 检查失败: {inspection_result['error']}")
            return inspection_result
        
        # 打印报告
        self._print_report(inspection_result)
        
        # 保存到文件
        if output_file:
            try:
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(inspection_result, f, ensure_ascii=False, indent=2, default=str)
                print(f"\n💾 报告已保存到: {output_file}")
            except Exception as e:
                print(f"❌ 保存报告失败: {e}")
        
        return inspection_result
    
    def _print_report(self, result: Dict[str, Any]):
        """打印检查报告"""
        basic_info = result.get('basic_info', {})
        
        print(f"\n" + "="*80)
        print(f"📋 集合检查报告: {result['collection_name']}")
        print(f"🕐 检查时间: {result['inspection_time']}")
        print(f"="*80)
        
        # 基本信息
        print(f"\n📊 基本信息:")
        print(f"  📄 文档总数: {basic_info.get('total_documents', 0):,}")
        print(f"  💾 存储大小: {self._format_bytes(basic_info.get('storage_size', 0))}")
        print(f"  📐 平均文档大小: {self._format_bytes(basic_info.get('avg_obj_size', 0))}")
        print(f"  🗂️  索引数量: {basic_info.get('indexes_count', 0)}")
        print(f"  🔍 索引大小: {self._format_bytes(basic_info.get('total_index_size', 0))}")
        
        # 字段分析
        if 'field_analysis' in result:
            field_analysis = result['field_analysis']
            
            if 'error' not in field_analysis:
                print(f"\n🏷️  字段分析:")
                print(f"  🔢 字段总数: {field_analysis.get('total_fields', 0)}")
                print(f"  📊 样本大小: {field_analysis.get('sample_size', 0)}")
                
                # 显示前10个字段的详细信息
                fields = field_analysis.get('fields', {})
                if fields:
                    print(f"\n  📋 主要字段信息 (前10个):")
                    for i, (field_name, field_info) in enumerate(list(fields.items())[:10]):
                        print(f"    {i+1:2d}. {field_name}")
                        print(f"        类型: {field_info.get('type', 'unknown')}")
                        print(f"        空值率: {field_info.get('null_percentage', 0):.1f}%")
                        
                        # 显示样本值
                        sample_values = field_info.get('sample_values', [])
                        if sample_values:
                            sample_str = ', '.join([str(v)[:50] for v in sample_values[:3]])
                            print(f"        样本值: {sample_str}")
                        print()
        
        # 时间分析
        if 'time_analysis' in result:
            time_analysis = result['time_analysis']
            
            if time_analysis and 'error' not in time_analysis:
                print(f"📅 时间范围分析:")
                
                for field_name, time_info in time_analysis.items():
                    print(f"\n  🕒 时间字段: {field_name}")
                    print(f"      记录数量: {time_info.get('records_count', 0):,}")
                    print(f"      数据类型: {time_info.get('data_type', 'unknown')}")
                    print(f"      最早时间: {time_info.get('earliest', 'N/A')}")
                    print(f"      最晚时间: {time_info.get('latest', 'N/A')}")
                    
                    if 'time_span_days' in time_info:
                        print(f"      时间跨度: {time_info['time_span_days']} 天")
                    
                    if 'earliest_parsed' in time_info:
                        print(f"      解析范围: {time_info['earliest_parsed']} ~ {time_info['latest_parsed']}")
            else:
                print(f"📅 时间范围分析: 未找到时间字段")
        
        # 样本文档
        if 'sample_documents' in result:
            samples = result['sample_documents']
            if samples:
                print(f"\n📄 样本文档 (前{len(samples)}条):")
                for i, doc in enumerate(samples, 1):
                    print(f"\n  样本 {i}:")
                    # 只显示前5个字段
                    for j, (key, value) in enumerate(list(doc.items())[:5]):
                        if isinstance(value, str) and len(value) > 100:
                            value = value[:100] + "..."
                        print(f"    {key}: {value}")
                    if len(doc) > 5:
                        print(f"    ... (还有 {len(doc) - 5} 个字段)")
    
    def _format_bytes(self, bytes_size: int) -> str:
        """格式化字节大小"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_size < 1024.0:
                return f"{bytes_size:.1f} {unit}"
            bytes_size /= 1024.0
        return f"{bytes_size:.1f} PB"


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='数据库集合检查器')
    
    parser.add_argument('--list', '-l', action='store_true', 
                       help='列出所有集合')
    
    parser.add_argument('--collection', '-c', type=str,
                       help='指定要检查的集合名称')
    
    parser.add_argument('--simple', '-s', action='store_true',
                       help='简单模式，只显示基本信息')
    
    parser.add_argument('--output', '-o', type=str,
                       help='输出报告到指定文件 (JSON格式)')
    
    parser.add_argument('--interactive', '-i', action='store_true',
                       help='交互模式，可以选择集合进行检查')
    
    parser.add_argument('--financial', '-f', type=str,
                       help='查找指定集合中的财务指标字段')
    
    parser.add_argument('--fields', type=str, nargs='+',
                       help='检查指定字段的详细信息 (需要配合 --collection 使用)')
    
    args = parser.parse_args()
    
    # 创建检查器
    inspector = DatabaseCollectionInspector()
    
    # 列出所有集合
    if args.list:
        print("📚 数据库集合列表:")
        collections = inspector.list_all_collections()
        for i, collection in enumerate(collections, 1):
            print(f"  {i:2d}. {collection}")
        print(f"\n总计: {len(collections)} 个集合")
        return
    
    # 交互模式
    if args.interactive:
        collections = inspector.list_all_collections()
        
        print("📚 可用集合:")
        for i, collection in enumerate(collections, 1):
            print(f"  {i:2d}. {collection}")
        
        try:
            choice = input(f"\n请选择要检查的集合 (1-{len(collections)}) 或输入集合名称: ").strip()
            
            if choice.isdigit():
                index = int(choice) - 1
                if 0 <= index < len(collections):
                    collection_name = collections[index]
                else:
                    print("❌ 无效的选择")
                    return
            else:
                collection_name = choice
            
            # 询问是否详细检查
            detailed_choice = input("是否进行详细检查? (y/N): ").strip().lower()
            detailed = detailed_choice in ['y', 'yes', '是']
            
        except KeyboardInterrupt:
            print("\n👋 退出")
            return
        
        # 生成报告
        inspector.generate_report(collection_name, detailed=detailed, output_file=args.output)
        return
    
    # 查找财务指标字段
    if args.financial:
        print(f"🔍 正在查找集合 {args.financial} 中的财务指标字段...")
        financial_result = inspector.find_financial_fields(args.financial)
        
        if 'error' in financial_result:
            print(f"❌ 查找失败: {financial_result['error']}")
            return
        
        print(f"\n📊 财务字段分析结果:")
        print(f"  📄 字段总数: {financial_result['total_fields']}")
        print(f"  💰 财务字段数: {financial_result['financial_fields_count']}")
        
        if financial_result['financial_fields']:
            print(f"\n🏷️  发现的财务指标字段:")
            for field_name, field_info in financial_result['financial_fields'].items():
                print(f"\n  📈 {field_name}")
                print(f"      匹配关键词: {field_info['matched_keyword']}")
                print(f"      数据类型: {field_info['field_type']}")
                print(f"      有数据: {'是' if field_info['has_data'] else '否'}")
                if field_info['sample_values']:
                    sample_str = ', '.join([str(v) for v in field_info['sample_values'][:3]])
                    print(f"      样本值: {sample_str}")
        
        print(f"\n📋 所有字段预览 (前50个):")
        fields_sample = financial_result.get('all_fields_sample', [])
        for i, field in enumerate(fields_sample):
            print(f"  {field}", end="  ")
            if (i + 1) % 5 == 0:
                print()
        
        if args.output:
            try:
                with open(args.output, 'w', encoding='utf-8') as f:
                    json.dump(financial_result, f, ensure_ascii=False, indent=2, default=str)
                print(f"\n💾 结果已保存到: {args.output}")
            except Exception as e:
                print(f"❌ 保存失败: {e}")
        
        return
    
    # 检查指定字段
    if args.fields and args.collection:
        print(f"🔍 正在检查集合 {args.collection} 中的指定字段...")
        field_result = inspector.get_specific_field_info(args.collection, args.fields)
        
        if 'error' in field_result:
            print(f"❌ 检查失败: {field_result['error']}")
            return
        
        print(f"\n📊 字段详细信息:")
        for field_name, field_info in field_result.items():
            print(f"\n🏷️  字段: {field_name}")
            
            if field_info.get('exists', True):
                print(f"    📄 存在记录数: {field_info['exists_count']:,}")
                print(f"    ✅ 有效记录数: {field_info['non_null_count']:,}")
                print(f"    ❌ 空值比例: {field_info['null_percentage']:.1f}%")
                
                print(f"    📝 样本数据:")
                for i, sample in enumerate(field_info['sample_values'][:5], 1):
                    print(f"      {i}. {sample['ts_code']} ({sample['trade_date']}): {sample['value']}")
            else:
                print(f"    ❌ {field_info['message']}")
        
        if args.output:
            try:
                with open(args.output, 'w', encoding='utf-8') as f:
                    json.dump(field_result, f, ensure_ascii=False, indent=2, default=str)
                print(f"\n💾 结果已保存到: {args.output}")
            except Exception as e:
                print(f"❌ 保存失败: {e}")
        
        return
    
    # 检查指定集合
    if args.collection:
        detailed = not args.simple
        inspector.generate_report(args.collection, detailed=detailed, output_file=args.output)
        return
    
    # 如果没有参数，显示帮助
    parser.print_help()


if __name__ == "__main__":
    main()