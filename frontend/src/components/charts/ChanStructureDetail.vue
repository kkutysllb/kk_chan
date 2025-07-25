<template>
  <div class="chan-structure-detail">
    <div class="detail-header">
      <h3>{{ getStructureTitle() }}</h3>
      <el-tag :type="getStructureTagType()" size="small">
        {{ getStructureLevel() }}
      </el-tag>
    </div>

    <!-- 分型详情 -->
    <div v-if="structure.fenxing_type" class="structure-section">
      <h4>分型信息</h4>
      <div class="info-grid">
        <div class="info-item">
          <span class="label">类型:</span>
          <span class="value" :class="structure.fenxing_type === 'top' ? 'text-danger' : 'text-success'">
            {{ structure.fenxing_type === 'top' ? '顶分型' : '底分型' }}
          </span>
        </div>
        <div class="info-item">
          <span class="label">价格:</span>
          <span class="value">¥{{ formatPrice(structure.price) }}</span>
        </div>
        <div class="info-item">
          <span class="label">强度:</span>
          <span class="value">{{ formatPercent(structure.strength) }}</span>
        </div>
        <div class="info-item">
          <span class="label">置信度:</span>
          <span class="value">{{ formatPercent(structure.confidence) }}</span>
        </div>
      </div>

      <!-- 技术确认 -->
      <div class="confirmation-section">
        <h5>技术确认</h5>
        <div class="confirmation-grid">
          <div class="confirmation-item">
            <el-icon :color="structure.volume_confirmation ? '#67c23a' : '#f56c6c'">
              <component :is="structure.volume_confirmation ? 'Check' : 'Close'" />
            </el-icon>
            <span>成交量确认</span>
          </div>
          <div class="confirmation-item">
            <el-icon :color="structure.macd_confirmation ? '#67c23a' : '#f56c6c'">
              <component :is="structure.macd_confirmation ? 'Check' : 'Close'" />
            </el-icon>
            <span>MACD确认</span>
          </div>
          <div class="confirmation-item">
            <el-icon :color="structure.rsi_confirmation ? '#67c23a' : '#f56c6c'">
              <component :is="structure.rsi_confirmation ? 'Check' : 'Close'" />
            </el-icon>
            <span>RSI确认</span>
          </div>
          <div class="confirmation-item">
            <el-icon :color="structure.bollinger_confirmation ? '#67c23a' : '#f56c6c'">
              <component :is="structure.bollinger_confirmation ? 'Check' : 'Close'" />
            </el-icon>
            <span>布林带确认</span>
          </div>
        </div>
      </div>

      <!-- 机器学习评估 -->
      <div class="ml-section">
        <h5>机器学习评估</h5>
        <div class="ml-metrics">
          <div class="metric-item">
            <span class="metric-label">预测概率:</span>
            <el-progress 
              :percentage="structure.ml_probability * 100" 
              :color="getProgressColor(structure.ml_probability)"
            />
          </div>
          <div class="metric-item">
            <span class="metric-label">历史成功率:</span>
            <el-progress 
              :percentage="structure.historical_success_rate * 100"
              :color="getProgressColor(structure.historical_success_rate)"
            />
          </div>
        </div>
      </div>
    </div>

    <!-- 笔详情 -->
    <div v-if="structure.direction && structure.start_fenxing" class="structure-section">
      <h4>笔信息</h4>
      <div class="info-grid">
        <div class="info-item">
          <span class="label">方向:</span>
          <span class="value" :class="structure.direction === 'up' ? 'text-danger' : 'text-success'">
            {{ structure.direction === 'up' ? '上笔' : '下笔' }}
          </span>
        </div>
        <div class="info-item">
          <span class="label">起始价格:</span>
          <span class="value">¥{{ formatPrice(structure.start_fenxing.price) }}</span>
        </div>
        <div class="info-item">
          <span class="label">结束价格:</span>
          <span class="value">¥{{ formatPrice(structure.end_fenxing.price) }}</span>
        </div>
        <div class="info-item">
          <span class="label">价格变化:</span>
          <span class="value" :class="structure.price_change > 0 ? 'text-danger' : 'text-success'">
            {{ structure.price_change > 0 ? '+' : '' }}{{ formatPrice(structure.price_change) }}
            ({{ formatPercent(structure.price_change_pct / 100) }})
          </span>
        </div>
        <div class="info-item">
          <span class="label">持续时间:</span>
          <span class="value">{{ structure.duration }}个K线</span>
        </div>
        <div class="info-item">
          <span class="label">笔的强度:</span>
          <span class="value">{{ formatPercent(structure.strength) }}</span>
        </div>
        <div class="info-item">
          <span class="label">笔的纯度:</span>
          <span class="value">{{ formatPercent(structure.purity) }}</span>
        </div>
        <div class="info-item">
          <span class="label">有效概率:</span>
          <span class="value">{{ formatPercent(structure.validity_probability) }}</span>
        </div>
      </div>

      <!-- 背离分析 -->
      <div class="divergence-section">
        <h5>背离分析</h5>
        <div class="divergence-grid">
          <div class="divergence-item">
            <el-icon :color="structure.macd_divergence ? '#e6a23c' : '#909399'">
              <component :is="structure.macd_divergence ? 'Warning' : 'Minus'" />
            </el-icon>
            <span>MACD背离</span>
          </div>
          <div class="divergence-item">
            <el-icon :color="structure.rsi_divergence ? '#e6a23c' : '#909399'">
              <component :is="structure.rsi_divergence ? 'Warning' : 'Minus'" />
            </el-icon>
            <span>RSI背离</span>
          </div>
        </div>
      </div>

      <!-- 成交量分析 -->
      <div class="volume-section">
        <h5>成交量分析</h5>
        <div class="volume-info">
          <div class="volume-item">
            <span class="label">量价配合:</span>
            <el-tag :type="structure.volume_confirmation ? 'success' : 'info'" size="small">
              {{ structure.volume_confirmation ? '良好' : '一般' }}
            </el-tag>
          </div>
          <div class="volume-item">
            <span class="label">成交量模式:</span>
            <span class="value">{{ getVolumePatternText(structure.volume_pattern) }}</span>
          </div>
          <div class="volume-item">
            <span class="label">平均量比:</span>
            <span class="value">{{ structure.avg_volume_ratio?.toFixed(2) || 'N/A' }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 中枢详情 -->
    <div v-if="structure.high && structure.low && structure.center" class="structure-section">
      <h4>中枢信息</h4>
      <div class="info-grid">
        <div class="info-item">
          <span class="label">中枢高点:</span>
          <span class="value">¥{{ formatPrice(structure.high) }}</span>
        </div>
        <div class="info-item">
          <span class="label">中枢低点:</span>
          <span class="value">¥{{ formatPrice(structure.low) }}</span>
        </div>
        <div class="info-item">
          <span class="label">中枢中心:</span>
          <span class="value">¥{{ formatPrice(structure.center) }}</span>
        </div>
        <div class="info-item">
          <span class="label">区间大小:</span>
          <span class="value">¥{{ formatPrice(structure.range_size) }}</span>
        </div>
        <div class="info-item">
          <span class="label">持续时间:</span>
          <span class="value">{{ structure.duration_days?.toFixed(1) }}天</span>
        </div>
        <div class="info-item">
          <span class="label">延伸次数:</span>
          <span class="value">{{ structure.extension_count }}次</span>
        </div>
        <div class="info-item">
          <span class="label">突破尝试:</span>
          <span class="value">{{ structure.breakthrough_attempts }}次</span>
        </div>
        <div class="info-item">
          <span class="label">整理质量:</span>
          <span class="value">{{ formatPercent(structure.consolidation_quality) }}</span>
        </div>
      </div>

      <!-- 突破概率分析 -->
      <div class="breakout-section">
        <h5>突破概率分析</h5>
        <div class="probability-chart">
          <div class="probability-item">
            <span class="label">向上突破:</span>
            <el-progress 
              :percentage="structure.breakout_probability * 100"
              color="#67c23a"
              :show-text="true"
            />
          </div>
          <div class="probability-item">
            <span class="label">向下跌破:</span>
            <el-progress 
              :percentage="structure.breakdown_probability * 100"
              color="#f56c6c"
              :show-text="true"
            />
          </div>
          <div class="probability-item">
            <span class="label">继续整理:</span>
            <el-progress 
              :percentage="structure.continuation_probability * 100"
              color="#e6a23c"
              :show-text="true"
            />
          </div>
        </div>
      </div>

      <!-- 方向倾向 -->
      <div class="bias-section">
        <h5>突破方向倾向</h5>
        <div class="bias-indicator">
          <el-tag 
            :type="getBiasTagType(structure.breakout_direction_bias)" 
            size="large"
          >
            {{ getBiasText(structure.breakout_direction_bias) }}
          </el-tag>
        </div>
      </div>
    </div>

    <!-- 操作建议 -->
    <div class="action-section">
      <h4>操作建议</h4>
      <div class="action-content">
        <el-alert
          :title="getActionTitle()"
          :type="getActionType()"
          :description="getActionDescription()"
          show-icon
          :closable="false"
        />
      </div>
    </div>

    <!-- 相关数据 -->
    <div class="related-section">
      <h4>相关数据</h4>
      <div class="related-buttons">
        <el-button size="small" @click="showRelatedStructures">
          <el-icon><Connection /></el-icon>
          相关结构
        </el-button>
        <el-button size="small" @click="showHistoricalAnalysis">
          <el-icon><TrendCharts /></el-icon>
          历史分析
        </el-button>
        <el-button size="small" @click="exportStructureData">
          <el-icon><Download /></el-icon>
          导出数据
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { formatPrice, formatPercent, formatDateTime } from '@/utils/format'
import type { ChanStructure } from '@/types/api'

interface Props {
  structure: any // 缠论结构对象
  symbol: string
  timeframe: string
}

const props = defineProps<Props>()
const emit = defineEmits(['show-related', 'show-historical', 'export-data'])

// 计算属性
const getStructureTitle = () => {
  if (props.structure.fenxing_type) {
    return props.structure.fenxing_type === 'top' ? '顶分型' : '底分型'
  } else if (props.structure.direction && props.structure.start_fenxing) {
    return props.structure.direction === 'up' ? '上笔' : '下笔'
  } else if (props.structure.high && props.structure.low) {
    return '中枢'
  } else if (props.structure.constituent_bis) {
    return props.structure.direction === 'up' ? '上线段' : '下线段'
  }
  return '未知结构'
}

const getStructureTagType = () => {
  if (props.structure.confidence > 0.8) return 'success'
  if (props.structure.confidence > 0.6) return 'warning'
  return 'info'
}

const getStructureLevel = () => {
  return props.timeframe === 'daily' ? '日线级别' : 
         props.timeframe === '30min' ? '30分钟级别' : 
         props.timeframe === '5min' ? '5分钟级别' : '未知级别'
}

const getProgressColor = (value: number) => {
  if (value > 0.8) return '#67c23a'
  if (value > 0.6) return '#e6a23c'
  return '#f56c6c'
}

const getVolumePatternText = (pattern: string) => {
  const patterns: Record<string, string> = {
    'increasing': '放量',
    'decreasing': '缩量',
    'normal': '正常',
    'spike': '异常放量',
    'dry': '异常缩量'
  }
  return patterns[pattern] || pattern
}

const getBiasTagType = (bias: string) => {
  if (bias === 'up') return 'danger'
  if (bias === 'down') return 'success'
  return 'info'
}

const getBiasText = (bias: string) => {
  if (bias === 'up') return '向上倾向'
  if (bias === 'down') return '向下倾向'
  return '中性'
}

const getActionTitle = () => {
  if (props.structure.fenxing_type) {
    return props.structure.fenxing_type === 'top' ? '关注卖点' : '关注买点'
  } else if (props.structure.breakout_probability > 0.7) {
    return '突破概率较高'
  } else if (props.structure.continuation_probability > 0.7) {
    return '继续整理概率较高'
  }
  return '持续观察'
}

const getActionType = () => {
  if (props.structure.confidence > 0.8) return 'success'
  if (props.structure.confidence > 0.6) return 'warning'
  return 'info'
}

const getActionDescription = () => {
  if (props.structure.fenxing_type === 'top') {
    return '顶分型出现，关注价格是否有效跌破，可考虑减仓或止盈操作。'
  } else if (props.structure.fenxing_type === 'bottom') {
    return '底分型出现，关注价格是否有效突破，可考虑逢低布局。'
  } else if (props.structure.breakout_probability > 0.7) {
    return '中枢突破概率较高，可关注突破确认后的跟进机会。'
  } else if (props.structure.breakdown_probability > 0.7) {
    return '中枢跌破概率较高，注意风险控制，及时止损。'
  }
  return '当前结构需要进一步确认，建议持续观察后续变化。'
}

// 方法
const showRelatedStructures = () => {
  emit('show-related', props.structure)
}

const showHistoricalAnalysis = () => {
  emit('show-historical', props.structure)
}

const exportStructureData = () => {
  emit('export-data', props.structure)
}
</script>

<style lang="scss" scoped>
.chan-structure-detail {
  padding: 20px;

  .detail-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
    padding-bottom: 10px;
    border-bottom: 1px solid #ebeef5;

    h3 {
      margin: 0;
      color: #303133;
      font-size: 18px;
    }
  }

  .structure-section {
    margin-bottom: 24px;

    h4 {
      margin: 0 0 16px 0;
      color: #606266;
      font-size: 16px;
      font-weight: 600;
    }

    h5 {
      margin: 16px 0 12px 0;
      color: #909399;
      font-size: 14px;
      font-weight: 600;
    }
  }

  .info-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 12px;
    margin-bottom: 16px;
  }

  .info-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 8px 12px;
    background: #f8f9fa;
    border-radius: 4px;

    .label {
      color: #909399;
      font-size: 13px;
    }

    .value {
      color: #303133;
      font-weight: 500;
      font-size: 13px;

      &.text-danger {
        color: #f56c6c;
      }

      &.text-success {
        color: #67c23a;
      }
    }
  }

  .confirmation-section {
    margin-top: 16px;
  }

  .confirmation-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 12px;
  }

  .confirmation-item {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 8px 12px;
    background: #f8f9fa;
    border-radius: 4px;
    font-size: 13px;
    color: #606266;
  }

  .ml-section {
    margin-top: 16px;
  }

  .ml-metrics {
    display: flex;
    flex-direction: column;
    gap: 12px;
  }

  .metric-item {
    .metric-label {
      display: block;
      margin-bottom: 4px;
      color: #909399;
      font-size: 13px;
    }
  }

  .divergence-section {
    margin-top: 16px;
  }

  .divergence-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 12px;
  }

  .divergence-item {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 8px 12px;
    background: #f8f9fa;
    border-radius: 4px;
    font-size: 13px;
    color: #606266;
  }

  .volume-section {
    margin-top: 16px;
  }

  .volume-info {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }

  .volume-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 6px 12px;
    background: #f8f9fa;
    border-radius: 4px;

    .label {
      color: #909399;
      font-size: 13px;
    }

    .value {
      color: #303133;
      font-size: 13px;
    }
  }

  .breakout-section {
    margin-top: 16px;
  }

  .probability-chart {
    display: flex;
    flex-direction: column;
    gap: 12px;
  }

  .probability-item {
    .label {
      display: block;
      margin-bottom: 4px;
      color: #909399;
      font-size: 13px;
    }
  }

  .bias-section {
    margin-top: 16px;
  }

  .bias-indicator {
    text-align: center;
    padding: 16px;
  }

  .action-section {
    margin-bottom: 24px;

    h4 {
      margin: 0 0 16px 0;
      color: #606266;
      font-size: 16px;
      font-weight: 600;
    }
  }

  .related-section {
    h4 {
      margin: 0 0 16px 0;
      color: #606266;
      font-size: 16px;
      font-weight: 600;
    }
  }

  .related-buttons {
    display: flex;
    gap: 12px;
    flex-wrap: wrap;
  }
}
</style>