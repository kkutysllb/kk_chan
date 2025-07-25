<template>
  <div class="watchlist-table">
    <el-card class="watchlist-card">
      <template #header>
        <div class="card-header">
          <span class="title">自选股列表</span>
          <div class="header-controls">
            <el-input
              v-model="searchSymbol"
              placeholder="输入股票代码"
              size="small"
              style="width: 150px; margin-right: 10px;"
              @keyup.enter="addToWatchlist"
            >
              <template #append>
                <el-button @click="addToWatchlist" :loading="adding">
                  <el-icon><Plus /></el-icon>
                </el-button>
              </template>
            </el-input>
            <el-button 
              type="primary" 
              size="small" 
              @click="refreshWatchlist"
              :loading="loading"
            >
              刷新
            </el-button>
          </div>
        </div>
      </template>
      
      <div class="watchlist-content">
        <el-table 
          :data="watchlistData" 
          v-loading="loading"
          @row-click="selectStock"
          highlight-current-row
          style="width: 100%"
        >
          <el-table-column prop="symbol" label="代码" width="100" />
          <el-table-column prop="name" label="名称" width="120" />
          <el-table-column prop="current_price" label="现价" width="80">
            <template #default="{ row }">
              <span v-if="row.current_price">¥{{ row.current_price.toFixed(2) }}</span>
              <span v-else>--</span>
            </template>
          </el-table-column>
          <el-table-column prop="change_pct" label="涨跌幅" width="80">
            <template #default="{ row }">
              <span 
                v-if="row.change_pct !== undefined"
                :class="{
                  'positive': row.change_pct > 0,
                  'negative': row.change_pct < 0,
                  'neutral': row.change_pct === 0
                }"
              >
                {{ (row.change_pct * 100).toFixed(2) }}%
              </span>
              <span v-else>--</span>
            </template>
          </el-table-column>
          <el-table-column prop="volume" label="成交量" width="100">
            <template #default="{ row }">
              <span v-if="row.volume">{{ formatVolume(row.volume) }}</span>
              <span v-else>--</span>
            </template>
          </el-table-column>
          <el-table-column prop="signal" label="信号" width="80">
            <template #default="{ row }">
              <el-tag 
                v-if="row.latest_signal"
                :type="getSignalType(row.latest_signal.type)"
                size="small"
              >
                {{ getSignalText(row.latest_signal.type) }}
              </el-tag>
              <span v-else>--</span>
            </template>
          </el-table-column>
          <el-table-column prop="trend" label="趋势" width="80">
            <template #default="{ row }">
              <el-tag 
                v-if="row.trend"
                :type="getTrendType(row.trend)"
                size="small"
              >
                {{ getTrendText(row.trend) }}
              </el-tag>
              <span v-else>--</span>
            </template>
          </el-table-column>
          <el-table-column prop="update_time" label="更新时间" width="120">
            <template #default="{ row }">
              <span v-if="row.update_time">{{ formatTime(row.update_time) }}</span>
              <span v-else>--</span>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="100" fixed="right">
            <template #default="{ row }">
              <el-button 
                link 
                size="small" 
                @click.stop="removeFromWatchlist(row.symbol)"
                :loading="removing === row.symbol"
              >
                移除
              </el-button>
            </template>
          </el-table-column>
        </el-table>
        
        <div class="pagination" v-if="watchlistData.length > pageSize">
          <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[10, 20, 50, 100]"
            :total="totalItems"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
          />
        </div>
      </div>
      
      <div class="empty-state" v-if="!watchlistData.length && !loading">
        <el-empty description="暂无自选股">
          <el-button type="primary" @click="showAddDialog = true">添加自选股</el-button>
        </el-empty>
      </div>
    </el-card>
    
    <!-- 添加自选股对话框 -->
    <el-dialog v-model="showAddDialog" title="添加自选股" width="400px">
      <el-form :model="addForm" label-width="80px">
        <el-form-item label="股票代码">
          <el-input v-model="addForm.symbol" placeholder="如: 000001.SZ" />
        </el-form-item>
        <el-form-item label="股票名称">
          <el-input v-model="addForm.name" placeholder="可选，系统会自动获取" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddDialog = false">取消</el-button>
        <el-button type="primary" @click="confirmAdd" :loading="adding">添加</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, reactive } from 'vue'
import { Plus } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

interface WatchlistItem {
  symbol: string
  name?: string
  current_price?: number
  change_pct?: number
  volume?: number
  latest_signal?: {
    type: string
    confidence: number
  }
  trend?: string
  update_time?: string
}

interface Props {
  onSelectStock?: (symbol: string) => void
}

const props = defineProps<Props>()
const emit = defineEmits<{
  selectStock: [symbol: string]
}>()

const loading = ref(false)
const adding = ref(false)
const removing = ref('')
const searchSymbol = ref('')
const showAddDialog = ref(false)

const currentPage = ref(1)
const pageSize = ref(20)
const totalItems = ref(0)

const addForm = reactive({
  symbol: '',
  name: ''
})

// 模拟数据
const mockWatchlistData = ref<WatchlistItem[]>([
  {
    symbol: '000001.SZ',
    name: '平安银行',
    current_price: 12.35,
    change_pct: 0.024,
    volume: 125000000,
    latest_signal: { type: 'buy', confidence: 0.85 },
    trend: 'up',
    update_time: new Date().toISOString()
  },
  {
    symbol: '000002.SZ',
    name: '万科A',
    current_price: 18.76,
    change_pct: -0.018,
    volume: 89000000,
    latest_signal: { type: 'sell', confidence: 0.72 },
    trend: 'down',
    update_time: new Date().toISOString()
  },
  {
    symbol: '600519.SH',
    name: '贵州茅台',
    current_price: 1680.50,
    change_pct: 0.012,
    volume: 45000000,
    latest_signal: { type: 'hold', confidence: 0.65 },
    trend: 'sideways',
    update_time: new Date().toISOString()
  }
])

