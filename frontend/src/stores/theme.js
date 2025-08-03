import { ref, computed } from 'vue'
import { defineStore } from 'pinia'

export const useThemeStore = defineStore('theme', () => {
  // 主题状态
  const isDark = ref(false)
  const systemPreference = ref('auto') // 'light', 'dark', 'auto'
  
  // 计算当前主题
  const currentTheme = computed(() => {
    if (systemPreference.value === 'auto') {
      return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
    }
    return systemPreference.value
  })
  
  // 初始化主题
  const initTheme = () => {
    // 从localStorage读取用户偏好
    const saved = localStorage.getItem('theme-preference')
    if (saved) {
      systemPreference.value = saved
    }
    
    // 应用主题
    applyTheme()
    
    // 监听系统主题变化
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', applyTheme)
  }
  
  // 应用主题
  const applyTheme = () => {
    const theme = currentTheme.value
    isDark.value = theme === 'dark'
    
    // 更新document类名
    document.documentElement.classList.toggle('dark', isDark.value)
    document.documentElement.setAttribute('data-theme', theme)
    
    // 更新Element Plus主题
    if (isDark.value) {
      document.documentElement.classList.add('dark')
    } else {
      document.documentElement.classList.remove('dark')
    }
  }
  
  // 切换主题
  const toggleTheme = () => {
    systemPreference.value = isDark.value ? 'light' : 'dark'
    localStorage.setItem('theme-preference', systemPreference.value)
    applyTheme()
  }
  
  // 设置主题
  const setTheme = (theme) => {
    systemPreference.value = theme
    localStorage.setItem('theme-preference', theme)
    applyTheme()
  }
  
  return {
    isDark,
    systemPreference,
    currentTheme,
    initTheme,
    toggleTheme,
    setTheme
  }
}) 