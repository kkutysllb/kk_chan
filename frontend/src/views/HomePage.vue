<template>
  <div class="home-page">
    <div class="page-layout">
      <!-- 左侧配置面板 -->
      <aside class="sidebar-panel" :class="{ collapsed: sidebarCollapsed }">
        <div class="sidebar-header">
          <div class="sidebar-title" v-show="!sidebarCollapsed">
            <el-icon class="title-icon"><Setting /></el-icon>
            <span>分析配置</span>
          </div>
          <button 
            class="collapse-btn"
            @click="toggleSidebar"
            :title="sidebarCollapsed ? '展开面板' : '收起面板'"
          >
            <el-icon>
              <component :is="sidebarCollapsed ? 'ArrowRight' : 'ArrowLeft'" />
            </el-icon>
          </button>
        </div>
        <div class="sidebar-content">
          <StockSelector />
        </div>
      </aside>

      <!-- 主内容区域 -->
      <main class="main-content">
        <div class="content-wrapper">
          <!-- 标签导航 -->
          <nav class="tab-navigation">
            <div class="tab-list">
              <button 
                v-for="tab in tabs" 
                :key="tab.name"
                class="tab-item"
                :class="{ active: activeTab === tab.name }"
                @click="activeTab = tab.name"
              >
                <el-icon class="tab-icon">
                  <component :is="tab.icon" />
                </el-icon>
                <span class="tab-label">{{ tab.label }}</span>
                <div class="tab-indicator"></div>
              </button>
            </div>
          </nav>
          
          <!-- 内容区域 -->
          <div class="content-area">
            <div class="content-panel">
              <transition name="fade" mode="out-in">
                <component :is="currentComponent" :key="activeTab" />
              </transition>
            </div>
          </div>
        </div>
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useGlobalStore } from '@/stores/global'
import { Setting, ArrowLeft, ArrowRight, TrendCharts, DataAnalysis, Bell, Document } from '@element-plus/icons-vue'
import StockSelector from '@/components/StockSelector.vue'
import ChanChart from '@/components/ChanChart.vue'
import DataDetail from '@/components/DataDetail.vue'
import TradingSignals from '@/components/TradingSignals.vue'
import AnalysisReport from '@/components/AnalysisReport.vue'

const global = useGlobalStore()
const activeTab = ref('chart')
const sidebarCollapsed = ref(false)

// 标签配置
const tabs = ref([
  { name: 'chart', label: '图表分析', icon: 'TrendCharts' },
  { name: 'data', label: '数据详情', icon: 'DataAnalysis' },
  { name: 'signals', label: '交易信号', icon: 'Bell' },
  { name: 'report', label: '分析报告', icon: 'Document' }
])

// 当前组件
const currentComponent = computed(() => {
  const componentMap = {
    chart: ChanChart,
    data: DataDetail,
    signals: TradingSignals,
    report: AnalysisReport
  }
  return componentMap[activeTab.value]
})

// 切换侧边栏
const toggleSidebar = () => {
  sidebarCollapsed.value = !sidebarCollapsed.value
}
</script>

<style scoped>
.home-page {
  min-height: calc(100vh - 80px);
  position: relative;
  overflow: auto;
}

.page-layout {
  min-height: 100%;
  display: flex;
  gap: 24px;
  padding: 24px;
  position: relative;
  z-index: 1;
}

/* 侧边栏面板 */
.sidebar-panel {
  width: 380px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-radius: 24px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.1);
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.sidebar-panel.collapsed {
  width: 80px;
}

.dark .sidebar-panel {
  background: rgba(30, 41, 59, 0.95);
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.sidebar-header {
  padding: 20px 24px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.1), rgba(118, 75, 162, 0.1));
}

