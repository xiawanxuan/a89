<template>
  <div class="version-panel">
    <div class="panel-header">
      <h4>修复版本</h4>
      <span class="version-count">{{ versions.length }}/5</span>
    </div>
    <div class="version-list">
      <div
        v-for="version in sortedVersions"
        :key="version.id"
        class="version-item"
        :class="{
          'version-selected': version.is_selected === 1,
          'version-active': previewVersionId === version.id,
        }"
        @click="handlePreview(version)"
      >
        <div class="version-thumb">
          <img :src="version.repaired_path" :alt="`版本 ${version.version_number}`" />
          <div class="version-badge" :class="getScoreClass(version.quality_score)">
            {{ Math.round(version.quality_score) }}
          </div>
          <div v-if="version.is_selected === 1" class="selected-badge">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" width="14" height="14">
              <polyline points="20 6 9 17 4 12" />
            </svg>
          </div>
        </div>
        <div class="version-info">
          <div class="version-title">版本 {{ version.version_number }}</div>
          <div class="version-time">{{ formatTime(version.created_at) }}</div>
        </div>
        <button
          v-if="version.is_selected !== 1"
          class="btn-select"
          @click.stop="handleSelect(version)"
        >
          选用此版
        </button>
      </div>
    </div>
    <div class="version-actions">
      <button
        class="btn-retry"
        @click="$emit('retry')"
        :disabled="isProcessing"
      >
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
          <polyline points="1 4 1 10 7 10" />
          <path d="M3.51 15a9 9 0 1 0 2.13-9.36L1 10" />
        </svg>
        重新修复
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import type { RepairVersion } from '@/api'

const props = defineProps<{
  versions: RepairVersion[]
  isProcessing?: boolean
}>()

const emit = defineEmits<{
  (e: 'select', version: RepairVersion): void
  (e: 'preview', version: RepairVersion): void
  (e: 'retry'): void
}>()

const previewVersionId = ref<string | null>(null)

const sortedVersions = computed(() => {
  return [...props.versions].sort((a, b) => b.version_number - a.version_number)
})

function handlePreview(version: RepairVersion) {
  previewVersionId.value = version.id
  emit('preview', version)
}

function handleSelect(version: RepairVersion) {
  emit('select', version)
}

function getScoreClass(score: number) {
  if (score >= 90) return 'score-excellent'
  if (score >= 70) return 'score-good'
  if (score >= 50) return 'score-fair'
  return 'score-poor'
}

function formatTime(dateStr: string) {
  const d = new Date(dateStr)
  return `${d.getMonth() + 1}/${d.getDate()} ${d.getHours().toString().padStart(2, '0')}:${d.getMinutes().toString().padStart(2, '0')}`
}
</script>

<style scoped>
.version-panel {
  background: #1a202c;
  border: 1px solid #4a5568;
  border-radius: 8px;
  overflow: hidden;
}
.panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 12px;
  background: #2d3748;
  border-bottom: 1px solid #4a5568;
}
.panel-header h4 {
  margin: 0;
  font-size: 13px;
  font-weight: 600;
  color: #e2e8f0;
}
.version-count {
  font-size: 11px;
  color: #a0aec0;
  background: rgba(113, 128, 150, 0.2);
  padding: 2px 8px;
  border-radius: 10px;
}
.version-list {
  max-height: 280px;
  overflow-y: auto;
}
.version-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  border-bottom: 1px solid #374151;
  cursor: pointer;
  transition: background 0.2s;
}
.version-item:hover {
  background: rgba(66, 153, 225, 0.1);
}
.version-item.version-selected {
  background: rgba(72, 187, 120, 0.15);
  border-left: 3px solid #48bb78;
}
.version-item.version-active {
  background: rgba(66, 153, 225, 0.2);
}
.version-thumb {
  position: relative;
  width: 56px;
  height: 56px;
  border-radius: 4px;
  overflow: hidden;
  flex-shrink: 0;
  background: #2d3748;
}
.version-thumb img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.version-badge {
  position: absolute;
  top: 2px;
  right: 2px;
  font-size: 10px;
  font-weight: 700;
  padding: 1px 5px;
  border-radius: 8px;
  color: white;
}
.version-badge.score-excellent { background: #48bb78; }
.version-badge.score-good { background: #4299e1; }
.version-badge.score-fair { background: #ed8936; }
.version-badge.score-poor { background: #fc8181; }
.selected-badge {
  position: absolute;
  bottom: 2px;
  left: 2px;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: #48bb78;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
}
.version-info {
  flex: 1;
  min-width: 0;
}
.version-title {
  font-size: 13px;
  font-weight: 600;
  color: #e2e8f0;
  margin-bottom: 2px;
}
.version-time {
  font-size: 11px;
  color: #718096;
}
.btn-select {
  padding: 6px 10px;
  font-size: 11px;
  font-weight: 600;
  border: none;
  border-radius: 4px;
  background: #4299e1;
  color: white;
  cursor: pointer;
  flex-shrink: 0;
  transition: background 0.2s;
}
.btn-select:hover {
  background: #3182ce;
}
.version-actions {
  padding: 10px 12px;
  border-top: 1px solid #4a5568;
}
.btn-retry {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 8px 12px;
  font-size: 13px;
  font-weight: 600;
  border: none;
  border-radius: 6px;
  background: linear-gradient(135deg, #e53e3e, #c53030);
  color: white;
  cursor: pointer;
  transition: all 0.2s;
}
.btn-retry:hover:not(:disabled) {
  background: linear-gradient(135deg, #c53030, #9b2c2c);
}
.btn-retry:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
.version-list::-webkit-scrollbar {
  width: 6px;
}
.version-list::-webkit-scrollbar-track {
  background: #2d3748;
}
.version-list::-webkit-scrollbar-thumb {
  background: #4a5568;
  border-radius: 3px;
}
</style>
