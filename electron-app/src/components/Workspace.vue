<template>
  <div class="workspace">
    <el-empty v-if="!currentPatient" description="请从左侧选择患者" />

    <div v-else class="workspace-content">
      <TaskCard :patient="currentPatient" />
      <PatientInfoCard :patient="currentPatient" />
      <NoteGenerationCard :patient="currentPatient" />
      <RehabPlanCard :patient="currentPatient" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { usePatientStore } from '@/stores/patient'
import TaskCard from './TaskCard.vue'
import PatientInfoCard from './PatientInfoCard.vue'
import NoteGenerationCard from './NoteGenerationCard.vue'
import RehabPlanCard from './RehabPlanCard.vue'

const patientStore = usePatientStore()
const currentPatient = computed(() => patientStore.currentPatient)
</script>

<style scoped>
.workspace {
  height: 100%;
  overflow-y: auto;
}

.workspace-content {
  display: flex;
  flex-direction: column;
  gap: 15px;
}
</style>
