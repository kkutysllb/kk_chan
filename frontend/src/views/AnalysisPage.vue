<template>
  <div class="stock-analysis-page">
    <div class="page-header">
      <h1 class="page-title">
        <el-icon><TrendCharts /></el-icon>
        缠论智能分析
      </h1>
      <p class="page-subtitle">基于缠中说禅理论的专业股票技术分析平台：多周期联合分析 + 智能买卖点识别</p>
    </div>

    <div class="page-content">
      <!-- 股票选择面板 -->
      <el-card class="config-panel" shadow="hover">
        <template #header>
          <div class="card-header">
            <div class="card-title">
              <el-icon class="card-icon"><TrendCharts /></el-icon>
              <span>股票选择</span>
            </div>
            <el-button 
              type="primary" 
              :loading="analyzing"
              @click="startAnalysis"
            >
              {{ analyzing ? '分析中...' : '开始分析' }}
            </el-button>
          </div>
        </template>

        <div class="config-content">
          <StockSelector />
        </div>
      </el-card>

      <!-- 分析结果面板 -->
      <el-card class="results-panel" shadow="hover">
        <template #header>
          <div class="card-header">
            <div class="card-title">
              <el-icon class="card-icon"><DataAnalysis /></el-icon>
              <span>分析结果</span>
            </div>
            <div class="tab-buttons">
              <el-button-group>
                <el-button 
                  v-for="tab in tabs" 
                  :key="tab.name"
                  :type="activeTab === tab.name ? 'primary' : 'default'"
                  size="small"
                  @click="activeTab = tab.name"
                >
                  <el-icon><component :is="tab.icon" /></el-icon>
                  {{ tab.label }}
                </el-button>
              </el-button-group>
            </div>
          </div>
        </template>

        <div class="results-content">
          <transition name="fade" mode="out-in">
            <component :is="currentComponent" :key="activeTab" />
          </transition>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useGlobalStore } from '@/stores/global'
import { TrendCharts, DataAnalysis, Bell, Document } from '@element-plus/icons-vue'
import StockSelector from '@/components/StockSelector.vue'
import ChanChart from '@/components/ChanChart.vue'
import DataDetail from '@/components/DataDetail.vue'
import TradingSignals from '@/components/TradingSignals.vue'
import AnalysisReport from '@/components/AnalysisReport.vue'

const route = useRoute()
const global = useGlobalStore()
const activeTab = ref('chart')
const analyzing = ref(false)

// 标签配置  
const tabs = ref([
  { name: 'chart', label: '图表分析', icon: 'TrendCharts' },
  { name: 'data', label: '数据详情', icon: 'DataAnalysis' },
  { name: 'signals', label: '交易信号', icon: 'Bell' },
  { name: 'report', label: '分析报告', icon: 'Document' }
])

// 当前组件
const currentComponent = computed(() => {
  const componentMap = {
    chart: ChanChart,
    data: DataDetail,
    signals: TradingSignals,
    report: AnalysisReport
  }
  return componentMap[activeTab.value]
})

// 开始分析
const startAnalysis = async () => {
  const currentStock = global.currentStock?.symbol
  if (!currentStock) {
    ElMessage.warning('请先选择股票')
    return
  }

  analyzing.value = true
  try {
    console.log('开始缠论分析:', currentStock)
    
    // 根据分析模式选择合适的API
    const analysisMode = global.analysisMode || 'multi-level'
    console.log('分析模式:', analysisMode)
    
    await global.fetchAnalysisData({
      symbol: currentStock,
      analysisMode: analysisMode,
      timeframe: global.currentTimeframe || '30min',
      levels: global.levels || ['daily', '30min', '5min'],
      days: global.currentDays || 90
    })
    
    ElMessage.success('分析完成')
    
  } catch (error) {
    console.error('分析失败:', error)
    ElMessage.error(`分析失败: ${error.message || '网络错误'}`)
  } finally {
    analyzing.value = false
  }
}

