<template>
  <div class="chan-chart">
    <el-card class="chart-card">
      <template #header>
        <div class="chart-header">
          <div class="chart-title">
            <span>{{ chartTitle }}</span>
            <el-tag v-if="currentStock" size="small" type="primary">
              {{ currentStock.symbol }}
            </el-tag>
          </div>
          <div class="chart-controls">
            <el-button-group size="small">
              <el-button
                v-for="preset in timePresets"
                :key="preset.value"
                :type="currentTimeframe === preset.value ? 'primary' : 'default'"
                @click="changeTimeframe(preset.value)"
              >
                {{ preset.label }}
              </el-button>
            </el-button-group>
            <el-button
              :icon="RefreshRight"
              size="small"
              @click="refreshChart"
              :loading="refreshing"
              title="刷新图表"
            />
            <el-button
              :icon="Download"
              size="small"
              @click="exportChart"
              title="导出图片"
            />
          </div>
        </div>
      </template>

      <div class="chart-container">
        <!-- 加载状态 -->
        <div v-if="loading" class="chart-loading">
          <el-skeleton animated>
            <template #template>
              <el-skeleton-item variant="rect" style="width: 100%; height: 400px;" />
            </template>
          </el-skeleton>
        </div>

        <!-- 无数据状态 -->
        <div v-else-if="!hasData" class="chart-empty">
          <el-empty
            description="暂无数据"
            :image-size="120"
          >
            <el-button type="primary" @click="$emit('analyze')">
              开始分析
            </el-button>
          </el-empty>
        </div>

        <!-- 图表内容 -->
        <div v-else class="chart-content">
          <!-- 主图表 -->
          <v-chart
            ref="mainChartRef"
            :option="mainChartOption"
            :theme="isDark ? 'dark' : 'light'"
            autoresize
            class="main-chart"
            @click="handleChartClick"
          />

          <!-- MACD图表 -->
          <v-chart
            ref="macdChartRef"
            :option="macdChartOption"
            :theme="isDark ? 'dark' : 'light'"
            autoresize
            class="macd-chart"
          />
        </div>

        <!-- 数据统计 -->
        <div v-if="hasData" class="chart-stats">
          <div class="stats-item">
            <span class="stats-label">分型:</span>
            <span class="stats-value">{{ summary?.fenxing_count || 0 }}</span>
          </div>
          <div class="stats-item">
            <span class="stats-label">笔:</span>
            <span class="stats-value">{{ summary?.bi_count || 0 }}</span>
          </div>
          <div class="stats-item">
            <span class="stats-label">中枢:</span>
            <span class="stats-value">{{ summary?.zhongshu_count || 0 }}</span>
          </div>
          <div class="stats-item">
            <span class="stats-label">信号:</span>
            <span class="stats-value">{{ summary?.signal_count || 0 }}</span>
          </div>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, watch, nextTick } from 'vue'
import { use } from 'echarts/core'
import { CustomChart } from 'echarts/charts'
import VChart from 'vue-echarts'
import { RefreshRight, Download } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { useGlobalStore } from '@/stores/global'

// 注册 CustomChart
use([CustomChart])

const global = useGlobalStore()

// 组件状态
const mainChartRef = ref()
const macdChartRef = ref()
const refreshing = ref(false)
const isDark = ref(false)

// 时间级别预设
const timePresets = [
  { label: '5分', value: '5min' },
  { label: '30分', value: '30min' },
  { label: '日线', value: 'daily' },
]

// 计算属性
const loading = computed(() => global.loading)
const hasData = computed(() => global.hasData)
const currentStock = computed(() => global.currentStock)
const currentTimeframe = computed(() => global.currentTimeframe)
const summary = computed(() => global.analysisSummary)
const chartData = computed(() => global.chartData)
const klineData = computed(() => global.klineData)
const chanStructures = computed(() => global.chanStructures)
const tradingSignals = computed(() => global.tradingSignals)

const chartTitle = computed(() => {
  if (!currentStock.value) return '缠论分析图表'
  const { symbol, timeframe } = currentStock.value
  const timeframeMap = {
    '5min': '5分钟',
    '30min': '30分钟',
    'daily': '日线',
  }
  return `${symbol} - ${timeframeMap[timeframe] || timeframe}`
})

