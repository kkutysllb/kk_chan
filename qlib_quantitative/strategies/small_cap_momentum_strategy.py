#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小市值动量突破策略 - Abu框架版本
基于原有小市值动量策略移植到Abu框架

策略特点：
1. 市值小于100亿的中小盘股票
2. 成交量作为主要参考指标
3. 结合MACD、KDJ、RSI技术指标
4. 关联筹码分布和胜率统计数据
5. 基于3因子策略思想优化
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import logging
from dataclasses import dataclass
import warnings

# Abu框架导入
import abupy as abu
from abupy import AbuFactorBuyBase, AbuFactorSellBase
from abupy import AbuBenchmark, AbuCapital, AbuKLManager
from abupy import AbuMetricsBase

# 本地导入
from ..core.strategy_base import AbuStrategyBase
from ..core.data_adapter import AbuDataAdapter

warnings.filterwarnings("ignore")


@dataclass
class SmallCapMomentumConfig:
    """小市值动量策略配置"""
    # 基础配置
    initial_capital: float = 1000000  # 初始资金
    position_size: float = 0.04       # 单股最大仓位4%
    
    # 市值筛选参数（放宽限制）
    max_market_cap: float = 2000000.0   # 最大市值200亿（万元）
    min_market_cap: float = 50000.0     # 最小市值5亿（万元）
    
    # 成交量参数（降低要求）
    volume_ratio_min: float = 0.6       # 量比最低要求
    volume_ratio_strong: float = 1.0    # 强势量比阈值
    volume_ma_period: int = 20           # 成交量均线周期
    volume_surge_ratio: float = 1.2      # 成交量放大倍数
    volume_consistency_days: int = 2     # 成交量持续放大天数
    
    # 换手率参数（放宽范围）
    turnover_rate_min: float = 0.5       # 换手率最低要求0.5%
    turnover_rate_max: float = 20.0      # 换手率上限20%
    
    # 评分参数（降低门槛）
    min_total_score: float = 0.45        # 最低总分要求（归一化后）
    strong_signal_score: float = 0.65    # 强信号分数阈值
    
    # 技术指标参数
    macd_fast: int = 12
    macd_slow: int = 26
    macd_signal: int = 9
    kdj_period: int = 9
    kdj_overbought: float = 80
    kdj_oversold: float = 20
    rsi_period: int = 14
    rsi_overbought: float = 70
    rsi_oversold: float = 30
    
    # 风险控制参数（改善盈亏比）
    stop_loss: float = 0.08              # 止损8%（给予更多波动空间）
    take_profit: float = 0.12            # 止盈12%（更现实的目标）
    max_single_stock: float = 0.06       # 单股最大权重6%（降低集中度风险）
    
    # 动态止损参数
    trailing_stop_activation: float = 0.05  # 移动止损激活点5%
    trailing_stop_distance: float = 0.03    # 移动止损距离3%
    
    # 因子权重参数
    volume_factor_weight: float = 0.4    # 成交量因子权重
    technical_factor_weight: float = 0.3  # 技术因子权重
    quality_factor_weight: float = 0.3    # 质量因子权重


