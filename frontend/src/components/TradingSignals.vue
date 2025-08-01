<template>
  <div class="trading-signals">
    <div class="signals-container">
      <!-- 无数据状态 -->
      <div v-if="!hasSignals" class="empty-state">
        <el-empty description="暂无交易信号" :image-size="120">
          <el-button type="primary" @click="$emit('analyze')">
            开始分析
          </el-button>
        </el-empty>
      </div>

      <!-- 信号列表 -->
      <div v-else class="signals-content">
        <!-- 信号统计 -->
        <el-card class="stats-card" shadow="hover">
          <template #header>
            <span class="card-title">信号统计</span>
          </template>
          <div class="signal-stats">
            <div class="stat-item buy">
              <div class="stat-number">{{ buySignals.length }}</div>
              <div class="stat-label">买入信号</div>
            </div>
            <div class="stat-item sell">
              <div class="stat-number">{{ sellSignals.length }}</div>
              <div class="stat-label">卖出信号</div>
            </div>
            <div class="stat-item total">
              <div class="stat-number">{{ allSignals.length }}</div>
              <div class="stat-label">总信号数</div>
            </div>
          </div>
        </el-card>

        <!-- 信号筛选 -->
        <el-card class="filter-card" shadow="hover">
          <template #header>
            <span class="card-title">信号筛选</span>
          </template>
          <div class="filter-controls">
            <el-radio-group v-model="signalFilter" @change="handleFilterChange">
              <el-radio-button value="all">全部</el-radio-button>
              <el-radio-button value="buy">买入</el-radio-button>
              <el-radio-button value="sell">卖出</el-radio-button>
            </el-radio-group>
            
            <el-select
              v-model="levelFilter"
              placeholder="信号级别"
              style="width: 120px; margin-left: 16px;"
              @change="handleFilterChange"
            >
              <el-option label="全部" value="all" />
              <el-option label="一类" value="1buy" />
              <el-option label="二类" value="2buy" />
              <el-option label="三类" value="3buy" />
            </el-select>
            
            <el-input
              v-model="searchKeyword"
              placeholder="搜索信号描述"
              style="width: 200px; margin-left: 16px;"
              clearable
              @input="handleFilterChange"
            >
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
            </el-input>
          </div>
        </el-card>

        <!-- 信号表格 -->
        <el-card class="signals-table-card" shadow="hover">
          <template #header>
            <div class="table-header">
              <span class="card-title">交易信号列表</span>
              <div class="table-actions">
                <el-button
                  size="small"
                  @click="exportSignals"
                  :icon="Download"
                >
                  导出
                </el-button>
              </div>
            </div>
          </template>
          
          <el-table
            :data="filteredSignals"
            size="small"
            stripe
            empty-text="暂无符合条件的信号"
            @row-click="handleRowClick"
            class="signals-table"
          >
            <el-table-column type="index" label="序号" width="60" />
            
            <el-table-column prop="type" label="类型" width="80">
              <template #default="{ row }">
                <el-tag
                  :type="row.type === 'buy' ? 'success' : 'danger'"
                  size="small"
                >
                  {{ row.type === 'buy' ? '买入' : '卖出' }}
                </el-tag>
              </template>
            </el-table-column>
            
            <el-table-column prop="value" label="级别" width="80">
              <template #default="{ row }">
                <el-tag
                  :type="getLevelTagType(row.value)"
                  size="small"
                >
                  {{ getLevelText(row.value) }}
                </el-tag>
              </template>
            </el-table-column>
            
            <el-table-column prop="coord" label="价格" width="100">
              <template #default="{ row }">
                <span class="price-value">
                  {{ row.coord?.[1]?.toFixed(2) || '-' }}
                </span>
              </template>
            </el-table-column>
            
            <el-table-column prop="strength" label="强度" width="80">
              <template #default="{ row }">
                <el-progress
                  :percentage="(row.strength * 100).toFixed(0)"
                  :color="getStrengthColor(row.strength)"
                  :stroke-width="6"
                  :show-text="false"
                />
                <span class="strength-text">
                  {{ (row.strength * 100).toFixed(0) }}%
                </span>
              </template>
            </el-table-column>
            
            <el-table-column prop="confidence" label="置信度" width="100">
              <template #default="{ row }">
                <el-rate
                  :model-value="row.confidence * 5"
                  disabled
                  size="small"
                  :colors="['#F56C6C', '#E6A23C', '#67C23A']"
                />
              </template>
            </el-table-column>
            
            <el-table-column prop="coord" label="时间" width="120">
              <template #default="{ row }">
                {{ row.coord?.[0] || '-' }}
              </template>
            </el-table-column>
            
            <el-table-column prop="description" label="描述" min-width="200">
              <template #default="{ row }">
                <el-tooltip
                  :content="row.description"
                  placement="top"
                  :disabled="!row.description || row.description.length < 30"
                >
                  <span class="description-text">
                    {{ row.description || '-' }}
                  </span>
                </el-tooltip>
              </template>
            </el-table-column>
            
            <el-table-column label="操作" width="100">
              <template #default="{ row, $index }">
                <el-button
                  size="small"
                  type="primary"
                  link
                  @click.stop="showSignalDetail(row, $index)"
                >
                  详情
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </div>
    </div>

    <!-- 信号详情弹窗 -->
    <el-dialog
      v-model="detailDialogVisible"
      title="信号详情"
      width="500px"
      :before-close="handleDetailClose"
    >
      <div v-if="selectedSignal" class="signal-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="信号类型">
            <el-tag
              :type="selectedSignal.type === 'buy' ? 'success' : 'danger'"
            >
              {{ selectedSignal.type === 'buy' ? '买入信号' : '卖出信号' }}
            </el-tag>
          </el-descriptions-item>
          
          <el-descriptions-item label="信号级别">
            <el-tag :type="getLevelTagType(selectedSignal.value)">
              {{ getLevelText(selectedSignal.value) }}
            </el-tag>
          </el-descriptions-item>
          
          <el-descriptions-item label="触发价格">
            {{ selectedSignal.coord?.[1]?.toFixed(2) || '-' }}
          </el-descriptions-item>
          
          <el-descriptions-item label="触发时间">
            {{ selectedSignal.coord?.[0] || '-' }}
          </el-descriptions-item>
          
          <el-descriptions-item label="信号强度">
            {{ (selectedSignal.strength * 100).toFixed(1) }}%
          </el-descriptions-item>
          
          <el-descriptions-item label="置信度">
            {{ (selectedSignal.confidence * 100).toFixed(1) }}%
          </el-descriptions-item>
          
          <el-descriptions-item label="详细描述" :span="2">
            {{ selectedSignal.description || '暂无描述' }}
          </el-descriptions-item>
        </el-descriptions>
      </div>
      
      <template #footer>
        <el-button @click="detailDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { Search, Download } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { useGlobalStore } from '@/stores/global'

