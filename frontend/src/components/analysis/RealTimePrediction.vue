<template>
  <div class="real-time-prediction">
    <el-card class="prediction-card">
      <template #header>
        <div class="card-header">
          <span class="title">实时预测</span>
          <el-button 
            type="primary" 
            size="small" 
            @click="refreshPrediction"
            :loading="loading"
          >
            刷新
          </el-button>
        </div>
      </template>
      
      <div class="prediction-content" v-if="predictionData">
        <div class="main-prediction">
          <div class="prediction-signal">
            <el-tag 
              :type="getSignalType(predictionData.prediction)"
              size="large"
              class="signal-tag"
            >
              {{ getPredictionText(predictionData.prediction) }}
            </el-tag>
            <div class="confidence">
              <span class="confidence-label">置信度:</span>
              <el-progress 
                :percentage="(predictionData.confidence || 0) * 100"
                :color="getConfidenceColor(predictionData.confidence)"
                :show-text="false"
                size="small"
              />
              <span class="confidence-value">
                {{ ((predictionData.confidence || 0) * 100).toFixed(1) }}%
              </span>
            </div>
          </div>
          
          <div class="price-info" v-if="predictionData.current_price">
            <div class="price-item">
              <span class="price-label">当前价格:</span>
              <span class="price-value">¥{{ predictionData.current_price.toFixed(2) }}</span>
            </div>
            <div class="price-item" v-if="predictionData.volume">
              <span class="price-label">成交量:</span>
              <span class="price-value">{{ formatVolume(predictionData.volume) }}</span>
            </div>
          </div>
        </div>
        
        <div class="prediction-details" v-if="predictionData.latest_data">
          <el-divider content-position="left">最新数据</el-divider>
          <div class="details-grid">
            <div class="detail-item">
              <span class="detail-label">开盘:</span>
              <span class="detail-value">¥{{ predictionData.latest_data.open?.toFixed(2) || '--' }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">最高:</span>
              <span class="detail-value">¥{{ predictionData.latest_data.high?.toFixed(2) || '--' }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">最低:</span>
              <span class="detail-value">¥{{ predictionData.latest_data.low?.toFixed(2) || '--' }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">收盘:</span>
              <span class="detail-value">¥{{ predictionData.latest_data.close?.toFixed(2) || '--' }}</span>
            </div>
          </div>
        </div>
        
        <div class="prediction-history" v-if="predictionData.prediction_history?.length">
          <el-divider content-position="left">历史预测</el-divider>
          <div class="history-list">
            <div 
              v-for="(history, index) in predictionData.prediction_history.slice(0, 5)" 
              :key="index"
              class="history-item"
            >
              <el-tag 
                :type="getSignalType(history.prediction)"
                size="small"
              >
                {{ getPredictionText(history.prediction) }}
              </el-tag>
              <span class="history-time">
                {{ formatTime(history.timestamp) }}
              </span>
              <span class="history-confidence">
                {{ ((history.confidence || 0) * 100).toFixed(1) }}%
              </span>
            </div>
          </div>
        </div>
        
        <div class="update-time">
          <el-text type="info" size="small">
            最后更新: {{ formatTime(predictionData.timestamp) }}
          </el-text>
        </div>
      </div>
      
      <div class="empty-state" v-else-if="!loading">
        <el-empty description="暂无预测数据">
          <el-button type="primary" @click="refreshPrediction">获取预测</el-button>
        </el-empty>
      </div>
      
      <div class="loading-state" v-if="loading">
        <el-skeleton :rows="3" animated />
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useChanAnalysisStore } from '@/stores/chanAnalysis'
import type { RealTimePrediction } from '@/types/api'
import { ElMessage } from 'element-plus'

interface Props {
  symbol: string
  timeframe?: string
}

const props = withDefaults(defineProps<Props>(), {
  timeframe: 'daily'
})

const chanStore = useChanAnalysisStore()
const loading = ref(false)

const predictionData = computed(() => {
  return chanStore.realTimePredictions[`${props.symbol}_${props.timeframe}`]
})

const getPredictionText = (prediction?: string): string => {
  const texts: Record<string, string> = {
    'buy': '买入信号',
    'sell': '卖出信号',
    'hold': '持有',
    'wait': '观望'
  }
  return texts[prediction || ''] || '无信号'
}

const getSignalType = (prediction?: string): string => {
  if (!prediction) return 'info'
  if (prediction === 'buy') return 'success'
  if (prediction === 'sell') return 'danger'
  if (prediction === 'hold') return 'warning'
  return 'info'
}

const getConfidenceColor = (confidence?: number): string => {
  if (!confidence) return '#909399'
  if (confidence > 0.8) return '#67c23a'
  if (confidence > 0.6) return '#e6a23c'
  if (confidence > 0.4) return '#f56c6c'
  return '#909399'
}

const formatVolume = (volume: number): string => {
  if (volume >= 100000000) {
    return (volume / 100000000).toFixed(2) + '亿'
  } else if (volume >= 10000) {
    return (volume / 10000).toFixed(2) + '万'
  }
  return volume.toString()
}

const formatTime = (dateStr?: string): string => {
  if (!dateStr) return '未知'
  try {
    return new Date(dateStr).toLocaleString('zh-CN')
  } catch {
    return '未知'
  }
}

const refreshPrediction = async () => {
  if (!props.symbol) {
    ElMessage.warning('请先选择股票代码')
    return
  }
  
  loading.value = true
  try {
    await chanStore.loadRealTimePrediction({
      symbol: props.symbol,
      timeframe: props.timeframe,
      include_confidence: true
    })
    ElMessage.success('预测更新成功')
  } catch (error) {
    console.error('预测失败:', error)
    ElMessage.error('预测失败，请重试')
  } finally {
    loading.value = false
  }
}

watch(() => [props.symbol, props.timeframe], () => {
  if (props.symbol) {
    refreshPrediction()
  }
}, { immediate: true })

onMounted(() => {
  if (props.symbol) {
    refreshPrediction()
  }
})
</script>

<style scoped lang="scss">
.real-time-prediction {
  .prediction-card {
    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      
      .title {
        font-size: 16px;
        font-weight: 600;
        color: #303133;
      }
    }
  }
  
  .main-prediction {
    text-align: center;
    margin-bottom: 30px;
    
    .prediction-signal {
      margin-bottom: 20px;
      
      .signal-tag {
        font-size: 18px;
        padding: 8px 20px;
        margin-bottom: 15px;
      }
      
      .confidence {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 10px;
        max-width: 300px;
        margin: 0 auto;
        
        .confidence-label {
          font-size: 14px;
          color: #606266;
          min-width: 60px;
        }
        
        .confidence-value {
          font-size: 14px;
          font-weight: 600;
          color: #303133;
          min-width: 50px;
        }
      }
    }
    
    .price-info {
      display: flex;
      justify-content: center;
      gap: 40px;
      
      .price-item {
        text-align: center;
        
        .price-label {
          display: block;
          font-size: 12px;
          color: #909399;
          margin-bottom: 4px;
        }
        
        .price-value {
          display: block;
          font-size: 18px;
          font-weight: 600;
          color: #303133;
        }
      }
    }
  }
  
  .details-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 15px;
    margin-bottom: 20px;
    
    .detail-item {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 10px;
      background: #f8f9fa;
      border-radius: 6px;
      
      .detail-label {
        font-size: 13px;
        color: #606266;
      }
      
      .detail-value {
        font-size: 13px;
        font-weight: 500;
        color: #303133;
      }
    }
  }
  
  .history-list {
    .history-item {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 8px 0;
      border-bottom: 1px solid #f0f0f0;
      
      &:last-child {
        border-bottom: none;
      }
      
      .history-time {
        font-size: 12px;
        color: #909399;
        flex: 1;
        text-align: center;
      }
      
      .history-confidence {
        font-size: 12px;
        color: #606266;
        min-width: 50px;
        text-align: right;
      }
    }
  }
  
  .update-time {
    text-align: center;
    margin-top: 20px;
    padding-top: 15px;
    border-top: 1px solid #f0f0f0;
  }
  
  .empty-state,
  .loading-state {
    padding: 40px 20px;
    text-align: center;
  }
}

@media (max-width: 768px) {
  .real-time-prediction {
    .price-info {
      flex-direction: column;
      gap: 20px;
    }
    
    .details-grid {
      grid-template-columns: 1fr;
    }
  }
}
</style>