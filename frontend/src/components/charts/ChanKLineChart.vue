<template>
  <div class="chan-kline-chart">
    <div class="chart-header">
      <div class="stock-info">
        <span class="stock-symbol">{{ stockInfo.symbol }}</span>
        <span class="stock-name">{{ stockInfo.name }}</span>
        <span class="current-price" :class="priceChangeClass">
          ¥{{ stockInfo.currentPrice }}
        </span>
        <span class="price-change" :class="priceChangeClass">
          {{ stockInfo.priceChange >= 0 ? '+' : '' }}{{ stockInfo.priceChange }}
          ({{ stockInfo.priceChangePercent }}%)
        </span>
      </div>
      
      <div class="chart-controls">
        <el-radio-group v-model="currentTimeframe" @change="onTimeframeChange">
          <el-radio-button 
            v-for="tf in timeframes" 
            :key="tf.value" 
            :value="tf.value"
          >
            {{ tf.label }}
          </el-radio-button>
        </el-radio-group>
        
        <el-button-group class="ml-4">
          <el-button 
            :type="showChanStructure ? 'primary' : 'default'"
            @click="toggleChanStructure"
            size="small"
          >
            缠论结构
          </el-button>
          <el-button 
            :type="showTechnicalIndicators ? 'primary' : 'default'"
            @click="toggleTechnicalIndicators"
            size="small"
          >
            技术指标
          </el-button>
          <el-button 
            :type="showTradingSignals ? 'primary' : 'default'"
            @click="toggleTradingSignals"
            size="small"
          >
            交易信号
          </el-button>
        </el-button-group>
        
        <el-button @click="refreshData" :loading="loading" size="small">
          <el-icon><Refresh /></el-icon>
        </el-button>
      </div>
    </div>
    
    <div class="chart-container" ref="chartContainer">
      <v-chart
        ref="chartRef"
        :option="chartOption"
        :loading="loading"
        :autoresize="true"
        @click="onChartClick"
        @mouseover="onChartMouseOver"
        class="main-chart"
      />
    </div>
    
    <!-- 缠论结构详情面板 -->
    <el-drawer
      v-model="structureDrawerVisible"
      title="缠论结构详情"
      direction="rtl"
      size="400px"
    >
      <ChanStructureDetail
        v-if="selectedStructure"
        :structure="selectedStructure"
        :symbol="stockInfo.symbol"
        :timeframe="currentTimeframe"
      />
    </el-drawer>
    
    <!-- 交易信号详情面板 -->
    <el-drawer
      v-model="signalDrawerVisible"
      title="交易信号详情"
      direction="rtl"
      size="400px"
    >
      <TradingSignalDetail
        v-if="selectedSignal"
        :signal="selectedSignal"
        :symbol="stockInfo.symbol"
      />
    </el-drawer>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import { useResizeObserver } from '@vueuse/core'
import { useChanAnalysisStore } from '@/stores/chanAnalysis'
import { useMarketDataStore } from '@/stores/marketData'
import ChanStructureDetail from './ChanStructureDetail.vue'
import TradingSignalDetail from './TradingSignalDetail.vue'
import { generateKLineOption } from '@/utils/chartOptions'
import { formatPrice, formatPercent } from '@/utils/format'
import type { ChanStructure, TradingSignal } from '@/types/chan'

interface Props {
  symbol: string
  height?: string | number
  autoRefresh?: boolean
  refreshInterval?: number
}

const props = withDefaults(defineProps<Props>(), {
  height: '600px',
  autoRefresh: false,
  refreshInterval: 30000
})

// Stores
const chanStore = useChanAnalysisStore()
const marketStore = useMarketDataStore()

// 响应式数据
const chartRef = ref()
const chartContainer = ref()
const loading = ref(false)
const currentTimeframe = ref('daily')
const showChanStructure = ref(true)
const showTechnicalIndicators = ref(true)
const showTradingSignals = ref(true)
const structureDrawerVisible = ref(false)
const signalDrawerVisible = ref(false)
const selectedStructure = ref<ChanStructure | null>(null)
const selectedSignal = ref<TradingSignal | null>(null)

// 时间周期选项
const timeframes = [
  { label: '5分钟', value: '5min' },
  { label: '30分钟', value: '30min' },
  { label: '日线', value: 'daily' },
  { label: '周线', value: 'weekly' },
  { label: '月线', value: 'monthly' }
]

// 计算属性
const stockInfo = computed(() => ({
  symbol: props.symbol,
  name: marketStore.getStockName(props.symbol) || '获取中...',
  currentPrice: marketStore.getCurrentPrice(props.symbol),
  priceChange: marketStore.getPriceChange(props.symbol),
  priceChangePercent: marketStore.getPriceChangePercent(props.symbol)
}))

const priceChangeClass = computed(() => ({
  'price-up': stockInfo.value.priceChange > 0,
  'price-down': stockInfo.value.priceChange < 0,
  'price-flat': stockInfo.value.priceChange === 0
}))

