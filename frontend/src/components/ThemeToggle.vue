<template>
  <div class="theme-toggle-wrapper">
    <el-dropdown 
      trigger="click" 
      placement="bottom-end"
      @command="handleCommand"
      class="theme-dropdown"
    >
      <el-button 
        class="theme-toggle-btn"
        :class="{ 'is-dark': isDark }"
        circle
        size="large"
      >
        <el-icon class="theme-icon">
          <component :is="currentIcon" />
        </el-icon>
      </el-button>
      
      <template #dropdown>
        <el-dropdown-menu class="theme-menu">
          <el-dropdown-item 
            command="light"
            :class="{ active: systemPreference === 'light' }"
            class="theme-option"
          >
            <el-icon class="option-icon"><Sunny /></el-icon>
            <span class="option-text">浅色主题</span>
            <div class="option-preview light-preview"></div>
          </el-dropdown-item>
          
          <el-dropdown-item 
            command="dark"
            :class="{ active: systemPreference === 'dark' }"
            class="theme-option"
          >
            <el-icon class="option-icon"><Moon /></el-icon>
            <span class="option-text">深色主题</span>
            <div class="option-preview dark-preview"></div>
          </el-dropdown-item>
          
          <el-dropdown-item 
            command="auto"
            :class="{ active: systemPreference === 'auto' }"
            class="theme-option"
          >
            <el-icon class="option-icon"><Monitor /></el-icon>
            <span class="option-text">跟随系统</span>
            <div class="option-preview auto-preview"></div>
          </el-dropdown-item>
        </el-dropdown-menu>
      </template>
    </el-dropdown>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Sunny, Moon, Monitor } from '@element-plus/icons-vue'
import { useThemeStore } from '@/stores/theme'

const themeStore = useThemeStore()
const { isDark, systemPreference, setTheme } = themeStore

// 当前图标
const currentIcon = computed(() => {
  if (systemPreference.value === 'auto') {
    return Monitor
  }
  return isDark.value ? Moon : Sunny
})

// 处理主题切换
const handleCommand = (command) => {
  setTheme(command)
}
</script>

<style scoped>
.theme-toggle-wrapper {
  position: relative;
}

.theme-toggle-btn {
  background: var(--bg-glass) !important;
  backdrop-filter: var(--backdrop-blur);
  border: 1px solid var(--glass-border) !important;
  color: var(--text-primary) !important;
  width: 44px;
  height: 44px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
}

.theme-toggle-btn:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-lg);
  border-color: var(--border-focus) !important;
}

.theme-toggle-btn.is-dark {
  background: var(--bg-glass) !important;
}

.theme-icon {
  font-size: 20px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.theme-toggle-btn:hover .theme-icon {
  transform: rotate(180deg);
}

/* 下拉菜单样式 */
:deep(.theme-dropdown .el-dropdown__popper) {
  background: var(--bg-glass) !important;
  backdrop-filter: var(--backdrop-blur);
  border: 1px solid var(--glass-border) !important;
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-xl);
  padding: var(--space-sm);
  min-width: 200px;
}

:deep(.theme-menu) {
  background: transparent !important;
  border: none !important;
  box-shadow: none !important;
  padding: 0;
}

.theme-option {
  display: flex !important;
  align-items: center;
  gap: var(--space-md);
  padding: var(--space-md) var(--space-lg) !important;
  margin-bottom: var(--space-xs);
  border-radius: var(--radius-lg) !important;
  color: var(--text-primary) !important;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
}

.theme-option:hover {
  background: var(--color-primary-light) !important;
  color: var(--color-primary) !important;
  transform: translateX(4px);
}

.theme-option.active {
  background: var(--color-primary) !important;
  color: var(--text-inverse) !important;
}

.theme-option.active::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  width: 3px;
  height: 100%;
  background: var(--text-inverse);
  border-radius: 0 2px 2px 0;
}

.option-icon {
  font-size: 18px;
  flex-shrink: 0;
}

.option-text {
  flex: 1;
  font-weight: 500;
  font-size: 14px;
}

.option-preview {
  width: 24px;
  height: 16px;
  border-radius: var(--radius-sm);
  border: 1px solid var(--border-primary);
  flex-shrink: 0;
  position: relative;
  overflow: hidden;
}

.light-preview {
  background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
}

.dark-preview {
  background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
}

.auto-preview {
  background: linear-gradient(90deg, #ffffff 0%, #ffffff 50%, #1e293b 50%, #0f172a 100%);
}

.auto-preview::after {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 1px;
  height: 80%;
  background: var(--border-primary);
}

/* 主题切换动画 */
.theme-toggle-btn,
.theme-option {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .theme-toggle-btn {
    width: 40px;
    height: 40px;
  }
  
  .theme-icon {
    font-size: 18px;
  }
  
  :deep(.theme-dropdown .el-dropdown__popper) {
    min-width: 180px;
  }
  
  .option-text {
    font-size: 13px;
  }
}
</style> 