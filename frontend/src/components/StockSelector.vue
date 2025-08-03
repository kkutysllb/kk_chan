<template>
  <div class="stock-selector">
    <!-- 配置区域 - 重新布局 -->
    <div class="config-container">
      <!-- 上半部分：股票选择（全宽） -->
      <div class="stock-selection-section">
        <el-form ref="formRef" :model="form" :rules="rules" class="stock-form">
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
      </div>

      <!-- 下半部分：左右分栏布局 -->
      <div class="config-sections">
        <!-- 左侧：时间设置 -->
        <div class="time-section">
          <div class="section-header">
            <el-icon class="section-icon"><Clock /></el-icon>
            <span class="section-title">时间设置</span>
          </div>
          
          <div class="time-config">
            <div class="config-row">
              <label class="config-label">分析模式</label>
              <el-radio-group 
                v-model="form.analysisMode" 
                @change="handleAnalysisModeChange"
                class="timeframe-group"
                size="small"
              >
                <el-radio-button value="multi-level">多级别分析</el-radio-button>
                <el-radio-button value="single-level">单级别分析</el-radio-button>
              </el-radio-group>
            </div>
            
            <div v-if="form.analysisMode === 'single-level'" class="config-row">
              <label class="config-label">时间级别</label>
              <el-radio-group 
                v-model="form.timeframe" 
                @change="handleTimeframeChange"
                class="timeframe-group"
                size="small"
              >
                <el-radio-button value="5min">5分</el-radio-button>
                <el-radio-button value="30min">30分</el-radio-button>
                <el-radio-button value="daily">日线</el-radio-button>
              </el-radio-group>
            </div>
            
            <div v-if="form.analysisMode === 'multi-level'" class="config-row">
              <label class="config-label">分析级别</label>
              <el-checkbox-group v-model="form.levels" size="small" class="levels-group">
                <el-checkbox value="daily" disabled>日线</el-checkbox>
                <el-checkbox value="30min" disabled>30分钟</el-checkbox>
                <el-checkbox value="5min" disabled>5分钟</el-checkbox>
              </el-checkbox-group>
              <div class="levels-note">默认分析所有级别</div>
            </div>

            <div class="config-row">
              <label class="config-label">分析周期</label>
              <div class="period-config">
                <el-input-number
                  v-model="form.days"
                  :min="timeframeLimits.min"
                  :max="timeframeLimits.max"
                  :step="timeframeLimits.step"
                  size="small"
                  controls-position="right"
                  class="period-input"
                />
                <span class="period-unit">天</span>
              </div>
            </div>
          </div>
        </div>

        <!-- 右侧：高级参数 -->
        <div class="advanced-section">
          <div class="section-header">
            <el-icon class="section-icon"><Setting /></el-icon>
            <span class="section-title">高级参数</span>
            <el-switch
              v-model="advancedEnabled"
              size="small"
              class="advanced-toggle"
            />
          </div>
          
          <div v-if="advancedEnabled" class="advanced-config">
            <div class="config-row">
              <label class="config-label">买卖点识别</label>
              <el-switch v-model="form.enableBuySellPoints" size="small" />
            </div>

            <div class="config-row">
              <label class="config-label">背驰分析</label>
              <el-switch v-model="form.enableBackchiAnalysis" size="small" />
            </div>

            <div v-if="form.analysisMode === 'multi-level'" class="config-row">
              <label class="config-label">多级别确认</label>
              <el-switch v-model="form.enableMultiLevelConfirmation" size="small" />
            </div>
            
            <div class="config-row">
              <label class="config-label">缠论结构分析</label>
              <el-switch v-model="form.enableStructureAnalysis" size="small" />
            </div>
          </div>
          
          <div v-else class="advanced-disabled">
            <span class="disabled-text">开启高级参数以配置分析选项</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, watch, onMounted } from 'vue'
import { useGlobalStore } from '@/stores/global'
import { TrendCharts, Clock, Setting } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const global = useGlobalStore()

// 表单数据
const form = reactive({
  symbol: '',
  analysisMode: 'multi-level', // 新增：分析模式
  timeframe: '30min', // 单级别模式使用
  levels: ['daily', '30min', '5min'], // 多级别模式使用
  days: 90,
  enableBuySellPoints: true, // 是否启用买卖点识别
  enableBackchiAnalysis: true, // 是否启用背驰分析
  enableMultiLevelConfirmation: true, // 是否启用多级别确认
  enableStructureAnalysis: true // 是否启用缠论结构分析
})

