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

        <div class="config-container">
          <!-- 基础配置 -->
          <div class="config-section">
            <div class="section-header">
              <el-icon class="section-icon"><Setting /></el-icon>
              <span class="section-title">基础配置</span>
            </div>
            <div class="section-content">
              <el-form :model="selectionConfig" class="config-form">
                <el-row :gutter="20">
                  <el-col :span="12">
                    <div class="form-group">
                      <label class="form-label">最大结果数量</label>
                      <el-input-number
                        v-model="selectionConfig.max_results"
                        :min="10"
                        :max="200"
                        :step="10"
                        placeholder="选股结果数量"
                        size="large"
                        class="full-width"
                      />
                    </div>
                  </el-col>
                  <el-col :span="12">
                    <div class="form-group">
                      <label class="form-label">配置预设</label>
                      <el-select 
                        v-model="selectedPreset" 
                        placeholder="选择预设配置"
                        @change="applyPresetConfig"
                        size="large"
                        class="full-width"
                      >
                        <el-option label="保守策略" value="conservative" />
                        <el-option label="平衡策略" value="balanced" />
                        <el-option label="激进策略" value="aggressive" />
                        <el-option label="自定义" value="custom" />
                      </el-select>
                    </div>
                  </el-col>
                </el-row>
                <el-row :gutter="20">
                  <el-col :span="12">
                    <div class="form-group">
                      <label class="form-label">分析天数</label>
                      <el-input-number
                        v-model="selectionConfig.days"
                        :min="30"
                        :max="200"
                        :step="10"
                        size="large"
                        class="full-width"
                      />
                    </div>
                  </el-col>
                  <el-col :span="12">
                    <div class="form-group">
                      <label class="form-label">金叉确认期间</label>
                      <el-input-number
                        v-model="selectionConfig.confirm_days"
                        :min="1"
                        :max="5"
                        :step="1"
                        size="large"
                        class="full-width"
                      />
                    </div>
                  </el-col>
                </el-row>
              </el-form>
            </div>
          </div>

          <!-- 背驰参数 -->
          <div class="config-section">
            <div class="section-header">
              <el-icon class="section-icon"><TrendCharts /></el-icon>
              <span class="section-title">背驰参数</span>
            </div>
            <div class="section-content">
              <el-form :model="selectionConfig" class="config-form">
                <div class="slider-group">
                  <label class="form-label">背驰强度阈值</label>
                  <el-slider
                    v-model="selectionConfig.min_backchi_strength"
                    :min="0"
                    :max="1"
                    :step="0.1"
                    :format-tooltip="formatTooltip"
                    show-input
                    class="config-slider"
                  />
                </div>
                <div class="slider-group">
                  <label class="form-label">绿柱面积比阈值（买入）</label>
                  <el-slider
                    v-model="selectionConfig.min_area_ratio"
                    :min="1.1"
                    :max="3.0"
                    :step="0.1"
                    :format-tooltip="val => `${val.toFixed(1)}倍`"
                    show-input
                    class="config-slider"
                  />
                </div>
                <div class="slider-group">
                  <label class="form-label">红柱面积缩小比例（卖出）</label>
                  <el-slider
                    v-model="selectionConfig.max_area_shrink_ratio"
                    :min="0.5"
                    :max="0.9"
                    :step="0.05"
                    :format-tooltip="val => `${(val*100).toFixed(0)}%`"
                    show-input
                    class="config-slider"
                  />
                </div>
                <div class="form-group">
                  <label class="form-label">死叉确认期间（天）</label>
                  <el-input-number
                    v-model="selectionConfig.death_cross_confirm_days"
                    :min="1"
                    :max="5"
                    :step="1"
                    size="large"
                    style="width: 200px;"
                  />
                </div>
              </el-form>
            </div>
          </div>
        </div>
      </el-card>

      <!-- 选股结果 -->
      <el-card class="results-panel" shadow="hover" v-if="selectionResults">
        <template #header>
          <div class="card-header">
            <span class="card-title">选股结果</span>
            <div class="result-actions">
              <div class="result-stats">
                <el-tag type="success" size="large">
                  筛选出 {{ totalResults }} 只股票
                </el-tag>
                <el-tag type="info" class="ml-2">
                  成功率 {{ (selectionResults.statistics?.success_rate || 0).toFixed(1) }}%
                </el-tag>
              </div>
              <div class="export-buttons">
                <el-button 
                  type="success" 
                  :icon="Download" 
                  size="small"
                  @click="exportToExcel"
                  :disabled="!allResults || allResults.length === 0"
                >
                  导出Excel
                </el-button>
                <el-button 
                  type="primary" 
                  :icon="Document" 
                  size="small"
                  @click="exportToJson"
                  :disabled="!allResults || allResults.length === 0"
                >
                  导出JSON
                </el-button>
              </div>
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
            style="width: 100%"
          >
            <el-table-column type="index" label="序号" width="60" :index="getTableIndex" />
            
            <el-table-column prop="basic_info.symbol" label="股票代码" min-width="100">
              <template #default="{ row }">
                <el-link type="primary" @click="viewStockDetail(row.basic_info.symbol)">
                  {{ row.basic_info.symbol }}
                </el-link>
              </template>
            </el-table-column>
            
            <el-table-column prop="basic_info.name" label="股票名称" min-width="140" show-overflow-tooltip />
            
            <el-table-column prop="scoring.overall_score" label="综合评分" min-width="120" sortable>
              <template #default="{ row }">
                <el-progress
                  :percentage="Math.min(row.scoring.overall_score, 100)"
                  :stroke-width="12"
                  :color="getScoreColor(row.scoring.overall_score)"
                  :format="() => `${row.scoring.overall_score.toFixed(1)}`"
                />
              </template>
            </el-table-column>
            
            <el-table-column prop="scoring.signal_strength" label="信号强度" min-width="100">
              <template #default="{ row }">
                <el-tag 
                  :type="getStrengthType(row.scoring.signal_strength)"
                  size="small"
                >
                  {{ getStrengthText(row.scoring.signal_strength) }}
                </el-tag>
              </template>
            </el-table-column>
            
            <el-table-column prop="scoring.recommendation" label="投资建议" min-width="140" show-overflow-tooltip>
              <template #default="{ row }">
                <el-tag 
                  :type="getRecommendationType(row.scoring.recommendation)"
                  size="small"
                >
                  {{ row.scoring.recommendation }}
                </el-tag>
              </template>
            </el-table-column>
            
            <el-table-column label="背驰分析" min-width="200">
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
            
            <el-table-column label="技术分析" min-width="180">
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
            
            <el-table-column label="关键价位" min-width="240">
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
            
            <el-table-column label="分析时间" min-width="120">
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
import { TrendCharts, Download, Document, Setting } from '@element-plus/icons-vue'
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

