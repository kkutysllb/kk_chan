import { createApp } from 'vue'
import { createPinia } from 'pinia'
import router from './router'
import App from './App.vue'

// Element Plus 样式和中文语言包
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import 'element-plus/theme-chalk/dark/css-vars.css'
import zhCn from 'element-plus/es/locale/lang/zh-cn'

// 自定义样式
import './styles/index.css'
import './styles/themes.css'

// ECharts注册
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { LineChart, CandlestickChart, ScatterChart, BarChart } from 'echarts/charts'
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
  DataZoomComponent,
  MarkPointComponent,
  MarkLineComponent,
  ToolboxComponent,
} from 'echarts/components'

// 注册必要的ECharts组件
use([
  CanvasRenderer,
  LineChart,
  CandlestickChart,
  ScatterChart,
  BarChart,
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
  DataZoomComponent,
  MarkPointComponent,
  MarkLineComponent,
  ToolboxComponent,
])

const app = createApp(App)
const pinia = createPinia()

// 配置Element Plus中文
app.use(ElementPlus, {
  locale: zhCn,
})

app.use(pinia)
app.use(router)

// 全局错误处理
app.config.errorHandler = (err, vm, info) => {
  console.error('全局错误:', err, info)
}

app.mount('#app')