<template>
  <div class="analysis-report">
    <div class="report-container">
      <!-- 无数据状态 -->
      <div v-if="!hasData" class="empty-state">
        <el-empty description="暂无分析报告" :image-size="120">
          <el-button type="primary" @click="$emit('analyze')">
            开始分析
          </el-button>
        </el-empty>
      </div>

      <!-- 报告内容 -->
      <div v-else class="report-content">
        <!-- 分析概览 -->
        <el-card class="overview-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span class="card-title">分析概览</span>
              <el-button
                size="small"
                :icon="Download"
                @click="exportReport"
              >
                导出报告
              </el-button>
            </div>
          </template>
          
          <div class="overview-content">
            <div class="stock-info">
              <h3>{{ currentStock?.symbol }} 缠论分析报告</h3>
              <div class="info-tags">
                <el-tag type="primary">{{ timeframeText }}</el-tag>
                <el-tag type="info">{{ analysisData?.meta?.data_count }}条数据</el-tag>
                <el-tag type="success">{{ formatTime(analysisData?.meta?.analysis_time) }}</el-tag>
              </div>
            </div>
            
            <div class="key-metrics">
              <div class="metric-item">
                <div class="metric-label">市场趋势</div>
                <div class="metric-value trend">{{ getTrendText() }}</div>
              </div>
              <div class="metric-item">
                <div class="metric-label">结构完整性</div>
                <div class="metric-value">{{ getStructureScore() }}%</div>
              </div>
              <div class="metric-item">
                <div class="metric-label">信号质量</div>
                <div class="metric-value">{{ getSignalQuality() }}</div>
              </div>
            </div>
          </div>
        </el-card>

        <!-- 技术分析 -->
        <el-card class="analysis-card" shadow="hover">
          <template #header>
            <span class="card-title">技术分析</span>
          </template>
          
          <div class="analysis-sections">
            <!-- 分型分析 -->
            <div class="analysis-section">
              <h4>分型分析</h4>
              <div class="section-content">
                <p class="analysis-text">
                  本次分析共识别出 <strong>{{ summary?.fenxing_count || 0 }}</strong> 个分型，
                  其中顶分型和底分型分布{{ getFenxingDistribution() }}。
                  分型的识别为后续笔段构造提供了基础支撑。
                </p>
                <div class="analysis-points">
                  <el-tag
                    v-for="point in getFenxingAnalysisPoints()"
                    :key="point.text"
                    :type="point.type"
                    size="small"
                    class="analysis-tag"
                  >
                    {{ point.text }}
                  </el-tag>
                </div>
              </div>
            </div>

            <!-- 笔段分析 -->
            <div class="analysis-section">
              <h4>笔段分析</h4>
              <div class="section-content">
                <p class="analysis-text">
                  识别出 <strong>{{ summary?.bi_count || 0 }}</strong> 条笔段，
                  笔段的构造显示了价格运行的{{ getBiTrendText() }}特征。
                  {{ getBiAnalysisText() }}
                </p>
                <div class="analysis-points">
                  <el-tag
                    v-for="point in getBiAnalysisPoints()"
                    :key="point.text"
                    :type="point.type"
                    size="small"
                    class="analysis-tag"
                  >
                    {{ point.text }}
                  </el-tag>
                </div>
              </div>
            </div>

            <!-- 中枢分析 -->
            <div class="analysis-section">
              <h4>中枢分析</h4>
              <div class="section-content">
                <p class="analysis-text">
                  当前识别出 <strong>{{ summary?.zhongshu_count || 0 }}</strong> 个中枢结构。
                  {{ getZhongshuAnalysisText() }}
                </p>
                <div class="analysis-points">
                  <el-tag
                    v-for="point in getZhongshuAnalysisPoints()"
                    :key="point.text"
                    :type="point.type"
                    size="small"
                    class="analysis-tag"
                  >
                    {{ point.text }}
                  </el-tag>
                </div>
              </div>
            </div>

            <!-- 信号分析 -->
            <div class="analysis-section">
              <h4>交易信号分析</h4>
              <div class="section-content">
                <p class="analysis-text">
                  本次分析产生 <strong>{{ summary?.signal_count || 0 }}</strong> 个交易信号，
                  {{ getSignalAnalysisText() }}
                </p>
                <div class="signal-breakdown">
                  <div class="signal-stats">
                    <div class="signal-stat buy">
                      <span class="stat-label">买入信号</span>
                      <span class="stat-value">{{ getBuySignalCount() }}</span>
                    </div>
                    <div class="signal-stat sell">
                      <span class="stat-label">卖出信号</span>
                      <span class="stat-value">{{ getSellSignalCount() }}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </el-card>

        <!-- 投资建议 -->
        <el-card class="advice-card" shadow="hover">
          <template #header>
            <span class="card-title">投资建议</span>
          </template>
          
          <div class="advice-content">
            <div class="advice-level">
              <div class="level-indicator" :class="getAdviceLevel().class">
                {{ getAdviceLevel().text }}
              </div>
              <div class="level-description">
                {{ getAdviceLevel().description }}
              </div>
            </div>
            
            <div class="advice-points">
              <div
                v-for="(advice, index) in getInvestmentAdvice()"
                :key="index"
                class="advice-point"
              >
                <el-icon class="advice-icon" :class="advice.type">
                  <component :is="advice.icon" />
                </el-icon>
                <div class="advice-text">
                  <div class="advice-title">{{ advice.title }}</div>
                  <div class="advice-desc">{{ advice.description }}</div>
                </div>
              </div>
            </div>
          </div>
        </el-card>

        <!-- 风险提示 -->
        <el-card class="risk-card" shadow="hover">
          <template #header>
            <span class="card-title">风险提示</span>
          </template>
          
          <el-alert
            type="warning"
            show-icon
            :closable="false"
            class="risk-alert"
          >
            <template #title>
              <strong>重要声明</strong>
            </template>
            <div class="risk-content">
              <ul class="risk-list">
                <li>本分析基于缠论技术分析方法，仅供参考，不构成投资建议</li>
                <li>股市有风险，投资需谨慎，请根据自身风险承受能力进行投资决策</li>
                <li>技术分析存在滞后性，实际操作中请结合基本面分析和市场环境</li>
                <li>过往表现不代表未来收益，请注意控制投资风险</li>
              </ul>
            </div>
          </el-alert>
        </el-card>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Download, TrendCharts, Warning, InfoFilled } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { useGlobalStore } from '@/stores/global'

