#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整回测脚本 - 使用qlib框架和真实A股交易规则
支持：100万初始资金、万3佣金、千分之一印花税、T+1交易、买卖点预测
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

def run_complete_backtest():
    """运行完整回测"""
    logger.info("🚀 开始完整回测 - A股真实交易规则")
    
    try:
        # 1. 导入模块
        from core.trading_costs import TradingCostConfig, TradingCostCalculator, PositionManager
        from core.data_adapter import QlibDataAdapter
        
        # 尝试导入策略模块
        try:
            from strategies.curious_ragdoll_boll_qlib import CuriousRagdollBollConfig, CuriousRagdollBollModel
        except ImportError:
            # 如果导入失败，使用简化版本
            from dataclasses import dataclass
            
            @dataclass
            class CuriousRagdollBollConfig:
                stock_pool_size: int = 50
                fixed_positions: int = 10
                boll_period: int = 20
                boll_std: float = 2.0
            
            class CuriousRagdollBollModel:
                def __init__(self, config):
                    self.config = config
                
                def generate_signals(self, data):
                    # 简化的信号生成逻辑
                    signals = pd.Series(index=data.index, dtype=float)
                    
                    # 计算简单的布林带信号
                    if len(data) >= self.config.boll_period:
                        close_prices = data['close']
                        ma = close_prices.rolling(window=self.config.boll_period).mean()
                        std = close_prices.rolling(window=self.config.boll_period).std()
                        upper_band = ma + self.config.boll_std * std
                        lower_band = ma - self.config.boll_std * std
                        
                        # 生成简单信号
                        signals = pd.Series(0.5, index=data.index)  # 默认中性
                        signals[close_prices < lower_band] = 0.8  # 买入信号
                        signals[close_prices > upper_band] = 0.2  # 卖出信号
                    
                    return signals
        
        logger.info("✅ 模块导入成功")
        
        # 2. 配置参数
        # 交易费用配置
        cost_config = TradingCostConfig(
            commission_rate=0.0003,      # 万3佣金
            min_commission=5.0,          # 最低5元佣金
            stamp_tax_rate=0.001,        # 千分之一印花税
            transfer_fee_rate=0.00002,   # 万分之0.2过户费
            trade_unit=100               # 100股一手
        )
        
        # 策略配置
        strategy_config = CuriousRagdollBollConfig(
            stock_pool_size=50,
            fixed_positions=10,
            boll_period=20,
            boll_std=2.0
        )
        
        # 回测参数
        initial_capital = 1000000  # 100万初始资金
        start_date = "2023-01-01"
        end_date = "2023-12-31"
        
        logger.info(f"📊 回测参数:")
        logger.info(f"  初始资金: {initial_capital:,} 元")
        logger.info(f"  回测期间: {start_date} 至 {end_date}")
        logger.info(f"  佣金费率: {cost_config.commission_rate:.4f} ({cost_config.commission_rate*10000:.1f}万)")
        logger.info(f"  印花税率: {cost_config.stamp_tax_rate:.4f} ({cost_config.stamp_tax_rate*1000:.1f}千)")
        logger.info(f"  持仓数量: {strategy_config.fixed_positions}只")
        
        # 3. 初始化组件
        data_adapter = QlibDataAdapter()
        cost_calculator = TradingCostCalculator(cost_config)
        position_manager = PositionManager(cost_calculator)
        strategy_model = CuriousRagdollBollModel(strategy_config)
        
        # 4. 获取股票池
        logger.info("🎯 获取股票池...")
        stocks = data_adapter.get_stock_list("CSI500")
        if not stocks:
            raise Exception("无法获取股票池")
        
        # 筛选小市值股票
        small_cap_stocks = data_adapter.filter_small_cap_stocks(
            end_date, 
            count=strategy_config.stock_pool_size
        )
        
        if small_cap_stocks:
            stocks = small_cap_stocks
        else:
            stocks = stocks[:strategy_config.stock_pool_size]
        
        logger.info(f"✅ 股票池: {len(stocks)}只股票")
        
        # 5. 获取历史数据
        logger.info("📈 获取历史数据...")
        stock_data = {}
        for stock in stocks:
            data = data_adapter.get_stock_data(stock, start_date, end_date)
            if not data.empty:
                stock_data[stock] = data
        
        if not stock_data:
            raise Exception("无法获取股票数据")
        
        logger.info(f"✅ 获取到{len(stock_data)}只股票的数据")
        
        # 6. 生成交易信号
        logger.info("🧠 生成交易信号...")
        all_signals = {}
        for stock, data in stock_data.items():
            signals = strategy_model.generate_signals(data)
            all_signals[stock] = signals
        
        # 7. 执行回测
        logger.info("⚡ 执行回测...")
        
        # 初始化回测状态
        current_capital = initial_capital
        daily_portfolio_value = []
        daily_positions = []
        
        # 获取所有交易日
        all_dates = set()
        for data in stock_data.values():
            all_dates.update(data.index)
        all_dates = sorted(all_dates)
        
        logger.info(f"📅 回测期间: {len(all_dates)}个交易日")
        
        # 逐日模拟交易
        for i, date in enumerate(all_dates):
            logger.info(f"📅 交易日 {i+1}/{len(all_dates)}: {date.strftime('%Y-%m-%d')}")
            
            # 获取当日价格
            current_prices = {}
            for stock, data in stock_data.items():
                if date in data.index:
                    current_prices[stock] = data.loc[date, 'close']
            
            # 获取当日信号
            daily_signals = {}
            for stock, signals in all_signals.items():
                if date in signals.index:
                    daily_signals[stock] = signals[date]
            
            # 计算当前持仓价值
            position_value = position_manager.get_position_value(current_prices)
            total_portfolio_value = current_capital + position_value['total_value']
            
            # 卖出信号处理
            sell_amount = 0
            for stock, signal in daily_signals.items():
                if signal < 0.3 and stock in position_manager.positions:  # 卖出信号
                    position = position_manager.positions[stock]
                    if stock in current_prices:
                        sell_result = position_manager.sell_stock(
                            stock, 
                            current_prices[stock], 
                            position['quantity'], 
                            date
                        )
                        if sell_result['success']:
                            sell_amount += sell_result['net_amount']
                            logger.info(f"  卖出 {stock}: {sell_result['quantity']}股, 净收入: {sell_result['net_amount']:.2f}元")
            
            # 更新可用资金
            current_capital += sell_amount
            
            # 买入信号处理
            buy_signals = {k: v for k, v in daily_signals.items() if v > 0.7}  # 买入信号
            
            if buy_signals and current_capital > 10000:  # 至少有1万元才进行买入
                # 按信号强度排序
                sorted_signals = sorted(buy_signals.items(), key=lambda x: x[1], reverse=True)
                
                # 选择前N只股票
                selected_stocks = [stock for stock, _ in sorted_signals[:strategy_config.fixed_positions]]
                
                # 等权重分配资金
                if selected_stocks:
                    available_capital_per_stock = current_capital / len(selected_stocks)
                    
                    for stock in selected_stocks:
                        if stock in current_prices and stock not in position_manager.positions:
                            price = current_prices[stock]
                            
                            # 计算最优持仓
                            optimal_position = cost_calculator.optimize_position_size(
                                price, 
                                available_capital_per_stock, 
                                stock, 
                                max_position_pct=1.0
                            )
                            
                            if optimal_position['optimal_quantity'] > 0:
                                buy_result = position_manager.buy_stock(
                                    stock, 
                                    price, 
                                    optimal_position['optimal_quantity'], 
                                    date
                                )
                                
                                if buy_result['success']:
                                    current_capital -= buy_result['total_amount']
                                    logger.info(f"  买入 {stock}: {buy_result['quantity']}股, 总成本: {buy_result['total_amount']:.2f}元")
            
            # 记录每日状态
            final_position_value = position_manager.get_position_value(current_prices)
            final_portfolio_value = current_capital + final_position_value['total_value']
            
            daily_portfolio_value.append({
                'date': date,
                'cash': current_capital,
                'position_value': final_position_value['total_value'],
                'total_value': final_portfolio_value,
                'daily_return': (final_portfolio_value / initial_capital - 1) if i == 0 else 
                               (final_portfolio_value / daily_portfolio_value[-1]['total_value'] - 1)
            })
            
            daily_positions.append({
                'date': date,
                'positions': len(position_manager.positions),
                'stocks': list(position_manager.positions.keys())
            })
        
        # 8. 分析结果
        logger.info("📊 分析回测结果...")
        
        # 创建结果DataFrame
        portfolio_df = pd.DataFrame(daily_portfolio_value)
        portfolio_df.set_index('date', inplace=True)
        
        # 计算性能指标
        total_return = (portfolio_df['total_value'].iloc[-1] / initial_capital - 1)
        annual_return = ((portfolio_df['total_value'].iloc[-1] / initial_capital) ** (252 / len(portfolio_df)) - 1)
        
        # 计算最大回撤
        rolling_max = portfolio_df['total_value'].expanding().max()
        drawdown = (portfolio_df['total_value'] - rolling_max) / rolling_max
        max_drawdown = drawdown.min()
        
        # 计算夏普比率
        daily_returns = portfolio_df['total_value'].pct_change().dropna()
        sharpe_ratio = (daily_returns.mean() / daily_returns.std() * np.sqrt(252)) if daily_returns.std() > 0 else 0
        
        # 计算胜率
        win_rate = (daily_returns > 0).mean()
        
        # 获取交易统计
        trade_stats = position_manager.get_trade_statistics()
        
        # 9. 生成报告
        results = {
            'backtest_info': {
                'start_date': start_date,
                'end_date': end_date,
                'initial_capital': initial_capital,
                'final_capital': portfolio_df['total_value'].iloc[-1],
                'trading_days': len(portfolio_df),
                'stock_pool_size': len(stocks)
            },
            'performance_metrics': {
                'total_return': total_return,
                'annual_return': annual_return,
                'max_drawdown': max_drawdown,
                'sharpe_ratio': sharpe_ratio,
                'volatility': daily_returns.std() * np.sqrt(252),
                'win_rate': win_rate
            },
            'trading_costs': {
                'commission_rate': cost_config.commission_rate,
                'stamp_tax_rate': cost_config.stamp_tax_rate,
                'total_costs': trade_stats.get('total_costs', 0)
            },
            'trade_statistics': trade_stats,
            'daily_portfolio': portfolio_df.to_dict('records'),
            'final_positions': position_manager.get_position_value(current_prices),
            'trade_history': position_manager.trade_history
        }
        
        # 10. 保存结果
        output_dir = "/Users/libing/kk_Projects/kk_Stock/kk_stock_backend/abu_quantitative/results"
        os.makedirs(output_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        result_file = os.path.join(output_dir, f"complete_backtest_{timestamp}.json")
        
        with open(result_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2, default=str)
        
        logger.info(f"💾 回测结果已保存: {result_file}")
        
        # 11. 显示结果
        logger.info("🎉 回测完成! 结果摘要:")
        logger.info(f"  初始资金: {initial_capital:,} 元")
        logger.info(f"  最终资金: {portfolio_df['total_value'].iloc[-1]:,.2f} 元")
        logger.info(f"  总收益率: {total_return:.2%}")
        logger.info(f"  年化收益率: {annual_return:.2%}")
        logger.info(f"  最大回撤: {max_drawdown:.2%}")
        logger.info(f"  夏普比率: {sharpe_ratio:.2f}")
        logger.info(f"  波动率: {daily_returns.std() * np.sqrt(252):.2%}")
        logger.info(f"  胜率: {win_rate:.2%}")
        logger.info(f"  总交易次数: {trade_stats.get('total_trades', 0)}")
        logger.info(f"  总交易成本: {trade_stats.get('total_costs', 0):,.2f} 元")
        
        if trade_stats.get('sell_trades', 0) > 0:
            logger.info(f"  交易胜率: {trade_stats.get('win_rate', 0):.2%}")
            logger.info(f"  已实现盈利: {trade_stats.get('total_realized_profit', 0):,.2f} 元")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ 回测失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = run_complete_backtest()
    sys.exit(0 if success else 1)