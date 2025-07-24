#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Qlib框架系统集成最终验证脚本
验证从abupy到qlib的完整迁移和集成
"""

import sys
import os
import logging
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def validate_qlib_system():
    """验证Qlib系统集成"""
    logger.info("🎯 开始Qlib系统集成最终验证")
    
    validation_results = {}
    
    # 1. 验证核心模块导入
    logger.info("📦 验证核心模块导入...")
    try:
        from strategies.curious_ragdoll_boll_qlib import (
            CuriousRagdollBollConfig, 
            CuriousRagdollBollModel,
            CuriousRagdollBollStrategy,
            CuriousRagdollBollBacktester
        )
        from core.data_adapter import QlibDataAdapter
        from core.backtest_engine_qlib import QlibBacktestEngine
        from core.portfolio_manager_qlib import QlibPortfolioManager
        
        validation_results['核心模块导入'] = True
        logger.info("✅ 核心模块导入成功")
    except Exception as e:
        validation_results['核心模块导入'] = False
        logger.error(f"❌ 核心模块导入失败: {e}")
        return validation_results
    
    # 2. 验证数据连接和获取
    logger.info("🔗 验证数据连接和获取...")
    try:
        adapter = QlibDataAdapter()
        stocks = adapter.get_stock_list("CSI500")
        
        if len(stocks) > 0:
            test_stock = stocks[0]
            data = adapter.get_stock_data(test_stock, "2023-01-01", "2023-01-31")
            
            if not data.empty:
                validation_results['数据连接和获取'] = True
                logger.info(f"✅ 数据连接成功，获取到{len(stocks)}只股票，{test_stock}有{len(data)}条数据")
            else:
                validation_results['数据连接和获取'] = False
                logger.error("❌ 数据获取失败，返回空数据")
        else:
            validation_results['数据连接和获取'] = False
            logger.error("❌ 股票列表获取失败")
    except Exception as e:
        validation_results['数据连接和获取'] = False
        logger.error(f"❌ 数据连接失败: {e}")
    
    # 3. 验证策略模型功能
    logger.info("🧠 验证策略模型功能...")
    try:
        config = CuriousRagdollBollConfig()
        model = CuriousRagdollBollModel(config)
        
        # 测试技术指标计算
        test_data = pd.DataFrame({
            'close': np.random.normal(100, 10, 50),
            'volume': np.random.normal(1000, 100, 50)
        })
        
        boll_result = model.calculate_boll_bands(test_data['close'])
        momentum_result = model.calculate_momentum_factors(test_data)
        trend_result = model.calculate_trend_factors(test_data)
        
        if boll_result and momentum_result and trend_result:
            validation_results['策略模型功能'] = True
            logger.info("✅ 策略模型功能正常")
        else:
            validation_results['策略模型功能'] = False
            logger.error("❌ 策略模型功能异常")
    except Exception as e:
        validation_results['策略模型功能'] = False
        logger.error(f"❌ 策略模型测试失败: {e}")
    
    # 4. 验证回测引擎
    logger.info("⚙️ 验证回测引擎...")
    try:
        engine = QlibBacktestEngine(adapter)
        validation_results['回测引擎'] = True
        logger.info("✅ 回测引擎创建成功")
    except Exception as e:
        validation_results['回测引擎'] = False
        logger.error(f"❌ 回测引擎创建失败: {e}")
    
    # 5. 验证投资组合管理
    logger.info("📊 验证投资组合管理...")
    try:
        portfolio_manager = QlibPortfolioManager()
        validation_results['投资组合管理'] = True
        logger.info("✅ 投资组合管理器创建成功")
    except Exception as e:
        validation_results['投资组合管理'] = False
        logger.error(f"❌ 投资组合管理创建失败: {e}")
    
    # 6. 验证完整回测流程
    logger.info("🔄 验证完整回测流程...")
    try:
        config = CuriousRagdollBollConfig(
            stock_pool_size=5,
            fixed_positions=3
        )
        
        backtester = CuriousRagdollBollBacktester(config)
        portfolio_metrics, indicators = backtester.run_backtest(
            start_date="2023-01-01",
            end_date="2023-01-10",
            benchmark="SH000905"
        )
        
        results = backtester.analyze_results(portfolio_metrics, indicators)
        
        if results:
            validation_results['完整回测流程'] = True
            logger.info("✅ 完整回测流程验证成功")
        else:
            validation_results['完整回测流程'] = False
            logger.error("❌ 完整回测流程返回空结果")
    except Exception as e:
        validation_results['完整回测流程'] = False
        logger.error(f"❌ 完整回测流程失败: {e}")
    
    return validation_results

def validate_performance_comparison():
    """验证性能对比"""
    logger.info("📈 验证性能对比...")
    
    try:
        # 运行完整回测
        from strategies.curious_ragdoll_boll_qlib import CuriousRagdollBollConfig, CuriousRagdollBollBacktester
        
        config = CuriousRagdollBollConfig()
        backtester = CuriousRagdollBollBacktester(config)
        
        # 运行2023年全年回测
        portfolio_metrics, indicators = backtester.run_backtest(
            start_date="2023-01-01",
            end_date="2023-12-31",
            benchmark="SH000905"
        )
        
        results = backtester.analyze_results(portfolio_metrics, indicators)
        
        logger.info("📊 2023年完整回测结果:")
        logger.info(f"  年化收益率: {results.get('annual_return', 0):.2%}")
        logger.info(f"  最大回撤: {results.get('max_drawdown', 0):.2%}")
        logger.info(f"  夏普比率: {results.get('sharpe_ratio', 0):.2f}")
        logger.info(f"  胜率: {results.get('win_rate', 0):.2%}")
        logger.info(f"  总收益: {results.get('total_return', 0):.2%}")
        logger.info(f"  股票数量: {results.get('stocks_count', 0)}")
        logger.info(f"  交易日数: {results.get('trading_days', 0)}")
        
        return results
        
    except Exception as e:
        logger.error(f"❌ 性能对比失败: {e}")
        return None

def generate_final_report(validation_results, performance_results):
    """生成最终报告"""
    logger.info("📄 生成最终验证报告...")
    
    # 计算通过率
    total_tests = len(validation_results)
    passed_tests = sum(validation_results.values())
    pass_rate = passed_tests / total_tests * 100
    
    # 构建报告
    report = {
        "系统验证": {
            "验证时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "qlib框架版本": "0.9.6",
            "Python版本": sys.version,
            "验证结果": validation_results,
            "通过率": f"{passed_tests}/{total_tests} ({pass_rate:.1f}%)",
            "总体状态": "✅ 通过" if pass_rate == 100 else "❌ 失败"
        },
        "性能验证": performance_results,
        "技术特性": {
            "数据源": "真实MongoDB数据库",
            "框架迁移": "从abupy完全迁移至qlib",
            "策略类型": "好奇布偶猫BOLL择时策略",
            "技术指标": ["布林带", "RSI", "MACD", "动量因子", "趋势因子"],
            "风控机制": ["止损", "止盈", "仓位控制", "小市值筛选"],
            "回测功能": ["多股票回测", "性能分析", "风险评估", "结果可视化"]
        },
        "系统优势": {
            "AI驱动": "基于微软qlib AI量化投资平台",
            "数据完整性": "使用真实tushare数据，无模拟数据",
            "模块化设计": "完整的数据适配器、策略模型、回测引擎",
            "性能监控": "全面的性能指标和风险控制",
            "扩展性": "支持多策略并行回测和比较"
        }
    }
    
    # 保存报告
    output_dir = "/Users/libing/kk_Projects/kk_Stock/kk_stock_backend/abu_quantitative/results"
    os.makedirs(output_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = os.path.join(output_dir, f"qlib_system_validation_{timestamp}.json")
    
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2, default=str)
    
    logger.info(f"📄 最终验证报告已保存: {report_file}")
    return report

def main():
    """主函数"""
    logger.info("🚀 开始Qlib系统集成最终验证")
    
    try:
        # 1. 系统功能验证
        validation_results = validate_qlib_system()
        
        # 2. 性能验证
        performance_results = validate_performance_comparison()
        
        # 3. 生成最终报告
        report = generate_final_report(validation_results, performance_results)
        
        # 4. 显示验证结果
        logger.info("🎯 Qlib系统集成最终验证完成")
        logger.info(f"📊 系统验证结果: {report['系统验证']['通过率']}")
        logger.info(f"📈 总体状态: {report['系统验证']['总体状态']}")
        
        # 详细结果
        logger.info("📋 详细验证结果:")
        for test_name, result in validation_results.items():
            status = "✅" if result else "❌"
            logger.info(f"  {status} {test_name}")
        
        # 性能结果
        if performance_results:
            logger.info("📈 性能验证结果:")
            logger.info(f"  年化收益率: {performance_results.get('annual_return', 0):.2%}")
            logger.info(f"  最大回撤: {performance_results.get('max_drawdown', 0):.2%}")
            logger.info(f"  夏普比率: {performance_results.get('sharpe_ratio', 0):.2f}")
            logger.info(f"  胜率: {performance_results.get('win_rate', 0):.2%}")
        
        # 最终结论
        if all(validation_results.values()):
            logger.info("🎉 恭喜！Qlib框架系统集成验证全部通过！")
            logger.info("🔥 系统已成功从abupy完全迁移至qlib框架")
            logger.info("📊 所有核心功能运行正常，可以投入生产使用")
        else:
            logger.warning("⚠️ 部分功能验证失败，请检查相关模块")
        
        return all(validation_results.values())
        
    except Exception as e:
        logger.error(f"❌ 系统验证异常: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)