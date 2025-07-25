<template>
  <div class="market-view">
    <div class="market-header">
      <h2 class="page-title">市场概览</h2>
      <div class="header-controls">
        <el-select v-model="selectedMarket" size="small" style="width: 120px; margin-right: 10px;">
          <el-option label="A股" value="A股" />
          <el-option label="港股" value="港股" />
          <el-option label="美股" value="美股" />
        </el-select>
        <el-button type="primary" size="small" @click="refreshMarketData" :loading="loading">
          刷新
        </el-button>
      </div>
    </div>
    
    <!-- 市场指数 -->
    <div class="market-indices">
      <el-row :gutter="20">
        <el-col :span="6" v-for="index in marketIndices" :key="index.symbol">
          <el-card class="index-card">
            <div class="index-info">
              <div class="index-name">{{ index.name }}</div>
              <div class="index-price">{{ index.current_price.toFixed(2) }}</div>
              <div 
                class="index-change"
                :class="{
                  'positive': index.change_pct > 0,
                  'negative': index.change_pct < 0,
                  'neutral': index.change_pct === 0
                }"
              >
                {{ index.change_pct > 0 ? '+' : '' }}{{ (index.change_pct * 100).toFixed(2) }}%
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>
    
    <!-- 市场热力图 -->
    <div class="market-heatmap" style="margin-top: 30px;">
      <MarketHeatmap :market="selectedMarket" />
    </div>
    
    <!-- 板块表现 -->
    <div class="sector-performance" style="margin-top: 30px;">
      <el-card>
        <template #header>
          <div class="card-header">
            <span class="title">板块表现</span>
            <el-radio-group v-model="sectorTimeframe" size="small">
              <el-radio-button value="1D">日</el-radio-button>
              <el-radio-button value="5D">5日</el-radio-button>
              <el-radio-button value="1M">月</el-radio-button>
            </el-radio-group>
          </div>
        </template>
        
        <div class="sector-grid">
          <div 
            v-for="sector in sectorData" 
            :key="sector.name"
            class="sector-item"
            @click="viewSectorDetail(sector)"
          >
            <div class="sector-name">{{ sector.name }}</div>
            <div 
              class="sector-change"
              :class="{
                'positive': sector.change_pct > 0,
                'negative': sector.change_pct < 0,
                'neutral': sector.change_pct === 0
              }"
            >
              {{ sector.change_pct > 0 ? '+' : '' }}{{ (sector.change_pct * 100).toFixed(2) }}%
            </div>
            <div class="sector-stocks">{{ sector.stock_count }}只股票</div>
          </div>
        </div>
      </el-card>
    </div>
    
    <!-- 市场统计 -->
    <div class="market-stats" style="margin-top: 30px;">
      <el-row :gutter="20">
        <el-col :span="12">
          <el-card>
            <template #header>
              <span class="title">上涨下跌统计</span>
            </template>
            <div class="stats-content">
              <div class="stat-item">
                <span class="stat-label">上涨:</span>
                <span class="stat-value positive">{{ marketStats.rising_count }}</span>
              </div>
              <div class="stat-item">
                <span class="stat-label">下跌:</span>
                <span class="stat-value negative">{{ marketStats.falling_count }}</span>
              </div>
              <div class="stat-item">
                <span class="stat-label">持平:</span>
                <span class="stat-value neutral">{{ marketStats.flat_count }}</span>
              </div>
              <div class="stat-item">
                <span class="stat-label">停牌:</span>
                <span class="stat-value">{{ marketStats.suspended_count }}</span>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="12">
          <el-card>
            <template #header>
              <span class="title">成交量统计</span>
            </template>
            <div class="stats-content">
              <div class="stat-item">
                <span class="stat-label">总成交量:</span>
                <span class="stat-value">{{ formatVolume(marketStats.total_volume) }}</span>
              </div>
              <div class="stat-item">
                <span class="stat-label">总成交额:</span>
                <span class="stat-value">{{ formatAmount(marketStats.total_amount) }}</span>
              </div>
              <div class="stat-item">
                <span class="stat-label">平均换手率:</span>
                <span class="stat-value">{{ (marketStats.avg_turnover * 100).toFixed(2) }}%</span>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import MarketHeatmap from '@/components/charts/MarketHeatmap.vue'

const loading = ref(false)
const selectedMarket = ref('A股')
const sectorTimeframe = ref('1D')