const watchlistData = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  totalItems.value = mockWatchlistData.value.length
  return mockWatchlistData.value.slice(start, end)
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

const getTrendText = (trend: string): string => {
  const texts: Record<string, string> = {
    'up': '上涨',
    'down': '下跌',
    'sideways': '横盘'
  }
  return texts[trend] || trend
}

const getTrendType = (trend: string): string => {
  if (trend === 'up') return 'success'
  if (trend === 'down') return 'danger'
  return 'warning'
}

const formatVolume = (volume: number): string => {
  if (volume >= 100000000) {
    return (volume / 100000000).toFixed(2) + '亿'
  } else if (volume >= 10000) {
    return (volume / 10000).toFixed(2) + '万'
  }
  return volume.toString()
}

const formatTime = (dateStr: string): string => {
  try {
    const date = new Date(dateStr)
    return date.toLocaleTimeString('zh-CN', { 
      hour: '2-digit', 
      minute: '2-digit' 
    })
  } catch {
    return '未知'
  }
}

const selectStock = (row: WatchlistItem) => {
  emit('selectStock', row.symbol)
  if (props.onSelectStock) {
    props.onSelectStock(row.symbol)
  }
}

const addToWatchlist = async () => {
  if (!searchSymbol.value.trim()) {
    ElMessage.warning('请输入股票代码')
    return
  }
  
  adding.value = true
  try {
    // 模拟添加逻辑
    const exists = mockWatchlistData.value.find(item => item.symbol === searchSymbol.value)
    if (exists) {
      ElMessage.warning('该股票已在自选列表中')
      return
    }
    
    mockWatchlistData.value.unshift({
      symbol: searchSymbol.value,
      name: `模拟${searchSymbol.value}`,
      current_price: Math.random() * 100 + 10,
      change_pct: (Math.random() - 0.5) * 0.1,
      volume: Math.floor(Math.random() * 100000000),
      latest_signal: { 
        type: ['buy', 'sell', 'hold'][Math.floor(Math.random() * 3)], 
        confidence: Math.random() 
      },
      trend: ['up', 'down', 'sideways'][Math.floor(Math.random() * 3)],
      update_time: new Date().toISOString()
    })
    
    searchSymbol.value = ''
    ElMessage.success('添加成功')
  } catch (error) {
    console.error('添加失败:', error)
    ElMessage.error('添加失败，请重试')
  } finally {
    adding.value = false
  }
}

const confirmAdd = async () => {
  if (!addForm.symbol.trim()) {
    ElMessage.warning('请输入股票代码')
    return
  }
  
  searchSymbol.value = addForm.symbol
  await addToWatchlist()
  
  if (!adding.value) {
    showAddDialog.value = false
    addForm.symbol = ''
    addForm.name = ''
  }
}

const removeFromWatchlist = async (symbol: string) => {
  try {
    await ElMessageBox.confirm(
      `确认要从自选列表中移除 ${symbol} 吗？`,
      '确认移除',
      {
        confirmButtonText: '确认',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    removing.value = symbol
    
    // 模拟移除逻辑
    const index = mockWatchlistData.value.findIndex(item => item.symbol === symbol)
    if (index > -1) {
      mockWatchlistData.value.splice(index, 1)
      ElMessage.success('移除成功')
    }
  } catch {
    // 用户取消
  } finally {
    removing.value = ''
  }
}

const refreshWatchlist = async () => {
  loading.value = true
  try {
    // 模拟刷新逻辑
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    // 更新数据
    mockWatchlistData.value.forEach(item => {
      item.current_price = (item.current_price || 0) * (1 + (Math.random() - 0.5) * 0.02)
      item.change_pct = (Math.random() - 0.5) * 0.1
      item.update_time = new Date().toISOString()
    })
    
    ElMessage.success('刷新成功')
  } catch (error) {
    console.error('刷新失败:', error)
    ElMessage.error('刷新失败，请重试')
  } finally {
    loading.value = false
  }
}

const handleSizeChange = (val: number) => {
  pageSize.value = val
  currentPage.value = 1
}

const handleCurrentChange = (val: number) => {
  currentPage.value = val
}

onMounted(() => {
  // 可以在这里加载真实数据
})
</script>

<style scoped lang="scss">
.watchlist-table {
  .watchlist-card {
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
  
  .watchlist-content {
    :deep(.el-table) {
      .positive {
        color: #67c23a;
        font-weight: 600;
      }
      
      .negative {
        color: #f56c6c;
        font-weight: 600;
      }
      
      .neutral {
        color: #909399;
      }
      
      .el-table__row {
        cursor: pointer;
        
        &:hover {
          background-color: #f5f7fa;
        }
      }
    }
  }
  
  .pagination {
    margin-top: 20px;
    text-align: center;
  }
  
  .empty-state {
    padding: 40px 20px;
    text-align: center;
  }
}

@media (max-width: 768px) {
  .watchlist-table {
    .card-header {
      flex-direction: column;
      gap: 15px;
      align-items: stretch;
      
      .header-controls {
        justify-content: center;
      }
    }
  }
}
</style>