<template>
  <div id="app" class="app-container">
    <!-- 现代化顶部导航栏 -->
    <header class="modern-header">
      <div class="header-glass">
        <div class="header-content">
          <div class="logo-section">
            <div class="logo-wrapper">
              <div class="logo-icon">
                <svg viewBox="0 0 24 24" class="icon-svg">
                  <path d="M3 13h8V3H9v6H3v4zm0 8h6v-6H3v6zm10 0h8v-6h-2v4h-6v2zm8-8V9h-6v4h6z" fill="currentColor"/>
                </svg>
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
              
              <el-tooltip :content="isDark ? '切换到亮色模式' : '切换到暗色模式'" placement="bottom">
                <button 
                  class="action-btn theme-btn"
                  @click="toggleTheme"
                >
                  <el-icon>
                    <component :is="isDark ? Sunny : Moon" />
                  </el-icon>
                </button>
              </el-tooltip>
              
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
import { RefreshRight, Sunny, Moon, Setting } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { useGlobalStore } from '@/stores/global'

const global = useGlobalStore()
const refreshing = ref(false)
const isDark = ref(false)
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

// 切换主题
const toggleTheme = () => {
  isDark.value = !isDark.value
  const html = document.documentElement
  if (isDark.value) {
    html.classList.add('dark')
  } else {
    html.classList.remove('dark')
  }
  localStorage.setItem('theme', isDark.value ? 'dark' : 'light')
}

// 初始化主题
onMounted(() => {
  const savedTheme = localStorage.getItem('theme')
  isDark.value = savedTheme === 'dark'
  if (isDark.value) {
    document.documentElement.classList.add('dark')
  }
})
</script>

<style scoped>
.app-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
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
  background: linear-gradient(135deg, #667eea, #764ba2);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 16px rgba(102, 126, 234, 0.3);
}

.icon-svg {
  width: 24px;
  height: 24px;
  color: white;
}

.logo-text {
  display: flex;
  flex-direction: column;
}

.app-title {
  margin: 0;
  font-size: 24px;
  font-weight: 700;
  color: white;
  line-height: 1.2;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.app-subtitle {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.8);
  font-weight: 500;
  letter-spacing: 0.5px;
}

/* 中央状态区域 */
.header-center {
  flex: 1;
  display: flex;
  justify-content: center;
}

.status-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 20px;
  backdrop-filter: blur(10px);
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

.status-text {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.9);
  font-weight: 500;
}

/* 操作按钮区域 */
.header-actions {
  flex: 1;
  display: flex;
  justify-content: flex-end;
}

.action-group {
  display: flex;
  align-items: center;
  gap: 8px;
}

.action-btn {
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

.action-btn:hover {
  background: rgba(255, 255, 255, 0.2);
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
  
  .app-title {
    font-size: 20px;
  }
  
  .header-center {
    display: none;
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