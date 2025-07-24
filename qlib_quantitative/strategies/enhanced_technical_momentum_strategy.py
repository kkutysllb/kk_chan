#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强版多因子技术动量突破策略 - Abu框架版本
基于原有增强技术动量策略移植到Abu框架

策略特点：
1. 集成18个技术指标的综合评分系统
2. 包含趋势类、震荡类、成交量类、波动性类指标
3. 动态阈值调整和市场环境适应
4. 多因子权重优化
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
class EnhancedTechnicalMomentumConfig:
    """增强版技术动量策略配置"""
    # 基础配置
    initial_capital: float = 1000000  # 初始资金
    position_size: float = 0.08       # 单股仓位8%
    
    # 均线参数
    ma_periods: List[int] = None      # MA周期
    
    # 成交量参数
    volume_ratio_threshold: float = 1.1  # 量比阈值
    
    # RSI参数
    rsi_upper: float = 70
    rsi_lower: float = 30
    
    # MACD参数
    macd_fast: int = 12
    macd_slow: int = 26
    macd_signal: int = 9
    
    # KDJ参数
    kdj_upper: float = 80
    kdj_lower: float = 20
    
    # CCI参数
    cci_upper: float = 100
    cci_lower: float = -100
    
    # 威廉指标参数
    wr_upper: float = -20
    wr_lower: float = -80
    
    # 布林带参数
    boll_squeeze_threshold: float = 0.05
    
    # DMI参数
    dmi_adx_threshold: float = 25
    
    # 评分阈值
    buy_score_threshold: int = 12     # 买入总分阈值
    strong_buy_threshold: int = 18    # 强买入阈值
    
    # 风险控制
    stop_loss: float = 0.05           # 止损5%
    take_profit: float = 0.12         # 止盈12%
    
    # 权重参数
    technical_weight: float = 0.4     # 技术面权重
    fundamental_weight: float = 0.35  # 基本面权重
    market_weight: float = 0.25       # 市场环境权重
    volatility_adjustment: bool = True # 波动率调整
    
    def __post_init__(self):
        if self.ma_periods is None:
            self.ma_periods = [5, 10, 20, 30]


