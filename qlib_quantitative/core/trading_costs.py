#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A股交易费用计算模块
支持准确的佣金、印花税、过户费计算
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
import logging
from dataclasses import dataclass
from datetime import datetime


@dataclass
class TradingCostConfig:
    """交易费用配置"""
    # 佣金费率
    commission_rate: float = 0.0003  # 万3佣金
    min_commission: float = 5.0      # 最低佣金5元
    
    # 印花税 (仅卖出收取)
    stamp_tax_rate: float = 0.001    # 千分之一
    
    # 过户费 (仅上海股票)
    transfer_fee_rate: float = 0.00002  # 万分之0.2
    min_transfer_fee: float = 1.0       # 最低1元
    
    # 其他费用
    regulatory_fee_rate: float = 0.00002  # 监管费万分之0.2
    
    # 交易单位
    trade_unit: int = 100  # A股以手为单位，1手=100股


class TradingCostCalculator:
    """交易费用计算器"""
    
    def __init__(self, config: TradingCostConfig = None):
        self.config = config or TradingCostConfig()
        self.logger = logging.getLogger(__name__)
    
    def calculate_buy_costs(self, price: float, quantity: int, stock_code: str) -> Dict[str, float]:
        """计算买入费用"""
        # 确保数量是100的整数倍
        quantity = int(quantity // self.config.trade_unit) * self.config.trade_unit
        
        if quantity <= 0:
            return {'total_cost': 0, 'commission': 0, 'transfer_fee': 0, 'regulatory_fee': 0}
        
        trade_amount = price * quantity
        
        # 佣金
        commission = max(trade_amount * self.config.commission_rate, self.config.min_commission)
        
        # 过户费 (仅上海股票)
        transfer_fee = 0
        if stock_code.startswith('SH') or stock_code.startswith('60'):
            transfer_fee = max(quantity * self.config.transfer_fee_rate, self.config.min_transfer_fee)
        
        # 监管费
        regulatory_fee = trade_amount * self.config.regulatory_fee_rate
        
        total_cost = commission + transfer_fee + regulatory_fee
        
        return {
            'total_cost': total_cost,
            'commission': commission,
            'transfer_fee': transfer_fee,
            'regulatory_fee': regulatory_fee,
            'trade_amount': trade_amount,
            'actual_quantity': quantity
        }
    
    def calculate_sell_costs(self, price: float, quantity: int, stock_code: str) -> Dict[str, float]:
        """计算卖出费用"""
        if quantity <= 0:
            return {'total_cost': 0, 'commission': 0, 'stamp_tax': 0, 'transfer_fee': 0, 'regulatory_fee': 0}
        
        trade_amount = price * quantity
        
        # 佣金
        commission = max(trade_amount * self.config.commission_rate, self.config.min_commission)
        
        # 印花税
        stamp_tax = trade_amount * self.config.stamp_tax_rate
        
        # 过户费 (仅上海股票)
        transfer_fee = 0
        if stock_code.startswith('SH') or stock_code.startswith('60'):
            transfer_fee = max(quantity * self.config.transfer_fee_rate, self.config.min_transfer_fee)
        
        # 监管费
        regulatory_fee = trade_amount * self.config.regulatory_fee_rate
        
        total_cost = commission + stamp_tax + transfer_fee + regulatory_fee
        
        return {
            'total_cost': total_cost,
            'commission': commission,
            'stamp_tax': stamp_tax,
            'transfer_fee': transfer_fee,
            'regulatory_fee': regulatory_fee,
            'trade_amount': trade_amount,
            'net_amount': trade_amount - total_cost
        }
    
    def calculate_round_trip_costs(self, buy_price: float, sell_price: float, quantity: int, stock_code: str) -> Dict[str, float]:
        """计算完整交易成本"""
        buy_costs = self.calculate_buy_costs(buy_price, quantity, stock_code)
        sell_costs = self.calculate_sell_costs(sell_price, quantity, stock_code)
        
        total_costs = buy_costs['total_cost'] + sell_costs['total_cost']
        gross_profit = (sell_price - buy_price) * quantity
        net_profit = gross_profit - total_costs
        
        return {
            'buy_costs': buy_costs,
            'sell_costs': sell_costs,
            'total_costs': total_costs,
            'gross_profit': gross_profit,
            'net_profit': net_profit,
            'cost_ratio': total_costs / (buy_price * quantity) if buy_price * quantity > 0 else 0,
            'net_return': net_profit / (buy_price * quantity) if buy_price * quantity > 0 else 0
        }
    
    def optimize_position_size(self, price: float, available_capital: float, stock_code: str, max_position_pct: float = 0.1) -> Dict[str, float]:
        """优化持仓规模"""
        # 考虑交易费用后的最优持仓
        max_position_value = available_capital * max_position_pct
        
        # 计算可买入的最大手数
        max_shares_by_capital = int(max_position_value / price)
        max_hands = max_shares_by_capital // self.config.trade_unit
        
        if max_hands <= 0:
            return {'optimal_quantity': 0, 'optimal_value': 0, 'costs': 0}
        
        # 计算交易费用
        optimal_quantity = max_hands * self.config.trade_unit
        costs = self.calculate_buy_costs(price, optimal_quantity, stock_code)
        
        # 确保有足够资金支付费用
        total_required = costs['trade_amount'] + costs['total_cost']
        
        if total_required > max_position_value:
            # 减少持仓以留出费用
            max_hands -= 1
            optimal_quantity = max(0, max_hands * self.config.trade_unit)
            costs = self.calculate_buy_costs(price, optimal_quantity, stock_code)
        
        return {
            'optimal_quantity': optimal_quantity,
            'optimal_value': costs['trade_amount'],
            'costs': costs['total_cost'],
            'total_required': costs['trade_amount'] + costs['total_cost']
        }


class PositionManager:
    """持仓管理器 - 处理T+1交易规则"""
    
    def __init__(self, cost_calculator: TradingCostCalculator = None):
        self.cost_calculator = cost_calculator or TradingCostCalculator()
        self.positions = {}  # 持仓记录
        self.t1_pending = {}  # T+1待卖出股票
        self.trade_history = []  # 交易历史
        self.logger = logging.getLogger(__name__)
    
    def buy_stock(self, stock_code: str, price: float, quantity: int, date: datetime) -> Dict[str, float]:
        """买入股票"""
        if quantity <= 0:
            return {'success': False, 'message': '数量必须大于0'}
        
        # 计算交易费用
        costs = self.cost_calculator.calculate_buy_costs(price, quantity, stock_code)
        actual_quantity = costs['actual_quantity']
        
        if actual_quantity <= 0:
            return {'success': False, 'message': '买入数量不足一手'}
        
        # 更新持仓
        if stock_code not in self.positions:
            self.positions[stock_code] = {
                'quantity': 0,
                'avg_cost': 0,
                'total_cost': 0,
                'buy_date': date
            }
        
        position = self.positions[stock_code]
        old_total_cost = position['total_cost']
        old_quantity = position['quantity']
        
        # 计算新的平均成本
        new_total_cost = old_total_cost + costs['trade_amount'] + costs['total_cost']
        new_quantity = old_quantity + actual_quantity
        new_avg_cost = new_total_cost / new_quantity if new_quantity > 0 else 0
        
        # 更新持仓
        position['quantity'] = new_quantity
        position['avg_cost'] = new_avg_cost
        position['total_cost'] = new_total_cost
        position['buy_date'] = date
        
        # 记录交易
        trade_record = {
            'date': date,
            'stock_code': stock_code,
            'action': 'BUY',
            'price': price,
            'quantity': actual_quantity,
            'costs': costs['total_cost'],
            'total_amount': costs['trade_amount'] + costs['total_cost']
        }
        self.trade_history.append(trade_record)
        
        return {
            'success': True,
            'quantity': actual_quantity,
            'costs': costs['total_cost'],
            'total_amount': costs['trade_amount'] + costs['total_cost']
        }
    
    def sell_stock(self, stock_code: str, price: float, quantity: int, date: datetime) -> Dict[str, float]:
        """卖出股票 - 考虑T+1规则"""
        if stock_code not in self.positions:
            return {'success': False, 'message': '没有持仓'}
        
        position = self.positions[stock_code]
        
        # 检查T+1规则
        if position['buy_date'].date() == date.date():
            return {'success': False, 'message': 'T+1规则限制，当日买入不能卖出'}
        
        # 检查持仓数量
        available_quantity = position['quantity']
        if quantity > available_quantity:
            quantity = available_quantity
        
        if quantity <= 0:
            return {'success': False, 'message': '卖出数量不足'}
        
        # 计算交易费用
        costs = self.cost_calculator.calculate_sell_costs(price, quantity, stock_code)
        
        # 计算盈亏
        cost_basis = position['avg_cost'] * quantity
        gross_profit = price * quantity - cost_basis
        net_profit = gross_profit - costs['total_cost']
        
        # 更新持仓
        position['quantity'] -= quantity
        if position['quantity'] <= 0:
            del self.positions[stock_code]
        else:
            # 重新计算剩余持仓的总成本
            remaining_cost = position['total_cost'] - cost_basis
            position['total_cost'] = remaining_cost
        
        # 记录交易
        trade_record = {
            'date': date,
            'stock_code': stock_code,
            'action': 'SELL',
            'price': price,
            'quantity': quantity,
            'costs': costs['total_cost'],
            'gross_profit': gross_profit,
            'net_profit': net_profit,
            'net_amount': costs['net_amount']
        }
        self.trade_history.append(trade_record)
        
        return {
            'success': True,
            'quantity': quantity,
            'costs': costs['total_cost'],
            'gross_profit': gross_profit,
            'net_profit': net_profit,
            'net_amount': costs['net_amount']
        }
    
    def get_position_value(self, current_prices: Dict[str, float]) -> Dict[str, float]:
        """获取当前持仓市值"""
        total_value = 0
        total_cost = 0
        total_profit = 0
        
        position_details = {}
        
        for stock_code, position in self.positions.items():
            if stock_code in current_prices:
                current_price = current_prices[stock_code]
                market_value = current_price * position['quantity']
                cost_value = position['total_cost']
                unrealized_profit = market_value - cost_value
                
                position_details[stock_code] = {
                    'quantity': position['quantity'],
                    'avg_cost': position['avg_cost'],
                    'current_price': current_price,
                    'market_value': market_value,
                    'cost_value': cost_value,
                    'unrealized_profit': unrealized_profit,
                    'return_rate': unrealized_profit / cost_value if cost_value > 0 else 0
                }
                
                total_value += market_value
                total_cost += cost_value
                total_profit += unrealized_profit
        
        return {
            'total_value': total_value,
            'total_cost': total_cost,
            'total_profit': total_profit,
            'total_return': total_profit / total_cost if total_cost > 0 else 0,
            'positions': position_details
        }
    
    def get_trade_statistics(self) -> Dict[str, float]:
        """获取交易统计"""
        if not self.trade_history:
            return {}
        
        trades = pd.DataFrame(self.trade_history)
        
        # 基本统计
        total_trades = len(trades)
        buy_trades = trades[trades['action'] == 'BUY']
        sell_trades = trades[trades['action'] == 'SELL']
        
        # 交易成本
        total_costs = trades['costs'].sum()
        
        # 盈利统计
        if len(sell_trades) > 0:
            profitable_trades = sell_trades[sell_trades['net_profit'] > 0]
            losing_trades = sell_trades[sell_trades['net_profit'] <= 0]
            
            win_rate = len(profitable_trades) / len(sell_trades)
            avg_profit = profitable_trades['net_profit'].mean() if len(profitable_trades) > 0 else 0
            avg_loss = losing_trades['net_profit'].mean() if len(losing_trades) > 0 else 0
            
            return {
                'total_trades': total_trades,
                'buy_trades': len(buy_trades),
                'sell_trades': len(sell_trades),
                'total_costs': total_costs,
                'win_rate': win_rate,
                'avg_profit': avg_profit,
                'avg_loss': avg_loss,
                'profit_loss_ratio': abs(avg_profit / avg_loss) if avg_loss != 0 else 0,
                'total_realized_profit': sell_trades['net_profit'].sum()
            }
        
        return {
            'total_trades': total_trades,
            'buy_trades': len(buy_trades),
            'sell_trades': len(sell_trades),
            'total_costs': total_costs
        }


# 示例使用
if __name__ == "__main__":
    # 创建费用计算器
    cost_config = TradingCostConfig(
        commission_rate=0.0003,  # 万3佣金
        stamp_tax_rate=0.001,    # 千分之一印花税
        min_commission=5.0       # 最低5元佣金
    )
    
    calculator = TradingCostCalculator(cost_config)
    
    # 示例：计算买入1000股平安银行的费用
    stock_code = "SZ000001"
    price = 12.50
    quantity = 1000
    
    buy_costs = calculator.calculate_buy_costs(price, quantity, stock_code)
    print(f"买入费用: {buy_costs}")
    
    # 示例：计算卖出费用
    sell_costs = calculator.calculate_sell_costs(13.00, quantity, stock_code)
    print(f"卖出费用: {sell_costs}")
    
    # 示例：计算完整交易成本
    round_trip = calculator.calculate_round_trip_costs(12.50, 13.00, quantity, stock_code)
    print(f"完整交易成本: {round_trip}")