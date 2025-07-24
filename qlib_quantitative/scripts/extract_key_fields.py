#!/usr/bin/env python3
"""
提取stock_factor_pro集合中的关键情绪和趋势字段
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.db_handler import get_db_handler
import json


def extract_key_fields():
    """提取关键的情绪和趋势字段"""
    print("🔍 提取stock_factor_pro集合中的关键字段...")
    
    try:
        # 获取数据库连接
        db_handler = get_db_handler()
        collection = db_handler.get_collection('stock_factor_pro')
        
        # 获取一个样本记录
        sample_record = collection.find_one({})
        if not sample_record:
            print("❌ 没有找到样本记录")
            return
        
        all_fields = list(sample_record.keys())
        
        # 定义字段分类
        field_categories = {
            '情绪指标': {
                'keywords': ['sentiment', 'emotion', 'fear', 'greed', 'panic', 'vix', 'confidence', 'mood'],
                'fields': []
            },
            '资金流向': {
                'keywords': ['flow', 'money', 'fund', 'capital', 'net', 'inflow', 'outflow', 'volume', 'turnover', 'amount'],
                'fields': []
            },
            '布林带指标': {
                'keywords': ['boll'],
                'fields': []
            },
            'MACD指标': {
                'keywords': ['macd'],
                'fields': []
            },
            'RSI指标': {
                'keywords': ['rsi'],
                'fields': []
            },
            'KDJ指标': {
                'keywords': ['kdj'],
                'fields': []
            },
            'CCI指标': {
                'keywords': ['cci'],
                'fields': []
            },
            '移动平均线': {
                'keywords': ['ma_', 'ema_', 'sma_', 'expma'],
                'fields': []
            },
            '乖离率': {
                'keywords': ['bias'],
                'fields': []
            },
            '动量指标': {
                'keywords': ['mtm', 'momentum', 'roc', 'maroc'],
                'fields': []
            },
            '成交量指标': {
                'keywords': ['obv', 'emv', 'mfi', 'vol'],
                'fields': []
            },
            '波动率指标': {
                'keywords': ['atr', 'volatility', 'mass'],
                'fields': []
            },
            '趋势指标': {
                'keywords': ['dmi', 'adx', 'trend', 'direction', 'slope'],
                'fields': []
            },
            '心理线指标': {
                'keywords': ['psy'],
                'fields': []
            },
            '其他技术指标': {
                'keywords': ['asi', 'cr', 'wr', 'trix', 'dpo', 'bbi'],
                'fields': []
            }
        }
        
        # 基础价格和市值字段
        basic_fields = {
            '基础价格数据': [
                'ts_code', 'trade_date', 'open', 'high', 'low', 'close', 'pre_close',
                'change', 'pct_chg', 'vol', 'amount'
            ],
            '市值估值数据': [
                'total_share', 'float_share', 'free_share', 'total_mv', 'circ_mv',
                'pe', 'pe_ttm', 'pb', 'ps', 'ps_ttm', 'dv_ratio', 'dv_ttm'
            ],
            '换手率数据': [
                'turnover_rate', 'turnover_rate_f', 'volume_ratio'
            ]
        }
        
        # 分类字段
        for field in all_fields:
            if field == '_id':
                continue
                
            field_lower = field.lower()
            
            # 检查每个类别
            for category, info in field_categories.items():
                if any(keyword in field_lower for keyword in info['keywords']):
                    info['fields'].append(field)
                    break
        
        # 输出结果
        print("\n📊 stock_factor_pro 集合字段分析报告")
        print("=" * 80)
        print(f"总字段数: {len(all_fields)}")
        
        # 输出基础字段
        print("\n📋 基础数据字段:")
        print("-" * 50)
        for category, fields in basic_fields.items():
            print(f"\n{category}:")
            existing_fields = [f for f in fields if f in all_fields]
            for field in existing_fields:
                sample_val = sample_record.get(field, 'N/A')
                print(f"  {field:<25} | 示例: {sample_val}")
        
        # 输出技术指标字段
        print("\n📈 技术指标字段:")
        print("-" * 50)
        
        total_tech_fields = 0
        for category, info in field_categories.items():
            if info['fields']:
                print(f"\n{category} ({len(info['fields'])}个):")
                total_tech_fields += len(info['fields'])
                
                # 只显示前5个字段示例，避免输出过长
                display_fields = info['fields'][:5]
                for field in display_fields:
                    sample_val = sample_record.get(field, 'N/A')
                    print(f"  {field:<25} | 示例: {sample_val}")
                
                if len(info['fields']) > 5:
                    print(f"  ... 还有 {len(info['fields']) - 5} 个字段")
        
        print(f"\n技术指标字段总数: {total_tech_fields}")
        
        # 重点情绪和趋势相关字段详细说明
        print("\n🎯 重点情绪和趋势相关字段详细说明:")
        print("=" * 80)
        
        key_field_descriptions = {
            # 情绪和市场情绪相关
            'turnover_rate': '换手率 - 反映市场活跃度和投资者情绪',
            'turnover_rate_f': '自由流通股换手率 - 更准确的市场活跃度指标',
            'volume_ratio': '量比 - 当日成交量与平均成交量的比值，反映资金关注度',
            
            # 布林带指标 - 趋势和波动
            'boll_upper_qfq': '布林带上轨 - 压力位，突破表示强势上涨',
            'boll_mid_qfq': '布林带中轨 - 移动平均线，趋势方向参考',
            'boll_lower_qfq': '布林带下轨 - 支撑位，跌破表示弱势下跌',
            
            # MACD指标 - 趋势跟踪
            'macd_dif_qfq': 'MACD DIF线 - 快慢均线差值，反映短期趋势',
            'macd_dea_qfq': 'MACD DEA线 - DIF的平滑移动平均，信号线',
            'macd_qfq': 'MACD柱状图 - DIF与DEA的差值，动量变化',
            
            # RSI指标 - 超买超卖
            'rsi_qfq_6': 'RSI6日 - 相对强弱指数，>70超买，<30超卖',
            'rsi_qfq_12': 'RSI12日 - 中期相对强弱指数',
            'rsi_qfq_24': 'RSI24日 - 长期相对强弱指数',
            
            # KDJ指标 - 随机指标
            'kdj_k_qfq': 'KDJ K值 - 快速随机指标',
            'kdj_d_qfq': 'KDJ D值 - 慢速随机指标',
            'kdj_qfq': 'KDJ J值 - 超前指标，反映极端情况',
            
            # 移动平均线 - 趋势
            'ma_qfq_5': '5日移动平均线 - 短期趋势',
            'ma_qfq_10': '10日移动平均线 - 短期趋势',
            'ma_qfq_20': '20日移动平均线 - 中期趋势',
            'ma_qfq_60': '60日移动平均线 - 中长期趋势',
            
            # 乖离率 - 偏离程度
            'bias1_qfq': '6日乖离率 - 价格与短期均线的偏离程度',
            'bias2_qfq': '12日乖离率 - 价格与中期均线的偏离程度',
            'bias3_qfq': '24日乖离率 - 价格与长期均线的偏离程度',
            
            # 动量指标
            'mtm_qfq': '动量指标 - 价格变化速度',
            'maroc_qfq': '变化率指标 - 价格变化幅度',
            
            # 成交量指标
            'obv_qfq': 'OBV能量潮 - 成交量与价格关系，资金流向',
            'mfi_qfq': '资金流量指数 - 结合价格和成交量的强度指标',
            
            # 波动率指标
            'atr_qfq': '真实波动幅度 - 衡量价格波动程度',
            'mass_qfq': '佳庆指标 - 价格波动的质量',
            
            # 心理线
            'psy_qfq': '心理线 - 投资者心理预期和情绪指标'
        }
        
        # 输出重点字段说明
        for field, description in key_field_descriptions.items():
            if field in all_fields:
                sample_val = sample_record.get(field, 'N/A')
                print(f"{field:<20} | {description}")
                print(f"{'':>20} | 示例值: {sample_val}")
                print()
        
        # 生成简化的分析报告
        report = {
            'summary': {
                'total_fields': len(all_fields),
                'technical_indicator_fields': total_tech_fields,
                'analysis_date': str(sample_record.get('trade_date', 'unknown'))
            },
            'field_categories': {}
        }
        
        # 添加分类统计
        for category, info in field_categories.items():
            if info['fields']:
                report['field_categories'][category] = {
                    'count': len(info['fields']),
                    'fields': info['fields'][:10]  # 只保存前10个字段
                }
        
        # 保存简化报告
        output_file = "/home/libing/kk_Projects/kk_stock/kk_stock_backend/quantitative/key_fields_summary.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"💾 关键字段汇总已保存到: {output_file}")
        
        return report
        
    except Exception as e:
        print(f"❌ 提取过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    print("📊 股票因子关键字段提取工具")
    print("=" * 60)
    
    result = extract_key_fields()
    
    if result:
        print("\n✅ 提取完成！")
        print("\n📋 主要发现:")
        print(f"  - 数据库包含丰富的技术指标，共 {result['summary']['technical_indicator_fields']} 个技术指标字段")
        print(f"  - 涵盖了主流的技术分析指标：MACD、RSI、KDJ、布林带、移动平均线等")
        print(f"  - 包含三种复权方式的数据：前复权(qfq)、后复权(hfq)、不复权(bfq)")
        print(f"  - 提供了丰富的市场情绪和资金流向指标")
    else:
        print("❌ 提取失败")