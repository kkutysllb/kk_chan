#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
每日全市场缠论选股脚本
用于每日从全市场中筛选买入和卖出目标，为调仓换股提供决策依据

运行方式：
python daily_stock_selection.py

输出：
1. 买入候选股票列表（按评分排序）
2. 卖出候选股票列表（按评分排序）
3. 每日选股报告文件
"""

import sys
import os
import json
import csv
from datetime import datetime, timedelta
from typing import List, Dict, Any
import logging

# 添加项目路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from chan_theory_v2.strategies.backchi_stock_selector import BackchiStockSelector, SignalStrength

# 配置日志
def setup_logging():
    """设置日志配置"""
    log_dir = os.path.join(current_dir, "logs")
    os.makedirs(log_dir, exist_ok=True)
    
    today = datetime.now().strftime("%Y%m%d")
    log_file = os.path.join(log_dir, f"daily_selection_{today}.log")
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(log_file, encoding='utf-8')
        ]
    )
    return logging.getLogger(__name__)

class DailyStockSelector:
    """每日股票选择器"""
    
    def __init__(self):
        """初始化"""
        self.logger = setup_logging()
        self.selector = BackchiStockSelector()
        self.results_dir = os.path.join(current_dir, "selection_results")
        os.makedirs(self.results_dir, exist_ok=True)
        
        self.logger.info("🚀 每日选股系统启动")
        self.logger.info(f"📁 结果保存目录: {self.results_dir}")
    
    def run_daily_selection(self) -> Dict[str, Any]:
        """执行每日选股"""
        self.logger.info("="*60)
        self.logger.info("🎯 开始每日全市场选股分析")
        self.logger.info("="*60)
        
        start_time = datetime.now()
        
        try:
            # 执行全市场选股
            all_signals = self.selector.run_stock_selection(max_results=200)  # 获取更多结果用于分类
            
            # 分类整理结果
            buy_signals = [s for s in all_signals if s.signal_type == "买入"]
            sell_signals = [s for s in all_signals if s.signal_type == "卖出"]
            
            # 按强度和评分进一步筛选
            strong_buy_signals = [s for s in buy_signals if s.signal_strength in [SignalStrength.STRONG, SignalStrength.MEDIUM]]
            strong_sell_signals = [s for s in sell_signals if s.signal_strength in [SignalStrength.STRONG, SignalStrength.MEDIUM]]
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            # 整理结果
            results = {
                'analysis_date': start_time.strftime("%Y-%m-%d"),
                'analysis_time': start_time.strftime("%Y-%m-%d %H:%M:%S"),
                'duration_seconds': duration,
                'total_signals': len(all_signals),
                'buy_signals': {
                    'all': buy_signals,
                    'strong': strong_buy_signals,
                    'count': len(buy_signals),
                    'strong_count': len(strong_buy_signals)
                },
                'sell_signals': {
                    'all': sell_signals,
                    'strong': strong_sell_signals,
                    'count': len(sell_signals),
                    'strong_count': len(strong_sell_signals)
                }
            }
            
            self.logger.info(f"⏱️ 选股完成，耗时: {duration:.1f}秒")
            self.logger.info(f"📊 选股结果: 买入{len(buy_signals)}个 (强信号{len(strong_buy_signals)}个), 卖出{len(sell_signals)}个 (强信号{len(strong_sell_signals)}个)")
            
            return results
            
        except Exception as e:
            self.logger.error(f"❌ 每日选股失败: {e}", exc_info=True)
            return {}
    
    def save_results(self, results: Dict[str, Any]) -> None:
        """保存选股结果"""
        if not results:
            return
        
        today = results['analysis_date'].replace('-', '')
        
        # 保存JSON格式详细结果
        json_file = os.path.join(self.results_dir, f"selection_{today}.json")
        self._save_json_results(results, json_file)
        
        # 保存CSV格式简化结果
        csv_file = os.path.join(self.results_dir, f"selection_{today}.csv")
        self._save_csv_results(results, csv_file)
        
        # 保存可读的文本报告
        report_file = os.path.join(self.results_dir, f"report_{today}.txt")
        self._save_text_report(results, report_file)
        
        self.logger.info(f"💾 结果已保存:")
        self.logger.info(f"  📄 详细数据: {json_file}")
        self.logger.info(f"  📊 CSV表格: {csv_file}")
        self.logger.info(f"  📝 文本报告: {report_file}")
    
    def _save_json_results(self, results: Dict[str, Any], file_path: str) -> None:
        """保存JSON格式结果"""
        # 转换StockSignal对象为字典
        json_data = {
            'analysis_date': results['analysis_date'],
            'analysis_time': results['analysis_time'],
            'duration_seconds': results['duration_seconds'],
            'summary': {
                'total_signals': results['total_signals'],
                'buy_count': results['buy_signals']['count'],
                'buy_strong_count': results['buy_signals']['strong_count'],
                'sell_count': results['sell_signals']['count'],
                'sell_strong_count': results['sell_signals']['strong_count']
            },
            'buy_signals': [self._signal_to_dict(s) for s in results['buy_signals']['all']],
            'sell_signals': [self._signal_to_dict(s) for s in results['sell_signals']['all']]
        }
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, ensure_ascii=False, indent=2)
    
    def _save_csv_results(self, results: Dict[str, Any], file_path: str) -> None:
        """保存CSV格式结果"""
        with open(file_path, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            
            # 写入表头
            writer.writerow([
                '股票代码', '股票名称', '信号类型', '综合评分', '信号强度', 
                '投资建议', '背驰类型', '背驰强度', 'MACD金叉', 
                '入场价', '止损价', '止盈价', '分析时间'
            ])
            
            # 写入买入信号
            for signal in results['buy_signals']['all']:
                writer.writerow([
                    signal.symbol, signal.name, signal.signal_type,
                    f"{signal.overall_score:.1f}", signal.signal_strength.value,
                    signal.recommendation, getattr(signal, 'backchi_type', ''),
                    f"{getattr(signal, 'reliability', 0.0):.3f}",
                    "是" if getattr(signal, 'has_macd_golden_cross', False) else "否",
                    f"{signal.entry_price:.2f}" if signal.entry_price else "",
                    f"{signal.stop_loss:.2f}" if signal.stop_loss else "",
                    f"{signal.take_profit:.2f}" if signal.take_profit else "",
                    signal.analysis_time.strftime('%Y-%m-%d %H:%M:%S')
                ])
            
            # 写入卖出信号
            for signal in results['sell_signals']['all']:
                writer.writerow([
                    signal.symbol, signal.name, signal.signal_type,
                    f"{signal.overall_score:.1f}", signal.signal_strength.value,
                    signal.recommendation, getattr(signal, 'backchi_type', ''),
                    f"{getattr(signal, 'reliability', 0.0):.3f}",
                    "否",  # 卖出信号不考虑MACD金叉
                    f"{signal.entry_price:.2f}" if signal.entry_price else "",
                    f"{signal.stop_loss:.2f}" if signal.stop_loss else "",
                    f"{signal.take_profit:.2f}" if signal.take_profit else "",
                    signal.analysis_time.strftime('%Y-%m-%d %H:%M:%S')
                ])
    
    def _save_text_report(self, results: Dict[str, Any], file_path: str) -> None:
        """保存文本报告"""
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write("🎯 每日缠论选股报告\n")
            f.write("="*60 + "\n\n")
            
            f.write(f"📅 分析日期: {results['analysis_date']}\n")
            f.write(f"⏰ 分析时间: {results['analysis_time']}\n")
            f.write(f"⏱️ 分析耗时: {results['duration_seconds']:.1f}秒\n\n")
            
            # 汇总统计
            f.write("📊 选股汇总\n")
            f.write("-" * 30 + "\n")
            f.write(f"总信号数量: {results['total_signals']}\n")
            f.write(f"买入信号: {results['buy_signals']['count']}个 (强信号: {results['buy_signals']['strong_count']}个)\n")
            f.write(f"卖出信号: {results['sell_signals']['count']}个 (强信号: {results['sell_signals']['strong_count']}个)\n\n")
            
            # 买入推荐
            if results['buy_signals']['strong']:
                f.write("🟢 强烈推荐买入 (调仓目标)\n")
                f.write("-" * 40 + "\n")
                for i, signal in enumerate(results['buy_signals']['strong'][:10], 1):
                    f.write(f"{i:2d}. {signal.symbol} {signal.name}\n")
                    f.write(f"    评分: {signal.overall_score:.1f} | 强度: {signal.signal_strength.value}\n")
                    f.write(f"    建议: {signal.recommendation}\n")
                    f.write(f"    背驰强度: {getattr(signal, 'reliability', 0.0):.3f}\n")
                    if signal.entry_price:
                        f.write(f"    入场价: {signal.entry_price:.2f} | 止损: {signal.stop_loss:.2f} | 止盈: {signal.take_profit:.2f}\n")
                    f.write("\n")
            
            # 卖出推荐  
            if results['sell_signals']['strong']:
                f.write("🔴 强烈推荐卖出 (减仓目标)\n")
                f.write("-" * 40 + "\n")
                for i, signal in enumerate(results['sell_signals']['strong'][:10], 1):
                    f.write(f"{i:2d}. {signal.symbol} {signal.name}\n")
                    f.write(f"    评分: {signal.overall_score:.1f} | 强度: {signal.signal_strength.value}\n")
                    f.write(f"    建议: {signal.recommendation}\n")
                    f.write(f"    背驰强度: {getattr(signal, 'reliability', 0.0):.3f}\n")
                    if signal.entry_price:
                        f.write(f"    入场价: {signal.entry_price:.2f} | 止损: {signal.stop_loss:.2f} | 止盈: {signal.take_profit:.2f}\n")
                    f.write("\n")
            
            # 操作建议
            f.write("💡 操作建议\n")
            f.write("-" * 20 + "\n")
            f.write("1. 调仓换股:\n")
            f.write("   - 重点关注强烈推荐买入的股票作为新增仓位\n")
            f.write("   - 优先卖出强烈推荐卖出的持仓股票\n")
            f.write("   - 建议分批建仓/减仓，控制风险\n\n")
            f.write("2. 风险控制:\n")
            f.write("   - 严格按照止损价执行止损\n")
            f.write("   - 单只股票仓位控制在合理范围\n")
            f.write("   - 密切关注市场整体走势\n\n")
            
            f.write("📝 备注: 本报告基于缠论30分钟级别背驰分析生成，仅供参考，投资需谨慎。\n")
    
    def _signal_to_dict(self, signal) -> Dict[str, Any]:
        """将StockSignal对象转换为字典"""
        return {
            'symbol': signal.symbol,
            'name': signal.name,
            'signal_type': signal.signal_type,
            'overall_score': signal.overall_score,
            'signal_strength': signal.signal_strength.value,
            'recommendation': signal.recommendation,
            'backchi_type': getattr(signal, 'backchi_type', None),
            'reliability': getattr(signal, 'reliability', 0.0),
            'description': getattr(signal, 'description', ''),
            'has_macd_golden_cross': getattr(signal, 'has_macd_golden_cross', False),
            'has_macd_death_cross': getattr(signal, 'has_macd_death_cross', False),
            'entry_price': signal.entry_price,
            'stop_loss': signal.stop_loss,
            'take_profit': signal.take_profit,
            'analysis_time': signal.analysis_time.isoformat()
        }
    
    def print_summary(self, results: Dict[str, Any]) -> None:
        """打印选股摘要"""
        if not results:
            print("❌ 没有选股结果可显示")
            return
        
        print("\n" + "="*60)
        print("📈 每日选股摘要")
        print("="*60)
        print(f"📅 分析日期: {results['analysis_date']}")
        print(f"⏱️ 分析耗时: {results['duration_seconds']:.1f}秒")
        print()
        
        print("📊 选股统计:")
        print(f"  • 总信号: {results['total_signals']}个")
        print(f"  • 买入信号: {results['buy_signals']['count']}个 (强信号: {results['buy_signals']['strong_count']}个)")
        print(f"  • 卖出信号: {results['sell_signals']['count']}个 (强信号: {results['sell_signals']['strong_count']}个)")
        print()
        
        # 显示强买入信号前5名
        if results['buy_signals']['strong']:
            print("🟢 强买入信号 TOP5:")
            for i, signal in enumerate(results['buy_signals']['strong'][:5], 1):
                print(f"  {i}. {signal.symbol} {signal.name} (评分:{signal.overall_score:.1f})")
        
        # 显示强卖出信号前5名
        if results['sell_signals']['strong']:
            print("🔴 强卖出信号 TOP5:")
            for i, signal in enumerate(results['sell_signals']['strong'][:5], 1):
                print(f"  {i}. {signal.symbol} {signal.name} (评分:{signal.overall_score:.1f})")
        
        print("\n💡 建议:")
        print("  - 重点关注强买入信号作为调仓目标")
        print("  - 优先处理强卖出信号减仓换股")
        print("  - 查看详细报告文件获取完整分析")

def main():
    """主函数"""
    print("🚀 每日缠论选股系统")
    print(f"运行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # 执行每日选股
        selector = DailyStockSelector()
        results = selector.run_daily_selection()
        
        if results:
            # 保存结果
            selector.save_results(results)
            
            # 显示摘要
            selector.print_summary(results)
            
        else:
            print("❌ 选股失败，请检查日志")
            
    except KeyboardInterrupt:
        print("\n⚠️ 用户中断程序")
    except Exception as e:
        print(f"❌ 程序异常: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()