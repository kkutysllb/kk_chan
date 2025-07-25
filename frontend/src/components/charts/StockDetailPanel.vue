<template>
  <div class="stock-detail-panel">
    <el-drawer
      v-model="visible"
      title="股票详情"
      :size="500"
      direction="rtl"
    >
      <div v-if="stockData" class="stock-content">
        <!-- 股票基本信息 -->
        <div class="stock-header">
          <div class="stock-info">
            <h3>{{ stockData.symbol }}</h3>
            <span class="stock-name">{{ stockData.name || '股票名称' }}</span>
          </div>
          <div class="stock-price">
            <div class="current-price">¥{{ stockData.current_price?.toFixed(2) || '--' }}</div>
            <div 
              class="price-change"
              :class="{
                'positive': (stockData.change_pct || 0) > 0,
                'negative': (stockData.change_pct || 0) < 0,
                'neutral': (stockData.change_pct || 0) === 0
              }"
            >
              {{ (stockData.change_pct || 0) > 0 ? '+' : '' }}{{ ((stockData.change_pct || 0) * 100).toFixed(2) }}%
            </div>
          </div>
        </div>
        
        <!-- 股票数据 -->
        <el-descriptions :column="2" border style="margin: 20px 0;">
          <el-descriptions-item label="开盘价">
            ¥{{ stockData.open?.toFixed(2) || '--' }}
          </el-descriptions-item>
          <el-descriptions-item label="最高价">
            ¥{{ stockData.high?.toFixed(2) || '--' }}
          </el-descriptions-item>
          <el-descriptions-item label="最低价">
            ¥{{ stockData.low?.toFixed(2) || '--' }}
          </el-descriptions-item>
          <el-descriptions-item label="昨收价">
            ¥{{ stockData.prev_close?.toFixed(2) || '--' }}
          </el-descriptions-item>
          <el-descriptions-item label="成交量">
            {{ formatVolume(stockData.volume || 0) }}
          </el-descriptions-item>
          <el-descriptions-item label="成交额">
            {{ formatAmount(stockData.amount || 0) }}
          </el-descriptions-item>
          <el-descriptions-item label="换手率">
            {{ ((stockData.turnover_rate || 0) * 100).toFixed(2) }}%
          </el-descriptions-item>
          <el-descriptions-item label="市盈率">
            {{ stockData.pe_ratio?.toFixed(2) || '--' }}
          </el-descriptions-item>
        </el-descriptions>
        
        <!-- 缠论信号 -->
        <div class="chan-signals" v-if="stockData.chan_analysis">
          <h4>缠论分析</h4>
          <div class="signal-tags">
            <el-tag 
              v-if="stockData.chan_analysis.trend"
              :type="getTrendType(stockData.chan_analysis.trend)"
              style="margin-right: 10px;"
            >
              {{ getTrendText(stockData.chan_analysis.trend) }}
            </el-tag>
            <el-tag 
              v-if="stockData.chan_analysis.signal"
              :type="getSignalType(stockData.chan_analysis.signal)"
            >
              {{ getSignalText(stockData.chan_analysis.signal) }}
            </el-tag>
          </div>
          
          <div class="chan-metrics" style="margin-top: 15px;">
            <div class="metric-item" v-if="stockData.chan_analysis.strength">
              <span class="metric-label">缠论强度:</span>
              <el-progress 
                :percentage="stockData.chan_analysis.strength * 100"
                :color="getStrengthColor(stockData.chan_analysis.strength)"
                style="width: 100px;"
              />
            </div>
            <div class="metric-item" v-if="stockData.chan_analysis.confidence">
              <span class="metric-label">信号置信度:</span>
              <span class="metric-value">{{ (stockData.chan_analysis.confidence * 100).toFixed(1) }}%</span>
            </div>
          </div>
        </div>
        
        <!-- 行业信息 -->
        <div class="sector-info" v-if="stockData.sector">
          <h4>行业信息</h4>
          <div class="sector-tags">
            <el-tag type="info" style="margin-right: 10px;">{{ stockData.sector }}</el-tag>
            <el-tag v-if="stockData.industry" type="info">{{ stockData.industry }}</el-tag>
          </div>
          
          <div class="sector-performance" v-if="stockData.sector_performance">
            <div class="performance-item">
              <span class="performance-label">板块表现:</span>
              <span 
                class="performance-value"
                :class="{
                  'positive': stockData.sector_performance > 0,
                  'negative': stockData.sector_performance < 0
                }"
              >
                {{ stockData.sector_performance > 0 ? '+' : '' }}{{ (stockData.sector_performance * 100).toFixed(2) }}%
              </span>
            </div>
          </div>
        </div>
        
        <!-- 快捷操作 -->
        <div class="quick-actions">
          <h4>快捷操作</h4>
          <el-button-group>
            <el-button size="small" @click="addToWatchlist">
              <el-icon><Star /></el-icon>
              加入自选
            </el-button>
            <el-button size="small" @click="viewAnalysis">
              <el-icon><TrendCharts /></el-icon>
              查看分析
            </el-button>
            <el-button size="small" @click="viewChart">
              <el-icon><DataLine /></el-icon>
              查看K线
            </el-button>
          </el-button-group>
        </div>
      </div>
      
      <div v-else class="empty-content">
        <el-empty description="暂无股票详情" />
      </div>
    </el-drawer>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { Star, TrendCharts, DataLine } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

