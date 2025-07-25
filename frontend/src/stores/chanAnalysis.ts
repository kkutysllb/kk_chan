import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { apiService } from '@/services/api'
import type { 
  ChanAnalysisResponse,
  ChanStructure,
  TradingSignal,
  KLineData,
  TechnicalIndicator,
  MultiTimeframeAnalysis,
  RealTimePrediction,
  ChanAnalysisRequest,
  RealTimePredictionRequest,
  MultiTimeframeRequest,
  TradingSignalResponse
} from '@/types/api'

export const useChanAnalysisStore = defineStore('chanAnalysis', () => {
  // 状态
  const analysisResults = ref<Record<string, Record<string, ChanAnalysisResponse['data']>>>({})
  const klineData = ref<Record<string, Record<string, KLineData[]>>>({})
  const technicalIndicators = ref<Record<string, Record<string, TechnicalIndicator[]>>>({})
  const realTimePredictions = ref<Record<string, RealTimePrediction>>({})
  const multiTimeframeAnalysis = ref<Record<string, MultiTimeframeAnalysis>>({})
  const tradingSignals = ref<Record<string, TradingSignalResponse['data']>>({})
  const loading = ref<Record<string, boolean>>({})
  const error = ref<Record<string, string>>({})
  
  // 缓存状态
  const cacheTimestamps = ref<Record<string, number>>({})
  const CACHE_DURATION = 5 * 60 * 1000 // 5分钟缓存

  // 计算属性
  const isLoading = computed(() => (symbol: string, timeframe?: string) => {
    const key = timeframe ? `${symbol}:${timeframe}` : symbol
    return loading.value[key] || false
  })

  const hasError = computed(() => (symbol: string, timeframe?: string) => {
    const key = timeframe ? `${symbol}:${timeframe}` : symbol
    return error.value[key] || null
  })

  // 获取K线数据
  const getKLineData = computed(() => (symbol: string, timeframe: string) => {
    return klineData.value[symbol]?.[timeframe] || []
  })

  // 获取缠论结构
  const getChanStructures = computed(() => (symbol: string, timeframe: string) => {
    const result = analysisResults.value[symbol]?.[timeframe]
    if (!result) return null

    return {
      fenxings: (result as any).fenxings || [],
      bis: (result as any).bis || [],
      xianduan: (result as any).xianduan || [],
      zhongshus: (result as any).zhongshus || []
    }
  })

  // 获取交易信号
  const getTradingSignals = computed(() => (symbol: string, timeframe: string) => {
    return analysisResults.value[symbol]?.[timeframe]?.trading_signals || []
  })

  // 获取技术指标
  const getTechnicalIndicators = computed(() => (symbol: string, timeframe: string) => {
    const data = technicalIndicators.value[symbol]?.[timeframe]
    
    // 如果没有数据，返回空对象而不是空数组，避免.find错误
    if (!data) return {}
    
    // 如果数据是对象格式，直接返回
    if (typeof data === 'object' && !Array.isArray(data)) {
      return data
    }
    
    // 如果是数组格式，也返回（保持兼容性）
    return data
  })

  // 获取实时预测
  const getRealTimePrediction = computed(() => (symbol: string) => {
    return realTimePredictions.value[symbol]
  })

  // 操作方法
  const setLoading = (key: string, value: boolean) => {
    loading.value[key] = value
  }

  const setError = (key: string, value: string | null) => {
    if (value) {
      error.value[key] = value
    } else {
      delete error.value[key]
    }
  }

  const isCacheValid = (key: string): boolean => {
    const timestamp = cacheTimestamps.value[key]
    if (!timestamp) return false
    return Date.now() - timestamp < CACHE_DURATION
  }

  const setCacheTimestamp = (key: string) => {
    cacheTimestamps.value[key] = Date.now()
  }

  // 加载K线数据
  const loadKLineData = async (
    symbol: string, 
    timeframe: string, 
    forceRefresh = false
  ) => {
    const cacheKey = `kline:${symbol}:${timeframe}`
    
    if (!forceRefresh && isCacheValid(cacheKey)) {
      return getKLineData.value(symbol, timeframe)
    }

    const loadingKey = `${symbol}:${timeframe}:kline`
    setLoading(loadingKey, true)
    setError(loadingKey, null)

    try {
      const response = await apiService.getKLineData({
        symbol,
        timeframe,
        limit: 1000,
        include_volume: true
      })

      if (!klineData.value[symbol]) {
        klineData.value[symbol] = {}
      }
      klineData.value[symbol][timeframe] = response.data

      setCacheTimestamp(cacheKey)
      return response.data
    } catch (err: any) {
      const errorMsg = err.message || '加载K线数据失败'
      setError(loadingKey, errorMsg)
      throw new Error(errorMsg)
    } finally {
      setLoading(loadingKey, false)
    }
  }

  // 加载缠论分析
  const loadChanAnalysis = async (
    symbol: string,
    timeframe: string,
    forceRefresh = false
  ) => {
    const cacheKey = `chan:${symbol}:${timeframe}`
    
    if (!forceRefresh && isCacheValid(cacheKey)) {
      return analysisResults.value[symbol]?.[timeframe]
    }

    const loadingKey = `${symbol}:${timeframe}:chan`
    setLoading(loadingKey, true)
    setError(loadingKey, null)

    try {
      const response = await apiService.comprehensiveChanAnalysis({
        symbol,
        timeframes: [timeframe],
        include_ml_prediction: true,
        include_signals: true,
        force_refresh: forceRefresh
      })

      if (!analysisResults.value[symbol]) {
        analysisResults.value[symbol] = {}
      }
      
      // 存储分析结果
      const analysisData = (response as any).timeframe_results?.[timeframe] || response
      analysisResults.value[symbol][timeframe] = analysisData

      setCacheTimestamp(cacheKey)
      return analysisData
    } catch (err: any) {
      const errorMsg = err.message || '加载缠论分析失败'
      setError(loadingKey, errorMsg)
      throw new Error(errorMsg)
    } finally {
      setLoading(loadingKey, false)
    }
  }

  // 加载技术指标
  const loadTechnicalIndicators = async (
    symbol: string,
    timeframe: string,
    forceRefresh = false
  ) => {
    const cacheKey = `indicators:${symbol}:${timeframe}`
    
    if (!forceRefresh && isCacheValid(cacheKey)) {
      return getTechnicalIndicators.value(symbol, timeframe)
    }

    const loadingKey = `${symbol}:${timeframe}:indicators`
    setLoading(loadingKey, true)
    setError(loadingKey, null)

    try {
      const response = await apiService.getTechnicalIndicators({
        symbol,
        timeframe,
        indicators: ['MA', 'MACD', 'RSI', 'BOLL', 'KDJ']
      })

      if (!technicalIndicators.value[symbol]) {
        technicalIndicators.value[symbol] = {}
      }
      
      // 确保数据格式正确
      const indicatorData = response.data || {}
      technicalIndicators.value[symbol][timeframe] = indicatorData

      setCacheTimestamp(cacheKey)
      return indicatorData
    } catch (err: any) {
      const errorMsg = err.message || '加载技术指标失败'
      console.error('技术指标加载错误:', err)
      setError(loadingKey, errorMsg)
      
      // 返回空对象而不是抛出错误，避免中断后续处理
      if (!technicalIndicators.value[symbol]) {
        technicalIndicators.value[symbol] = {}
      }
      technicalIndicators.value[symbol][timeframe] = {}
      
      return {} as any
    } finally {
      setLoading(loadingKey, false)
    }
  }

  // 加载实时预测
  const loadRealTimePrediction = async (request: RealTimePredictionRequest) => {
    const symbol = request.symbol
    const timeframe = request.timeframe || 'daily'
    const loadingKey = `${symbol}:prediction`
    setLoading(loadingKey, true)
    setError(loadingKey, null)

    try {
      const response = await apiService.getRealTimePrediction(request)

      const key = `${symbol}_${timeframe}`
      realTimePredictions.value[key] = response.data
      return response.data
    } catch (err: any) {
      const errorMsg = err.message || '加载实时预测失败'
      setError(loadingKey, errorMsg)
      throw new Error(errorMsg)
    } finally {
      setLoading(loadingKey, false)
    }
  }

  // 加载多时间周期分析
  const loadMultiTimeframeAnalysis = async (
    request: MultiTimeframeRequest
  ) => {
    const symbol = request.symbol
    const timeframes = request.timeframes || ['daily', '30min', '5min']
    const loadingKey = `${symbol}:multi`
    setLoading(loadingKey, true)
    setError(loadingKey, null)

    try {
      const response = await apiService.getMultiTimeframeAnalysis({
        symbol,
        timeframes,
        analysis_depth: 'standard'
      })

      multiTimeframeAnalysis.value[symbol] = response.analysis
      return response.analysis
    } catch (err: any) {
      const errorMsg = err.message || '加载多时间周期分析失败'
      setError(loadingKey, errorMsg)
      throw new Error(errorMsg)
    } finally {
      setLoading(loadingKey, false)
    }
  }

  // 加载交易信号
  const loadTradingSignals = async (request: {
    symbol: string
    timeframes: string[]
    signal_types: string[]
    limit?: number
  }) => {
    const loadingKey = `${request.symbol}:signals`
    setLoading(loadingKey, true)
    setError(loadingKey, null)

    try {
      // 调用后端API获取交易信号
      const response = await apiService.getTradingSignals({
        symbol: request.symbol,
        timeframes: request.timeframes,
        signal_types: request.signal_types,
        limit: request.limit || 50
      })

      const key = `${request.symbol}_${request.timeframes[0]}`
      tradingSignals.value[key] = response.data
      return response.data
    } catch (err: any) {
      const errorMsg = err.message || '加载交易信号失败'
      setError(loadingKey, errorMsg)
      throw new Error(errorMsg)
    } finally {
      setLoading(loadingKey, false)
    }
  }

  // 批量分析
  const batchAnalysis = async (symbols: string[], timeframes: string[] = ['daily']) => {
    const loadingKey = 'batch'
    setLoading(loadingKey, true)
    setError(loadingKey, null)

    try {
      const response = await apiService.batchChanAnalysis({
        symbols,
        timeframes,
        max_concurrent: 5
      })

      // 处理批量结果
      response.results.forEach((result: any) => {
        if (result.success && result.symbol) {
          if (!analysisResults.value[result.symbol]) {
            analysisResults.value[result.symbol] = {}
          }
          
          timeframes.forEach(tf => {
            if ((result as any).timeframe_results?.[tf]) {
              analysisResults.value[result.symbol][tf] = (result as any).timeframe_results[tf]
              setCacheTimestamp(`chan:${result.symbol}:${tf}`)
            }
          })
        }
      })

      return response.results
    } catch (err: any) {
      const errorMsg = err.message || '批量分析失败'
      setError(loadingKey, errorMsg)
      throw new Error(errorMsg)
    } finally {
      setLoading(loadingKey, false)
    }
  }

  // 获取特定交易信号
  const getTradingSignalById = (signalId: string): TradingSignal | null => {
    for (const symbol in analysisResults.value) {
      for (const timeframe in analysisResults.value[symbol]) {
        const signals = analysisResults.value[symbol][timeframe].trading_signals || []
        const signal = signals.find((s: any) => s.id === signalId)
        if (signal) return signal
      }
    }
    return null
  }

  // 获取特定缠论结构
  const getChanStructureById = (structureId: string): ChanStructure | null => {
    for (const symbol in analysisResults.value) {
      for (const timeframe in analysisResults.value[symbol]) {
        const result = analysisResults.value[symbol][timeframe]
        
        // 搜索各种结构类型
        const allStructures = [
          ...(result.fenxings || []),
          ...(result.bis || []),
          ...(result.xianduan || []),
          ...(result.zhongshus || [])
        ]
        
        const structure = allStructures.find((s: any) => s.id === structureId)
        if (structure) return structure
      }
    }
    return null
  }

  // 清除缓存
  const clearCache = (symbol?: string, timeframe?: string) => {
    if (symbol && timeframe) {
      // 清除特定缓存
      const keys = [
        `kline:${symbol}:${timeframe}`,
        `chan:${symbol}:${timeframe}`,
        `indicators:${symbol}:${timeframe}`
      ]
      keys.forEach(key => delete cacheTimestamps.value[key])
    } else if (symbol) {
      // 清除特定股票的所有缓存
      Object.keys(cacheTimestamps.value).forEach(key => {
        if (key.includes(symbol)) {
          delete cacheTimestamps.value[key]
        }
      })
    } else {
      // 清除所有缓存
      cacheTimestamps.value = {}
    }
  }

  // 重置状态
  const resetState = () => {
    analysisResults.value = {}
    klineData.value = {}
    technicalIndicators.value = {}
    realTimePredictions.value = {}
    multiTimeframeAnalysis.value = {}
    tradingSignals.value = {}
    loading.value = {}
    error.value = {}
    cacheTimestamps.value = {}
  }

  return {
    // 状态
    analysisResults,
    klineData,
    technicalIndicators,
    realTimePredictions,
    multiTimeframeAnalysis,
    tradingSignals,
    loading,
    error,
    
    // 计算属性
    isLoading,
    hasError,
    getKLineData,
    getChanStructures,
    getTradingSignals,
    getTechnicalIndicators,
    getRealTimePrediction,
    
    // 方法
    loadKLineData,
    loadChanAnalysis,
    loadTechnicalIndicators,
    loadRealTimePrediction,
    loadMultiTimeframeAnalysis,
    loadTradingSignals,
    batchAnalysis,
    getTradingSignalById,
    getChanStructureById,
    clearCache,
    resetState
  }
})