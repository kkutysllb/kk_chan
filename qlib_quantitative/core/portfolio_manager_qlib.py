# -*- coding: utf-8 -*-
"""
Qlib投资组合管理器
基于Qlib框架的投资组合管理和风险控制
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
import logging
from datetime import datetime, timedelta
import json

# qlib导入
from qlib.log import get_module_logger


class QlibPortfolioManager:
    """
    Qlib投资组合管理器
    负责资金分配、仓位管理和风险控制
    基于Qlib框架的投资组合管理系统
    """
    
    def __init__(self, 
                 initial_capital: float = 10000000, 
                 config: Dict[str, Any] = None,
                 **kwargs):
        """
        初始化投资组合管理器
        
        Args:
            initial_capital: 初始资金
            config: 配置参数
            **kwargs: 其他参数
        """
        # 初始化投资组合管理器
        
        self.initial_capital = initial_capital
        self.config = config or {}
        self.logger = get_module_logger(__name__)
        
        # 投资组合配置
        self.max_position_ratio = self.config.get('max_position_ratio', 0.1)  # 单只股票最大仓位比例
        self.max_total_position = self.config.get('max_total_position', 0.95)  # 最大总仓位
        self.min_cash_ratio = self.config.get('min_cash_ratio', 0.05)  # 最小现金比例
        self.risk_free_rate = self.config.get('risk_free_rate', 0.03)  # 无风险利率
        
        # 风险控制参数
        self.max_drawdown_limit = self.config.get('max_drawdown_limit', 0.2)  # 最大回撤限制
        self.stop_loss_ratio = self.config.get('stop_loss_ratio', 0.1)  # 止损比例
        self.take_profit_ratio = self.config.get('take_profit_ratio', 0.2)  # 止盈比例
        
        # 投资组合状态
        self.current_positions = {}  # 当前持仓
        self.available_cash = initial_capital  # 可用现金
        self.total_value = initial_capital  # 总资产价值
        self.portfolio_history = []  # 投资组合历史
        
        # 初始化策略
        self._setup_strategy()
    
    def _setup_strategy(self):
        """设置投资组合策略"""
        try:
            # 使用简化的策略配置
            self.strategy_config = {
                'topk': self.config.get('topk', 10),
                'n_drop': self.config.get('n_drop', 5),
                'risk_degree': self.config.get('risk_degree', 0.95)
            }
            
            self.logger.info("投资组合策略初始化完成")
            
        except Exception as e:
            self.logger.error(f"投资组合策略初始化失败: {e}")
            raise
    
    def calculate_position_size(self, 
                               symbol: str, 
                               price: float, 
                               signal_strength: float = 1.0,
                               volatility: float = None) -> int:
        """
        计算仓位大小
        
        Args:
            symbol: 股票代码
            price: 当前价格
            signal_strength: 信号强度 (0-1)
            volatility: 波动率
            
        Returns:
            int: 建议买入股数
        """
        try:
            # 检查是否已有持仓
            if symbol in self.current_positions:
                self.logger.warning(f"股票 {symbol} 已有持仓，跳过")
                return 0
            
            # 检查可用现金
            if self.available_cash < price * 100:  # 至少能买1手
                self.logger.warning(f"可用现金不足，无法买入 {symbol}")
                return 0
            
            # 基础仓位计算
            base_position_value = self.total_value * self.max_position_ratio
            
            # 根据信号强度调整
            adjusted_position_value = base_position_value * signal_strength
            
            # 根据波动率调整（如果提供）
            if volatility is not None:
                # 波动率越高，仓位越小
                volatility_adjustment = max(0.5, 1 - volatility)
                adjusted_position_value *= volatility_adjustment
            
            # 计算股数（向下取整到100的倍数）
            shares = int(adjusted_position_value / price / 100) * 100
            
            # 检查是否超过可用现金
            required_cash = shares * price
            if required_cash > self.available_cash:
                shares = int(self.available_cash / price / 100) * 100
            
            # 检查总仓位限制
            current_position_ratio = self._calculate_current_position_ratio()
            new_position_ratio = required_cash / self.total_value
            
            if current_position_ratio + new_position_ratio > self.max_total_position:
                # 调整仓位以不超过总仓位限制
                max_new_position_value = (self.max_total_position - current_position_ratio) * self.total_value
                shares = int(max_new_position_value / price / 100) * 100
            
            self.logger.info(f"计算 {symbol} 仓位: {shares} 股，价值: {shares * price:.2f}")
            return shares
            
        except Exception as e:
            self.logger.error(f"计算仓位大小失败: {e}")
            return 0
    
    def generate_trade_decision(self, 
                               predictions: pd.DataFrame, 
                               current_positions: Dict[str, float] = None) -> List[Dict[str, Any]]:
        """
        生成交易决策
        
        Args:
            predictions: 预测结果
            current_positions: 当前持仓
            
        Returns:
            List[Dict[str, Any]]: 交易决策列表
        """
        try:
            # 使用简化的交易决策生成逻辑
            trade_decisions = self._generate_simple_trade_decision(
                predictions, 
                current_positions or self.current_positions
            )
            
            # 根据风险控制调整交易决策
            adjusted_decisions = self._apply_risk_controls(trade_decisions)
            
            return adjusted_decisions
            
        except Exception as e:
            self.logger.error(f"生成交易决策失败: {e}")
            return []
    
    def _generate_simple_trade_decision(self, predictions, current_positions):
        """简化的交易决策生成"""
        # 这里可以实现简化的交易决策逻辑
        return []
    
    def _apply_risk_controls(self, trade_decisions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """应用风险控制"""
        adjusted_decisions = []
        
        for decision in trade_decisions:
            try:
                symbol = decision.get('instrument')
                amount = decision.get('amount', 0)
                direction = decision.get('direction', 0)
                
                # 检查仓位限制
                if direction > 0:  # 买入
                    # 检查单只股票最大仓位
                    current_position_ratio = self._get_symbol_position_ratio(symbol)
                    if current_position_ratio + abs(amount) > self.max_position_ratio:
                        # 调整买入量
                        max_additional = self.max_position_ratio - current_position_ratio
                        decision['amount'] = max(0, max_additional)
                
                # 检查总仓位限制
                total_position_ratio = self._calculate_current_position_ratio()
                if total_position_ratio + abs(amount) > self.max_total_position:
                    # 调整交易量
                    max_additional = self.max_total_position - total_position_ratio
                    decision['amount'] = max(0, max_additional)
                
                # 检查现金限制
                cash_ratio = self.available_cash / self.total_value
                if cash_ratio < self.min_cash_ratio and direction > 0:
                    # 如果现金不足，减少买入量
                    available_for_investment = (cash_ratio - self.min_cash_ratio) * self.total_value
                    if available_for_investment <= 0:
                        decision['amount'] = 0
                    else:
                        decision['amount'] = min(decision['amount'], available_for_investment / self.total_value)
                
                adjusted_decisions.append(decision)
                
            except Exception as e:
                self.logger.error(f"应用风险控制失败: {e}")
                adjusted_decisions.append(decision)
        
        return adjusted_decisions
    
    def add_position(self, symbol: str, shares: int, price: float, date: datetime) -> bool:
        """
        添加持仓
        
        Args:
            symbol: 股票代码
            shares: 股数
            price: 买入价格
            date: 买入日期
            
        Returns:
            bool: 是否成功添加
        """
        try:
            if symbol in self.current_positions:
                self.logger.warning(f"股票 {symbol} 已有持仓")
                return False
            
            cost = shares * price
            if cost > self.available_cash:
                self.logger.error(f"资金不足，无法买入 {symbol}")
                return False
            
            # 添加持仓
            self.current_positions[symbol] = {
                'shares': shares,
                'avg_price': price,
                'cost': cost,
                'buy_date': date,
                'current_price': price,
                'market_value': cost,
                'unrealized_pnl': 0,
                'stop_loss_price': price * (1 - self.stop_loss_ratio),
                'take_profit_price': price * (1 + self.take_profit_ratio)
            }
            
            # 更新可用现金
            self.available_cash -= cost
            
            self.logger.info(f"成功买入 {symbol}: {shares} 股，价格: {price}，成本: {cost:.2f}")
            return True
            
        except Exception as e:
            self.logger.error(f"添加持仓失败: {e}")
            return False
    
    def remove_position(self, symbol: str, shares: int, price: float, date: datetime) -> bool:
        """
        减少或清除持仓
        
        Args:
            symbol: 股票代码
            shares: 卖出股数
            price: 卖出价格
            date: 卖出日期
            
        Returns:
            bool: 是否成功卖出
        """
        try:
            if symbol not in self.current_positions:
                self.logger.warning(f"股票 {symbol} 无持仓")
                return False
            
            position = self.current_positions[symbol]
            
            if shares > position['shares']:
                self.logger.error(f"卖出股数 {shares} 超过持仓 {position['shares']}")
                return False
            
            # 计算收益
            proceeds = shares * price
            cost_basis = shares * position['avg_price']
            realized_pnl = proceeds - cost_basis
            
            # 更新持仓
            if shares == position['shares']:
                # 全部卖出
                del self.current_positions[symbol]
            else:
                # 部分卖出
                position['shares'] -= shares
                position['cost'] -= cost_basis
                position['market_value'] = position['shares'] * position['current_price']
                position['unrealized_pnl'] = position['market_value'] - position['cost']
            
            # 更新可用现金
            self.available_cash += proceeds
            
            self.logger.info(f"成功卖出 {symbol}: {shares} 股，价格: {price}，收益: {realized_pnl:.2f}")
            return True
            
        except Exception as e:
            self.logger.error(f"卖出持仓失败: {e}")
            return False
    
    def update_positions(self, price_data: Dict[str, float], date: datetime):
        """
        更新持仓市值和盈亏
        
        Args:
            price_data: 股票价格数据 {symbol: price}
            date: 更新日期
        """
        try:
            total_market_value = self.available_cash
            
            for symbol, position in self.current_positions.items():
                if symbol in price_data:
                    current_price = price_data[symbol]
                    position['current_price'] = current_price
                    position['market_value'] = position['shares'] * current_price
                    position['unrealized_pnl'] = position['market_value'] - position['cost']
                    
                    total_market_value += position['market_value']
            
            self.total_value = total_market_value
            
            # 记录投资组合历史
            self.portfolio_history.append({
                'date': date,
                'total_value': self.total_value,
                'available_cash': self.available_cash,
                'positions_value': total_market_value - self.available_cash,
                'position_count': len(self.current_positions)
            })
            
        except Exception as e:
            self.logger.error(f"更新持仓失败: {e}")
    
    def check_risk_controls(self) -> List[Dict[str, Any]]:
        """
        检查风险控制条件
        
        Returns:
            List[Dict[str, Any]]: 风险警告列表
        """
        warnings = []
        
        try:
            # 检查最大回撤
            if len(self.portfolio_history) > 1:
                peak_value = max([h['total_value'] for h in self.portfolio_history])
                current_drawdown = (peak_value - self.total_value) / peak_value
                
                if current_drawdown > self.max_drawdown_limit:
                    warnings.append({
                        'type': 'max_drawdown',
                        'message': f"当前回撤 {current_drawdown:.2%} 超过限制 {self.max_drawdown_limit:.2%}",
                        'severity': 'high'
                    })
            
            # 检查现金比例
            cash_ratio = self.available_cash / self.total_value
            if cash_ratio < self.min_cash_ratio:
                warnings.append({
                    'type': 'low_cash',
                    'message': f"现金比例 {cash_ratio:.2%} 低于最小要求 {self.min_cash_ratio:.2%}",
                    'severity': 'medium'
                })
            
            # 检查个股止损止盈
            for symbol, position in self.current_positions.items():
                current_price = position['current_price']
                
                if current_price <= position['stop_loss_price']:
                    warnings.append({
                        'type': 'stop_loss',
                        'symbol': symbol,
                        'message': f"{symbol} 触发止损，当前价格: {current_price}, 止损价格: {position['stop_loss_price']}",
                        'severity': 'high'
                    })
                
                if current_price >= position['take_profit_price']:
                    warnings.append({
                        'type': 'take_profit',
                        'symbol': symbol,
                        'message': f"{symbol} 触发止盈，当前价格: {current_price}, 止盈价格: {position['take_profit_price']}",
                        'severity': 'medium'
                    })
            
            return warnings
            
        except Exception as e:
            self.logger.error(f"风险检查失败: {e}")
            return []
    
    def get_portfolio_summary(self) -> Dict[str, Any]:
        """
        获取投资组合摘要
        
        Returns:
            Dict[str, Any]: 投资组合摘要
        """
        try:
            positions_value = sum([pos['market_value'] for pos in self.current_positions.values()])
            total_cost = sum([pos['cost'] for pos in self.current_positions.values()])
            total_unrealized_pnl = sum([pos['unrealized_pnl'] for pos in self.current_positions.values()])
            
            return {
                'total_value': self.total_value,
                'available_cash': self.available_cash,
                'positions_value': positions_value,
                'cash_ratio': self.available_cash / self.total_value,
                'position_count': len(self.current_positions),
                'total_cost': total_cost,
                'total_unrealized_pnl': total_unrealized_pnl,
                'unrealized_return': total_unrealized_pnl / total_cost if total_cost > 0 else 0,
                'total_return': (self.total_value - self.initial_capital) / self.initial_capital
            }
            
        except Exception as e:
            self.logger.error(f"获取投资组合摘要失败: {e}")
            return {}
    
    def get_position_details(self) -> pd.DataFrame:
        """
        获取持仓明细
        
        Returns:
            DataFrame: 持仓明细
        """
        try:
            if not self.current_positions:
                return pd.DataFrame()
            
            positions_data = []
            for symbol, position in self.current_positions.items():
                positions_data.append({
                    'symbol': symbol,
                    'shares': position['shares'],
                    'avg_price': position['avg_price'],
                    'current_price': position['current_price'],
                    'cost': position['cost'],
                    'market_value': position['market_value'],
                    'unrealized_pnl': position['unrealized_pnl'],
                    'unrealized_return': position['unrealized_pnl'] / position['cost'],
                    'weight': position['market_value'] / self.total_value,
                    'buy_date': position['buy_date'],
                    'holding_days': (datetime.now() - position['buy_date']).days
                })
            
            return pd.DataFrame(positions_data)
            
        except Exception as e:
            self.logger.error(f"获取持仓明细失败: {e}")
            return pd.DataFrame()
    
    def _calculate_current_position_ratio(self) -> float:
        """计算当前总仓位比例"""
        positions_value = sum([pos['market_value'] for pos in self.current_positions.values()])
        return positions_value / self.total_value
    
    def _get_symbol_position_ratio(self, symbol: str) -> float:
        """获取单只股票仓位比例"""
        if symbol in self.current_positions:
            return self.current_positions[symbol]['market_value'] / self.total_value
        return 0
    
    def reset_portfolio(self):
        """重置投资组合"""
        self.current_positions.clear()
        self.available_cash = self.initial_capital
        self.total_value = self.initial_capital
        self.portfolio_history.clear()
        self.logger.info("投资组合已重置")
    
    def export_portfolio_history(self) -> pd.DataFrame:
        """
        导出投资组合历史
        
        Returns:
            DataFrame: 投资组合历史数据
        """
        try:
            if not self.portfolio_history:
                return pd.DataFrame()
            
            df = pd.DataFrame(self.portfolio_history)
            df['date'] = pd.to_datetime(df['date'])
            df.set_index('date', inplace=True)
            
            # 计算收益率
            df['daily_return'] = df['total_value'].pct_change()
            df['cumulative_return'] = (df['total_value'] / self.initial_capital) - 1
            
            return df
            
        except Exception as e:
            self.logger.error(f"导出投资组合历史失败: {e}")
            return pd.DataFrame()


# 便捷函数
def create_portfolio_manager(initial_capital: float = 10000000, 
                           config: Dict[str, Any] = None) -> QlibPortfolioManager:
    """
    创建投资组合管理器
    
    Args:
        initial_capital: 初始资金
        config: 配置参数
        
    Returns:
        QlibPortfolioManager: 投资组合管理器实例
    """
    return QlibPortfolioManager(initial_capital, config)


def create_topk_dropout_portfolio(topk: int = 10, 
                                 n_drop: int = 5,
                                 initial_capital: float = 10000000,
                                 config: Dict[str, Any] = None) -> QlibPortfolioManager:
    """
    创建TopK Dropout投资组合策略
    
    Args:
        topk: 选择前K只股票
        n_drop: 每次调仓时丢弃的股票数量
        initial_capital: 初始资金
        config: 配置参数
        
    Returns:
        QlibPortfolioManager: 投资组合管理器实例
    """
    if config is None:
        config = {}
    
    config.update({
        'topk': topk,
        'n_drop': n_drop
    })
    
    return QlibPortfolioManager(initial_capital, config)