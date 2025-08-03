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
            <div class="stat-item type1">
              <div class="stat-number">{{ allSignals.filter(s => s.point_level === 1 || s.level?.includes('type1')).length }}</div>
              <div class="stat-label">一类信号</div>
            </div>
            <div class="stat-item type2">
              <div class="stat-number">{{ allSignals.filter(s => s.point_level === 2 || s.level?.includes('type2')).length }}</div>
              <div class="stat-label">二类信号</div>
            </div>
            <div class="stat-item type3">
              <div class="stat-number">{{ allSignals.filter(s => s.point_level === 3 || s.level?.includes('type3')).length }}</div>
              <div class="stat-label">三类信号</div>
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
              style="width: 140px; margin-left: 16px;"
              @change="handleFilterChange"
            >
              <el-option label="全部" value="all" />
              <el-option label="一类买点" value="type1_buy" />
              <el-option label="二类买点" value="type2_buy" />
              <el-option label="三类买点" value="type3_buy" />
              <el-option label="一类卖点" value="type1_sell" />
              <el-option label="二类卖点" value="type2_sell" />
              <el-option label="三类卖点" value="type3_sell" />
              <el-option label="背驰信号" value="backchi" />
            </el-select>
            
            <el-select
              v-model="timeframeFilter"
              placeholder="信号确认"
              style="width: 140px; margin-left: 16px;"
              @change="handleFilterChange"
            >
              <el-option label="全部" value="all" />
              <el-option label="多级别确认" value="confirmed" />
              <el-option label="高级别确认" value="higher_confirmed" />
              <el-option label="低级别确认" value="lower_confirmed" />
              <el-option label="未确认" value="unconfirmed" />
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
                  :type="getSignalType(row) === 'buy' ? 'danger' : 'success'"
                  size="small"
                >
                  {{ getSignalType(row) === 'buy' ? '买入' : '卖出' }}
                </el-tag>
              </template>
            </el-table-column>
            
            <el-table-column prop="point_class" label="级别" width="100">
              <template #default="{ row }">
                <el-tag
                  :type="getLevelTagType(row.level || row.point_class)"
                  size="small"
                >
                  {{ row.point_class || getLevelText(row.level) }}
                </el-tag>
              </template>
            </el-table-column>
            
            <el-table-column prop="price" label="价格" width="100">
              <template #default="{ row }">
                <span 
                  class="price-value"
                  :class="{
                    'price-buy': getSignalType(row) === 'buy',
                    'price-sell': getSignalType(row) === 'sell'
                  }"
                >
                  {{ getSignalPrice(row) }}
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
                <div class="confidence-display">
                  <el-rate
                    :model-value="(row.confidence || row.reliability || 0) * 5"
                    disabled
                    size="small"
                    :colors="['#F56C6C', '#E6A23C', '#67C23A']"
                  />
                  <span class="confidence-text">
                    {{ ((row.confidence || row.reliability || 0) * 100).toFixed(0) }}%
                  </span>
                </div>
              </template>
            </el-table-column>
            
            <el-table-column prop="timestamp" label="时间" width="120">
              <template #default="{ row }">
                {{ getSignalTime(row) }}
              </template>
            </el-table-column>
            
            <el-table-column prop="confirmed" label="确认状态" width="100">
              <template #default="{ row }">
                <div class="confirmation-status">
                  <el-tag
                    v-if="row.confirmed_higher"
                    type="success"
                    size="small"
                    style="margin-right: 4px;"
                  >
                    高确认
                  </el-tag>
                  <el-tag
                    v-if="row.confirmed_lower"
                    type="warning"
                    size="small"
                  >
                    低确认
                  </el-tag>
                  <el-tag
                    v-if="!row.confirmed_higher && !row.confirmed_lower"
                    type="info"
                    size="small"
                  >
                    待确认
                  </el-tag>
                </div>
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
            
            <el-table-column label="操作" width="120">
              <template #default="{ row, $index }">
                <el-button
                  size="small"
                  type="primary"
                  round
                  @click.stop="showSignalDetail(row, $index)"
                  class="detail-button"
                >
                  <el-icon style="margin-right: 4px;"><Search /></el-icon>
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
      width="700px"
      :before-close="handleDetailClose"
      class="signal-detail-dialog"
      align-center
    >
      <div v-if="selectedSignal" class="signal-detail-content">
        <!-- 信号概要卡片 -->
        <div class="signal-summary-card">
          <div class="signal-header">
            <div class="signal-type-badge">
              <el-tag
                :type="getSignalType(selectedSignal) === 'buy' ? 'danger' : 'success'"
                size="large"
                round
              >
                <el-icon style="margin-right: 6px;">
                  <TrendCharts v-if="getSignalType(selectedSignal) === 'buy'" />
                  <TrendCharts v-else />
                </el-icon>
                {{ getSignalType(selectedSignal) === 'buy' ? '买入信号' : '卖出信号' }}
              </el-tag>
            </div>
            <div class="signal-level-badge">
              <el-tag 
                :type="getLevelTagType(selectedSignal.level || selectedSignal.point_class)"
                size="large"
                round
              >
                {{ selectedSignal.point_class || getLevelText(selectedSignal.level) }}
              </el-tag>
            </div>
          </div>
          
          <div class="signal-metrics">
            <div class="metric-item">
              <div class="metric-label">触发价格</div>
              <div 
                class="metric-value price"
                :class="{
                  'price-buy-large': getSignalType(selectedSignal) === 'buy',
                  'price-sell-large': getSignalType(selectedSignal) === 'sell'
                }"
              >
                ¥{{ getSignalPrice(selectedSignal) }}
              </div>
            </div>
            <div class="metric-item">
              <div class="metric-label">信号强度</div>
              <div class="metric-value">
                <el-progress
                  :percentage="(selectedSignal.strength * 100)"
                  :color="getStrengthColor(selectedSignal.strength)"
                  :stroke-width="8"
                  :show-text="false"
                  style="width: 100px;"
                />
                <span class="metric-percentage">{{ (selectedSignal.strength * 100).toFixed(1) }}%</span>
              </div>
            </div>
            <div class="metric-item">
              <div class="metric-label">置信度</div>
              <div class="metric-value">
                <el-rate
                  :model-value="(selectedSignal.confidence || selectedSignal.reliability || 0) * 5"
                  disabled
                  size="small"
                  :colors="['#F56C6C', '#E6A23C', '#67C23A']"
                />
                <span class="metric-percentage">{{ ((selectedSignal.confidence || selectedSignal.reliability || 0) * 100).toFixed(1) }}%</span>
              </div>
            </div>
          </div>
        </div>

        <!-- 详细信息 -->
        <div class="signal-details-grid">
          <div class="detail-section">
            <h4 class="section-title">
              <el-icon><Clock /></el-icon>
              时间信息
            </h4>
            <div class="detail-item">
              <span class="detail-label">触发时间</span>
              <span class="detail-value">{{ getSignalTime(selectedSignal) }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">时间级别</span>
              <span class="detail-value">{{ selectedSignal.timeframe || '30分钟' }}</span>
            </div>
          </div>

          <div class="detail-section">
            <h4 class="section-title">
              <el-icon><Checked /></el-icon>
              确认状态
            </h4>
            <div class="detail-item">
              <span class="detail-label">高级别确认</span>
              <el-tag 
                :type="selectedSignal.confirmed_higher ? 'success' : 'info'"
                size="small"
                round
              >
                {{ selectedSignal.confirmed_higher ? '已确认' : '待确认' }}
              </el-tag>
            </div>
            <div class="detail-item">
              <span class="detail-label">低级别确认</span>
              <el-tag 
                :type="selectedSignal.confirmed_lower ? 'success' : 'info'"
                size="small"
                round
              >
                {{ selectedSignal.confirmed_lower ? '已确认' : '待确认' }}
              </el-tag>
            </div>
          </div>

          <div class="detail-section" v-if="selectedSignal.backchi_type || selectedSignal.related_zhongshu || selectedSignal.related_seg">
            <h4 class="section-title">
              <el-icon><Connection /></el-icon>
              关联信息
            </h4>
            <div class="detail-item" v-if="selectedSignal.backchi_type">
              <span class="detail-label">背驰类型</span>
              <span class="detail-value">{{ selectedSignal.backchi_type }}</span>
            </div>
            <div class="detail-item" v-if="selectedSignal.related_zhongshu">
              <span class="detail-label">相关中枢</span>
              <span class="detail-value">{{ selectedSignal.related_zhongshu }}</span>
            </div>
            <div class="detail-item" v-if="selectedSignal.related_seg">
              <span class="detail-label">相关线段</span>
              <span class="detail-value">{{ selectedSignal.related_seg }}</span>
            </div>
          </div>

          <div class="detail-section full-width">
            <h4 class="section-title">
              <el-icon><Document /></el-icon>
              详细描述
            </h4>
            <div class="description-content">
              {{ selectedSignal.description || '暂无详细描述' }}
            </div>
          </div>
        </div>
      </div>
      
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="detailDialogVisible = false" round>
            <el-icon style="margin-right: 4px;"><Close /></el-icon>
            关闭
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { Search, Download, TrendCharts, Clock, Checked, Connection, Document, Close } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { useGlobalStore } from '@/stores/global'
import { useThemeStore } from '@/stores/theme'

const global = useGlobalStore()
const theme = useThemeStore()

// 组件状态
const signalFilter = ref('all')
const levelFilter = ref('all')
const timeframeFilter = ref('all')
const searchKeyword = ref('')
const detailDialogVisible = ref(false)
const selectedSignal = ref(null)

// 计算属性 - 基于缠论v2数据结构
const buySellingPoints = computed(() => global.buySellingPoints || [])
const backchiSignals = computed(() => global.backchiSignals || [])
const chanStatistics = computed(() => global.chanStatistics || {})

// 处理缠论v2的BuySellPoint数据结构 - 兼容新的字段映射
const allSignals = computed(() => {
  const signals = []
  
  // 处理买卖点数据 - 基于新的BuySellPoint数据结构
  buySellingPoints.value.forEach(point => {
    // 解析买卖点类型和级别 - 支持新的point_level字段
    const pointLevel = point.point_level || 1
    const pointType = point.type || (point.name?.includes('买') ? 'buy' : 'sell')
    const pointClass = pointType === 'buy' ? `${pointLevel}类买点` : `${pointLevel}类卖点`
    
    // 从kline_index获取价格和时间信息
    let price = point.value || point.price
    let timestamp = point.coord?.[0] || point.timestamp
    
    // 如果有kline_index，尝试从图表数据获取更准确的价格时间
    if (point.kline_index !== undefined && global.klineData) {
      const klineData = global.klineData
      if (klineData && klineData.length > point.kline_index) {
        const kline = klineData[point.kline_index]
        if (kline) {
          timestamp = kline.timestamp || kline[0]
          price = point.value || kline.close || kline[4]
        }
      }
    }
    
    signals.push({
      ...point,
      source: 'buy_sell_point',
      type: pointType,
      level: `type${pointLevel}_${pointType}`,
      point_class: pointClass,
      price: price,
      timestamp: timestamp,
      strength: point.strength || 0.8,
      confidence: point.confidence || point.reliability || 0.7,
      description: point.description || `${pointClass} - ${point.backchi_type || '缠论信号'}`,
      timeframe: point.timeframe || '30分钟',
      backchi_type: point.backchi_type,
      related_zhongshu: point.related_zhongshu,
      related_seg: point.related_seg,
      macd_data: point.macd_data,
      confirmed_higher: point.confirmed_higher || false,
      confirmed_lower: point.confirmed_lower || false
    })
  })
  
  // 处理背驰分析数据 - 保持兼容性
  backchiSignals.value.forEach(analysis => {
    signals.push({
      ...analysis,
      source: 'backchi_analysis',
      type: analysis.is_buy_signal ? 'buy' : 'sell',
      level: 'backchi',
      point_class: analysis.backchi_type || '背驰信号',
      price: analysis.price,
      timestamp: analysis.timestamp,
      strength: analysis.backchi_strength || 0.6,
      confidence: analysis.confidence || 0.6,
      description: `${analysis.backchi_type || '背驰'}信号 - ${analysis.description || 'MACD背驰分析'}`,
      timeframe: analysis.timeframe || '30分钟'
    })
  })
  
  return signals
})

const hasSignals = computed(() => allSignals.value.length > 0)

const buySignals = computed(() => 
  allSignals.value.filter(signal => signal.type === 'buy' || signal.signal_type === 'buy')
)

const sellSignals = computed(() => 
  allSignals.value.filter(signal => signal.type === 'sell' || signal.signal_type === 'sell')
)

const filteredSignals = computed(() => {
  let signals = allSignals.value

  // 类型筛选
  if (signalFilter.value !== 'all') {
    signals = signals.filter(signal => getSignalType(signal) === signalFilter.value)
  }

  // 级别筛选
  if (levelFilter.value !== 'all') {
    signals = signals.filter(signal => (signal.value || signal.level) === levelFilter.value)
  }

  // 确认状态筛选
  if (timeframeFilter.value !== 'all') {
    switch (timeframeFilter.value) {
      case 'confirmed':
        signals = signals.filter(signal => signal.confirmed_higher && signal.confirmed_lower)
        break
      case 'higher_confirmed':
        signals = signals.filter(signal => signal.confirmed_higher)
        break
      case 'lower_confirmed':
        signals = signals.filter(signal => signal.confirmed_lower)
        break
      case 'unconfirmed':
        signals = signals.filter(signal => !signal.confirmed_higher && !signal.confirmed_lower)
        break
    }
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
const getSignalType = (signal) => {
  return signal.type || signal.signal_type || 'unknown'
}

const getSignalPrice = (signal) => {
  // 优先使用新的价格字段
  if (signal.price !== undefined && signal.price !== null) {
    return Number(signal.price).toFixed(2)
  }
  if (signal.value !== undefined && signal.value !== null) {
    return Number(signal.value).toFixed(2)
  }
  if (signal.coord && signal.coord[1]) {
    return Number(signal.coord[1]).toFixed(2)
  }
  return '-'
}

const getSignalTime = (signal) => {
  // 优先使用新的时间字段
  if (signal.timestamp) {
    // 如果是时间戳格式，进行格式化
    if (typeof signal.timestamp === 'number') {
      return new Date(signal.timestamp).toLocaleString('zh-CN')
    }
    return signal.timestamp
  }
  if (signal.coord && signal.coord[0]) {
    return signal.coord[0]
  }
  return '-'
}

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
    'type1_buy': 'danger',      // 买入用红色
    'type2_buy': 'warning', 
    'type3_buy': 'info',
    'type1_sell': 'success',    // 卖出用绿色
    'type2_sell': 'warning',
    'type3_sell': 'info',
    'backchi': 'primary',
    'trend_backchi': 'primary',
    'range_backchi': 'warning',
    // 新增支持级别文本
    '一类买点': 'danger',      // 买入用红色
    '二类买点': 'warning',
    '三类买点': 'info',
    '一类卖点': 'success',    // 卖出用绿色
    '二类卖点': 'warning',
    '三类卖点': 'info',
    '背驰信号': 'primary',
  }
  return typeMap[level] || 'info'
}

const getLevelText = (level) => {
  const textMap = {
    'type1_buy': '一类买点',
    'type2_buy': '二类买点',
    'type3_buy': '三类买点',
    'type1_sell': '一类卖点',
    'type2_sell': '二类卖点',
    'type3_sell': '三类卖点',
    'backchi': '背驰',
    'trend_backchi': '趋势背驰',
    'range_backchi': '盘整背驰',
  }
  return textMap[level] || level || '-'
}

const getStrengthColor = (strength) => {
  if (strength >= 0.8) return '#67C23A'
  if (strength >= 0.6) return '#E6A23C'
  return '#F56C6C'
}

const getTimeframeTagType = (timeframe) => {
  const typeMap = {
    '日线': 'danger',
    '30分钟': 'warning',
    '5分钟': 'success'
  }
  return typeMap[timeframe] || 'info'
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
      类型: getSignalType(signal) === 'buy' ? '买入' : '卖出',
      级别: getLevelText(signal.value || signal.level),
      价格: getSignalPrice(signal),
      时间: getSignalTime(signal),
      强度: ((signal.strength || 0) * 100).toFixed(1) + '%',
      置信度: ((signal.confidence || 0) * 100).toFixed(1) + '%',
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
  background: var(--el-fill-color-lighter);
  border-radius: 3px;
}

.dark .trading-signals::-webkit-scrollbar-track {
  background: var(--el-fill-color-dark);
}

.trading-signals::-webkit-scrollbar-thumb {
  background: var(--el-border-color);
  border-radius: 3px;
}

.trading-signals::-webkit-scrollbar-thumb:hover {
  background: var(--el-border-color-dark);
}

.detail-button {
  font-size: 12px !important;
  padding: 6px 12px !important;
  border-radius: 20px !important;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
  border: none !important;
  color: white !important;
  font-weight: 600 !important;
  transition: all 0.3s ease !important;
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3) !important;
}

.detail-button:hover {
  transform: translateY(-2px) scale(1.05) !important;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.5) !important;
  background: linear-gradient(135deg, #5a6fd8 0%, #6a4190 100%) !important;
}

.detail-button:active {
  transform: translateY(0) scale(1) !important;
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
  background: var(--el-bg-color);
  border: 1px solid var(--el-border-color-light);
  border-radius: 16px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  transition: all 0.3s ease;
}

.dark .stats-card {
  background: var(--el-bg-color);
  border: 1px solid var(--el-border-color-light);
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.6);
}

