<template>
  <div class="app-layout">
    <ToolBar :activeTab="activeTab" @update:activeTab="activeTab = $event" />
    <HomeView :activeTab="activeTab" />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import ToolBar from '@/components/ToolBar.vue'
import HomeView from '@/views/HomeView.vue'

const activeTab = ref('upload')
</script>

<style scoped>
.app-layout {
  display: flex;
  flex-direction: column;
  height: 100vh;
  width: 100vw;
  overflow: hidden;
}
</style>