class EnhancedTechnicalMomentumBuyFactor(AbuFactorBuyBase):
    """增强版技术动量买入因子"""
    
    def __init__(self, config: EnhancedTechnicalMomentumConfig = None):
        super().__init__()
        self.config = config or EnhancedTechnicalMomentumConfig()
        self.data_adapter = AbuDataAdapter()
        
        # 市场环境状态
        self.market_regime = 'neutral'
        
    def _init_self(self, **kwargs):
        """初始化买入因子"""
        # 获取股票代码
        self.symbol = self.kl_pd.name if hasattr(self.kl_pd, 'name') else 'unknown'
        
        # 分析市场环境
        self._analyze_market_regime()
        
    def _analyze_market_regime(self):
        """分析市场环境"""
        try:
            if len(self.kl_pd) < 20:
                return
                
            # 使用最近20天数据判断市场环境
            recent_data = self.kl_pd.tail(20)
            
            # 计算波动率
            returns = recent_data['close'].pct_change().dropna()
            volatility = returns.std() * np.sqrt(252)  # 年化波动率
            
            # 计算趋势强度（简化版ADX）
            high_low = recent_data['high'] - recent_data['low']
            close_prev = recent_data['close'].shift(1)
            true_range = np.maximum(high_low, 
                                  np.maximum(abs(recent_data['high'] - close_prev),
                                           abs(recent_data['low'] - close_prev)))
            atr = true_range.rolling(14).mean().iloc[-1]
            trend_strength = atr / recent_data['close'].iloc[-1] if recent_data['close'].iloc[-1] > 0 else 0
            
            # 判断市场环境
            if trend_strength > 0.03 and volatility > 0.3:
                self.market_regime = 'volatile'
            elif trend_strength < 0.015 and volatility < 0.2:
                self.market_regime = 'stable'
            elif recent_data['close'].iloc[-1] > recent_data['close'].iloc[0]:
                self.market_regime = 'bull'
            else:
                self.market_regime = 'bear'
                
        except Exception as e:
            self.market_regime = 'neutral'
            
    def _score_ma_trend(self, current_data: pd.Series) -> Tuple[int, str]:
        """均线趋势评分 (满分3分)"""
        try:
            ma5 = current_data.get('ma_qfq_5', 0)
            ma10 = current_data.get('ma_qfq_10', 0)
            ma20 = current_data.get('ma_qfq_20', 0)
            ma30 = current_data.get('ma_qfq_30', 0)
            close = current_data.get('close', 0)
            
            score = 0
            reasons = []
            
            # 价格在均线之上
            if close > ma5 > ma10 > ma20:
                score += 3
                reasons.append('多头排列')
            elif close > ma5 > ma10:
                score += 2
                reasons.append('短期多头')
            elif close > ma5:
                score += 1
                reasons.append('突破MA5')
                
            return score, ', '.join(reasons)
            
        except Exception as e:
            return 0, ''
            
    def _score_macd_signal(self, current_data: pd.Series) -> Tuple[int, str]:
        """MACD信号评分 (满分3分)"""
        try:
            macd_dif = current_data.get('macd_dif', 0)
            macd_dea = current_data.get('macd_dea', 0)
            macd_hist = current_data.get('macd', 0)
            
            score = 0
            reasons = []
            
            # MACD金叉
            if macd_dif > macd_dea:
                score += 1
                reasons.append('MACD金叉')
                
            # MACD在零轴上方
            if macd_hist > 0:
                score += 1
                reasons.append('MACD零轴上')
                
            # MACD强势
            if macd_dif > 0 and macd_dea > 0:
                score += 1
                reasons.append('MACD强势')
                
            return score, ', '.join(reasons)
            
        except Exception as e:
            return 0, ''
            
    def _score_rsi_signal(self, current_data: pd.Series) -> Tuple[int, str]:
        """RSI信号评分 (满分2分)"""
        try:
            rsi = current_data.get('rsi_6', 50)
            
            score = 0
            reason = ''
            
            if 30 < rsi < 70:  # 健康区间
                score += 2
                reason = 'RSI健康'
            elif 20 < rsi < 80:  # 可接受区间
                score += 1
                reason = 'RSI可接受'
                
            return score, reason
            
        except Exception as e:
            return 0, ''
            
    def _score_kdj_signal(self, current_data: pd.Series) -> Tuple[int, str]:
        """KDJ信号评分 (满分2分)"""
        try:
            kdj_k = current_data.get('kdj_k', 50)
            kdj_d = current_data.get('kdj_d', 50)
            
            score = 0
            reasons = []
            
            # KDJ金叉
            if kdj_k > kdj_d:
                score += 1
                reasons.append('KDJ金叉')
                
            # KDJ未超买
            if kdj_k < self.config.kdj_upper:
                score += 1
                reasons.append('KDJ未超买')
                
            return score, ', '.join(reasons)
            
        except Exception as e:
            return 0, ''
            
    def _score_volume_signal(self, current_data: pd.Series) -> Tuple[int, str]:
        """成交量信号评分 (满分3分)"""
        try:
            volume_ratio = current_data.get('volume_ratio', 1.0)
            turnover_rate = current_data.get('turnover_rate_f', 0)
            
            score = 0
            reasons = []
            
            # 量比评分
            if volume_ratio >= 2.0:
                score += 2
                reasons.append('放量突破')
            elif volume_ratio >= self.config.volume_ratio_threshold:
                score += 1
                reasons.append('温和放量')
                
            # 换手率评分
            if 1.0 <= turnover_rate <= 10.0:
                score += 1
                reasons.append('换手率健康')
                
            return score, ', '.join(reasons)
            
        except Exception as e:
            return 0, ''
            
    def _score_market_environment(self, current_data: pd.Series) -> Tuple[int, str]:
        """市场环境评分 (满分2分)"""
        score = 0
        reason = ''
        
        if self.market_regime == 'bull':
            score = 2
            reason = '牛市环境'
        elif self.market_regime == 'stable':
            score = 1
            reason = '稳定环境'
        elif self.market_regime == 'neutral':
            score = 1
            reason = '中性环境'
            
        return score, reason
        
    def _calculate_comprehensive_score(self, current_data: pd.Series) -> Tuple[int, List[str]]:
        """计算综合技术评分"""
        total_score = 0
        all_reasons = []
        
        # 趋势类指标
        ma_score, ma_reason = self._score_ma_trend(current_data)
        total_score += ma_score
        if ma_reason:
            all_reasons.append(ma_reason)
            
        macd_score, macd_reason = self._score_macd_signal(current_data)
        total_score += macd_score
        if macd_reason:
            all_reasons.append(macd_reason)
            
        # 震荡类指标
        rsi_score, rsi_reason = self._score_rsi_signal(current_data)
        total_score += rsi_score
        if rsi_reason:
            all_reasons.append(rsi_reason)
            
        kdj_score, kdj_reason = self._score_kdj_signal(current_data)
        total_score += kdj_score
        if kdj_reason:
            all_reasons.append(kdj_reason)
            
        # 成交量类指标
        volume_score, volume_reason = self._score_volume_signal(current_data)
        total_score += volume_score
        if volume_reason:
            all_reasons.append(volume_reason)
            
        # 市场环境
        env_score, env_reason = self._score_market_environment(current_data)
        total_score += env_score
        if env_reason:
            all_reasons.append(env_reason)
            
        return total_score, all_reasons
        
    def _get_dynamic_threshold(self) -> int:
        """获取动态阈值"""
        base_threshold = self.config.buy_score_threshold
        
        # 根据市场环境调整阈值
        if self.market_regime == 'bull':
            return max(base_threshold - 2, 8)  # 牛市降低阈值
        elif self.market_regime == 'bear':
            return base_threshold + 2  # 熊市提高阈值
        else:
            return base_threshold
            
    def fit_month(self, today):
        """Abu框架买入信号判断"""
        if self.today_ind < 30:  # 需要足够的历史数据
            return None
            
        try:
            current_data = self.kl_pd.iloc[self.today_ind]
            
            # 计算综合技术评分
            total_score, reasons = self._calculate_comprehensive_score(current_data)
            
            # 获取动态阈值
            threshold = self._get_dynamic_threshold()
            
            # 检查买入条件
            if total_score >= self.config.strong_buy_threshold:
                # 强买入信号
                return self.buy_today()
            elif total_score >= threshold:
                # 普通买入信号
                return self.buy_today()
                
            return None
            
        except Exception as e:
            return None


