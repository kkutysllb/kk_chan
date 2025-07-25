<template>
  <div class="analysis-view">
    <div class="analysis-header">
      <el-page-header @back="goBack">
        <template #content>
          <span class="page-title">缠论分析</span>
        </template>
      </el-page-header>
      
      <div class="symbol-selector">
        <el-input
          v-model="currentSymbol"
          placeholder="输入股票代码"
          style="width: 200px;"
          @keyup.enter="loadAnalysis"
        >
          <template #append>
            <el-button @click="loadAnalysis" :loading="loading">
              分析
            </el-button>
          </template>
        </el-input>
      </div>
    </div>
    
    <div class="analysis-content" v-if="currentSymbol">
      <el-row :gutter="20">
        <el-col :span="12">
          <ChanKLineChart :symbol="currentSymbol" />
        </el-col>
        <el-col :span="12">
          <MultiTimeframeAnalysis :symbol="currentSymbol" />
        </el-col>
      </el-row>
      
      <el-row :gutter="20" style="margin-top: 20px;">
        <el-col :span="12">
          <RealTimePrediction :symbol="currentSymbol" />
        </el-col>
        <el-col :span="12">
          <TradingSignals :symbol="currentSymbol" />
        </el-col>
      </el-row>
      
      <el-row style="margin-top: 20px;">
        <el-col :span="24">
          <ChanStructureDetail :symbol="currentSymbol" />
        </el-col>
      </el-row>
    </div>
    
    <div class="empty-state" v-else>
      <el-empty description="请选择股票进行分析">
        <el-button type="primary" @click="showSymbolDialog = true">选择股票</el-button>
      </el-empty>
    </div>
    
    <!-- 股票选择对话框 -->
    <el-dialog v-model="showSymbolDialog" title="选择股票" width="500px">
      <el-input
        v-model="dialogSymbol"
        placeholder="输入股票代码，如: 000001.SZ"
        @keyup.enter="confirmSymbol"
      />
      <template #footer>
        <el-button @click="showSymbolDialog = false">取消</el-button>
        <el-button type="primary" @click="confirmSymbol">确认</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import ChanKLineChart from '@/components/charts/ChanKLineChart.vue'
import ChanStructureDetail from '@/components/charts/ChanStructureDetail.vue'
import MultiTimeframeAnalysis from '@/components/analysis/MultiTimeframeAnalysis.vue'
import RealTimePrediction from '@/components/analysis/RealTimePrediction.vue'
import TradingSignals from '@/components/analysis/TradingSignals.vue'

const route = useRoute()
const router = useRouter()

const loading = ref(false)
const currentSymbol = ref('')
const showSymbolDialog = ref(false)
const dialogSymbol = ref('')

const goBack = () => {
  router.push('/')
}

const loadAnalysis = async () => {
  if (!currentSymbol.value.trim()) {
    ElMessage.warning('请输入股票代码')
    return
  }
  
  loading.value = true
  try {
    // 更新路由
    await router.push(`/analysis/${currentSymbol.value}`)
    ElMessage.success('分析开始')
  } catch (error) {
    console.error('分析失败:', error)
    ElMessage.error('分析失败，请重试')
  } finally {
    loading.value = false
  }
}

const confirmSymbol = () => {
  if (dialogSymbol.value.trim()) {
    currentSymbol.value = dialogSymbol.value.trim().toUpperCase()
    showSymbolDialog.value = false
    dialogSymbol.value = ''
    loadAnalysis()
  }
}

// 监听路由参数变化
watch(
  () => route.params.symbol,
  (newSymbol) => {
    if (newSymbol && typeof newSymbol === 'string') {
      currentSymbol.value = newSymbol
    }
  },
  { immediate: true }
)

onMounted(() => {
  const symbol = route.params.symbol
  if (symbol && typeof symbol === 'string') {
    currentSymbol.value = symbol
  }
})
</script>

<style scoped lang="scss">
.analysis-view {
  padding: 20px;
  
  .analysis-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 30px;
    
    .page-title {
      font-size: 20px;
      font-weight: 600;
      color: #303133;
    }
  }
  
  .analysis-content {
    min-height: 600px;
  }
  
  .empty-state {
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 400px;
  }
}

@media (max-width: 768px) {
  .analysis-view {
    padding: 10px;
    
    .analysis-header {
      flex-direction: column;
      gap: 15px;
      align-items: stretch;
    }
    
    .analysis-content {
      :deep(.el-col) {
        margin-bottom: 20px;
      }
    }
  }
}
</style>