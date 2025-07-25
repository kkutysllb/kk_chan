<template>
  <div class="dashboard">
    <!-- 顶部工具栏 -->
    <div class="dashboard-header">
      <div class="header-left">
        <h1>KK缠论量化分析平台</h1>
        <el-breadcrumb separator="/">
          <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
          <el-breadcrumb-item>控制台</el-breadcrumb-item>
        </el-breadcrumb>
      </div>
      
      <div class="header-right">
        <el-select
          v-model="selectedSymbol"
          filterable
          remote
          reserve-keyword
          placeholder="搜索股票代码/名称"
          :remote-method="searchStocks"
          :loading="searchLoading"
          @change="onSymbolChange"
          style="width: 240px;"
        >
          <el-option
            v-for="stock in stockOptions"
            :key="stock.symbol"
            :label="`${stock.name} (${stock.symbol})`"
            :value="stock.symbol"
          />
        </el-select>
        
        <el-button-group>
          <el-button @click="addToWatchlist" :disabled="!selectedSymbol">
            <el-icon><Star /></el-icon>
            加入自选
          </el-button>
          <el-button @click="refreshAll" :loading="globalLoading">
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
        </el-button-group>
      </div>
    </div>

    <!-- 主要内容区域 -->
    <div class="dashboard-content">
      <!-- 第一行：主图表 -->
      <div class="chart-row">
        <div class="main-chart-container">
          <ChanKLineChart
            v-if="selectedSymbol"
            :symbol="selectedSymbol"
            :height="600"
            :auto-refresh="true"
            :refresh-interval="30000"
          />
          <div v-else class="empty-chart">
            <el-empty description="请选择股票查看分析图表" />
          </div>
        </div>
      </div>

      <!-- 第二行：多时间周期分析 -->
      <div class="analysis-row" v-if="selectedSymbol">
        <el-card class="analysis-card">
          <template #header>
            <div class="card-header">
              <span>多时间周期分析</span>
              <el-button text @click="refreshMultiTimeframe">
                <el-icon><Refresh /></el-icon>
              </el-button>
            </div>
          </template>
          <MultiTimeframeAnalysis
            :symbol="selectedSymbol"
            :timeframes="['daily', '30min', '5min']"
          />
        </el-card>

        <el-card class="analysis-card">
          <template #header>
            <div class="card-header">
              <span>实时预测</span>
              <el-button text @click="refreshPrediction">
                <el-icon><Refresh /></el-icon>
              </el-button>
            </div>
          </template>
          <RealTimePrediction
            :symbol="selectedSymbol"
            :include-confidence="true"
          />
        </el-card>

        <el-card class="analysis-card">
          <template #header>
            <div class="card-header">
              <span>交易信号</span>
              <el-button text @click="refreshSignals">
                <el-icon><Refresh /></el-icon>
              </el-button>
            </div>
          </template>
          <TradingSignals
            :symbol="selectedSymbol"
            :timeframes="['daily', '30min']"
            :limit="10"
          />
        </el-card>
      </div>

      <!-- 第三行：市场概览 -->
      <div class="market-row">
        <el-card class="market-card">
          <template #header>
            <div class="card-header">
              <span>市场热力图</span>
              <el-button text @click="refreshHeatmap">
                <el-icon><Refresh /></el-icon>
              </el-button>
            </div>
          </template>
          <MarketHeatmap
            :market="'A股'"
            :auto-refresh="true"
            :refresh-interval="120000"
          />
        </el-card>
      </div>

      <!-- 第四行：自选股票 -->
      <div class="watchlist-row">
        <el-card class="watchlist-card">
          <template #header>
            <div class="card-header">
              <span>自选股票</span>
              <div class="header-actions">
                <el-button text @click="batchAnalyze" :loading="batchLoading">
                  <el-icon><DataAnalysis /></el-icon>
                  批量分析
                </el-button>
                <el-button text @click="refreshWatchlist">
                  <el-icon><Refresh /></el-icon>
                </el-button>
              </div>
            </div>
          </template>
          <WatchlistTable
            :watchlist="watchlist"
            @symbol-click="onWatchlistSymbolClick"
            @remove-symbol="removeFromWatchlist"
          />
        </el-card>
      </div>
    </div>

    <!-- 底部状态栏 -->
    <div class="dashboard-footer">
      <div class="footer-left">
        <el-tag size="small" type="success">
          数据库: {{ systemStatus.database }}
        </el-tag>
        <el-tag size="small" :type="systemStatus.ml_models === 'healthy' ? 'success' : 'warning'">
          ML模型: {{ systemStatus.ml_models }}
        </el-tag>
        <el-tag size="small" :type="systemStatus.cache === 'healthy' ? 'success' : 'info'">
          缓存: {{ systemStatus.cache }}
        </el-tag>
      </div>
      
      <div class="footer-right">
        <span class="status-text">
          最后更新: {{ lastUpdateTime }}
        </span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { useChanAnalysisStore } from '@/stores/chanAnalysis'
