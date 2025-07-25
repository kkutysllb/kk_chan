<template>
  <div class="strategies-view">
    <div class="strategies-header">
      <h2 class="page-title">量化策略</h2>
      <div class="header-controls">
        <el-button type="primary" size="small" @click="showCreateDialog = true">
          创建策略
        </el-button>
        <el-button type="default" size="small" @click="refreshStrategies" :loading="loading">
          刷新
        </el-button>
      </div>
    </div>
    
    <!-- 策略列表 -->
    <div class="strategies-content">
      <el-row :gutter="20">
        <el-col 
          :span="8" 
          v-for="strategy in strategiesData" 
          :key="strategy.id"
          style="margin-bottom: 20px;"
        >
          <el-card class="strategy-card" @click="viewStrategy(strategy)">
            <div class="strategy-header">
              <div class="strategy-name">{{ strategy.name }}</div>
              <el-tag 
                :type="getStatusType(strategy.status)"
                size="small"
              >
                {{ getStatusText(strategy.status) }}
              </el-tag>
            </div>
            
            <div class="strategy-description">
              {{ strategy.description }}
            </div>
            
            <div class="strategy-metrics">
              <div class="metric-item">
                <span class="metric-label">年收益率:</span>
                <span 
                  class="metric-value"
                  :class="strategy.annual_return > 0 ? 'positive' : 'negative'"
                >
                  {{ (strategy.annual_return * 100).toFixed(2) }}%
                </span>
              </div>
              <div class="metric-item">
                <span class="metric-label">夏普比率:</span>
                <span class="metric-value">{{ strategy.sharpe_ratio.toFixed(3) }}</span>
              </div>
              <div class="metric-item">
                <span class="metric-label">最大回撤:</span>
                <span class="metric-value negative">
                  {{ (strategy.max_drawdown * 100).toFixed(2) }}%
                </span>
              </div>
              <div class="metric-item">
                <span class="metric-label">胜率:</span>
                <span class="metric-value">{{ (strategy.win_rate * 100).toFixed(1) }}%</span>
              </div>
            </div>
            
            <div class="strategy-actions">
              <el-button 
                link 
                size="small" 
                @click.stop="editStrategy(strategy)"
              >
                编辑
              </el-button>
              <el-button 
                link 
                size="small" 
                @click.stop="runBacktest(strategy)"
                :loading="backtestLoading === strategy.id"
              >
                回测
              </el-button>
              <el-button 
                link 
                size="small" 
                @click.stop="toggleStrategy(strategy)"
                :loading="toggleLoading === strategy.id"
              >
                {{ strategy.status === 'running' ? '停止' : '启动' }}
              </el-button>
              <el-button 
                link 
                size="small" 
                @click.stop="deleteStrategy(strategy)"
                style="color: #f56c6c;"
              >
                删除
              </el-button>
            </div>
          </el-card>
        </el-col>
      </el-row>
      
      <div class="empty-state" v-if="!strategiesData.length && !loading">
        <el-empty description="暂无策略">
          <el-button type="primary" @click="showCreateDialog = true">创建第一个策略</el-button>
        </el-empty>
      </div>
    </div>
    
    <!-- 创建策略对话框 -->
    <el-dialog v-model="showCreateDialog" title="创建策略" width="600px">
      <el-form :model="createForm" label-width="100px">
        <el-form-item label="策略名称">
          <el-input v-model="createForm.name" placeholder="输入策略名称" />
        </el-form-item>
        <el-form-item label="策略描述">
          <el-input 
            v-model="createForm.description" 
            type="textarea" 
            :rows="3"
            placeholder="输入策略描述"
          />
        </el-form-item>
        <el-form-item label="策略类型">
          <el-select v-model="createForm.type" placeholder="选择策略类型">
            <el-option label="缠论分析" value="chan_theory" />
            <el-option label="技术指标" value="technical" />
            <el-option label="基本面分析" value="fundamental" />
            <el-option label="量价分析" value="volume_price" />
          </el-select>
        </el-form-item>
        <el-form-item label="时间周期">
          <el-select v-model="createForm.timeframe" placeholder="选择时间周期">
            <el-option label="5分钟" value="5min" />
            <el-option label="30分钟" value="30min" />
            <el-option label="日线" value="daily" />
            <el-option label="周线" value="weekly" />
            <el-option label="月线" value="monthly" />
          </el-select>
        </el-form-item>
        <el-form-item label="策略参数">
          <el-input 
            v-model="createForm.parameters" 
            type="textarea" 
            :rows="4"
            placeholder="输入JSON格式的策略参数"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="createStrategy" :loading="creating">创建</el-button>
      </template>
    </el-dialog>
    
    <!-- 策略详情对话框 -->
    <el-dialog v-model="showDetailDialog" title="策略详情" width="800px">
      <div v-if="selectedStrategy">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="策略名称">
            {{ selectedStrategy.name }}
          </el-descriptions-item>
          <el-descriptions-item label="策略状态">
            <el-tag :type="getStatusType(selectedStrategy.status)">
              {{ getStatusText(selectedStrategy.status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="策略类型">
            {{ selectedStrategy.type }}
          </el-descriptions-item>
          <el-descriptions-item label="时间周期">
            {{ selectedStrategy.timeframe }}
          </el-descriptions-item>
          <el-descriptions-item label="创建时间">
            {{ formatTime(selectedStrategy.created_at) }}
          </el-descriptions-item>
          <el-descriptions-item label="最后运行">
            {{ formatTime(selectedStrategy.last_run) }}
          </el-descriptions-item>
        </el-descriptions>
        
        <el-divider>性能指标</el-divider>
        <div class="performance-metrics">
          <el-row :gutter="20">
            <el-col :span="6">
              <div class="metric-card">
                <div class="metric-title">年收益率</div>
                <div 
                  class="metric-big-value"
                  :class="selectedStrategy.annual_return > 0 ? 'positive' : 'negative'"
                >
                  {{ (selectedStrategy.annual_return * 100).toFixed(2) }}%
                </div>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="metric-card">
                <div class="metric-title">夏普比率</div>
                <div class="metric-big-value">
                  {{ selectedStrategy.sharpe_ratio.toFixed(3) }}
                </div>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="metric-card">
                <div class="metric-title">最大回撤</div>
                <div class="metric-big-value negative">
                  {{ (selectedStrategy.max_drawdown * 100).toFixed(2) }}%
                </div>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="metric-card">
                <div class="metric-title">胜率</div>
                <div class="metric-big-value">
                  {{ (selectedStrategy.win_rate * 100).toFixed(1) }}%
                </div>
              </div>
            </el-col>
          </el-row>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'

interface Strategy {
  id: string
  name: string
  description: string
  type: string
  timeframe: string
  status: 'running' | 'stopped' | 'paused'
  annual_return: number
  sharpe_ratio: number
  max_drawdown: number
  win_rate: number
  created_at: string
  last_run?: string
  parameters?: any
}

const loading = ref(false)
const creating = ref(false)
const backtestLoading = ref('')
const toggleLoading = ref('')
const showCreateDialog = ref(false)
const showDetailDialog = ref(false)
const selectedStrategy = ref<Strategy | null>(null)

const createForm = reactive({
  name: '',
  description: '',
  type: '',
  timeframe: '',
  parameters: '{}'
})

// 模拟策略数据
const strategiesData = ref<Strategy[]>([
  {
    id: '1',
    name: '缠论多级别分析策略',
    description: '基于缠论理论的多时间周期分析策略，结合分型、笔、中枢等结构进行交易决策',
    type: 'chan_theory',
    timeframe: 'daily',
    status: 'running',
    annual_return: 0.245,
    sharpe_ratio: 1.85,
    max_drawdown: -0.12,
    win_rate: 0.68,
    created_at: '2024-01-15T10:30:00Z',
    last_run: '2024-01-20T14:25:00Z'
  },
  {
    id: '2',
    name: '动量价格突破策略',
    description: '结合成交量和价格变化，识别突破信号进行交易',
    type: 'volume_price',
    timeframe: '30min',
    status: 'stopped',
    annual_return: 0.186,
    sharpe_ratio: 1.42,
    max_drawdown: -0.18,
    win_rate: 0.62,
    created_at: '2024-01-10T09:15:00Z',
    last_run: '2024-01-18T16:45:00Z'
  },
  {
    id: '3',
    name: '基本面量化选股',
    description: '基于财务数据和估值指标的量化选股策略',
    type: 'fundamental',
    timeframe: 'weekly',
    status: 'paused',
    annual_return: 0.156,
    sharpe_ratio: 1.28,
    max_drawdown: -0.08,
    win_rate: 0.59,
    created_at: '2024-01-05T14:20:00Z',
    last_run: '2024-01-15T11:30:00Z'
  }
])

const getStatusText = (status: string): string => {
  const texts: Record<string, string> = {
    'running': '运行中',
    'stopped': '已停止',
    'paused': '已暂停'
  }
  return texts[status] || status
}

const getStatusType = (status: string): string => {
  if (status === 'running') return 'success'
  if (status === 'stopped') return 'danger'
  if (status === 'paused') return 'warning'
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

const refreshStrategies = async () => {
  loading.value = true
  try {
    await new Promise(resolve => setTimeout(resolve, 1000))
    ElMessage.success('策略列表刷新成功')
  } catch (error) {
    console.error('刷新失败:', error)
    ElMessage.error('刷新失败，请重试')
  } finally {
    loading.value = false
  }
}

const createStrategy = async () => {
  if (!createForm.name.trim()) {
    ElMessage.warning('请输入策略名称')
    return
  }
  
  creating.value = true
  try {
    // 模拟创建逻辑
    await new Promise(resolve => setTimeout(resolve, 1500))
    
    const newStrategy: Strategy = {
      id: Date.now().toString(),
      name: createForm.name,
      description: createForm.description,
      type: createForm.type,
      timeframe: createForm.timeframe,
      status: 'stopped',
      annual_return: 0,
      sharpe_ratio: 0,
      max_drawdown: 0,
      win_rate: 0,
      created_at: new Date().toISOString()
    }
    
    strategiesData.value.unshift(newStrategy)
    
    // 重置表单
    Object.keys(createForm).forEach(key => {
      if (key === 'parameters') {
        (createForm as any)[key] = '{}'
      } else {
        (createForm as any)[key] = ''
      }
    })
    
    showCreateDialog.value = false
    ElMessage.success('策略创建成功')
  } catch (error) {
    console.error('创建失败:', error)
    ElMessage.error('策略创建失败，请重试')
  } finally {
    creating.value = false
  }
}

const viewStrategy = (strategy: Strategy) => {
  selectedStrategy.value = strategy
  showDetailDialog.value = true
}

const editStrategy = (strategy: Strategy) => {
  ElMessage.info(`编辑策略 ${strategy.name}（功能开发中）`)
}

const runBacktest = async (strategy: Strategy) => {
  backtestLoading.value = strategy.id
  try {
    await new Promise(resolve => setTimeout(resolve, 2000))
    ElMessage.success(`${strategy.name} 回测完成`)
  } catch (error) {
    console.error('回测失败:', error)
    ElMessage.error('回测失败，请重试')
  } finally {
    backtestLoading.value = ''
  }
}

const toggleStrategy = async (strategy: Strategy) => {
  toggleLoading.value = strategy.id
  try {
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    const newStatus = strategy.status === 'running' ? 'stopped' : 'running'
    strategy.status = newStatus
    
    if (newStatus === 'running') {
      strategy.last_run = new Date().toISOString()
    }
    
    ElMessage.success(`策略${newStatus === 'running' ? '启动' : '停止'}成功`)
  } catch (error) {
    console.error('切换状态失败:', error)
    ElMessage.error('操作失败，请重试')
  } finally {
    toggleLoading.value = ''
  }
}

const deleteStrategy = async (strategy: Strategy) => {
  try {
    await ElMessageBox.confirm(
      `确认要删除策略 "${strategy.name}" 吗？此操作不可恢复。`,
      '确认删除',
      {
        confirmButtonText: '确认删除',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    const index = strategiesData.value.findIndex(s => s.id === strategy.id)
    if (index > -1) {
      strategiesData.value.splice(index, 1)
      ElMessage.success('策略删除成功')
    }
  } catch {
    // 用户取消
  }
}

onMounted(() => {
  // 可以在这里加载真实数据
})
</script>

<style scoped lang="scss">
.strategies-view {
  padding: 20px;
  
  .strategies-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 30px;
    
    .page-title {
      font-size: 24px;
      font-weight: 600;
      color: #303133;
      margin: 0;
    }
    
    .header-controls {
      display: flex;
      gap: 10px;
    }
  }
  
  .strategy-card {
    cursor: pointer;
    transition: all 0.3s ease;
    height: 280px;
    
    &:hover {
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
      transform: translateY(-2px);
    }
    
    .strategy-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 15px;
      
      .strategy-name {
        font-size: 16px;
        font-weight: 600;
        color: #303133;
      }
    }
    
    .strategy-description {
      font-size: 13px;
      color: #606266;
      line-height: 1.5;
      margin-bottom: 20px;
      min-height: 40px;
    }
    
    .strategy-metrics {
      margin-bottom: 20px;
      
      .metric-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 8px;
        
        .metric-label {
          font-size: 12px;
          color: #909399;
        }
        
        .metric-value {
          font-size: 13px;
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
    
    .strategy-actions {
      display: flex;
      justify-content: space-between;
      border-top: 1px solid #ebeef5;
      padding-top: 15px;
    }
  }
  
  .empty-state {
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 400px;
  }
  
  .performance-metrics {
    margin-top: 20px;
    
    .metric-card {
      text-align: center;
      padding: 20px;
      border: 1px solid #ebeef5;
      border-radius: 8px;
      
      .metric-title {
        font-size: 14px;
        color: #606266;
        margin-bottom: 10px;
      }
      
      .metric-big-value {
        font-size: 24px;
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
}

@media (max-width: 768px) {
  .strategies-view {
    padding: 10px;
    
    .strategies-header {
      flex-direction: column;
      gap: 15px;
      align-items: stretch;
    }
    
    .strategies-content {
      :deep(.el-col) {
        margin-bottom: 20px;
      }
    }
  }
}
</style>