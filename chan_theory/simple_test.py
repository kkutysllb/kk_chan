#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单测试缠论笔连接优化
针对用户图片中的问题
"""

import sys
import os
import pandas as pd
from datetime import datetime, timedelta

# 添加项目路径
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(os.path.dirname(current_dir))
sys.path.insert(0, backend_dir)

# 重置优化逻辑为简单版本
def test_real_stock_data():
    """使用真实股票数据测试"""
    print("🧪 测试真实股票缠论笔连接优化")
    print("=" * 50)
    
    # 使用缠论引擎分析真实数据
    from analysis.chan_theory.core.chan_theory_engine import ChanTheoryEngine
    from analysis.chan_theory.models.chan_theory_models import ChanTheoryConfig, TrendLevel
    
    # 创建配置 - 使用2025年1月1日以后的数据
    config = ChanTheoryConfig(
        symbol='000001.SZ',
        start_date=datetime(2025, 1, 1),
        end_date=datetime.now(),
        fenxing_strength=0.01,
        min_bi_length=3,
        bi_strength_threshold=0.01,
        min_fenxing_gap=2
    )
    
    print(f"🔧 分析配置: {config.symbol}")
    print(f"📊 分析 daily 级别")
    
    # 创建引擎并分析
    try:
        engine = ChanTheoryEngine(config)
        
        # 使用analyze_complete方法
        result = engine.analyze_complete(
            symbol=config.symbol,
            start_date=config.start_date,
            end_date=config.end_date
        )
        
        if result and 'structure_results' in result:
            structure_results = result['structure_results']
            level_results = structure_results.get('level_results', {})
            
            if TrendLevel.DAILY in level_results:
                daily_result = level_results[TrendLevel.DAILY]
                
                print(f"\n📊 {config.symbol} 日线分析结果:")
                print(f"  顶分型: {len(daily_result.get('fenxing_tops', []))} 个")
                print(f"  底分型: {len(daily_result.get('fenxing_bottoms', []))} 个")  
                print(f"  笔: {len(daily_result.get('bi_list', []))} 条")
                
                # 显示顶分型
                tops = daily_result.get('fenxing_tops', [])
                if tops:
                    print(f"\n🔺 顶分型详情:")
                    for i, top in enumerate(tops):
                        print(f"  {i+1}. 价格: {top.price:.2f}, 时间: {top.timestamp.date()}")
                
                # 显示笔连接
                bi_list = daily_result.get('bi_list', [])
                if bi_list:
                    print(f"\n🔗 笔连接:")
                    for i, bi in enumerate(bi_list):
                        print(f"  {i+1}. {bi.direction.value}: {bi.start_price:.2f} -> {bi.end_price:.2f}")
                
                print(f"\n✅ 分析完成")
                return True
            else:
                print("❌ 没有日线数据")
                
        else:
            print("❌ 分析失败")
            
    except Exception as e:
        print(f"❌ 分析出错: {e}")
        import traceback
        traceback.print_exc()
        
    return False

if __name__ == "__main__":
    print("🚀 简单缠论笔连接优化测试")
    print("📋 目标：使用真实数据验证优化效果")
    print()
    
    success = test_real_stock_data()
    
    print("\n" + "=" * 50)
    if success:
        print("✅ 测试完成")
        print("📝 请检查连续同类型分型是否正确合并")
    else:
        print("❌ 测试失败")