// 主图表配置
const mainChartOption = computed(() => {
  console.log('计算图表配置 - hasData:', hasData.value, 'klineData:', klineData.value)
  
  if (!hasData.value || !klineData.value) {
    console.log('没有数据，返回空配置')
    return {}
  }

  const { categories, values } = klineData.value
  
  // 调试：直接从全局状态获取数据
  console.log('全局状态数据:', global.analysisData?.chart_data)
  console.log('chanStructures路径:', global.analysisData?.chart_data?.chan_structures)
  console.log('signals路径:', global.analysisData?.chart_data?.signals)
  
  // 直接从global.analysisData获取数据，绕过computed属性
  const rawChanStructures = global.analysisData?.chart_data?.chan_structures
  const rawSignals = global.analysisData?.chart_data?.signals
  
  const fenxingData = rawChanStructures?.fenxing || []
  const biData = rawChanStructures?.bi || []
  const zhongshuData = rawChanStructures?.zhongshu || []
  const signals = rawSignals || []
  
  console.log('缠论数据:', {
    fenxingData: fenxingData.length,
    biData: biData.length, 
    zhongshuData: zhongshuData.length,
    signals: signals.length
  })
  console.log('具体数据:', { fenxingData, biData, zhongshuData, signals })

  return {
    title: {
      text: chartTitle.value,
      left: 'center',
      textStyle: {
        fontSize: 16,
        fontWeight: 'bold',
      },
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'cross',
        animation: false,
      },
      formatter: function (params) {
        if (!params || params.length === 0) return ''
        
        const dataIndex = params[0].dataIndex
        const categoryValue = categories[dataIndex]
        const klineValue = values[dataIndex]
        
        if (!klineValue) return ''
        
        const [open, close, low, high] = klineValue
        const color = close >= open ? '#ef5150' : '#26a69a'
        const change = ((close - open) / open * 100).toFixed(2)
        
        return `
          <div style="text-align: left;">
            <div style="margin-bottom: 8px; font-weight: bold;">${categoryValue}</div>
            <div style="color: ${color};">
              开盘: ${open}<br/>
              收盘: ${close}<br/>
              最低: ${low}<br/>
              最高: ${high}<br/>
              涨跌: ${change}%
            </div>
          </div>
        `
      },
    },
    legend: {
      data: [
        { name: 'K线', icon: 'rect' },
        ...(fenxingData.filter(f => f.type === 'top').length > 0 ? [{ name: '顶分型', icon: 'triangle' }] : []),
        ...(fenxingData.filter(f => f.type === 'bottom').length > 0 ? [{ name: '底分型', icon: 'triangle' }] : []),
        ...(biData.filter(b => b.direction === 'up').length > 0 ? [{ name: '上笔', icon: 'line', textStyle: { color: '#e91e63' } }] : []),
        ...(biData.filter(b => b.direction === 'down').length > 0 ? [{ name: '下笔', icon: 'line', textStyle: { color: '#2196f3' } }] : []),
        ...(zhongshuData.length > 0 ? [{ name: '中枢', icon: 'rect', textStyle: { color: '#ff9800' } }] : []),
        ...(signals.filter(s => s.type === 'buy').length > 0 ? [{ name: '买点', icon: 'arrow' }] : []),
        ...(signals.filter(s => s.type === 'sell').length > 0 ? [{ name: '卖点', icon: 'arrow' }] : [])
      ],
      top: 30,
    },
    grid: {
      left: '3%',
      right: '3%',
      top: '15%',
      bottom: '25%',
      containLabel: true,
    },
    xAxis: {
      type: 'category',
      data: categories,
      boundaryGap: false,
      axisLine: { onZero: false },
      splitLine: { show: false },
      min: 'dataMin',
      max: 'dataMax',
    },
    yAxis: {
      scale: true,
      splitArea: {
        show: true,
      },
    },
    dataZoom: [
      {
        type: 'inside',
        start: 80,
        end: 100,
      },
      {
        show: true,
        type: 'slider',
        top: '90%',
        start: 80,
        end: 100,
      },
    ],
    series: [
      // K线图
      {
        name: 'K线',
        type: 'candlestick',
        data: values,
        itemStyle: {
          color: '#ef5150',      // 阳线颜色
          color0: '#26a69a',     // 阴线颜色
          borderColor: '#ef5150',
          borderColor0: '#26a69a',
        },
      },
      // 顶分型
      {
        name: '顶分型',
        type: 'scatter',
        data: fenxingData
          .filter(item => item.type === 'top')
          .map(item => ({
            value: [item.coord[0], item.coord[1]],
            tooltip: {
              formatter: `${item.name}<br/>价格: ${item.value}<br/>强度: ${item.strength}`,
            },
          })),
        symbol: 'triangle',
        symbolRotate: 0,
        symbolSize: 8,
        itemStyle: {
          color: '#f44336',
        },
        zlevel: 10,
      },
      // 底分型
      {
        name: '底分型',
        type: 'scatter',
        data: fenxingData
          .filter(item => item.type === 'bottom')
          .map(item => ({
            value: [item.coord[0], item.coord[1]],
            tooltip: {
              formatter: `${item.name}<br/>价格: ${item.value}<br/>强度: ${item.strength}`,
            },
          })),
        symbol: 'triangle',
        symbolRotate: 180,
        symbolSize: 8,
        itemStyle: {
          color: '#4caf50',
        },
        zlevel: 10,
      },
      // 上笔
      ...biData.filter(bi => bi.direction === 'up').map((bi, index) => ({
        name: index === 0 ? '上笔' : '',
        type: 'line',
        data: [
          { name: bi.coords[0][0], value: [bi.coords[0][0], bi.coords[0][1]] },
          { name: bi.coords[1][0], value: [bi.coords[1][0], bi.coords[1][1]] }
        ],
        lineStyle: {
          color: '#e91e63',
          width: 2,
        },
        symbol: 'none',
        tooltip: {
          formatter: `${bi.name}<br/>幅度: ${(bi.amplitude * 100).toFixed(2)}%<br/>长度: ${bi.length}个K线`,
        },
        zlevel: 5,
      })),
      // 下笔
      ...biData.filter(bi => bi.direction === 'down').map((bi, index) => ({
        name: index === 0 ? '下笔' : '',
        type: 'line',
        data: [
          { name: bi.coords[0][0], value: [bi.coords[0][0], bi.coords[0][1]] },
          { name: bi.coords[1][0], value: [bi.coords[1][0], bi.coords[1][1]] }
        ],
        lineStyle: {
          color: '#2196f3',
          width: 2,
        },
        symbol: 'none',
        tooltip: {
          formatter: `${bi.name}<br/>幅度: ${(bi.amplitude * 100).toFixed(2)}%<br/>长度: ${bi.length}个K线`,
        },
        zlevel: 5,
      })),
      // 中枢区域
      ...zhongshuData.map((zs, index) => ({
        name: index === 0 ? '中枢' : '',
        type: 'custom',
        renderItem: function (params, api) {
          const startTime = zs.coords[0][0]
          const endTime = zs.coords[1][0]
          const high = zs.high
          const low = zs.low
          
          const startPoint = api.coord([startTime, high])
          const endPoint = api.coord([endTime, high])
          const startLowPoint = api.coord([startTime, low])
          
          if (!startPoint || !endPoint || !startLowPoint) return null
          
          return {
            type: 'rect',
            shape: {
              x: startPoint[0],
              y: startPoint[1],
              width: endPoint[0] - startPoint[0],
              height: startLowPoint[1] - startPoint[1]
            },
            style: {
              fill: 'rgba(255, 152, 0, 0.15)',
              stroke: '#ff9800',
              lineWidth: 1,
            }
          }
        },
        data: [[zs.coords[0][0], zs.coords[1][0], zs.high, zs.low]],
        tooltip: {
          formatter: `${zs.name}<br/>高点: ${zs.high}<br/>低点: ${zs.low}<br/>中心: ${zs.center}<br/>持续时间: ${zs.duration}个交易日`,
        },
        zlevel: 1,
      })),
      // 买点
      {
        name: '买点',
        type: 'scatter',
        data: signals
          .filter(signal => signal.type === 'buy')
          .map(signal => ({
            value: [signal.coord[0], signal.coord[1]],
            tooltip: {
              formatter: `${signal.name}<br/>价格: ${signal.coord[1]}<br/>描述: ${signal.description || ''}`,
            },
          })),
        symbol: 'arrow',
        symbolRotate: 90,
        symbolSize: 12,
        itemStyle: {
          color: '#4caf50',
        },
        zlevel: 15,
      },
      // 卖点
      {
        name: '卖点',
        type: 'scatter',
        data: signals
          .filter(signal => signal.type === 'sell')
          .map(signal => ({
            value: [signal.coord[0], signal.coord[1]],
            tooltip: {
              formatter: `${signal.name}<br/>价格: ${signal.coord[1]}<br/>描述: ${signal.description || ''}`,
            },
          })),
        symbol: 'arrow',
        symbolRotate: -90,
        symbolSize: 12,
        itemStyle: {
          color: '#f44336',
        },
        zlevel: 15,
      },
    ],
  }
})

