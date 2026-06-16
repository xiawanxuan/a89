<template>
  <div class="quality-score" :class="scoreClass">
    <div class="score-circle">
      <svg class="score-svg" viewBox="0 0 100 100">
        <circle cx="50" cy="50" r="42" fill="none" stroke="#4a5568" stroke-width="8" />
        <circle
          cx="50"
          cy="50"
          r="42"
          fill="none"
          :stroke="strokeColor"
          stroke-width="8"
          stroke-linecap="round"
          :stroke-dasharray="circumference"
          :stroke-dashoffset="strokeOffset"
          transform="rotate(-90 50 50)"
          class="score-progress"
        />
      </svg>
      <div class="score-value">
        <span class="score-number">{{ displayScore }}</span>
        <span class="score-label">分</span>
      </div>
    </div>
    <div class="score-info">
      <span class="score-title">字符完整度评分</span>
      <span class="score-desc">{{ scoreDesc }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  score: number
  size?: 'sm' | 'md' | 'lg'
}>()

const size = computed(() => props.size || 'md')
const displayScore = computed(() => Math.round(props.score))

const circumference = 2 * Math.PI * 42
const strokeOffset = computed(() => {
  const progress = Math.max(0, Math.min(100, props.score)) / 100
  return circumference * (1 - progress)
})

const strokeColor = computed(() => {
  const s = props.score
  if (s >= 90) return '#48bb78'
  if (s >= 70) return '#4299e1'
  if (s >= 50) return '#ed8936'
  return '#fc8181'
})

const scoreClass = computed(() => {
  const s = props.score
  if (s >= 90) return 'score-excellent'
  if (s >= 70) return 'score-good'
  if (s >= 50) return 'score-fair'
  return 'score-poor'
})

const scoreDesc = computed(() => {
  const s = props.score
  if (s >= 90) return '优秀，字符清晰完整'
  if (s >= 70) return '良好，可正常识别'
  if (s >= 50) return '一般，部分笔画模糊'
  return '较差，建议重新修复'
})
</script>

<style scoped>
.quality-score {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  border-radius: 8px;
  background: rgba(45, 55, 72, 0.5);
  border: 1px solid #4a5568;
}
.score-circle {
  position: relative;
  width: 64px;
  height: 64px;
  flex-shrink: 0;
}
.score-svg {
  width: 100%;
  height: 100%;
}
.score-progress {
  transition: stroke-dashoffset 0.8s ease-out, stroke 0.3s;
}
.score-value {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}
.score-number {
  font-size: 20px;
  font-weight: 700;
  color: #e2e8f0;
  line-height: 1;
}
.score-label {
  font-size: 10px;
  color: #a0aec0;
  margin-top: 2px;
}
.score-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.score-title {
  font-size: 13px;
  font-weight: 600;
  color: #e2e8f0;
}
.score-desc {
  font-size: 12px;
  color: #a0aec0;
}
.score-excellent { border-color: rgba(72, 187, 120, 0.4); }
.score-good { border-color: rgba(66, 153, 225, 0.4); }
.score-fair { border-color: rgba(237, 137, 54, 0.4); }
.score-poor { border-color: rgba(252, 129, 129, 0.4); }
</style>
