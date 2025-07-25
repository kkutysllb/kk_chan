import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import { createPinia } from 'pinia'

// Element Plus
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import zhCn from 'element-plus/es/locale/lang/zh-cn'

// ECharts
import ECharts from 'vue-echarts'
import { use } from 'echarts/core'
import {
  CanvasRenderer,
  SVGRenderer
} from 'echarts/renderers'
import {
  LineChart,
  BarChart,
  CandlestickChart,
  ScatterChart,
  HeatmapChart,
  TreemapChart
} from 'echarts/charts'
import {
  GridComponent,
  LegendComponent,
  TitleComponent,
  ToolboxComponent,
  TooltipComponent,
  DataZoomComponent,
  MarkLineComponent,
  MarkPointComponent,
  BrushComponent
} from 'echarts/components'

// 注册ECharts组件
use([
  CanvasRenderer,
  SVGRenderer,
  LineChart,
  BarChart,
  CandlestickChart,
  ScatterChart,
  HeatmapChart,
  TreemapChart,
  GridComponent,
  LegendComponent,
  TitleComponent,
  ToolboxComponent,
  TooltipComponent,
  DataZoomComponent,
  MarkLineComponent,
  MarkPointComponent,
  BrushComponent
])

// 样式
import './styles/index.scss'

const app = createApp(App)

// 注册Element Plus图标
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

// 使用插件
app.use(createPinia())
app.use(router)
app.use(ElementPlus, {
  locale: zhCn
})

// 注册ECharts组件
app.component('VChart', ECharts)

app.mount('#app')