const global = useGlobalStore()

// 计算属性
const hasData = computed(() => global.hasData)
const analysisData = computed(() => global.analysisData)
const summary = computed(() => global.analysisSummary)
const currentStock = computed(() => global.currentStock)
const tradingSignals = computed(() => global.tradingSignals)
const chanStructures = computed(() => global.chanStructures)

const timeframeText = computed(() => {
  const timeframeMap = {
    '5min': '5分钟',
    '30min': '30分钟',
    'daily': '日线',
  }
  return timeframeMap[analysisData.value?.meta?.timeframe] || '-'
})

// 方法
const formatTime = (timeStr) => {
  if (!timeStr) return '-'
  try {
    const date = new Date(timeStr)
    return date.toLocaleDateString('zh-CN')
  } catch {
    return timeStr
  }
}

const getTrendText = () => {
  const biCount = summary.value?.bi_count || 0
  const zhongshuCount = summary.value?.zhongshu_count || 0
  
  if (zhongshuCount > 0) {
    return '震荡整理'
  } else if (biCount > 3) {
    return '趋势明确'
  } else {
    return '方向不明'
  }
}

const getStructureScore = () => {
  const fenxingCount = summary.value?.fenxing_count || 0
  const biCount = summary.value?.bi_count || 0
  const zhongshuCount = summary.value?.zhongshu_count || 0
  
  let score = 0
  if (fenxingCount > 0) score += 30
  if (biCount > 0) score += 40
  if (zhongshuCount > 0) score += 30
  
  return Math.min(score, 100)
}

const getSignalQuality = () => {
  const signalCount = summary.value?.signal_count || 0
  if (signalCount === 0) return '无信号'
  if (signalCount >= 5) return '丰富'
  if (signalCount >= 3) return '适中'
  return '较少'
}

const getFenxingDistribution = () => {
  const fenxingList = chanStructures.value?.fenxing || []
  const topCount = fenxingList.filter(f => f.type === 'top').length
  const bottomCount = fenxingList.filter(f => f.type === 'bottom').length
  
  if (topCount === bottomCount) return '均衡'
  if (topCount > bottomCount) return '偏向顶分型'
  return '偏向底分型'
}

const getFenxingAnalysisPoints = () => {
  const points = []
  const count = summary.value?.fenxing_count || 0
  
  if (count === 0) {
    points.push({ text: '无分型识别', type: 'info' })
  } else if (count < 5) {
    points.push({ text: '分型较少', type: 'warning' })
  } else {
    points.push({ text: '分型充足', type: 'success' })
  }
  
  return points
}

