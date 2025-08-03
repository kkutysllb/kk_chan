<template>
  <div class="loading-spinner" :class="{ fullscreen }">
    <div class="spinner-container">
      <div class="spinner-ring">
        <div></div>
        <div></div>
        <div></div>
        <div></div>
      </div>
      <div class="loading-text" v-if="text">
        {{ text }}
      </div>
      <div class="loading-dots" v-if="showDots">
        <span></span>
        <span></span>
        <span></span>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  text: {
    type: String,
    default: ''
  },
  fullscreen: {
    type: Boolean,
    default: false
  },
  showDots: {
    type: Boolean,
    default: true
  }
})
</script>

<style scoped>
.loading-spinner {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--space-xl);
}

.loading-spinner.fullscreen {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 9999;
  background: var(--bg-overlay);
  backdrop-filter: var(--backdrop-blur);
}

.spinner-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-lg);
}

.spinner-ring {
  display: inline-block;
  position: relative;
  width: 64px;
  height: 64px;
}

.spinner-ring div {
  box-sizing: border-box;
  display: block;
  position: absolute;
  width: 51px;
  height: 51px;
  margin: 6px;
  border: 6px solid var(--color-primary);
  border-radius: 50%;
  animation: spinner-ring 1.2s cubic-bezier(0.5, 0, 0.5, 1) infinite;
  border-color: var(--color-primary) transparent transparent transparent;
}

.spinner-ring div:nth-child(1) {
  animation-delay: -0.45s;
}

.spinner-ring div:nth-child(2) {
  animation-delay: -0.3s;
}

.spinner-ring div:nth-child(3) {
  animation-delay: -0.15s;
}

@keyframes spinner-ring {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}

.loading-text {
  font-size: 1rem;
  font-weight: 600;
  color: var(--text-primary);
  text-align: center;
  margin-top: var(--space-md);
}

.loading-dots {
  display: flex;
  gap: var(--space-xs);
  align-items: center;
}

.loading-dots span {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background-color: var(--color-primary);
  animation: loading-dots 1.4s ease-in-out infinite both;
}

.loading-dots span:nth-child(1) {
  animation-delay: -0.32s;
}

.loading-dots span:nth-child(2) {
  animation-delay: -0.16s;
}

@keyframes loading-dots {
  0%, 80%, 100% {
    transform: scale(0);
    opacity: 0.5;
  }
  40% {
    transform: scale(1);
    opacity: 1;
  }
}

/* 脉冲效果 */
.spinner-ring::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: var(--color-primary-light);
  animation: pulse 2s ease-in-out infinite;
  z-index: -1;
}

@keyframes pulse {
  0% {
    transform: translate(-50%, -50%) scale(0.8);
    opacity: 1;
  }
  100% {
    transform: translate(-50%, -50%) scale(1.2);
    opacity: 0;
  }
}
</style> 