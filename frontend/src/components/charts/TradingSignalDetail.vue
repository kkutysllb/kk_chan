<template>
  <div class="trading-signal-detail">
    <el-drawer
      v-model="visible"
      title="交易信号详情"
      :size="600"
      direction="rtl"
    >
      <div v-if="signalData" class="signal-content">
        <!-- 信号基本信息 -->
        <div class="signal-header">
          <div class="signal-symbol">
            <h3>{{ signalData.symbol }}</h3>
            <span class="signal-name">{{ signalData.name || '股票名称' }}</span>
          </div>
          <el-tag 
            :type="getSignalType(signalData.type)"
            size="large"
          >
            {{ getSignalText(signalData.type) }}
          </el-tag>
        </div>
        
        <!-- 信号详情 -->
        <el-descriptions :column="2" border style="margin: 20px 0;">
          <el-descriptions-item label="信号类型">
            {{ getSignalText(signalData.type) }}
          </el-descriptions-item>
          <el-descriptions-item label="置信度">
            <el-progress 
              :percentage="(signalData.confidence || 0) * 100"
              :color="getConfidenceColor(signalData.confidence)"
              :show-text="false"
              style="width: 100px; margin-right: 10px;"
            />
            {{ ((signalData.confidence || 0) * 100).toFixed(1) }}%
          </el-descriptions-item>
          <el-descriptions-item label="信号价格">
            ¥{{ signalData.price?.toFixed(2) || '--' }}
          </el-descriptions-item>
          <el-descriptions-item label="当前价格">
            ¥{{ signalData.current_price?.toFixed(2) || '--' }}
          </el-descriptions-item>
          <el-descriptions-item label="时间周期">
            {{ signalData.timeframe || 'daily' }}
          </el-descriptions-item>
          <el-descriptions-item label="信号时间">
            {{ formatTime(signalData.timestamp) }}
          </el-descriptions-item>
        </el-descriptions>
        
        <!-- 信号分析 -->
        <div class="signal-analysis">
          <h4>信号分析</h4>
          <div class="analysis-content">
            <div class="analysis-item" v-if="signalData.chan_structure">
              <span class="analysis-label">缠论结构:</span>
              <span class="analysis-value">{{ signalData.chan_structure }}</span>
            </div>
            <div class="analysis-item" v-if="signalData.technical_factors">
              <span class="analysis-label">技术因子:</span>
              <span class="analysis-value">{{ signalData.technical_factors.join(', ') }}</span>
            </div>
            <div class="analysis-item" v-if="signalData.reason">
              <span class="analysis-label">信号原因:</span>
              <span class="analysis-value">{{ signalData.reason }}</span>
            </div>
          </div>
        </div>
        
        <!-- 风险提示 -->
        <div class="risk-warning" v-if="signalData.risk_level">
          <h4>风险评估</h4>
          <el-alert 
            :title="getRiskText(signalData.risk_level)"
            :type="getRiskType(signalData.risk_level)"
            :description="signalData.risk_description"
            show-icon
            :closable="false"
          />
        </div>
        
        <!-- 历史表现 -->
        <div class="performance-stats" v-if="signalData.historical_performance">
          <h4>历史表现</h4>
          <el-row :gutter="20">
            <el-col :span="8">
              <div class="stat-card">
                <div class="stat-value">{{ (signalData.historical_performance.win_rate * 100).toFixed(1) }}%</div>
                <div class="stat-label">胜率</div>
              </div>
            </el-col>
            <el-col :span="8">
              <div class="stat-card">
                <div class="stat-value positive">{{ (signalData.historical_performance.avg_return * 100).toFixed(2) }}%</div>
                <div class="stat-label">平均收益</div>
              </div>
            </el-col>
            <el-col :span="8">
              <div class="stat-card">
                <div class="stat-value">{{ signalData.historical_performance.total_signals }}</div>
                <div class="stat-label">历史信号</div>
              </div>
            </el-col>
          </el-row>
        </div>
        
        <!-- 操作建议 -->
        <div class="action-suggestions">
          <h4>操作建议</h4>
          <div class="suggestions-list">
            <div class="suggestion-item" v-if="signalData.entry_price">
              <el-icon><TrendCharts /></el-icon>
              <span>建议入场价格: ¥{{ signalData.entry_price.toFixed(2) }}</span>
            </div>
            <div class="suggestion-item" v-if="signalData.stop_loss">
              <el-icon><Warning /></el-icon>
              <span>止损价格: ¥{{ signalData.stop_loss.toFixed(2) }}</span>
            </div>
            <div class="suggestion-item" v-if="signalData.take_profit">
              <el-icon><Check /></el-icon>
              <span>止盈价格: ¥{{ signalData.take_profit.toFixed(2) }}</span>
            </div>
          </div>
        </div>
      </div>
      
      <div v-else class="empty-content">
        <el-empty description="暂无信号详情" />
      </div>
    </el-drawer>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { TrendCharts, Warning, Check } from '@element-plus/icons-vue'

