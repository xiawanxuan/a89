<template>
  <div class="compare-slider" ref="containerRef">
    <div class="compare-images">
      <div class="image-layer image-original">
        <img :src="originalSrc" alt="原始图像" @load="onImageLoad" />
        <div class="image-label">原始图像</div>
      </div>
      <div class="image-layer image-repaired" :style="{ clipPath: clipPathRepaired }">
        <img :src="repairedSrc" alt="修复图像" />
        <div class="image-label">修复结果</div>
      </div>
      <div class="slider-line" :style="{ left: sliderPos + '%' }">
        <div class="slider-handle" @mousedown="startDrag" @touchstart="startDragTouch">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2">
            <polyline points="15 18 9 12 15 6" />
          </svg>
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2">
            <polyline points="9 18 15 12 9 6" />
          </svg>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

const props = defineProps<{
  originalSrc: string
  repairedSrc: string
}>()

const containerRef = ref<HTMLDivElement>()
const sliderPos = ref(50)
const isDragging = ref(false)

const clipPathRepaired = computed(() => {
  return `inset(0 ${100 - sliderPos.value}% 0 0)`
})

function onImageLoad() {
  // image loaded
}

function startDrag(e: MouseEvent) {
  isDragging.value = true
  const moveHandler = (ev: MouseEvent) => {
    updatePosition(ev.clientX)
  }
  const upHandler = () => {
    isDragging.value = false
    document.removeEventListener('mousemove', moveHandler)
    document.removeEventListener('mouseup', upHandler)
  }
  document.addEventListener('mousemove', moveHandler)
  document.addEventListener('mouseup', upHandler)
}

function startDragTouch(e: TouchEvent) {
  isDragging.value = true
  const moveHandler = (ev: TouchEvent) => {
    updatePosition(ev.touches[0].clientX)
  }
  const upHandler = () => {
    isDragging.value = false
    document.removeEventListener('touchmove', moveHandler)
    document.removeEventListener('touchend', upHandler)
  }
  document.addEventListener('touchmove', moveHandler)
  document.addEventListener('touchend', upHandler)
}

function updatePosition(clientX: number) {
  if (!containerRef.value) return
  const rect = containerRef.value.getBoundingClientRect()
  const pos = ((clientX - rect.left) / rect.width) * 100
  sliderPos.value = Math.max(5, Math.min(95, pos))
}
</script>

<style scoped>
.compare-slider {
  width: 100%;
  height: 100%;
  position: relative;
  overflow: hidden;
  border-radius: 8px;
  background: #1a202c;
}
.compare-images {
  position: relative;
  width: 100%;
  height: 100%;
}
.image-layer {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
}
.image-layer img {
  width: 100%;
  height: 100%;
  object-fit: contain;
}
.image-repaired {
  clip-path: inset(0 50% 0 0);
}
.image-label {
  position: absolute;
  bottom: 12px;
  padding: 4px 12px;
  background: rgba(0, 0, 0, 0.7);
  color: white;
  font-size: 13px;
  border-radius: 4px;
}
.image-original .image-label {
  right: 12px;
}
.image-repaired .image-label {
  left: 12px;
}
.slider-line {
  position: absolute;
  top: 0;
  bottom: 0;
  width: 3px;
  background: white;
  transform: translateX(-50%);
  z-index: 10;
  box-shadow: 0 0 8px rgba(0, 0, 0, 0.5);
}
.slider-handle {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 2px;
  cursor: ew-resize;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.5);
}
.slider-handle:hover {
  background: rgba(229, 62, 62, 0.8);
}
</style>
