# index_factor_pro集合技术指标分析报告

## 📊 数据库连接信息

- **数据库**: quant_analysis
- **集合**: index_factor_pro
- **总记录数**: 971,051条
- **数据时间范围**: 2023-01-03 至 2025-07-17
- **数据质量**: 优秀（100%完整度）

## 🎯 技术指标字段分类总结

### 1. 趋势判断因子 (39个字段)

**均线系列:**
- `ma_bfq_5`, `ma_bfq_10`, `ma_bfq_20`, `ma_bfq_30`, `ma_bfq_60`, `ma_bfq_90`, `ma_bfq_250` - 简单移动平均线
- `ema_bfq_5`, `ema_bfq_10`, `ema_bfq_20`, `ema_bfq_30`, `ema_bfq_60`, `ema_bfq_90`, `ema_bfq_250` - 指数移动平均线
- `expma_12_bfq`, `expma_50_bfq` - 指数平滑移动平均线

**MACD系列:**
- `macd_bfq` - MACD主线
- `macd_dea_bfq` - MACD信号线(DEA)
- `macd_dif_bfq` - MACD差值线(DIF)

**布林带系列:**
- `boll_upper_bfq` - 布林带上轨
- `boll_mid_bfq` - 布林带中轨
- `boll_lower_bfq` - 布林带下轨

**DMI系列:**
- `dmi_adx_bfq` - ADX趋势强度指标
- `dmi_pdi_bfq` - PDI正向指标
- `dmi_mdi_bfq` - MDI负向指标

**其他趋势指标:**
- `cci_bfq` - CCI顺势指标
- `bias1_bfq`, `bias2_bfq`, `bias3_bfq` - 乖离率
- `dfma_dif_bfq`, `dfma_difma_bfq` - DFMA系列
- `dpo_bfq` - 区间震荡线
- `trix_bfq` - TRIX指标
- `ktn_upper_bfq`, `ktn_mid_bfq`, `ktn_down_bfq` - 肯特纳通道

### 2. 动量判断因子 (14个字段)

**RSI系列:**
- `rsi_bfq_6`, `rsi_bfq_12`, `rsi_bfq_24` - 相对强弱指标

**KDJ系列:**
- `kdj_k_bfq` - KDJ-K值
- `kdj_d_bfq` - KDJ-D值  
- `kdj_bfq` - KDJ-J值

**威廉指标:**
- `wr_bfq`, `wr1_bfq` - 威廉指标

**其他动量指标:**
- `roc_bfq` - 变化率指标
- `mtm_bfq` - 动量指标
- `mtmma_bfq` - 动量移动平均
- `psy_bfq`, `psyma_bfq` - 心理线及其移动平均
- `maroc_bfq` - MA-ROC指标

### 3. 波动率判断因子 (4个字段)

- `atr_bfq` - 真实波幅 (Average True Range)
- `mass_bfq` - 梅斯线
- `asi_bfq` - 振动升降指标
- `asit_bfq` - 振动升降指标趋势

### 4. 成交量/资金流向判断因子 (7个字段)

- `vol` - 成交量
- `amount` - 成交额
- `obv_bfq` - 能量潮指标 (On-Balance Volume)
- `vr_bfq` - 成交量比率
- `mfi_bfq` - 资金流量指标 (Money Flow Index)
- `emv_bfq` - 简易波动指标
- `maemv_bfq` - EMV移动平均

### 5. 市场情绪判断因子 (3个字段)

- `brar_ar_bfq` - AR人气指标
- `brar_br_bfq` - BR意愿指标
- `cr_bfq` - CR能量指标

### 6. 市场宽度判断因子 (4个字段)

- `updays` - 上涨天数
- `downdays` - 下跌天数
- `topdays` - 创新高天数
- `lowdays` - 创新低天数

### 7. 基础价格数据 (16个字段)

- `open`, `close`, `high`, `low` - OHLC价格
- `change`, `pct_change` - 涨跌幅
- `pre_close` - 前收盘价
- `trade_date`, `ts_code` - 日期和代码
- `taq_down_bfq`, `taq_mid_bfq`, `taq_up_bfq` - TAQ价格系列
- `xsii_td1_bfq`, `xsii_td2_bfq`, `xsii_td3_bfq`, `xsii_td4_bfq` - XSII系列

## 💡 市场环境判断技术因子建议

### 1. 趋势环境判断

**推荐核心指标组合:**
```python
trend_indicators = {
    '多周期均线': ['ma_bfq_5', 'ma_bfq_20', 'ma_bfq_60', 'ma_bfq_250'],
    'MACD系列': ['macd_bfq', 'macd_dea_bfq', 'macd_dif_bfq'],
    '布林带': ['boll_upper_bfq', 'boll_mid_bfq', 'boll_lower_bfq'],
    'ADX趋势强度': ['dmi_adx_bfq', 'dmi_pdi_bfq', 'dmi_mdi_bfq']
}
```

**判断逻辑:**
- 多头排列: MA5 > MA20 > MA60 > MA250
- MACD金叉: DIF > DEA 且 MACD > 0
- 布林带突破: 价格突破上轨或下轨
- ADX > 30: 强趋势环境

### 2. 动量环境判断

**推荐核心指标组合:**
```python
momentum_indicators = {
    'RSI超买超卖': ['rsi_bfq_6', 'rsi_bfq_12', 'rsi_bfq_24'],
    'KDJ随机指标': ['kdj_k_bfq', 'kdj_d_bfq', 'kdj_bfq'],
    '威廉指标': ['wr_bfq'],
    '变化率': ['roc_bfq']
}
```