interface StockDetail {
  symbol: string
  name?: string
  current_price?: number
  change_pct?: number
  open?: number
  high?: number
  low?: number
  prev_close?: number
  volume?: number
  amount?: number
  turnover_rate?: number
  pe_ratio?: number
  sector?: string
  industry?: string
  sector_performance?: number
  chan_analysis?: {
    trend: string
    signal: string
    strength: number
    confidence: number
  }
}

interface Props {
  modelValue: boolean
  stockData?: StockDetail | null
}

interface Emits {
  'update:modelValue': [value: boolean]
  'add-to-watchlist': [symbol: string]
  'view-analysis': [symbol: string]
  'view-chart': [symbol: string]
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

const formatVolume = (volume: number): string => {
  if (volume >= 100000000) {
    return (volume / 100000000).toFixed(2) + '亿手'
  } else if (volume >= 10000) {
    return (volume / 10000).toFixed(2) + '万手'
  }
  return volume.toString() + '手'
}

const formatAmount = (amount: number): string => {
  if (amount >= 100000000) {
    return (amount / 100000000).toFixed(2) + '亿元'
  } else if (amount >= 10000) {
    return (amount / 10000).toFixed(2) + '万元'
  }
  return amount.toString() + '元'
}

const getTrendText = (trend: string): string => {
  const texts: Record<string, string> = {
    'up': '上涨趋势',
    'down': '下跌趋势',
    'sideways': '横盘整理'
  }
  return texts[trend] || trend
}

const getTrendType = (trend: string): string => {
  if (trend === 'up') return 'success'
  if (trend === 'down') return 'danger'
  return 'warning'
}

const getSignalText = (signal: string): string => {
  const texts: Record<string, string> = {
    'buy': '买入信号',
    'sell': '卖出信号',
    'hold': '持有',
    'wait': '观望'
  }
  return texts[signal] || signal
}

const getSignalType = (signal: string): string => {
  if (signal === 'buy') return 'success'
  if (signal === 'sell') return 'danger'
  if (signal === 'hold') return 'warning'
  return 'info'
}

const getStrengthColor = (strength: number): string => {
  if (strength > 0.8) return '#67c23a'
  if (strength > 0.6) return '#e6a23c'
  if (strength > 0.4) return '#f56c6c'
  return '#909399'
}

const addToWatchlist = () => {
  if (props.stockData?.symbol) {
    emit('add-to-watchlist', props.stockData.symbol)
    ElMessage.success('已加入自选股列表')
  }
}

const viewAnalysis = () => {
  if (props.stockData?.symbol) {
    emit('view-analysis', props.stockData.symbol)
  }
}

const viewChart = () => {
  if (props.stockData?.symbol) {
    emit('view-chart', props.stockData.symbol)
  }
}
</script>

<style scoped lang="scss">
.stock-detail-panel {
  .stock-content {
    .stock-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 20px;
      padding-bottom: 15px;
      border-bottom: 1px solid #ebeef5;
      
      .stock-info {
        h3 {
          margin: 0 0 5px 0;
          font-size: 20px;
          color: #303133;
        }
        
        .stock-name {
          font-size: 14px;
          color: #909399;
        }
      }
      
      .stock-price {
        text-align: right;
        
        .current-price {
          font-size: 24px;
          font-weight: 600;
          color: #303133;
          margin-bottom: 5px;
        }
        
        .price-change {
          font-size: 16px;
          font-weight: 500;
          
          &.positive {
            color: #67c23a;
          }
          
          &.negative {
            color: #f56c6c;
          }
          
          &.neutral {
            color: #909399;
          }
        }
      }
    }
    
    .chan-signals,
    .sector-info,
    .quick-actions {
      margin-bottom: 25px;
      
      h4 {
        margin: 0 0 15px 0;
        font-size: 16px;
        color: #303133;
      }
    }
    
    .chan-metrics {
      .metric-item {
        display: flex;
        align-items: center;
        margin-bottom: 10px;
        
        .metric-label {
          min-width: 80px;
          font-size: 14px;
          color: #606266;
          margin-right: 10px;
        }
        
        .metric-value {
          font-size: 14px;
          font-weight: 500;
          color: #303133;
        }
      }
    }
    
    .sector-performance {
      margin-top: 15px;
      
      .performance-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        
        .performance-label {
          font-size: 14px;
          color: #606266;
        }
        
        .performance-value {
          font-size: 14px;
          font-weight: 600;
          
          &.positive {
            color: #67c23a;
          }
          
          &.negative {
            color: #f56c6c;
          }
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