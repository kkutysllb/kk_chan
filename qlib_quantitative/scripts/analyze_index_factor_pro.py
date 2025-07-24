#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
分析index_factor_pro集合的字段结构
用于市场环境判断的技术指标分析
"""

import sys
import os
from pprint import pprint
from collections import defaultdict
import json

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from api.db_handler import get_db_handler


def analyze_index_factor_pro():
    """分析index_factor_pro集合的字段结构"""
    
    print("=" * 80)
    print("📊 index_factor_pro集合字段结构分析")
    print("=" * 80)
    
    try:
        # 获取数据库连接
        db_handler = get_db_handler()
        collection = db_handler.get_collection('index_factor_pro')
        
        # 1. 获取集合基本信息
        print("\n🔍 1. 集合基本信息")
        print("-" * 50)
        total_count = collection.count_documents({})
        print(f"总记录数: {total_count:,}")
        
        # 获取最早和最晚的数据
        earliest = collection.find().sort('trade_date', 1).limit(1)
        latest = collection.find().sort('trade_date', -1).limit(1)
        
        earliest_doc = list(earliest)[0] if earliest else None
        latest_doc = list(latest)[0] if latest else None
        
        if earliest_doc and latest_doc:
            print(f"最早日期: {earliest_doc.get('trade_date', 'N/A')}")
            print(f"最晚日期: {latest_doc.get('trade_date', 'N/A')}")
        
        # 2. 获取样本记录查看所有字段
        print("\n📋 2. 样本记录字段结构")
        print("-" * 50)
        sample_doc = collection.find_one()
        
        if not sample_doc:
            print("❌ 集合中没有数据")
            return
        
        print("样本记录的所有字段:")
        all_fields = list(sample_doc.keys())
        for i, field in enumerate(all_fields, 1):
            field_value = sample_doc[field]
            field_type = type(field_value).__name__
            print(f"{i:2d}. {field:<25} ({field_type:<10}) = {field_value}")
        
        # 3. 技术指标字段分类
        print("\n🎯 3. 技术指标字段分类")
        print("-" * 50)
        
        # 定义技术指标分类
        indicator_categories = {
            'trend_indicators': {
                'name': '趋势指标',
                'description': '用于判断市场趋势方向和强度',
                'fields': []
            },
            'momentum_indicators': {
                'name': '动量指标',
                'description': '用于判断市场动量和超买超卖状态',
                'fields': []
            },
            'volatility_indicators': {
                'name': '波动率指标',
                'description': '用于衡量市场波动性和风险水平',
                'fields': []
            },
            'volume_indicators': {
                'name': '成交量指标',
                'description': '用于分析资金流向和市场参与度',
                'fields': []
            },
            'sentiment_indicators': {
                'name': '情绪指标',
                'description': '用于衡量市场情绪和投资者心理',
                'fields': []
            },
            'breadth_indicators': {
                'name': '市场宽度指标',
                'description': '用于衡量市场整体参与度和广度',
                'fields': []
            },
            'basic_info': {
                'name': '基础信息',
                'description': '日期、代码等基础字段',
                'fields': []
            }
        }
        
        # 字段分类规则
        field_classification = {
            # 基础信息
            'ts_code': 'basic_info',
            'trade_date': 'basic_info',
            'ann_date': 'basic_info',
            
            # 趋势指标
            'ma5': 'trend_indicators',
            'ma10': 'trend_indicators', 
            'ma20': 'trend_indicators',
            'ma30': 'trend_indicators',
            'ma60': 'trend_indicators',
            'ma120': 'trend_indicators',
            'ma250': 'trend_indicators',
            'ema12': 'trend_indicators',
            'ema26': 'trend_indicators',
            'macd': 'trend_indicators',
            'macd_signal': 'trend_indicators',
            'macd_hist': 'trend_indicators',
            'boll_upper': 'trend_indicators',
            'boll_mid': 'trend_indicators',
            'boll_lower': 'trend_indicators',
            'sar': 'trend_indicators',
            'adx': 'trend_indicators',
            'plus_di': 'trend_indicators',
            'minus_di': 'trend_indicators',
            'cci': 'trend_indicators',
            'aroon_up': 'trend_indicators',
            'aroon_down': 'trend_indicators',
            'aroon_osc': 'trend_indicators',
            
            # 动量指标
            'rsi6': 'momentum_indicators',
            'rsi12': 'momentum_indicators',
            'rsi24': 'momentum_indicators',
            'stoch_k': 'momentum_indicators',
            'stoch_d': 'momentum_indicators',
            'williams_r': 'momentum_indicators',
            'roc': 'momentum_indicators',
            'momentum': 'momentum_indicators',
            'ultimate_osc': 'momentum_indicators',
            
            # 波动率指标
            'atr': 'volatility_indicators',
            'boll_width': 'volatility_indicators',
            'std_dev': 'volatility_indicators',
            'vr': 'volatility_indicators',
            'tr': 'volatility_indicators',
            
            # 成交量指标
            'obv': 'volume_indicators',
            'ad_line': 'volume_indicators',
            'cmf': 'volume_indicators',
            'mfi': 'volume_indicators',
            'vol_ma5': 'volume_indicators',
            'vol_ma10': 'volume_indicators',
            'vol_ma20': 'volume_indicators',
            'vol_ratio': 'volume_indicators',
            'vwap': 'volume_indicators',
            'pvt': 'volume_indicators',
            'fi': 'volume_indicators',
            'nvi': 'volume_indicators',
            'pvi': 'volume_indicators',
            
            # 情绪指标
            'vix': 'sentiment_indicators',
            'put_call_ratio': 'sentiment_indicators',
            'fear_greed': 'sentiment_indicators',
            'sentiment_score': 'sentiment_indicators',
            
            # 市场宽度指标
            'advance_decline': 'breadth_indicators',
            'new_high_low': 'breadth_indicators',
            'up_down_ratio': 'breadth_indicators',
            'market_breadth': 'breadth_indicators',
        }
        
        # 对字段进行分类
        unclassified_fields = []
        
        for field in all_fields:
            if field == '_id':  # 跳过MongoDB的_id字段
                continue
                
            classified = False
            
            # 精确匹配
            if field in field_classification:
                category = field_classification[field]
                indicator_categories[category]['fields'].append(field)
                classified = True
            else:
                # 模糊匹配
                field_lower = field.lower()
                
                # 去除_bfq后缀进行匹配
                field_base = field_lower.replace('_bfq', '')
                
                # 趋势指标模糊匹配
                if any(keyword in field_base for keyword in ['ma_', 'ema_', 'sma_', 'macd', 'boll', 'sar', 'adx', 'dmi', 'cci', 'aroon', 'ichimoku', 'supertrend', 'expma', 'dfma', 'bias', 'dpo', 'trix', 'bbis', 'ktn']):
                    indicator_categories['trend_indicators']['fields'].append(field)
                    classified = True
                # 动量指标模糊匹配
                elif any(keyword in field_base for keyword in ['rsi', 'stoch', 'kdj', 'williams', 'roc', 'momentum', 'ultimate', 'wr', 'mtm', 'psy']):
                    indicator_categories['momentum_indicators']['fields'].append(field)
                    classified = True
                # 波动率指标模糊匹配
                elif any(keyword in field_base for keyword in ['atr', 'volatility', 'std', 'var', 'width', 'range', 'mass', 'asi', 'asit']):
                    indicator_categories['volatility_indicators']['fields'].append(field)
                    classified = True
                # 成交量指标模糊匹配
                elif any(keyword in field_base for keyword in ['vol', 'obv', 'ad', 'cmf', 'mfi', 'vwap', 'pvt', 'fi', 'nvi', 'pvi', 'vr', 'emv', 'amount']):
                    indicator_categories['volume_indicators']['fields'].append(field)
                    classified = True
                # 情绪指标模糊匹配
                elif any(keyword in field_base for keyword in ['vix', 'sentiment', 'fear', 'greed', 'put_call', 'brar', 'cr']):
                    indicator_categories['sentiment_indicators']['fields'].append(field)
                    classified = True
                # 市场宽度指标模糊匹配
                elif any(keyword in field_base for keyword in ['advance', 'decline', 'breadth', 'high_low', 'up_down', 'updays', 'downdays', 'topdays', 'lowdays']):
                    indicator_categories['breadth_indicators']['fields'].append(field)
                    classified = True
                # 价格数据
                elif any(keyword in field_base for keyword in ['open', 'close', 'high', 'low', 'change', 'pct_change', 'pre_close', 'xsii', 'taq']):
                    indicator_categories['basic_info']['fields'].append(field)
                    classified = True
                # 基础信息模糊匹配
                elif any(keyword in field_lower for keyword in ['date', 'code', 'id', 'name', 'symbol']):
                    indicator_categories['basic_info']['fields'].append(field)
                    classified = True
            
            if not classified:
                unclassified_fields.append(field)
        
        # 显示分类结果
        for category_key, category_info in indicator_categories.items():
            if category_info['fields']:
                print(f"\n🔹 {category_info['name']} ({len(category_info['fields'])}个字段)")
                print(f"   描述: {category_info['description']}")
                print("   字段:")
                for field in sorted(category_info['fields']):
                    field_value = sample_doc.get(field, 'N/A')
                    print(f"     • {field:<25} = {field_value}")
        
        # 显示未分类字段
        if unclassified_fields:
            print(f"\n❓ 未分类字段 ({len(unclassified_fields)}个)")
            for field in sorted(unclassified_fields):
                field_value = sample_doc.get(field, 'N/A')
                print(f"     • {field:<25} = {field_value}")
        
        # 4. 市场环境判断建议
        print("\n💡 4. 市场环境判断可用的技术因子建议")
        print("-" * 50)
        
        market_env_suggestions = {
            "趋势判断": {
                "推荐指标": ["ma20", "ma60", "macd", "macd_signal", "adx", "boll_upper", "boll_lower"],
                "用途": "判断市场整体趋势方向，确定牛市、熊市或震荡市",
                "策略": "多周期均线排列，MACD金叉死叉，ADX趋势强度，布林带位置"
            },
            "波动率环境": {
                "推荐指标": ["atr", "boll_width", "std_dev", "vr"],
                "用途": "衡量市场波动性水平，识别高波动和低波动环境",
                "策略": "ATR相对位置，布林带宽度，标准差变化"
            },
            "市场情绪": {
                "推荐指标": ["rsi6", "rsi12", "williams_r", "stoch_k", "cci"],
                "用途": "判断市场超买超卖状态，识别情绪极端点",
                "策略": "RSI极值区域，威廉指标反转信号，随机指标背离"
            },
            "资金流向": {
                "推荐指标": ["obv", "cmf", "mfi", "vol_ratio", "ad_line"],
                "用途": "分析资金进出情况，判断市场参与度",
                "策略": "OBV趋势，资金流量指标，成交量比率"
            },
            "动量强度": {
                "推荐指标": ["roc", "momentum", "aroon_up", "aroon_down"],
                "用途": "衡量价格变化速度，识别加速和减速阶段",
                "策略": "变化率指标，动量指标，阿隆指标"
            }
        }
        
        for env_type, info in market_env_suggestions.items():
            print(f"\n🎯 {env_type}")
            print(f"   推荐指标: {', '.join(info['推荐指标'])}")
            print(f"   用途: {info['用途']}")
            print(f"   策略: {info['策略']}")
        
        # 5. 多条样本数据展示
        print("\n📊 5. 多条样本数据展示")
        print("-" * 50)
        
        # 获取最新的5条记录
        recent_docs = list(collection.find().sort('trade_date', -1).limit(5))
        
        if recent_docs:
            print("最新5条记录的关键指标:")
            key_fields = ['trade_date', 'ts_code', 'ma_bfq_20', 'rsi_bfq_12', 'macd_bfq', 'atr_bfq', 'vr_bfq']
            
            # 打印表头
            header = " | ".join([f"{field:<12}" for field in key_fields])
            print(f"   {header}")
            print(f"   {'-' * len(header)}")
            
            # 打印数据
            for doc in recent_docs:
                row_data = []
                for field in key_fields:
                    value = doc.get(field, 'N/A')
                    if isinstance(value, (int, float)):
                        row_data.append(f"{value:<12.4f}")
                    else:
                        row_data.append(f"{str(value):<12}")
                
                row = " | ".join(row_data)
                print(f"   {row}")
        
        # 6. 数据质量检查
        print("\n🔍 6. 数据质量检查")
        print("-" * 50)
        
        # 检查关键字段的非空率 - 使用实际存在的字段名
        key_indicators = ['ma_bfq_20', 'rsi_bfq_12', 'macd_bfq', 'atr_bfq', 'vr_bfq']
        sample_size = min(1000, total_count)  # 取样检查
        
        sample_docs = list(collection.find().limit(sample_size))
        
        print(f"基于{sample_size}条记录的数据质量检查:")
        for field in key_indicators:
            non_null_count = sum(1 for doc in sample_docs if doc.get(field) is not None)
            completeness = (non_null_count / sample_size) * 100
            print(f"   {field:<15}: {completeness:6.2f}% 完整度 ({non_null_count}/{sample_size})")
        
        print("\n✅ 分析完成！")
        print("💡 建议使用上述技术指标组合来构建市场环境判断模型")
        
    except Exception as e:
        print(f"❌ 分析过程中出现错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    analyze_index_factor_pro()