.dark .sidebar-header {
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.sidebar-title {
  display: flex;
  align-items: center;
  gap: 12px;
  font-weight: 600;
  color: var(--el-text-color-primary);
  font-size: 16px;
}

.title-icon {
  color: #667eea;
  font-size: 18px;
}

.collapse-btn {
  width: 32px;
  height: 32px;
  border: none;
  border-radius: 8px;
  background: rgba(102, 126, 234, 0.1);
  color: #667eea;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.collapse-btn:hover {
  background: rgba(102, 126, 234, 0.2);
  transform: scale(1.1);
}

.sidebar-content {
  flex: 1;
  overflow-y: auto;
  padding: 0;
}

/* 主内容区域 */
.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.content-wrapper {
  flex: 1;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-radius: 24px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
  min-height: 0;
}

.dark .content-wrapper {
  background: rgba(30, 41, 59, 0.95);
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

/* 标签导航 */
.tab-navigation {
  padding: 24px 24px 0;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.05), rgba(118, 75, 162, 0.05));
}

.tab-list {
  display: flex;
  gap: 8px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
}

.dark .tab-list {
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.tab-item {
  position: relative;
  padding: 16px 24px;
  border: none;
  background: transparent;
  color: var(--el-text-color-secondary);
  cursor: pointer;
  transition: all 0.3s ease;
  border-radius: 12px 12px 0 0;
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 500;
  font-size: 14px;
  min-width: 120px;
  justify-content: center;
}

.tab-item:hover {
  color: #667eea;
  background: rgba(102, 126, 234, 0.1);
  transform: translateY(-2px);
}

.tab-item.active {
  color: #667eea;
  background: rgba(255, 255, 255, 0.8);
  box-shadow: 0 4px 16px rgba(102, 126, 234, 0.2);
}

.dark .tab-item.active {
  background: rgba(30, 41, 59, 0.8);
}

.tab-icon {
  font-size: 16px;
}

.tab-indicator {
  position: absolute;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 0;
  height: 3px;
  background: linear-gradient(135deg, #667eea, #764ba2);
  border-radius: 2px;
  transition: all 0.3s ease;
}

.tab-item.active .tab-indicator {
  width: 60%;
}

/* 内容区域 */
.content-area {
  flex: 1;
  padding: 24px;
  min-height: 0;
}

.content-panel {
  min-height: 600px;
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.5);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.3);
}

.dark .content-panel {
  background: rgba(15, 23, 42, 0.5);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

/* 过渡动画 */
.fade-enter-active,
.fade-leave-active {
  transition: all 0.3s ease;
}

.fade-enter-from {
  opacity: 0;
  transform: translateY(20px);
}

.fade-leave-to {
  opacity: 0;
  transform: translateY(-20px);
}

/* 滚动条样式 */
.sidebar-content::-webkit-scrollbar {
  width: 6px;
}

.sidebar-content::-webkit-scrollbar-track {
  background: rgba(0, 0, 0, 0.05);
  border-radius: 3px;
}

.sidebar-content::-webkit-scrollbar-thumb {
  background: rgba(102, 126, 234, 0.3);
  border-radius: 3px;
}

.sidebar-content::-webkit-scrollbar-thumb:hover {
  background: rgba(102, 126, 234, 0.5);
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .page-layout {
    gap: 16px;
    padding: 16px;
  }
  
  .sidebar-panel {
    width: 320px;
  }
}

@media (max-width: 768px) {
  .page-layout {
    flex-direction: column;
    gap: 12px;
    padding: 12px;
  }
  
  .sidebar-panel {
    width: 100%;
    height: auto;
    max-height: 300px;
  }
  
  .sidebar-panel.collapsed {
    width: 100%;
    height: 60px;
  }
  
  .tab-list {
    overflow-x: auto;
    scrollbar-width: none;
    -ms-overflow-style: none;
  }
  
  .tab-list::-webkit-scrollbar {
    display: none;
  }
  
  .tab-item {
    min-width: 100px;
    padding: 12px 16px;
    font-size: 12px;
  }
}

@media (max-width: 480px) {
   .tab-item .tab-label {
     display: none;
   }
   
   .tab-item {
     min-width: 60px;
     padding: 12px;
   }
   
   .content-area {
     padding: 16px;
   }
 }
</style>