const getBiTrendText = () => {
  const biList = chanStructures.value?.bi || []
  const upCount = biList.filter(bi => bi.direction === 'up').length
  const downCount = biList.filter(bi => bi.direction === 'down').length
  
  if (upCount > downCount * 1.5) return '上升'
  if (downCount > upCount * 1.5) return '下降'
  return '震荡'
}

const getBiAnalysisText = () => {
  const biCount = summary.value?.bi_count || 0
  
  if (biCount === 0) {
    return '当前数据不足以构成完整笔段。'
  } else if (biCount < 3) {
    return '笔段数量较少，趋势特征不明显。'
  } else {
    return '笔段结构完整，为中枢和信号分析提供了良好基础。'
  }
}

const getBiAnalysisPoints = () => {
  const points = []
  const count = summary.value?.bi_count || 0
  
  if (count === 0) {
    points.push({ text: '无笔段构成', type: 'info' })
  } else if (count < 3) {
    points.push({ text: '笔段较少', type: 'warning' })
  } else {
    points.push({ text: '笔段充足', type: 'success' })
    points.push({ text: '结构清晰', type: 'success' })
  }
  
  return points
}

const getZhongshuAnalysisText = () => {
  const count = summary.value?.zhongshu_count || 0
  
  if (count === 0) {
    return '当前无中枢结构，表明价格运行趋势性较强或数据不足。'
  } else if (count === 1) {
    return '存在单一中枢，价格在此区间震荡整理。'
  } else {
    return `存在${count}个中枢，显示价格经历了多次震荡整理。`
  }
}

const getZhongshuAnalysisPoints = () => {
  const points = []
  const count = summary.value?.zhongshu_count || 0
  
  if (count === 0) {
    points.push({ text: '无中枢结构', type: 'info' })
    points.push({ text: '趋势性强', type: 'primary' })
  } else {
    points.push({ text: '存在中枢', type: 'success' })
    points.push({ text: '震荡整理', type: 'warning' })
  }
  
  return points
}

const getSignalAnalysisText = () => {
  const count = summary.value?.signal_count || 0
  
  if (count === 0) {
    return '当前数据未产生明确的买卖点信号。'
  } else {
    return '信号质量和可靠性需要结合市场环境和其他技术指标综合判断。'
  }
}

const getBuySignalCount = () => {
  return tradingSignals.value.filter(s => s.type === 'buy').length
}

const getSellSignalCount = () => {
  return tradingSignals.value.filter(s => s.type === 'sell').length
}

const getAdviceLevel = () => {
  const signalCount = summary.value?.signal_count || 0
  const zhongshuCount = summary.value?.zhongshu_count || 0
  const buyCount = getBuySignalCount()
  const sellCount = getSellSignalCount()
  
  if (buyCount > sellCount && signalCount >= 3) {
    return {
      text: '积极关注',
      class: 'positive',
      description: '技术面显示积极信号，可适度关注'
    }
  } else if (sellCount > buyCount && signalCount >= 3) {
    return {
      text: '谨慎观望',
      class: 'negative',
      description: '技术面显示谨慎信号，建议观望'
    }
  } else {
    return {
      text: '中性观察',
      class: 'neutral',
      description: '技术面信号不明确，保持观察'
    }
  }
}

const getInvestmentAdvice = () => {
  const advice = []
  const buyCount = getBuySignalCount()
  const sellCount = getSellSignalCount()
  const zhongshuCount = summary.value?.zhongshu_count || 0
  
  if (buyCount > 0) {
    advice.push({
      icon: TrendCharts,
      type: 'positive',
      title: '关注买点',
      description: `识别出${buyCount}个买入信号，建议关注相应价位`
    })
  }
  
  if (sellCount > 0) {
    advice.push({
      icon: Warning,
      type: 'negative',
      title: '注意风险',
      description: `识别出${sellCount}个卖出信号，注意风险控制`
    })
  }
  
  if (zhongshuCount > 0) {
    advice.push({
      icon: InfoFilled,
      type: 'neutral',
      title: '震荡整理',
      description: '存在中枢结构，价格可能在区间震荡'
    })
  }
  
  if (advice.length === 0) {
    advice.push({
      icon: InfoFilled,
      type: 'neutral',
      title: '观察等待',
      description: '当前技术面信号不明确，建议继续观察'
    })
  }
  
  return advice
}