const global = useGlobalStore()

// 组件状态
const signalFilter = ref('all')
const levelFilter = ref('all')
const searchKeyword = ref('')
const detailDialogVisible = ref(false)
const selectedSignal = ref(null)

// 计算属性
const allSignals = computed(() => global.tradingSignals || [])
const hasSignals = computed(() => allSignals.value.length > 0)

const buySignals = computed(() => 
  allSignals.value.filter(signal => signal.type === 'buy')
)

const sellSignals = computed(() => 
  allSignals.value.filter(signal => signal.type === 'sell')
)

const filteredSignals = computed(() => {
  let signals = allSignals.value

  // 类型筛选
  if (signalFilter.value !== 'all') {
    signals = signals.filter(signal => signal.type === signalFilter.value)
  }

  // 级别筛选
  if (levelFilter.value !== 'all') {
    signals = signals.filter(signal => signal.value === levelFilter.value)
  }

  // 关键词搜索
  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase()
    signals = signals.filter(signal => 
      (signal.description || '').toLowerCase().includes(keyword)
    )
  }

  return signals
})

// 方法
const handleFilterChange = () => {
  // 筛选变化时的处理逻辑
  console.log('筛选条件变化:', {
    signalFilter: signalFilter.value,
    levelFilter: levelFilter.value,
    searchKeyword: searchKeyword.value,
  })
}

const getLevelTagType = (level) => {
  const typeMap = {
    '1buy': 'success',
    '2buy': 'warning', 
    '3buy': 'info',
    '1sell': 'success',
    '2sell': 'warning',
    '3sell': 'info',
  }
  return typeMap[level] || 'info'
}