// MACD图表配置 - 修正样式错乱问题
const macdChartOption = computed(() => {
  if (!hasData.value || !klineData.value) {
    return {}
  }

  const { categories } = klineData.value
  const macdData = global.analysisData?.chart_data?.indicators?.macd || { dif: [], dea: [], macd: [] }

  console.log('MACD数据调试:', {
    categories: categories?.length,
    dif: macdData.dif?.length,
    dea: macdData.dea?.length,
    macd: macdData.macd?.length,
    difSample: macdData.dif?.slice(0, 3),
    deaSample: macdData.dea?.slice(0, 3),
    macdSample: macdData.macd?.slice(0, 3)
  })

  return {
    animation: false,
    legend: {
      bottom: 5,
      left: 'center',
      data: ['DIF', 'DEA', 'MACD'],
      textStyle: {
        fontSize: 12,
        color: '#666'
      }
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'cross'
      }
    },
    grid: {
      left: '8%',
      right: '8%',
      top: '10%',
      bottom: '20%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: categories,
      boundaryGap: false,
      axisLine: { 
        show: true,
        lineStyle: { color: '#ccc' }
      },
      axisTick: { show: false },
      axisLabel: { 
        show: true,
        fontSize: 10,
        color: '#666',
        interval: 'auto',
        rotate: 0
      },
      splitLine: { show: false }
    },
    yAxis: {
      type: 'value',
      scale: true,
      axisLine: { 
        show: true,
        lineStyle: { color: '#ccc' }
      },
      axisTick: { show: false },
      axisLabel: {
        show: true,
        fontSize: 10,
        color: '#666'
      },
      splitLine: { 
        show: true,
        lineStyle: {
          color: '#f0f0f0'
        }
      }
    },
    dataZoom: [
      {
        type: 'inside',
        start: 80,
        end: 100
      }
    ],
    series: [
      // MACD柱状图放在最底层
      {
        name: 'MACD',
        type: 'bar',
        data: (macdData.macd || []).map((value) => ({
          value: value || 0,
          itemStyle: {
            color: (value || 0) >= 0 ? '#ff6b6b' : '#4ecdc4'
          }
        })),
        barWidth: '50%',
        z: 1
      },
      // DIF线
      {
        name: 'DIF',
        type: 'line',
        data: macdData.dif || [],
        symbol: 'none',  // 去掉圆点标记
        smooth: false,   // 不平滑，显示真实数据点
        lineStyle: {
          color: '#ff4757',
          width: 2
        },
        z: 3
      },
      // DEA线  
      {
        name: 'DEA',
        type: 'line',
        data: macdData.dea || [],
        symbol: 'none',  // 去掉圆点标记
        smooth: false,   // 不平滑，显示真实数据点
        lineStyle: {
          color: '#3742fa',
          width: 2
        },
        z: 3
      }
    ]
  }
})

