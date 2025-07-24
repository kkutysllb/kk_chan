#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
市场环境判断技术因子总结
基于index_factor_pro集合分析结果
"""

import sys
import os
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from api.db_handler import get_db_handler


class MarketEnvironmentFactors:
    """市场环境判断技术因子分析器"""
    
    def __init__(self):
        self.db_handler = get_db_handler()
        self.collection = self.db_handler.get_collection('index_factor_pro')
        
        # 定义各类技术因子
        self.trend_factors = {
            'ma_bfq_5': '5日均线',
            'ma_bfq_10': '10日均线',
            'ma_bfq_20': '20日均线',
            'ma_bfq_30': '30日均线',
            'ma_bfq_60': '60日均线',
            'ma_bfq_90': '90日均线',
            'ma_bfq_250': '250日均线',
            'ema_bfq_5': '5日指数均线',
            'ema_bfq_10': '10日指数均线',
            'ema_bfq_20': '20日指数均线',
            'ema_bfq_30': '30日指数均线',
            'ema_bfq_60': '60日指数均线',
            'ema_bfq_90': '90日指数均线',
            'ema_bfq_250': '250日指数均线',
            'macd_bfq': 'MACD主线',
            'macd_dea_bfq': 'MACD信号线',
            'macd_dif_bfq': 'MACD差值线',
            'boll_upper_bfq': '布林带上轨',
            'boll_mid_bfq': '布林带中轨',
            'boll_lower_bfq': '布林带下轨',
            'dmi_adx_bfq': 'ADX趋势强度',
            'dmi_pdi_bfq': 'PDI正向指标',
            'dmi_mdi_bfq': 'MDI负向指标',
            'cci_bfq': 'CCI顺势指标',
            'bias1_bfq': '乖离率1',
            'bias2_bfq': '乖离率2',
            'bias3_bfq': '乖离率3',
            'expma_12_bfq': '12日EXPMA',
            'expma_50_bfq': '50日EXPMA',
            'dfma_dif_bfq': 'DFMA差值',
            'dfma_difma_bfq': 'DFMA信号',
            'dpo_bfq': '区间震荡线',
            'trix_bfq': 'TRIX指标',
            'ktn_upper_bfq': '肯特纳上轨',
            'ktn_mid_bfq': '肯特纳中轨',
            'ktn_down_bfq': '肯特纳下轨'
        }
        
        self.momentum_factors = {
            'rsi_bfq_6': '6日RSI',
            'rsi_bfq_12': '12日RSI',
            'rsi_bfq_24': '24日RSI',
            'kdj_k_bfq': 'KDJ-K值',
            'kdj_d_bfq': 'KDJ-D值',
            'kdj_bfq': 'KDJ-J值',
            'wr_bfq': '威廉指标',
            'wr1_bfq': '威廉指标1',
            'roc_bfq': '变化率指标',
            'mtm_bfq': '动量指标',
            'mtmma_bfq': '动量移动平均',
            'psy_bfq': '心理线',
            'psyma_bfq': '心理线移动平均',
            'maroc_bfq': 'MA-ROC指标'
        }
        
        self.volatility_factors = {
            'atr_bfq': '真实波幅',
            'mass_bfq': '梅斯线',
            'ma_mass_bfq': '梅斯线移动平均',
            'asi_bfq': '振动升降指标',
            'asit_bfq': '振动升降指标趋势'
        }
        
        self.volume_factors = {
            'vol': '成交量',
            'amount': '成交额',
            'obv_bfq': '能量潮指标',
            'vr_bfq': '成交量比率',
            'mfi_bfq': '资金流量指标',
            'emv_bfq': '简易波动指标',
            'maemv_bfq': 'EMV移动平均'
        }
        
        self.sentiment_factors = {
            'brar_ar_bfq': 'AR人气指标',
            'brar_br_bfq': 'BR意愿指标',
            'cr_bfq': 'CR能量指标'
        }
        
        self.breadth_factors = {
            'updays': '上涨天数',
            'downdays': '下跌天数',
            'topdays': '创新高天数',
            'lowdays': '创新低天数'
        }
    
    def get_market_environment_analysis(self, index_code='000001.SH', days=60):
        """获取市场环境分析"""
        
        print(f"📊 市场环境技术因子分析 - {index_code}")
        print("=" * 80)
        
        # 获取最近N天的数据
        end_date = datetime.now().strftime('%Y%m%d')
        start_date = (datetime.now() - timedelta(days=days)).strftime('%Y%m%d')
        
        query = {
            'ts_code': index_code,
            'trade_date': {'$gte': start_date, '$lte': end_date}
        }
        
        data = list(self.collection.find(query).sort('trade_date', -1))
        
        if not data:
            print(f"❌ 没有找到{index_code}的数据")
            return None
        
        print(f"🔍 分析期间: {start_date} 到 {end_date}")
        print(f"📈 数据条数: {len(data)}条")
        
        # 获取最新数据
        latest_data = data[0]
        
        # 1. 趋势判断
        print("\n🎯 1. 趋势判断因子")
        print("-" * 50)
        
        trend_analysis = self._analyze_trend(latest_data)
        for factor, analysis in trend_analysis.items():
            print(f"• {factor}: {analysis}")
        
        # 2. 动量分析
        print("\n⚡ 2. 动量判断因子")
        print("-" * 50)
        
        momentum_analysis = self._analyze_momentum(latest_data)
        for factor, analysis in momentum_analysis.items():
            print(f"• {factor}: {analysis}")
        
        # 3. 波动率分析
        print("\n📊 3. 波动率判断因子")
        print("-" * 50)
        
        volatility_analysis = self._analyze_volatility(latest_data, data)
        for factor, analysis in volatility_analysis.items():
            print(f"• {factor}: {analysis}")
        
        # 4. 资金流向分析
        print("\n💰 4. 资金流向判断因子")
        print("-" * 50)
        
        volume_analysis = self._analyze_volume(latest_data, data)
        for factor, analysis in volume_analysis.items():
            print(f"• {factor}: {analysis}")
        
        # 5. 市场情绪分析
        print("\n😊 5. 市场情绪判断因子")
        print("-" * 50)
        
        sentiment_analysis = self._analyze_sentiment(latest_data)
        for factor, analysis in sentiment_analysis.items():
            print(f"• {factor}: {analysis}")
        
        # 6. 综合市场环境判断
        print("\n🌐 6. 综合市场环境判断")
        print("-" * 50)
        
        overall_analysis = self._analyze_overall_environment(latest_data, data)
        for aspect, result in overall_analysis.items():
            print(f"• {aspect}: {result}")
        
        return {
            'trend': trend_analysis,
            'momentum': momentum_analysis,
            'volatility': volatility_analysis,
            'volume': volume_analysis,
            'sentiment': sentiment_analysis,
            'overall': overall_analysis
        }
    
    def _analyze_trend(self, data):
        """分析趋势指标"""
        analysis = {}
        
        # 均线排列
        ma_5 = data.get('ma_bfq_5', 0)
        ma_20 = data.get('ma_bfq_20', 0)
        ma_60 = data.get('ma_bfq_60', 0)
        ma_250 = data.get('ma_bfq_250', 0)
        close = data.get('close', 0)
        
        # 多头排列检查
        if ma_5 > ma_20 > ma_60 > ma_250:
            analysis['均线排列'] = f"多头排列 (5日:{ma_5:.2f} > 20日:{ma_20:.2f} > 60日:{ma_60:.2f} > 250日:{ma_250:.2f})"
        elif ma_5 < ma_20 < ma_60 < ma_250:
            analysis['均线排列'] = f"空头排列 (5日:{ma_5:.2f} < 20日:{ma_20:.2f} < 60日:{ma_60:.2f} < 250日:{ma_250:.2f})"
        else:
            analysis['均线排列'] = f"震荡排列 (5日:{ma_5:.2f}, 20日:{ma_20:.2f}, 60日:{ma_60:.2f}, 250日:{ma_250:.2f})"
        
        # MACD分析
        macd = data.get('macd_bfq', 0)
        macd_dea = data.get('macd_dea_bfq', 0)
        macd_dif = data.get('macd_dif_bfq', 0)
        
        if macd_dif > macd_dea and macd > 0:
            analysis['MACD'] = f"强势多头 (MACD:{macd:.2f}, DIF:{macd_dif:.2f} > DEA:{macd_dea:.2f})"
        elif macd_dif > macd_dea and macd < 0:
            analysis['MACD'] = f"弱势反弹 (MACD:{macd:.2f}, DIF:{macd_dif:.2f} > DEA:{macd_dea:.2f})"
        elif macd_dif < macd_dea and macd > 0:
            analysis['MACD'] = f"强势调整 (MACD:{macd:.2f}, DIF:{macd_dif:.2f} < DEA:{macd_dea:.2f})"
        else:
            analysis['MACD'] = f"弱势下跌 (MACD:{macd:.2f}, DIF:{macd_dif:.2f} < DEA:{macd_dea:.2f})"
        
        # 布林带分析
        boll_upper = data.get('boll_upper_bfq', 0)
        boll_mid = data.get('boll_mid_bfq', 0)
        boll_lower = data.get('boll_lower_bfq', 0)
        
        if close > boll_upper:
            analysis['布林带'] = f"突破上轨 (收盘:{close:.2f} > 上轨:{boll_upper:.2f})"
        elif close < boll_lower:
            analysis['布林带'] = f"跌破下轨 (收盘:{close:.2f} < 下轨:{boll_lower:.2f})"
        elif close > boll_mid:
            analysis['布林带'] = f"上轨区间 (收盘:{close:.2f} > 中轨:{boll_mid:.2f})"
        else:
            analysis['布林带'] = f"下轨区间 (收盘:{close:.2f} < 中轨:{boll_mid:.2f})"
        
        # ADX趋势强度
        adx = data.get('dmi_adx_bfq', 0)
        if adx > 30:
            analysis['ADX趋势强度'] = f"强趋势 (ADX:{adx:.2f} > 30)"
        elif adx > 20:
            analysis['ADX趋势强度'] = f"中等趋势 (ADX:{adx:.2f})"
        else:
            analysis['ADX趋势强度'] = f"弱趋势 (ADX:{adx:.2f} < 20)"
        
        return analysis
    
    def _analyze_momentum(self, data):
        """分析动量指标"""
        analysis = {}
        
        # RSI分析
        rsi_6 = data.get('rsi_bfq_6', 0)
        rsi_12 = data.get('rsi_bfq_12', 0)
        rsi_24 = data.get('rsi_bfq_24', 0)
        
        if rsi_12 > 80:
            analysis['RSI'] = f"严重超买 (RSI12:{rsi_12:.2f} > 80)"
        elif rsi_12 > 70:
            analysis['RSI'] = f"超买 (RSI12:{rsi_12:.2f} > 70)"
        elif rsi_12 < 20:
            analysis['RSI'] = f"严重超卖 (RSI12:{rsi_12:.2f} < 20)"
        elif rsi_12 < 30:
            analysis['RSI'] = f"超卖 (RSI12:{rsi_12:.2f} < 30)"
        else:
            analysis['RSI'] = f"正常区间 (RSI12:{rsi_12:.2f})"
        
        # KDJ分析
        kdj_k = data.get('kdj_k_bfq', 0)
        kdj_d = data.get('kdj_d_bfq', 0)
        kdj_j = data.get('kdj_bfq', 0)
        
        if kdj_k > 80 and kdj_d > 80:
            analysis['KDJ'] = f"超买区域 (K:{kdj_k:.2f}, D:{kdj_d:.2f}, J:{kdj_j:.2f})"
        elif kdj_k < 20 and kdj_d < 20:
            analysis['KDJ'] = f"超卖区域 (K:{kdj_k:.2f}, D:{kdj_d:.2f}, J:{kdj_j:.2f})"
        elif kdj_k > kdj_d:
            analysis['KDJ'] = f"金叉向上 (K:{kdj_k:.2f} > D:{kdj_d:.2f})"
        else:
            analysis['KDJ'] = f"死叉向下 (K:{kdj_k:.2f} < D:{kdj_d:.2f})"
        
        # 威廉指标
        wr = data.get('wr_bfq', 0)
        if wr > 80:
            analysis['威廉指标'] = f"超卖 (WR:{wr:.2f} > 80)"
        elif wr < 20:
            analysis['威廉指标'] = f"超买 (WR:{wr:.2f} < 20)"
        else:
            analysis['威廉指标'] = f"正常 (WR:{wr:.2f})"
        
        return analysis
    
    def _analyze_volatility(self, latest_data, historical_data):
        """分析波动率指标"""
        analysis = {}
        
        # ATR分析
        atr = latest_data.get('atr_bfq', 0)
        
        # 计算ATR的历史分位数
        atr_values = [d.get('atr_bfq', 0) for d in historical_data if d.get('atr_bfq')]
        if atr_values:
            atr_percentile = (sum(1 for v in atr_values if v < atr) / len(atr_values)) * 100
            if atr_percentile > 80:
                analysis['ATR波动率'] = f"高波动环境 (ATR:{atr:.2f}, 分位数:{atr_percentile:.1f}%)"
            elif atr_percentile < 20:
                analysis['ATR波动率'] = f"低波动环境 (ATR:{atr:.2f}, 分位数:{atr_percentile:.1f}%)"
            else:
                analysis['ATR波动率'] = f"正常波动环境 (ATR:{atr:.2f}, 分位数:{atr_percentile:.1f}%)"
        
        # 布林带宽度分析
        boll_upper = latest_data.get('boll_upper_bfq', 0)
        boll_lower = latest_data.get('boll_lower_bfq', 0)
        boll_mid = latest_data.get('boll_mid_bfq', 0)
        
        if boll_mid > 0:
            boll_width = ((boll_upper - boll_lower) / boll_mid) * 100
            if boll_width > 10:
                analysis['布林带宽度'] = f"高波动 (宽度:{boll_width:.2f}%)"
            elif boll_width < 3:
                analysis['布林带宽度'] = f"低波动 (宽度:{boll_width:.2f}%)"
            else:
                analysis['布林带宽度'] = f"正常波动 (宽度:{boll_width:.2f}%)"
        
        return analysis
    
    def _analyze_volume(self, latest_data, historical_data):
        """分析成交量指标"""
        analysis = {}
        
        # 成交量分析
        vol = latest_data.get('vol', 0)
        amount = latest_data.get('amount', 0)
        
        # 计算成交量的历史分位数
        vol_values = [d.get('vol', 0) for d in historical_data if d.get('vol')]
        if vol_values:
            vol_percentile = (sum(1 for v in vol_values if v < vol) / len(vol_values)) * 100
            if vol_percentile > 80:
                analysis['成交量'] = f"放量 (成交量:{vol/100000000:.2f}亿, 分位数:{vol_percentile:.1f}%)"
            elif vol_percentile < 20:
                analysis['成交量'] = f"缩量 (成交量:{vol/100000000:.2f}亿, 分位数:{vol_percentile:.1f}%)"
            else:
                analysis['成交量'] = f"正常 (成交量:{vol/100000000:.2f}亿, 分位数:{vol_percentile:.1f}%)"
        
        # OBV分析
        obv = latest_data.get('obv_bfq', 0)
        if len(historical_data) > 1:
            prev_obv = historical_data[1].get('obv_bfq', 0)
            if obv > prev_obv:
                analysis['OBV'] = f"资金流入 (OBV:{obv/100000000:.2f}亿 > 前值:{prev_obv/100000000:.2f}亿)"
            elif obv < prev_obv:
                analysis['OBV'] = f"资金流出 (OBV:{obv/100000000:.2f}亿 < 前值:{prev_obv/100000000:.2f}亿)"
            else:
                analysis['OBV'] = f"资金平衡 (OBV:{obv/100000000:.2f}亿)"
        
        # MFI分析
        mfi = latest_data.get('mfi_bfq', 0)
        if mfi > 80:
            analysis['MFI'] = f"资金超买 (MFI:{mfi:.2f} > 80)"
        elif mfi < 20:
            analysis['MFI'] = f"资金超卖 (MFI:{mfi:.2f} < 20)"
        else:
            analysis['MFI'] = f"资金正常 (MFI:{mfi:.2f})"
        
        return analysis
    
    def _analyze_sentiment(self, data):
        """分析市场情绪指标"""
        analysis = {}
        
        # AR指标
        ar = data.get('brar_ar_bfq', 0)
        if ar > 180:
            analysis['AR人气'] = f"人气过热 (AR:{ar:.2f} > 180)"
        elif ar < 80:
            analysis['AR人气'] = f"人气低迷 (AR:{ar:.2f} < 80)"
        else:
            analysis['AR人气'] = f"人气正常 (AR:{ar:.2f})"
        
        # BR指标
        br = data.get('brar_br_bfq', 0)
        if br > 300:
            analysis['BR意愿'] = f"意愿过强 (BR:{br:.2f} > 300)"
        elif br < 50:
            analysis['BR意愿'] = f"意愿过弱 (BR:{br:.2f} < 50)"
        else:
            analysis['BR意愿'] = f"意愿正常 (BR:{br:.2f})"
        
        # CR指标
        cr = data.get('cr_bfq', 0)
        if cr > 200:
            analysis['CR能量'] = f"能量过度 (CR:{cr:.2f} > 200)"
        elif cr < 50:
            analysis['CR能量'] = f"能量不足 (CR:{cr:.2f} < 50)"
        else:
            analysis['CR能量'] = f"能量正常 (CR:{cr:.2f})"
        
        return analysis
    
    def _analyze_overall_environment(self, latest_data, historical_data):
        """综合市场环境分析"""
        analysis = {}
        
        # 趋势强度评分
        trend_score = 0
        
        # 均线排列评分
        ma_5 = latest_data.get('ma_bfq_5', 0)
        ma_20 = latest_data.get('ma_bfq_20', 0)
        ma_60 = latest_data.get('ma_bfq_60', 0)
        close = latest_data.get('close', 0)
        
        if close > ma_5 > ma_20 > ma_60:
            trend_score += 3
        elif close > ma_20:
            trend_score += 1
        elif close < ma_20:
            trend_score -= 1
        
        # MACD评分
        macd = latest_data.get('macd_bfq', 0)
        macd_dea = latest_data.get('macd_dea_bfq', 0)
        macd_dif = latest_data.get('macd_dif_bfq', 0)
        
        if macd_dif > macd_dea and macd > 0:
            trend_score += 2
        elif macd_dif > macd_dea:
            trend_score += 1
        elif macd_dif < macd_dea:
            trend_score -= 1
        
        # 趋势判断
        if trend_score >= 4:
            analysis['趋势环境'] = f"强势上升趋势 (评分:{trend_score}/5)"
        elif trend_score >= 2:
            analysis['趋势环境'] = f"上升趋势 (评分:{trend_score}/5)"
        elif trend_score >= 0:
            analysis['趋势环境'] = f"震荡趋势 (评分:{trend_score}/5)"
        elif trend_score >= -2:
            analysis['趋势环境'] = f"下降趋势 (评分:{trend_score}/5)"
        else:
            analysis['趋势环境'] = f"强势下降趋势 (评分:{trend_score}/5)"
        
        # 超买超卖程度
        rsi_12 = latest_data.get('rsi_bfq_12', 0)
        if rsi_12 > 80:
            analysis['超买超卖'] = f"严重超买 (RSI:{rsi_12:.2f})"
        elif rsi_12 > 70:
            analysis['超买超卖'] = f"超买 (RSI:{rsi_12:.2f})"
        elif rsi_12 < 20:
            analysis['超买超卖'] = f"严重超卖 (RSI:{rsi_12:.2f})"
        elif rsi_12 < 30:
            analysis['超买超卖'] = f"超卖 (RSI:{rsi_12:.2f})"
        else:
            analysis['超买超卖'] = f"正常区间 (RSI:{rsi_12:.2f})"
        
        # 波动率环境
        atr = latest_data.get('atr_bfq', 0)
        atr_values = [d.get('atr_bfq', 0) for d in historical_data if d.get('atr_bfq')]
        if atr_values:
            atr_percentile = (sum(1 for v in atr_values if v < atr) / len(atr_values)) * 100
            if atr_percentile > 80:
                analysis['波动率环境'] = f"高波动环境 (分位数:{atr_percentile:.1f}%)"
            elif atr_percentile < 20:
                analysis['波动率环境'] = f"低波动环境 (分位数:{atr_percentile:.1f}%)"
            else:
                analysis['波动率环境'] = f"正常波动环境 (分位数:{atr_percentile:.1f}%)"
        
        return analysis
    
    def print_factor_summary(self):
        """打印技术因子总结"""
        print("\n📊 index_factor_pro集合技术因子总结")
        print("=" * 80)
        
        print("\n🎯 趋势判断因子 (39个)")
        print("-" * 50)
        for key, desc in self.trend_factors.items():
            print(f"• {key:<20} - {desc}")
        
        print("\n⚡ 动量判断因子 (14个)")
        print("-" * 50)
        for key, desc in self.momentum_factors.items():
            print(f"• {key:<20} - {desc}")
        
        print("\n📊 波动率判断因子 (5个)")
        print("-" * 50)
        for key, desc in self.volatility_factors.items():
            print(f"• {key:<20} - {desc}")
        
        print("\n💰 资金流向判断因子 (7个)")
        print("-" * 50)
        for key, desc in self.volume_factors.items():
            print(f"• {key:<20} - {desc}")
        
        print("\n😊 情绪判断因子 (3个)")
        print("-" * 50)
        for key, desc in self.sentiment_factors.items():
            print(f"• {key:<20} - {desc}")
        
        print("\n📈 市场宽度判断因子 (4个)")
        print("-" * 50)
        for key, desc in self.breadth_factors.items():
            print(f"• {key:<20} - {desc}")
        
        print(f"\n✅ 总计: {len(self.trend_factors) + len(self.momentum_factors) + len(self.volatility_factors) + len(self.volume_factors) + len(self.sentiment_factors) + len(self.breadth_factors)}个技术因子")
        
        print("\n💡 市场环境判断建议:")
        print("1. 趋势环境: 使用均线排列、MACD、布林带、ADX等指标")
        print("2. 动量环境: 使用RSI、KDJ、威廉指标等超买超卖指标")
        print("3. 波动率环境: 使用ATR、布林带宽度等波动率指标")
        print("4. 资金环境: 使用OBV、MFI、成交量等资金流向指标")
        print("5. 情绪环境: 使用AR、BR、CR等情绪指标")
        print("6. 综合环境: 结合多个维度的指标进行综合判断")


def main():
    """主函数"""
    analyzer = MarketEnvironmentFactors()
    
    # 打印技术因子总结
    analyzer.print_factor_summary()
    
    # 分析具体指数的市场环境
    print("\n" + "=" * 80)
    analyzer.get_market_environment_analysis('000001.SH', days=30)


if __name__ == "__main__":
    main()