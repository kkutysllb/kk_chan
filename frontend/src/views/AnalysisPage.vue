<template>
  <div class="analysis-page">
    <!-- 这个页面可以用于单独的分析展示 -->
    <HomePage />
  </div>
</template>

<script setup>
import HomePage from './HomePage.vue'
</script>

<style scoped>
.analysis-page {
  min-height: calc(100vh - 80px);
}
</style>