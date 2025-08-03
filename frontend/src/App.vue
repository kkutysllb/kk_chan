<template>
  <div id="app" class="app-container">
    <!-- 现代化顶部导航栏 -->
    <header class="modern-header">
      <div class="header-glass">
        <div class="header-content">
          <div class="logo-section">
            <div class="logo-wrapper">
              <div class="logo-icon">
                <img src="@/assets/images/logo.jpg" alt="KK缠论" class="logo-image" />
              </div>
              <div class="logo-text">
                <h1 class="app-title">KK缠论</h1>
                <span class="app-subtitle">量化分析平台</span>
              </div>
            </div>
          </div>
          
          <div class="header-center">
            <div class="status-indicator">
              <div class="status-dot" :class="{ active: isConnected }"></div>
              <span class="status-text">{{ isConnected ? '实时连接' : '离线模式' }}</span>
            </div>
          </div>
          
          <div class="header-actions">
            <div class="nav-group">
              <el-button 
                type="primary" 
                :class="{ active: $route.name === 'Analysis' }"
                @click="$router.push('/analysis')"
                size="small"
                round
              >
                <el-icon><TrendCharts /></el-icon>
                缠论分析
              </el-button>
              
              <el-button 
                type="success" 
                :class="{ active: $route.name === 'StockSelection' }"
                @click="$router.push('/stock-selection')"
                size="small"
                round
              >
                <el-icon><DataAnalysis /></el-icon>
                智能选股
              </el-button>
            </div>
            
            <div class="action-group">
              <el-tooltip content="刷新数据" placement="bottom">
                <button 
                  class="action-btn refresh-btn"
                  @click="refreshData"
                  :disabled="refreshing"
                >
                  <el-icon :class="{ 'rotating': refreshing }">
                    <RefreshRight />
                  </el-icon>
                </button>
              </el-tooltip>
              
              <!-- 主题切换组件 -->
              <ThemeToggle />
              
              <el-tooltip content="设置" placement="bottom">
                <button class="action-btn settings-btn">
                  <el-icon><Setting /></el-icon>
                </button>
              </el-tooltip>
            </div>
          </div>
        </div>
      </div>
    </header>

    <!-- 主要内容区域 -->
    <main class="main-container">
      <router-view />
    </main>
    
    <!-- 背景装饰 -->
    <div class="bg-decoration">
      <div class="decoration-circle circle-1"></div>
      <div class="decoration-circle circle-2"></div>
      <div class="decoration-circle circle-3"></div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { RefreshRight, Setting, TrendCharts, DataAnalysis } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { useGlobalStore } from '@/stores/global'
import { useThemeStore } from '@/stores/theme'
import ThemeToggle from '@/components/ThemeToggle.vue'

const global = useGlobalStore()
const themeStore = useThemeStore()
const refreshing = ref(false)
const isConnected = ref(true)

// 模拟连接状态
setInterval(() => {
  // 这里可以添加实际的连接检测逻辑
  isConnected.value = Math.random() > 0.1 // 90%的时间保持连接
}, 5000)

// 刷新数据
const refreshData = async () => {
  refreshing.value = true
  try {
    await global.refreshAllData()
    ElMessage.success('数据刷新成功')
  } catch (error) {
    ElMessage.error('数据刷新失败')
    console.error('Refresh error:', error)
  } finally {
    refreshing.value = false
  }
}

// 初始化主题
onMounted(() => {
  themeStore.initTheme()
})
</script>

<style scoped>
.app-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: var(--bg-primary);
  position: relative;
}

/* 背景装饰 */
.bg-decoration {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 0;
}

.decoration-circle {
  position: absolute;
  border-radius: 50%;
  background: linear-gradient(45deg, rgba(255, 255, 255, 0.1), rgba(255, 255, 255, 0.05));
  animation: float 6s ease-in-out infinite;
}

.circle-1 {
  width: 300px;
  height: 300px;
  top: -150px;
  right: -150px;
  animation-delay: 0s;
}

.circle-2 {
  width: 200px;
  height: 200px;
  bottom: -100px;
  left: -100px;
  animation-delay: 2s;
}

.circle-3 {
  width: 150px;
  height: 150px;
  top: 50%;
  right: 10%;
  animation-delay: 4s;
}

@keyframes float {
  0%, 100% {
    transform: translateY(0px) rotate(0deg);
  }
  50% {
    transform: translateY(-20px) rotate(180deg);
  }
}

/* 现代化头部 */
.modern-header {
  position: relative;
  z-index: 100;
  height: 80px;
  padding: 0;
}