const exportReport = () => {
  try {
    const reportContent = generateReportContent()
    const blob = new Blob([reportContent], { type: 'text/plain;charset=utf-8' })
    const link = document.createElement('a')
    link.href = URL.createObjectURL(blob)
    link.download = `analysis_report_${currentStock.value?.symbol}_${Date.now()}.txt`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    
    ElMessage.success('报告导出成功')
  } catch (error) {
    console.error('导出失败:', error)
    ElMessage.error('报告导出失败')
  }
}

const generateReportContent = () => {
  const stock = currentStock.value
  const meta = analysisData.value?.meta
  
  return `
${stock?.symbol} 缠论分析报告
========================================

基本信息:
- 股票代码: ${stock?.symbol}
- 分析级别: ${timeframeText.value}
- 数据条数: ${meta?.data_count}
- 分析时间: ${formatTime(meta?.analysis_time)}

技术分析:
- 分型数量: ${summary.value?.fenxing_count || 0}
- 笔段数量: ${summary.value?.bi_count || 0}
- 中枢数量: ${summary.value?.zhongshu_count || 0}
- 交易信号: ${summary.value?.signal_count || 0}

投资建议:
${getAdviceLevel().text} - ${getAdviceLevel().description}

风险提示:
本分析仅供参考，投资有风险，决策需谨慎。

生成时间: ${new Date().toLocaleString()}
  `.trim()
}

// 发射事件
defineEmits(['analyze'])
</script>

<style scoped>
.analysis-report {
  height: 100%;
  overflow-y: auto;
  background: transparent;
}

.analysis-report::-webkit-scrollbar {
  width: 6px;
}

.analysis-report::-webkit-scrollbar-track {
  background: rgba(0, 0, 0, 0.05);
  border-radius: 3px;
}

.analysis-report::-webkit-scrollbar-thumb {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 3px;
}