// 状态管理
const analyzing = ref(false)
const searchLoading = ref(false)
const stockOptions = ref([])
const advancedEnabled = ref(false)
const formRef = ref()

// 表单验证规则
const rules = {
  symbol: [
    { required: true, message: '请选择股票', trigger: 'change' }
  ]
}

// 时间级别限制
const timeframeLimits = computed(() => {
  const limits = {
    '5min': { min: 7, max: 30, step: 1 },
    '30min': { min: 30, max: 180, step: 10 },
    'daily': { min: 90, max: 1000, step: 30 }
  }
  return limits[form.timeframe] || limits['30min']
})

// 搜索股票
const searchStocks = async (query) => {
  if (!query || query.length < 2) {
    stockOptions.value = []
    return
  }
  
  searchLoading.value = true
  try {
    const { stockApi } = await import('@/utils/api')
    const response = await stockApi.searchStocks(query)
    
    // 后端已经返回正确格式，直接使用
    const stocks = response || []
    
    stockOptions.value = stocks
  } catch (error) {
    console.error('搜索股票失败:', error)
    ElMessage.error(`搜索股票失败: ${error.message || '网络错误'}`)
    stockOptions.value = []
  } finally {
    searchLoading.value = false
  }
}

// 处理股票选择变化
const handleSymbolChange = (value) => {
  console.log('股票选择变化:', value)
  global.setCurrentStock({ symbol: value })
}

// 处理分析模式变化
const handleAnalysisModeChange = (value) => {
  console.log('分析模式变化:', value)
  // 根据分析模式更新全局状态
  global.setCurrentStock({ 
    symbol: form.symbol,
    analysisMode: value,
    timeframe: value === 'single-level' ? form.timeframe : undefined,
    levels: value === 'multi-level' ? form.levels : undefined,
    days: form.days
  })
}

// 处理时间级别变化
const handleTimeframeChange = (value) => {
  console.log('时间级别变化:', value)
  // 根据时间级别调整周期范围
  const limits = timeframeLimits.value
  if (form.days < limits.min || form.days > limits.max) {
    form.days = Math.min(Math.max(form.days, limits.min), limits.max)
  }
}

// 处理分析
const handleAnalyze = async () => {
  if (!form.symbol) {
    ElMessage.warning('请先选择股票')
    return
  }
  
  analyzing.value = true
  try {
    console.log('开始分析:', form)
    // 这里调用分析API
    await new Promise(resolve => setTimeout(resolve, 2000))
    ElMessage.success('分析完成')
  } catch (error) {
    console.error('分析失败:', error)
    ElMessage.error('分析失败')
  } finally {
    analyzing.value = false
  }
}

// 格式化提示
const formatDaysTooltip = (val) => {
  return `${val}天`
}

// 监听表单变化
watch(() => form.timeframe, (newVal) => {
  console.log('时间级别变化:', newVal)
})

watch(() => form.days, (newVal) => {
  console.log('分析周期变化:', newVal)
})

// 初始化
onMounted(() => {
  console.log('StockSelector 组件已加载')
})

// 暴露方法给父组件
defineExpose({
  handleAnalyze,
  form
})
</script>

<style scoped>
.stock-selector {
  width: 100%;
}

.config-container {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

/* 股票选择区域 */
.stock-selection-section {
  width: 100%;
}

/* 深色主题 */
:root.dark .section-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 1rem;
  padding-bottom: 0.5rem;
  border-bottom: 2px solid rgba(255, 255, 255, 0.2);
}

:root.dark .section-icon {
  font-size: 1.1rem;
  color: #64b5f6;
}

:root.dark .section-title {
  font-size: 1rem;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.9);
}

/* 浅色主题 */
:root:not(.dark) .section-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 1rem;
  padding-bottom: 0.5rem;
  border-bottom: 2px solid rgba(0, 0, 0, 0.15);
}

:root:not(.dark) .section-icon {
  font-size: 1.1rem;
  color: #2563eb;
}

