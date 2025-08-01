<template>
  <div class="stock-selector">
    <!-- 标题区域 -->
    <div class="selector-header">
      <div class="header-title">
        <span class="title-icon">🎯</span>
        <span class="title-text">分析配置</span>
      </div>
      <el-button
        type="primary"
        @click="handleAnalyze"
        :loading="analyzing"
        :disabled="!form.symbol"
        class="analyze-button"
      >
        <span v-if="!analyzing">开始分析</span>
        <span v-else>分析中...</span>
      </el-button>
    </div>

    <!-- 配置区域 -->
    <div class="config-sections">
      <!-- 股票选择卡片 -->
      <el-card class="config-card stock-card" shadow="hover">
        <template #header>
          <div class="card-title">
            <el-icon class="title-icon"><TrendCharts /></el-icon>
            <span>股票选择</span>
          </div>
        </template>
        
        <el-form ref="formRef" :model="form" :rules="rules" class="config-form">
          <el-form-item prop="symbol">
            <el-select
              v-model="form.symbol"
              placeholder="搜索股票代码或名称"
              filterable
              remote
              reserve-keyword
              :remote-method="searchStocks"
              :loading="searchLoading"
              class="stock-select"
              @change="handleSymbolChange"
              size="large"
            >
              <el-option
                v-for="stock in stockOptions"
                :key="stock.value"
                :label="stock.label"
                :value="stock.value"
              >
                <div class="stock-option">
                  <span class="stock-code">{{ stock.value }}</span>
                  <span class="stock-name">{{ stock.name }}</span>
                </div>
              </el-option>
            </el-select>
          </el-form-item>
        </el-form>
      </el-card>

      <!-- 时间配置卡片 -->
      <el-card class="config-card time-card" shadow="hover">
        <template #header>
          <div class="card-title">
            <el-icon class="title-icon"><Clock /></el-icon>
            <span>时间设置</span>
          </div>
        </template>
        
        <div class="time-config">
          <div class="config-group">
            <label class="config-label">时间级别</label>
            <el-radio-group 
              v-model="form.timeframe" 
              @change="handleTimeframeChange"
              class="timeframe-group"
            >
              <el-radio-button value="5min">5分钟</el-radio-button>
              <el-radio-button value="30min">30分钟</el-radio-button>
              <el-radio-button value="daily">日线</el-radio-button>
            </el-radio-group>
          </div>

          <div class="config-group">
            <label class="config-label">分析周期</label>
            <div class="period-config">
              <el-slider
                v-model="form.days"
                :min="timeframeLimits.min"
                :max="timeframeLimits.max"
                :step="timeframeLimits.step"
                :format-tooltip="formatDaysTooltip"
                show-input
                class="period-slider"
                @change="handleDaysChange"
              />
              <div class="period-hint">
                建议：{{ timeframeLimits.min }}-{{ timeframeLimits.max }}天
              </div>
            </div>
          </div>
        </div>
      </el-card>

      <!-- 高级参数卡片 -->
      <el-card class="config-card advanced-card" shadow="hover">
        <template #header>
          <div class="card-title">
            <el-icon class="title-icon"><Setting /></el-icon>
            <span>高级参数</span>
            <el-switch
              v-model="advancedEnabled"
              size="small"
              style="margin-left: auto;"
            />
          </div>
        </template>
        
        <div v-show="advancedEnabled" class="advanced-params">
          <div class="param-group">
            <label class="param-label">最小笔长度</label>
            <el-input-number
              v-model="form.advanced.minBiLength"
              :min="3"
              :max="20"
              :step="1"
              size="small"
              controls-position="right"
            />
            <div class="param-desc">控制笔的识别敏感度</div>
          </div>

          <div class="param-group">
            <label class="param-label">最小线段笔数</label>
            <el-input-number
              v-model="form.advanced.minXdBiCount"
              :min="2"
              :max="10"
              :step="1"
              size="small"
              controls-position="right"
            />
            <div class="param-desc">构成线段需要的最少笔数</div>
          </div>

          <div class="param-group">
            <label class="param-label">分型强度阈值</label>
            <el-input-number
              v-model="form.advanced.fenxingThreshold"
              :min="0.0001"
              :max="0.01"
              :step="0.0001"
              :precision="4"
              size="small"
              controls-position="right"
            />
            <div class="param-desc">分型识别的价格波动阈值</div>
          </div>
        </div>
      </el-card>
    </div>

    <!-- 分析状态 -->
    <div v-if="analysisStatus" class="analysis-status">
      <el-alert
        :title="analysisStatus.title"
        :type="analysisStatus.type"
        :description="analysisStatus.description"
        show-icon
        :closable="false"
        class="status-alert"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, watch, onMounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { TrendCharts, Clock, Setting } from '@element-plus/icons-vue'
