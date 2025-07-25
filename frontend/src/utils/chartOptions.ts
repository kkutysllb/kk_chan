/**
 * ECharts图表配置生成工具
 * 专为缠论分析优化的图表配置
 */

import type { EChartsOption } from 'echarts'
import type { KLineData, ChanStructure, TradingSignal, TechnicalIndicator } from '@/types/chan'
import { formatDateTime, formatPrice } from './format'

// 缠论颜色配置
export const CHAN_COLORS = {
  // K线颜色
  up: '#ec0000',
  down: '#00da3c',
  
  // 分型颜色
  topFenxing: '#ff4757',
  bottomFenxing: '#2ed573',
  
  // 笔的颜色
  upBi: '#ff6b6b',
  downBi: '#4ecdc4',
  
  // 线段颜色
  upXianduan: '#ff9ff3',
  downXianduan: '#54a0ff',
  
  // 中枢颜色
  zhongshu: '#ffa726',
  zhongshuArea: 'rgba(255, 167, 38, 0.1)',
  
  // 信号颜色
  buySignal: '#00c851',
  sellSignal: '#ff4444',
  
  // 技术指标颜色
  ma5: '#ff6b35',
  ma10: '#f7931e',
  ma20: '#ffb347',
  ma30: '#4ecdc4',
  ma60: '#45b7d1',
  
  macd: '#ff6b35',
  signal: '#4ecdc4',
  histogram: '#ffa726',
  
  rsi: '#9c88ff',
  bollUpper: '#ff6b35',
  bollMiddle: '#ffa726',
  bollLower: '#4ecdc4'
}

interface ChartOptionsParams {
  klineData: KLineData[]
  chanStructures?: ChanStructure | null
  tradingSignals?: TradingSignal[]
  technicalIndicators?: TechnicalIndicator[] | Record<string, any> | null
  symbol: string
  timeframe: string
}

export function generateKLineOption(params: ChartOptionsParams): EChartsOption {
  const {
    klineData,
    chanStructures,
    tradingSignals,
    technicalIndicators,
    symbol,
    timeframe
  } = params

  if (!klineData || klineData.length === 0) {
    return {
      title: {
        text: '暂无数据',
        left: 'center',
        top: 'center'
      }
    }
  }

  // 准备数据 - 确保klineData是数组
  const dataArray = Array.isArray(klineData) ? klineData : []
  const dates = dataArray.map(item => formatDateTime(item.timestamp || item.trade_date, timeframe))
  const ohlcData = dataArray.map(item => [item.open, item.close, item.low, item.high])
  const volumeData = dataArray.map(item => item.volume || item.vol)

  // 基础配置
  const option: EChartsOption = {
    animation: false,
    grid: [
      {
        id: 'main',
        left: '8%',
        right: '8%',
        top: '8%',
        height: '50%'
      },
      {
        id: 'volume',
        left: '8%',
        right: '8%',
        top: '65%',
        height: '16%'
      },
      {
        id: 'indicator',
        left: '8%',
        right: '8%',
        top: '84%',
        height: '12%'
      }
    ],
    xAxis: [
      {
        id: 'main',
        type: 'category',
        data: dates,
        axisLine: { onZero: false },
        splitLine: { show: false },
        gridIndex: 0,
        axisLabel: { show: false }
      },
      {
        id: 'volume',
        type: 'category',
        data: dates,
        axisLine: { onZero: false },
        splitLine: { show: false },
        gridIndex: 1,
        axisLabel: { show: false }
      },
      {
        id: 'indicator',
        type: 'category',
        data: dates,
        axisLine: { onZero: false },
        splitLine: { show: false },
        gridIndex: 2
      }
    ],
    yAxis: [
      {
        id: 'main',
        scale: true,
        gridIndex: 0,
        splitArea: { show: true }
      },
      {
        id: 'volume',
        scale: true,
        gridIndex: 1,
        splitNumber: 2,
        axisLabel: { show: false },
        axisLine: { show: false },
        axisTick: { show: false },
        splitLine: { show: false }
      },
      {
        id: 'indicator',
        scale: true,
        gridIndex: 2,
        splitNumber: 2
      }
    ],
    dataZoom: [
      {
        type: 'inside',
        xAxisIndex: [0, 1, 2],
        start: 70,
        end: 100
      },
      {
        show: true,
        xAxisIndex: [0, 1, 2],
        type: 'slider',
        top: '94%',
        start: 70,
        end: 100
      }
    ],
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'cross'
      },
      formatter: function (params: any) {
        return generateTooltipFormatter(params, klineData)
      }
    },
    series: [] as any[]
  }

  // 添加K线系列
  option.series!.push({
    name: 'K线',
    type: 'candlestick',
    data: ohlcData,
    xAxisIndex: 0,
    yAxisIndex: 0,
    itemStyle: {
      color: CHAN_COLORS.up,
      color0: CHAN_COLORS.down,
      borderColor: CHAN_COLORS.up,
      borderColor0: CHAN_COLORS.down
    }
  })

  // 添加成交量系列
  option.series!.push({
    name: '成交量',
    type: 'bar',
    data: volumeData,
    xAxisIndex: 1,
    yAxisIndex: 1,
    itemStyle: {
      color: function (params: any) {
        const kline = klineData[params.dataIndex]
        return kline.close > kline.open ? CHAN_COLORS.up : CHAN_COLORS.down
      }
    }
  })

  // 添加移动平均线
  if (technicalIndicators) {
    addMovingAverages(option, technicalIndicators, dates)
  }

  // 添加缠论结构
  if (chanStructures) {
    addChanStructures(option, chanStructures, klineData)
  }

  // 添加交易信号
  if (tradingSignals) {
    addTradingSignals(option, tradingSignals, klineData)
  }

  // 添加技术指标（MACD, RSI等）
  if (technicalIndicators) {
    addTechnicalIndicators(option, technicalIndicators, dates)
  }

  return option
}

