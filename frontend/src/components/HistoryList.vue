<template>
  <div class="history-list">
    <div class="history-header">
      <h3>修复历史记录</h3>
      <button class="btn-refresh" @click="refresh">刷新</button>
    </div>
    <div class="history-items" v-if="store.historyList.length > 0">
      <div
        class="history-item"
        v-for="task in store.historyList"
        :key="task.id"
        @click="selectTask(task)"
      >
        <div class="item-thumb">
          <img :src="task.original_path" alt="" v-if="task.original_path" />
        </div>
        <div class="item-info">
          <div class="item-filename">{{ task.filename }}</div>
          <div class="item-meta">
            <span class="item-time">{{ formatTime(task.created_at) }}</span>
            <span class="item-regions">{{ task.regions?.length || 0 }} 个区域</span>
          </div>
        </div>
        <div class="item-status" :class="'status-' + task.status">
          {{ statusMap[task.status] || task.status }}
        </div>
        <div class="item-actions">
          <button class="btn-icon" @click.stop="deleteTask(task.id)" title="删除">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14">
              <polyline points="3 6 5 6 21 6" /><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" />
            </svg>
          </button>
        </div>
      </div>
    </div>
    <div class="history-empty" v-else>
      <p>暂无修复记录</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useRepairStore } from '@/stores/repair'
import type { RepairTask } from '@/api'
import { deleteHistory } from '@/api'

const store = useRepairStore()

const statusMap: Record<string, string> = {
  pending: '待修复',
  queued: '排队中',
  processing: '修复中',
  completed: '已完成',
  failed: '失败',
}

onMounted(() => {
  store.loadHistory()
})

function refresh() {
  store.loadHistory()
}

function selectTask(task: RepairTask) {
  store.currentTask = task
  store.selectedRegions = task.regions?.map(r => ({ x: r.x, y: r.y, width: r.width, height: r.height })) || []
}

async function deleteTask(taskId: string) {
  try {
    await deleteHistory(taskId)
    store.loadHistory()
  } catch {
    // silent
  }
}

function formatTime(iso: string): string {
  const d = new Date(iso)
  return d.toLocaleString('zh-CN', { month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' })
}
</script>

<style scoped>
.history-list {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: #1a202c;
  border-radius: 8px;
  overflow: hidden;
}
.history-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: #2d3748;
  border-bottom: 1px solid #4a5568;
}
.history-header h3 {
  margin: 0;
  font-size: 15px;
  color: #e2e8f0;
}
.btn-refresh {
  padding: 4px 12px;
  border: 1px solid #4a5568;
  border-radius: 4px;
  background: transparent;
  color: #a0aec0;
  font-size: 12px;
  cursor: pointer;
}
.btn-refresh:hover {
  background: #4a5568;
  color: #e2e8f0;
}
.history-items {
  flex: 1;
  overflow-y: auto;
}
.history-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 16px;
  border-bottom: 1px solid rgba(74, 85, 104, 0.3);
  cursor: pointer;
  transition: background 0.2s;
}
.history-item:hover {
  background: rgba(74, 85, 104, 0.3);
}
.item-thumb {
  width: 48px;
  height: 48px;
  border-radius: 4px;
  overflow: hidden;
  background: #2d3748;
  flex-shrink: 0;
}
.item-thumb img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.item-info {
  flex: 1;
  min-width: 0;
}
.item-filename {
  font-size: 13px;
  color: #e2e8f0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.item-meta {
  font-size: 12px;
  color: #718096;
  display: flex;
  gap: 12px;
  margin-top: 2px;
}
.item-status {
  font-size: 12px;
  font-weight: 600;
  padding: 2px 8px;
  border-radius: 10px;
  white-space: nowrap;
}
.item-status.status-pending { background: rgba(113, 128, 150, 0.2); color: #a0aec0; }
.item-status.status-queued { background: rgba(237, 137, 54, 0.2); color: #ed8936; }
.item-status.status-processing { background: rgba(66, 153, 225, 0.2); color: #4299e1; }
.item-status.status-completed { background: rgba(72, 187, 120, 0.2); color: #48bb78; }
.item-status.status-failed { background: rgba(229, 62, 62, 0.2); color: #fc8181; }
.item-actions {
  display: flex;
  gap: 4px;
}
.btn-icon {
  width: 28px;
  height: 28px;
  border: none;
  border-radius: 4px;
  background: transparent;
  color: #718096;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}
.btn-icon:hover {
  background: rgba(229, 62, 62, 0.2);
  color: #fc8181;
}
.history-empty {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #718096;
  font-size: 14px;
}
</style>