interface TradingSignalDetail {
  symbol: string
  name?: string
  type: string
  confidence: number
  price: number
  current_price: number
  timeframe: string
  timestamp: string
  chan_structure?: string
  technical_factors?: string[]
  reason?: string
  risk_level?: 'low' | 'medium' | 'high'
  risk_description?: string
  historical_performance?: {
    win_rate: number
    avg_return: number
    total_signals: number
  }
  entry_price?: number
  stop_loss?: number
  take_profit?: number
}

interface Props {
  modelValue: boolean
  signalData?: TradingSignalDetail | null
}

interface Emits {
  'update:modelValue': [value: boolean]
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const visible = ref(props.modelValue)

watch(() => props.modelValue, (newValue) => {
  visible.value = newValue
})

watch(visible, (newValue) => {
  emit('update:modelValue', newValue)
})

const getSignalText = (type: string): string => {
  const texts: Record<string, string> = {
    'buy': '买入信号',
    'sell': '卖出信号',
    'hold': '持有',
    'wait': '观望'
  }
  return texts[type] || type
}

const getSignalType = (type: string): string => {
  if (type === 'buy') return 'success'
  if (type === 'sell') return 'danger'
  if (type === 'hold') return 'warning'
  return 'info'
}

const getConfidenceColor = (confidence?: number): string => {
  if (!confidence) return '#909399'
  if (confidence > 0.8) return '#67c23a'
  if (confidence > 0.6) return '#e6a23c'
  if (confidence > 0.4) return '#f56c6c'
  return '#909399'
}

const getRiskText = (level: string): string => {
  const texts: Record<string, string> = {
    'low': '低风险',
    'medium': '中等风险', 
    'high': '高风险'
  }
  return texts[level] || level
}

const getRiskType = (level: string): string => {
  if (level === 'low') return 'success'
  if (level === 'medium') return 'warning'
  if (level === 'high') return 'error'
  return 'info'
}

const formatTime = (dateStr?: string): string => {
  if (!dateStr) return '未知'
  try {
    return new Date(dateStr).toLocaleString('zh-CN')
  } catch {
    return '未知'
  }
}
</script>

<style scoped lang="scss">
.trading-signal-detail {
  .signal-content {
    .signal-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 20px;
      padding-bottom: 15px;
      border-bottom: 1px solid #ebeef5;
      
      .signal-symbol {
        h3 {
          margin: 0 0 5px 0;
          font-size: 20px;
          color: #303133;
        }
        
        .signal-name {
          font-size: 14px;
          color: #909399;
        }
      }
    }
    
    .signal-analysis,
    .risk-warning,
    .performance-stats,
    .action-suggestions {
      margin-bottom: 25px;
      
      h4 {
        margin: 0 0 15px 0;
        font-size: 16px;
        color: #303133;
      }
    }
    
    .analysis-content {
      .analysis-item {
        display: flex;
        margin-bottom: 10px;
        
        .analysis-label {
          min-width: 80px;
          font-size: 14px;
          color: #606266;
        }
        
        .analysis-value {
          font-size: 14px;
          color: #303133;
          line-height: 1.4;
        }
      }
    }
    
    .stat-card {
      text-align: center;
      padding: 15px;
      border: 1px solid #ebeef5;
      border-radius: 8px;
      
      .stat-value {
        font-size: 20px;
        font-weight: 600;
        color: #303133;
        margin-bottom: 5px;
        
        &.positive {
          color: #67c23a;
        }
        
        &.negative {
          color: #f56c6c;
        }
      }
      
      .stat-label {
        font-size: 12px;
        color: #909399;
      }
    }
    
    .suggestions-list {
      .suggestion-item {
        display: flex;
        align-items: center;
        margin-bottom: 10px;
        font-size: 14px;
        color: #606266;
        
        .el-icon {
          margin-right: 8px;
          color: #409eff;
        }
      }
    }
  }
  
  .empty-content {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 200px;
  }
}
</style>