import { useMarketDataStore } from '@/stores/marketData'
import { useWatchlistStore } from '@/stores/watchlist'
import { apiService } from '@/services/api'

// 组件导入
import ChanKLineChart from '@/components/charts/ChanKLineChart.vue'
import MultiTimeframeAnalysis from '@/components/analysis/MultiTimeframeAnalysis.vue'
import RealTimePrediction from '@/components/analysis/RealTimePrediction.vue'
import TradingSignals from '@/components/analysis/TradingSignals.vue'
import MarketHeatmap from '@/components/charts/MarketHeatmap.vue'
import WatchlistTable from '@/components/watchlist/WatchlistTable.vue'

// Stores
const chanStore = useChanAnalysisStore()
const marketStore = useMarketDataStore()
const watchlistStore = useWatchlistStore()

// 响应式数据
const selectedSymbol = ref('')
const stockOptions = ref<any[]>([])
const searchLoading = ref(false)
const globalLoading = ref(false)
const batchLoading = ref(false)
const lastUpdateTime = ref('')

const systemStatus = reactive({
  database: 'healthy',
  ml_models: 'healthy',
  cache: 'healthy'
})

// 计算属性
const watchlist = computed(() => watchlistStore.getWatchlist)

// 方法
const searchStocks = async (query: string) => {
  if (!query || query.length < 2) {
    stockOptions.value = []
    return
  }

  searchLoading.value = true
  try {
    const response = await apiService.searchStocks(query)
    stockOptions.value = response.data || []
  } catch (error) {
    console.error('搜索股票失败:', error)
    stockOptions.value = []
  } finally {
    searchLoading.value = false
  }
}

const onSymbolChange = (symbol: string) => {
  if (symbol) {
    // 自动加载股票信息
    marketStore.updateRealTimeData(symbol)
    updateLastUpdateTime()
  }
}

const onWatchlistSymbolClick = (symbol: string) => {
  selectedSymbol.value = symbol
  onSymbolChange(symbol)
}

const addToWatchlist = () => {
  if (!selectedSymbol.value) return
  
  watchlistStore.addToWatchlist(selectedSymbol.value)
  ElMessage.success('已添加到自选股票')
}

const removeFromWatchlist = (symbol: string) => {
  watchlistStore.removeFromWatchlist(symbol)
  ElMessage.success('已从自选股票中移除')
}

const batchAnalyze = async () => {
  const symbols = watchlist.value.map(item => item.symbol)
  if (symbols.length === 0) {
    ElMessage.warning('自选股票为空')
    return
  }

  batchLoading.value = true
  try {
    await chanStore.batchAnalysis(symbols, ['daily'])
    ElMessage.success(`批量分析完成，共处理 ${symbols.length} 只股票`)
    updateLastUpdateTime()
  } catch (error) {
    console.error('批量分析失败:', error)
    ElMessage.error('批量分析失败')
  } finally {
    batchLoading.value = false
  }
}

