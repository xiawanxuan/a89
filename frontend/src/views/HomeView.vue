<template>
  <div class="home-view">
    <template v-if="activeTab === 'upload'">
      <div class="main-layout">
        <div class="left-panel">
          <ImageUpload v-if="!store.currentTask" />
          <DamageSelector v-else ref="selectorRef" />
        </div>
        <div class="right-panel">
          <RepairPreview />
        </div>
      </div>
    </template>

    <template v-if="activeTab === 'batch'">
      <div class="batch-layout">
        <BatchUpload />
        <div class="batch-progress-section" style="margin-top: 16px;">
          <ProgressBar />
        </div>
        <div class="batch-results" v-if="store.batchTask && store.batchTask.items">
          <h4>处理结果</h4>
          <div class="batch-item" v-for="item in store.batchTask.items" :key="item.id">
            <span class="batch-item-name">{{ item.filename }}</span>
            <span class="batch-item-status" :class="'status-' + item.status">
              {{ batchStatusMap[item.status] || item.status }}
            </span>
          </div>
        </div>
      </div>
    </template>

    <template v-if="activeTab === 'history'">
      <div class="history-layout">
        <HistoryList />
      </div>
    </template>

    <div class="bottom-bar" v-if="store.batchTask && store.batchTask.status === 'processing'">
      <ProgressBar />
    </div>

    <div class="error-toast" v-if="store.error" @click="store.error = null">
      {{ store.error }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRepairStore } from '@/stores/repair'
import ImageUpload from '@/components/ImageUpload.vue'
import DamageSelector from '@/components/DamageSelector.vue'
import RepairPreview from '@/components/RepairPreview.vue'
import BatchUpload from '@/components/BatchUpload.vue'
import ProgressBar from '@/components/ProgressBar.vue'
import HistoryList from '@/components/HistoryList.vue'

const store = useRepairStore()
const selectorRef = ref()

const props = defineProps<{
  activeTab: string
}>()

const batchStatusMap: Record<string, string> = {
  pending: '等待中',
  processing: '处理中',
  completed: '已完成',
  failed: '失败',
  skipped: '已跳过',
}
</script>

<style scoped>
.home-view {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}
.main-layout {
  flex: 1;
  display: flex;
  gap: 16px;
  padding: 16px;
  overflow: hidden;
}
.left-panel {
  flex: 3;
  min-width: 0;
  display: flex;
  flex-direction: column;
}
.right-panel {
  flex: 2;
  min-width: 300px;
  display: flex;
  flex-direction: column;
}
.batch-layout {
  flex: 1;
  padding: 24px;
  max-width: 700px;
  margin: 0 auto;
  width: 100%;
}
.batch-results {
  margin-top: 20px;
  background: #2d3748;
  border-radius: 8px;
  padding: 16px;
}
.batch-results h4 {
  margin: 0 0 12px;
  color: #e2e8f0;
  font-size: 15px;
}
.batch-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid rgba(74, 85, 104, 0.3);
  font-size: 13px;
}
.batch-item-name {
  color: #e2e8f0;
}
.batch-item-status {
  font-weight: 600;
  font-size: 12px;
}
.batch-item-status.status-pending { color: #a0aec0; }
.batch-item-status.status-processing { color: #4299e1; }
.batch-item-status.status-completed { color: #48bb78; }
.batch-item-status.status-failed { color: #fc8181; }
.batch-item-status.status-skipped { color: #718096; }
.history-layout {
  flex: 1;
  padding: 16px;
  overflow: hidden;
}
.bottom-bar {
  padding: 12px 16px;
  background: #2d3748;
  border-top: 1px solid #4a5568;
}
.error-toast {
  position: fixed;
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%);
  padding: 10px 24px;
  background: #e53e3e;
  color: white;
  border-radius: 8px;
  font-size: 14px;
  cursor: pointer;
  z-index: 1000;
  box-shadow: 0 4px 12px rgba(229, 62, 62, 0.4);
}
</style>
