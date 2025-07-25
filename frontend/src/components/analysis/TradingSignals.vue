<template>
  <div class="trading-signals">
    <el-card class="signals-card">
      <template #header>
        <div class="card-header">
          <span class="title">交易信号</span>
          <div class="header-controls">
            <el-select v-model="selectedTimeframe" size="small" style="width: 100px; margin-right: 10px;">
              <el-option label="日线" value="daily" />
              <el-option label="30分" value="30min" />
              <el-option label="5分" value="5min" />
            </el-select>
            <el-button 
              type="primary" 
              size="small" 
              @click="refreshSignals"
              :loading="loading"
            >
              刷新
            </el-button>
          </div>
        </div>
      </template>
      
      <div class="signals-filters">
        <el-checkbox-group v-model="selectedSignalTypes" @change="filterSignals">
          <el-checkbox value="buy">买入信号</el-checkbox>
          <el-checkbox value="sell">卖出信号</el-checkbox>
        </el-checkbox-group>
      </div>
      
      <div class="signals-content" v-if="filteredSignals?.length">
        <div class="signals-stats">
          <div class="stat-item">
            <span class="stat-label">总信号数:</span>
            <span class="stat-value">{{ signalsData?.total_signals || 0 }}</span>
          </div>
          <div class="stat-item" v-if="signalsData?.success_rate">
            <span class="stat-label">成功率:</span>
            <span class="stat-value">{{ (signalsData.success_rate * 100).toFixed(1) }}%</span>
          </div>
          <div class="stat-item" v-if="signalsData?.avg_return">
            <span class="stat-label">平均收益:</span>
            <span class="stat-value" :class="signalsData.avg_return > 0 ? 'positive' : 'negative'">
              {{ (signalsData.avg_return * 100).toFixed(2) }}%
            </span>
          </div>
        </div>
        
        <div class="signals-list">
          <div 
            v-for="(signal, index) in filteredSignals.slice(0, displayLimit)" 
            :key="index"
            class="signal-item"
          >
            <div class="signal-header">
              <el-tag 
                :type="getSignalType(signal.signal_type)"
                size="small"
              >
                {{ getSignalText(signal.signal_type) }}
              </el-tag>
              <span class="signal-time">
                {{ formatTime(signal.signal_date || signal.timestamp) }}
              </span>
            </div>
            
            <div class="signal-content">
              <div class="signal-price" v-if="signal.price">
                <span class="price-label">信号价格:</span>
                <span class="price-value">¥{{ signal.price.toFixed(2) }}</span>
              </div>
              
              <div class="signal-confidence" v-if="signal.confidence">
                <span class="confidence-label">置信度:</span>
                <el-progress 
                  :percentage="signal.confidence * 100"
                  :color="getConfidenceColor(signal.confidence)"
                  :show-text="false"
                  size="small"
                  style="width: 60px;"
                />
                <span class="confidence-value">{{ (signal.confidence * 100).toFixed(1) }}%</span>
              </div>
              
              <div class="signal-reason" v-if="signal.reason">
                <span class="reason-label">信号原因:</span>
                <span class="reason-text">{{ signal.reason }}</span>
              </div>
              
              <div class="signal-result" v-if="signal.result">
                <span class="result-label">执行结果:</span>
                <span 
                  class="result-value"
                  :class="signal.result.return > 0 ? 'positive' : 'negative'"
                >
                  {{ (signal.result.return * 100).toFixed(2) }}%
                </span>
              </div>
            </div>
          </div>
        </div>
        
        <div class="load-more" v-if="filteredSignals.length > displayLimit">
          <el-button 
            link 
            @click="loadMore"
            :loading="loadingMore"
          >
            加载更多 ({{ filteredSignals.length - displayLimit }} 条)
          </el-button>
        </div>
      </div>
      
      <div class="empty-state" v-else-if="!loading">
        <el-empty description="暂无交易信号">
          <el-button type="primary" @click="refreshSignals">获取信号</el-button>
        </el-empty>
      </div>
      
      <div class="loading-state" v-if="loading">
        <el-skeleton :rows="4" animated />
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useChanAnalysisStore } from '@/stores/chanAnalysis'
import type { TradingSignal } from '@/types/api'
import { ElMessage } from 'element-plus'

interface Props {
  symbol: string
}

const props = defineProps<Props>()
const chanStore = useChanAnalysisStore()

const loading = ref(false)
const loadingMore = ref(false)
const selectedTimeframe = ref('daily')
const selectedSignalTypes = ref(['buy', 'sell'])
const displayLimit = ref(10)

const signalsData = computed(() => {
  return chanStore.tradingSignals[`${props.symbol}_${selectedTimeframe.value}`]
})