// 处理路由参数
onMounted(() => {
  console.log('AnalysisPage loaded')
  
  // 检查URL查询参数中是否有股票代码
  const symbol = route.query.symbol
  if (symbol) {
    console.log('从URL参数获取股票代码:', symbol)
    global.setCurrentStock({ symbol })
  }
})
</script>

<style scoped>
.stock-analysis-page {
  min-height: 100vh;
  background: var(--el-bg-color);
  padding: 0;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.page-header {
  text-align: center;
  padding: var(--space-xl) var(--space-xl) 0;
  margin-bottom: var(--space-2xl);
}

.page-title {
  font-size: 2.5rem;
  font-weight: 800;
  background: linear-gradient(135deg, #64b5f6 0%, #2196f3 50%, #1976d2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin: 0 0 var(--space-md) 0;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-md);
  letter-spacing: -0.02em;
}

:root:not(.dark) .page-title {
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

:root.dark .page-title {
  text-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
}

.page-title .el-icon {
  color: #64b5f6;
  font-size: 2.2rem;
}

:root:not(.dark) .page-title .el-icon {
  filter: drop-shadow(0 1px 2px rgba(100, 181, 246, 0.2));
}

:root.dark .page-title .el-icon {
  filter: drop-shadow(0 2px 4px rgba(100, 181, 246, 0.3));
}

.page-subtitle {
  font-size: 1.125rem;
  margin: 0;
  font-weight: 500;
}

:root:not(.dark) .page-subtitle {
  color: #f57c00;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

:root.dark .page-subtitle {
  color: #ffa726;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2), 0 0 10px rgba(255, 167, 38, 0.3);
}

.page-content {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 0;
}

.config-panel,
.results-panel {
  background: var(--el-bg-color);
  border: none;
  border-radius: 0;
  border-bottom: 1px solid var(--el-border-color-light);
  box-shadow: none;
  margin: 0;
  padding: var(--space-xl);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.results-panel {
  border-bottom: none;
}

.config-panel:hover,
.results-panel:hover {
  transform: none;
  background: var(--el-bg-color-page);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin: 0;
}

.card-title {
  font-size: 1.25rem;
  font-weight: 700;
  color: #64b5f6;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex: 0 0 auto; /* 不拉伸，保持原始大小 */
}

.card-icon {
  color: #64b5f6;
  font-size: 1.3rem;
}

.config-content {
  padding: var(--space-lg) 0 0;
}

.results-content {
  min-height: 600px;
  padding: var(--space-lg) 0 0;
}

.tab-buttons {
  display: flex;
  gap: var(--space-sm);
}

.tab-buttons .el-button-group {
  box-shadow: var(--shadow-md);
  border-radius: var(--radius-lg);
  overflow: hidden;
}

.tab-buttons .el-button {
  border: none;
  font-weight: 600;
  transition: all 0.3s ease;
}

.tab-buttons .el-button:not(.el-button--primary) {
  background: var(--bg-tertiary);
  color: var(--text-secondary);
}

.tab-buttons .el-button:not(.el-button--primary):hover {
  background: var(--bg-secondary);
  color: var(--text-primary);
  transform: translateY(-2px);
}

/* 过渡动画 */
.fade-enter-active,
.fade-leave-active {
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.fade-enter-from {
  opacity: 0;
  transform: translateY(30px) scale(0.95);
}

.fade-leave-to {
  opacity: 0;
  transform: translateY(-30px) scale(0.95);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .stock-analysis-page {
    padding: var(--space-md);
  }
  
  .page-title {
    font-size: 2rem;
    flex-direction: column;
    gap: var(--space-sm);
  }
  
  .page-subtitle {
    font-size: 1rem;
  }
  
  .card-header {
    flex-direction: column;
    align-items: flex-start;
    gap: var(--space-md);
  }
  
  .tab-buttons .el-button span:not(.el-icon) {
    display: none;
  }
  
  .results-content {
    min-height: 400px;
  }
}

@media (max-width: 480px) {
  .page-title {
    font-size: 1.75rem;
  }
  
  .card-header {
    gap: var(--space-sm);
  }
  
  .tab-buttons .el-button {
    padding: var(--space-sm);
    min-width: auto;
  }
}
</style>