.stats-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
}

.signal-stats {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
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
  background: linear-gradient(135deg, #F56C6C 0%, #f78989 100%);
  color: white;
  box-shadow: 0 4px 20px rgba(245, 108, 108, 0.3);
}

.stat-item.sell {
  background: linear-gradient(135deg, #67C23A 0%, #85ce61 100%);
  color: white;
  box-shadow: 0 4px 20px rgba(103, 194, 58, 0.3);
}

.stat-item.type1 {
  background: linear-gradient(135deg, #F56C6C 0%, #f78989 100%);
  color: white;
  box-shadow: 0 4px 20px rgba(245, 108, 108, 0.3);
}

.stat-item.type2 {
  background: linear-gradient(135deg, #E6A23C 0%, #eebe77 100%);
  color: white;
  box-shadow: 0 4px 20px rgba(230, 162, 60, 0.3);
}

.stat-item.type3 {
  background: linear-gradient(135deg, #909399 0%, #b1b3b8 100%);
  color: white;
  box-shadow: 0 4px 20px rgba(144, 147, 153, 0.3);
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
  background: var(--el-bg-color);
  border: 1px solid var(--el-border-color-light);
  border-radius: 16px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  transition: all 0.3s ease;
}

.dark .filter-card {
  background: var(--el-bg-color);
  border: 1px solid var(--el-border-color-light);
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.6);
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
  background: var(--el-bg-color);
  border: 1px solid var(--el-border-color-light);
  border-radius: 16px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  transition: all 0.3s ease;
}

.dark .signals-table-card {
  background: var(--el-bg-color);
  border: 1px solid var(--el-border-color-light);
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.6);
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

.price-value.price-buy {
  background: linear-gradient(135deg, #F56C6C 0%, #f78989 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.price-value.price-sell {
  background: linear-gradient(135deg, #67C23A 0%, #85ce61 100%);
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

.confidence-display {
  display: flex;
  align-items: center;
  gap: 8px;
}

.confidence-text {
  font-size: 12px;
  color: var(--el-text-color-secondary);
  font-weight: 500;
}

.confirmation-status {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.confirmation-status .el-tag {
  font-size: 10px;
  padding: 2px 6px;
}

.signal-detail-content {
  padding: 0;
}

.signal-summary-card {
  background: linear-gradient(135deg, 
    var(--el-fill-color-lighter) 0%, 
    var(--el-fill-color-light) 100%);
  border-radius: 16px;
  padding: 24px;
  margin-bottom: 24px;
  border: 1px solid var(--el-border-color-lighter);
}

.dark .signal-summary-card {
  background: linear-gradient(135deg, 
    var(--el-fill-color-dark) 0%, 
    var(--el-fill-color) 100%);
  border: 1px solid var(--el-border-color);
}

.signal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.signal-type-badge,
.signal-level-badge {
  :deep(.el-tag) {
    padding: 8px 16px;
    font-size: 14px;
    font-weight: 600;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  }
}

.signal-metrics {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
}

.metric-item {
  text-align: center;
}

.metric-label {
  font-size: 12px;
  color: var(--el-text-color-secondary);
  margin-bottom: 8px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  font-weight: 500;
}

.metric-value {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.metric-value.price {
  font-size: 24px;
  font-weight: 700;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.metric-value.price.price-buy-large {
  background: linear-gradient(135deg, #F56C6C 0%, #f78989 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.metric-value.price.price-sell-large {
  background: linear-gradient(135deg, #67C23A 0%, #85ce61 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.metric-percentage {
  font-size: 14px;
  font-weight: 600;
  color: var(--el-text-color-primary);
}

.signal-details-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
}

.detail-section {
  background: var(--el-bg-color-overlay);
  border: 1px solid var(--el-border-color-lighter);
  border-radius: 12px;
  padding: 20px;
  transition: all 0.3s ease;
}

.dark .detail-section {
  background: var(--el-fill-color-darker);
  border: 1px solid var(--el-border-color);
}

.detail-section:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.dark .detail-section:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}

.detail-section.full-width {
  grid-column: 1 / -1;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0 0 16px 0;
  font-size: 16px;
  font-weight: 600;
  color: var(--el-text-color-primary);
  
  .el-icon {
    color: var(--el-color-primary);
  }
}

.detail-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid var(--el-border-color-lighter);
}

.dark .detail-item {
  border-bottom: 1px solid var(--el-border-color);
}

.detail-item:last-child {
  border-bottom: none;
}

.detail-label {
  font-size: 14px;
  color: var(--el-text-color-secondary);
  font-weight: 500;
}

.detail-value {
  font-size: 14px;
  color: var(--el-text-color-primary);
  font-weight: 600;
}

.description-content {
  background: var(--el-fill-color-light);
  border: 1px solid var(--el-border-color-lighter);
  border-radius: 8px;
  padding: 16px;
  font-size: 14px;
  line-height: 1.6;
  color: var(--el-text-color-regular);
  min-height: 60px;
}

.dark .description-content {
  background: var(--el-fill-color);
  border: 1px solid var(--el-border-color);
}

.dialog-footer {
  text-align: center;
  padding: 16px 0;
  
  .el-button {
    padding: 10px 24px;
    font-weight: 600;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border: none;
    color: white;
    transition: all 0.3s ease;
  }
  
  .el-button:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
    background: linear-gradient(135deg, #5a6fd8 0%, #6a4190 100%);
  }
}

:deep(.el-card__header) {
  background: var(--el-fill-color-light);
  border-bottom: 1px solid var(--el-border-color-light);
  padding: 20px 24px;
  border-radius: 16px 16px 0 0;
}

.dark :deep(.el-card__header) {
  background: var(--el-fill-color-dark);
  border-bottom: 1px solid var(--el-border-color);
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
  background: var(--el-fill-color-lighter);
  color: var(--el-text-color-primary);
  font-weight: 600;
  border-bottom: 2px solid var(--el-border-color-light);
}

.dark :deep(.el-table th) {
  background: var(--el-fill-color-dark);
  border-bottom: 2px solid var(--el-border-color);
}

:deep(.el-table td) {
  border-bottom: 1px solid var(--el-border-color-lighter);
}

.dark :deep(.el-table td) {
  border-bottom: 1px solid var(--el-border-color);
}

:deep(.el-table tr:hover) {
  background: var(--el-fill-color-light);
}

.dark :deep(.el-table tr:hover) {
  background: var(--el-fill-color);
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

.signal-detail-dialog :deep(.el-dialog) {
  border-radius: 20px;
  overflow: hidden;
  background: var(--el-bg-color);
  border: 1px solid var(--el-border-color-light);
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
}

.dark .signal-detail-dialog :deep(.el-dialog) {
  background: var(--el-bg-color);
  border: 1px solid var(--el-border-color);
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.7);
}

.signal-detail-dialog :deep(.el-dialog__header) {
  background: linear-gradient(135deg, 
    var(--el-fill-color-light) 0%, 
    var(--el-fill-color-lighter) 100%);
  border-bottom: 1px solid var(--el-border-color-light);
  padding: 24px 32px;
  
  .el-dialog__title {
    font-size: 20px;
    font-weight: 700;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }
}

.dark .signal-detail-dialog :deep(.el-dialog__header) {
  background: linear-gradient(135deg, 
    var(--el-fill-color-dark) 0%, 
    var(--el-fill-color) 100%);
  border-bottom: 1px solid var(--el-border-color);
}

.signal-detail-dialog :deep(.el-dialog__body) {
  background: var(--el-bg-color);
  padding: 32px;
  max-height: 70vh;
  overflow-y: auto;
}

.signal-detail-dialog :deep(.el-dialog__footer) {
  background: var(--el-fill-color-light);
  border-top: 1px solid var(--el-border-color-light);
  padding: 20px 32px;
}

.dark .signal-detail-dialog :deep(.el-dialog__footer) {
  background: var(--el-fill-color-dark);
  border-top: 1px solid var(--el-border-color);
}

.signal-detail-dialog :deep(.el-dialog__close) {
  font-size: 20px;
  color: var(--el-text-color-secondary);
  transition: all 0.3s ease;
}

.signal-detail-dialog :deep(.el-dialog__close:hover) {
  color: var(--el-color-primary);
  transform: scale(1.1);
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
  
  .signal-detail-dialog :deep(.el-dialog) {
    width: 95vw !important;
    margin: 20px auto !important;
  }
  
  .signal-detail-dialog :deep(.el-dialog__header) {
    padding: 20px 24px;
    
    .el-dialog__title {
      font-size: 18px;
    }
  }
  
  .signal-detail-dialog :deep(.el-dialog__body) {
    padding: 24px;
    max-height: 60vh;
  }
  
  .signal-summary-card {
    padding: 20px;
    margin-bottom: 20px;
  }
  
  .signal-metrics {
    grid-template-columns: 1fr;
    gap: 16px;
  }
  
  .signal-details-grid {
    grid-template-columns: 1fr;
    gap: 16px;
  }
  
  .section-title {
    font-size: 15px;
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
  
  .signal-detail-dialog :deep(.el-dialog) {
    width: 100vw !important;
    height: 100vh !important;
    margin: 0 !important;
    border-radius: 0 !important;
  }
  
  .signal-detail-dialog :deep(.el-dialog__header) {
    padding: 16px 20px;
    
    .el-dialog__title {
      font-size: 16px;
    }
  }
  
  .signal-detail-dialog :deep(.el-dialog__body) {
    padding: 20px;
    max-height: calc(100vh - 160px);
  }
  
  .signal-summary-card {
    padding: 16px;
    margin-bottom: 16px;
  }
  
  .signal-header {
    flex-direction: column;
    gap: 12px;
    align-items: stretch;
  }
  
  .metric-value.price {
    font-size: 20px;
  }
  
  .detail-section {
    padding: 16px;
  }
  
  .section-title {
    font-size: 14px;
  }
  
  .detail-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 4px;
  }
  
  .description-content {
    padding: 12px;
    font-size: 13px;
  }
}
</style>