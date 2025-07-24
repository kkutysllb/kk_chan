#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
好奇布偶猫BOLL择时策略 - Qlib框架版本
基于布林带指标的小市值股票择时策略

策略逻辑：
1. 从中证500成分股中选择市值最小的50只股票作为股票池
2. 使用20日布林带进行择时
3. 买入条件（3个必要条件）：
   - 前一交易日收盘价 < 布林下轨
   - 当前收盘价 > 前一交易日收盘价（反弹）
   - 当前收盘价 > 前期低点（突破前期低点）
4. 卖出条件（2个条件）：
   - 止损：当前价格 < 前期低点（止损位）
   - 止盈：前几日触及布林上轨且当前价格回落
5. 止损位设置为前期低点

作者：基于聚宽好奇布偶猫策略原版逻辑改编 - Qlib框架版本
"""

import pandas as pd
import numpy as np
from dataclasses import dataclass
from typing import Dict, Any, Optional, List
import logging

from qlib.log import get_module_logger
from qlib.utils import init_instance_by_config
from qlib.model.base import Model
from qlib.strategy.base import BaseStrategy


@dataclass
class CuriousRagdollBollConfig:
    """好奇布偶猫BOLL策略配置"""
    # 布林带参数
    boll_period: int = 20  # 布林带周期
    boll_std: float = 2.0  # 布林带标准差倍数
    
    # 股票池参数
    stock_pool_size: int = 50  # 候选股票池大小
    fixed_positions: int = 10  # 固定持仓股票数量
    
    # 技术指标参数
    lookback_period: int = 10  # 前期低点回看期
    atr_period: int = 14  # ATR计算周期
    
    # 风控参数
    stop_loss_pct: float = 0.08  # 止损比例8%
    take_profit_pct: float = 0.15  # 止盈比例15%
    max_position_value: float = 100000  # 单只股票最大持仓金额
    
    # 趋势因子阈值
    trend_ma_threshold: float = 0.01  # 价格相对均线阈值
    trend_macd_threshold: float = 0  # MACD阈值
    trend_boll_position_threshold: float = 0.3  # 布林带位置阈值
    trend_bias_threshold: float = -5  # 乖离率阈值
    
    # 动量因子阈值
    momentum_volume_ratio_threshold: float = 1.2  # 量比阈值
    momentum_rsi_lower: float = 30  # RSI下限
    momentum_rsi_upper: float = 70  # RSI上限
    momentum_turnover_threshold: float = 0.5  # 换手率阈值
    
    # 信号质量控制
    trend_score_threshold: int = 3  # 趋势评分阈值
    momentum_score_threshold: int = 2  # 动量评分阈值


class CuriousRagdollBollModel(Model):
    """好奇布偶猫BOLL模型 - 基于技术指标的信号生成"""
    
    def __init__(self, config: CuriousRagdollBollConfig = None):
        if config is None:
            config = CuriousRagdollBollConfig()
        self.config = config
        # 初始化模型
    
    def calculate_boll_bands(self, prices: pd.Series) -> Dict[str, float]:
        """计算布林带指标"""
        if len(prices) < self.config.boll_period:
            return {}
        
        # 计算移动平均线
        ma = prices.rolling(window=self.config.boll_period).mean().iloc[-1]
        
        # 计算标准差
        std = prices.rolling(window=self.config.boll_period).std().iloc[-1]
        
        # 计算布林带上下轨
        upper_band = ma + self.config.boll_std * std
        lower_band = ma - self.config.boll_std * std
        
        return {
            'ma': ma,
            'upper': upper_band,
            'lower': lower_band,
            'std': std
        }
    
    def calculate_momentum_factors(self, data: pd.DataFrame) -> Optional[Dict[str, float]]:
        """计算动量因子"""
        try:
            if len(data) < 10:
                return None
            
            # 计算量比（当前成交量 / 过去5日平均成交量）
            current_volume = data['volume'].iloc[-1]
            avg_volume_5d = data['volume'].iloc[-6:-1].mean()
            volume_ratio = current_volume / avg_volume_5d if avg_volume_5d > 0 else 1.0
            
            # 计算RSI
            prices = data['close']
            delta = prices.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            current_rsi = rsi.iloc[-1] if not rsi.empty else 50.0
            
            # 计算换手率（简化版本）
            turnover_rate = current_volume / data['volume'].rolling(window=20).mean().iloc[-1] if len(data) >= 20 else 1.0
            
            return {
                'volume_ratio': volume_ratio,
                'rsi': current_rsi,
                'turnover_rate': turnover_rate
            }
            
        except Exception as e:
            logging.error(f"计算动量因子失败: {e}")
            return None
    
    def calculate_trend_factors(self, data: pd.DataFrame) -> Optional[Dict[str, float]]:
        """计算趋势因子"""
        try:
            if len(data) < 10:
                return None
            
            prices = data['close']
            current_price = prices.iloc[-1]
            
            # 计算20日均线
            ma = prices.rolling(window=20).mean()
            ma_value = ma.iloc[-1]
            prev_ma = ma.iloc[-2] if len(ma) >= 2 else ma_value
            
            # 价格相对于均线的位置
            price_vs_ma = (current_price - ma_value) / ma_value if ma_value > 0 else 0
            
            # 均线趋势
            ma_trend = (ma_value - prev_ma) / prev_ma if prev_ma > 0 else 0
            
            # 计算MACD
            ema_12 = prices.ewm(span=12).mean()
            ema_26 = prices.ewm(span=26).mean()
            dif = ema_12 - ema_26
            dea = dif.ewm(span=9).mean()
            macd = (dif - dea).iloc[-1]
            
            # 计算布林带位置
            boll = self.calculate_boll_bands(prices)
            boll_position = 0
            if boll and boll['upper'] > boll['lower']:
                boll_position = (current_price - boll['lower']) / (boll['upper'] - boll['lower'])
            
            # 计算乖离率
            bias = (current_price - ma_value) / ma_value * 100 if ma_value > 0 else 0
            
            return {
                'price_vs_ma': price_vs_ma,
                'ma_trend': ma_trend,
                'macd': macd,
                'boll_position': boll_position,
                'bias': bias
            }
            
        except Exception as e:
            logging.error(f"计算趋势因子失败: {e}")
            return None
    
    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        """生成交易信号"""
        signals = pd.Series(index=data.index, dtype=float)
        
        for i in range(self.config.boll_period + 5, len(data)):
            # 获取当前数据段
            current_data = data.iloc[:i+1]
            prices = current_data['close']
            
            # 计算布林带（使用前一天的数据）
            boll = self.calculate_boll_bands(prices[:-1])
            if not boll:
                continue
            
            # 当前价格和前一日价格
            current_price = prices.iloc[-1]
            prev_price = prices.iloc[-2]
            
            # 计算前期低点
            lookback_start = max(0, len(prices) - self.config.lookback_period - 2)
            lookback_end = len(prices) - 2
            prev_low = prices.iloc[lookback_start:lookback_end].min()
            
            # 原版策略的3个买入条件
            condition1 = prev_price < boll['lower']
            condition2 = current_price > prev_price
            condition3 = current_price > prev_low
            
            # 计算趋势因子
            trend = self.calculate_trend_factors(current_data)
            trend_condition = True
            if trend:
                trend_condition1 = trend['price_vs_ma'] > self.config.trend_ma_threshold
                trend_condition2 = trend['ma_trend'] > 0
                trend_condition3 = trend['macd'] > self.config.trend_macd_threshold
                trend_condition4 = trend['boll_position'] > self.config.trend_boll_position_threshold
                trend_condition5 = trend['bias'] > self.config.trend_bias_threshold
                
                trend_score = sum([trend_condition1, trend_condition2, trend_condition3, trend_condition4, trend_condition5])
                trend_condition = trend_score >= self.config.trend_score_threshold
            
            # 计算动量因子
            momentum = self.calculate_momentum_factors(current_data)
            momentum_condition = True
            if momentum:
                momentum_condition1 = momentum['volume_ratio'] > self.config.momentum_volume_ratio_threshold
                momentum_condition2 = momentum['rsi'] > self.config.momentum_rsi_lower and momentum['rsi'] < self.config.momentum_rsi_upper
                momentum_condition3 = momentum['turnover_rate'] > self.config.momentum_turnover_threshold
                
                momentum_score = sum([momentum_condition1, momentum_condition2, momentum_condition3])
                momentum_condition = momentum_score >= self.config.momentum_score_threshold
            
            # 生成买入信号
            if condition1 and condition2 and condition3 and trend_condition and momentum_condition:
                signals.iloc[i] = 1.0
            else:
                signals.iloc[i] = 0.0
        
        return signals
    
    def fit(self, dataset):
        """模型训练 - 对于信号型策略，这里主要是参数校验"""
        from qlib.log import get_module_logger
        self.logger = get_module_logger(__name__)
        self.logger.info("好奇布偶猫BOLL模型训练完成")
        return self
    
    def predict(self, dataset) -> pd.Series:
        """预测交易信号"""
        # 获取数据
        data = dataset.get_data()
        
        # 生成信号
        signals = {}
        for symbol in data.index.get_level_values('instrument').unique():
            symbol_data = data.loc[symbol]
            symbol_signals = self.generate_signals(symbol_data)
            signals[symbol] = symbol_signals
        
        # 合并所有股票的信号
        all_signals = pd.concat(signals, names=['instrument', 'datetime'])
        
        return all_signals


class CuriousRagdollBollStrategy(BaseStrategy):
    """好奇布偶猫BOLL策略"""
    
    def __init__(self, config: CuriousRagdollBollConfig = None, **kwargs):
        super().__init__(**kwargs)
        if config is None:
            config = CuriousRagdollBollConfig()
        self.config = config
        
        # 策略名称
        self.name = "好奇布偶猫BOLL策略"
        
        # 初始化模型
        self.model = CuriousRagdollBollModel(config)
        
        # 设置策略参数
        self.topk = config.fixed_positions
        self.n_drop = 0
    
    def generate_trade_decision(self, execute_result=None):
        """生成交易决策"""
        # 获取信号
        signals = self.signal
        
        # 根据配置选择股票
        trade_decisions = []
        
        for date in signals.index.get_level_values('datetime').unique():
            date_signals = signals.loc[pd.IndexSlice[:, date], :]
            
            # 选择信号最强的股票
            if isinstance(date_signals, pd.Series):
                date_signals = date_signals.to_frame('signal')
            
            # 过滤出有买入信号的股票
            buy_signals = date_signals[date_signals['signal'] > 0.5]
            
            if len(buy_signals) > 0:
                # 按信号强度排序，选择前N只
                buy_signals = buy_signals.sort_values('signal', ascending=False)
                selected_stocks = buy_signals.head(self.config.fixed_positions)
                
                for stock in selected_stocks.index.get_level_values('instrument'):
                    trade_decisions.append({
                        'datetime': date,
                        'instrument': stock,
                        'amount': 1.0 / self.config.fixed_positions,  # 等权重
                        'direction': 1  # 买入
                    })
        
        return trade_decisions
    
    def run_backtest(self, symbols: List[str], start_date: str, end_date: str, benchmark: str = None) -> Dict[str, Any]:
        """运行策略回测"""
        try:
            # 使用内置的回测方法
            backtester = CuriousRagdollBollBacktester(self.config)
            
            # 运行回测
            portfolio_metrics, indicators = backtester.run_backtest(
                start_date=start_date,
                end_date=end_date,
                benchmark=benchmark or "SH000905"
            )
            
            # 分析结果
            results = backtester.analyze_results(portfolio_metrics, indicators)
            
            return results
            
        except Exception as e:
            logging.error(f"策略回测失败: {e}")
            return {}


class CuriousRagdollBollDataHandler:
    """好奇布偶猫BOLL数据处理器"""
    
    def __init__(self, config: CuriousRagdollBollConfig = None):
        if config is None:
            config = CuriousRagdollBollConfig()
        self.config = config
    
    def get_feature_config(self, start_time: str, end_time: str):
        """获取特征配置"""
        return {
            "class": "qlib.contrib.data.handler.Alpha158",
            "kwargs": {
                "start_time": start_time,
                "end_time": end_time,
                "fit_start_time": start_time,
                "fit_end_time": end_time,
                "instruments": "csi500",
                "infer_processors": [
                    {"class": "qlib.data.dataset.processor.RobustZScoreNorm", "kwargs": {"fields_group": "feature"}},
                    {"class": "qlib.data.dataset.processor.Fillna", "kwargs": {"fields_group": "feature"}}
                ],
                "learn_processors": [
                    {"class": "qlib.data.dataset.processor.DropnaLabel"},
                    {"class": "qlib.data.dataset.processor.CSRankNorm", "kwargs": {"fields_group": "label"}}
                ],
                "label": ["Ref($close, -2) / Ref($close, -1) - 1"]
            }
        }
    
    def get_data_config(self, start_time: str, end_time: str, instruments: str = "csi500"):
        """获取数据配置"""
        return {
            "class": "qlib.data.dataset.DatasetH",
            "kwargs": {
                "handler": self.get_feature_config(start_time, end_time),
                "segments": {
                    "train": (start_time, end_time),
                    "valid": (start_time, end_time),
                    "test": (start_time, end_time)
                }
            }
        }


class CuriousRagdollBollBacktester:
    """好奇布偶猫BOLL回测器"""
    
    def __init__(self, config: CuriousRagdollBollConfig = None):
        if config is None:
            config = CuriousRagdollBollConfig()
        self.config = config
        
        # 设置日志
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def run_backtest(self, start_date: str, end_date: str, benchmark: str = "SH000905"):
        """运行回测 - 使用qlib标准回测流程"""
        
        # 使用qlib的标准回测流程
        from qlib.contrib.strategy.strategy import TopkDropoutStrategy
        from qlib.contrib.evaluate import backtest
        from qlib.backtest.executor import SimulatorExecutor
        from qlib.data.dataset import DatasetH
        from qlib.contrib.data.handler import Alpha158
        
        # 创建数据处理器配置
        data_handler_config = {
            "start_time": start_date,
            "end_time": end_date,
            "fit_start_time": start_date,
            "fit_end_time": end_date,
            "instruments": "csi500",
            "infer_processors": [
                {"class": "RobustZScoreNorm", "kwargs": {"fields_group": "feature"}},
                {"class": "Fillna", "kwargs": {"fields_group": "feature"}}
            ],
            "learn_processors": [
                {"class": "DropnaLabel"},
                {"class": "CSRankNorm", "kwargs": {"fields_group": "label"}}
            ],
            "label": ["Ref($close, -2) / Ref($close, -1) - 1"]
        }
        
        # 创建数据集
        dataset = DatasetH(data_handler_config)
        
        # 使用策略模型生成预测
        model = CuriousRagdollBollModel(self.config)
        predictions = model.predict(dataset)
        
        # 创建qlib标准策略
        strategy = TopkDropoutStrategy(
            topk=self.config.fixed_positions,
            n_drop=0,
            signal=predictions
        )
        
        # 配置回测参数
        backtest_config = {
            "limit_threshold": 0.095,
            "account": 10000000,
            "benchmark": benchmark,
            "deal_price": "close",
            "open_cost": 0.0005,
            "close_cost": 0.0015,
            "min_cost": 5,
            "trade_unit": 100,
            "generate_portfolio_metrics": True
        }
        
        # 执行qlib标准回测
        report, positions = backtest(predictions, **backtest_config)
        
        # 提取标准回测结果
        portfolio_metric_dict = {
            'excess_return_with_cost': report['return'] - report['bench'],
            'portfolio_return': report['return'],
            'benchmark_return': report['bench'],
            'turnover': report.get('turnover', pd.Series()),
            'positions': positions
        }
        
        # 计算详细指标
        total_return = report['return'].iloc[-1]
        excess_return = (report['return'] - report['bench']).iloc[-1]
        
        indicator_dict = {
            'total_return': total_return,
            'excess_return': excess_return,
            'benchmark_return': report['bench'].iloc[-1],
            'trading_days': len(report),
            'total_trades': len(positions),
            'turnover_rate': report.get('turnover', pd.Series()).mean()
        }
        
        return portfolio_metric_dict, indicator_dict
    
    def analyze_results(self, portfolio_metric_dict, indicator_dict):
        """分析回测结果 - 使用qlib内置分析功能"""
        from qlib.contrib.evaluate import risk_analysis
        
        results = {}
        
        # 使用qlib内置的风险分析功能
        if 'portfolio_return' in portfolio_metric_dict and 'benchmark_return' in portfolio_metric_dict:
            portfolio_return = portfolio_metric_dict['portfolio_return']
            benchmark_return = portfolio_metric_dict['benchmark_return']
            
            # 使用qlib的风险分析
            risk_metrics = risk_analysis(
                portfolio_return, 
                benchmark_return, 
                freq='daily'
            )
            
            # 提取qlib标准指标
            results.update({
                'annual_return': risk_metrics.get('annual_return', 0),
                'max_drawdown': risk_metrics.get('max_drawdown', 0),
                'sharpe_ratio': risk_metrics.get('sharpe_ratio', 0),
                'information_ratio': risk_metrics.get('information_ratio', 0),
                'volatility': risk_metrics.get('volatility', 0),
                'downside_deviation': risk_metrics.get('downside_deviation', 0),
                'calmar_ratio': risk_metrics.get('calmar_ratio', 0),
                'sortino_ratio': risk_metrics.get('sortino_ratio', 0)
            })
            
            # 计算交易统计
            if 'positions' in portfolio_metric_dict:
                positions = portfolio_metric_dict['positions']
                
                # 计算交易次数和胜率
                trades = self._analyze_trades(positions)
                results.update(trades)
            
            # 计算胜率 (基于日收益)
            daily_returns = portfolio_return.pct_change().dropna()
            win_rate = (daily_returns > 0).mean()
            results['win_rate'] = win_rate
        
        # 添加其他指标
        results.update(indicator_dict)
        
        return results
    
    def _analyze_trades(self, positions):
        """分析交易记录"""
        if positions is None or len(positions) == 0:
            return {
                'total_trades': 0,
                'winning_trades': 0,
                'losing_trades': 0,
                'trade_win_rate': 0,
                'avg_winning_trade': 0,
                'avg_losing_trade': 0,
                'max_winning_trade': 0,
                'max_losing_trade': 0
            }
        
        # 分析每笔交易的盈亏
        trades = []
        for date, position_data in positions.items():
            if isinstance(position_data, dict):
                for instrument, trade_info in position_data.items():
                    if 'pnl' in trade_info:
                        trades.append(trade_info['pnl'])
        
        if not trades:
            return {
                'total_trades': 0,
                'winning_trades': 0,
                'losing_trades': 0,
                'trade_win_rate': 0,
                'avg_winning_trade': 0,
                'avg_losing_trade': 0,
                'max_winning_trade': 0,
                'max_losing_trade': 0
            }
        
        trades = np.array(trades)
        winning_trades = trades[trades > 0]
        losing_trades = trades[trades < 0]
        
        return {
            'total_trades': len(trades),
            'winning_trades': len(winning_trades),
            'losing_trades': len(losing_trades),
            'trade_win_rate': len(winning_trades) / len(trades) if len(trades) > 0 else 0,
            'avg_winning_trade': winning_trades.mean() if len(winning_trades) > 0 else 0,
            'avg_losing_trade': losing_trades.mean() if len(losing_trades) > 0 else 0,
            'max_winning_trade': winning_trades.max() if len(winning_trades) > 0 else 0,
            'max_losing_trade': losing_trades.min() if len(losing_trades) > 0 else 0
        }
    
    def save_results(self, results: Dict, output_dir: str):
        """保存回测结果"""
        import os
        import json
        from datetime import datetime
        
        # 创建输出目录
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        strategy_dir = os.path.join(output_dir, f"curious_ragdoll_boll_{timestamp}")
        os.makedirs(strategy_dir, exist_ok=True)
        
        # 保存结果
        results_file = os.path.join(strategy_dir, "backtest_results.json")
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False, default=str)
        
        self.logger.info(f"回测结果已保存到: {strategy_dir}")
        
        return strategy_dir


# 策略工厂函数
def create_curious_ragdoll_boll_strategy(config: CuriousRagdollBollConfig = None):
    """创建好奇布偶猫BOLL策略实例"""
    return CuriousRagdollBollStrategy(config)


# 默认配置实例
DEFAULT_CONFIG = CuriousRagdollBollConfig()


# 示例使用
if __name__ == "__main__":
    # 初始化qlib环境
    # qlib.init(provider_uri="~/.qlib/qlib_data/cn_data", region="cn")
    
    # 创建策略配置
    config = CuriousRagdollBollConfig(
        boll_period=20,
        boll_std=2.0,
        stock_pool_size=50,
        fixed_positions=10,
        stop_loss_pct=0.08,
        take_profit_pct=0.15
    )
    
    # 创建回测器
    backtester = CuriousRagdollBollBacktester(config)
    
    # 运行回测
    portfolio_metrics, indicators = backtester.run_backtest(
        start_date="2020-01-01",
        end_date="2023-12-31",
        benchmark="SH000905"
    )
    
    # 分析结果
    results = backtester.analyze_results(portfolio_metrics, indicators)
    
    # 保存结果
    output_dir = "/Users/libing/kk_Projects/kk_Stock/kk_stock_backend/abu_quantitative/results"
    backtester.save_results(results, output_dir)
    
    # 打印关键指标
    print("回测结果:")
    print(f"年化收益率: {results.get('annual_return', 0):.2%}")
    print(f"最大回撤: {results.get('max_drawdown', 0):.2%}")
    print(f"夏普比率: {results.get('sharpe_ratio', 0):.2f}")
    print(f"胜率: {results.get('win_rate', 0):.2%}")