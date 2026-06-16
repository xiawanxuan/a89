import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
})

export interface DamageRegion {
  x: number
  y: number
  width: number
  height: number
}

export interface RepairTask {
  id: string
  filename: string
  original_path: string
  repaired_path: string | null
  quality_score: number | null
  selected_version_id: string | null
  status: string
  created_at: string
  completed_at: string | null
  regions: DamageRegionOut[]
  versions: RepairVersion[]
}

export interface DamageRegionOut {
  id: string
  x: number
  y: number
  width: number
  height: number
  repaired_path: string | null
}

export interface RepairVersion {
  id: string
  task_id: string
  version_number: number
  repaired_path: string
  quality_score: number
  created_at: string
  is_selected: number
}

export interface BatchTask {
  id: string
  total_count: number
  completed_count: number
  failed_count: number
  status: string
  created_at: string
  completed_at: string | null
  items?: BatchItem[]
}

export interface BatchItem {
  id: string
  batch_id: string
  task_id: string | null
  filename: string
  status: string
}

export interface UploadResponse {
  task_id: string
  filename: string
  original_path: string
}

export async function uploadSingleImage(file: File): Promise<UploadResponse> {
  const formData = new FormData()
  formData.append('file', file)
  const { data } = await api.post('/upload/single', formData)
  return data
}

export async function uploadBatchZip(file: File): Promise<{ batch_id: string; total_count: number }> {
  const formData = new FormData()
  formData.append('file', file)
  const { data } = await api.post('/upload/batch', formData)
  return data
}

export async function startRepair(taskId: string, regions: DamageRegion[]): Promise<any> {
  const { data } = await api.post('/repair/start', { task_id: taskId, regions })
  return data
}

export async function detectDamage(taskId: string): Promise<DamageRegionOut[]> {
  const { data } = await api.post(`/repair/detect/${taskId}`)
  return data
}

export async function getRepairStatus(taskId: string): Promise<RepairTask> {
  const { data } = await api.get(`/repair/status/${taskId}`)
  return data
}

export async function retryRepair(taskId: string): Promise<any> {
  const { data } = await api.post(`/repair/retry/${taskId}`)
  return data
}

export async function listVersions(taskId: string): Promise<RepairVersion[]> {
  const { data } = await api.get(`/repair/versions/${taskId}`)
  return data
}

export async function selectVersion(taskId: string, versionId: string): Promise<any> {
  const { data } = await api.post('/repair/select-version', { task_id: taskId, version_id: versionId })
  return data
}

export async function getBatchStatus(batchId: string): Promise<BatchTask> {
  const { data } = await api.get(`/batch/status/${batchId}`)
  return data
}

export async function listBatchTasks(skip = 0, limit = 20): Promise<BatchTask[]> {
  const { data } = await api.get('/batch/list', { params: { skip, limit } })
  return data
}

export async function listHistory(skip = 0, limit = 20, status?: string): Promise<RepairTask[]> {
  const { data } = await api.get('/history/list', { params: { skip, limit, status } })
  return data
}

export async function getHistoryDetail(taskId: string): Promise<RepairTask> {
  const { data } = await api.get(`/history/detail/${taskId}`)
  return data
}

export async function deleteHistory(taskId: string): Promise<void> {
  await api.delete(`/history/${taskId}`)
}
