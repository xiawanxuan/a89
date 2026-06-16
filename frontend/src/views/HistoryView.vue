<template>
  <div class="history-view">
    <HistoryList />
  </div>
</template>

<script setup lang="ts">
import HistoryList from '@/components/HistoryList.vue'
</script>

<style scoped>
.history-view {
  flex: 1;
  padding: 16px;
  overflow: hidden;
}
</style>