// 切换时间级别
const changeTimeframe = async (timeframe) => {
  if (timeframe === currentTimeframe.value) return
  
  try {
    await global.fetchAnalysisData({ timeframe })
  } catch (error) {
    ElMessage.error('切换时间级别失败')
  }
}

// 刷新图表
const refreshChart = async () => {
  refreshing.value = true
  try {
    await global.refreshAllData()
    ElMessage.success('图表刷新成功')
  } catch (error) {
    ElMessage.error('图表刷新失败')
  } finally {
    refreshing.value = false
  }
}

// 导出图表
const exportChart = () => {
  if (!mainChartRef.value) {
    ElMessage.warning('图表未加载完成')
    return
  }
  
  try {
    const url = mainChartRef.value.getDataURL({
      type: 'png',
      pixelRatio: 2,
      backgroundColor: '#fff',
    })
    
    const link = document.createElement('a')
    link.download = `${currentStock.value?.symbol || 'chart'}_${currentTimeframe.value}_${Date.now()}.png`
    link.href = url
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    
    ElMessage.success('图表导出成功')
  } catch (error) {
    console.error('导出失败:', error)
    ElMessage.error('图表导出失败')
  }
}

// 图表点击事件
const handleChartClick = (params) => {
  console.log('图表点击:', params)
  // 可以在这里处理图表点击事件，比如显示详细信息
}

