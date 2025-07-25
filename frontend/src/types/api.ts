/**
 * API接口类型定义
 * 定义前后端交互的数据结构
 */

// ===== 通用类型 =====

export interface ApiResponse<T = any> {
  success: boolean
  data: T
  message?: string
  error?: string
  timestamp?: string
  cache_hit?: boolean
  computation_time?: number
}

export interface PaginationParams {
  limit?: number
  offset?: number
  page?: number
  page_size?: number
}

export interface TimeRangeParams {
  start_date?: string | Date
  end_date?: string | Date
}

// ===== 缠论分析相关 =====

export interface ChanAnalysisRequest {
  symbol: string
  timeframes: string[]
  start_date?: string | Date
  end_date?: string | Date
  include_ml_prediction?: boolean
  include_signals?: boolean
  force_refresh?: boolean
  config?: Record<string, any>
}

export interface ChanAnalysisResponse extends ApiResponse {
  data: {
    symbol: string
    analysis_date: string
    timeframes: string[]
    timeframe_results: Record<string, any>
    multi_timeframe_analysis: Record<string, any>
    trading_signals: TradingSignal[]
    ml_predictions: Record<string, any>
    risk_assessment: Record<string, any>
    computation_time: number
    data_quality_score: number
  }
}

export interface BatchAnalysisRequest {
  symbols: string[]
  timeframes: string[]
  start_date?: string | Date
  end_date?: string | Date
  max_concurrent?: number
}

export interface BatchAnalysisResponse extends ApiResponse {
  results: ChanAnalysisResponse['data'][]
  total_processed: number
  processing_time: number
  failed_symbols: string[]
}

export interface RealTimePredictionRequest {
  symbol: string
  timeframe?: string
  include_confidence?: boolean
}

export interface RealTimePredictionResponse extends ApiResponse {
  symbol: string
  timeframe: string
  prediction: {
    signal_type: 'buy' | 'sell' | 'hold'
    confidence: number
    probability: Record<string, number>
    next_price_target?: number
    risk_level: string
    timestamp: string
  }
}

export interface TradingSignalResponse extends ApiResponse {
  symbol: string
  signals: TradingSignal[]
  total_signals: number
}

export interface StructureMappingResponse extends ApiResponse {
  symbol: string
  primary_timeframe: string
  secondary_timeframe: string
  mapping: {
    correlation_score: number
    consistency_level: string
    mapping_points: Array<{
      primary_structure: any
      secondary_structure: any
      correlation: number
    }>
  }
}

export interface MultiTimeframeRequest {
  symbol: string
  timeframes: string[]
  analysis_depth?: string
}

export interface MultiTimeframeResponse extends ApiResponse {
  symbol: string
  timeframes: string[]
  analysis: {
    trend_consistency: Record<string, any>
    structure_alignment: Record<string, any>
    signal_confirmation: Record<string, any>
    risk_assessment: Record<string, any>
  }
  consistency_score: number
}

// ===== 数据可视化相关 =====

export interface ChartDataRequest {
  symbol: string
  chart_type: string
  timeframe: string
  start_date?: string | Date
  end_date?: string | Date
  indicators?: string[]
  structures?: string[]
  config?: Record<string, any>
}

export interface ChartDataResponse extends ApiResponse {
  chart_type: string
  symbol: string
  timeframe: string
  data: any
}

export interface KLineRequest extends TimeRangeParams {
  symbol: string
  timeframe: string
  limit?: number
  include_volume?: boolean
}

export interface KLineResponse extends ApiResponse {
  symbol: string
  timeframe: string
  data: KLineData[]
  data_points: number
}

export interface TechnicalIndicatorRequest {
  symbol: string
  indicators: string[]
  timeframe: string
  periods?: Record<string, any>
}

export interface TechnicalIndicatorResponse extends ApiResponse {
  symbol: string
  timeframe: string
  indicators: string[]
  data: TechnicalIndicator[]
}

export interface StructureOverlayResponse extends ApiResponse {
  symbol: string
  timeframe: string
  structures: string[]
  overlay_data: {
    fenxings: Array<{
      timestamp: string
      price: number
      type: string
      style: Record<string, any>
    }>
    bis: Array<{
      start: { timestamp: string; price: number }
      end: { timestamp: string; price: number }
      direction: string
      style: Record<string, any>
    }>
    xianduan: Array<{
      points: Array<{ timestamp: string; price: number }>
      direction: string
      style: Record<string, any>
    }>
    zhongshus: Array<{
      start_time: string
      end_time: string
      high: number
      low: number
      style: Record<string, any>
    }>
    signals: Array<{
      timestamp: string
      price: number
      type: string
      subtype: string
      style: Record<string, any>
    }>
  }
}

export interface HeatmapDataResponse extends ApiResponse {
  market: string
  metric: string
  timeframe: string
  data: Array<{
    symbol: string
    name: string
    value: number
    sector: string
    market_cap: number
    color_value: number
  }>
  chart_config: Record<string, any>
}