// 添加移动平均线
function addMovingAverages(
  option: EChartsOption,
  indicators: TechnicalIndicator[] | Record<string, any>,
  dates: string[]
) {
  // 处理不同的数据格式
  let maData: any = null
  
  if (Array.isArray(indicators)) {
    // 如果是数组格式
    maData = indicators.find(ind => ind.name === 'MA')
  } else if (indicators && typeof indicators === 'object') {
    // 如果是对象格式，直接使用MA字段
    maData = indicators.MA || indicators.ma
  }
  
  if (!maData) return

  const maTypes = ['MA5', 'MA10', 'MA20', 'MA30', 'MA60']
  const maColors = [CHAN_COLORS.ma5, CHAN_COLORS.ma10, CHAN_COLORS.ma20, CHAN_COLORS.ma30, CHAN_COLORS.ma60]

  maTypes.forEach((maType, index) => {
    if (maData.data[maType]) {
      option.series!.push({
        name: maType,
        type: 'line',
        data: maData.data[maType],
        xAxisIndex: 0,
        yAxisIndex: 0,
        smooth: true,
        lineStyle: {
          color: maColors[index],
          width: 1
        },
        showSymbol: false
      })
    }
  })
}

// 添加缠论结构
function addChanStructures(
  option: EChartsOption,
  structures: ChanStructure,
  klineData: KLineData[]
) {
  // 添加分型标记点
  if (structures.fenxings && structures.fenxings.length > 0) {
    const fenxingMarkPoints = structures.fenxings.map((fx: any) => ({
      name: fx.fenxing_type === 'top' ? '顶分型' : '底分型',
      coord: [fx.index, fx.price],
      symbol: fx.fenxing_type === 'top' ? 'triangle' : 'diamond',
      symbolSize: 8,
      itemStyle: {
        color: fx.fenxing_type === 'top' ? CHAN_COLORS.topFenxing : CHAN_COLORS.bottomFenxing
      },
      structureId: fx.id
    }))

    // 将分型添加到K线系列的markPoint中
    const klineSeries = option.series![0] as any
    if (!klineSeries.markPoint) {
      klineSeries.markPoint = { data: [] }
    }
    klineSeries.markPoint.data.push(...fenxingMarkPoints)
  }

  // 添加笔的标记线
  if (structures.bis && structures.bis.length > 0) {
    const biMarkLines = structures.bis.map((bi: any) => ({
      name: `${bi.direction === 'up' ? '上笔' : '下笔'}`,
      lineStyle: {
        color: bi.direction === 'up' ? CHAN_COLORS.upBi : CHAN_COLORS.downBi,
        width: 2,
        type: 'solid'
      },
      data: [
        { coord: [bi.start_fenxing.index, bi.start_fenxing.price] },
        { coord: [bi.end_fenxing.index, bi.end_fenxing.price] }
      ],
      structureId: bi.id
    }))

    const klineSeries = option.series![0] as any
    if (!klineSeries.markLine) {
      klineSeries.markLine = { data: [] }
    }
    klineSeries.markLine.data.push(...biMarkLines)
  }

  // 添加中枢区域
  if (structures.zhongshus && structures.zhongshus.length > 0) {
    structures.zhongshus.forEach((zs: any) => {
      // 找到对应的时间索引
      const startIndex = klineData.findIndex(k => new Date(k.timestamp) >= new Date(zs.start_time))
      const endIndex = klineData.findIndex(k => new Date(k.timestamp) >= new Date(zs.end_time))
      
      if (startIndex !== -1 && endIndex !== -1) {
        // 添加中枢区域
        option.series!.push({
          name: '中枢',
          type: 'line',
          xAxisIndex: 0,
          yAxisIndex: 0,
          data: Array(klineData.length).fill(null).map((_, index) => {
            if (index >= startIndex && index <= endIndex) {
              return zs.high
            }
            return null
          }),
          lineStyle: {
            color: CHAN_COLORS.zhongshu,
            width: 1,
            type: 'dashed'
          },
          areaStyle: {
            color: CHAN_COLORS.zhongshuArea
          },
          showSymbol: false,
          silent: true
        })

        // 添加中枢下边线
        option.series!.push({
          name: '中枢下边',
          type: 'line',
          xAxisIndex: 0,
          yAxisIndex: 0,
          data: Array(klineData.length).fill(null).map((_, index) => {
            if (index >= startIndex && index <= endIndex) {
              return zs.low
            }
            return null
          }),
          lineStyle: {
            color: CHAN_COLORS.zhongshu,
            width: 1,
            type: 'dashed'
          },
          showSymbol: false,
          silent: true
        })
      }
    })
  }
}

