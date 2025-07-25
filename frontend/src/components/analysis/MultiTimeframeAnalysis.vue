<template>
  <div class="multi-timeframe-analysis">
    <el-card class="analysis-card">
      <template #header>
        <div class="card-header">
          <span class="title">多时间周期分析</span>
          <el-button 
            type="primary" 
            size="small" 
            @click="refreshAnalysis"
            :loading="loading"
          >
            刷新分析
          </el-button>
        </div>
      </template>
      
      <div class="timeframe-selector">
        <el-checkbox-group v-model="selectedTimeframes" @change="updateAnalysis">
          <el-checkbox value="5min">5分钟</el-checkbox>
          <el-checkbox value="30min">30分钟</el-checkbox>
          <el-checkbox value="daily">日线</el-checkbox>
          <el-checkbox value="weekly">周线</el-checkbox>
          <el-checkbox value="monthly">月线</el-checkbox>
        </el-checkbox-group>
      </div>

      <div class="analysis-content" v-if="analysisData">
        <div class="timeframe-grid">
          <div 
            v-for="timeframe in selectedTimeframes" 
            :key="timeframe"
            class="timeframe-item"
          >
            <div class="timeframe-header">
              <h4>{{ getTimeframeName(timeframe) }}</h4>
              <el-tag 
                :type="getSignalType(analysisData.results?.[timeframe]?.trend)"
                size="small"
              >
                {{ analysisData.results?.[timeframe]?.trend || '无信号' }}
              </el-tag>
            </div>
            
            <div class="timeframe-metrics">
              <div class="metric-item">
                <span class="metric-label">强度评分:</span>
                <el-progress 
                  :percentage="(analysisData.results?.[timeframe]?.strength || 0) * 100"
                  :color="getStrengthColor(analysisData.results?.[timeframe]?.strength)"
                  size="small"
                />
              </div>
              
              <div class="metric-item">
                <span class="metric-label">确信度:</span>
                <span class="metric-value">
                  {{ ((analysisData.results?.[timeframe]?.confidence || 0) * 100).toFixed(1) }}%
                </span>
              </div>
              
              <div class="metric-item">
                <span class="metric-label">最后更新:</span>
                <span class="metric-value">
                  {{ formatTime(analysisData.results?.[timeframe]?.analysis_date) }}
                </span>
              </div>
            </div>
            
            <div class="structure-info" v-if="analysisData.results?.[timeframe]?.chan_analysis">
              <el-divider content-position="left">缠论结构</el-divider>
              <div class="structure-grid">
                <div class="structure-item">
                  <span class="structure-label">分型:</span>
                  <span class="structure-value">
                    {{ analysisData.results[timeframe].chan_analysis.fenxing_count || 0 }}
                  </span>
                </div>
                <div class="structure-item">
                  <span class="structure-label">笔:</span>
                  <span class="structure-value">
                    {{ analysisData.results[timeframe].chan_analysis.bi_count || 0 }}
                  </span>
                </div>
                <div class="structure-item">
                  <span class="structure-label">中枢:</span>
                  <span class="structure-value">
                    {{ analysisData.results[timeframe].chan_analysis.zhongshu_count || 0 }}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <div class="consistency-score" v-if="analysisData.consistency_score">
          <el-divider content-position="center">一致性评分</el-divider>
          <div class="score-display">
            <el-progress 
              type="circle"
              :percentage="analysisData.consistency_score * 100"
              :color="getConsistencyColor(analysisData.consistency_score)"
              :width="120"
            >
              <template #default="{ percentage }">
                <span class="score-text">{{ percentage.toFixed(1) }}</span>
              </template>
            </el-progress>
            <div class="score-description">
              <p>{{ getConsistencyDescription(analysisData.consistency_score) }}</p>
            </div>
          </div>
        </div>
      </div>
      
      <div class="empty-state" v-else-if="!loading">
        <el-empty description="暂无分析数据">
          <el-button type="primary" @click="refreshAnalysis">开始分析</el-button>
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
import type { MultiTimeframeAnalysis } from '@/types/api'
import { ElMessage } from 'element-plus'

interface Props {
  symbol: string
}

const props = defineProps<Props>()
const chanStore = useChanAnalysisStore()

const loading = ref(false)
const selectedTimeframes = ref(['5min', '30min', 'daily'])

const analysisData = computed(() => {
  return chanStore.multiTimeframeAnalysis[props.symbol]
})

const getTimeframeName = (timeframe: string): string => {
  const names: Record<string, string> = {
    '5min': '5分钟',
    '30min': '30分钟',
    'daily': '日线',
    'weekly': '周线',
    'monthly': '月线'
  }
  return names[timeframe] || timeframe
}