const refreshAll = async () => {
  globalLoading.value = true
  try {
    const promises = []
    
    // 刷新当前股票数据
    if (selectedSymbol.value) {
      promises.push(
        chanStore.loadChanAnalysis(selectedSymbol.value, 'daily', true),
        marketStore.updateRealTimeData(selectedSymbol.value)
      )
    }
    
    // 刷新自选股票数据
    const watchlistSymbols = watchlist.value.map(item => item.symbol)
    if (watchlistSymbols.length > 0) {
      promises.push(
        marketStore.batchUpdateRealTimeData(watchlistSymbols)
      )
    }
    
    // 刷新系统状态
    promises.push(checkSystemStatus())
    
    await Promise.all(promises)
    updateLastUpdateTime()
    ElMessage.success('刷新完成')
  } catch (error) {
    console.error('刷新失败:', error)
    ElMessage.error('刷新失败')
  } finally {
    globalLoading.value = false
  }
}

const refreshMultiTimeframe = () => {
  if (selectedSymbol.value) {
    chanStore.loadMultiTimeframeAnalysis(selectedSymbol.value)
  }
}

const refreshPrediction = () => {
  if (selectedSymbol.value) {
    chanStore.loadRealTimePrediction(selectedSymbol.value)
  }
}

const refreshSignals = () => {
  if (selectedSymbol.value) {
    // 刷新交易信号
  }
}

const refreshHeatmap = () => {
  // 刷新热力图
}

const refreshWatchlist = async () => {
  const symbols = watchlist.value.map(item => item.symbol)
  if (symbols.length > 0) {
    await marketStore.batchUpdateRealTimeData(symbols)
    updateLastUpdateTime()
  }
}

const checkSystemStatus = async () => {
  try {
    const response = await apiService.healthCheck()
    systemStatus.database = response.services.database || 'unknown'
    systemStatus.ml_models = response.services.ml_models || 'unknown'
    systemStatus.cache = response.services.cache || 'unknown'
  } catch (error) {
    console.error('获取系统状态失败:', error)
    systemStatus.database = 'error'
    systemStatus.ml_models = 'error'
    systemStatus.cache = 'error'
  }
}

const updateLastUpdateTime = () => {
  lastUpdateTime.value = new Date().toLocaleTimeString()
}

// 生命周期
onMounted(async () => {
  // 加载初始数据
  await Promise.all([
    watchlistStore.loadWatchlist(),
    checkSystemStatus()
  ])
  
  updateLastUpdateTime()
  
  // 设置定时刷新
  setInterval(() => {
    checkSystemStatus()
  }, 60000) // 每分钟检查一次系统状态
  
  setInterval(() => {
    if (watchlist.value.length > 0) {
      const symbols = watchlist.value.map(item => item.symbol)
      marketStore.batchUpdateRealTimeData(symbols)
      updateLastUpdateTime()
    }
  }, 30000) // 每30秒更新自选股票数据
})
</script>

<style lang="scss" scoped>
.dashboard {
  min-height: 100vh;
  background: #f0f2f5;
  display: flex;
  flex-direction: column;

  .dashboard-header {
    background: #fff;
    padding: 16px 24px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    display: flex;
    justify-content: space-between;
    align-items: center;
    position: sticky;
    top: 0;
    z-index: 100;

    .header-left {
      h1 {
        margin: 0 0 4px 0;
        color: #303133;
        font-size: 24px;
        font-weight: 600;
      }
    }

    .header-right {
      display: flex;
      align-items: center;
      gap: 16px;
    }
  }

  .dashboard-content {
    flex: 1;
    padding: 24px;
    display: flex;
    flex-direction: column;
    gap: 24px;

    .chart-row {
      .main-chart-container {
        .empty-chart {
          background: #fff;
          border-radius: 8px;
          height: 600px;
          display: flex;
          align-items: center;
          justify-content: center;
        }
      }
    }

    .analysis-row {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
      gap: 24px;

      .analysis-card {
        border-radius: 8px;
        box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
      }
    }

    .market-row {
      .market-card {
        border-radius: 8px;
        box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
      }
    }

    .watchlist-row {
      .watchlist-card {
        border-radius: 8px;
        box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
      }
    }
  }

  .dashboard-footer {
    background: #fff;
    padding: 12px 24px;
    border-top: 1px solid #ebeef5;
    display: flex;
    justify-content: space-between;
    align-items: center;

    .footer-left {
      display: flex;
      gap: 12px;
    }

    .footer-right {
      .status-text {
        color: #909399;
        font-size: 12px;
      }
    }
  }
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;

  .header-actions {
    display: flex;
    gap: 8px;
  }
}
</style>