// 导出功能函数
const exportToExcel = () => {
  try {
    const data = allResults.value.map((row, index) => ({
      '序号': index + 1,
      '股票代码': row.basic_info?.symbol || '-',
      '股票名称': row.basic_info?.name || '-',
      '信号类型': row.basic_info?.signal_type || '-',
      '综合评分': row.scoring?.overall_score || '-',
      '信号强度': getStrengthText(row.scoring?.signal_strength) || '-',
      '推荐等级': row.scoring?.recommendation || '-',
      '背驰类型': row.backchi_analysis?.backchi_type === 'bottom' ? '底背驰' : (row.backchi_analysis?.backchi_type === 'top' ? '顶背驰' : '-'),
      '可靠度': row.backchi_analysis?.reliability ? `${(row.backchi_analysis.reliability * 100).toFixed(1)}%` : '-',
      'MACD状态': row.backchi_analysis?.has_macd_golden_cross ? '金叉' : (row.backchi_analysis?.has_macd_death_cross ? '死叉' : '中性'),
      '入场价格': row.key_prices?.entry_price || '-',
      '止损价格': row.key_prices?.stop_loss || '-',
      '止盈价格': row.key_prices?.take_profit || '-',
      '风险回报比': row.key_prices?.risk_reward_ratio || '-',
      '分析时间': row.basic_info?.analysis_time ? new Date(row.basic_info.analysis_time).toLocaleString('zh-CN') : '-',
      '背驰描述': row.backchi_analysis?.description || '-'
    }))

    // 创建CSV内容
    const headers = Object.keys(data[0])
    const csvContent = [
      headers.join(','),
      ...data.map(row => headers.map(header => `"${row[header]}"`).join(','))
    ].join('\n')

    // 添加BOM以支持中文
    const BOM = '\uFEFF'
    const blob = new Blob([BOM + csvContent], { type: 'text/csv;charset=utf-8;' })
    
    // 创建下载链接
    const link = document.createElement('a')
    const url = URL.createObjectURL(blob)
    link.setAttribute('href', url)
    
    const timestamp = new Date().toISOString().slice(0, 19).replace(/[:-]/g, '')
    link.setAttribute('download', `缠论选股结果_${timestamp}.csv`)
    
    link.style.visibility = 'hidden'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    
    ElMessage.success('Excel文件导出成功！')
  } catch (error) {
    console.error('导出Excel失败:', error)
    ElMessage.error('导出Excel失败，请重试')
  }
}

