/**
 * 缠论相关类型定义
 */

// 分型类型
export interface FenXing {
  id: string
  timestamp: string
  price: number
  fenxing_type: 'top' | 'bottom'
  index: number
  strength: number
  confidence: number
  volume_confirmation: boolean
  position_in_trend: string
  next_target?: number
  support_resistance: number
  ml_probability: number
  historical_success_rate: number
}

// 笔数据
export interface Bi {
  id: string
  start_fenxing: FenXing
  end_fenxing: FenXing
  direction: 'up' | 'down' | 'sideways'
  strength: number
  purity: number
  duration: number
  price_change: number
  price_change_pct: number
  volume_confirmation: boolean
  validity_probability: number
}

// 线段数据
export interface XianDuan {
  id: string
  start_time: string
  end_time: string
  direction: 'up' | 'down'
  high: number
  low: number
  strength: number
  bis: Bi[]
}

// 中枢数据
export interface ZhongShu {
  id: string
  level: string
  start_time: string
  end_time: string
  high: number
  low: number
  center: number
  range_size: number
  extension_count: number
  breakout_probability: number
  breakdown_probability: number
  continuation_probability: number
}

// 缠论结构
export interface ChanStructure {
  fenxings: FenXing[]
  bis: Bi[]
  xianduan: XianDuan[]
  zhongshus: ZhongShu[]
}

// 交易信号详情
export interface TradingSignalDetail {
  id: string
  signal_type: 'buy' | 'sell' | 'hold'
  signal_subtype: string
  timestamp: string
  price: number
  strength: number
  confidence: number
  priority: string
  target_price?: number
  stop_loss_price?: number
  risk_reward_ratio: number
  description?: string
  analysis_reason?: string
}

// 股票详情
export interface StockDetail {
  symbol: string
  name: string
  current_price: number
  change: number
  change_percent: number
  volume: number
  market_cap: number
  pe_ratio?: number
  pb_ratio?: number
  industry?: string
  concept?: string[]
  technical_rating?: string
  fundamental_rating?: string
}