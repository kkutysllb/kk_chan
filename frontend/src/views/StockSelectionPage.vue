<template>
  <div class="stock-selection-page">
    <div class="page-header">
      <h1 class="page-title">
        <el-icon><TrendCharts /></el-icon>
        缠论智能选股
      </h1>
      <p class="page-subtitle">基于MACD红绿柱面积对比的双向背驰选股策略：底背驰买入 + 顶背驰卖出</p>
    </div>

    <div class="page-content">
      <!-- 选股配置面板 -->
      <el-card class="config-panel" shadow="hover">
        <template #header>
          <div class="card-header">
            <span class="card-title">选股配置</span>
            <el-button 
              type="primary" 
              :loading="loading"
              @click="runStockSelection"
            >
              {{ loading ? '选股中...' : '开始选股' }}
            </el-button>
          </div>
        </template>

        <el-form :model="selectionConfig" label-width="150px" class="config-form">
          <el-row :gutter="24">
            <el-col :span="12">
              <el-form-item label="最大结果数量">
                <el-input-number
                  v-model="selectionConfig.max_results"
                  :min="10"
                  :max="200"
                  :step="10"
                  placeholder="选股结果数量"
                />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="配置预设">
                <el-select 
                  v-model="selectedPreset" 
                  placeholder="选择预设配置"
                  @change="applyPresetConfig"
                >
                  <el-option label="保守策略" value="conservative" />
                  <el-option label="平衡策略" value="balanced" />
                  <el-option label="激进策略" value="aggressive" />
                  <el-option label="自定义" value="custom" />
                </el-select>
              </el-form-item>
            </el-col>
          </el-row>

          <el-row :gutter="24">
            <el-col :span="12">
              <el-form-item label="背驰强度阈值">
                <el-slider
                  v-model="selectionConfig.min_backchi_strength"
                  :min="0"
                  :max="1"
                  :step="0.1"
                  :format-tooltip="formatTooltip"
                  show-input
                />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="绿柱面积比阈值（买入）">
                <el-slider
                  v-model="selectionConfig.min_area_ratio"
                  :min="1.1"
                  :max="3.0"
                  :step="0.1"
                  :format-tooltip="val => `${val.toFixed(1)}倍`"
                  show-input
                />
              </el-form-item>
            </el-col>
          </el-row>

          <el-row :gutter="24">
            <el-col :span="12">
              <el-form-item label="红柱面积缩小比例（卖出）">
                <el-slider
                  v-model="selectionConfig.max_area_shrink_ratio"
                  :min="0.5"
                  :max="0.9"
                  :step="0.05"
                  :format-tooltip="val => `${(val*100).toFixed(0)}%`"
                  show-input
                />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="死叉确认期间（天）">
                <el-input-number
                  v-model="selectionConfig.death_cross_confirm_days"
                  :min="1"
                  :max="5"
                  :step="1"
                />
              </el-form-item>
            </el-col>
          </el-row>

          <el-row :gutter="24">
            <el-col :span="12">
              <el-form-item label="分析天数">
                <el-input-number
                  v-model="selectionConfig.days"
                  :min="30"
                  :max="200"
                  :step="10"
                />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="金叉确认期间">
                <el-input-number
                  v-model="selectionConfig.confirm_days"
                  :min="1"
                  :max="5"
                  :step="1"
                />
              </el-form-item>
            </el-col>
          </el-row>
        </el-form>
      </el-card>

      <!-- 选股结果 -->
      <el-card class="results-panel" shadow="hover" v-if="selectionResults">
        <template #header>
          <div class="card-header">
            <span class="card-title">选股结果</span>
            <div class="result-stats">
              <el-tag type="success" size="large">
                筛选出 {{ totalResults }} 只股票
              </el-tag>
              <el-tag type="info" class="ml-2">
                成功率 {{ (selectionResults.statistics?.success_rate || 0).toFixed(1) }}%
              </el-tag>
            </div>
          </div>
        </template>

        <!-- 统计信息 -->
        <div class="statistics-section" v-if="selectionResults.statistics">
          <div class="stats-grid">
            <div class="stat-item">
              <div class="stat-value">{{ selectionResults.statistics.total_signals || 0 }}</div>
              <div class="stat-label">信号总数</div>
            </div>
            <div class="stat-item">
              <div class="stat-value">{{ selectionResults.statistics.buy_signals_count || 0 }}</div>
              <div class="stat-label">买入信号</div>
            </div>
            <div class="stat-item">
              <div class="stat-value">{{ selectionResults.statistics.sell_signals_count || 0 }}</div>
              <div class="stat-label">卖出信号</div>
            </div>
            <div class="stat-item">
              <div class="stat-value">{{ selectionResults.statistics.strength_distribution?.strong || 0 }}</div>
              <div class="stat-label">强信号</div>
            </div>
          </div>
        </div>

        <!-- 选股结果表格 -->
        <div class="results-table">
          <el-table
            :data="currentPageData"
            size="small"
            max-height="600"
            empty-text="暂无选股结果"
            @row-click="handleRowClick"
          >
            <el-table-column type="index" label="#" width="50" :index="getTableIndex" />
            
            <el-table-column prop="basic_info.symbol" label="股票代码" width="100">
              <template #default="{ row }">
                <el-link type="primary" @click="viewStockDetail(row.basic_info.symbol)">
                  {{ row.basic_info.symbol }}
                </el-link>
              </template>
            </el-table-column>
            
            <el-table-column prop="basic_info.name" label="股票名称" width="120" />
            
            <el-table-column prop="scoring.overall_score" label="综合评分" width="100" sortable>
              <template #default="{ row }">
                <el-progress
                  :percentage="Math.min(row.scoring.overall_score, 100)"
                  :stroke-width="12"
                  :color="getScoreColor(row.scoring.overall_score)"
                  :format="() => `${row.scoring.overall_score.toFixed(1)}`"
                />
              </template>
            </el-table-column>
            
            <el-table-column prop="scoring.signal_strength" label="信号强度" width="100">
              <template #default="{ row }">
                <el-tag 
                  :type="getStrengthType(row.scoring.signal_strength)"
                  size="small"
                >
                  {{ getStrengthText(row.scoring.signal_strength) }}
                </el-tag>
              </template>
            </el-table-column>
            
            <el-table-column prop="scoring.recommendation" label="投资建议" width="100">
              <template #default="{ row }">
                <el-tag 
                  :type="getRecommendationType(row.scoring.recommendation)"
                  size="small"
                >
                  {{ row.scoring.recommendation }}
                </el-tag>
              </template>
            </el-table-column>
            
            <el-table-column label="背驰分析" width="150">
              <template #default="{ row }">
                <div class="analysis-info">
                  <div class="analysis-item">
                    <el-tag 
                      :type="row.backchi_analysis.backchi_type === 'bottom' ? 'success' : 'danger'" 
                      size="small"
                    >
                      {{ row.backchi_analysis.backchi_type === 'bottom' ? '底背驰' : '顶背驰' }}
                    </el-tag>
                    <span class="ml-1">{{ (row.backchi_analysis.reliability * 100).toFixed(1) }}%</span>
                  </div>
                  <div v-if="row.backchi_analysis.has_macd_golden_cross" class="analysis-item">
                    <el-tag type="warning" size="small">MACD金叉</el-tag>
                  </div>
                  <div v-if="row.backchi_analysis.has_macd_death_cross" class="analysis-item">
                    <el-tag type="danger" size="small">MACD死叉</el-tag>
                  </div>
                  <div class="analysis-item">
                    <span class="text-sm text-gray-500">
                      {{ getAreaRatioFromDescription(row.backchi_analysis.description) }}
                    </span>
                  </div>
                </div>
              </template>
            </el-table-column>
            
            <el-table-column label="技术分析" width="150">
              <template #default="{ row }">
                <div class="analysis-info">
                  <div class="analysis-item">
                    <span class="text-sm text-gray-500">
                      价差: {{ getMacdValueFromDescription(row.backchi_analysis.description, 'price_diff') }}
                    </span>
                  </div>
                  <div class="analysis-item">
                    <span class="text-sm text-gray-500">
                      可靠度: {{ (row.backchi_analysis.reliability * 100).toFixed(0) }}%
                    </span>
                  </div>
                  <div class="analysis-item">
                    <span class="text-sm text-gray-500">
                      状态: {{ row.backchi_analysis.has_macd_golden_cross ? '金叉' : (row.backchi_analysis.has_macd_death_cross ? '死叉' : '中性') }}
                    </span>
                  </div>
                </div>
              </template>
            </el-table-column>
            
            <el-table-column label="关键价位" width="180">
              <template #default="{ row }">
                <div class="price-info" v-if="row.key_prices.entry_price">
                  <div class="price-item">
                    <span class="price-label">入场:</span>
                    <span class="price-value">{{ row.key_prices.entry_price }}</span>
                  </div>
                  <div class="price-item">
                    <span class="price-label">止损:</span>
                    <span class="price-value text-red-500">{{ row.key_prices.stop_loss?.toFixed(2) }}</span>
                  </div>
                  <div class="price-item">
                    <span class="price-label">止盈:</span>
                    <span class="price-value text-green-500">{{ row.key_prices.take_profit?.toFixed(2) }}</span>
                  </div>
                  <div class="price-item">
                    <span class="price-label">盈亏比:</span>
                    <span class="price-value">{{ row.key_prices.risk_reward_ratio }}</span>
                  </div>
                </div>
                <span v-else class="text-gray-400">无价位信息</span>
              </template>
            </el-table-column>
            
            <el-table-column label="分析时间" width="120">
              <template #default="{ row }">
                <span class="text-sm text-gray-500">
                  {{ formatTime(row.basic_info.analysis_time) }}
                </span>
              </template>
            </el-table-column>
            
            <el-table-column label="操作" width="100" fixed="right">
              <template #default="{ row }">
                <el-button
                  type="primary"
                  size="small"
                  @click="viewStockDetail(row.basic_info.symbol)"
                >
                  查看详情
                </el-button>
              </template>
            </el-table-column>
          </el-table>

          <!-- 分页组件 -->
          <div class="pagination-wrapper" v-if="totalResults > 0">
            <el-pagination
              v-model:current-page="currentPage"
              v-model:page-size="pageSize"
              :page-sizes="[10, 20, 50, 100]"
              :total="totalResults"
              layout="total, sizes, prev, pager, next, jumper"
              @size-change="handleSizeChange"
              @current-change="handleCurrentChange"
            />
          </div>
        </div>
      </el-card>

      <!-- 空状态 -->
      <el-card v-else class="empty-results" shadow="hover">
        <el-empty description="点击开始选股，查看筛选结果">
          <el-button type="primary" @click="runStockSelection">
            开始选股
          </el-button>
        </el-empty>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { TrendCharts } from '@element-plus/icons-vue'