class SmallCapMomentumBuyFactor(AbuFactorBuyBase):
    """小市值动量买入因子"""
    
    def __init__(self, config: SmallCapMomentumConfig = None):
        super().__init__()
        self.config = config or SmallCapMomentumConfig()
        self.data_adapter = AbuDataAdapter()
        
        # 策略状态
        self.last_rebalance_date = None
        self.rebalance_frequency = 10  # 每10个交易日调仓一次（降低频率）
        self.min_holding_days = 3      # 最小持仓天数
        
    def _init_self(self, **kwargs):
        """初始化买入因子"""
        # 获取股票代码
        self.symbol = self.kl_pd.name if hasattr(self.kl_pd, 'name') else 'unknown'
        
    def _get_market_regime(self, current_data: pd.Series) -> str:
        """判断市场状态"""
        try:
            # 获取基准指数（如沪深300）的近期表现
            if self.today_ind < 20:
                return "neutral"
            
            # 计算最近20天的收益率
            recent_returns = self.kl_pd.iloc[self.today_ind-20:self.today_ind]['close'].pct_change()
            avg_return = recent_returns.mean()
            volatility = recent_returns.std()
            
            if avg_return > 0.002 and volatility < 0.03:  # 温和上涨
                return "bullish"
            elif avg_return < -0.002 and volatility > 0.03:  # 下跌且波动大
                return "bearish"
            else:
                return "neutral"
                
        except:
            return "neutral"
        
    def _check_market_cap_condition(self, current_data: pd.Series) -> bool:
        """检查市值条件"""
        try:
            # 从数据适配器获取市值数据
            market_cap = current_data.get('total_mv', 0)  # 总市值，单位万元
            if market_cap == 0:
                # 如果没有市值数据，尝试从其他字段获取
                market_cap = current_data.get('market_cap', 0)
                
            return self.config.min_market_cap <= market_cap <= self.config.max_market_cap
        except:
            return False
            
    def _analyze_volume_momentum(self, current_data: pd.Series) -> float:
        """成交量动量分析（满分15分）"""
        score = 0.0
        
        try:
            # 获取当前数据
            volume_ratio = current_data.get('volume_ratio', 1.0)
            turnover_rate = current_data.get('turnover_rate_f', 0)
            current_price = current_data.get('close', 0)
            amount = current_data.get('amount', 0)
            
            # 1. 量比评分（5分）
            if volume_ratio >= 2.0:
                score += 5
            elif volume_ratio >= 1.5:
                score += 4
            elif volume_ratio >= 1.2:
                score += 3
            elif volume_ratio >= 1.0:
                score += 2
            elif volume_ratio >= 0.8:
                score += 1
                
            # 2. 换手率评分（5分）
            if 2.0 <= turnover_rate <= 8.0:  # 理想换手率区间
                score += 5
            elif 1.5 <= turnover_rate <= 10.0:
                score += 4
            elif 1.0 <= turnover_rate <= 12.0:
                score += 3
            elif 0.8 <= turnover_rate <= 15.0:
                score += 2
            elif 0.5 <= turnover_rate <= 20.0:
                score += 1
                
            # 3. 成交额评分（5分）
            if amount > 0:
                # 成交额越大，流动性越好
                if amount >= 100000:  # 1亿以上
                    score += 5
                elif amount >= 50000:  # 5000万以上
                    score += 4
                elif amount >= 20000:  # 2000万以上
                    score += 3
                elif amount >= 10000:  # 1000万以上
                    score += 2
                elif amount >= 5000:   # 500万以上
                    score += 1
                    
        except Exception as e:
            pass
            
        return min(score, 15.0)
        
    def _analyze_technical_indicators(self, current_data: pd.Series) -> float:
        """技术指标分析（满分8分）- 简化版本"""
        score = 0.0
        
        try:
            # 1. 价格动量评分（4分）- 替代复杂的技术指标
            close = current_data.get('close', 0)
            if self.today_ind >= 5:
                prev_close = self.kl_pd.iloc[self.today_ind-5]['close']
                momentum = (close - prev_close) / prev_close
                
                if momentum > 0.03:  # 5日涨幅超过3%
                    score += 4
                elif momentum > 0.01:  # 5日涨幅超过1%
                    score += 3
                elif momentum > 0:  # 5日正收益
                    score += 2
                elif momentum > -0.02:  # 5日跌幅小于2%
                    score += 1
                    
            # 2. 相对强度评分（4分）- 相对于市场的表现
            if self.today_ind >= 10:
                stock_returns = self.kl_pd.iloc[self.today_ind-10:self.today_ind]['close'].pct_change()
                avg_return = stock_returns.mean()
                
                if avg_return > 0.005:  # 平均日收益率超过0.5%
                    score += 4
                elif avg_return > 0.002:  # 平均日收益率超过0.2%
                    score += 3
                elif avg_return > 0:  # 平均日收益率为正
                    score += 2
                elif avg_return > -0.002:  # 平均日收益率大于-0.2%
                    score += 1
                    
        except Exception as e:
            pass
            
        return min(score, 8.0)
        
    def _analyze_quality_factors(self, current_data: pd.Series) -> float:
        """质量因子分析（满分4分）"""
        score = 0.0
        
        try:
            # 1. 价格位置评分（2分）
            close = current_data.get('close', 0)
            high_52w = current_data.get('high_52w', close)  # 52周最高价
            low_52w = current_data.get('low_52w', close)    # 52周最低价
            
            if high_52w > low_52w:
                price_position = (close - low_52w) / (high_52w - low_52w)
                if 0.3 <= price_position <= 0.8:  # 理想价格位置
                    score += 2
                elif 0.2 <= price_position <= 0.9:
                    score += 1
                    
            # 2. 波动率评分（2分）
            atr = current_data.get('atr_qfq', 0)
            if close > 0 and atr > 0:
                volatility = atr / close
                if 0.02 <= volatility <= 0.06:  # 适中波动率
                    score += 2
                elif 0.01 <= volatility <= 0.08:
                    score += 1
                    
        except Exception as e:
            pass
            
        return min(score, 4.0)
        
    def _calculate_multi_factor_score(self, current_data: pd.Series) -> float:
        """计算多因子综合得分"""
        # 计算各因子得分
        volume_score = self._analyze_volume_momentum(current_data)
        technical_score = self._analyze_technical_indicators(current_data)
        quality_score = self._analyze_quality_factors(current_data)
        
        # 加权计算总分
        total_score = (
            volume_score * self.config.volume_factor_weight +
            technical_score * self.config.technical_factor_weight +
            quality_score * self.config.quality_factor_weight
        )
        
        # 归一化到0-1区间
        max_possible_score = (
            15 * self.config.volume_factor_weight +
            8 * self.config.technical_factor_weight +
            4 * self.config.quality_factor_weight
        )
        
        normalized_score = total_score / max_possible_score if max_possible_score > 0 else 0
        
        return normalized_score
        
    def _should_rebalance(self, current_date: datetime) -> bool:
        """判断是否需要调仓"""
        if self.last_rebalance_date is None:
            return True
            
        # 计算交易日差异（简化处理）
        days_diff = (current_date - self.last_rebalance_date).days
        return days_diff >= self.rebalance_frequency
        
    def fit_month(self, today):
        """Abu框架买入信号判断"""
        if self.today_ind < 30:  # 需要足够的历史数据
            return None
            
        try:
            current_date = self.kl_pd.index[self.today_ind]
            current_data = self.kl_pd.iloc[self.today_ind]
            
            # 1. 市场状态检查
            market_regime = self._get_market_regime(current_data)
            if market_regime == "bearish":
                # 熊市中提高选股标准
                min_score = self.config.min_total_score + 0.1
            else:
                min_score = self.config.min_total_score
            
            # 2. 检查市值条件
            if not self._check_market_cap_condition(current_data):
                return None
                
            # 3. 检查基础流动性条件（放宽要求）
            volume_ratio = current_data.get('volume_ratio', 0)
            turnover_rate = current_data.get('turnover_rate_f', 0)
            
            if (volume_ratio < self.config.volume_ratio_min or 
                turnover_rate < self.config.turnover_rate_min or 
                turnover_rate > self.config.turnover_rate_max):
                return None
                
            # 4. 计算多因子得分
            score = self._calculate_multi_factor_score(current_data)
            
            # 5. 检查得分阈值（根据市场状态调整）
            if score < min_score:
                return None
                
            # 6. 检查调仓频率
            if not self._should_rebalance(current_date):
                return None
                
            # 7. 额外的趋势确认（减少假信号）
            close = current_data.get('close', 0)
            if self.today_ind >= 3:
                prev_close = self.kl_pd.iloc[self.today_ind-3]['close']
                if close <= prev_close:  # 要求价格在上升趋势中
                    return None
                
            # 8. 生成买入信号
            self.last_rebalance_date = current_date
            return self.buy_today()
            
        except Exception as e:
            return None