import { useGlobalStore } from '@/stores/global'
import { pythonApi } from '@/utils/api'

const global = useGlobalStore()

// 表单数据
const form = reactive({
  symbol: '',
  timeframe: 'daily',
  days: 90,
  advanced: {
    minBiLength: 5,
    minXdBiCount: 3,
    fenxingThreshold: 0.001,
  },
})

// 表单验证规则
const rules = {
  symbol: [
    { required: true, message: '请选择股票代码', trigger: 'change' },
  ],
  timeframe: [
    { required: true, message: '请选择时间级别', trigger: 'change' },
  ],
  days: [
    { required: true, message: '请设置分析天数', trigger: 'change' },
    { type: 'number', min: 7, max: 365, message: '分析天数应在7-365天之间', trigger: 'change' },
  ],
}

// 组件状态
const formRef = ref()
const analyzing = ref(false)
const searchLoading = ref(false)
const stockOptions = ref([])
const advancedEnabled = ref(false)
const analysisStatus = ref(null)

// 计算不同时间级别的天数限制
const timeframeLimits = computed(() => {
  const limits = {
    '5min': { min: 1, max: 30, step: 1 },
    '30min': { min: 7, max: 90, step: 7 },
    'daily': { min: 30, max: 365, step: 30 },
  }
  return limits[form.timeframe] || limits['daily']
})

// 搜索股票
const searchStocks = async (query) => {
  if (!query || query.length < 1) {
    stockOptions.value = []
    return
  }
  
  searchLoading.value = true
  try {
    // 直接调用后端API进行搜索，避免前端过滤
    const stocks = await pythonApi.getStockList(query)
    
    // 限制显示前50个结果
    stockOptions.value = stocks.slice(0, 50)
    
  } catch (error) {
    console.error('搜索股票失败:', error)
    ElMessage.error('获取股票列表失败')
    stockOptions.value = []
  } finally {
    searchLoading.value = false
  }
}

// 格式化天数提示
const formatDaysTooltip = (value) => {
  return `${value}天`
}

// 处理股票变化
const handleSymbolChange = (symbol) => {
  console.log('股票代码变化:', symbol)
  global.setCurrentStock({ symbol })
}

// 处理时间级别变化
const handleTimeframeChange = (timeframe) => {
  console.log('时间级别变化:', timeframe)
  
  // 调整天数到合适范围
  const limits = timeframeLimits.value
  if (form.days < limits.min) {
    form.days = limits.min
  } else if (form.days > limits.max) {
    form.days = limits.max
  }
  
  global.setCurrentStock({ timeframe })
}

// 处理天数变化
const handleDaysChange = (days) => {
  console.log('分析天数变化:', days)
  global.setCurrentStock({ days })
}

// 开始分析
const handleAnalyze = async () => {
  try {
    await formRef.value.validate()
    
    analyzing.value = true
    analysisStatus.value = {
      title: '正在分析...',
      type: 'info',
      description: `正在分析 ${form.symbol} ${form.timeframe} 级别数据...`,
    }
    
    // 执行分析
    await global.fetchAnalysisData({
      symbol: form.symbol,
      timeframe: form.timeframe,
      days: form.days,
      ...form.advanced,
    })
    
    analysisStatus.value = {
      title: '分析完成',
      type: 'success',
      description: '缠论分析已完成，请查看图表结果',
    }
    
    ElMessage.success('分析完成')
    
    // 3秒后清除状态
    setTimeout(() => {
      analysisStatus.value = null
    }, 3000)
    
  } catch (error) {
    console.error('分析失败:', error)
    analysisStatus.value = {
      title: '分析失败',
      type: 'error',
      description: error.message || '分析过程中出现错误',
    }
    ElMessage.error('分析失败')
  } finally {
    analyzing.value = false
  }
}

