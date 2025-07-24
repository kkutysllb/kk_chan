#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
多趋势共振策略 - Abu框架版本
基于原有策略移植到Abu框架

核心特点：
1. 严格的多时间周期趋势共振分析
2. 基于MACD、KDJ、RSI等技术指标
3. 实现T+1交易规则
4. 减少交易频率，提高信号质量
5. 按手数买入
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import logging
from dataclasses import dataclass

# Abu框架导入
import abupy as abu
from abupy import AbuFactorBuyBase, AbuFactorSellBase
from abupy import AbuBenchmark, AbuCapital, AbuKLManager
from abupy import AbuMetricsBase

# 本地导入
from ..core.strategy_base import AbuStrategyBase
from ..core.data_adapter import AbuDataAdapter


@dataclass
class MultiTrendResonanceConfig:
    """多趋势共振策略配置"""
    # 基础配置
    initial_capital: float = 1000000  # 初始资金
    max_position_ratio: float = 0.1   # 单只股票最大仓位比例
    stop_loss: float = 0.08           # 止损比例
    take_profit: float = 0.15         # 止盈比例
    
    # MACD参数
    macd_fast: int = 12
    macd_slow: int = 26
    macd_signal: int = 9
    
    # KDJ参数
    kdj_period: int = 9
    kdj_overbought: float = 80
    kdj_oversold: float = 20
    
    # RSI参数
    rsi_period: int = 12
    rsi_overbought: float = 80
    rsi_oversold: float = 20
    
    # 成交量参数
    volume_ma_period: int = 20
    volume_ratio_threshold: float = 1.5
    
    # 趋势判断参数
    trend_strength_threshold: float = 3.0
    resonance_threshold: float = 2  # 至少需要2个周期共振
    
    # 风险控制参数
    max_drawdown: float = 0.15
    max_daily_trades: int = 2
    min_holding_days: int = 3
    
    # T+1交易参数
    enable_t1_rule: bool = True
    