const filteredSignals = computed(() => {
  if (!signalsData.value?.signals) return []
  
  return signalsData.value.signals.filter((signal: TradingSignal) => 
    selectedSignalTypes.value.includes(signal.signal_type)
  )
})

const getSignalText = (signalType: string): string => {
  const texts: Record<string, string> = {
    'buy': '买入',
    'sell': '卖出',
    'hold': '持有',
    'wait': '观望'
  }
  return texts[signalType] || signalType
}

const getSignalType = (signalType: string): string => {
  if (signalType === 'buy') return 'success'
  if (signalType === 'sell') return 'danger'
  if (signalType === 'hold') return 'warning'
  return 'info'
}

const getConfidenceColor = (confidence: number): string => {
  if (confidence > 0.8) return '#67c23a'
  if (confidence > 0.6) return '#e6a23c'
  if (confidence > 0.4) return '#f56c6c'
  return '#909399'
}

const formatTime = (dateStr?: string): string => {
  if (!dateStr) return '未知'
  try {
    return new Date(dateStr).toLocaleString('zh-CN')
  } catch {
    return '未知'
  }
}

const refreshSignals = async () => {
  if (!props.symbol) {
    ElMessage.warning('请先选择股票代码')
    return
  }
  
  loading.value = true
  try {
    await chanStore.loadTradingSignals({
      symbol: props.symbol,
      timeframes: [selectedTimeframe.value],
      signal_types: selectedSignalTypes.value,
      limit: 50
    })
    ElMessage.success('信号更新成功')
  } catch (error) {
    console.error('信号加载失败:', error)
    ElMessage.error('信号加载失败，请重试')
  } finally {
    loading.value = false
  }
}

const filterSignals = () => {
  displayLimit.value = 10
}

const loadMore = () => {
  displayLimit.value += 10
}

watch(() => [props.symbol, selectedTimeframe.value], () => {
  if (props.symbol) {
    refreshSignals()
  }
}, { immediate: true })

onMounted(() => {
  if (props.symbol) {
    refreshSignals()
  }
})
</script>

<style scoped lang="scss">
.trading-signals {
  .signals-card {
    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      
      .title {
        font-size: 16px;
        font-weight: 600;
        color: #303133;
      }
      
      .header-controls {
        display: flex;
        align-items: center;
      }
    }
  }
  
  .signals-filters {
    margin-bottom: 20px;
    padding: 15px;
    background: #f8f9fa;
    border-radius: 8px;
  }
  
  .signals-stats {
    display: flex;
    justify-content: space-around;
    margin-bottom: 20px;
    padding: 15px;
    background: #f8f9fa;
    border-radius: 8px;
    
    .stat-item {
      text-align: center;
      
      .stat-label {
        display: block;
        font-size: 12px;
        color: #909399;
        margin-bottom: 4px;
      }
      
      .stat-value {
        display: block;
        font-size: 16px;
        font-weight: 600;
        color: #303133;
        
        &.positive {
          color: #67c23a;
        }
        
        &.negative {
          color: #f56c6c;
        }
      }
    }
  }
  
  .signals-list {
    .signal-item {
      padding: 15px;
      margin-bottom: 10px;
      border: 1px solid #ebeef5;
      border-radius: 8px;
      background: #fff;
      transition: all 0.3s ease;
      
      &:hover {
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
      }
      
      .signal-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 10px;
        
        .signal-time {
          font-size: 12px;
          color: #909399;
        }
      }
      
      .signal-content {
        .signal-price,
        .signal-confidence,
        .signal-reason,
        .signal-result {
          display: flex;
          align-items: center;
          margin-bottom: 8px;
          font-size: 13px;
          
          &:last-child {
            margin-bottom: 0;
          }
          
          span:first-child {
            color: #606266;
            min-width: 80px;
          }
          
          .price-value,
          .confidence-value,
          .reason-text,
          .result-value {
            color: #303133;
            font-weight: 500;
            
            &.positive {
              color: #67c23a;
            }
            
            &.negative {
              color: #f56c6c;
            }
          }
          
          .reason-text {
            font-weight: normal;
            line-height: 1.4;
          }
        }
        
        .signal-confidence {
          gap: 10px;
        }
      }
    }
  }
  
  .load-more {
    text-align: center;
    margin-top: 20px;
  }
  
  .empty-state,
  .loading-state {
    padding: 40px 20px;
    text-align: center;
  }
}

@media (max-width: 768px) {
  .trading-signals {
    .signals-stats {
      flex-direction: column;
      gap: 15px;
    }
    
    .signal-header {
      flex-direction: column;
      align-items: flex-start;
      gap: 8px;
    }
  }
}
</style>