import { pythonApi } from '@/utils/api'
import { useRouter } from 'vue-router'

const router = useRouter()

// 响应式数据
const loading = ref(false)
const selectionResults = ref(null)
const selectedPreset = ref('balanced')
const currentPage = ref(1)
const pageSize = ref(10)

// 选股配置
const selectionConfig = reactive({
  max_results: 50,
  min_backchi_strength: 0.6,
  min_area_ratio: 1.5,
  max_area_shrink_ratio: 0.8,
  days: 60,
  confirm_days: 3,
  death_cross_confirm_days: 2
})

// 计算属性
const allResults = computed(() => {
  if (!selectionResults.value || !selectionResults.value.results) return []
  return [...(selectionResults.value.results.buy_signals || []), ...(selectionResults.value.results.sell_signals || [])]
})

const totalResults = computed(() => allResults.value.length)

const currentPageData = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return allResults.value.slice(start, end)
})

// 预设配置
const presetConfigs = {
  conservative: {
    min_backchi_strength: 0.8,
    min_area_ratio: 2.0,
    max_area_shrink_ratio: 0.7,
    death_cross_confirm_days: 3,
    description: '保守策略：高阈值严格筛选'
  },
  balanced: {
    min_backchi_strength: 0.6,
    min_area_ratio: 1.5,
    max_area_shrink_ratio: 0.8,
    death_cross_confirm_days: 2,
    description: '平衡策略：中等阈值筛选'
  },
  aggressive: {
    min_backchi_strength: 0.4,
    min_area_ratio: 1.2,
    max_area_shrink_ratio: 0.85,
    death_cross_confirm_days: 1,
    description: '激进策略：低阈值快速响应'
  }
}

