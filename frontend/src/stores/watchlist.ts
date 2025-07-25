import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { WatchlistItem } from '@/types/api'
import { apiService } from '@/services/api'

export const useWatchlistStore = defineStore('watchlist', () => {
  // 状态
  const watchlist = ref<WatchlistItem[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  // 计算属性
  const watchlistCount = computed(() => watchlist.value.length)
  
  const getWatchlist = computed(() => watchlist.value)
  
  const getStockBySymbol = computed(() => {
    return (symbol: string) => watchlist.value.find(item => item.symbol === symbol)
  })

  const isInWatchlist = computed(() => {
    return (symbol: string) => watchlist.value.some(item => item.symbol === symbol)
  })

  // 操作
  const loadWatchlist = async () => {
    loading.value = true
    error.value = null
    
    try {
      // 模拟加载自选股数据
      watchlist.value = [
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
      ]
    } catch (err) {
      error.value = err instanceof Error ? err.message : '加载自选股失败'
      throw err
    } finally {
      loading.value = false
    }
  }

  const addToWatchlist = async (symbol: string, name?: string) => {
    if (isInWatchlist.value(symbol)) {
      throw new Error('该股票已在自选列表中')
    }

    loading.value = true
    error.value = null
    
    try {
      // 模拟添加自选股
      const newItem: WatchlistItem = {
        symbol,
        name: name || `模拟${symbol}`,
        current_price: Math.random() * 100 + 10,
        change_pct: (Math.random() - 0.5) * 0.1,
        volume: Math.floor(Math.random() * 100000000),
        latest_signal: { 
          type: ['buy', 'sell', 'hold'][Math.floor(Math.random() * 3)] as 'buy' | 'sell' | 'hold', 
          confidence: Math.random() 
        },
        trend: ['up', 'down', 'sideways'][Math.floor(Math.random() * 3)] as 'up' | 'down' | 'sideways',
        update_time: new Date().toISOString()
      }
      
      watchlist.value.unshift(newItem)
    } catch (err) {
      error.value = err instanceof Error ? err.message : '添加自选股失败'
      throw err
    } finally {
      loading.value = false
    }
  }

  const removeFromWatchlist = async (symbol: string) => {
    const index = watchlist.value.findIndex(item => item.symbol === symbol)
    if (index === -1) {
      throw new Error('未找到该股票')
    }

    loading.value = true
    error.value = null
    
    try {
      watchlist.value.splice(index, 1)
    } catch (err) {
      error.value = err instanceof Error ? err.message : '移除自选股失败'
      throw err
    } finally {
      loading.value = false
    }
  }

  const updateWatchlist = async () => {
    loading.value = true
    error.value = null
    
    try {
      // 模拟更新数据
      watchlist.value.forEach(item => {
        item.current_price = (item.current_price || 0) * (1 + (Math.random() - 0.5) * 0.02)
        item.change_pct = (Math.random() - 0.5) * 0.1
        item.update_time = new Date().toISOString()
      })
    } catch (err) {
      error.value = err instanceof Error ? err.message : '更新自选股失败'
      throw err
    } finally {
      loading.value = false
    }
  }

  const clearWatchlist = async () => {
    loading.value = true
    error.value = null
    
    try {
      watchlist.value = []
    } catch (err) {
      error.value = err instanceof Error ? err.message : '清空自选股失败'
      throw err
    } finally {
      loading.value = false
    }
  }

  return {
    // 状态
    watchlist,
    loading,
    error,
    
    // 计算属性
    watchlistCount,
    getWatchlist,
    getStockBySymbol,
    isInWatchlist,
    
    // 操作
    loadWatchlist,
    addToWatchlist,
    removeFromWatchlist,
    updateWatchlist,
    clearWatchlist
  }
})