.analysis-report::-webkit-scrollbar-thumb:hover {
  background: linear-gradient(135deg, #5a6fd8 0%, #6a4190 100%);
}

.report-container {
  height: 100%;
  background: transparent;
}

.empty-state {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.report-content {
  display: flex;
  flex-direction: column;
  gap: 24px;
  padding: 24px 0;
}

@keyframes slideInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.report-content > * {
  animation: slideInUp 0.5s ease;
}

.report-content > *:nth-child(1) { animation-delay: 0.1s; }
.report-content > *:nth-child(2) { animation-delay: 0.2s; }
.report-content > *:nth-child(3) { animation-delay: 0.3s; }
.report-content > *:nth-child(4) { animation-delay: 0.4s; }

.card-title {
  font-weight: 600;
  color: var(--el-text-color-primary);
  font-size: 16px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.overview-card {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  transition: all 0.3s ease;
  
  .overview-content {
    display: flex;
    flex-direction: column;
    gap: 24px;
  }
  
  .stock-info h3 {
    margin: 0 0 16px 0;
    color: var(--el-text-color-primary);
    font-size: 20px;
    font-weight: 700;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }
  
  .info-tags {
    display: flex;
    gap: 12px;
    flex-wrap: wrap;
  }
  
  .key-metrics {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 20px;
  }
  
  .metric-item {
    text-align: center;
    padding: 20px;
    background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
    border: 1px solid rgba(102, 126, 234, 0.2);
    border-radius: 12px;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    position: relative;
    overflow: hidden;
  }
  
  .metric-item::before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.1), transparent);
    transition: left 0.5s ease;
  }
  
  .metric-item:hover {
    transform: translateY(-4px) scale(1.02);
    box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
    border-color: rgba(102, 126, 234, 0.4);
  }
  
  .metric-item:hover::before {
    left: 100%;
  }
  
  .metric-label {
    font-size: 14px;
    color: var(--el-text-color-secondary);
    margin-bottom: 12px;
    font-weight: 500;
  }
  
  .metric-value {
    font-size: 22px;
    font-weight: 700;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }
  
  .metric-value.trend {
    background: linear-gradient(135deg, #67C23A 0%, #85ce61 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }
}

.dark .overview-card {
  background: rgba(44, 62, 80, 0.95);
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
}

.overview-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
}

.analysis-card {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  transition: all 0.3s ease;
  
  .analysis-sections {
    display: flex;
    flex-direction: column;
    gap: 28px;
  }
  
  .analysis-section h4 {
    margin: 0 0 16px 0;
    color: var(--el-color-primary);
    border-bottom: 3px solid transparent;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    border-image: linear-gradient(135deg, #667eea 0%, #764ba2 100%) 1;
    border-bottom: 3px solid;
    padding-bottom: 8px;
    font-size: 16px;
    font-weight: 600;
  }
  
  .section-content {
    .analysis-text {
      line-height: 1.7;
      margin-bottom: 16px;
      color: var(--el-text-color-regular);
      font-size: 15px;
      font-weight: 500;
    }
    
    .analysis-points {
      display: flex;
      gap: 12px;
      flex-wrap: wrap;
    }
    
    .analysis-tag {
      margin: 2px;
      border-radius: 8px;
      font-weight: 500;
      padding: 6px 14px;
      box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
      transition: all 0.3s ease;
    }
    
    .analysis-tag:hover {
      transform: translateY(-2px);
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    }
  }
  
  .signal-breakdown {
    margin-top: 16px;
  }
  
  .signal-stats {
    display: flex;
    gap: 20px;
    justify-content: center;
  }
  
  .signal-stat {
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 16px 20px;
    border-radius: 12px;
    min-width: 100px;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    position: relative;
    overflow: hidden;
  }
  
  .signal-stat::before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
    transition: left 0.5s ease;
  }
  
  .signal-stat:hover::before {
    left: 100%;
  }
  
  .signal-stat.buy {
    background: linear-gradient(135deg, rgba(103, 194, 58, 0.1) 0%, rgba(133, 206, 97, 0.1) 100%);
    border: 2px solid rgba(103, 194, 58, 0.3);
    box-shadow: 0 4px 15px rgba(103, 194, 58, 0.2);
  }
  
  .signal-stat.sell {
    background: linear-gradient(135deg, rgba(245, 108, 108, 0.1) 0%, rgba(247, 137, 137, 0.1) 100%);
    border: 2px solid rgba(245, 108, 108, 0.3);
    box-shadow: 0 4px 15px rgba(245, 108, 108, 0.2);
  }
  
  .signal-stat:hover {
    transform: translateY(-4px) scale(1.05);
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.2);
  }
  
  .stat-label {
    font-size: 13px;
    color: var(--el-text-color-secondary);
    font-weight: 500;
  }
  
  .stat-value {
    font-size: 24px;
    font-weight: 700;
    margin-top: 8px;
  }
  
  .signal-stat.buy .stat-value {
    color: var(--el-color-success);
    text-shadow: 0 2px 4px rgba(103, 194, 58, 0.3);
  }
  
  .signal-stat.sell .stat-value {
    color: var(--el-color-danger);
    text-shadow: 0 2px 4px rgba(245, 108, 108, 0.3);
  }
}

.dark .analysis-card {
  background: rgba(44, 62, 80, 0.95);
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
}

.analysis-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
}

.advice-card {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  transition: all 0.3s ease;
  
  .advice-content {
    display: flex;
    flex-direction: column;
    gap: 24px;
  }
  
  .advice-level {
    text-align: center;
    padding: 24px;
    border-radius: 12px;
    background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
    border: 1px solid rgba(102, 126, 234, 0.2);
    position: relative;
    overflow: hidden;
  }
  
  .advice-level::before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.1), transparent);
    transition: left 0.6s ease;
  }
  
  .advice-level:hover::before {
    left: 100%;
  }
  
  .level-indicator {
    font-size: 28px;
    font-weight: 700;
    margin-bottom: 12px;
    text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  }
  
  .level-indicator.positive {
    background: linear-gradient(135deg, #67C23A 0%, #85ce61 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }
  
  .level-indicator.negative {
    background: linear-gradient(135deg, #F56C6C 0%, #f78989 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }
  
  .level-indicator.neutral {
    background: linear-gradient(135deg, #E6A23C 0%, #eebe77 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }
  
  .level-description {
    color: var(--el-text-color-regular);
    font-size: 15px;
    font-weight: 500;
    line-height: 1.6;
  }
  
  .advice-points {
    display: flex;
    flex-direction: column;
    gap: 16px;
  }
  
  .advice-point {
    display: flex;
    align-items: flex-start;
    gap: 16px;
    padding: 16px;
    border-radius: 12px;
    background: linear-gradient(135deg, rgba(102, 126, 234, 0.05) 0%, rgba(118, 75, 162, 0.05) 100%);
    border: 1px solid rgba(102, 126, 234, 0.1);
    transition: all 0.3s ease;
    position: relative;
    overflow: hidden;
  }
  
  .advice-point::before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.1), transparent);
    transition: left 0.5s ease;
  }
  
  .advice-point:hover {
    transform: translateX(4px);
    background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
    border-color: rgba(102, 126, 234, 0.2);
    box-shadow: 0 4px 12px rgba(102, 126, 234, 0.15);
  }
  
  .advice-point:hover::before {
    left: 100%;
  }
  
  .advice-icon {
    font-size: 22px;
    margin-top: 2px;
    filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.1));
  }
  
  .advice-icon.positive {
    color: var(--el-color-success);
  }
  
  .advice-icon.negative {
    color: var(--el-color-danger);
  }
  
  .advice-icon.neutral {
    color: var(--el-color-info);
  }
  
  .advice-text {
    flex: 1;
  }
  
  .advice-title {
    font-weight: 600;
    margin-bottom: 6px;
    color: var(--el-text-color-primary);
    font-size: 15px;
  }
  
  .advice-desc {
    color: var(--el-text-color-regular);
    line-height: 1.5;
    font-size: 14px;
    font-weight: 500;
  }
}

