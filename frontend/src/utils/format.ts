/**
 * 格式化工具函数
 */

/**
 * 格式化价格
 */
export function formatPrice(price: number | string, precision = 2): string {
  const num = typeof price === 'string' ? parseFloat(price) : price
  if (isNaN(num)) return '--'
  return num.toFixed(precision)
}

/**
 * 格式化百分比
 */
export function formatPercent(value: number | string, precision = 2): string {
  const num = typeof value === 'string' ? parseFloat(value) : value
  if (isNaN(num)) return '--'
  return `${(num * 100).toFixed(precision)}%`
}

/**
 * 格式化数字，添加千分位分隔符
 */
export function formatNumber(value: number | string, precision = 2): string {
  const num = typeof value === 'string' ? parseFloat(value) : value
  if (isNaN(num)) return '--'
  
  return num.toLocaleString('zh-CN', {
    minimumFractionDigits: precision,
    maximumFractionDigits: precision
  })
}

/**
 * 格式化大数字（万、亿）
 */
export function formatLargeNumber(value: number | string): string {
  const num = typeof value === 'string' ? parseFloat(value) : value
  if (isNaN(num)) return '--'
  
  if (num >= 1e8) {
    return `${(num / 1e8).toFixed(2)}亿`
  } else if (num >= 1e4) {
    return `${(num / 1e4).toFixed(2)}万`
  } else {
    return num.toString()
  }
}

/**
 * 格式化成交量
 */
export function formatVolume(volume: number | string): string {
  const num = typeof volume === 'string' ? parseFloat(volume) : volume
  if (isNaN(num)) return '--'
  
  if (num >= 1e8) {
    return `${(num / 1e8).toFixed(2)}亿手`
  } else if (num >= 1e4) {
    return `${(num / 1e4).toFixed(2)}万手`
  } else {
    return `${num}手`
  }
}

/**
 * 格式化日期时间
 */
export function formatDateTime(
  date: string | Date | number, 
  timeframe?: string
): string {
  const d = new Date(date)
  if (isNaN(d.getTime())) return '--'
  
  const year = d.getFullYear()
  const month = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  const hour = String(d.getHours()).padStart(2, '0')
  const minute = String(d.getMinutes()).padStart(2, '0')
  
  if (timeframe === '1min' || timeframe === '5min' || timeframe === '30min') {
    return `${month}-${day} ${hour}:${minute}`
  } else {
    return `${year}-${month}-${day}`
  }
}

/**
 * 格式化时间（仅时分）
 */
export function formatTime(date: string | Date | number): string {
  const d = new Date(date)
  if (isNaN(d.getTime())) return '--'
  
  const hour = String(d.getHours()).padStart(2, '0')
  const minute = String(d.getMinutes()).padStart(2, '0')
  
  return `${hour}:${minute}`
}

/**
 * 格式化涨跌幅显示
 */
export function formatPriceChange(
  change: number | string, 
  changePercent: number | string
): { text: string; class: string } {
  const changeNum = typeof change === 'string' ? parseFloat(change) : change
  const percentNum = typeof changePercent === 'string' ? parseFloat(changePercent) : changePercent
  
  if (isNaN(changeNum) || isNaN(percentNum)) {
    return { text: '--', class: 'neutral' }
  }
  
  const changeText = changeNum > 0 ? `+${changeNum.toFixed(2)}` : changeNum.toFixed(2)
  const percentText = percentNum > 0 ? `+${percentNum.toFixed(2)}%` : `${percentNum.toFixed(2)}%`
  
  let className = 'neutral'
  if (changeNum > 0) {
    className = 'rise'
  } else if (changeNum < 0) {
    className = 'fall'
  }
  
  return {
    text: `${changeText} (${percentText})`,
    class: className
  }
}

/**
 * 格式化市值
 */
export function formatMarketCap(marketCap: number | string): string {
  const num = typeof marketCap === 'string' ? parseFloat(marketCap) : marketCap
  if (isNaN(num)) return '--'
  
  if (num >= 1e12) {
    return `${(num / 1e12).toFixed(2)}万亿`
  } else if (num >= 1e8) {
    return `${(num / 1e8).toFixed(2)}亿`
  } else if (num >= 1e4) {
    return `${(num / 1e4).toFixed(2)}万`
  } else {
    return num.toString()
  }
}

/**
 * 获取涨跌颜色类名
 */
export function getPriceChangeClass(change: number | string): string {
  const num = typeof change === 'string' ? parseFloat(change) : change
  if (isNaN(num)) return 'neutral'
  
  if (num > 0) return 'rise'
  if (num < 0) return 'fall'
  return 'neutral'
}

/**
 * 格式化持续时间
 */
export function formatDuration(seconds: number): string {
  if (seconds < 60) {
    return `${seconds}秒`
  } else if (seconds < 3600) {
    return `${Math.floor(seconds / 60)}分钟`
  } else if (seconds < 86400) {
    return `${Math.floor(seconds / 3600)}小时`
  } else {
    return `${Math.floor(seconds / 86400)}天`
  }
}

/**
 * 格式化文件大小
 */
export function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 B'
  
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  
  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(2))} ${sizes[i]}`
}

/**
 * 截断文本
 */
export function truncateText(text: string, maxLength: number): string {
  if (text.length <= maxLength) return text
  return text.substring(0, maxLength) + '...'
}

/**
 * 格式化股票代码
 */
export function formatStockCode(code: string): string {
  if (!code) return '--'
  
  // 添加市场后缀
  if (code.startsWith('60') || code.startsWith('68') || code.startsWith('90')) {
    return `${code}.SH`
  } else if (code.startsWith('00') || code.startsWith('30')) {
    return `${code}.SZ`
  }
  
  return code
}

/**
 * 解析股票代码
 */
export function parseStockCode(fullCode: string): { code: string; market: string } {
  if (!fullCode) return { code: '', market: '' }
  
  const parts = fullCode.split('.')
  if (parts.length === 2) {
    return {
      code: parts[0],
      market: parts[1]
    }
  }
  
  return { code: fullCode, market: '' }
}