const chartOption = computed(() => {
  const klineData = chanStore.getKLineData(props.symbol, currentTimeframe.value)
  const chanStructures = showChanStructure.value 
    ? chanStore.getChanStructures(props.symbol, currentTimeframe.value)
    : null
  const tradingSignals = showTradingSignals.value
    ? chanStore.getTradingSignals(props.symbol, currentTimeframe.value)
    : null
  const technicalIndicators = showTechnicalIndicators.value
    ? chanStore.getTechnicalIndicators(props.symbol, currentTimeframe.value)
    : null

  return generateKLineOption({
    klineData,
    chanStructures,
    tradingSignals,
    technicalIndicators,
    symbol: props.symbol,
    timeframe: currentTimeframe.value
  })
})

// 方法
const onTimeframeChange = async (timeframe: string) => {
  loading.value = true
  try {
    await loadChartData(timeframe)
  } finally {
    loading.value = false
  }
}

const toggleChanStructure = () => {
  showChanStructure.value = !showChanStructure.value
}

const toggleTechnicalIndicators = () => {
  showTechnicalIndicators.value = !showTechnicalIndicators.value
}

const toggleTradingSignals = () => {
  showTradingSignals.value = !showTradingSignals.value
}

const refreshData = async () => {
  loading.value = true
  try {
    await Promise.all([
      loadChartData(currentTimeframe.value, true),
      marketStore.updateRealTimeData(props.symbol)
    ])
  } finally {
    loading.value = false
  }
}

const loadChartData = async (timeframe: string, forceRefresh = false) => {
  try {
    // 加载K线数据
    await chanStore.loadKLineData(props.symbol, timeframe, forceRefresh)
    
    // 加载缠论分析数据
    await chanStore.loadChanAnalysis(props.symbol, timeframe, forceRefresh)
    
    // 加载技术指标数据
    await chanStore.loadTechnicalIndicators(props.symbol, timeframe, forceRefresh)
  } catch (error) {
    console.error('加载图表数据失败:', error)
    ElMessage.error('加载数据失败，请稍后重试')
  }
}

const onChartClick = (params: any) => {
  if (params.componentType === 'markPoint') {
    // 点击交易信号
    const signalId = params.data?.signalId
    if (signalId) {
      const signal = chanStore.getTradingSignalById(signalId)
      if (signal) {
        selectedSignal.value = signal
        signalDrawerVisible.value = true
      }
    }
  } else if (params.componentType === 'markLine') {
    // 点击缠论结构
    const structureId = params.data?.structureId
    if (structureId) {
      const structure = chanStore.getChanStructureById(structureId)
      if (structure) {
        selectedStructure.value = structure
        structureDrawerVisible.value = true
      }
    }
  }
}

const onChartMouseOver = (params: any) => {
  // 鼠标悬停事件处理
  if (params.componentType === 'series') {
    // 显示详细信息tooltip
  }
}

// 生命周期
onMounted(async () => {
  loading.value = true
  try {
    // 加载股票基本信息
    await marketStore.loadStockInfo(props.symbol)
    await loadChartData(currentTimeframe.value)
    await marketStore.updateRealTimeData(props.symbol)
  } catch (error) {
    console.error('加载股票信息失败:', error)
  } finally {
    loading.value = false
  }
  
  // 自动刷新
  if (props.autoRefresh) {
    setInterval(() => {
      if (!loading.value) {
        refreshData()
      }
    }, props.refreshInterval)
  }
})

// 监听容器大小变化
useResizeObserver(chartContainer, () => {
  nextTick(() => {
    chartRef.value?.resize()
  })
})

// 监听symbol变化
watch(
  () => props.symbol,
  async (newSymbol) => {
    if (newSymbol) {
      loading.value = true
      try {
        await loadChartData(currentTimeframe.value)
        await marketStore.updateRealTimeData(newSymbol)
      } finally {
        loading.value = false
      }
    }
  }
)
</script>

<style lang="scss" scoped>
.chan-kline-chart {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  overflow: hidden;

  .chart-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 16px 20px;
    border-bottom: 1px solid #ebeef5;
    background: #fafafa;

    .stock-info {
      display: flex;
      align-items: center;
      gap: 12px;

      .stock-symbol {
        font-size: 18px;
        font-weight: 600;
        color: #303133;
      }

      .stock-name {
        font-size: 14px;
        color: #606266;
      }

      .current-price {
        font-size: 20px;
        font-weight: 600;
        
        &.price-up {
          color: #f56c6c;
        }
        
        &.price-down {
          color: #67c23a;
        }
        
        &.price-flat {
          color: #909399;
        }
      }

      .price-change {
        font-size: 14px;
        
        &.price-up {
          color: #f56c6c;
        }
        
        &.price-down {
          color: #67c23a;
        }
        
        &.price-flat {
          color: #909399;
        }
      }
    }

    .chart-controls {
      display: flex;
      align-items: center;
      gap: 12px;
    }
  }

  .chart-container {
    position: relative;
    height: v-bind(height);
    
    .main-chart {
      width: 100%;
      height: 100%;
    }
  }
}

.ml-4 {
  margin-left: 16px;
}
</style>