const getSignalType = (trend?: string): string => {
  if (!trend) return 'info'
  if (trend === 'buy' || trend === '上涨') return 'success'
  if (trend === 'sell' || trend === '下跌') return 'danger'
  return 'warning'
}

const getStrengthColor = (strength?: number): string => {
  if (!strength) return '#909399'
  if (strength > 0.8) return '#67c23a'
  if (strength > 0.6) return '#e6a23c'
  if (strength > 0.4) return '#f56c6c'
  return '#909399'
}

const getConsistencyColor = (score: number): string => {
  if (score > 0.8) return '#67c23a'
  if (score > 0.6) return '#e6a23c'
  return '#f56c6c'
}

const getConsistencyDescription = (score: number): string => {
  if (score > 0.8) return '各时间周期高度一致，信号可靠'
  if (score > 0.6) return '各时间周期基本一致，信号较可靠'
  if (score > 0.4) return '各时间周期存在分歧，需谨慎'
  return '各时间周期严重分歧，信号不可靠'
}

const formatTime = (dateStr?: string): string => {
  if (!dateStr) return '未知'
  try {
    return new Date(dateStr).toLocaleString('zh-CN')
  } catch {
    return '未知'
  }
}

const refreshAnalysis = async () => {
  if (!props.symbol) {
    ElMessage.warning('请先选择股票代码')
    return
  }
  
  loading.value = true
  try {
    await chanStore.loadMultiTimeframeAnalysis({
      symbol: props.symbol,
      timeframes: selectedTimeframes.value,
      analysis_depth: 'standard'
    })
    ElMessage.success('分析完成')
  } catch (error) {
    console.error('分析失败:', error)
    ElMessage.error('分析失败，请重试')
  } finally {
    loading.value = false
  }
}

const updateAnalysis = () => {
  if (selectedTimeframes.value.length > 0) {
    refreshAnalysis()
  }
}

watch(() => props.symbol, (newSymbol) => {
  if (newSymbol) {
    refreshAnalysis()
  }
}, { immediate: true })

onMounted(() => {
  if (props.symbol) {
    refreshAnalysis()
  }
})
</script>

<style scoped lang="scss">
.multi-timeframe-analysis {
  .analysis-card {
    margin-bottom: 20px;
    
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
  
  .timeframe-selector {
    margin-bottom: 20px;
    padding: 15px;
    background: #f8f9fa;
    border-radius: 8px;
  }
  
  .timeframe-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 20px;
    margin-bottom: 30px;
  }
  
  .timeframe-item {
    padding: 20px;
    border: 1px solid #ebeef5;
    border-radius: 8px;
    background: #fff;
    transition: all 0.3s ease;
    
    &:hover {
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
      transform: translateY(-2px);
    }
    
    .timeframe-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 15px;
      
      h4 {
        margin: 0;
        color: #303133;
        font-size: 14px;
        font-weight: 600;
      }
    }
    
    .timeframe-metrics {
      .metric-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 12px;
        
        .metric-label {
          font-size: 13px;
          color: #606266;
          min-width: 70px;
        }
        
        .metric-value {
          font-size: 13px;
          font-weight: 500;
          color: #303133;
        }
      }
    }
    
    .structure-info {
      margin-top: 15px;
      
      .structure-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 10px;
        
        .structure-item {
          text-align: center;
          padding: 8px;
          background: #f8f9fa;
          border-radius: 4px;
          
          .structure-label {
            display: block;
            font-size: 12px;
            color: #909399;
            margin-bottom: 4px;
          }
          
          .structure-value {
            display: block;
            font-size: 16px;
            font-weight: 600;
            color: #303133;
          }
        }
      }
    }
  }
  
  .consistency-score {
    text-align: center;
    padding: 20px;
    
    .score-display {
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 30px;
      
      .score-text {
        font-size: 18px;
        font-weight: 600;
      }
      
      .score-description {
        max-width: 200px;
        text-align: left;
        
        p {
          margin: 0;
          font-size: 14px;
          color: #606266;
          line-height: 1.5;
        }
      }
    }
  }
  
  .empty-state,
  .loading-state {
    padding: 40px 20px;
    text-align: center;
  }
}

@media (max-width: 768px) {
  .multi-timeframe-analysis {
    .timeframe-grid {
      grid-template-columns: 1fr;
    }
    
    .consistency-score {
      .score-display {
        flex-direction: column;
        gap: 20px;
        
        .score-description {
          text-align: center;
        }
      }
    }
  }
}
</style>