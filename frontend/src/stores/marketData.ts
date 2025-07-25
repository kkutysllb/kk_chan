import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { MarketData, MarketIndex, SectorData } from '@/types/api'
import { apiService } from '@/services/api'

export const useMarketDataStore = defineStore('marketData', () => {
  // 状态
  const marketIndices = ref<Record<string, MarketIndex>>({})
  const sectorData = ref<Record<string, SectorData[]>>({})
  const marketStats = ref<Record<string, any>>({})
  const heatmapData = ref<Record<string, any>>({})
  const stockCache = ref<Record<string, any>>({}) // 股票数据缓存
  const loading = ref(false)
  const error = ref<string | null>(null)

  // 计算属性
  const getMarketIndex = computed(() => {
    return (symbol: string) => marketIndices.value[symbol]
  })

  const getSectorData = computed(() => {
    return (market: string) => sectorData.value[market] || []
  })

  const getMarketStats = computed(() => {
    return (market: string) => marketStats.value[market]
  })

  // 股票相关的计算属性
  const getStockName = computed(() => {
    return (symbol: string) => {
      return stockCache.value[symbol]?.name || symbol
    }
  })

  const getCurrentPrice = computed(() => {
    return (symbol: string) => {
      return stockCache.value[symbol]?.current_price || 0
    }
  })

  const getPriceChange = computed(() => {
    return (symbol: string) => {
      return stockCache.value[symbol]?.change || 0
    }
  })

  const getPriceChangePercent = computed(() => {
    return (symbol: string) => {
      return stockCache.value[symbol]?.pct_change || 0
    }
  })

  // 操作
  const loadMarketIndices = async (symbols: string[]) => {
    loading.value = true
    error.value = null
    
    try {
      // 模拟加载市场指数数据
      for (const symbol of symbols) {
        marketIndices.value[symbol] = {
          symbol,
          name: getIndexName(symbol),
          current_price: Math.random() * 5000 + 2000,
          change_pct: (Math.random() - 0.5) * 0.06,
          volume: Math.floor(Math.random() * 1000000000),
          timestamp: new Date().toISOString()
        }
      }
    } catch (err) {
      error.value = err instanceof Error ? err.message : '加载市场指数失败'
      throw err
    } finally {
      loading.value = false
    }
  }

  const loadSectorData = async (market: string) => {
    loading.value = true
    error.value = null
    
    try {
      // 模拟加载板块数据
      sectorData.value[market] = [
        { name: '科技股', change_pct: Math.random() * 0.1 - 0.05, stock_count: 342 },
        { name: '金融股', change_pct: Math.random() * 0.1 - 0.05, stock_count: 156 },
        { name: '消费股', change_pct: Math.random() * 0.1 - 0.05, stock_count: 298 },
        { name: '地产股', change_pct: Math.random() * 0.1 - 0.05, stock_count: 89 },
        { name: '医药股', change_pct: Math.random() * 0.1 - 0.05, stock_count: 234 },
        { name: '制造业', change_pct: Math.random() * 0.1 - 0.05, stock_count: 567 }
      ]
    } catch (err) {
      error.value = err instanceof Error ? err.message : '加载板块数据失败'
      throw err
    } finally {
      loading.value = false
    }
  }

  const loadMarketStats = async (market: string) => {
    loading.value = true
    error.value = null
    
    try {
      // 模拟加载市场统计数据
      marketStats.value[market] = {
        rising_count: Math.floor(Math.random() * 1000) + 1500,
        falling_count: Math.floor(Math.random() * 1000) + 1200,
        flat_count: Math.floor(Math.random() * 300) + 100,
        suspended_count: Math.floor(Math.random() * 100) + 20,
        total_volume: Math.floor(Math.random() * 50000000000) + 10000000000,
        total_amount: Math.floor(Math.random() * 500000000000) + 100000000000,
        avg_turnover: Math.random() * 0.1 + 0.02
      }
    } catch (err) {
      error.value = err instanceof Error ? err.message : '加载市场统计失败'
      throw err
    } finally {
      loading.value = false
    }
  }

  const loadHeatmapData = async (market: string, metric: string) => {
    loading.value = true
    error.value = null
    
    try {
      const key = `${market}_${metric}`
      // 模拟生成热力图数据
      heatmapData.value[key] = {
        data: generateHeatmapData(),
        timestamp: new Date().toISOString()
      }
    } catch (err) {
      error.value = err instanceof Error ? err.message : '加载热力图数据失败'
      throw err
    } finally {
      loading.value = false
    }
  }

  const refreshAllData = async (market: string) => {
    await Promise.all([
      loadMarketIndices(['000001.SH', '399001.SZ', '399006.SZ', '000300.SH']),
      loadSectorData(market),
      loadMarketStats(market),
      loadHeatmapData(market, 'chan_strength')
    ])
  }

  // 辅助函数
  const getIndexName = (symbol: string): string => {
    const names: Record<string, string> = {
      '000001.SH': '上证指数',
      '399001.SZ': '深证成指',
      '399006.SZ': '创业板指',
      '000300.SH': '沪深300',
      '000905.SH': '中证500'
    }
    return names[symbol] || symbol
  }

  const generateHeatmapData = () => {
    const sectors = ['科技', '金融', '消费', '医药', '地产', '制造', '能源', '材料']
    const data = []
    
    for (let i = 0; i < 8; i++) {
      for (let j = 0; j < 8; j++) {
        data.push({
          x: i,
          y: j,
          value: Math.random() * 10 - 5,
          sector: sectors[i % sectors.length],
          symbol: `${String.fromCharCode(65 + i)}${j.toString().padStart(2, '0')}`,
          name: `股票${i}${j}`
        })
      }
    }
    
    return data
  }

  // 更新实时数据
  const updateRealTimeData = async (symbol: string) => {
    loading.value = true
    try {
      // 模拟更新实时数据
      await new Promise(resolve => setTimeout(resolve, 500))
      
      // 这里应该调用实时数据API
      console.log(`更新 ${symbol} 的实时数据`)
    } catch (err) {
      error.value = err instanceof Error ? err.message : '更新实时数据失败'
      throw err
    } finally {
      loading.value = false
    }
  }

  // 批量更新实时数据
  const batchUpdateRealTimeData = async (symbols: string[]) => {
    loading.value = true
    try {
      // 模拟批量更新实时数据
      await new Promise(resolve => setTimeout(resolve, 1000))
      
      // 这里应该调用批量实时数据API
      console.log(`批量更新 ${symbols.length} 只股票的实时数据`)
    } catch (err) {
      error.value = err instanceof Error ? err.message : '批量更新实时数据失败'
      throw err
    } finally {
      loading.value = false
    }
  }

  // 加载股票基本信息
  const loadStockInfo = async (symbol: string) => {
    if (stockCache.value[symbol]) {
      return stockCache.value[symbol]
    }

    loading.value = true
    try {
      const response = await apiService.getStockInfo(symbol)
      stockCache.value[symbol] = response.data
      return response.data
    } catch (err) {
      error.value = err instanceof Error ? err.message : '加载股票信息失败'
      // 设置默认值避免错误
      stockCache.value[symbol] = {
        name: symbol,
        current_price: 0,
        change: 0,
        pct_change: 0
      }
      throw err
    } finally {
      loading.value = false
    }
  }

  return {
    // 状态
    marketIndices,
    sectorData,
    marketStats,
    heatmapData,
    stockCache,
    loading,
    error,
    
    // 计算属性
    getMarketIndex,
    getSectorData,
    getMarketStats,
    getStockName,
    getCurrentPrice,
    getPriceChange,
    getPriceChangePercent,
    
    // 操作
    loadMarketIndices,
    loadSectorData,
    loadMarketStats,
    loadHeatmapData,
    loadStockInfo,
    refreshAllData,
    updateRealTimeData,
    batchUpdateRealTimeData
  }
})