// ===== 基础数据类型 =====

export interface KLineData {
  timestamp: string | Date
  open: number
  high: number
  low: number
  close: number
  volume: number
  amount?: number
  turnover_rate?: number
}

export interface TechnicalIndicator {
  name: string
  timeframe: string
  data: Record<string, number[]>
  parameters: Record<string, any>
}

export interface ChanStructure {
  fenxings: EnhancedFenXing[]
  bis: IntelligentBi[]
  xianduan: AdvancedXianDuan[]
  zhongshus: AdvancedZhongShu[]
}

export interface EnhancedFenXing {
  id: string
  timestamp: string | Date
  price: number
  fenxing_type: 'top' | 'bottom'
  index: number
  strength: number
  confidence: number
  volume_confirmation: boolean
  position_in_trend: string
  next_target?: number
  support_resistance: number
  macd_confirmation: boolean
  rsi_confirmation: boolean
  bollinger_confirmation: boolean
  ml_probability: number
  feature_importance: Record<string, number>
  historical_success_rate: number
  avg_holding_period: number
}

export interface IntelligentBi {
  id: string
  start_fenxing: EnhancedFenXing
  end_fenxing: EnhancedFenXing
  direction: 'up' | 'down'
  strength: number
  purity: number
  duration: number
  price_change: number
  price_change_pct: number
  volume_pattern: string
  volume_confirmation: boolean
  avg_volume_ratio: number
  macd_divergence: boolean
  rsi_divergence: boolean
  momentum_confirmation: boolean
  validity_probability: number
  break_probability: number
  ml_features: Record<string, number>
  market_regime: string
  volatility_level: string
}

export interface AdvancedXianDuan {
  id: string
  constituent_bis: IntelligentBi[]
  direction: 'up' | 'down'
  level: string
  start_time: string | Date
  end_time: string | Date
  start_price: number
  end_price: number
  bi_count: number
  structure_integrity: number
  trend_consistency: number
  momentum_strength: number
  volume_support: number
  breakout_potential: number
  moving_average_alignment: boolean
  indicator_confluence: number
  classification_confidence: number
  regression_target: number
  feature_vector: number[]
}

export interface AdvancedZhongShu {
  id: string
  level: string
  start_time: string | Date
  end_time: string | Date
  high: number
  low: number
  center: number
  range_size: number
  range_ratio: number
  extension_count: number
  breakthrough_attempts: number
  support_tests: number
  resistance_tests: number
  volume_distribution: Record<string, number>
  avg_volume_in_range: number
  volume_breakout_ratio: number
  market_structure_type: string
  consolidation_quality: number
  breakout_direction_bias: string
  next_direction_prob: Record<string, number>
  breakout_probability: number
  breakdown_probability: number
  continuation_probability: number
  formation_period: number
  expected_duration: number
  time_strength: number
}

export interface TradingSignal {
  id: string
  signal_type: 'buy' | 'sell'
  signal_subtype: string
  timestamp: string | Date
  price: number
  strength: number
  confidence: number
  priority: 'low' | 'medium' | 'high'
  chan_confirmation: boolean
  technical_confirmation: boolean
  volume_confirmation: boolean
  ml_confirmation: boolean
  target_price?: number
  stop_loss_price?: number
  risk_reward_ratio: number
  suggested_holding_period: number
  position_size_suggestion: number
  historical_success_rate: number
  avg_return: number
  max_favorable: number
  max_adverse: number
  market_condition: string
  sector_trend: string
}

// ===== 机器学习相关 =====

export interface ModelTrainingRequest {
  training_config: {
    model_type: string
    target_variable: string
    features: string[]
    hyperparameters: Record<string, any>
  }
  data_config: {
    start_date: string
    end_date: string
    symbols: string[]
    timeframes: string[]
  }
}

export interface ModelTrainingResponse extends ApiResponse {
  task_id: string
  status: string
  estimated_time: string
}

export interface ModelPerformanceResponse extends ApiResponse {
  model_name: string
  performance_metrics: {
    accuracy: number
    precision: number
    recall: number
    f1_score: number
    auc: number
    confusion_matrix: number[][]
    feature_importance: Array<{
      feature: string
      importance: number
    }>
  }
}

// ===== 数据管理相关 =====

export interface StockListRequest extends PaginationParams {
  market?: string
  sector?: string
  sort_by?: string
  sort_order?: 'asc' | 'desc'
}

export interface StockListResponse extends ApiResponse {
  data: Array<{
    symbol: string
    name: string
    market: string
    sector: string
    industry: string
    market_cap: number
    current_price: number
    price_change: number
    price_change_percent: number
    volume: number
    turnover_rate: number
    pe_ratio: number
    pb_ratio: number
  }>
  total: number
  page: number
  page_size: number
}