const exportToJson = () => {
  try {
    const exportData = {
      meta: {
        export_time: new Date().toISOString(),
        total_count: allResults.value.length,
        selection_config: selectionConfig
      },
      statistics: selectionResults.value?.statistics || {},
      results: allResults.value
    }

    const jsonContent = JSON.stringify(exportData, null, 2)
    const blob = new Blob([jsonContent], { type: 'application/json;charset=utf-8;' })
    
    const link = document.createElement('a')
    const url = URL.createObjectURL(blob)
    link.setAttribute('href', url)
    
    const timestamp = new Date().toISOString().slice(0, 19).replace(/[:-]/g, '')
    link.setAttribute('download', `缠论选股结果_${timestamp}.json`)
    
    link.style.visibility = 'hidden'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    
    ElMessage.success('JSON文件导出成功！')
  } catch (error) {
    console.error('导出JSON失败:', error)
    ElMessage.error('导出JSON失败，请重试')
  }
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
  background: var(--page-gradient);
  padding: 0;
  width: 100%;
  max-width: 100%;
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
  gap: var(--space-lg);
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
  margin: 0 auto;
  max-width: 640px;
  line-height: 1.7;
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
  max-width: 100vw;
  display: flex;
  flex-direction: column;
  gap: 0;
  padding: 0;
}

.config-panel,
.results-panel,
.empty-results {
  background: var(--bg-glass);
  backdrop-filter: var(--backdrop-blur);
  border: none;
  border-radius: 0;
  border-bottom: 1px solid var(--glass-border);
  box-shadow: none;
  margin: 0;
  padding: var(--space-xl);
  width: 100%;
  max-width: 100%;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.results-panel .el-card__body {
  padding: 0;
}

.results-panel,
.empty-results {
  border-bottom: none;
}

.config-panel:hover,
.results-panel:hover {
  transform: none;
  background: var(--bg-elevated);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-title {
  font-weight: 700;
  font-size: 1.25rem;
  color: var(--text-primary);
  background: var(--gradient-primary);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.result-actions {
  display: flex;
  align-items: center;
  gap: var(--space-xl);
}

.result-stats {
  display: flex;
  align-items: center;
  gap: var(--space-md);
}

.export-buttons {
  display: flex;
  gap: var(--space-sm);
}

.config-container {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.config-section {
  background: var(--bg-secondary);
  border-radius: 16px;
  padding: 1.5rem;
  border: 1px solid var(--border-primary);
  transition: all 0.3s ease;
}

.config-section:hover {
  background: var(--bg-elevated);
  border-color: var(--border-focus);
}

.section-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 1.5rem;
  padding-bottom: 0.75rem;
  border-bottom: 2px solid var(--border-primary);
}

.section-icon {
  font-size: 1.2rem;
  color: var(--color-primary);
}

.section-title {
  font-size: 1.1rem;
  font-weight: 700;
  color: var(--text-primary);
}

.section-content {
  padding: 0;
}

.config-form {
  margin: 0;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-label {
  display: block;
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 0.5rem;
}

.slider-group {
  margin-bottom: 2rem;
}

.slider-group .form-label {
  margin-bottom: 1rem;
}

.config-slider {
  padding-right: 1rem;
}

.full-width {
  width: 100%;
}

.config-form :deep(.el-form-item__label) {
  color: var(--text-primary);
  font-weight: 600;
}

.config-form :deep(.el-input__wrapper) {
  background-color: var(--bg-primary);
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-xs);
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

.config-form :deep(.el-input__wrapper:hover) {
  border-color: var(--border-focus);
  box-shadow: var(--shadow-sm);
}

.config-form :deep(.el-input__wrapper.is-focus) {
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px var(--color-primary-light);
}

.statistics-section {
  margin: 0 0 var(--space-xl) 0;
  padding: var(--space-xl);
  background: linear-gradient(135deg, 
    var(--bg-elevated) 0%, 
    rgba(255, 255, 255, 0.05) 50%, 
    var(--bg-elevated) 100%);
  backdrop-filter: blur(10px);
  border-radius: var(--radius-xl);
  border: 1px solid var(--border-primary);
  box-shadow: var(--shadow-lg);
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: var(--space-lg);
  width: 100%;
}

.stat-item {
  text-align: center;
  padding: var(--space-lg);
  background: linear-gradient(135deg, 
    var(--bg-secondary) 0%, 
    rgba(255, 255, 255, 0.05) 50%, 
    var(--bg-secondary) 100%);
  backdrop-filter: blur(8px);
  border-radius: var(--radius-lg);
  border: 1px solid var(--border-primary);
  box-shadow: var(--shadow-md);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
}

.stat-item:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-xl);
  border-color: var(--border-focus);
  background: linear-gradient(135deg, 
    var(--bg-elevated) 0%, 
    rgba(255, 255, 255, 0.1) 50%, 
    var(--bg-elevated) 100%);
}

.stat-item::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.1), transparent);
  transition: left 0.6s ease;
}

