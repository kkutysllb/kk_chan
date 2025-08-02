<template>
  <div class="stock-selection-page">
    <div class="page-header">
      <h1 class="page-title">
        <el-icon><TrendCharts /></el-icon>
        缠论智能选股
      </h1>
      <p class="page-subtitle">基于30分钟底背驰筛选 + 5分钟买点确认的多级别选股策略</p>
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
              <el-form-item label="买点强度阈值">
                <el-slider
                  v-model="selectionConfig.min_buy_point_strength"
                  :min="0"
                  :max="1"
                  :step="0.1"
                  :format-tooltip="formatTooltip"
                  show-input
                />
              </el-form-item>
            </el-col>
          </el-row>

          <el-row :gutter="24">
            <el-col :span="12">
              <el-form-item label="30分钟分析天数">
                <el-input-number
                  v-model="selectionConfig.days_30min"
                  :min="30"
                  :max="200"
                  :step="10"
                />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="5分钟分析天数">
                <el-input-number
                  v-model="selectionConfig.days_5min"
                  :min="5"
                  :max="30"
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
                筛选出 {{ selectionResults.meta?.actual_results || 0 }} 只股票
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
              <div class="stat-value">{{ selectionResults.statistics.signals_found || 0 }}</div>
              <div class="stat-label">信号总数</div>
            </div>
            <div class="stat-item">
              <div class="stat-value">{{ selectionResults.statistics.strength_distribution?.strong || 0 }}</div>
              <div class="stat-label">强信号</div>
            </div>
            <div class="stat-item">
              <div class="stat-value">{{ selectionResults.statistics.strength_distribution?.medium || 0 }}</div>
              <div class="stat-label">中等信号</div>
            </div>
            <div class="stat-item">
              <div class="stat-value">{{ selectionResults.statistics.recommendation_distribution?.['强烈关注'] || 0 }}</div>
              <div class="stat-label">强烈关注</div>
            </div>
          </div>
        </div>

        <!-- 选股结果表格 -->
        <div class="results-table">
          <el-table
            :data="selectionResults.results"
            size="small"
            max-height="600"
            empty-text="暂无选股结果"
            @row-click="handleRowClick"
          >
            <el-table-column type="index" label="#" width="50" />
            
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
                  :percentage="row.scoring.overall_score"
                  :stroke-width="12"
                  :color="getScoreColor(row.scoring.overall_score)"
                  :format="() => `${row.scoring.overall_score}`"
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
            
            <el-table-column label="30分钟分析" width="150">
              <template #default="{ row }">
                <div class="analysis-info">
                  <div v-if="row.min30_analysis.has_bottom_backchi" class="analysis-item">
                    <el-tag type="success" size="small">底背驰</el-tag>
                    <span class="ml-1">{{ (row.min30_analysis.backchi_strength * 100).toFixed(1) }}%</span>
                  </div>
                  <div class="analysis-item">
                    <el-tag 
                      :type="row.min30_analysis.trend_direction === 'up' ? 'danger' : 'primary'"
                      size="small"
                    >
                      {{ getTrendText(row.min30_analysis.trend_direction) }}
                    </el-tag>
                  </div>
                </div>
              </template>
            </el-table-column>
            
            <el-table-column label="5分钟分析" width="150">
              <template #default="{ row }">
                <div class="analysis-info">
                  <div v-if="row.min5_analysis.has_latest_buy_signal" class="analysis-item">
                    <el-tag type="warning" size="small">买点信号</el-tag>
                    <span class="ml-1">{{ (row.min5_analysis.latest_buy_strength * 100).toFixed(1) }}%</span>
                  </div>
                  <div class="analysis-item">
                    <span class="text-sm text-gray-500">
                      {{ row.min5_analysis.buy_points_count }} 个买点
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
                    <span class="price-value text-red-500">{{ row.key_prices.stop_loss }}</span>
                  </div>
                  <div class="price-item">
                    <span class="price-label">止盈:</span>
                    <span class="price-value text-green-500">{{ row.key_prices.take_profit }}</span>
                  </div>
                  <div class="price-item" v-if="row.key_prices.risk_reward_ratio">
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
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { TrendCharts } from '@element-plus/icons-vue'
import { pythonApi } from '@/utils/api'
import { useRouter } from 'vue-router'

const router = useRouter()

// 响应式数据
const loading = ref(false)
const selectionResults = ref(null)
const selectedPreset = ref('balanced')

// 选股配置
const selectionConfig = reactive({
  max_results: 50,
  min_backchi_strength: 0.6,
  min_buy_point_strength: 0.5,
  days_30min: 60,
  days_5min: 10
})

// 预设配置
const presetConfigs = {
  conservative: {
    min_backchi_strength: 0.8,
    min_buy_point_strength: 0.7,
    description: '保守策略：高强度信号筛选'
  },
  balanced: {
    min_backchi_strength: 0.6,
    min_buy_point_strength: 0.5,
    description: '平衡策略：中等强度信号筛选'
  },
  aggressive: {
    min_backchi_strength: 0.4,
    min_buy_point_strength: 0.3,
    description: '激进策略：低强度信号筛选'
  }
}

// 方法
const formatTooltip = (value) => {
  return `${(value * 100).toFixed(0)}%`
}

const applyPresetConfig = (preset) => {
  if (preset && presetConfigs[preset]) {
    const config = presetConfigs[preset]
    selectionConfig.min_backchi_strength = config.min_backchi_strength
    selectionConfig.min_buy_point_strength = config.min_buy_point_strength
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
      min_buy_point_strength: selectionConfig.min_buy_point_strength
    })
    
    selectionResults.value = result
    
    const count = result.meta?.actual_results || 0
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
  switch (recommendation) {
    case '强烈关注': return 'danger'
    case '密切监控': return 'warning'
    case '适度关注': return 'success'
    case '观望': return 'info'
    default: return 'info'
  }
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
    name: 'HomePage',
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