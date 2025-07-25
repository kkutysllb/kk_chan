/**
 * API服务层
 * 封装所有后端API调用
 */

import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios'
import { ElMessage } from 'element-plus'
import type {
  ChanAnalysisRequest,
  ChanAnalysisResponse,
  BatchAnalysisRequest,
  BatchAnalysisResponse,
  KLineRequest,
  KLineResponse,
  TechnicalIndicatorRequest,
  TechnicalIndicatorResponse,
  RealTimePredictionRequest,
  RealTimePredictionResponse,
  MultiTimeframeRequest,
  MultiTimeframeResponse,
  ChartDataRequest,
  ChartDataResponse
} from '@/types/api'

class ApiService {
  private instance: AxiosInstance
  private baseURL: string

  constructor() {
    this.baseURL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
    
    this.instance = axios.create({
      baseURL: this.baseURL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      }
    })

    this.setupInterceptors()
  }

  private setupInterceptors() {
    // 请求拦截器
    this.instance.interceptors.request.use(
      (config) => {
        // 添加认证token
        const token = localStorage.getItem('access_token')
        if (token) {
          config.headers.Authorization = `Bearer ${token}`
        }

        // 添加请求ID用于追踪
        config.headers['X-Request-ID'] = this.generateRequestId()

        // 显示加载状态
        if (config.showLoading !== false) {
          // 可以在这里显示全局loading
        }

        console.log(`[API] ${config.method?.toUpperCase()} ${config.url}`, config.data || config.params)
        return config
      },
      (error) => {
        console.error('[API] Request error:', error)
        return Promise.reject(error)
      }
    )

    // 响应拦截器
    this.instance.interceptors.response.use(
      (response: AxiosResponse) => {
        console.log(`[API] Response:`, response.data)
        
        // 检查业务状态码
        if (response.data && response.data.success === false) {
          const message = response.data.message || '请求失败'
          ElMessage.error(message)
          return Promise.reject(new Error(message))
        }

        return response
      },
      (error) => {
        console.error('[API] Response error:', error)
        
        // 处理不同类型的错误
        if (error.response) {
          const { status, data } = error.response
          let message = '请求失败'

          switch (status) {
            case 400:
              message = data.detail || '请求参数错误'
              break
            case 401:
              message = '认证失败，请重新登录'
              this.handleAuthError()
              break
            case 403:
              message = '权限不足'
              break
            case 404:
              message = '请求的资源不存在'
              break
            case 429:
              message = '请求过于频繁，请稍后重试'
              break
            case 500:
              message = data.detail || '服务器内部错误'
              break
            case 502:
            case 503:
            case 504:
              message = '服务器暂时不可用，请稍后重试'
              break
            default:
              message = data.detail || `请求失败 (${status})`
          }

          ElMessage.error(message)
          return Promise.reject(new Error(message))
        } else if (error.request) {
          const message = '网络连接失败，请检查网络设置'
          ElMessage.error(message)
          return Promise.reject(new Error(message))
        } else {
          const message = error.message || '未知错误'
          ElMessage.error(message)
          return Promise.reject(new Error(message))
        }
      }
    )
  }

  private generateRequestId(): string {
    return `req_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
  }

  private handleAuthError() {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    // 重定向到登录页面
    window.location.href = '/login'
  }

  // ===== 缠论分析相关API =====

  /**
   * 综合缠论分析
   */
  async comprehensiveChanAnalysis(request: ChanAnalysisRequest): Promise<ChanAnalysisResponse> {
    const response = await this.instance.post<ChanAnalysisResponse>(
      '/api/v2/chan/comprehensive_analysis',
      request
    )
    return response.data
  }

  /**
   * 批量缠论分析
   */
  async batchChanAnalysis(request: BatchAnalysisRequest): Promise<BatchAnalysisResponse> {
    const response = await this.instance.post<BatchAnalysisResponse>(
      '/api/v2/chan/batch_analysis',
      request
    )
    return response.data
  }

  /**
   * 实时预测
   */
  async getRealTimePrediction(request: RealTimePredictionRequest): Promise<RealTimePredictionResponse> {
    const { symbol, timeframe, include_confidence } = request
    const response = await this.instance.get<RealTimePredictionResponse>(
      `/api/v2/chan/real_time_prediction/${symbol}`,
      {
        params: { timeframe, include_confidence }
      }
    )
    return response.data
  }

  /**
   * 获取交易信号
   */
  async getTradingSignals(params: {
    symbol: string
    timeframes?: string[]
    signal_types?: string[]
    limit?: number
  }) {
    const response = await this.instance.get(
      `/api/v2/chan/trading_signals/${params.symbol}`,
      { params }
    )
    return response.data
  }

  /**
   * 获取结构映射
   */
  async getStructureMapping(params: {
    symbol: string
    primary_timeframe?: string
    secondary_timeframe?: string
  }) {
    const response = await this.instance.get(
      `/api/v2/chan/structure_mapping/${params.symbol}`,
      { params }
    )
    return response.data
  }

  /**
   * 多时间周期分析
   */
  async getMultiTimeframeAnalysis(request: MultiTimeframeRequest): Promise<MultiTimeframeResponse> {
    const { symbol, timeframes, analysis_depth } = request
    const response = await this.instance.get<MultiTimeframeResponse>(
      `/api/v2/chan/multi_timeframe/${symbol}`,
      {
        params: { timeframes, analysis_depth }
      }
    )
    return response.data
  }

  /**
   * 获取市场结构（图表专用）
   */
  async getMarketStructure(params: {
    symbol: string
    timeframe?: string
    structure_type?: string
  }) {
    const response = await this.instance.get(
      `/api/v2/chan/market_structure/${params.symbol}`,
      { params }
    )
    return response.data
  }

  /**
   * 策略回测
   */
  async backtestStrategy(params: {
    symbol: string
    start_date: string
    end_date: string
    strategy_config: Record<string, any>
  }) {
    const response = await this.instance.post(
      '/api/v2/chan/backtest',
      params
    )
    return response.data
  }

  // ===== 数据可视化相关API =====

  /**
   * 获取图表数据
   */
  async getChartData(request: ChartDataRequest): Promise<ChartDataResponse> {
    const response = await this.instance.post<ChartDataResponse>(
      '/api/v2/visualization/chart_data',
      request
    )
    return response.data
  }

  /**
   * 获取K线数据
   */
  async getKLineData(request: KLineRequest): Promise<KLineResponse> {
    const { symbol, timeframe, start_date, end_date, limit, include_volume } = request
    const response = await this.instance.get<KLineResponse>(
      `/api/v2/visualization/kline/${symbol}`,
      {
        params: { timeframe, start_date, end_date, limit, include_volume }
      }
    )
    return response.data
  }

  /**
   * 获取技术指标
   */
  async getTechnicalIndicators(request: TechnicalIndicatorRequest): Promise<TechnicalIndicatorResponse> {
    const { symbol, indicators, timeframe, periods } = request
    const response = await this.instance.get<TechnicalIndicatorResponse>(
      `/api/v2/visualization/technical_indicators/${symbol}`,
      {
        params: { indicators, timeframe, periods }
      }
    )
    return response.data
  }

  /**
   * 获取缠论结构叠加数据
   */
  async getChanStructureOverlay(params: {
    symbol: string
    timeframe?: string
    structures?: string[]
    show_signals?: boolean
    show_zhongshu?: boolean
  }) {
    const response = await this.instance.get(
      `/api/v2/visualization/chan_structure_overlay/${params.symbol}`,
      { params }
    )
    return response.data
  }

  /**
   * 获取市场热力图
   */
  async getMarketHeatmap(params: {
    market?: string
    metric?: string
    timeframe?: string
    sectors?: string[]
  } = {}) {
    const response = await this.instance.get(
      '/api/v2/visualization/market_heatmap',
      { params }
    )
    return response.data
  }

  /**
   * 获取信号分布统计
   */
  async getSignalDistribution(params: {
    symbol: string
    timeframe?: string
    signal_type?: string
    period_days?: number
  }) {
    const response = await this.instance.get(
      `/api/v2/visualization/signal_distribution/${params.symbol}`,
      { params }
    )
    return response.data
  }

  /**
   * 获取结构演化
   */
  async getStructureEvolution(params: {
    symbol: string
    timeframe?: string
    structure_type?: string
    period_days?: number
  }) {
    const response = await this.instance.get(
      `/api/v2/visualization/structure_evolution/${params.symbol}`,
      { params }
    )
    return response.data
  }

  /**
   * 获取性能仪表板
   */
  async getPerformanceDashboard(params: {
    symbol: string
    timeframes?: string[]
    metrics?: string[]
    benchmark?: string
  }) {
    const response = await this.instance.get(
      `/api/v2/visualization/performance_dashboard/${params.symbol}`,
      { params }
    )
    return response.data
  }

  /**
   * 获取实时图表数据
   */
  async getRealTimeChartData(params: {
    symbol: string
    timeframe?: string
    indicators?: string[]
    include_chan?: boolean
  }) {
    const response = await this.instance.get(
      `/api/v2/visualization/real_time_chart/${params.symbol}`,
      { params }
    )
    return response.data
  }

  // ===== 机器学习相关API =====

  /**
   * 训练模型
   */
  async trainModel(params: {
    training_config: Record<string, any>
    data_config: Record<string, any>
  }) {
    const response = await this.instance.post(
      '/api/v2/ml/train_model',
      params
    )
    return response.data
  }

  /**
   * 获取模型性能
   */
  async getModelPerformance(modelName: string) {
    const response = await this.instance.get(
      `/api/v2/ml/model_performance/${modelName}`
    )
    return response.data
  }

  // ===== 数据管理相关API =====

  /**
   * 获取股票列表
   */
  async getStockList(params: {
    market?: string
    sector?: string
    limit?: number
    offset?: number
  } = {}) {
    const response = await this.instance.get(
      '/api/v2/data/stocks',
      { params }
    )
    return response.data
  }

  /**
   * 搜索股票
   */
  async searchStocks(query: string) {
    const response = await this.instance.get(
      '/api/v2/data/search',
      { params: { q: query } }
    )
    return response.data
  }

  /**
   * 获取股票基本信息
   */
  async getStockInfo(symbol: string) {
    const response = await this.instance.get(
      `/api/v2/data/stock_info/${symbol}`
    )
    return response.data
  }

  /**
   * 获取实时行情
   */
  async getRealTimeQuote(symbols: string[]) {
    const response = await this.instance.post(
      '/api/v2/data/real_time_quote',
      { symbols }
    )
    return response.data
  }

  // ===== 系统相关API =====

  /**
   * 健康检查
   */
  async healthCheck() {
    const response = await this.instance.get('/health')
    return response.data
  }

  /**
   * 获取系统状态
   */
  async getSystemStatus() {
    const response = await this.instance.get('/api/v2/system/status')
    return response.data
  }

  // ===== WebSocket连接 =====

  /**
   * 创建WebSocket连接
   */
  createWebSocket(endpoint: string): WebSocket {
    const wsUrl = this.baseURL.replace('http', 'ws') + endpoint
    const ws = new WebSocket(wsUrl)
    
    ws.onopen = () => {
      console.log(`[WebSocket] Connected to ${endpoint}`)
    }
    
    ws.onclose = (event) => {
      console.log(`[WebSocket] Disconnected from ${endpoint}:`, event.code, event.reason)
    }
    
    ws.onerror = (error) => {
      console.error(`[WebSocket] Error on ${endpoint}:`, error)
    }
    
    return ws
  }

  /**
   * 订阅实时数据
   */
  subscribeRealTimeData(symbol: string, callback: (data: any) => void): WebSocket {
    const ws = this.createWebSocket(`/ws/real_time/${symbol}`)
    
    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        callback(data)
      } catch (error) {
        console.error('[WebSocket] Failed to parse message:', error)
      }
    }
    
    return ws
  }

  // ===== 工具方法 =====

  /**
   * 上传文件
   */
  async uploadFile(file: File, endpoint: string = '/api/v2/upload'): Promise<any> {
    const formData = new FormData()
    formData.append('file', file)
    
    const response = await this.instance.post(endpoint, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    
    return response.data
  }

  /**
   * 下载文件
   */
  async downloadFile(url: string, filename?: string): Promise<void> {
    const response = await this.instance.get(url, {
      responseType: 'blob'
    })
    
    // 创建下载链接
    const blob = new Blob([response.data])
    const downloadUrl = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = downloadUrl
    link.download = filename || 'download'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(downloadUrl)
  }

  /**
   * 取消请求
   */
  createCancelToken() {
    return axios.CancelToken.source()
  }
}

// 创建API服务实例
export const apiService = new ApiService()

// 导出类型用于组件使用
export type { ApiService }
export default apiService