class SmallCapMomentumSellFactor(AbuFactorSellBase):
    """小市值动量卖出因子"""
    
    def __init__(self, config: SmallCapMomentumConfig = None):
        super().__init__()
        self.config = config or SmallCapMomentumConfig()
        
    def _init_self(self, **kwargs):
        """初始化卖出因子"""
        self.symbol = self.kl_pd.name if hasattr(self.kl_pd, 'name') else 'unknown'
        
    def fit_month(self, today):
        """Abu框架卖出信号判断"""
        if not self.read_fit_month(today):
            return None
            
        try:
            current_data = self.kl_pd.iloc[self.today_ind]
            
            # 1. 止损止盈检查
            if hasattr(self, 'buy_price') and self.buy_price > 0:
                current_price = current_data['close']
                pnl_ratio = (current_price - self.buy_price) / self.buy_price
                
                # 止损：亏损超过8%
                if pnl_ratio <= -self.config.stop_loss:
                    return self.sell_today()
                    
                # 止盈：盈利超过12%
                if pnl_ratio >= self.config.take_profit:
                    return self.sell_today()
                    
                # 移动止损：盈利超过5%后启动
                if pnl_ratio >= self.config.trailing_stop_activation:
                    # 检查是否从高点回落超过3%
                    if self.today_ind >= 5:
                        recent_highs = self.kl_pd.iloc[self.today_ind-5:self.today_ind]['high']
                        max_high = recent_highs.max()
                        if max_high > 0:
                            drawdown = (max_high - current_price) / max_high
                            if drawdown >= self.config.trailing_stop_distance:
                                return self.sell_today()
                    
            # 2. 持仓时间检查
            if hasattr(self, 'buy_date') and self.buy_date:
                holding_days = (self.kl_pd.index[self.today_ind] - self.buy_date).days
                # 最小持仓期限，避免过度交易
                if holding_days < self.config.min_holding_days:
                    return None
                    
            # 3. 趋势恶化检查
            close = current_data.get('close', 0)
            if self.today_ind >= 5:
                # 连续5天下跌
                recent_closes = self.kl_pd.iloc[self.today_ind-4:self.today_ind+1]['close']
                if len(recent_closes) >= 5:
                    declining_days = sum(1 for i in range(1, len(recent_closes)) 
                                       if recent_closes.iloc[i] < recent_closes.iloc[i-1])
                    if declining_days >= 4:  # 连续4天下跌
                        return self.sell_today()
                        
            # 4. 成交量萎缩检查
            volume_ratio = current_data.get('volume_ratio', 1.0)
            if volume_ratio < 0.3:  # 成交量严重萎缩
                return self.sell_today()
                
            return None
            
        except Exception as e:
            return None


