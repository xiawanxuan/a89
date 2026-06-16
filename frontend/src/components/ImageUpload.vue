<template>
  <div class="upload-zone" :class="{ 'drag-over': isDragOver }" @dragover.prevent="isDragOver = true" @dragleave="isDragOver = false" @drop.prevent="handleDrop" @click="triggerFileInput">
    <input ref="fileInput" type="file" accept="image/png,image/jpeg,image/bmp,image/tiff" style="display: none" @change="handleFileSelect" />
    <div class="upload-content">
      <svg class="upload-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
        <polyline points="17 8 12 3 7 8" />
        <line x1="12" y1="3" x2="12" y2="15" />
      </svg>
      <p class="upload-text">{{ isDragOver ? '释放以上传' : '点击或拖拽上传古彝文手稿图像' }}</p>
      <p class="upload-hint">支持 PNG / JPG / BMP / TIFF，最大 20MB</p>
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
    await store.uploadImage(input.files[0])
    input.value = ''
  }
}

async function handleDrop(event: DragEvent) {
  isDragOver.value = false
  if (event.dataTransfer?.files && event.dataTransfer.files[0]) {
    await store.uploadImage(event.dataTransfer.files[0])
  }
}
</script>

<style scoped>
.upload-zone {
  border: 2px dashed #4a5568;
  border-radius: 12px;
  padding: 40px 20px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
  background: rgba(45, 55, 72, 0.5);
  min-height: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
}
.upload-zone:hover,
.upload-zone.drag-over {
  border-color: #e53e3e;
  background: rgba(229, 62, 62, 0.1);
}
.upload-content {
  color: #a0aec0;
}
.upload-icon {
  width: 48px;
  height: 48px;
  margin-bottom: 12px;
  color: #e53e3e;
}
.upload-text {
  font-size: 16px;
  margin-bottom: 8px;
  color: #e2e8f0;
}
.upload-hint {
  font-size: 13px;
  color: #718096;
}
</style>
