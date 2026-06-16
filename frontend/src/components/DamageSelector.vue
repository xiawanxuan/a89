<template>
  <div class="damage-selector" ref="containerRef">
    <div class="canvas-wrapper">
      <canvas ref="canvasRef" @mousedown="onMouseDown" @mousemove="onMouseMove" @mouseup="onMouseUp" @mouseleave="onMouseUp"></canvas>
    </div>
    <div class="selector-toolbar">
      <button class="btn-tool" :class="{ active: mode === 'select' }" @click="mode = 'select'">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
          <rect x="3" y="3" width="18" height="18" rx="2" />
        </svg>
        框选破损区域
      </button>
      <button class="btn-tool" @click="detectAuto">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
          <circle cx="11" cy="11" r="8" /><line x1="21" y1="21" x2="16.65" y2="16.65" />
        </svg>
        AI自动检测
      </button>
      <button class="btn-tool btn-danger" @click="clearAll" v-if="regions.length > 0">清除所有</button>
    </div>
    <div class="regions-list" v-if="regions.length > 0">
      <div class="region-item" v-for="(r, i) in regions" :key="i">
        <span class="region-label">区域 {{ i + 1 }}</span>
        <span class="region-info">{{ r.width }}×{{ r.height }} @ ({{ r.x }}, {{ r.y }})</span>
        <button class="btn-remove" @click="removeRegion(i)">×</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted, nextTick } from 'vue'
import { useRepairStore } from '@/stores/repair'

const store = useRepairStore()
const containerRef = ref<HTMLDivElement>()
const canvasRef = ref<HTMLCanvasElement>()

const mode = ref<'select' | 'view'>('select')
const isDrawing = ref(false)
const startX = ref(0)
const startY = ref(0)
const currentRect = ref<{ x: number; y: number; w: number; h: number } | null>(null)

const regions = ref(store.selectedRegions)
const imageScale = ref(1)
const offsetX = ref(0)
const offsetY = ref(0)
const imgElement = ref<HTMLImageElement | null>(null)

watch(() => store.currentTask, () => {
  loadImage()
})

watch(() => store.selectedRegions, (val) => {
  regions.value = val
  redraw()
}, { deep: true })

onMounted(() => {
  if (store.currentTask) {
    loadImage()
  }
})

function loadImage() {
  if (!store.currentTask) return
  const img = new Image()
  img.crossOrigin = 'anonymous'
  img.onload = () => {
    imgElement.value = img
    fitCanvas()
    redraw()
  }
  img.src = store.currentTask.original_path
}

function fitCanvas() {
  if (!canvasRef.value || !containerRef.value || !imgElement.value) return
  const canvas = canvasRef.value
  const container = containerRef.value
  const maxW = container.clientWidth - 4
  const maxH = container.clientHeight - 4
  const imgW = imgElement.value.width
  const imgH = imgElement.value.height
  const scale = Math.min(maxW / imgW, maxH / imgH, 1)
  imageScale.value = scale
  canvas.width = imgW * scale
  canvas.height = imgH * scale
  offsetX.value = 0
  offsetY.value = 0
}

function redraw() {
  if (!canvasRef.value || !imgElement.value) return
  const ctx = canvasRef.value.getContext('2d')
  if (!ctx) return

  const scale = imageScale.value
  ctx.clearRect(0, 0, canvasRef.value.width, canvasRef.value.height)
  ctx.drawImage(imgElement.value, 0, 0, imgElement.value.width * scale, imgElement.value.height * scale)

  ctx.strokeStyle = '#e53e3e'
  ctx.lineWidth = 2
  ctx.setLineDash([6, 3])
  for (const r of regions.value) {
    ctx.strokeRect(r.x * scale, r.y * scale, r.width * scale, r.height * scale)
    ctx.fillStyle = 'rgba(229, 62, 62, 0.15)'
    ctx.fillRect(r.x * scale, r.y * scale, r.width * scale, r.height * scale)
  }

  if (currentRect.value) {
    ctx.strokeStyle = '#f6ad55'
    ctx.lineWidth = 2
    ctx.setLineDash([4, 4])
    ctx.strokeRect(currentRect.value.x, currentRect.value.y, currentRect.value.w, currentRect.value.h)
    ctx.fillStyle = 'rgba(246, 173, 85, 0.2)'
    ctx.fillRect(currentRect.value.x, currentRect.value.y, currentRect.value.w, currentRect.value.h)
  }
  ctx.setLineDash([])
}

