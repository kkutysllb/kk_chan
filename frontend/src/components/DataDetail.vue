<template>
  <div class="data-detail">
    <div class="detail-container">
      <!-- 无数据状态 -->
      <div v-if="!hasData" class="empty-state">
        <el-empty description="暂无分析数据" :image-size="120">
          <el-button type="primary" @click="$emit('analyze')">
            开始分析
          </el-button>
        </el-empty>
      </div>

      <!-- 有数据时显示详情 -->
      <div v-else class="data-content">
        <!-- 基础信息 -->
        <el-card class="info-card" shadow="hover">
          <template #header>
            <span class="card-title">基础信息</span>
          </template>
          <div class="info-grid">
            <div class="info-item">
              <span class="info-label">股票代码:</span>
              <span class="info-value">{{ analysisData?.meta?.symbol || '-' }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">时间级别:</span>
              <span class="info-value">{{ timeframeText }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">数据条数:</span>
              <span class="info-value">{{ analysisData?.meta?.data_count || 0 }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">分析时间:</span>
              <span class="info-value">{{ formatTime(analysisData?.meta?.analysis_time) }}</span>
            </div>
          </div>
        </el-card>

        <!-- 分析统计 -->
        <el-card class="stats-card" shadow="hover">
          <template #header>
            <span class="card-title">分析统计</span>
          </template>
          <div class="stats-grid">
            <div class="stats-item">
              <div class="stats-number">{{ summary?.fenxing_count || 0 }}</div>
              <div class="stats-label">分型</div>
            </div>
            <div class="stats-item">
              <div class="stats-number">{{ summary?.bi_count || 0 }}</div>
              <div class="stats-label">笔</div>
            </div>
            <div class="stats-item">
              <div class="stats-number">{{ summary?.zhongshu_count || 0 }}</div>
              <div class="stats-label">中枢</div>
            </div>
            <div class="stats-item">
              <div class="stats-number">{{ summary?.signal_count || 0 }}</div>
              <div class="stats-label">信号</div>
            </div>
          </div>
        </el-card>

        <!-- 分型详情 -->
        <el-card class="detail-card" shadow="hover">
          <template #header>
            <span class="card-title">分型详情</span>
          </template>
          <el-table
            :data="fenxingList"
            size="small"
            max-height="300"
            empty-text="暂无分型数据"
          >
            <el-table-column prop="name" label="类型" width="80" />
            <el-table-column prop="price" label="价格" width="100">
              <template #default="{ row }">
                {{ row.value?.toFixed(2) || '-' }}
              </template>
            </el-table-column>
            <el-table-column prop="strength" label="强度" width="100">
              <template #default="{ row }">
                {{ (row.strength * 100)?.toFixed(2) || '-' }}%
              </template>
            </el-table-column>
            <el-table-column prop="confirmed" label="确认" width="80">
              <template #default="{ row }">
                <el-tag
                  :type="row.confirmed ? 'success' : 'warning'"
                  size="small"
                >
                  {{ row.confirmed ? '已确认' : '待确认' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="coord" label="时间">
              <template #default="{ row }">
                {{ row.coord?.[0] || '-' }}
              </template>
            </el-table-column>
          </el-table>
        </el-card>

        <!-- 笔段详情 -->
        <el-card class="detail-card" shadow="hover">
          <template #header>
            <span class="card-title">笔段详情</span>
          </template>
          <el-table
            :data="biList"
            size="small"
            max-height="300"
            empty-text="暂无笔段数据"
          >
            <el-table-column prop="name" label="类型" width="80" />
            <el-table-column prop="direction" label="方向" width="80">
              <template #default="{ row }">
                <el-tag
                  :type="row.direction === 'up' ? 'danger' : 'success'"
                  size="small"
                >
                  {{ row.direction === 'up' ? '上笔' : '下笔' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="amplitude" label="幅度" width="100">
              <template #default="{ row }">
                {{ (row.amplitude * 100)?.toFixed(2) || '-' }}%
              </template>
            </el-table-column>
            <el-table-column prop="length" label="长度" width="80" />
            <el-table-column prop="coords" label="起止时间">
              <template #default="{ row }">
                <div v-if="row.coords?.length >= 2">
                  {{ row.coords[0][0] }} ~ {{ row.coords[1][0] }}
                </div>
                <span v-else>-</span>
              </template>
            </el-table-column>
          </el-table>
        </el-card>

        <!-- 中枢详情 -->
        <el-card class="detail-card" shadow="hover">
          <template #header>
            <span class="card-title">中枢详情</span>
          </template>
          <el-table
            :data="zhongshuList"
            size="small"
            max-height="300"
            empty-text="暂无中枢数据"
          >
            <el-table-column prop="name" label="名称" width="100" />
            <el-table-column prop="high" label="高点" width="100">
              <template #default="{ row }">
                {{ row.high?.toFixed(2) || '-' }}
              </template>
            </el-table-column>
            <el-table-column prop="low" label="低点" width="100">
              <template #default="{ row }">
                {{ row.low?.toFixed(2) || '-' }}
              </template>
            </el-table-column>
            <el-table-column prop="center" label="中位" width="100">
              <template #default="{ row }">
                {{ row.center?.toFixed(2) || '-' }}
              </template>
            </el-table-column>
            <el-table-column prop="duration" label="持续天数" width="100" />
            <el-table-column prop="extend_count" label="延伸次数" width="100" />
          </el-table>
        </el-card>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useGlobalStore } from '@/stores/global'

const global = useGlobalStore()

// 计算属性
const hasData = computed(() => global.hasData)
const analysisData = computed(() => global.analysisData)
const summary = computed(() => global.analysisSummary)
const chanStructures = computed(() => global.chanStructures)

const timeframeText = computed(() => {
  const timeframeMap = {
    '5min': '5分钟',
    '30min': '30分钟',
    'daily': '日线',
  }
  return timeframeMap[analysisData.value?.meta?.timeframe] || '-'
})

const fenxingList = computed(() => {
  return chanStructures.value?.fenxing || []
})

const biList = computed(() => {
  return chanStructures.value?.bi || []
})

const zhongshuList = computed(() => {
  return chanStructures.value?.zhongshu || []
})

// 方法
const formatTime = (timeStr) => {
  if (!timeStr) return '-'
  try {
    const date = new Date(timeStr)
    return date.toLocaleString('zh-CN')
  } catch {
    return timeStr
  }
}

// 发射事件
defineEmits(['analyze'])
</script>

<style scoped>
.data-detail {
  height: 100%;
  overflow-y: auto;
  background: transparent;
}

.data-detail::-webkit-scrollbar {
  width: 6px;
}

.data-detail::-webkit-scrollbar-track {
  background: rgba(0, 0, 0, 0.05);
  border-radius: 3px;
}

.data-detail::-webkit-scrollbar-thumb {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 3px;
}

.data-detail::-webkit-scrollbar-thumb:hover {
  background: linear-gradient(135deg, #5a6fd8 0%, #6a4190 100%);
}

.detail-container {
  height: 100%;
  background: transparent;
}

.empty-state {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.data-content {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 20px;
  padding: 24px 0;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.data-content > * {
  animation: fadeInUp 0.4s ease;
}

.data-content > *:nth-child(1) { animation-delay: 0.1s; }
.data-content > *:nth-child(2) { animation-delay: 0.2s; }
.data-content > *:nth-child(3) { animation-delay: 0.3s; }
.data-content > *:nth-child(4) { animation-delay: 0.4s; }

.card-title {
  font-weight: 600;
  color: var(--el-text-color-primary);
  font-size: 16px;
}

.info-card {
  grid-column: span 2;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  transition: all 0.3s ease;
}

.dark .info-card {
  background: rgba(44, 62, 80, 0.95);
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
}

.info-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
}

.info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  margin: 4px 0;
  background: rgba(102, 126, 234, 0.05);
  border-radius: 8px;
  border: 1px solid rgba(102, 126, 234, 0.1);
  transition: all 0.3s ease;
}

.info-item:hover {
  background: rgba(102, 126, 234, 0.1);
  border-color: rgba(102, 126, 234, 0.2);
  transform: translateX(4px);
}

.info-label {
  color: var(--el-text-color-secondary);
  font-size: 14px;
  font-weight: 500;
}

.info-value {
  color: var(--el-text-color-primary);
  font-weight: 600;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.stats-card {
  grid-column: span 2;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  transition: all 0.3s ease;
}

.dark .stats-card {
  background: rgba(44, 62, 80, 0.95);
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
}

.stats-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}

.stats-item {
  text-align: center;
  padding: 20px;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
  border: 1px solid rgba(102, 126, 234, 0.2);
  border-radius: 12px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
}

.stats-item::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.1), transparent);
  transition: left 0.5s ease;
}

.stats-item:hover {
  transform: translateY(-4px) scale(1.02);
  box-shadow: 0 8px 25px rgba(102, 126, 234, 0.2);
  border-color: rgba(102, 126, 234, 0.4);
}

.stats-item:hover::before {
  left: 100%;
}

.stats-number {
  font-size: 28px;
  font-weight: 700;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-bottom: 8px;
}

.stats-label {
  font-size: 14px;
  color: var(--el-text-color-secondary);
  font-weight: 500;
}

.detail-card {
  min-height: 200px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  transition: all 0.3s ease;
}

.dark .detail-card {
  background: rgba(44, 62, 80, 0.95);
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
}

.detail-card:hover {
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

:deep(.el-table) {
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

:deep(.el-table th) {
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  color: var(--el-text-color-primary);
  font-weight: 600;
  border-bottom: 2px solid rgba(102, 126, 234, 0.1);
}

:deep(.el-table td) {
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
}

:deep(.el-table tr:hover) {
  background: rgba(102, 126, 234, 0.05);
}

:deep(.el-tag) {
  border-radius: 8px;
  font-weight: 500;
  padding: 4px 12px;
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .data-content {
    grid-template-columns: 1fr;
    gap: 16px;
  }
  
  .info-card,
  .stats-card {
    grid-column: span 1;
  }
}

@media (max-width: 768px) {
  .data-content {
    padding: 16px 0;
  }
  
  .info-grid {
    grid-template-columns: 1fr;
  }
  
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 12px;
  }
  
  .info-item {
    padding: 10px 12px;
  }
  
  .stats-item {
    padding: 16px;
  }
  
  .stats-number {
    font-size: 24px;
  }
}

@media (max-width: 480px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .data-content {
    gap: 12px;
    padding: 12px 0;
  }
}
</style>