class AbuSmallCapMomentumStrategy(AbuStrategyBase):
    """Abu框架小市值动量策略"""
    
    def __init__(self, config: SmallCapMomentumConfig = None):
        self.config = config or SmallCapMomentumConfig()
        super().__init__()
        
    def setup_buy_factors(self):
        """设置买入因子"""
        return [SmallCapMomentumBuyFactor(self.config)]
        
    def setup_sell_factors(self):
        """设置卖出因子"""
        return [SmallCapMomentumSellFactor(self.config)]
        
    def setup_position_factors(self):
        """设置仓位管理因子"""
        # 使用ATR止损和仓位管理
        from abupy import AbuFactorAtrNStop, AbuFactorPreAtrNStop
        return [
            AbuFactorAtrNStop(stop_loss_n=self.config.stop_loss, stop_win_n=self.config.take_profit),
            AbuFactorPreAtrNStop(pre_atr_n=1.0)
        ]
        
    def get_strategy_name(self) -> str:
        """获取策略名称"""
        return "小市值动量突破策略"
        
    def get_strategy_description(self) -> str:
        """获取策略描述"""
        return "基于小市值股票的动量突破策略，结合成交量、技术指标和质量因子进行选股"
        
    def get_stock_pool(self, date: datetime = None) -> List[str]:
        """获取小市值股票池"""
        try:
            if date is None:
                date = datetime.now()
                
            # 使用数据适配器获取股票列表
            data_adapter = AbuDataAdapter()
            stock_list = data_adapter.get_stock_list(date)
            
            # 筛选小市值股票
            small_cap_stocks = []
            for stock_code in stock_list[:500]:  # 限制查询数量
                try:
                    # 获取市值数据
                    factor_data = data_adapter.get_factor_data(
                        [stock_code], ['total_mv'], date
                    )
                    
                    if 'total_mv' in factor_data and not factor_data['total_mv'].empty:
                        market_cap = factor_data['total_mv'].iloc[0, 0]
                        if self.config.min_market_cap <= market_cap <= self.config.max_market_cap:
                            small_cap_stocks.append(stock_code)
                            
                except Exception as e:
                    continue
                    
            return small_cap_stocks[:100]  # 返回前100只
            
        except Exception as e:
            return []