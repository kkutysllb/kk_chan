import axios from 'axios'
import { ElMessage } from 'element-plus'

// 创建axios实例
const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    console.log('API请求:', config.method?.toUpperCase(), config.url, config.params || config.data)
    return config
  },
  (error) => {
    console.error('请求错误:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  (response) => {
    console.log('API响应:', response.config.url, response.status, response.data)
    return response.data
  },
  (error) => {
    console.error('响应错误:', error)
    
    let message = '网络请求失败'
    
    if (error.response) {
      const { status, data } = error.response
      switch (status) {
        case 400:
          message = data?.message || '请求参数错误'
          break
        case 401:
          message = '未授权访问'
          break
        case 403:
          message = '访问被禁止'
          break
        case 404:
          message = '请求的资源不存在'
          break
        case 500:
          message = '服务器内部错误'
          break
        default:
          message = data?.message || `请求失败 (${status})`
      }
    } else if (error.request) {
      message = '网络连接失败，请检查网络'
    }
    
    ElMessage.error(message)
    return Promise.reject(error)
  }
)

// API方法定义
export const stockApi = {
  // 获取股票列表
  getStockList() {
    return api.get('/stocks')
  },

  // 获取缠论分析数据
  getAnalysisData(params) {
    return api.get('/analysis', { params })
  },

  // 保存分析结果
  saveAnalysis(data) {
    return api.post('/analysis/save', data)
  },
}

// 直接调用Python API的方法
export const pythonApi = {
  // 调用后端代理服务获取分析数据
  async getAnalysisData({ symbol, timeframe = 'daily', days = 90 }) {
    try {
      console.log(`获取分析数据: ${symbol}, ${timeframe}, ${days}天`)
      
      // 调用后端代理服务API
      const response = await fetch(`http://localhost:8000/analysis?symbol=${symbol}&timeframe=${timeframe}&days=${days}`)
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      
      const data = await response.json()
      
      // 检查是否有错误信息
      if (data.error) {
        throw new Error(data.message || '分析失败')
      }
      
      return data
      
    } catch (error) {
      console.error('获取分析数据失败:', error)
      throw error
    }
  },

  // 获取股票列表
  async getStockList(query = '') {
    try {
      const url = query ? 
        `http://localhost:8000/stocks?query=${encodeURIComponent(query)}` : 
        'http://localhost:8000/stocks'
      
      const response = await fetch(url)
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      
      const data = await response.json()
      return data
      
    } catch (error) {
      console.error('获取股票列表失败:', error)
      throw error
    }
  },

  // 执行选股
  async runStockSelection({ max_results = 50, min_backchi_strength = null, min_buy_point_strength = null }) {
    try {
      let url = `http://localhost:8000/stock-selection?max_results=${max_results}`
      
      if (min_backchi_strength !== null) {
        url += `&min_backchi_strength=${min_backchi_strength}`
      }
      if (min_buy_point_strength !== null) {
        url += `&min_buy_point_strength=${min_buy_point_strength}`
      }
      
      console.log('执行选股:', { max_results, min_backchi_strength, min_buy_point_strength })
      
      const response = await fetch(url)
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      
      const data = await response.json()
      
      if (data.error) {
        throw new Error(data.message || '选股失败')
      }
      
      return data
      
    } catch (error) {
      console.error('选股执行失败:', error)
      throw error
    }
  },

  // POST方式执行选股
  async postStockSelection({ max_results = 50, custom_config = null }) {
    try {
      console.log('POST选股请求:', { max_results, custom_config })
      
      const response = await fetch('http://localhost:8000/stock-selection', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          max_results,
          custom_config
        })
      })
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      
      const data = await response.json()
      
      if (data.error) {
        throw new Error(data.message || '选股失败')
      }
      
      return data
      
    } catch (error) {
      console.error('POST选股失败:', error)
      throw error
    }
  },

  // 获取选股配置
  async getStockSelectionConfig() {
    try {
      const response = await fetch('http://localhost:8000/stock-selection/config')
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      
      const data = await response.json()
      return data
      
    } catch (error) {
      console.error('获取选股配置失败:', error)
      throw error
    }
  },

  // 更新选股配置
  async updateStockSelectionConfig(config) {
    try {
      console.log('更新选股配置:', config)
      
      const response = await fetch('http://localhost:8000/stock-selection/config', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ config })
      })
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      
      const data = await response.json()
      
      if (data.error) {
        throw new Error(data.message || '配置更新失败')
      }
      
      return data
      
    } catch (error) {
      console.error('更新选股配置失败:', error)
      throw error
    }
  },

  // 获取选股历史记录
  async getStockSelectionHistory(limit = 20) {
    try {
      const response = await fetch(`http://localhost:8000/stock-selection/history?limit=${limit}`)
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      
      const data = await response.json()
      return data
      
    } catch (error) {
      console.error('获取选股历史失败:', error)
      throw error
    }
  },
}

export default api