// 模拟市场指数数据
const marketIndices = ref([
  {
    symbol: '000001.SH',
    name: '上证指数',
    current_price: 3245.67,
    change_pct: 0.012
  },
  {
    symbol: '399001.SZ',
    name: '深证成指',
    current_price: 12456.78,
    change_pct: -0.008
  },
  {
    symbol: '399006.SZ',
    name: '创业板指',
    current_price: 2987.34,
    change_pct: 0.025
  },
  {
    symbol: '000300.SH',
    name: '沪深300',
    current_price: 4123.45,
    change_pct: 0.018
  }
])

// 模拟板块数据
const sectorData = ref([
  { name: '科技股', change_pct: 0.035, stock_count: 342 },
  { name: '金融股', change_pct: 0.012, stock_count: 156 },
  { name: '消费股', change_pct: -0.008, stock_count: 298 },
  { name: '地产股', change_pct: -0.025, stock_count: 89 },
  { name: '医药股', change_pct: 0.028, stock_count: 234 },
  { name: '制造业', change_pct: 0.015, stock_count: 567 },
  { name: '能源股', change_pct: -0.012, stock_count: 123 },
  { name: '农业股', change_pct: 0.008, stock_count: 78 }
])

// 模拟市场统计数据
const marketStats = reactive({
  rising_count: 2134,
  falling_count: 1876,
  flat_count: 234,
  suspended_count: 45,
  total_volume: 15600000000,
  total_amount: 245000000000,
  avg_turnover: 0.035
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

const refreshMarketData = async () => {
  loading.value = true
  try {
    // 模拟数据刷新
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    // 更新指数数据
    marketIndices.value.forEach(index => {
      index.current_price *= (1 + (Math.random() - 0.5) * 0.02)
      index.change_pct = (Math.random() - 0.5) * 0.05
    })
    
    // 更新板块数据
    sectorData.value.forEach(sector => {
      sector.change_pct = (Math.random() - 0.5) * 0.06
    })
    
    ElMessage.success('市场数据刷新成功')
  } catch (error) {
    console.error('刷新失败:', error)
    ElMessage.error('数据刷新失败，请重试')
  } finally {
    loading.value = false
  }
}

const viewSectorDetail = (sector: any) => {
  ElMessage.info(`查看 ${sector.name} 详情（功能开发中）`)
}

onMounted(() => {
  refreshMarketData()
})
</script>

<style scoped lang="scss">
.market-view {
  padding: 20px;
  
  .market-header {
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
      align-items: center;
    }
  }
  
  .market-indices {
    .index-card {
      text-align: center;
      cursor: pointer;
      transition: all 0.3s ease;
      
      &:hover {
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        transform: translateY(-2px);
      }
      
      .index-info {
        .index-name {
          font-size: 14px;
          color: #606266;
          margin-bottom: 8px;
        }
        
        .index-price {
          font-size: 22px;
          font-weight: 600;
          color: #303133;
          margin-bottom: 8px;
        }
        
        .index-change {
          font-size: 14px;
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
  }
  
  .sector-performance {
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
    
    .sector-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 15px;
      
      .sector-item {
        padding: 15px;
        border: 1px solid #ebeef5;
        border-radius: 8px;
        cursor: pointer;
        transition: all 0.3s ease;
        
        &:hover {
          box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
          transform: translateY(-1px);
        }
        
        .sector-name {
          font-size: 14px;
          font-weight: 500;
          color: #303133;
          margin-bottom: 8px;
        }
        
        .sector-change {
          font-size: 16px;
          font-weight: 600;
          margin-bottom: 4px;
          
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
        
        .sector-stocks {
          font-size: 12px;
          color: #909399;
        }
      }
    }
  }
  
  .market-stats {
    .title {
      font-size: 16px;
      font-weight: 600;
      color: #303133;
    }
    
    .stats-content {
      .stat-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 12px;
        
        &:last-child {
          margin-bottom: 0;
        }
        
        .stat-label {
          font-size: 14px;
          color: #606266;
        }
        
        .stat-value {
          font-size: 16px;
          font-weight: 600;
          color: #303133;
          
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
  }
}

@media (max-width: 768px) {
  .market-view {
    padding: 10px;
    
    .market-header {
      flex-direction: column;
      gap: 15px;
      align-items: stretch;
    }
    
    .market-indices {
      :deep(.el-col) {
        margin-bottom: 15px;
      }
    }
    
    .sector-grid {
      grid-template-columns: 1fr;
    }
  }
}
</style>