:root:not(.dark) .section-title {
  font-size: 1rem;
  font-weight: 600;
  color: #1f2937;
}

.stock-form {
  margin: 0;
}

.stock-select {
  width: 100%;
}

.stock-option {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.stock-code {
  font-weight: 600;
  color: #667eea;
}

.stock-name {
  color: #64748b;
  font-size: 0.9rem;
}

/* 多级别选择样式 */
.levels-group {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.levels-group .el-checkbox {
  margin-right: 0;
}

.levels-note {
  font-size: 0.8rem;
  color: #64748b;
  margin-top: 0.5rem;
  font-style: italic;
}

/* 配置区域分栏布局 */
.config-sections {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.5rem;
}

/* 深色主题 */
:root.dark .time-section,
:root.dark .advanced-section {
  background: rgba(0, 0, 0, 0.3);
  border-radius: 12px;
  padding: 1.25rem;
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
  transition: all 0.3s ease;
}

:root.dark .time-section:hover,
:root.dark .advanced-section:hover {
  transform: translateY(-2px);
  background: rgba(0, 0, 0, 0.4);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
}

/* 浅色主题 */
:root:not(.dark) .time-section,
:root:not(.dark) .advanced-section {
  background: rgba(255, 255, 255, 0.7);
  border-radius: 12px;
  padding: 1.25rem;
  border: 1px solid rgba(0, 0, 0, 0.1);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
}

:root:not(.dark) .time-section:hover,
:root:not(.dark) .advanced-section:hover {
  transform: translateY(-2px);
  background: rgba(255, 255, 255, 0.9);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
}

.advanced-toggle {
  margin-left: auto;
}

/* 配置行 */
.config-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1rem;
  gap: 1rem;
}

.config-row:last-child {
  margin-bottom: 0;
}

/* 深色主题 */
:root.dark .config-label {
  font-size: 0.9rem;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.8);
  white-space: nowrap;
  min-width: 80px;
}

/* 浅色主题 */
:root:not(.dark) .config-label {
  font-size: 0.9rem;
  font-weight: 500;
  color: #374151;
  white-space: nowrap;
  min-width: 80px;
}

/* 时间配置 */
.timeframe-group {
  flex: 1;
}

.timeframe-group .el-radio-button {
  margin-right: 0;
}

.period-config {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex: 1;
}

.period-input {
  width: 100px;
}

/* 深色主题 */
:root.dark .period-unit {
  font-size: 0.9rem;
  color: rgba(255, 255, 255, 0.7);
}

/* 浅色主题 */
:root:not(.dark) .period-unit {
  font-size: 0.9rem;
  color: #6b7280;
}

/* 高级配置 */
.advanced-config {
  display: flex;
  flex-direction: column;
}

.config-select {
  width: 120px;
}

/* 深色主题 */
:root.dark .advanced-disabled {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100px;
  color: rgba(255, 255, 255, 0.5);
  font-size: 0.9rem;
  background: rgba(0, 0, 0, 0.2);
  border-radius: 8px;
  border: 1px dashed rgba(255, 255, 255, 0.2);
}

/* 浅色主题 */
:root:not(.dark) .advanced-disabled {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100px;
  color: #9ca3af;
  font-size: 0.9rem;
  background: rgba(0, 0, 0, 0.02);
  border-radius: 8px;
  border: 1px dashed rgba(0, 0, 0, 0.2);
}

.disabled-text {
  text-align: center;
  font-style: italic;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .config-sections {
    grid-template-columns: 1fr;
    gap: 1rem;
  }
  
  .config-row {
    flex-direction: column;
    align-items: stretch;
    gap: 0.5rem;
  }
  
  .config-label {
    min-width: auto;
    margin-bottom: 0.25rem;
  }
  
  .period-config {
    justify-content: flex-start;
  }
  
  .timeframe-group {
    width: 100%;
  }
  
  .timeframe-group .el-radio-button {
    flex: 1;
  }
}

@media (max-width: 480px) {
  .config-container {
    gap: 1rem;
  }
  
  .time-section,
  .advanced-section {
    padding: 0.75rem;
  }
  
  .section-header {
    margin-bottom: 0.75rem;
  }
  
  .config-row {
    margin-bottom: 0.75rem;
  }
}
</style>