.stat-item:hover::before {
  left: 100%;
}

.stat-value {
  font-size: 2rem;
  font-weight: 800;
  color: var(--color-primary);
  margin-bottom: var(--space-xs);
  background: var(--gradient-primary);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.stat-label {
  font-size: 0.875rem;
  color: var(--text-secondary);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.results-table {
  padding: 0;
  margin: 0;
  width: 100%;
}

.results-panel {
  width: 100%;
  max-width: 100%;
  overflow-x: auto;
}

/* 现代化表格样式 */
.results-table :deep(.el-table) {
  background-color: var(--bg-elevated);
  border-radius: 0;
  overflow: hidden;
  box-shadow: none;
  border: none;
  border-top: 1px solid var(--border-primary);
  width: 100% !important;
  table-layout: auto;
}

.results-table :deep(.el-table .el-table__cell) {
  padding: var(--space-md) var(--space-sm);
}

.results-table :deep(.el-table__inner-wrapper) {
  width: 100% !important;
}

.results-table :deep(.el-table__header-wrapper),
.results-table :deep(.el-table__body-wrapper) {
  width: 100% !important;
}

.results-table :deep(.el-table__header) {
  background-color: var(--bg-secondary);
}

.results-table :deep(.el-table__header th) {
  background-color: var(--bg-secondary);
  color: var(--text-primary);
  font-weight: 700;
  font-size: 0.875rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  border-bottom: 2px solid var(--border-primary);
  padding: var(--space-lg) var(--space-md);
}

.results-table :deep(.el-table__body tr) {
  background-color: var(--bg-elevated);
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

.results-table :deep(.el-table__body tr:hover) {
  background-color: var(--bg-secondary);
  transform: scale(1.005);
  box-shadow: var(--shadow-md);
}

.results-table :deep(.el-table__body td) {
  color: var(--text-primary);
  border-bottom: 1px solid var(--border-primary);
  padding: var(--space-md);
}

.results-table :deep(.el-table__empty-text) {
  color: var(--text-secondary);
}

.pagination-wrapper {
  display: flex;
  justify-content: center;
  margin: var(--space-xl) 0 0 0;
  padding: var(--space-xl) var(--space-xl) 0;
  border-top: 1px solid var(--border-primary);
  background: var(--bg-elevated);
}

.pagination-wrapper :deep(.el-pagination) {
  background-color: transparent;
}

.pagination-wrapper :deep(.el-pagination .el-pager li) {
  background-color: var(--bg-elevated);
  color: var(--text-primary);
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-lg);
  margin: 0 var(--space-xs);
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

.pagination-wrapper :deep(.el-pagination .el-pager li:hover) {
  background-color: var(--color-primary-light);
  border-color: var(--color-primary);
  transform: translateY(-2px);
  box-shadow: var(--shadow-sm);
}

.pagination-wrapper :deep(.el-pagination .el-pager li.is-active) {
  background-color: var(--color-primary);
  color: var(--text-inverse);
  border-color: var(--color-primary);
  box-shadow: var(--shadow-md);
}

.pagination-wrapper :deep(.el-pagination .btn-prev),
.pagination-wrapper :deep(.el-pagination .btn-next) {
  background-color: var(--bg-elevated);
  color: var(--text-primary);
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-lg);
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

.pagination-wrapper :deep(.el-pagination .btn-prev:hover),
.pagination-wrapper :deep(.el-pagination .btn-next:hover) {
  background-color: var(--color-primary-light);
  border-color: var(--color-primary);
  transform: translateY(-2px);
}

.analysis-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
  font-size: 0.75rem;
}

.analysis-item {
  display: flex;
  align-items: center;
  gap: 4px;
  flex-wrap: wrap;
}

.analysis-item .text-sm {
  font-size: 0.7rem;
  line-height: 1.2;
}

/* 现代化按钮样式 */
:deep(.el-button) {
  border-radius: var(--radius-lg);
  font-weight: 600;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
}

:deep(.el-button:hover) {
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

:deep(.el-button--primary) {
  background: var(--gradient-primary);
  border: none;
  color: var(--text-inverse);
}

:deep(.el-button--success) {
  background: var(--gradient-success);
  border: none;
  color: var(--text-inverse);
}

:deep(.el-button--warning) {
  background: var(--gradient-warning);
  border: none;
  color: var(--text-inverse);
}

/* 现代化标签样式 */
:deep(.el-tag) {
  border-radius: var(--radius-full);
  font-weight: 600;
  font-size: 0.75rem;
  padding: var(--space-xs) var(--space-md);
  border: none;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

:deep(.el-tag--success) {
  background: var(--color-success-light);
  color: var(--color-success);
}

:deep(.el-tag--info) {
  background: var(--color-primary-light);
  color: var(--color-primary);
}

:deep(.el-tag--warning) {
  background: var(--color-warning-light);
  color: var(--color-warning);
}

:deep(.el-tag--danger) {
  background: var(--color-danger-light);
  color: var(--color-danger);
}



.price-info {
  display: flex;
  flex-direction: column;
  gap: 3px;
  font-size: 0.75rem;
  color: var(--text-secondary);
}

.price-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  white-space: nowrap;
}

.price-label {
  font-weight: 500;
  color: var(--el-text-color-secondary);
  min-width: 35px;
  font-size: 0.7rem;
}

.price-value {
  font-weight: 600;
  color: var(--el-text-color-primary);
  font-size: 0.75rem;
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .page-content {
    max-width: 100%;
    padding: 0;
  }
  
  .config-panel,
  .results-panel,
  .empty-results {
    padding: var(--space-lg);
  }
  
  .stats-grid {
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: var(--space-md);
  }
  
  .stat-value {
    font-size: 1.5rem;
  }
}

@media (max-width: 768px) {
  .stock-selection-page {
    padding: 0;
  }
  
  .page-header {
    padding: var(--space-lg) var(--space-md) 0;
  }
  
  .page-title {
    font-size: 2rem;
  }
  
  .page-subtitle {
    font-size: 1rem;
  }
  
  .config-panel,
  .results-panel,
  .empty-results {
    padding: var(--space-md);
  }
  
  .card-header {
    flex-direction: column;
    align-items: flex-start;
    gap: var(--space-md);
  }
  
  .result-actions {
    width: 100%;
    justify-content: space-between;
  }
  
  .export-buttons {
    flex-direction: column;
    width: 100%;
  }
  
  .stats-grid {
    grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
    gap: var(--space-sm);
  }
  
  .stat-item {
    padding: var(--space-md);
  }
  
  .stat-value {
    font-size: 1.25rem;
  }
  
  .stat-label {
    font-size: 0.75rem;
  }
  
  .config-form {
    padding: var(--space-md);
  }
  
  .results-table {
    padding: 0;
    margin: 0;
  }
  
  .results-table :deep(.el-table__header th) {
    padding: var(--space-md) var(--space-sm);
    font-size: 0.75rem;
  }
  
  .results-table :deep(.el-table__body td) {
    padding: var(--space-sm);
    font-size: 0.875rem;
  }
  
  .pagination-wrapper {
    padding: var(--space-md) var(--space-md) 0;
  }
}

@media (max-width: 480px) {
  .page-title {
    font-size: 1.75rem;
    flex-direction: column;
    gap: var(--space-sm);
  }
  
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: var(--space-sm);
  }
  
  .stat-item {
    padding: var(--space-md);
  }
  
  .results-table :deep(.el-table) {
    font-size: 0.75rem;
  }
  
  .analysis-info {
    gap: 2px;
  }
  
  .analysis-item .text-sm {
    font-size: 0.625rem;
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