// 监听数据变化，重新渲染图表
watch([hasData, chartData], () => {
  nextTick(() => {
    if (mainChartRef.value) {
      mainChartRef.value.resize()
    }
    if (macdChartRef.value) {
      macdChartRef.value.resize()
    }
  })
})

// 暴露方法给父组件
defineExpose({
  refreshChart,
  exportChart,
})

// 发射事件
defineEmits(['analyze'])
</script>

<style scoped>
.chan-chart {
  min-height: 600px;
}

.chart-card {
  min-height: 600px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  
  :deep(.el-card__header) {
    background: transparent;
    border-bottom: 1px solid rgba(0, 0, 0, 0.06);
    padding: 20px 24px;
  }
  
  :deep(.el-card__body) {
    min-height: calc(600px - 80px);
    padding: 0;
    background: transparent;
  }
}

.dark .chart-card {
  background: rgba(44, 62, 80, 0.95);
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
  
  :deep(.el-card__header) {
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  }
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chart-title {
  display: flex;
  align-items: center;
  gap: 12px;
  font-weight: bold;
}

.chart-controls {
  display: flex;
  align-items: center;
  gap: 12px;
  
  :deep(.el-button-group .el-button) {
    border-radius: 8px;
    font-weight: 500;
    transition: all 0.3s ease;
    padding: 8px 16px;
  }
  
  :deep(.el-button-group .el-button--primary) {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-color: transparent;
    color: white;
    box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
  }
  
  :deep(.el-button-group .el-button:hover) {
    transform: translateY(-1px);
  }
  
  :deep(.el-button) {
    border-radius: 8px;
    transition: all 0.3s ease;
  }
  
  :deep(.el-button:hover) {
    transform: translateY(-1px);
  }
}

.chart-container {
  min-height: 520px;
  position: relative;
  padding: 24px;
  background: transparent;
}

.chart-loading {
  min-height: 400px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.chart-empty {
  min-height: 400px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.chart-content {
  min-height: 400px;
  display: flex;
  flex-direction: column;
}

.main-chart {
  flex: 1;
  min-height: 400px;
}

.macd-chart {
  height: 200px;
  margin-top: 16px;
}

.chart-stats {
  position: absolute;
  top: 20px;
  right: 20px;
  display: flex;
  gap: 12px;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(10px);
  padding: 10px 14px;
  border-radius: 10px;
  font-size: 12px;
  z-index: 10;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  max-width: calc(100% - 40px);
  flex-wrap: wrap;
}

.dark .chart-stats {
  background: rgba(44, 62, 80, 0.9);
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}

.stats-item {
  display: flex;
  align-items: center;
  gap: 4px;
}

.stats-label {
  color: var(--el-text-color-secondary);
}

.stats-value {
  color: #667eea;
  font-weight: 600;
}

@media (max-width: 768px) {
  .chart-container {
    padding: 16px;
  }
  
  .chart-header {
    flex-direction: column;
    gap: 12px;
    align-items: flex-start;
  }
  
  .chart-stats {
    position: static;
    margin-bottom: 12px;
    justify-content: center;
    font-size: 11px;
    padding: 8px 12px;
  }
  
  .main-chart {
    min-height: 250px;
  }
  
  .macd-chart {
    height: 150px;
  }
}
</style>