const getLevelText = (level) => {
  const textMap = {
    '1buy': '一类买',
    '2buy': '二类买',
    '3buy': '三类买',
    '1sell': '一类卖',
    '2sell': '二类卖',
    '3sell': '三类卖',
  }
  return textMap[level] || level || '-'
}

const getStrengthColor = (strength) => {
  if (strength >= 0.8) return '#67C23A'
  if (strength >= 0.6) return '#E6A23C'
  return '#F56C6C'
}

const handleRowClick = (row) => {
  console.log('点击信号行:', row)
}

const showSignalDetail = (signal, index) => {
  selectedSignal.value = signal
  detailDialogVisible.value = true
}

const handleDetailClose = () => {
  detailDialogVisible.value = false
  selectedSignal.value = null
}

const exportSignals = () => {
  try {
    const data = filteredSignals.value.map(signal => ({
      类型: signal.type === 'buy' ? '买入' : '卖出',
      级别: getLevelText(signal.value),
      价格: signal.coord?.[1]?.toFixed(2) || '-',
      时间: signal.coord?.[0] || '-',
      强度: (signal.strength * 100).toFixed(1) + '%',
      置信度: (signal.confidence * 100).toFixed(1) + '%',
      描述: signal.description || '-',
    }))

    const csvContent = [
      Object.keys(data[0]).join(','),
      ...data.map(row => Object.values(row).join(','))
    ].join('\n')

    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
    const link = document.createElement('a')
    link.href = URL.createObjectURL(blob)
    link.download = `trading_signals_${Date.now()}.csv`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)

    ElMessage.success('信号数据导出成功')
  } catch (error) {
    console.error('导出失败:', error)
    ElMessage.error('导出失败')
  }
}

// 发射事件
defineEmits(['analyze'])
</script>

<style scoped>
.trading-signals {
  height: 100%;
  overflow-y: auto;
  background: transparent;
}

.trading-signals::-webkit-scrollbar {
  width: 6px;
}

.trading-signals::-webkit-scrollbar-track {
  background: rgba(0, 0, 0, 0.05);
  border-radius: 3px;
}

.trading-signals::-webkit-scrollbar-thumb {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 3px;
}

