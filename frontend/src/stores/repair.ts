import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { RepairTask, BatchTask, DamageRegion, DamageRegionOut } from '@/api'
import * as api from '@/api'

export const useRepairStore = defineStore('repair', () => {
  const currentTask = ref<RepairTask | null>(null)
  const selectedRegions = ref<DamageRegion[]>([])
  const detectedRegions = ref<DamageRegionOut[]>([])
  const batchTask = ref<BatchTask | null>(null)
  const historyList = ref<RepairTask[]>([])
  const batchList = ref<BatchTask[]>([])
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  const isTaskCompleted = computed(() => currentTask.value?.status === 'completed')
  const batchProgress = computed(() => {
    if (!batchTask.value) return 0
    const { completed_count, failed_count, total_count } = batchTask.value
    return total_count > 0 ? Math.round(((completed_count + failed_count) / total_count) * 100) : 0
  })

  async function uploadImage(file: File) {
    isLoading.value = true
    error.value = null
    try {
      const result = await api.uploadSingleImage(file)
      currentTask.value = {
        id: result.task_id,
        filename: result.filename,
        original_path: result.original_path,
        repaired_path: null,
        status: 'pending',
        created_at: new Date().toISOString(),
        completed_at: null,
        regions: [],
      }
      selectedRegions.value = []
      detectedRegions.value = []
    } catch (e: any) {
      error.value = e.response?.data?.detail || '上传失败'
    } finally {
      isLoading.value = false
    }
  }

  async function detectDamageRegions() {
    if (!currentTask.value) return
    isLoading.value = true
    try {
      const regions = await api.detectDamage(currentTask.value.id)
      detectedRegions.value = regions
      selectedRegions.value = regions.map(r => ({ x: r.x, y: r.y, width: r.width, height: r.height }))
    } catch (e: any) {
      error.value = e.response?.data?.detail || '检测失败'
    } finally {
      isLoading.value = false
    }
  }

  async function startRepair() {
    if (!currentTask.value || selectedRegions.value.length === 0) return
    isLoading.value = true
    try {
      await api.startRepair(currentTask.value.id, selectedRegions.value)
      currentTask.value.status = 'queued'
      pollRepairStatus()
    } catch (e: any) {
      error.value = e.response?.data?.detail || '启动修复失败'
    } finally {
      isLoading.value = false
    }
  }

  function pollRepairStatus() {
    if (!currentTask.value) return
    const interval = setInterval(async () => {
      try {
        const task = await api.getRepairStatus(currentTask.value!.id)
        currentTask.value = task
        if (task.status === 'completed' || task.status === 'failed') {
          clearInterval(interval)
        }
      } catch {
        clearInterval(interval)
      }
    }, 2000)
  }

  async function uploadBatch(file: File) {
    isLoading.value = true
    error.value = null
    try {
      const result = await api.uploadBatchZip(file)
      batchTask.value = {
        id: result.batch_id,
        total_count: result.total_count,
        completed_count: 0,
        failed_count: 0,
        status: 'pending',
        created_at: new Date().toISOString(),
        completed_at: null,
      }
      pollBatchStatus()
    } catch (e: any) {
      error.value = e.response?.data?.detail || '批量上传失败'
    } finally {
      isLoading.value = false
    }
  }

  function pollBatchStatus() {
    if (!batchTask.value) return
    const interval = setInterval(async () => {
      try {
        const batch = await api.getBatchStatus(batchTask.value!.id)
        batchTask.value = batch
        if (batch.status === 'completed' || batch.status === 'failed') {
          clearInterval(interval)
        }
      } catch {
        clearInterval(interval)
      }
    }, 3000)
  }

  async function loadHistory(skip = 0, limit = 20) {
    isLoading.value = true
    try {
      historyList.value = await api.listHistory(skip, limit)
    } catch (e: any) {
      error.value = e.response?.data?.detail || '加载历史失败'
    } finally {
      isLoading.value = false
    }
  }

  async function loadBatchList() {
    try {
      batchList.value = await api.listBatchTasks()
    } catch {
      // silent
    }
  }

  function addRegion(region: DamageRegion) {
    selectedRegions.value.push(region)
  }

  function removeRegion(index: number) {
    selectedRegions.value.splice(index, 1)
  }

  function clearRegions() {
    selectedRegions.value = []
    detectedRegions.value = []
  }

  function resetCurrent() {
    currentTask.value = null
    selectedRegions.value = []
    detectedRegions.value = []
    error.value = null
  }

  return {
    currentTask,
    selectedRegions,
    detectedRegions,
    batchTask,
    historyList,
    batchList,
    isLoading,
    error,
    isTaskCompleted,
    batchProgress,
    uploadImage,
    detectDamageRegions,
    startRepair,
    uploadBatch,
    loadHistory,
    loadBatchList,
    addRegion,
    removeRegion,
    clearRegions,
    resetCurrent,
  }
})
