# -*- coding: utf-8 -*-
"""
Qlib回测引擎
基于Qlib框架的回测执行引擎
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional
import logging
from datetime import datetime, timedelta
import os
import json

# qlib导入
from qlib.utils import init_instance_by_config
from qlib.log import get_module_logger
from qlib.data.dataset import DatasetH
from qlib.model.base import Model
from qlib.strategy.base import BaseStrategy


class QlibBacktestEngine:
    """
    Qlib回测引擎
    负责执行策略回测和结果分析
    基于Qlib框架的回测系统
    """
    
    def __init__(self, data_adapter, config: Dict[str, Any] = None):
        """
        初始化回测引擎
        
        Args:
            data_adapter: 数据适配器
            config: 回测配置
        """
        self.data_adapter = data_adapter
        self.config = config or {}
        self.logger = get_module_logger(__name__)
        
        # 回测参数
        self.initial_capital = self.config.get('initial_capital', 10000000)
        self.commission = self.config.get('commission', 0.0015)
        self.benchmark_symbol = self.config.get('benchmark', 'SH000905')
        
        # 回测结果
        self.results = {}
        
        # 初始化Qlib环境
        self._setup_qlib_environment()
    
    def _setup_qlib_environment(self):
        """设置Qlib框架环境"""
        try:
            # 设置基本日志级别
            self.logger.info("Qlib环境设置完成")
            
        except Exception as e:
            self.logger.error(f"Qlib环境设置失败: {e}")
            # 不抛出异常，继续执行
    
    def run_single_strategy(self, 
                           strategy: BaseStrategy,
                           symbols: List[str],
                           start_date: str,
                           end_date: str,
                           benchmark: str = None) -> Dict[str, Any]:
        """
        运行单个策略回测
        
        Args:
            strategy: 策略实例
            symbols: 股票代码列表
            start_date: 开始日期
            end_date: 结束日期
            benchmark: 基准指数
            
        Returns:
            Dict[str, Any]: 回测结果
        """
        try:
            if benchmark is None:
                benchmark = self.benchmark_symbol
            
            self.logger.info(f"开始回测策略: {strategy.name}")
            
            # 执行策略回测
            result = strategy.run_backtest(symbols, start_date, end_date, benchmark)
            
            # 保存结果
            self.results[strategy.name] = result
            
            self.logger.info(f"策略 {strategy.name} 回测完成")
            return result
            
        except Exception as e:
            self.logger.error(f"策略回测失败: {e}")
            raise
    
    def run_multiple_strategies(self,
                               strategies: List[BaseStrategy],
                               symbols: List[str],
                               start_date: str,
                               end_date: str,
                               benchmark: str = None) -> Dict[str, Dict[str, Any]]:
        """
        运行多个策略回测
        
        Args:
            strategies: 策略列表
            symbols: 股票代码列表
            start_date: 开始日期
            end_date: 结束日期
            benchmark: 基准指数
            
        Returns:
            Dict[str, Dict[str, Any]]: 所有策略的回测结果
        """
        results = {}
        
        for strategy in strategies:
            try:
                result = self.run_single_strategy(strategy, symbols, start_date, end_date, benchmark)
                results[strategy.name] = result
            except Exception as e:
                self.logger.error(f"策略 {strategy.name} 回测失败: {e}")
                results[strategy.name] = None
        
        return results
    
    def compare_strategies(self, strategy_names: List[str] = None) -> pd.DataFrame:
        """
        比较多个策略的表现
        
        Args:
            strategy_names: 要比较的策略名称列表，None表示比较所有策略
            
        Returns:
            DataFrame: 策略比较结果
        """
        if not self.results:
            raise RuntimeError("没有可比较的回测结果")
        
        if strategy_names is None:
            strategy_names = list(self.results.keys())
        
        comparison_data = []
        
        for name in strategy_names:
            if name not in self.results or self.results[name] is None:
                continue
            
            try:
                result = self.results[name]
                portfolio_metrics = result.get('portfolio_metrics')
                
                if portfolio_metrics is None:
                    continue
                
                # 计算基础指标
                performance_metrics = self._calculate_strategy_metrics(portfolio_metrics)
                
                comparison_data.append({
                    'strategy_name': name,
                    'annual_return': performance_metrics.get('annual_return', 0),
                    'max_drawdown': performance_metrics.get('max_drawdown', 0),
                    'sharpe_ratio': performance_metrics.get('sharpe_ratio', 0),
                    'win_rate': performance_metrics.get('win_rate', 0),
                    'total_return': performance_metrics.get('total_return', 0),
                    'volatility': performance_metrics.get('volatility', 0)
                })
                
            except Exception as e:
                self.logger.error(f"计算策略 {name} 指标失败: {e}")
        
        return pd.DataFrame(comparison_data)
    
    def generate_report(self, strategy_name: str, output_dir: str = None) -> Dict[str, Any]:
        """
        生成策略回测报告
        
        Args:
            strategy_name: 策略名称
            output_dir: 输出目录
            
        Returns:
            Dict[str, Any]: 报告数据
        """
        if strategy_name not in self.results:
            raise ValueError(f"策略 {strategy_name} 的回测结果不存在")
        
        result = self.results[strategy_name]
        if result is None:
            raise ValueError(f"策略 {strategy_name} 的回测结果为空")
        
        try:
            portfolio_metrics = result.get('portfolio_metrics')
            
            # 生成报告数据
            report = {
                'strategy_name': strategy_name,
                'backtest_period': {
                    'start_date': result.get('start_date'),
                    'end_date': result.get('end_date')
                },
                'summary': self._generate_summary(portfolio_metrics),
                'performance_metrics': self._calculate_strategy_metrics(portfolio_metrics),
                'risk_metrics': self._calculate_risk_metrics(portfolio_metrics),
                'benchmark': result.get('benchmark', 'SH000905')
            }
            
            # 保存报告
            if output_dir:
                self._save_report(report, output_dir, strategy_name)
            
            return report
            
        except Exception as e:
            self.logger.error(f"生成报告失败: {e}")
            raise
    
    def _generate_summary(self, portfolio_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """生成回测摘要"""
        if not portfolio_metrics:
            return {
                'total_return': 0,
                'annual_return': 0,
                'max_drawdown': 0,
                'sharpe_ratio': 0,
                'win_rate': 0
            }
        
        # 计算关键指标
        performance_metrics = self._calculate_strategy_metrics(portfolio_metrics)
        
        return {
            'total_return': performance_metrics.get('total_return', 0),
            'annual_return': performance_metrics.get('annual_return', 0),
            'max_drawdown': performance_metrics.get('max_drawdown', 0),
            'sharpe_ratio': performance_metrics.get('sharpe_ratio', 0),
            'win_rate': performance_metrics.get('win_rate', 0),
            'volatility': performance_metrics.get('volatility', 0)
        }
    
    def _calculate_strategy_metrics(self, portfolio_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """计算策略指标"""
        if not portfolio_metrics or 'excess_return_with_cost' not in portfolio_metrics:
            return {}
        
        try:
            returns = portfolio_metrics['excess_return_with_cost']
            
            # 计算年化收益率
            total_return = returns.iloc[-1] if len(returns) > 0 else 0
            days = len(returns)
            annual_return = (1 + total_return) ** (252 / days) - 1 if days > 0 else 0
            
            # 计算最大回撤
            cumulative_returns = (1 + returns).cumprod()
            running_max = cumulative_returns.cummax()
            drawdown = (cumulative_returns - running_max) / running_max
            max_drawdown = drawdown.min()
            
            # 计算夏普比率
            if len(returns) > 1:
                daily_returns = returns.pct_change().dropna()
                sharpe_ratio = daily_returns.mean() / daily_returns.std() * np.sqrt(252) if daily_returns.std() > 0 else 0
                volatility = daily_returns.std() * np.sqrt(252)
            else:
                sharpe_ratio = 0
                volatility = 0
            
            # 计算胜率
            win_rate = (returns > 0).mean() if len(returns) > 0 else 0
            
            return {
                'annual_return': annual_return,
                'max_drawdown': max_drawdown,
                'sharpe_ratio': sharpe_ratio,
                'win_rate': win_rate,
                'total_return': total_return,
                'volatility': volatility
            }
            
        except Exception as e:
            self.logger.error(f"计算策略指标失败: {e}")
            return {}
    
    def _calculate_performance_metrics(self, portfolio_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """计算表现指标"""
        return self._calculate_strategy_metrics(portfolio_metrics)
    
    def _calculate_risk_metrics(self, portfolio_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """计算风险指标"""
        metrics = self._calculate_strategy_metrics(portfolio_metrics)
        return {
            'max_drawdown': metrics.get('max_drawdown', 0),
            'volatility': metrics.get('volatility', 0),
            'var_95': 0,  # 可以进一步实现
            'cvar_95': 0,  # 可以进一步实现
            'beta': 0,  # 可以进一步实现
        }
    
    def _save_report(self, report: Dict[str, Any], output_dir: str, strategy_name: str):
        """保存报告到文件"""
        try:
            os.makedirs(output_dir, exist_ok=True)
            
            # 保存JSON格式报告
            report_file = os.path.join(output_dir, f"{strategy_name}_report.json")
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2, default=str)
            
            self.logger.info(f"报告已保存到: {report_file}")
            
        except Exception as e:
            self.logger.error(f"保存报告失败: {e}")
            raise
    
    def clear_results(self):
        """清空回测结果"""
        self.results.clear()
        self.logger.info("回测结果已清空")
    
    def batch_backtest(self, 
                      strategies: List[BaseStrategy],
                      symbols: List[str],
                      start_date: str,
                      end_date: str,
                      output_dir: str = None) -> Dict[str, Any]:
        """
        批量回测多个策略
        
        Args:
            strategies: 策略列表
            symbols: 股票代码列表
            start_date: 开始日期
            end_date: 结束日期
            output_dir: 输出目录
            
        Returns:
            Dict[str, Any]: 批量回测结果
        """
        try:
            # 运行多个策略
            results = self.run_multiple_strategies(strategies, symbols, start_date, end_date)
            
            # 比较策略表现
            comparison = self.compare_strategies()
            
            # 生成报告
            reports = {}
            for strategy_name in results.keys():
                if results[strategy_name] is not None:
                    reports[strategy_name] = self.generate_report(strategy_name, output_dir)
            
            batch_result = {
                'individual_results': results,
                'comparison': comparison,
                'reports': reports,
                'summary': {
                    'total_strategies': len(strategies),
                    'successful_strategies': len([r for r in results.values() if r is not None]),
                    'failed_strategies': len([r for r in results.values() if r is None]),
                    'backtest_period': {'start_date': start_date, 'end_date': end_date}
                }
            }
            
            self.logger.info(f"批量回测完成，成功 {batch_result['summary']['successful_strategies']} 个策略")
            return batch_result
            
        except Exception as e:
            self.logger.error(f"批量回测失败: {e}")
            raise


# 便捷函数
def create_backtest_engine(data_adapter, config: Dict[str, Any] = None) -> QlibBacktestEngine:
    """
    创建回测引擎
    
    Args:
        data_adapter: 数据适配器
        config: 回测配置
        
    Returns:
        QlibBacktestEngine: 回测引擎实例
    """
    return QlibBacktestEngine(data_adapter, config)


def run_strategy_backtest(strategy: BaseStrategy, 
                         symbols: List[str],
                         start_date: str,
                         end_date: str,
                         data_adapter,
                         config: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    运行单个策略回测的便捷函数
    
    Args:
        strategy: 策略实例
        symbols: 股票代码列表
        start_date: 开始日期
        end_date: 结束日期
        data_adapter: 数据适配器
        config: 回测配置
        
    Returns:
        Dict[str, Any]: 回测结果
    """
    engine = create_backtest_engine(data_adapter, config)
    return engine.run_single_strategy(strategy, symbols, start_date, end_date)