// 添加交易信号
function addTradingSignals(
  option: EChartsOption,
  signals: TradingSignal[],
  klineData: KLineData[]
) {
  const signalMarkPoints = signals.map((signal: any) => {
    // 找到对应的时间索引
    const index = klineData.findIndex(k => 
      Math.abs(new Date(k.timestamp).getTime() - new Date(signal.timestamp).getTime()) < 60000
    )
    
    if (index === -1) return null

    return {
      name: signal.signal_type === 'buy' ? '买入信号' : '卖出信号',
      coord: [index, signal.price],
      symbol: signal.signal_type === 'buy' ? 'arrow' : 'arrow',
      symbolRotate: signal.signal_type === 'buy' ? 0 : 180,
      symbolSize: [12, 16],
      itemStyle: {
        color: signal.signal_type === 'buy' ? CHAN_COLORS.buySignal : CHAN_COLORS.sellSignal
      },
      label: {
        show: true,
        position: signal.signal_type === 'buy' ? 'bottom' : 'top',
        formatter: signal.signal_subtype.toUpperCase(),
        fontSize: 10
      },
      signalId: signal.id
    }
  }).filter(Boolean)

  if (signalMarkPoints.length > 0) {
    const klineSeries = option.series![0] as any
    if (!klineSeries.markPoint) {
      klineSeries.markPoint = { data: [] }
    }
    klineSeries.markPoint.data.push(...signalMarkPoints)
  }
}

// 添加技术指标
function addTechnicalIndicators(
  option: EChartsOption,
  indicators: TechnicalIndicator[] | Record<string, any>,
  dates: string[]
) {
  // 处理不同的数据格式
  let macdData: any = null
  let rsiData: any = null
  
  if (Array.isArray(indicators)) {
    // 如果是数组格式
    macdData = indicators.find(ind => ind.name === 'MACD')
    rsiData = indicators.find(ind => ind.name === 'RSI')
  } else if (indicators && typeof indicators === 'object') {
    // 如果是对象格式
    macdData = indicators.MACD || indicators.macd
    rsiData = indicators.RSI || indicators.rsi
  }
  
  // 添加MACD
  if (macdData) {
    // MACD柱状图
    option.series!.push({
      name: 'MACD',
      type: 'bar',
      data: macdData.data.histogram || [],
      xAxisIndex: 2,
      yAxisIndex: 2,
      itemStyle: {
        color: function (params: any) {
          return params.value > 0 ? CHAN_COLORS.up : CHAN_COLORS.down
        }
      }
    })

    // DIF线
    if (macdData.data.dif) {
      option.series!.push({
        name: 'DIF',
        type: 'line',
        data: macdData.data.dif,
        xAxisIndex: 2,
        yAxisIndex: 2,
        lineStyle: { color: CHAN_COLORS.macd, width: 1 },
        showSymbol: false
      })
    }

    // DEA线
    if (macdData.data.dea) {
      option.series!.push({
        name: 'DEA',
        type: 'line',
        data: macdData.data.dea,
        xAxisIndex: 2,
        yAxisIndex: 2,
        lineStyle: { color: CHAN_COLORS.signal, width: 1 },
        showSymbol: false
      })
    }
  }
}

// 生成Tooltip格式化器
function generateTooltipFormatter(params: any, klineData: KLineData[]) {
  if (!params || params.length === 0) return ''

  const dataIndex = params[0].dataIndex
  const kline = klineData[dataIndex]
  
  if (!kline) return ''

  let html = `
    <div style="margin-bottom: 8px;">
      <strong>${formatDateTime(kline.timestamp)}</strong>
    </div>
    <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
      <span>开盘:</span>
      <span style="color: ${kline.close > kline.open ? CHAN_COLORS.up : CHAN_COLORS.down};">
        ${formatPrice(kline.open)}
      </span>
    </div>
    <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
      <span>收盘:</span>
      <span style="color: ${kline.close > kline.open ? CHAN_COLORS.up : CHAN_COLORS.down};">
        ${formatPrice(kline.close)}
      </span>
    </div>
    <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
      <span>最高:</span>
      <span>${formatPrice(kline.high)}</span>
    </div>
    <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
      <span>最低:</span>
      <span>${formatPrice(kline.low)}</span>
    </div>
    <div style="display: flex; justify-content: space-between;">
      <span>成交量:</span>
      <span>${(kline.volume / 10000).toFixed(2)}万</span>
    </div>
  `

  // 添加其他指标信息
  params.forEach((param: any) => {
    if (param.seriesName && !['K线', '成交量'].includes(param.seriesName)) {
      html += `
        <div style="display: flex; justify-content: space-between; margin-top: 4px;">
          <span>${param.seriesName}:</span>
          <span style="color: ${param.color};">${formatPrice(param.value)}</span>
        </div>
      `
    }
  })

  return html
}