**判断逻辑:**
- RSI > 70: 超买，RSI < 30: 超卖
- KDJ金叉死叉: K线与D线的交叉
- 威廉指标: WR > 80超卖，WR < 20超买
- ROC变化率: 衡量价格变化速度

### 3. 波动率环境判断

**推荐核心指标组合:**
```python
volatility_indicators = {
    '真实波幅': ['atr_bfq'],
    '布林带宽度': ['boll_upper_bfq', 'boll_lower_bfq', 'boll_mid_bfq'],
    '振动指标': ['asi_bfq', 'asit_bfq']
}
```

**判断逻辑:**
- ATR分位数 > 80%: 高波动环境
- 布林带宽度 = (上轨-下轨)/中轨: 宽度大表示高波动
- ASI趋势判断市场强弱

### 4. 资金流向环境判断

**推荐核心指标组合:**
```python
volume_indicators = {
    '成交量': ['vol', 'amount'],
    '资金流': ['obv_bfq', 'mfi_bfq'],
    '成交量指标': ['vr_bfq', 'emv_bfq']
}
```

**判断逻辑:**
- 成交量放大: 当日成交量 > 历史分位数80%
- OBV上升: 资金流入，OBV下降: 资金流出
- MFI > 80: 资金超买，MFI < 20: 资金超卖

### 5. 市场情绪环境判断

**推荐核心指标组合:**
```python
sentiment_indicators = {
    '人气指标': ['brar_ar_bfq'],
    '意愿指标': ['brar_br_bfq'],
    '能量指标': ['cr_bfq']
}
```

**判断逻辑:**
- AR > 180: 人气过热，AR < 80: 人气低迷
- BR > 300: 意愿过强，BR < 50: 意愿过弱
- CR > 200: 能量过度，CR < 50: 能量不足

## 🔍 实际数据分析示例 (上证指数 000001.SH)

**最新市场环境分析结果 (2025-07-17):**

### 趋势环境: 强势上升趋势 ⭐⭐⭐⭐⭐
- 均线多头排列: 5日(3511.09) > 20日(3465.49) > 60日(3391.61) > 250日(3233.47)
- MACD强势多头: MACD(3.79) > 0, DIF(33.51) > DEA(31.62)
- ADX强趋势: 61.80 > 30

### 动量环境: 超买状态 ⚠️
- RSI12超买: 70.61 > 70
- KDJ死叉: K(59.85) < D(66.55)

### 波动率环境: 高波动 📈
- ATR分位数: 85.7% (高波动环境)
- 布林带宽度: 4.99% (正常)

### 资金环境: 正常流入 💰
- 成交量: 4.72亿 (正常水平)
- OBV资金流入
- MFI: 71.03 (正常)

### 情绪环境: 过热 🔥
- AR人气过热: 199.77 > 180
- CR能量过度: 233.97 > 200

## 📈 技术因子应用建议

### 1. 市场环境识别模型

```python
def identify_market_environment(data):
    """
    基于技术因子的市场环境识别
    """
    # 趋势评分
    trend_score = calculate_trend_score(data)
    
    # 动量评分  
    momentum_score = calculate_momentum_score(data)
    
    # 波动率评分
    volatility_score = calculate_volatility_score(data)
    
    # 综合环境判断
    if trend_score >= 4 and momentum_score < 3:
        return "强势上升 + 超买调整"
    elif trend_score >= 3 and volatility_score < 2:
        return "上升趋势 + 低波动"
    # ... 更多组合判断
```

### 2. 因子筛选策略

**高频交易因子:**
- `rsi_bfq_6`, `kdj_k_bfq`, `wr_bfq` (短期动量)

**中期趋势因子:**
- `ma_bfq_20`, `macd_bfq`, `dmi_adx_bfq` (中期趋势)

**长期环境因子:**
- `ma_bfq_250`, `ema_bfq_250` (长期趋势)

### 3. 因子组合权重建议

| 环境类型 | 趋势因子权重 | 动量因子权重 | 波动率因子权重 | 资金因子权重 |
|---------|-------------|-------------|---------------|-------------|
| 牛市环境 | 40% | 20% | 20% | 20% |
| 熊市环境 | 30% | 30% | 25% | 15% |
| 震荡市场 | 25% | 35% | 25% | 15% |
| 高波动期 | 20% | 25% | 40% | 15% |

## ✅ 总结

1. **数据质量优秀**: index_factor_pro集合包含69个高质量技术因子，数据完整度100%

2. **因子覆盖全面**: 涵盖趋势、动量、波动率、资金流、情绪、市场宽度等6大维度

3. **应用场景丰富**: 适用于市场环境判断、策略信号生成、风险控制等多个场景

4. **实时性良好**: 数据更新至2025-07-17，支持实时市场分析

5. **技术指标专业**: 包含MACD、RSI、KDJ、布林带、ATR等经典技术指标

**建议在量化策略中优先使用以下核心因子组合:**
- 趋势判断: `ma_bfq_20`, `macd_bfq`, `dmi_adx_bfq`
- 动量判断: `rsi_bfq_12`, `kdj_k_bfq`, `wr_bfq`
- 波动率判断: `atr_bfq`, 布林带宽度
- 资金判断: `obv_bfq`, `mfi_bfq`, `vol`
- 情绪判断: `brar_ar_bfq`, `cr_bfq`

这套技术因子体系为构建全面的市场环境判断模型提供了坚实的数据基础。