class MultiTrendResonanceBuyFactor(AbuFactorBuyBase):
    """多趋势共振买入因子"""
    
    def __init__(self, config: MultiTrendResonanceConfig = None):
        super().__init__()
        self.config = config or MultiTrendResonanceConfig()
        self.data_adapter = AbuDataAdapter()
        
        # 策略状态
        self.buy_dates = {}  # 记录买入日期
        self.entry_prices = {}  # 记录买入价格
        self.daily_buy_count = {}  # 每日买入计数
        
    def _init_self(self, **kwargs):
        """初始化买入因子"""
        # 获取股票代码
        self.symbol = self.kl_pd.name if hasattr(self.kl_pd, 'name') else 'unknown'
        
        # 计算技术指标
        self._calculate_indicators()
        
    def _calculate_indicators(self):
        """计算技术指标"""
        # MACD
        self.kl_pd['macd_dif'], self.kl_pd['macd_dea'], self.kl_pd['macd_hist'] = self._calculate_macd(
            self.kl_pd['close'], self.config.macd_fast, self.config.macd_slow, self.config.macd_signal
        )
        
        # KDJ
        self.kl_pd['kdj_k'], self.kl_pd['kdj_d'], self.kl_pd['kdj_j'] = self._calculate_kdj(
            self.kl_pd['high'], self.kl_pd['low'], self.kl_pd['close'], self.config.kdj_period
        )
        
        # RSI
        self.kl_pd['rsi'] = self._calculate_rsi(self.kl_pd['close'], self.config.rsi_period)
        
        # 成交量比率
        self.kl_pd['volume_ma'] = self.kl_pd['volume'].rolling(window=self.config.volume_ma_period).mean()
        self.kl_pd['volume_ratio'] = self.kl_pd['volume'] / self.kl_pd['volume_ma']
        
    def _calculate_macd(self, close_prices, fast_period, slow_period, signal_period):
        """计算MACD指标"""
        exp1 = close_prices.ewm(span=fast_period).mean()
        exp2 = close_prices.ewm(span=slow_period).mean()
        macd_dif = exp1 - exp2
        macd_dea = macd_dif.ewm(span=signal_period).mean()
        macd_hist = macd_dif - macd_dea
        return macd_dif, macd_dea, macd_hist
        
    def _calculate_kdj(self, high_prices, low_prices, close_prices, period):
        """计算KDJ指标"""
        low_min = low_prices.rolling(window=period).min()
        high_max = high_prices.rolling(window=period).max()
        
        rsv = (close_prices - low_min) / (high_max - low_min) * 100
        k = rsv.ewm(com=2).mean()
        d = k.ewm(com=2).mean()
        j = 3 * k - 2 * d
        
        return k, d, j
        
    def _calculate_rsi(self, close_prices, period):
        """计算RSI指标"""
        delta = close_prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
        
    def _generate_weekly_data(self, current_index):
        """生成周线数据"""
        try:
            current_date = self.kl_pd.index[current_index]
            
            # 找到当前日期所在的周
            current_week_start = current_date - timedelta(days=current_date.weekday())
            current_week_end = current_week_start + timedelta(days=6)
            
            # 获取当周的数据
            week_mask = (self.kl_pd.index >= current_week_start) & (self.kl_pd.index <= current_week_end)
            week_data = self.kl_pd[week_mask]
            
            if week_data.empty:
                return None
                
            # 计算周线OHLC
            weekly_data = {
                'open': week_data['open'].iloc[0],
                'high': week_data['high'].max(),
                'low': week_data['low'].min(),
                'close': week_data['close'].iloc[-1],
                'volume': week_data['volume'].sum(),
                'macd_dif': week_data['macd_dif'].iloc[-1] if 'macd_dif' in week_data.columns else 0,
                'macd_dea': week_data['macd_dea'].iloc[-1] if 'macd_dea' in week_data.columns else 0,
                'kdj_k': week_data['kdj_k'].iloc[-1] if 'kdj_k' in week_data.columns else 50,
                'kdj_d': week_data['kdj_d'].iloc[-1] if 'kdj_d' in week_data.columns else 50,
                'rsi': week_data['rsi'].iloc[-1] if 'rsi' in week_data.columns else 50,
            }
            
            return pd.Series(weekly_data)
            
        except Exception as e:
            return None
            
    def _generate_monthly_data(self, current_index):
        """生成月线数据"""
        try:
            current_date = self.kl_pd.index[current_index]
            
            # 找到当前月份的数据
            current_month_start = current_date.replace(day=1)
            if current_month_start.month == 12:
                next_month = current_month_start.replace(year=current_month_start.year + 1, month=1)
            else:
                next_month = current_month_start.replace(month=current_month_start.month + 1)
            
            # 获取当月的数据
            month_mask = (self.kl_pd.index >= current_month_start) & (self.kl_pd.index < next_month)
            month_data = self.kl_pd[month_mask]
            
            if month_data.empty:
                return None
                
            # 计算月线OHLC
            monthly_data = {
                'open': month_data['open'].iloc[0],
                'high': month_data['high'].max(),
                'low': month_data['low'].min(),
                'close': month_data['close'].iloc[-1],
                'volume': month_data['volume'].sum(),
                'macd_dif': month_data['macd_dif'].iloc[-1] if 'macd_dif' in month_data.columns else 0,
                'macd_dea': month_data['macd_dea'].iloc[-1] if 'macd_dea' in month_data.columns else 0,
                'kdj_k': month_data['kdj_k'].iloc[-1] if 'kdj_k' in month_data.columns else 50,
                'kdj_d': month_data['kdj_d'].iloc[-1] if 'kdj_d' in month_data.columns else 50,
                'rsi': month_data['rsi'].iloc[-1] if 'rsi' in month_data.columns else 50,
            }
            
            return pd.Series(monthly_data)
            
        except Exception as e:
            return None
            
    def _analyze_trend(self, data, timeframe: str) -> str:
        """分析单个时间周期的趋势"""
        if data is None or data.empty:
            return 'neutral'
            
        try:
            trend_score = 0
            
            # 获取技术指标数据
            macd_dif = data.get('macd_dif', 0)
            macd_dea = data.get('macd_dea', 0)
            kdj_k = data.get('kdj_k', 50)
            kdj_d = data.get('kdj_d', 50)
            rsi = data.get('rsi', 50)
            volume_ratio = data.get('volume_ratio', 1)
            
            # 1. MACD多头信号（权重更高）
            if macd_dif > macd_dea and macd_dif > 0:
                trend_score += 2.5  # 强烈多头
            elif macd_dif > macd_dea:
                trend_score += 1.5  # 一般多头
            elif macd_dif < macd_dea and macd_dif < 0:
                trend_score -= 1.5  # 空头
                
            # 2. KDJ金叉信号
            if kdj_k > kdj_d and kdj_k < 80:  # 金叉且不超买
                trend_score += 2
            elif kdj_k > kdj_d:
                trend_score += 1
            elif kdj_k < kdj_d:
                trend_score -= 1
                
            # 3. RSI超买超卖
            if 30 < rsi < 70:  # 正常区间
                trend_score += 1
            elif rsi < 30:  # 超卖
                trend_score += 1.5
            elif rsi > 80:  # 超买
                trend_score -= 1.5
                
            # 4. 成交量确认
            if volume_ratio > 1:
                trend_score += 0.5
                
            # 趋势判断
            if trend_score >= 5:
                return 'strong_bullish'
            elif trend_score >= 3:
                return 'bullish'
            elif trend_score >= 1:
                return 'weak_bullish'
            elif trend_score >= -1:
                return 'neutral'
            else:
                return 'bearish'
                
        except Exception as e:
            return 'neutral'
            
    def _check_trend_resonance(self, daily_trend: str, weekly_trend: str, monthly_trend: str) -> str:
        """检查多时间周期趋势共振"""
        try:
            bullish_trends = ['strong_bullish', 'bullish', 'weak_bullish']
            neutral_trends = ['neutral']
            
            # 强烈看涨：需要所有周期都看涨
            if (daily_trend == 'strong_bullish' and 
                weekly_trend in bullish_trends and 
                monthly_trend in bullish_trends):
                return 'buy'
                
            # 一般看涨：至少两个周期看涨，第三个中性或看涨
            elif (daily_trend in bullish_trends and 
                  weekly_trend in bullish_trends and 
                  monthly_trend in (bullish_trends + neutral_trends)):
                return 'buy'
                
            # 日线强烈看涨 + 周线支持
            elif (daily_trend == 'strong_bullish' and 
                  weekly_trend in (bullish_trends + neutral_trends)):
                return 'buy'
                
            return 'hold'
            
        except Exception as e:
            return 'hold'
            
    def _calculate_resonance_strength(self, daily_trend: str, weekly_trend: str, monthly_trend: str) -> float:
        """计算共振强度分数"""
        trend_scores = {
            'strong_bullish': 4,
            'bullish': 3,
            'weak_bullish': 2,
            'neutral': 1,
            'bearish': 0
        }
        
        daily_score = trend_scores.get(daily_trend, 0)
        weekly_score = trend_scores.get(weekly_trend, 0) if weekly_trend else 0
        monthly_score = trend_scores.get(monthly_trend, 0) if monthly_trend else 0
        
        # 日线权重50%，周线30%，月线20%
        total_score = daily_score * 0.5 + weekly_score * 0.3 + monthly_score * 0.2
        return total_score
        
    def fit_month(self, today):
        """Abu框架买入信号判断"""
        if self.today_ind < 30:  # 需要足够的历史数据
            return None
            
        try:
            # 获取当前数据
            current_data = self.kl_pd.iloc[self.today_ind]
            current_date = self.kl_pd.index[self.today_ind]
            
            # 检查T+1规则
            if self.config.enable_t1_rule:
                if self.symbol in self.buy_dates:
                    last_buy_date = self.buy_dates[self.symbol]
                    if (current_date - last_buy_date).days < 1:
                        return None
                        
            # 检查每日买入限制
            date_str = current_date.strftime('%Y-%m-%d')
            if self.daily_buy_count.get(date_str, 0) >= self.config.max_daily_trades:
                return None
                
            # 生成多时间周期数据
            weekly_data = self._generate_weekly_data(self.today_ind)
            monthly_data = self._generate_monthly_data(self.today_ind)
            
            # 分析趋势
            daily_trend = self._analyze_trend(current_data, "日线")
            weekly_trend = self._analyze_trend(weekly_data, "周线") if weekly_data is not None else None
            monthly_trend = self._analyze_trend(monthly_data, "月线") if monthly_data is not None else None
            
            # 检查趋势共振
            resonance_signal = self._check_trend_resonance(daily_trend, weekly_trend, monthly_trend)
            
            if resonance_signal == 'buy':
                # 计算共振强度分数
                strength_score = self._calculate_resonance_strength(daily_trend, weekly_trend, monthly_trend)
                
                if strength_score >= self.config.trend_strength_threshold:
                    # 记录买入信息
                    self.buy_dates[self.symbol] = current_date
                    self.entry_prices[self.symbol] = current_data['close']
                    
                    # 更新每日买入计数
                    self.daily_buy_count[date_str] = self.daily_buy_count.get(date_str, 0) + 1
                    
                    return self.buy_today()
                    
            return None
            
        except Exception as e:
            return None