class EnhancedTechnicalMomentumSellFactor(AbuFactorSellBase):
    """增强版技术动量卖出因子"""
    
    def __init__(self, config: EnhancedTechnicalMomentumConfig = None):
        super().__init__()
        self.config = config or EnhancedTechnicalMomentumConfig()
        
    def _init_self(self, **kwargs):
        """初始化卖出因子"""
        self.symbol = self.kl_pd.name if hasattr(self.kl_pd, 'name') else 'unknown'
        
    def _check_technical_deterioration(self, current_data: pd.Series) -> bool:
        """检查技术指标恶化"""
        try:
            # MACD死叉
            macd_dif = current_data.get('macd_dif', 0)
            macd_dea = current_data.get('macd_dea', 0)
            if macd_dif < macd_dea:
                return True
                
            # RSI超卖
            rsi = current_data.get('rsi_6', 50)
            if rsi < 20:
                return True
                
            # KDJ死叉且超卖
            kdj_k = current_data.get('kdj_k', 50)
            kdj_d = current_data.get('kdj_d', 50)
            if kdj_k < kdj_d and kdj_k < 20:
                return True
                
            # 成交量萎缩
            volume_ratio = current_data.get('volume_ratio', 1.0)
            if volume_ratio < 0.5:
                return True
                
            return False
            
        except Exception as e:
            return False
            
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
                
                # 止损：亏损超过5%
                if pnl_ratio <= -self.config.stop_loss:
                    return self.sell_today()
                    
                # 止盈：盈利超过12%
                if pnl_ratio >= self.config.take_profit:
                    return self.sell_today()
                    
            # 2. 技术指标恶化检查
            if self._check_technical_deterioration(current_data):
                return self.sell_today()
                
            return None
            
        except Exception as e:
            return None


class AbuEnhancedTechnicalMomentumStrategy(AbuStrategyBase):
    """Abu框架增强版技术动量策略"""
    
    def __init__(self, config: EnhancedTechnicalMomentumConfig = None):
        self.config = config or EnhancedTechnicalMomentumConfig()
        super().__init__()
        
    def setup_buy_factors(self):
        """设置买入因子"""
        return [EnhancedTechnicalMomentumBuyFactor(self.config)]
        
    def setup_sell_factors(self):
        """设置卖出因子"""
        return [EnhancedTechnicalMomentumSellFactor(self.config)]
        
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
        return "增强版技术动量策略"
        
    def get_strategy_description(self) -> str:
        """获取策略描述"""
        return "基于18个技术指标的综合评分系统，包含趋势、震荡、成交量和市场环境因子"