<template>
  <div class="market-heatmap">
    <div class="heatmap-header">
      <div class="header-left">
        <h3>市场热力图</h3>
        <el-select v-model="selectedMetric" @change="onMetricChange" size="small">
          <el-option
            v-for="metric in metrics"
            :key="metric.value"
            :label="metric.label"
            :value="metric.value"
          />
        </el-select>
      </div>
      
      <div class="header-right">
        <el-radio-group v-model="selectedTimeframe" @change="onTimeframeChange" size="small">
          <el-radio-button 
            v-for="tf in timeframes"
            :key="tf.value"
            :value="tf.value"
          >
            {{ tf.label }}
          </el-radio-button>
        </el-radio-group>
        
        <el-button @click="refreshData" :loading="loading" size="small">
          <el-icon><Refresh /></el-icon>
        </el-button>
      </div>
    </div>

    <div class="heatmap-container" ref="heatmapContainer">
      <v-chart
        ref="heatmapRef"
        :option="heatmapOption"
        :loading="loading"
        :autoresize="true"
        @click="onHeatmapClick"
        @mouseover="onHeatmapMouseOver"
        class="heatmap-chart"
      />
    </div>

    <div class="heatmap-legend">
      <div class="legend-item">
        <span class="color-indicator hot"></span>
        <span>强势</span>
      </div>
      <div class="legend-item">
        <span class="color-indicator warm"></span>
        <span>偏强</span>
      </div>
      <div class="legend-item">
        <span class="color-indicator neutral"></span>
        <span>中性</span>
      </div>
      <div class="legend-item">
        <span class="color-indicator cool"></span>
        <span>偏弱</span>
      </div>
      <div class="legend-item">
        <span class="color-indicator cold"></span>
        <span>弱势</span>
      </div>
    </div>

    <!-- 股票详情抽屉 -->
    <el-drawer
      v-model="stockDrawerVisible"
      :title="`${selectedStock?.name} (${selectedStock?.symbol})`"
      direction="rtl"
      size="400px"
    >
      <StockDetailPanel
        v-if="selectedStock"
        :stock="selectedStock"
        :metric="selectedMetric"
      />
    </el-drawer>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import { useResizeObserver } from '@vueuse/core'
import { apiService } from '@/services/api'
import StockDetailPanel from './StockDetailPanel.vue'
import { formatPercent, formatPrice } from '@/utils/format'

interface Props {
  market?: string
  sectors?: string[]
  autoRefresh?: boolean
  refreshInterval?: number
}

const props = withDefaults(defineProps<Props>(), {
  market: 'A股',
  sectors: () => [],
  autoRefresh: false,
  refreshInterval: 60000
})

// 响应式数据
const heatmapRef = ref()
const heatmapContainer = ref()
const loading = ref(false)
const selectedMetric = ref('chan_strength')
const selectedTimeframe = ref('daily')
const stockDrawerVisible = ref(false)
const selectedStock = ref<any>(null)
const heatmapData = ref<any[]>([])

// 配置选项
const metrics = [
  { label: '缠论强度', value: 'chan_strength' },
  { label: '趋势强度', value: 'trend_strength' },
  { label: '突破概率', value: 'breakout_probability' },
  { label: '信号质量', value: 'signal_quality' },
  { label: '价格涨跌幅', value: 'price_change' },
  { label: '成交量比率', value: 'volume_ratio' },
  { label: '资金流向', value: 'money_flow' }
]

const timeframes = [
  { label: '5分钟', value: '5min' },
  { label: '30分钟', value: '30min' },
  { label: '日线', value: 'daily' }
]

// 计算属性
const heatmapOption = computed(() => {
  if (!heatmapData.value || heatmapData.value.length === 0) {
    return {
      title: {
        text: '暂无数据',
        left: 'center',
        top: 'center',
        textStyle: {
          color: '#909399',
          fontSize: 16
        }
      }
    }
  }

  // 准备数据
  const data = heatmapData.value.map(item => ({
    name: item.name,
    value: item.value,
    symbol: item.symbol,
    sector: item.sector,
    market_cap: item.market_cap || 0,
    itemStyle: {
      color: getColorByValue(item.change_pct || item.color_value || 0),
      borderColor: '#fff',
      borderWidth: 1
    },
    label: {
      show: true,
      formatter: (params: any) => {
        const lines = [
          params.data.name,
          getValueText(params.data.value, selectedMetric.value)
        ]
        return lines.join('\n')
      },
      fontSize: 10,
      color: '#fff',
      fontWeight: 'bold'
    }
  }))

  return {
    title: {
      text: `${getMetricLabel(selectedMetric.value)} - ${props.market}`,
      left: 'center',
      top: 20,
      textStyle: {
        color: '#303133',
        fontSize: 16,
        fontWeight: 'bold'
      }
    },
    tooltip: {
      trigger: 'item',
      formatter: (params: any) => {
        const data = params.data
        return `
          <div style="text-align: left;">
            <div style="margin-bottom: 4px;">
              <strong>${data.name} (${data.symbol})</strong>
            </div>
            <div style="margin-bottom: 2px;">
              行业: ${data.sector}
            </div>
            <div style="margin-bottom: 2px;">
              ${getMetricLabel(selectedMetric.value)}: ${getValueText(data.value, selectedMetric.value)}
            </div>
            <div style="margin-bottom: 2px;">
              市值: ${formatMarketCap(data.market_cap)}
            </div>
          </div>
        `
      }
    },
    series: [{
      type: 'treemap',
      data: data,
      roam: false,
      breadcrumb: {
        show: false
      },
      leafDepth: 1,
      levels: [{
        itemStyle: {
          borderColor: '#fff',
          borderWidth: 2,
          gapWidth: 2
        }
      }],
      animationDurationUpdate: 1000
    }]
  }
})