.dark .advice-card {
  background: rgba(44, 62, 80, 0.95);
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
}

.advice-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
}

.risk-card {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  transition: all 0.3s ease;
  
  .risk-alert {
    margin: 0;
    border-radius: 12px;
    border: 1px solid rgba(230, 162, 60, 0.3);
    background: linear-gradient(135deg, rgba(230, 162, 60, 0.1) 0%, rgba(238, 190, 119, 0.1) 100%);
  }
  
  .risk-content {
    margin-top: 12px;
  }
  
  .risk-list {
    margin: 0;
    padding-left: 24px;
    
    li {
      margin-bottom: 12px;
      line-height: 1.6;
      font-weight: 500;
      color: var(--el-text-color-regular);
      position: relative;
    }
    
    li::marker {
      color: var(--el-color-warning);
      font-weight: bold;
    }
  }
}

.dark .risk-card {
  background: rgba(44, 62, 80, 0.95);
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
}

.risk-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
}

:deep(.el-card__header) {
  background: rgba(102, 126, 234, 0.05);
  border-bottom: 1px solid rgba(102, 126, 234, 0.1);
  padding: 20px 24px;
  border-radius: 16px 16px 0 0;
}

:deep(.el-card__body) {
  padding: 24px;
  background: transparent;
}

:deep(.el-tag) {
  border-radius: 8px;
  font-weight: 500;
  padding: 6px 14px;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

:deep(.el-tag:hover) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

:deep(.el-button--primary) {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  border-radius: 12px;
  font-weight: 600;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

:deep(.el-button--primary::before) {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  transition: left 0.5s ease;
}

:deep(.el-button--primary:hover) {
  transform: translateY(-2px);
  box-shadow: 0 8px 16px rgba(102, 126, 234, 0.4);
}

:deep(.el-button--primary:hover::before) {
  left: 100%;
}

:deep(.el-descriptions) {
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

:deep(.el-descriptions__header) {
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
}

:deep(.el-descriptions__label) {
  font-weight: 600;
  color: var(--el-text-color-primary);
}

:deep(.el-descriptions__content) {
  font-weight: 500;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .report-content {
    gap: 20px;
    padding: 16px 0;
  }
  
  .key-metrics {
    grid-template-columns: 1fr;
    gap: 16px;
  }
  
  .metric-item {
    padding: 16px;
  }
  
  .metric-value {
    font-size: 18px;
  }
  
  .signal-stats {
    justify-content: center;
    gap: 16px;
  }
  
  .signal-stat {
    padding: 12px 16px;
    min-width: 80px;
  }
  
  .stat-value {
    font-size: 20px;
  }
  
  .advice-level {
    padding: 20px;
  }
  
  .level-indicator {
    font-size: 24px;
  }
  
  .advice-point {
    padding: 12px;
    gap: 12px;
  }
}

@media (max-width: 480px) {
  .report-content {
    padding: 12px 0;
    gap: 16px;
  }
  
  .overview-card .stock-info h3 {
    font-size: 18px;
  }
  
  .info-tags {
    flex-direction: column;
    gap: 8px;
  }
  
  .signal-stats {
    flex-direction: column;
    gap: 12px;
  }
  
  .level-indicator {
    font-size: 20px;
  }
  
  .advice-level {
    padding: 16px;
  }
  
  .advice-point {
    padding: 12px;
  }
  
  .advice-icon {
    font-size: 18px;
  }
}
</style>