export interface StockSearchResponse extends ApiResponse {
  data: Array<{
    symbol: string
    name: string
    market: string
    sector: string
    match_score: number
  }>
}

export interface StockInfoResponse extends ApiResponse {
  data: {
    symbol: string
    name: string
    full_name: string
    market: string
    sector: string
    industry: string
    list_date: string
    market_cap: number
    total_shares: number
    float_shares: number
    pe_ratio: number
    pb_ratio: number
    roe: number
    debt_ratio: number
    current_price: number
    price_change: number
    price_change_percent: number
    volume: number
    amount: number
    turnover_rate: number
    high_52w: number
    low_52w: number
    description: string
  }
}

export interface RealTimeQuoteRequest {
  symbols: string[]
}

export interface RealTimeQuoteResponse extends ApiResponse {
  data: Record<string, {
    symbol: string
    current_price: number
    price_change: number
    price_change_percent: number
    volume: number
    amount: number
    turnover_rate: number
    high: number
    low: number
    open: number
    prev_close: number
    timestamp: string
  }>
}

// ===== 系统状态相关 =====

export interface HealthCheckResponse {
  status: string
  timestamp: string
  version: string
  services: Record<string, string>
}

export interface SystemStatusResponse extends ApiResponse {
  system: {
    cpu_usage: number
    memory_usage: number
    disk_usage: number
    uptime: number
  }
  database: {
    status: string
    connections: number
    query_time_avg: number
  }
  cache: {
    status: string
    hit_rate: number
    memory_usage: number
  }
  api: {
    requests_per_minute: number
    avg_response_time: number
    error_rate: number
  }
}

// ===== WebSocket消息类型 =====

export interface WebSocketMessage<T = any> {
  type: string
  data: T
  timestamp: string
  request_id?: string
}

export interface RealTimeDataMessage extends WebSocketMessage {
  type: 'real_time_data'
  data: {
    symbol: string
    price: number
    volume: number
    timestamp: string
  }
}

export interface AnalysisUpdateMessage extends WebSocketMessage {
  type: 'analysis_update'
  data: {
    symbol: string
    timeframe: string
    update_type: 'new_signal' | 'structure_change' | 'prediction_update'
    content: any
  }
}

// ===== 市场数据相关 =====

export interface MarketData {
  market: string
  timestamp: string
  indices?: MarketIndex[]
  sectors?: SectorData[]
  stats?: MarketStats
}

export interface MarketIndex {
  symbol: string
  name: string
  current_price: number
  change_pct: number
  volume: number
  timestamp: string
}

export interface SectorData {
  name: string
  change_pct: number
  stock_count: number
  market_cap?: number
  volume?: number
}

export interface MarketStats {
  rising_count: number
  falling_count: number
  flat_count: number
  suspended_count: number
  total_volume: number
  total_amount: number
  avg_turnover: number
}

// ===== 自选股相关 =====

export interface WatchlistItem {
  symbol: string
  name?: string
  current_price?: number
  change_pct?: number
  volume?: number
  latest_signal?: {
    type: 'buy' | 'sell' | 'hold'
    confidence: number
  }
  trend?: 'up' | 'down' | 'sideways'
  update_time?: string
}

// ===== 多时间周期分析相关 =====

export interface MultiTimeframeAnalysis {
  symbol: string
  timeframes: string[]
  results: Record<string, {
    trend: string
    strength: number
    confidence: number
    analysis_date: string
    chan_analysis?: {
      fenxing_count: number
      bi_count: number
      zhongshu_count: number
    }
  }>
  consistency_score: number
}

// ===== 实时预测相关 =====

export interface RealTimePrediction {
  symbol: string
  timeframe: string
  prediction: string
  confidence: number
  current_price?: number
  volume?: number
  latest_data?: any
  prediction_history?: any[]
  timestamp: string
}

// ===== 错误类型 =====

export interface ApiError {
  error: true
  message: string
  status_code: number
  details?: any
  timestamp: string
}

// ===== 导出联合类型 =====

export type ApiRequestTypes = 
  | ChanAnalysisRequest
  | BatchAnalysisRequest
  | RealTimePredictionRequest
  | ChartDataRequest
  | KLineRequest
  | TechnicalIndicatorRequest
  | MultiTimeframeRequest
  | ModelTrainingRequest
  | StockListRequest
  | RealTimeQuoteRequest

export type ApiResponseTypes = 
  | ChanAnalysisResponse
  | BatchAnalysisResponse
  | RealTimePredictionResponse
  | ChartDataResponse
  | KLineResponse
  | TechnicalIndicatorResponse
  | MultiTimeframeResponse
  | ModelTrainingResponse
  | ModelPerformanceResponse
  | StockListResponse
  | StockInfoResponse
  | RealTimeQuoteResponse
  | HealthCheckResponse
  | SystemStatusResponse