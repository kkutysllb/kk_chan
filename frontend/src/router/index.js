import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('@/views/HomePage.vue'),
    meta: {
      title: '首页',
      keepAlive: true,
    },
  },
  {
    path: '/analysis/:symbol?',
    name: 'Analysis',
    component: () => import('@/views/AnalysisPage.vue'),
    meta: {
      title: '缠论分析',
      keepAlive: true,
    },
  },
  {
    path: '/stock-selection',
    name: 'StockSelection',
    component: () => import('@/views/StockSelectionPage.vue'),
    meta: {
      title: '智能选股',
      keepAlive: true,
    },
  },
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
})

// 路由守卫
router.beforeEach((to, from, next) => {
  // 设置页面标题
  if (to.meta?.title) {
    document.title = `${to.meta.title} - KK缠论量化分析平台`
  }
  next()
})

export default router