.trading-signals::-webkit-scrollbar-thumb:hover {
  background: linear-gradient(135deg, #5a6fd8 0%, #6a4190 100%);
}

.signals-container {
  height: 100%;
  background: transparent;
}

.empty-state {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.signals-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
  padding: 24px 0;
}

@keyframes slideInRight {
  from {
    opacity: 0;
    transform: translateX(30px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

.signals-content > * {
  animation: slideInRight 0.4s ease;
}

.signals-content > *:nth-child(1) { animation-delay: 0.1s; }
.signals-content > *:nth-child(2) { animation-delay: 0.2s; }
.signals-content > *:nth-child(3) { animation-delay: 0.3s; }

.card-title {
  font-weight: 600;
  color: var(--el-text-color-primary);
  font-size: 16px;
}

.stats-card {
  flex-shrink: 0;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  transition: all 0.3s ease;
}

.dark .stats-card {
  background: rgba(44, 62, 80, 0.95);
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
}

.stats-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
}

.signal-stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}

.stat-item {
  text-align: center;
  padding: 20px;
  border-radius: 12px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
  border: 2px solid transparent;
}

.stat-item::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
  transition: left 0.6s ease;
}

.stat-item.buy {
  background: linear-gradient(135deg, #67C23A 0%, #85ce61 100%);
  color: white;
  box-shadow: 0 4px 20px rgba(103, 194, 58, 0.3);
}

.stat-item.sell {
  background: linear-gradient(135deg, #F56C6C 0%, #f78989 100%);
  color: white;
  box-shadow: 0 4px 20px rgba(245, 108, 108, 0.3);
}

.stat-item.total {
  background: linear-gradient(135deg, #409EFF 0%, #66b1ff 100%);
  color: white;
  box-shadow: 0 4px 20px rgba(64, 158, 255, 0.3);
}

.stat-item:hover {
  transform: translateY(-4px) scale(1.02);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.2);
}

.stat-item:hover::before {
  left: 100%;
}

.stat-number {
  font-size: 32px;
  font-weight: 700;
  margin-bottom: 8px;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.stat-label {
  font-size: 14px;
  opacity: 0.95;
  font-weight: 500;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

.filter-card {
  flex-shrink: 0;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  transition: all 0.3s ease;
}

.dark .filter-card {
  background: rgba(44, 62, 80, 0.95);
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
}

.filter-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
}

.filter-controls {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 16px;
  padding: 4px 0;
}

.signals-table-card {
  flex: 1;
  min-height: 0;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  transition: all 0.3s ease;
}

.dark .signals-table-card {
  background: rgba(44, 62, 80, 0.95);
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
}

.signals-table-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.signals-table {
  height: 100%;
  border-radius: 12px;
  overflow: hidden;
}

.price-value {
  font-weight: 600;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.strength-text {
  margin-left: 8px;
  font-size: 12px;
  color: var(--el-text-color-secondary);
  font-weight: 500;
}

.description-text {
  display: block;
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-weight: 500;
  color: var(--el-text-color-regular);
}

.signal-detail {
  .el-descriptions {
    :deep(.el-descriptions__label) {
      font-weight: 600;
      color: var(--el-text-color-primary);
    }
    
    :deep(.el-descriptions__content) {
      font-weight: 500;
    }
  }
}

:deep(.el-card__header) {
  background: rgba(102, 126, 234, 0.05);
  border-bottom: 1px solid rgba(102, 126, 234, 0.1);
  padding: 20px 24px;
  border-radius: 16px 16px 0 0;
}

:deep(.el-card__body) {
  padding: 24px;
  background: transparent;
}

:deep(.el-table) {
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

:deep(.el-table th) {
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  color: var(--el-text-color-primary);
  font-weight: 600;
  border-bottom: 2px solid rgba(102, 126, 234, 0.1);
}

:deep(.el-table td) {
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
}

:deep(.el-table tr:hover) {
  background: rgba(102, 126, 234, 0.05);
}

:deep(.el-tag) {
  border-radius: 8px;
  font-weight: 500;
  padding: 4px 12px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

:deep(.el-radio-button__inner) {
  padding: 12px 20px;
  border-radius: 12px;
  font-weight: 500;
  transition: all 0.3s ease;
  border: 2px solid var(--el-border-color-light);
  background: var(--el-bg-color);
}

:deep(.el-radio-button__original-radio:checked + .el-radio-button__inner) {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-color: transparent;
  color: white;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

:deep(.el-radio-button__inner:hover) {
  border-color: var(--el-color-primary);
  transform: translateY(-2px);
}

:deep(.el-input__wrapper) {
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

:deep(.el-input__wrapper:hover) {
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.2);
}

:deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

:deep(.el-select .el-input) {
  border-radius: 12px;
}

:deep(.el-button--primary) {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  border-radius: 12px;
  font-weight: 600;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

:deep(.el-button--primary::before) {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  transition: left 0.5s ease;
}

:deep(.el-button--primary:hover) {
  transform: translateY(-2px);
  box-shadow: 0 8px 16px rgba(102, 126, 234, 0.4);
}

:deep(.el-button--primary:hover::before) {
  left: 100%;
}

:deep(.el-dialog) {
  border-radius: 16px;
  overflow: hidden;
  backdrop-filter: blur(20px);
  background: rgba(255, 255, 255, 0.95);
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.2);
}

:deep(.el-dialog__header) {
  background: rgba(102, 126, 234, 0.05);
  border-bottom: 1px solid rgba(102, 126, 234, 0.1);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .signals-content {
    padding: 16px 0;
    gap: 16px;
  }
  
  .signal-stats {
    grid-template-columns: 1fr;
    gap: 12px;
  }
  
  .stat-item {
    padding: 16px;
  }
  
  .stat-number {
    font-size: 24px;
  }
  
  .filter-controls {
    flex-direction: column;
    align-items: stretch;
    gap: 12px;
  }
  
  .filter-controls > * {
    width: 100%;
  }
  
  .table-header {
    flex-direction: column;
    gap: 12px;
    align-items: stretch;
  }
  
  :deep(.el-radio-button__inner) {
    padding: 10px 16px;
  }
}

@media (max-width: 480px) {
  .signals-content {
    padding: 12px 0;
    gap: 12px;
  }
  
  .stat-number {
    font-size: 20px;
  }
  
  .stat-label {
    font-size: 13px;
  }
}
</style>