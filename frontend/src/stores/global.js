import { defineStore } from 'pinia'
import { pythonApi } from '@/utils/api'

export const useGlobalStore = defineStore('global', {
  state: () => ({
    // 应用状态
    loading: false,
    error: null,
    
    // 股票数据
    currentSymbol: '',
    currentTimeframe: '30min',
    currentDays: 90,
    analysisMode: 'multi-level', // 新增：分析模式
    levels: ['daily', '30min', '5min'], // 新增：多级别分析的级别
    
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

    // 获取图表数据 - 兼容单级别和多级别API
    chartData() {
      // 多级别API：根据当前选择的时间周期返回对应数据
      if (this.analysisData?.results) {
        // 将前端时间周期格式转换为API格式
        const timeframeMapping = {
          '5min': '5min',
          '30min': '30min', 
          'daily': 'daily'
        }
        const apiTimeframe = timeframeMapping[this.currentTimeframe] || '30min'
        const levelData = this.analysisData.results[apiTimeframe]
        
        if (levelData) {
          return {
            kline: levelData.kline || [],
            chan_structures: levelData.structures || {},
            dynamics: levelData.dynamics || {},
            indicators: levelData.indicators || {}
          }
        }
        
        // 如果当前选择的周期没有数据，回退到可用的数据
        const fallbackLevel = this.analysisData.results['30min'] || this.analysisData.results['daily'] || this.analysisData.results['5min']
        if (fallbackLevel) {
          return {
            kline: fallbackLevel.kline || [],
            chan_structures: fallbackLevel.structures || {},
            dynamics: fallbackLevel.dynamics || {},
            indicators: fallbackLevel.indicators || {}
          }
        }
      }
      // 单级别API：直接返回chart_data
      return this.analysisData?.chart_data || null
    },

    // 获取分析摘要 - 兼容单级别和多级别API
    analysisSummary() {
      // 多级别API：根据当前选择的时间周期返回对应统计信息
      if (this.analysisData?.results) {
        const timeframeMapping = {
          '5min': '5min',
          '30min': '30min', 
          'daily': 'daily'
        }
        const apiTimeframe = timeframeMapping[this.currentTimeframe] || '30min'
        const levelData = this.analysisData.results[apiTimeframe]
        
        if (levelData?.structures) {
          const structures = levelData.structures
          const dynamics = levelData.dynamics || {}
          return {
            fenxing_count: structures.fenxing_count || 0,
            bi_count: structures.bi_count || 0,
            seg_count: structures.seg_count || 0,
            zhongshu_count: structures.zhongshu_count || 0,
            signal_count: (dynamics.buy_sell_points_count || 0) + (dynamics.backchi_count || 0)
          }
        }
        
        // 回退到可用数据
        const fallbackLevel = this.analysisData.results['30min'] || this.analysisData.results['daily'] || this.analysisData.results['5min']
        if (fallbackLevel?.structures) {
          const structures = fallbackLevel.structures
          const dynamics = fallbackLevel.dynamics || {}
          return {
            fenxing_count: structures.fenxing_count || 0,
            bi_count: structures.bi_count || 0,
            seg_count: structures.seg_count || 0,
            zhongshu_count: structures.zhongshu_count || 0,
            signal_count: (dynamics.buy_sell_points_count || 0) + (dynamics.backchi_count || 0)
          }
        }
        return null
      }
      // 单级别API：返回analysis.summary
      return this.analysisData?.analysis?.summary || null
    },

    // 获取分析评估 - 兼容单级别和多级别API
    analysisEvaluation() {
      // 多级别API：根据当前选择的时间周期返回对应数据
      if (this.analysisData?.results) {
        const timeframeMapping = {
          '5min': '5min',
          '30min': '30min', 
          'daily': 'daily'
        }
        const apiTimeframe = timeframeMapping[this.currentTimeframe] || '30min'
        const levelData = this.analysisData.results[apiTimeframe]
        
        if (levelData?.evaluation) {
          return levelData.evaluation
        }
        
        // 如果当前选择的周期没有评估数据，回退到可用的数据
        const fallbackLevel = this.analysisData.results['30min'] || this.analysisData.results['daily']
        return fallbackLevel?.evaluation || null
      }
      // 单级别API：返回analysis.evaluation
      return this.analysisData?.analysis?.evaluation || null
    },

    // 获取K线数据 - 兼容单级别和多级别API
    klineData() {
      // 多级别API：根据当前选择的时间周期返回对应数据
      if (this.analysisData?.results) {
        const timeframeMapping = {
          '5min': '5min',
          '30min': '30min', 
          'daily': 'daily'
        }
        const apiTimeframe = timeframeMapping[this.currentTimeframe] || '30min'
        const levelData = this.analysisData.results[apiTimeframe]
        
        if (levelData?.kline) {
          return levelData.kline
        }
        
        // 如果当前选择的周期没有数据，回退到可用的数据
        const fallbackLevel = this.analysisData.results['30min'] || this.analysisData.results['daily'] || this.analysisData.results['5min']
        return fallbackLevel?.kline || []
      }
      // 单级别API：返回chart_data.kline
      return this.analysisData?.chart_data?.kline || []
    },

    // 获取缠论结构数据 - 兼容单级别和多级别API
    chanStructures() {
      // 多级别API：根据当前选择的时间周期返回对应数据
      if (this.analysisData?.results) {
        const timeframeMapping = {
          '5min': '5min',
          '30min': '30min', 
          'daily': 'daily'
        }
        const apiTimeframe = timeframeMapping[this.currentTimeframe] || '30min'
        const levelData = this.analysisData.results[apiTimeframe]
        
        if (levelData?.structures) {
          const structures = levelData.structures
          console.log(`获取缠论结构数据(多级别-${apiTimeframe}):`, structures)
          return structures
        }
        
        // 如果当前选择的周期没有数据，回退到可用的数据
        const fallbackLevel = this.analysisData.results['30min'] || this.analysisData.results['daily'] || this.analysisData.results['5min']
        const structures = fallbackLevel?.structures || {}
        console.log('获取缠论结构数据(多级别-回退):', structures)
        return structures
      }
      // 单级别API：返回chart_data.chan_structures
      console.log('获取缠论结构数据(单级别):', this.analysisData?.chart_data?.chan_structures)
      return this.analysisData?.chart_data?.chan_structures || null
    },

    // 获取交易信号 - 兼容单级别和多级别API
    tradingSignals() {
      // 多级别API：根据当前选择的时间周期返回对应数据
      if (this.analysisData?.results) {
        const timeframeMapping = {
          '5min': '5min',
          '30min': '30min', 
          'daily': 'daily'
        }
        const apiTimeframe = timeframeMapping[this.currentTimeframe] || '30min'
        const levelData = this.analysisData.results[apiTimeframe]
        
        if (levelData?.dynamics) {
          const dynamics = levelData.dynamics
          console.log(`获取交易信号(多级别-${apiTimeframe}):`, dynamics)
          return {
            buy_sell_points: dynamics.buy_sell_points || [],
            backchi_analyses: dynamics.backchi || []
          }
        }
        
        // 如果当前选择的周期没有数据，回退到可用的数据
        const fallbackLevel = this.analysisData.results['30min'] || this.analysisData.results['daily'] || this.analysisData.results['5min']
        const dynamics = fallbackLevel?.dynamics || {}
        console.log('获取交易信号(多级别-回退):', dynamics)
        return {
          buy_sell_points: dynamics.buy_sell_points || [],
          backchi_analyses: dynamics.backchi || []
        }
      }
      // 单级别API：返回chart_data.dynamics
      console.log('获取交易信号(单级别):', this.analysisData?.chart_data?.dynamics)
      return {
        buy_sell_points: this.analysisData?.chart_data?.dynamics?.buy_sell_points || [],
        backchi_analyses: this.analysisData?.chart_data?.dynamics?.backchi || []
      }
    },

    // 获取买卖点信号 - 兼容单级别和多级别API数据结构
    buySellingPoints() {
      // 检查是否为多级别API数据结构
      if (this.analysisData?.results) {
        const allSignals = []
        const levels = ['daily', '30min', '5min']
        levels.forEach(level => {
          const levelData = this.analysisData.results[level]
          if (levelData?.dynamics?.buy_sell_points) {
            // 为每个信号添加时间级别信息
            const signals = levelData.dynamics.buy_sell_points.map(signal => ({
              ...signal,
              timeframe: level === 'daily' ? '日线' : (level === '30min' ? '30分钟' : '5分钟')
            }))
            allSignals.push(...signals)
          }
        })
        return allSignals
      }
      // 兼容单级别API数据结构
      return this.analysisData?.chart_data?.dynamics?.buy_sell_points || []
    },

    // 获取背驰信号 - 兼容单级别和多级别API数据结构
    backchiSignals() {
      // 检查是否为多级别API数据结构
      if (this.analysisData?.results) {
        const allSignals = []
        const levels = ['daily', '30min', '5min']
        levels.forEach(level => {
          const levelData = this.analysisData.results[level]
          if (levelData?.dynamics?.backchi) {
            // 为每个信号添加时间级别信息
            const signals = levelData.dynamics.backchi.map(signal => ({
              ...signal,
              timeframe: level === 'daily' ? '日线' : (level === '30min' ? '30分钟' : '5分钟')
            }))
            allSignals.push(...signals)
          }
        })
        return allSignals
      }
      // 兼容单级别API数据结构
      return this.analysisData?.chart_data?.dynamics?.backchi || []
    },

    // 获取缠论结构统计信息 - 兼容单级别和多级别API
    chanStatistics() {
      // 多级别API：根据当前选择的时间周期返回对应数据
      if (this.analysisData?.results) {
        const timeframeMapping = {
          '5min': '5min',
          '30min': '30min', 
          'daily': 'daily'
        }
        const apiTimeframe = timeframeMapping[this.currentTimeframe] || '30min'
        const levelData = this.analysisData.results[apiTimeframe]
        
        if (levelData?.structures) {
          return levelData.structures
        }
        
        // 如果当前选择的周期没有数据，回退到可用的数据
        const fallbackLevel = this.analysisData.results['30min'] || this.analysisData.results['daily'] || this.analysisData.results['5min']
        return fallbackLevel?.structures || null
      }
      // 单级别API：返回analysis.summary
      return this.analysisData?.analysis?.summary || null
    },

    // 获取趋势分析 - 兼容单级别和多级别API
    trendAnalysis() {
      // 多级别API：根据当前选择的时间周期返回对应数据
      if (this.analysisData?.results) {
        const timeframeMapping = {
          '5min': '5min',
          '30min': '30min', 
          'daily': 'daily'
        }
        const apiTimeframe = timeframeMapping[this.currentTimeframe] || '30min'
        const levelData = this.analysisData.results[apiTimeframe]
        
        let evaluation = levelData?.evaluation
        if (!evaluation) {
          // 如果当前选择的周期没有评估数据，回退到可用的数据
          const fallbackLevel = this.analysisData.results['30min'] || this.analysisData.results['daily']
          evaluation = fallbackLevel?.evaluation
        }
        
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
      }
      
      // 单级别API：使用analysis.evaluation
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
    setCurrentStock({ symbol, timeframe, days, analysisMode, levels }) {
      if (symbol) this.currentSymbol = symbol
      if (timeframe) this.currentTimeframe = timeframe
      if (days) this.currentDays = days
      if (analysisMode !== undefined) this.analysisMode = analysisMode
      if (levels) this.levels = levels
    },

    // 获取分析数据（支持多级别和单级别分析）
    async fetchAnalysisData(params = {}) {
      this.setLoading(true)
      this.clearError()

      try {
        const analysisMode = params.analysisMode || this.analysisMode || 'multi-level'
        
        let data
        if (analysisMode === 'multi-level') {
          // 多级别分析
          const requestParams = {
            symbol: params.symbol || this.currentSymbol,
            levels: params.levels || this.levels || ['daily', '30min', '5min'],
            days: params.days || this.currentDays,
          }
          console.log('获取多级别分析数据:', requestParams)
          data = await pythonApi.getAnalysisData(requestParams)
        } else {
          // 单级别分析
          const requestParams = {
            symbol: params.symbol || this.currentSymbol,
            timeframe: params.timeframe || this.currentTimeframe,
            days: params.days || this.currentDays,
          }
          console.log('获取单级别分析数据:', requestParams)
          data = await pythonApi.getSingleLevelAnalysisData(requestParams)
        }
        
        this.analysisData = data
        this.lastUpdateTime = new Date()
        
        // 更新当前参数
        this.setCurrentStock({
          symbol: params.symbol || this.currentSymbol,
          analysisMode: analysisMode,
          timeframe: params.timeframe,
          levels: params.levels,
          days: params.days || this.currentDays
        })
        
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