function getCanvasPos(e: MouseEvent) {
  const rect = canvasRef.value!.getBoundingClientRect()
  return { x: e.clientX - rect.left, y: e.clientY - rect.top }
}

function onMouseDown(e: MouseEvent) {
  if (mode.value !== 'select') return
  const pos = getCanvasPos(e)
  isDrawing.value = true
  startX.value = pos.x
  startY.value = pos.y
  currentRect.value = { x: pos.x, y: pos.y, w: 0, h: 0 }
}

function onMouseMove(e: MouseEvent) {
  if (!isDrawing.value) return
  const pos = getCanvasPos(e)
  currentRect.value = {
    x: Math.min(startX.value, pos.x),
    y: Math.min(startY.value, pos.y),
    w: Math.abs(pos.x - startX.value),
    h: Math.abs(pos.y - startY.value),
  }
  redraw()
}

function onMouseUp() {
  if (!isDrawing.value) return
  isDrawing.value = false
  if (currentRect.value && currentRect.value.w > 5 && currentRect.value.h > 5) {
    const scale = imageScale.value
    store.addRegion({
      x: Math.round(currentRect.value.x / scale),
      y: Math.round(currentRect.value.y / scale),
      width: Math.round(currentRect.value.w / scale),
      height: Math.round(currentRect.value.h / scale),
    })
  }
  currentRect.value = null
  redraw()
}

function removeRegion(index: number) {
  store.removeRegion(index)
  redraw()
}

function clearAll() {
  store.clearRegions()
  redraw()
}

async function detectAuto() {
  await store.detectDamageRegions()
  nextTick(() => redraw())
}

defineExpose({ loadImage, redraw })
</script>

<style scoped>
.damage-selector {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: #1a202c;
  border-radius: 8px;
  overflow: hidden;
}
.canvas-wrapper {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 8px;
  overflow: hidden;
  min-height: 300px;
}
.canvas-wrapper canvas {
  cursor: crosshair;
  max-width: 100%;
  max-height: 100%;
}
.selector-toolbar {
  display: flex;
  gap: 8px;
  padding: 8px 12px;
  background: #2d3748;
  border-top: 1px solid #4a5568;
}
.btn-tool {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 6px 12px;
  border: 1px solid #4a5568;
  border-radius: 6px;
  background: #1a202c;
  color: #e2e8f0;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
}
.btn-tool:hover {
  background: #4a5568;
}
.btn-tool.active {
  border-color: #e53e3e;
  background: rgba(229, 62, 62, 0.2);
}
.btn-tool.btn-danger {
  color: #fc8181;
  border-color: #e53e3e;
}
.btn-tool.btn-danger:hover {
  background: rgba(229, 62, 62, 0.3);
}
.regions-list {
  max-height: 150px;
  overflow-y: auto;
  padding: 8px 12px;
  background: #2d3748;
  border-top: 1px solid #4a5568;
}
.region-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 4px 0;
  font-size: 13px;
  color: #e2e8f0;
}
.region-label {
  color: #f6ad55;
  font-weight: 600;
  min-width: 50px;
}
.region-info {
  color: #a0aec0;
  flex: 1;
}
.btn-remove {
  width: 20px;
  height: 20px;
  border: none;
  border-radius: 50%;
  background: rgba(229, 62, 62, 0.3);
  color: #fc8181;
  cursor: pointer;
  font-size: 14px;
  line-height: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}
.btn-remove:hover {
  background: #e53e3e;
  color: white;
}
</style>
