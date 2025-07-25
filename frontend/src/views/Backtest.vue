<template>
  <div class="backtest-view">
    <div class="backtest-header">
      <h2 class="page-title">策略回测</h2>
      <div class="header-controls">
        <el-button type="primary" size="small" @click="showConfigDialog = true">
          新建回测
        </el-button>
        <el-button type="default" size="small" @click="refreshBacktests" :loading="loading">
          刷新
        </el-button>
      </div>
    </div>
    
    <!-- 回测列表 -->
    <div class="backtest-content">
      <el-table :data="backtestData" v-loading="loading" @row-click="viewBacktest">
        <el-table-column prop="name" label="回测名称" width="200" />
        <el-table-column prop="strategy" label="策略" width="150" />
        <el-table-column prop="symbol" label="股票" width="100" />
        <el-table-column prop="period" label="回测期间" width="200">
          <template #default="{ row }">
            {{ formatDate(row.start_date) }} - {{ formatDate(row.end_date) }}
          </template>
        </el-table-column>
        <el-table-column prop="total_return" label="总收益" width="100">
          <template #default="{ row }">
            <span :class="row.total_return > 0 ? 'positive' : 'negative'">
              {{ (row.total_return * 100).toFixed(2) }}%
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="annual_return" label="年化收益" width="100">
          <template #default="{ row }">
            <span :class="row.annual_return > 0 ? 'positive' : 'negative'">
              {{ (row.annual_return * 100).toFixed(2) }}%
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="sharpe_ratio" label="夏普比" width="80">
          <template #default="{ row }">
            {{ row.sharpe_ratio.toFixed(3) }}
          </template>
        </el-table-column>
        <el-table-column prop="max_drawdown" label="最大回撤" width="100">
          <template #default="{ row }">
            <span class="negative">{{ (row.max_drawdown * 100).toFixed(2) }}%</span>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="150">
          <template #default="{ row }">
            {{ formatTime(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button link size="small" @click.stop="viewBacktest(row)">
              查看
            </el-button>
            <el-button link size="small" @click.stop="compareBacktest(row)">
              对比
            </el-button>
            <el-button 
              link 
              size="small" 
              @click.stop="deleteBacktest(row)"
              style="color: #f56c6c;"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <div class="empty-state" v-if="!backtestData.length && !loading">
        <el-empty description="暂无回测结果">
          <el-button type="primary" @click="showConfigDialog = true">创建第一个回测</el-button>
        </el-empty>
      </div>
    </div>
    
    <!-- 回测配置对话框 -->
    <el-dialog v-model="showConfigDialog" title="回测配置" width="600px">
      <el-form :model="configForm" label-width="100px">
        <el-form-item label="回测名称">
          <el-input v-model="configForm.name" placeholder="输入回测名称" />
        </el-form-item>
        <el-form-item label="选择策略">
          <el-select v-model="configForm.strategy" placeholder="选择策略">
            <el-option label="缠论多级别分析策略" value="chan_theory" />
            <el-option label="动量价格突破策略" value="volume_price" />
            <el-option label="基本面量化选股" value="fundamental" />
          </el-select>
        </el-form-item>
        <el-form-item label="股票代码">
          <el-input v-model="configForm.symbol" placeholder="如: 000001.SZ" />
        </el-form-item>
        <el-form-item label="回测期间">
          <el-date-picker
            v-model="configForm.dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            style="width: 100%;"
          />
        </el-form-item>
        <el-form-item label="初始资金">
          <el-input-number 
            v-model="configForm.initial_capital" 
            :min="10000" 
            :max="10000000" 
            :step="10000"
            style="width: 100%;"
          />
        </el-form-item>
        <el-form-item label="手续费率">
          <el-input-number 
            v-model="configForm.commission_rate" 
            :min="0" 
            :max="0.01" 
            :step="0.0001"
            :precision="4"
            style="width: 100%;"
          />
        </el-form-item>
        <el-form-item label="滑点设置">
          <el-input-number 
            v-model="configForm.slippage" 
            :min="0" 
            :max="0.01" 
            :step="0.0001"
            :precision="4"
            style="width: 100%;"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showConfigDialog = false">取消</el-button>
        <el-button type="primary" @click="runBacktest" :loading="running">开始回测</el-button>
      </template>
    </el-dialog>
    
    <!-- 回测结果详情对话框 -->
    <el-dialog v-model="showDetailDialog" title="回测结果" width="1000px">
      <div v-if="selectedBacktest">
        <!-- 基本信息 -->
        <el-descriptions :column="3" border style="margin-bottom: 20px;">
          <el-descriptions-item label="回测名称">
            {{ selectedBacktest.name }}
          </el-descriptions-item>
          <el-descriptions-item label="策略">
            {{ selectedBacktest.strategy }}
          </el-descriptions-item>
          <el-descriptions-item label="股票">
            {{ selectedBacktest.symbol }}
          </el-descriptions-item>
          <el-descriptions-item label="回测期间">
            {{ formatDate(selectedBacktest.start_date) }} - {{ formatDate(selectedBacktest.end_date) }}
          </el-descriptions-item>
          <el-descriptions-item label="初始资金">
            ¥{{ selectedBacktest.initial_capital.toLocaleString() }}
          </el-descriptions-item>
          <el-descriptions-item label="最终资金">
            ¥{{ selectedBacktest.final_capital.toLocaleString() }}
          </el-descriptions-item>
        </el-descriptions>
        
        <!-- 性能指标 -->
        <el-divider>性能指标</el-divider>
        <el-row :gutter="20" style="margin-bottom: 20px;">
          <el-col :span="6">
            <div class="metric-card">
              <div class="metric-title">总收益率</div>
              <div 
                class="metric-big-value"
                :class="selectedBacktest.total_return > 0 ? 'positive' : 'negative'"
              >
                {{ (selectedBacktest.total_return * 100).toFixed(2) }}%
              </div>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="metric-card">
              <div class="metric-title">年化收益率</div>
              <div 
                class="metric-big-value"
                :class="selectedBacktest.annual_return > 0 ? 'positive' : 'negative'"
              >
                {{ (selectedBacktest.annual_return * 100).toFixed(2) }}%
              </div>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="metric-card">
              <div class="metric-title">夏普比率</div>
              <div class="metric-big-value">
                {{ selectedBacktest.sharpe_ratio.toFixed(3) }}
              </div>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="metric-card">
              <div class="metric-title">最大回撤</div>
              <div class="metric-big-value negative">
                {{ (selectedBacktest.max_drawdown * 100).toFixed(2) }}%
              </div>
            </div>
          </el-col>
        </el-row>
        
        <!-- 交易统计 -->
        <el-divider>交易统计</el-divider>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-card>
              <template #header>
                <span>交易次数</span>
              </template>
              <div class="trade-stats">
                <div class="stat-item">
                  <span class="label">总交易次数:</span>
                  <span class="value">{{ selectedBacktest.total_trades }}</span>
                </div>
                <div class="stat-item">
                  <span class="label">盈利交易:</span>
                  <span class="value positive">{{ selectedBacktest.winning_trades }}</span>
                </div>
                <div class="stat-item">
                  <span class="label">亏损交易:</span>
                  <span class="value negative">{{ selectedBacktest.losing_trades }}</span>
                </div>
                <div class="stat-item">
                  <span class="label">胜率:</span>
                  <span class="value">{{ (selectedBacktest.win_rate * 100).toFixed(1) }}%</span>
                </div>
              </div>
            </el-card>
          </el-col>
          <el-col :span="12">
            <el-card>
              <template #header>
                <span>收益分布</span>
              </template>
              <div class="trade-stats">
                <div class="stat-item">
                  <span class="label">平均盈利:</span>
                  <span class="value positive">¥{{ selectedBacktest.avg_win.toFixed(2) }}</span>
                </div>
                <div class="stat-item">
                  <span class="label">平均亏损:</span>
                  <span class="value negative">¥{{ selectedBacktest.avg_loss.toFixed(2) }}</span>
                </div>
                <div class="stat-item">
                  <span class="label">盈亏比:</span>
                  <span class="value">{{ selectedBacktest.profit_loss_ratio.toFixed(2) }}</span>
                </div>
                <div class="stat-item">
                  <span class="label">最大单笔盈利:</span>
                  <span class="value positive">¥{{ selectedBacktest.max_win.toFixed(2) }}</span>
                </div>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'

interface BacktestResult {
  id: string
  name: string
  strategy: string
  symbol: string
  start_date: string
  end_date: string
  initial_capital: number
  final_capital: number
  total_return: number
  annual_return: number
  sharpe_ratio: number
  max_drawdown: number
  total_trades: number
  winning_trades: number
  losing_trades: number
  win_rate: number
  avg_win: number
  avg_loss: number
  profit_loss_ratio: number
  max_win: number
  created_at: string
}

const loading = ref(false)
const running = ref(false)
const showConfigDialog = ref(false)
const showDetailDialog = ref(false)
const selectedBacktest = ref<BacktestResult | null>(null)

const configForm = reactive({
  name: '',
  strategy: '',
  symbol: '',
  dateRange: [],
  initial_capital: 100000,
  commission_rate: 0.0003,
  slippage: 0.0001
})

// 模拟回测数据
const backtestData = ref<BacktestResult[]>([
  {
    id: '1',
    name: '缠论策略回测_20240101',
    strategy: '缠论多级别分析策略',
    symbol: '000001.SZ',
    start_date: '2023-01-01',
    end_date: '2023-12-31',
    initial_capital: 100000,
    final_capital: 124500,
    total_return: 0.245,
    annual_return: 0.245,
    sharpe_ratio: 1.85,
    max_drawdown: -0.12,
    total_trades: 48,
    winning_trades: 32,
    losing_trades: 16,
    win_rate: 0.667,
    avg_win: 1250.50,
    avg_loss: -650.25,
    profit_loss_ratio: 1.92,
    max_win: 4500.00,
    created_at: '2024-01-15T10:30:00Z'
  },
  {
    id: '2',
    name: '动量策略回测_20240105',
    strategy: '动量价格突破策略',
    symbol: '600519.SH',
    start_date: '2023-01-01',
    end_date: '2023-12-31',
    initial_capital: 100000,
    final_capital: 118600,
    total_return: 0.186,
    annual_return: 0.186,
    sharpe_ratio: 1.42,
    max_drawdown: -0.18,
    total_trades: 35,
    winning_trades: 22,
    losing_trades: 13,
    win_rate: 0.629,
    avg_win: 1180.75,
    avg_loss: -720.45,
    profit_loss_ratio: 1.64,
    max_win: 3200.00,
    created_at: '2024-01-10T14:20:00Z'
  }
])

const formatDate = (dateStr: string): string => {
  try {
    return new Date(dateStr).toLocaleDateString('zh-CN')
  } catch {
    return dateStr
  }
}

const formatTime = (dateStr: string): string => {
  try {
    return new Date(dateStr).toLocaleDateString('zh-CN')
  } catch {
    return dateStr
  }
}

const refreshBacktests = async () => {
  loading.value = true
  try {
    await new Promise(resolve => setTimeout(resolve, 1000))
    ElMessage.success('回测列表刷新成功')
  } catch (error) {
    console.error('刷新失败:', error)
    ElMessage.error('刷新失败，请重试')
  } finally {
    loading.value = false
  }
}

const runBacktest = async () => {
  if (!configForm.name.trim()) {
    ElMessage.warning('请输入回测名称')
    return
  }
  
  if (!configForm.strategy) {
    ElMessage.warning('请选择策略')
    return
  }
  
  if (!configForm.symbol.trim()) {
    ElMessage.warning('请输入股票代码')
    return
  }
  
  if (!configForm.dateRange || configForm.dateRange.length !== 2) {
    ElMessage.warning('请选择回测期间')
    return
  }
  
  running.value = true
  try {
    // 模拟回测运行
    await new Promise(resolve => setTimeout(resolve, 3000))
    
    const newBacktest: BacktestResult = {
      id: Date.now().toString(),
      name: configForm.name,
      strategy: configForm.strategy,
      symbol: configForm.symbol,
      start_date: configForm.dateRange[0],
      end_date: configForm.dateRange[1],
      initial_capital: configForm.initial_capital,
      final_capital: configForm.initial_capital * (1 + Math.random() * 0.5 - 0.1),
      total_return: Math.random() * 0.5 - 0.1,
      annual_return: Math.random() * 0.4 - 0.05,
      sharpe_ratio: Math.random() * 2 + 0.5,
      max_drawdown: -Math.random() * 0.3,
      total_trades: Math.floor(Math.random() * 100) + 20,
      winning_trades: 0,
      losing_trades: 0,
      win_rate: Math.random() * 0.4 + 0.4,
      avg_win: Math.random() * 2000 + 500,
      avg_loss: -(Math.random() * 1000 + 300),
      profit_loss_ratio: Math.random() * 2 + 0.8,
      max_win: Math.random() * 5000 + 1000,
      created_at: new Date().toISOString()
    }
    
    newBacktest.winning_trades = Math.floor(newBacktest.total_trades * newBacktest.win_rate)
    newBacktest.losing_trades = newBacktest.total_trades - newBacktest.winning_trades
    
    backtestData.value.unshift(newBacktest)
    
    // 重置表单
    Object.keys(configForm).forEach(key => {
      if (key === 'initial_capital') {
        (configForm as any)[key] = 100000
      } else if (key === 'commission_rate') {
        (configForm as any)[key] = 0.0003
      } else if (key === 'slippage') {
        (configForm as any)[key] = 0.0001
      } else if (key === 'dateRange') {
        (configForm as any)[key] = []
      } else {
        (configForm as any)[key] = ''
      }
    })
    
    showConfigDialog.value = false
    ElMessage.success('回测完成！')
  } catch (error) {
    console.error('回测失败:', error)
    ElMessage.error('回测失败，请重试')
  } finally {
    running.value = false
  }
}

const viewBacktest = (backtest: BacktestResult) => {
  selectedBacktest.value = backtest
  showDetailDialog.value = true
}

const compareBacktest = (backtest: BacktestResult) => {
  ElMessage.info(`回测对比功能开发中: ${backtest.name}`)
}

const deleteBacktest = async (backtest: BacktestResult) => {
  try {
    await ElMessageBox.confirm(
      `确认要删除回测 "${backtest.name}" 吗？此操作不可恢复。`,
      '确认删除',
      {
        confirmButtonText: '确认删除',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    const index = backtestData.value.findIndex(b => b.id === backtest.id)
    if (index > -1) {
      backtestData.value.splice(index, 1)
      ElMessage.success('回测结果删除成功')
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
.backtest-view {
  padding: 20px;
  
  .backtest-header {
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
  
  :deep(.el-table) {
    .positive {
      color: #67c23a;
      font-weight: 600;
    }
    
    .negative {
      color: #f56c6c;
      font-weight: 600;
    }
    
    .el-table__row {
      cursor: pointer;
      
      &:hover {
        background-color: #f5f7fa;
      }
    }
  }
  
  .empty-state {
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 400px;
  }
  
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
  
  .trade-stats {
    .stat-item {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 12px;
      
      &:last-child {
        margin-bottom: 0;
      }
      
      .label {
        font-size: 14px;
        color: #606266;
      }
      
      .value {
        font-size: 14px;
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
  .backtest-view {
    padding: 10px;
    
    .backtest-header {
      flex-direction: column;
      gap: 15px;
      align-items: stretch;
    }
  }
}
</style>