<template>
  <div class="repair-preview">
    <div class="preview-header">
      <h3>修复结果预览</h3>
      <span class="status-badge" :class="statusClass">{{ statusText }}</span>
    </div>
    <div class="preview-content" v-if="store.currentTask">
      <template v-if="store.isTaskCompleted">
        <CompareSlider
          :original-src="store.currentTask.original_path"
          :repaired-src="store.currentTask.repaired_path!"
        />
      </template>
      <template v-else-if="store.currentTask.status === 'processing' || store.currentTask.status === 'queued'">
        <div class="loading-state">
          <div class="spinner"></div>
          <p>正在修复中，请稍候...</p>
        </div>
      </template>
      <template v-else-if="store.currentTask.status === 'failed'">
        <div class="error-state">
          <svg viewBox="0 0 24 24" fill="none" stroke="#fc8181" stroke-width="2" width="48" height="48">
            <circle cx="12" cy="12" r="10" /><line x1="15" y1="9" x2="9" y2="15" /><line x1="9" y1="9" x2="15" y2="15" />
          </svg>
          <p>修复失败，请重试</p>
        </div>
      </template>
      <template v-else>
        <div class="empty-state">
          <svg viewBox="0 0 24 24" fill="none" stroke="#718096" stroke-width="2" width="48" height="48">
            <rect x="3" y="3" width="18" height="18" rx="2" /><circle cx="8.5" cy="8.5" r="1.5" /><polyline points="21 15 16 10 5 21" />
          </svg>
          <p>框选破损区域后点击「开始修复」</p>
        </div>
      </template>
    </div>
    <div class="preview-empty" v-else>
      <svg viewBox="0 0 24 24" fill="none" stroke="#4a5568" stroke-width="2" width="64" height="64">
        <rect x="3" y="3" width="18" height="18" rx="2" /><circle cx="8.5" cy="8.5" r="1.5" /><polyline points="21 15 16 10 5 21" />
      </svg>
      <p>请先上传古彝文手稿图像</p>
    </div>
    <div class="preview-actions" v-if="store.currentTask && store.selectedRegions.length > 0 && store.currentTask.status === 'pending'">
      <button class="btn-repair" @click="store.startRepair()" :disabled="store.isLoading">
        {{ store.isLoading ? '提交中...' : '开始修复' }}
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRepairStore } from '@/stores/repair'
import CompareSlider from './CompareSlider.vue'

const store = useRepairStore()

const statusText = computed(() => {
  if (!store.currentTask) return ''
  const map: Record<string, string> = {
    pending: '待修复',
    queued: '排队中',
    processing: '修复中',
    completed: '已完成',
    failed: '失败',
  }
  return map[store.currentTask.status] || store.currentTask.status
})

const statusClass = computed(() => {
  if (!store.currentTask) return ''
  return `status-${store.currentTask.status}`
})
</script>

<style scoped>
.repair-preview {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: #1a202c;
  border-radius: 8px;
  overflow: hidden;
}
.preview-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  background: #2d3748;
  border-bottom: 1px solid #4a5568;
}
.preview-header h3 {
  margin: 0;
  font-size: 15px;
  color: #e2e8f0;
  font-weight: 600;
}
.status-badge {
  padding: 2px 10px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
}
.status-badge.status-pending { background: rgba(113, 128, 150, 0.3); color: #a0aec0; }
.status-badge.status-queued { background: rgba(237, 137, 54, 0.3); color: #ed8936; }
.status-badge.status-processing { background: rgba(66, 153, 225, 0.3); color: #4299e1; }
.status-badge.status-completed { background: rgba(72, 187, 120, 0.3); color: #48bb78; }
.status-badge.status-failed { background: rgba(229, 62, 62, 0.3); color: #fc8181; }
.preview-content {
  flex: 1;
  min-height: 300px;
  display: flex;
  align-items: center;
  justify-content: center;
}
.preview-empty {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #4a5568;
  gap: 12px;
}
.preview-empty p {
  font-size: 14px;
  color: #718096;
}
.loading-state,
.error-state,
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  color: #a0aec0;
}
.loading-state p,
.error-state p,
.empty-state p {
  font-size: 14px;
  margin: 0;
}
.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid #4a5568;
  border-top-color: #4299e1;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}
@keyframes spin {
  to { transform: rotate(360deg); }
}
.preview-actions {
  padding: 12px 16px;
  background: #2d3748;
  border-top: 1px solid #4a5568;
}
.btn-repair {
  width: 100%;
  padding: 10px;
  border: none;
  border-radius: 6px;
  background: linear-gradient(135deg, #e53e3e, #c53030);
  color: white;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}
.btn-repair:hover:not(:disabled) {
  background: linear-gradient(135deg, #c53030, #9b2c2c);
}
.btn-repair:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>