// 方法
const getColorByValue = (value: number): string => {
  // 标准化到0-1区间
  const normalized = Math.max(0, Math.min(1, (value + 1) / 2))
  
  if (normalized > 0.8) return '#ff4757' // 热 - 红色
  if (normalized > 0.6) return '#ff7675' // 暖 - 浅红色
  if (normalized > 0.4) return '#fdcb6e' // 中性 - 黄色
  if (normalized > 0.2) return '#74b9ff' // 凉 - 浅蓝色
  return '#0984e3' // 冷 - 蓝色
}

const getValueText = (value: number, metric: string): string => {
  switch (metric) {
    case 'chan_strength':
    case 'trend_strength':
    case 'breakout_probability':
    case 'signal_quality':
      return formatPercent(value)
    case 'price_change':
      return `${value > 0 ? '+' : ''}${formatPercent(value / 100)}`
    case 'volume_ratio':
      return `${value.toFixed(2)}倍`
    case 'money_flow':
      return value > 0 ? '净流入' : '净流出'
    default:
      return value.toString()
  }
}

const getMetricLabel = (metric: string): string => {
  const metricObj = metrics.find(m => m.value === metric)
  return metricObj?.label || metric
}

const formatMarketCap = (marketCap: number): string => {
  if (marketCap >= 1e12) {
    return `${(marketCap / 1e12).toFixed(1)}万亿`
  } else if (marketCap >= 1e8) {
    return `${(marketCap / 1e8).toFixed(0)}亿`
  } else if (marketCap >= 1e4) {
    return `${(marketCap / 1e4).toFixed(0)}万`
  }
  return marketCap.toString()
}

const loadHeatmapData = async () => {
  loading.value = true
  try {
    const response = await apiService.getMarketHeatmap({
      market: props.market,
      metric: selectedMetric.value,
      timeframe: selectedTimeframe.value,
      sectors: props.sectors
    })
    
    heatmapData.value = response.data?.data || response.data || []
  } catch (error) {
    console.error('加载热力图数据失败:', error)
    ElMessage.error('加载热力图数据失败')
    heatmapData.value = []
  } finally {
    loading.value = false
  }
}

const onMetricChange = () => {
  loadHeatmapData()
}

const onTimeframeChange = () => {
  loadHeatmapData()
}

const refreshData = () => {
  loadHeatmapData()
}

const onHeatmapClick = (params: any) => {
  if (params.data) {
    selectedStock.value = {
      symbol: params.data.symbol,
      name: params.data.name,
      sector: params.data.sector,
      market_cap: params.data.market_cap,
      value: params.data.value,
      color_value: params.data.color_value
    }
    stockDrawerVisible.value = true
  }
}

const onHeatmapMouseOver = (params: any) => {
  // 可以在这里添加悬停效果
}

// 生命周期
onMounted(() => {
  loadHeatmapData()
  
  // 自动刷新
  if (props.autoRefresh) {
    setInterval(() => {
      if (!loading.value) {
        loadHeatmapData()
      }
    }, props.refreshInterval)
  }
})

// 监听容器大小变化
useResizeObserver(heatmapContainer, () => {
  nextTick(() => {
    heatmapRef.value?.resize()
  })
})

// 监听props变化
watch(
  () => [props.market, props.sectors],
  () => {
    loadHeatmapData()
  },
  { deep: true }
)
</script>

<style lang="scss" scoped>
.market-heatmap {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  overflow: hidden;

  .heatmap-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 16px 20px;
    border-bottom: 1px solid #ebeef5;
    background: #fafafa;

    .header-left {
      display: flex;
      align-items: center;
      gap: 16px;

      h3 {
        margin: 0;
        color: #303133;
        font-size: 16px;
        font-weight: 600;
      }
    }

    .header-right {
      display: flex;
      align-items: center;
      gap: 12px;
    }
  }

  .heatmap-container {
    height: 500px;
    position: relative;

    .heatmap-chart {
      width: 100%;
      height: 100%;
    }
  }

  .heatmap-legend {
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 24px;
    padding: 16px 20px;
    background: #f8f9fa;
    border-top: 1px solid #ebeef5;

    .legend-item {
      display: flex;
      align-items: center;
      gap: 6px;
      font-size: 12px;
      color: #606266;

      .color-indicator {
        width: 12px;
        height: 12px;
        border-radius: 2px;

        &.hot {
          background: #ff4757;
        }

        &.warm {
          background: #ff7675;
        }

        &.neutral {
          background: #fdcb6e;
        }

        &.cool {
          background: #74b9ff;
        }

        &.cold {
          background: #0984e3;
        }
      }
    }
  }
}
</style>