class MultiTrendResonanceSellFactor(AbuFactorSellBase):
    """多趋势共振卖出因子"""
    
    def __init__(self, config: MultiTrendResonanceConfig = None):
        super().__init__()
        self.config = config or MultiTrendResonanceConfig()
        
    def _init_self(self, **kwargs):
        """初始化卖出因子"""
        self.symbol = self.kl_pd.name if hasattr(self.kl_pd, 'name') else 'unknown'
        
        # 计算技术指标（与买入因子相同）
        self._calculate_indicators()
        
    def _calculate_indicators(self):
        """计算技术指标"""
        # RSI
        self.kl_pd['rsi'] = self._calculate_rsi(self.kl_pd['close'], self.config.rsi_period)
        
        # MACD
        self.kl_pd['macd_dif'], self.kl_pd['macd_dea'], self.kl_pd['macd_hist'] = self._calculate_macd(
            self.kl_pd['close'], self.config.macd_fast, self.config.macd_slow, self.config.macd_signal
        )
        
        # KDJ
        self.kl_pd['kdj_k'], self.kl_pd['kdj_d'], self.kl_pd['kdj_j'] = self._calculate_kdj(
            self.kl_pd['high'], self.kl_pd['low'], self.kl_pd['close'], self.config.kdj_period
        )
        
        # 成交量比率
        self.kl_pd['volume_ma'] = self.kl_pd['volume'].rolling(window=self.config.volume_ma_period).mean()
        self.kl_pd['volume_ratio'] = self.kl_pd['volume'] / self.kl_pd['volume_ma']
        
    def _calculate_macd(self, close_prices, fast_period, slow_period, signal_period):
        """计算MACD指标"""
        exp1 = close_prices.ewm(span=fast_period).mean()
        exp2 = close_prices.ewm(span=slow_period).mean()
        macd_dif = exp1 - exp2
        macd_dea = macd_dif.ewm(span=signal_period).mean()
        macd_hist = macd_dif - macd_dea
        return macd_dif, macd_dea, macd_hist
        
    def _calculate_kdj(self, high_prices, low_prices, close_prices, period):
        """计算KDJ指标"""
        low_min = low_prices.rolling(window=period).min()
        high_max = high_prices.rolling(window=period).max()
        
        rsv = (close_prices - low_min) / (high_max - low_min) * 100
        k = rsv.ewm(com=2).mean()
        d = k.ewm(com=2).mean()
        j = 3 * k - 2 * d
        
        return k, d, j
        
    def _calculate_rsi(self, close_prices, period):
        """计算RSI指标"""
        delta = close_prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
        
    def _check_daily_exhaustion(self, current_data) -> bool:
        """检查日线趋势衰竭信号"""
        try:
            exhaustion_signals = 0
            
            # 1. RSI严重超买
            rsi = current_data.get('rsi', 50)
            if rsi > 85:  # 严重超买
                exhaustion_signals += 2
            elif rsi > 75:  # 一般超买
                exhaustion_signals += 1
                
            # 2. MACD顶背离
            macd_hist = current_data.get('macd_hist', 0)
            if macd_hist < -0.1:  # MACD柱状图显著转负
                exhaustion_signals += 2
            elif macd_hist < 0:
                exhaustion_signals += 1
                    
            # 3. KDJ超买
            kdj_k = current_data.get('kdj_k', 50)
            kdj_j = current_data.get('kdj_j', 50)
            if kdj_j > 90 or kdj_k > 85:  # 严重超买
                exhaustion_signals += 2
            elif kdj_j > self.config.kdj_overbought or kdj_k > self.config.kdj_overbought:
                exhaustion_signals += 1
                
            # 4. 成交量萎缩
            volume_ratio = current_data.get('volume_ratio', 1)
            if volume_ratio < 0.6:  # 成交量显著萎缩
                exhaustion_signals += 1
                
            # 需要至少3个衰竭信号才卖出
            return exhaustion_signals >= 3
            
        except Exception as e:
            return False
            
    def fit_month(self, today):
        """Abu框架卖出信号判断"""
        if not self.read_fit_month(today):
            return None
            
        try:
            # 获取当前数据
            current_data = self.kl_pd.iloc[self.today_ind]
            current_price = current_data['close']
            
            # 获取买入价格
            if hasattr(self, 'buy_price') and self.buy_price > 0:
                entry_price = self.buy_price
            else:
                return None
                
            # 计算盈亏比例
            pnl_ratio = (current_price - entry_price) / entry_price
            
            # 止损（严格执行）
            if pnl_ratio <= -self.config.stop_loss:
                return self.sell_today()
                
            # 止盈（严格执行）
            if pnl_ratio >= self.config.take_profit:
                return self.sell_today()
                
            # 趋势衰竭信号
            if self._check_daily_exhaustion(current_data):
                return self.sell_today()
                
            return None
            
        except Exception as e:
            return None


class AbuMultiTrendResonanceStrategy(AbuStrategyBase):
    """Abu框架多趋势共振策略"""
    
    def __init__(self, config: MultiTrendResonanceConfig = None):
        self.config = config or MultiTrendResonanceConfig()
        super().__init__()
        
    def setup_buy_factors(self):
        """设置买入因子"""
        return [MultiTrendResonanceBuyFactor(self.config)]
        
    def setup_sell_factors(self):
        """设置卖出因子"""
        return [MultiTrendResonanceSellFactor(self.config)]
        
    def setup_position_factors(self):
        """设置仓位管理因子"""
        # 使用固定比例仓位管理
        from abupy import AbuFactorAtrNStop, AbuFactorPreAtrNStop
        return [
            AbuFactorAtrNStop(stop_loss_n=self.config.stop_loss, stop_win_n=self.config.take_profit),
            AbuFactorPreAtrNStop(pre_atr_n=1.0)
        ]
        
    def get_strategy_name(self) -> str:
        """获取策略名称"""
        return "多趋势共振策略"
        
    def get_strategy_description(self) -> str:
        """获取策略描述"""
        return "基于多时间周期趋势共振的量化交易策略，结合MACD、KDJ、RSI等技术指标进行买卖决策"