// 方法
const formatTooltip = (value) => {
  return `${(value * 100).toFixed(0)}%`
}

const getTableIndex = (index) => {
  return (currentPage.value - 1) * pageSize.value + index + 1
}

const handleSizeChange = (val) => {
  pageSize.value = val
  currentPage.value = 1
}

const handleCurrentChange = (val) => {
  currentPage.value = val
}

const getAreaRatioFromDescription = (description) => {
  if (!description) return '-'
  const match = description.match(/面积比([\d.]+)/)
  return match ? `面积比: ${match[1]}` : '-'
}

const getMacdValueFromDescription = (description, type) => {
  // 从描述中提取价差信息作为MACD相关数据的替代显示
  if (!description) return '-'
  
  try {
    if (type === 'price_diff') {
      const match = description.match(/价差([\d.]+)%/)
      return match ? `${match[1]}%` : '-'
    }
    // DIF、DEA具体数值后端未返回，显示状态信息
    return '-'
  } catch {
    return '-'
  }
}

const applyPresetConfig = (preset) => {
  if (preset && presetConfigs[preset]) {
    const config = presetConfigs[preset]
    selectionConfig.min_backchi_strength = config.min_backchi_strength
    selectionConfig.min_area_ratio = config.min_area_ratio
    selectionConfig.max_area_shrink_ratio = config.max_area_shrink_ratio
    selectionConfig.death_cross_confirm_days = config.death_cross_confirm_days
    ElMessage.success(`已应用${config.description}`)
  }
}

