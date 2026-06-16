<template>
  <div class="batch-upload">
    <div class="batch-zone" :class="{ 'drag-over': isDragOver }" @dragover.prevent="isDragOver = true" @dragleave="isDragOver = false" @drop.prevent="handleDrop" @click="triggerFileInput">
      <input ref="fileInput" type="file" accept=".zip,application/zip,application/x-zip-compressed" style="display: none" @change="handleFileSelect" />
      <div class="batch-content">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="36" height="36">
          <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
          <polyline points="14 2 14 8 20 8" />
          <line x1="12" y1="18" x2="12" y2="12" />
          <line x1="9" y1="15" x2="15" y2="15" />
        </svg>
        <p class="batch-text">{{ isDragOver ? '释放以上传' : '上传ZIP压缩包（最多50张图像）' }}</p>
        <p class="batch-hint">支持 PNG / JPG / BMP / TIFF 图像，打包为ZIP格式</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRepairStore } from '@/stores/repair'

const store = useRepairStore()
const isDragOver = ref(false)
const fileInput = ref<HTMLInputElement>()

function triggerFileInput() {
  fileInput.value?.click()
}

async function handleFileSelect(event: Event) {
  const input = event.target as HTMLInputElement
  if (input.files && input.files[0]) {
    await store.uploadBatch(input.files[0])
    input.value = ''
  }
}

async function handleDrop(event: DragEvent) {
  isDragOver.value = false
  if (event.dataTransfer?.files && event.dataTransfer.files[0]) {
    await store.uploadBatch(event.dataTransfer.files[0])
  }
}
</script>

<style scoped>
.batch-upload {
  width: 100%;
}
.batch-zone {
  border: 2px dashed #4a5568;
  border-radius: 8px;
  padding: 24px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s;
  background: rgba(45, 55, 72, 0.3);
}
.batch-zone:hover,
.batch-zone.drag-over {
  border-color: #ed8936;
  background: rgba(237, 137, 54, 0.1);
}
.batch-content {
  color: #a0aec0;
}
.batch-text {
  font-size: 15px;
  margin: 8px 0 4px;
  color: #e2e8f0;
}
.batch-hint {
  font-size: 12px;
  color: #718096;
  margin: 0;
}
</style>