// 自动分析 - 当股票或参数改变时
watch([() => form.symbol, () => form.timeframe], async ([newSymbol, newTimeframe]) => {
  if (newSymbol && newTimeframe) {
    console.log('检测到股票或时间级别变化，自动开始分析...')
    await handleAnalyze()
  }
}, { immediate: false })

// 监听全局状态变化
watch(() => global.currentStock, (newStock) => {
  if (newStock.symbol !== form.symbol) {
    form.symbol = newStock.symbol
  }
  if (newStock.timeframe !== form.timeframe) {
    form.timeframe = newStock.timeframe
  }
  if (newStock.days !== form.days) {
    form.days = newStock.days
  }
}, { immediate: true })

// 初始化
onMounted(async () => {
  // 从全局状态恢复表单
  const currentStock = global.currentStock
  if (currentStock.symbol) {
    form.symbol = currentStock.symbol
  }
  form.timeframe = currentStock.timeframe
  form.days = currentStock.days
  
  // 如果有股票代码，初始化搜索选项
  if (form.symbol) {
    await searchStocks(form.symbol)
    console.log('组件初始化完成，自动开始分析...')
    await nextTick() // 等待DOM更新
    handleAnalyze()
  }
})
</script>

<style scoped>
.stock-selector {
  display: flex;
  flex-direction: column;
  padding: 0;
  min-height: 0;
}

/* 标题区域 */
.selector-header {
  padding: 20px 24px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 16px 16px 0 0;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 4px 20px rgba(102, 126, 234, 0.3);
}

.header-title {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 18px;
  font-weight: 600;
}

.header-title .title-icon {
  font-size: 24px;
}

.analyze-button {
  background: rgba(255, 255, 255, 0.2) !important;
  border: 2px solid rgba(255, 255, 255, 0.3) !important;
  color: white !important;
  backdrop-filter: blur(10px);
  border-radius: 12px !important;
  padding: 8px 20px !important;
  font-weight: 600;
  transition: all 0.3s ease;
}

.analyze-button:hover {
  background: rgba(255, 255, 255, 0.3) !important;
  border-color: rgba(255, 255, 255, 0.5) !important;
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.2);
}

/* 配置区域 */
.config-sections {
  padding: 24px;
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 24px;
  background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
}

.dark .config-sections {
  background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
}

/* 配置卡片 */
.config-card {
  border: none !important;
  border-radius: 16px !important;
  overflow: hidden;
  transition: all 0.3s ease;
  background: rgba(255, 255, 255, 0.95) !important;
  backdrop-filter: blur(20px);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.08) !important;
  position: relative;
  z-index: 1;
}

.dark .config-card {
  background: rgba(30, 41, 59, 0.95) !important;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3) !important;
}

.config-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.12) !important;
  z-index: 10;
}

.dark .config-card:hover {
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.4) !important;
}

/* 卡片标题 */
.card-title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 16px;
  font-weight: 600;
  color: var(--el-text-color-primary);
}

.card-title .title-icon {
  font-size: 18px;
  color: #667eea;
}

/* 股票选择卡片 */
.stock-card {
  border-left: 4px solid #10b981 !important;
}

.stock-select {
  width: 100%;
}

:deep(.stock-select .el-input__wrapper) {
  height: 48px;
  border-radius: 12px;
  border: 2px solid var(--el-border-color-light);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
}

:deep(.stock-select .el-input__wrapper:hover) {
  border-color: #10b981;
  box-shadow: 0 4px 20px rgba(16, 185, 129, 0.15);
}

:deep(.stock-select .el-input__wrapper.is-focus) {
  border-color: #10b981;
  box-shadow: 0 4px 20px rgba(16, 185, 129, 0.25);
}

