import { defineStore } from 'pinia'
import { pythonApi } from '@/utils/api'

export const useGlobalStore = defineStore('global', {
  state: () => ({
    // 应用状态
    loading: false,
    error: null,
    
    // 股票数据
    currentSymbol: '',
    currentTimeframe: 'daily',
    currentDays: 90,
    
    // 分析数据
    analysisData: null,
    lastUpdateTime: null,
    
    // 界面状态
    sidebarCollapsed: false,
    activeTab: 'chart',
  }),

  getters: {
    // 获取当前分析的股票信息
    currentStock() {
      return {
        symbol: this.currentSymbol,
        timeframe: this.currentTimeframe,
        days: this.currentDays,
      }
    },

    // 获取图表数据
    chartData() {
      return this.analysisData?.chart_data || null
    },

    // 获取分析摘要
    analysisSummary() {
      return this.analysisData?.analysis?.summary || null
    },

    // 获取分析评估
    analysisEvaluation() {
      return this.analysisData?.analysis?.evaluation || null
    },

    // 获取K线数据
    klineData() {
      return this.analysisData?.chart_data?.kline || null
    },

    // 获取缠论结构数据
    chanStructures() {
      console.log('获取缠论结构数据:', this.analysisData?.chart_data?.chan_structures)
      return this.analysisData?.chart_data?.chan_structures || null
    },

    // 获取交易信号 - 基于缠论v2引擎数据结构
    tradingSignals() {
      console.log('获取交易信号:', this.analysisData?.chart_data?.dynamics)
      return {
        buy_sell_points: this.analysisData?.chart_data?.dynamics?.buy_sell_points || [],
        backchi_analyses: this.analysisData?.chart_data?.dynamics?.backchi || []
      }
    },

    // 获取买卖点信号 - 对应缠论v2的BuySellPoint
    buySellingPoints() {
      return this.analysisData?.chart_data?.dynamics?.buy_sell_points || []
    },

    // 获取背驰信号 - 对应缠论v2的BackChiAnalysis
    backchiSignals() {
      return this.analysisData?.chart_data?.dynamics?.backchi || []
    },

    // 获取缠论结构统计信息
    chanStatistics() {
      return this.analysisData?.analysis?.summary || null
    },

    // 获取趋势分析
    trendAnalysis() {
      const evaluation = this.analysisData?.analysis?.evaluation
      if (!evaluation) return null
      
      return {
        trend_direction: evaluation.trend_direction,
        trend_strength: evaluation.trend_strength,
        confidence_score: evaluation.confidence_score,
        risk_level: evaluation.risk_level,
        recommended_action: evaluation.recommended_action,
        entry_price: evaluation.entry_price,
        stop_loss: evaluation.stop_loss,
        take_profit: evaluation.take_profit
      }
    },

    // 是否有数据
    hasData() {
      return !!this.analysisData
    },

    // 调试：获取完整数据结构
    debugData() {
      console.log('完整数据结构:', this.analysisData)
      return this.analysisData
    },
  },

  actions: {
    // 设置加载状态
    setLoading(loading) {
      this.loading = loading
    },

    // 设置错误
    setError(error) {
      this.error = error
    },

    // 清除错误
    clearError() {
      this.error = null
    },

    // 设置当前股票
    setCurrentStock({ symbol, timeframe, days }) {
      if (symbol) this.currentSymbol = symbol
      if (timeframe) this.currentTimeframe = timeframe
      if (days) this.currentDays = days
    },

    // 获取分析数据
    async fetchAnalysisData(params = {}) {
      this.setLoading(true)
      this.clearError()

      try {
        const requestParams = {
          symbol: params.symbol || this.currentSymbol,
          timeframe: params.timeframe || this.currentTimeframe,
          days: params.days || this.currentDays,
        }

        console.log('获取分析数据:', requestParams)
        
        const data = await pythonApi.getAnalysisData(requestParams)
        
        this.analysisData = data
        this.lastUpdateTime = new Date()
        
        // 更新当前参数
        this.setCurrentStock(requestParams)
        
        console.log('分析数据获取成功:', data)
        return data
      } catch (error) {
        console.error('获取分析数据失败:', error)
        this.setError(error.message || '获取数据失败')
        throw error
      } finally {
        this.setLoading(false)
      }
    },

    // 刷新所有数据
    async refreshAllData() {
      return this.fetchAnalysisData()
    },

    // 切换侧边栏
    toggleSidebar() {
      this.sidebarCollapsed = !this.sidebarCollapsed
    },

    // 设置活动标签
    setActiveTab(tab) {
      this.activeTab = tab
    },

    // 重置状态
    reset() {
      this.analysisData = null
      this.lastUpdateTime = null
      this.error = null
      this.loading = false
    },
  },

  // 持久化配置
  persist: {
    key: 'kk-chan-global',
    storage: localStorage,
    paths: [
      'currentSymbol',
      'currentTimeframe', 
      'currentDays',
      'sidebarCollapsed',
      'activeTab',
    ],
  },
})