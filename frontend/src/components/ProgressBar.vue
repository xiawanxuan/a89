<template>
  <div class="progress-bar-wrapper" v-if="store.batchTask">
    <div class="progress-header">
      <span class="progress-title">批量处理进度</span>
      <span class="progress-stats">
        {{ store.batchTask.completed_count }} / {{ store.batchTask.total_count }} 完成
        <span v-if="store.batchTask.failed_count > 0" class="failed-count">
          {{ store.batchTask.failed_count }} 失败
        </span>
      </span>
    </div>
    <div class="progress-track">
      <div class="progress-fill" :style="{ width: store.batchProgress + '%' }" :class="progressClass"></div>
    </div>
    <div class="progress-footer">
      <span class="progress-percent">{{ store.batchProgress }}%</span>
      <span class="progress-status" :class="'status-' + store.batchTask.status">
        {{ statusText }}
      </span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRepairStore } from '@/stores/repair'

const store = useRepairStore()

const progressClass = computed(() => {
  if (!store.batchTask) return ''
  if (store.batchTask.status === 'completed') return 'fill-success'
  if (store.batchTask.status === 'failed') return 'fill-error'
  if (store.batchTask.failed_count > 0) return 'fill-warning'
  return ''
})

const statusText = computed(() => {
  if (!store.batchTask) return ''
  const map: Record<string, string> = {
    pending: '等待中',
    processing: '处理中',
    completed: '已完成',
    failed: '失败',
  }
  return map[store.batchTask.status] || store.batchTask.status
})
</script>

<style scoped>
.progress-bar-wrapper {
  padding: 12px 16px;
  background: #2d3748;
  border-radius: 8px;
}
.progress-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}
.progress-title {
  font-size: 14px;
  font-weight: 600;
  color: #e2e8f0;
}
.progress-stats {
  font-size: 13px;
  color: #a0aec0;
}
.failed-count {
  color: #fc8181;
  margin-left: 8px;
}
.progress-track {
  height: 8px;
  background: #4a5568;
  border-radius: 4px;
  overflow: hidden;
}
.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #4299e1, #3182ce);
  border-radius: 4px;
  transition: width 0.5s ease;
}
.progress-fill.fill-success {
  background: linear-gradient(90deg, #48bb78, #38a169);
}
.progress-fill.fill-error {
  background: linear-gradient(90deg, #fc8181, #e53e3e);
}
.progress-fill.fill-warning {
  background: linear-gradient(90deg, #4299e1, #ed8936);
}
.progress-footer {
  display: flex;
  justify-content: space-between;
  margin-top: 6px;
  font-size: 12px;
}
.progress-percent {
  color: #a0aec0;
}
.progress-status {
  font-weight: 600;
}
.progress-status.status-pending { color: #a0aec0; }
.progress-status.status-processing { color: #4299e1; }
.progress-status.status-completed { color: #48bb78; }
.progress-status.status-failed { color: #fc8181; }
</style>