.stock-option {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.stock-code {
  font-weight: 600;
  color: var(--el-text-color-primary);
}

.stock-name {
  color: var(--el-text-color-secondary);
  font-size: 12px;
}

/* 时间配置卡片 */
.time-card {
  border-left: 4px solid #3b82f6 !important;
}

.time-config {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.config-group {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.config-label {
  font-size: 14px;
  font-weight: 600;
  color: var(--el-text-color-primary);
  margin-bottom: 8px;
}

.timeframe-group {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

:deep(.timeframe-group .el-radio-button__inner) {
  padding: 12px 20px;
  border-radius: 10px;
  font-weight: 500;
  transition: all 0.3s ease;
  border: 2px solid var(--el-border-color-light);
  background: var(--el-bg-color);
  min-width: 80px;
  text-align: center;
}

:deep(.timeframe-group .el-radio-button__original-radio:checked + .el-radio-button__inner) {
  background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
  border-color: transparent;
  color: white;
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
}

:deep(.timeframe-group .el-radio-button__inner:hover) {
  border-color: #3b82f6;
  transform: translateY(-2px);
}

.period-config {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.period-slider {
  width: 100%;
}

:deep(.period-slider .el-slider__runway) {
  background: linear-gradient(135deg, #e2e8f0 0%, #cbd5e1 100%);
  height: 10px;
  border-radius: 5px;
}

:deep(.period-slider .el-slider__bar) {
  background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
  border-radius: 5px;
}

:deep(.period-slider .el-slider__button) {
  width: 22px;
  height: 22px;
  border: 3px solid #3b82f6;
  background: white;
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
  transition: all 0.3s ease;
}

:deep(.period-slider .el-slider__button:hover) {
  transform: scale(1.2);
  box-shadow: 0 6px 20px rgba(59, 130, 246, 0.4);
}

.period-hint {
  font-size: 12px;
  color: var(--el-text-color-secondary);
  text-align: center;
  padding: 8px 16px;
  background: var(--el-fill-color-extra-light);
  border-radius: 8px;
  border: 1px solid var(--el-border-color-lighter);
}

/* 高级参数卡片 */
.advanced-card {
  border-left: 4px solid #f59e0b !important;
}

.advanced-params {
  display: flex;
  flex-direction: column;
  gap: 20px;
  margin-top: 16px;
  padding: 16px;
  background: var(--el-fill-color-extra-light);
  border-radius: 12px;
  border: 1px dashed var(--el-border-color);
}

.param-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.param-label {
  font-size: 13px;
  font-weight: 600;
  color: var(--el-text-color-primary);
}

.param-desc {
  font-size: 11px;
  color: var(--el-text-color-secondary);
  font-style: italic;
  margin-top: 4px;
}

:deep(.advanced-params .el-input-number) {
  width: 100%;
}

:deep(.advanced-params .el-input-number .el-input__wrapper) {
  border-radius: 8px;
  border: 1px solid var(--el-border-color-light);
  transition: all 0.3s ease;
}

:deep(.advanced-params .el-input-number .el-input__wrapper:hover) {
  border-color: #f59e0b;
}

:deep(.advanced-params .el-input-number .el-input__wrapper.is-focus) {
  border-color: #f59e0b;
  box-shadow: 0 0 0 2px rgba(245, 158, 11, 0.1);
}

/* 分析状态 */
.analysis-status {
  margin: 20px 24px;
  border-radius: 12px;
  overflow: hidden;
  animation: slideInUp 0.5s ease;
}

.status-alert {
  border: none !important;
  border-radius: 12px !important;
}

@keyframes slideInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .selector-header {
    padding: 16px 20px;
    flex-direction: column;
    gap: 12px;
    text-align: center;
  }
  
  .config-sections {
    padding: 16px;
    gap: 16px;
  }
  
  .timeframe-group {
    flex-direction: column;
  }
  
  :deep(.timeframe-group .el-radio-button__inner) {
    width: 100%;
  }
}

/* 滚动条样式 */
.config-sections::-webkit-scrollbar {
  width: 6px;
}

.config-sections::-webkit-scrollbar-track {
  background: var(--el-fill-color-lighter);
  border-radius: 3px;
}

.config-sections::-webkit-scrollbar-thumb {
  background: var(--el-border-color-dark);
  border-radius: 3px;
}

.config-sections::-webkit-scrollbar-thumb:hover {
  background: var(--el-color-primary);
}
</style>