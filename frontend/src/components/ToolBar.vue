<template>
  <div class="toolbar">
    <div class="toolbar-brand">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="24" height="24">
        <path d="M12 2L2 7l10 5 10-5-10-5z" /><path d="M2 17l10 5 10-5" /><path d="M2 12l10 5 10-5" />
      </svg>
      <span class="brand-text">古彝文手稿修复系统</span>
    </div>
    <div class="toolbar-actions">
      <button class="toolbar-btn" :class="{ active: activeTab === 'upload' }" @click="setTab('upload')">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18">
          <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" /><polyline points="17 8 12 3 7 8" /><line x1="12" y1="3" x2="12" y2="15" />
        </svg>
        上传修复
      </button>
      <button class="toolbar-btn" :class="{ active: activeTab === 'batch' }" @click="setTab('batch')">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18">
          <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" /><polyline points="14 2 14 8 20 8" />
        </svg>
        批量上传
      </button>
      <button class="toolbar-btn" :class="{ active: activeTab === 'history' }" @click="setTab('history')">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18">
          <circle cx="12" cy="12" r="10" /><polyline points="12 6 12 12 16 14" />
        </svg>
        历史记录
      </button>
    </div>
    <div class="toolbar-info">
      <span class="gpu-badge" v-if="gpuAvailable">GPU</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const props = defineProps<{
  activeTab: string
}>()

const emit = defineEmits<{
  (e: 'update:activeTab', value: string): void
}>()

const gpuAvailable = ref(true)

function setTab(tab: string) {
  emit('update:activeTab', tab)
}
</script>

<style scoped>
.toolbar {
  display: flex;
  align-items: center;
  height: 56px;
  padding: 0 20px;
  background: linear-gradient(135deg, #1a1a2e, #16213e);
  border-bottom: 1px solid rgba(229, 62, 62, 0.3);
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
}
.toolbar-brand {
  display: flex;
  align-items: center;
  gap: 10px;
  color: #e53e3e;
  flex-shrink: 0;
}
.brand-text {
  font-size: 18px;
  font-weight: 700;
  letter-spacing: 1px;
  background: linear-gradient(135deg, #e53e3e, #f6ad55);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}
.toolbar-actions {
  display: flex;
  gap: 4px;
  margin-left: 40px;
}
.toolbar-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  border: none;
  border-radius: 6px;
  background: transparent;
  color: #a0aec0;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
}
.toolbar-btn:hover {
  background: rgba(255, 255, 255, 0.08);
  color: #e2e8f0;
}
.toolbar-btn.active {
  background: rgba(229, 62, 62, 0.2);
  color: #fc8181;
}
.toolbar-info {
  margin-left: auto;
  display: flex;
  align-items: center;
  gap: 8px;
}
.gpu-badge {
  padding: 2px 8px;
  border-radius: 4px;
  background: rgba(72, 187, 120, 0.2);
  color: #48bb78;
  font-size: 11px;
  font-weight: 700;
}
</style>
