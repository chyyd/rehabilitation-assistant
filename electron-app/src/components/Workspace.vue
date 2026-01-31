<template>
  <div ref="workspaceRef" class="workspace">
    <el-empty v-if="!currentPatient" description="请从左侧选择患者" />

    <div v-else class="workspace-content">
      <TaskCard :patient="currentPatient" />
      <PatientInfoCard :patient="currentPatient" />
      <NoteGenerationCard :patient="currentPatient" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { usePatientStore } from '@/stores/patient'
import TaskCard from './TaskCard.vue'
import PatientInfoCard from './PatientInfoCard.vue'
import NoteGenerationCard from './NoteGenerationCard.vue'

const patientStore = usePatientStore()
const currentPatient = computed(() => patientStore.currentPatient)
const workspaceRef = ref<HTMLElement | null>(null)

// 监听患者变化，滚动到顶部
watch(() => patientStore.currentPatient?.id, (newId, oldId) => {
  if (newId && newId !== oldId && workspaceRef.value) {
    workspaceRef.value.scrollTop = 0
  }
})
</script>

<style scoped>
.workspace {
  height: 100%;
  overflow-y: auto;
  padding-right: 4px;
}

.workspace-content {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

/* 自定义滚动条 - 细小美观 */
.workspace::-webkit-scrollbar {
  width: 6px;
}

.workspace::-webkit-scrollbar-track {
  background: transparent;
}

.workspace::-webkit-scrollbar-thumb {
  background: rgba(144, 147, 153, 0.3);
  border-radius: 3px;
  transition: background 0.3s;
}

.workspace::-webkit-scrollbar-thumb:hover {
  background: rgba(144, 147, 153, 0.5);
}
</style>