.header-glass {
  height: 100%;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(20px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.dark .header-glass {
  background: rgba(30, 41, 59, 0.8);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.header-content {
  height: 100%;
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 32px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

/* Logo区域 */
.logo-section {
  flex: 1;
}

.logo-wrapper {
  display: flex;
  align-items: center;
  gap: 16px;
}

.logo-icon {
  width: 48px;
  height: 48px;
  border-radius: var(--radius-xl);
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: var(--shadow-lg);
  overflow: hidden;
}

.logo-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: var(--radius-xl);
}

.logo-text {
  display: flex;
  flex-direction: column;
}

/* 深色主题 */
:root.dark .app-title {
  margin: 0;
  font-size: 24px;
  font-weight: 700;
  color: white;
  line-height: 1.2;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

:root.dark .app-subtitle {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.8);
  font-weight: 500;
  letter-spacing: 0.5px;
}

/* 浅色主题 */
:root:not(.dark) .app-title {
  margin: 0;
  font-size: 24px;
  font-weight: 700;
  color: #1f2937;
  line-height: 1.2;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

:root:not(.dark) .app-subtitle {
  font-size: 12px;
  color: #6b7280;
  font-weight: 500;
  letter-spacing: 0.5px;
}

/* 中央状态区域 */
.header-center {
  flex: 1;
  display: flex;
  justify-content: center;
}

/* 深色主题 */
:root.dark .status-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 20px;
  backdrop-filter: blur(10px);
}

:root.dark .status-text {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.9);
  font-weight: 500;
}

/* 浅色主题 */
:root:not(.dark) .status-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: rgba(0, 0, 0, 0.05);
  border-radius: 20px;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(0, 0, 0, 0.1);
}

:root:not(.dark) .status-text {
  font-size: 12px;
  color: #374151;
  font-weight: 500;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #ef4444;
  transition: all 0.3s ease;
}

.status-dot.active {
  background: #10b981;
  box-shadow: 0 0 8px rgba(16, 185, 129, 0.5);
}

/* 操作按钮区域 */
.header-actions {
  flex: 1;
  display: flex;
  justify-content: flex-end;
  align-items: center;
  gap: 20px;
}

.nav-group {
  display: flex;
  align-items: center;
  gap: 12px;
}

/* 深色主题导航按钮 */
:root.dark .nav-group .el-button {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: white;
  font-weight: 500;
  transition: all 0.3s ease;
}

:root.dark .nav-group .el-button:hover {
  background: rgba(255, 255, 255, 0.2);
  border-color: rgba(255, 255, 255, 0.3);
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
}

:root.dark .nav-group .el-button.active {
  background: rgba(255, 255, 255, 0.9);
  color: #667eea;
  border-color: rgba(255, 255, 255, 0.9);
  box-shadow: 0 4px 16px rgba(102, 126, 234, 0.3);
}

/* 浅色主题导航按钮 */
:root:not(.dark) .nav-group .el-button {
  background: rgba(0, 0, 0, 0.05);
  border: 1px solid rgba(0, 0, 0, 0.1);
  color: #374151;
  font-weight: 500;
  transition: all 0.3s ease;
}

:root:not(.dark) .nav-group .el-button:hover {
  background: rgba(0, 0, 0, 0.08);
  border-color: rgba(0, 0, 0, 0.15);
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
}

:root:not(.dark) .nav-group .el-button.active {
  background: #667eea;
  color: white;
  border-color: #667eea;
  box-shadow: 0 4px 16px rgba(102, 126, 234, 0.3);
}

.action-group {
  display: flex;
  align-items: center;
  gap: 8px;
}

/* 深色主题 */
:root.dark .action-btn {
  width: 44px;
  height: 44px;
  border: none;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  color: white;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
}

:root.dark .action-btn:hover {
  background: rgba(255, 255, 255, 0.2);
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
}

/* 浅色主题 */
:root:not(.dark) .action-btn {
  width: 44px;
  height: 44px;
  border: none;
  border-radius: 12px;
  background: rgba(0, 0, 0, 0.05);
  backdrop-filter: blur(10px);
  color: #374151;
  border: 1px solid rgba(0, 0, 0, 0.1);
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
}

:root:not(.dark) .action-btn:hover {
  background: rgba(0, 0, 0, 0.08);
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
}

.action-btn:active {
  transform: translateY(0);
}

.action-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
}

.refresh-btn:hover {
  background: linear-gradient(135deg, #10b981, #059669);
}

.theme-btn:hover {
  background: linear-gradient(135deg, #f59e0b, #d97706);
}

.settings-btn:hover {
  background: linear-gradient(135deg, #8b5cf6, #7c3aed);
}

/* 旋转动画 */
.rotating {
  animation: rotate 1s linear infinite;
}

@keyframes rotate {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

/* 主内容区域 */
.main-container {
  flex: 1;
  position: relative;
  z-index: 1;
  overflow: visible;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .header-content {
    padding: 0 16px;
  }
  
  .logo-wrapper {
    gap: 12px;
  }
  
  .logo-icon {
    width: 40px;
    height: 40px;
  }
  
  .logo-image {
    width: 100%;
    height: 100%;
    object-fit: cover;
    border-radius: var(--radius-lg);
  }
  
  .app-title {
    font-size: 20px;
  }
  
  .header-center {
    display: none;
  }
  
  .nav-group {
    gap: 8px;
  }
  
  .nav-group .el-button span {
    display: none;
  }
  
  .nav-group .el-button {
    min-width: 40px;
    padding: 8px 12px;
  }
  
  .action-btn {
    width: 40px;
    height: 40px;
  }
}

@media (max-width: 480px) {
  .app-subtitle {
    display: none;
  }
  
  .action-group {
    gap: 4px;
  }
}
</style>