const runStockSelection = async () => {
  loading.value = true
  try {
    ElMessage.info('开始执行选股，请稍候...')
    
    const result = await pythonApi.runStockSelection({
      max_results: selectionConfig.max_results,
      min_backchi_strength: selectionConfig.min_backchi_strength,
      min_area_ratio: selectionConfig.min_area_ratio,
      max_area_shrink_ratio: selectionConfig.max_area_shrink_ratio,
      confirm_days: selectionConfig.confirm_days,
      death_cross_confirm_days: selectionConfig.death_cross_confirm_days
    })
    
    selectionResults.value = result
    currentPage.value = 1 // 重置到第一页
    
    const count = totalResults.value
    ElMessage.success(`选股完成！筛选出 ${count} 只股票`)
    
  } catch (error) {
    console.error('选股失败:', error)
    ElMessage.error(`选股失败: ${error.message}`)
  } finally {
    loading.value = false
  }
}

const getScoreColor = (score) => {
  if (score >= 80) return '#67c23a' // 绿色
  if (score >= 60) return '#e6a23c' // 橙色
  return '#f56c6c' // 红色
}

const getStrengthType = (strength) => {
  switch (strength) {
    case 'strong': return 'success'
    case 'medium': return 'warning'
    case 'weak': return 'info'
    default: return 'info'
  }
}

const getStrengthText = (strength) => {
  switch (strength) {
    case 'strong': return '强'
    case 'medium': return '中'
    case 'weak': return '弱'
    default: return '未知'
  }
}

const getRecommendationType = (recommendation) => {
  if (recommendation?.includes('强烈')) return 'danger'
  if (recommendation?.includes('建议')) return 'warning'
  if (recommendation?.includes('谨慎')) return 'success'
  return 'info'
}

const getTrendText = (direction) => {
  switch (direction) {
    case 'up': return '上涨'
    case 'down': return '下跌'
    case 'sideways': return '横盘'
    default: return '未知'
  }
}

const formatTime = (timeStr) => {
  if (!timeStr) return '-'
  try {
    const date = new Date(timeStr)
    return date.toLocaleString('zh-CN', {
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    })
  } catch {
    return timeStr
  }
}

const handleRowClick = (row) => {
  // 点击行查看详情
  viewStockDetail(row.basic_info.symbol)
}

const viewStockDetail = (symbol) => {
  // 跳转到股票详情页面
  router.push({
    name: 'Home',
    query: { symbol }
  })
}

// 生命周期
onMounted(() => {
  // 初始化时应用默认预设
  applyPresetConfig(selectedPreset.value)
})
</script>

<style scoped>
.stock-selection-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.page-header {
  text-align: center;
  margin-bottom: 30px;
}

.page-title {
  font-size: 32px;
  font-weight: 700;
  color: white;
  margin: 0 0 10px 0;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
}

.page-subtitle {
  font-size: 16px;
  color: rgba(255, 255, 255, 0.8);
  margin: 0;
  max-width: 600px;
  margin: 0 auto;
  line-height: 1.6;
}

.page-content {
  max-width: 1400px;
  margin: 0 auto;
}

.config-panel,
.results-panel,
.empty-results {
  margin-bottom: 20px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-title {
  font-weight: 600;
  font-size: 18px;
  color: var(--el-text-color-primary);
}

.result-stats {
  display: flex;
  align-items: center;
}

.config-form {
  padding: 20px;
}

.statistics-section {
  margin-bottom: 20px;
  padding: 20px;
  background: rgba(102, 126, 234, 0.05);
  border-radius: 12px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
}

.stat-item {
  text-align: center;
  padding: 16px;
  background: rgba(255, 255, 255, 0.8);
  border-radius: 8px;
  border: 1px solid rgba(102, 126, 234, 0.1);
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  color: #667eea;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 12px;
  color: var(--el-text-color-secondary);
  font-weight: 500;
}

.results-table {
  padding: 0 20px 20px;
}

.pagination-wrapper {
  display: flex;
  justify-content: center;
  margin-top: 20px;
  padding: 20px 0;
  border-top: 1px solid var(--el-border-color-lighter);
}

.analysis-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.analysis-item {
  display: flex;
  align-items: center;
  gap: 4px;
}

.price-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
  font-size: 12px;
}

.price-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.price-label {
  font-weight: 500;
  color: var(--el-text-color-secondary);
  min-width: 30px;
}

.price-value {
  font-weight: 600;
  color: var(--el-text-color-primary);
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .page-content {
    padding: 0 10px;
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .page-title {
    font-size: 24px;
  }
  
  .config-form {
    padding: 10px;
  }
}

/* 工具类 */
.ml-1 { margin-left: 4px; }
.ml-2 { margin-left: 8px; }
.text-sm { font-size: 12px; }
.text-gray-400 { color: #9ca3af; }
.text-gray-500 { color: #6b7280; }
.text-red-500 { color: #ef4444; }
.text-green-500 { color: #10b981; }
</style>