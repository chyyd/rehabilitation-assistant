<template>
  <div class="patient-list">
    <el-tabs v-model="activeTab" class="patient-tabs">
      <el-tab-pane label="在院患者" name="active">
        <div class="list-header">
          <h3>在院患者</h3>
          <el-badge :value="activePatients.length" class="count-badge" />
        </div>

        <div v-if="patientStore.loading" class="loading">
          <el-skeleton :rows="3" animated />
        </div>

        <div v-else class="patient-cards">
          <div
            v-for="patient in sortedPatients"
            :key="patient.id"
            class="patient-card"
            :class="getPriorityClass(patient)"
          >
            <div class="card-header" @click="selectPatient(patient)">
              <span class="priority-icon">{{ getPriorityIcon(patient) }}</span>
              <div class="patient-info">
                <div class="patient-name">{{ patient.name || '未知' }}</div>
                <div class="patient-meta">
                  第{{ patient.days_in_hospital }}天 | {{ patient.hospital_number }}
                </div>
              </div>
            </div>
            <div class="patient-diagnosis" @click="selectPatient(patient)">
              {{ patient.diagnosis || '未填写诊断' }}
            </div>
            <div class="card-actions">
              <el-button
                :icon="Edit"
                size="small"
                text
                @click.stop="showEditDialog(patient)"
              >
                编辑
              </el-button>
            </div>
          </div>
        </div>
      </el-tab-pane>

      <el-tab-pane label="出院患者" name="discharged">
        <DischargedPatientList @undoDischarge="handleUndoDischarge" />
      </el-tab-pane>
    </el-tabs>

    <!-- 编辑患者对话框 -->
    <EditPatientDialog
      v-model="editDialogVisible"
      :patient="selectedPatient"
      @success="handleEditSuccess"
      @discharged="handleDischarged"
    />
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch, onMounted } from 'vue'
import { Edit } from '@element-plus/icons-vue'
import { usePatientStore } from '@/stores/patient'
import EditPatientDialog from './EditPatientDialog.vue'
import DischargedPatientList from './DischargedPatientList.vue'
import { ElMessage } from 'element-plus'

const patientStore = usePatientStore()
const editDialogVisible = ref(false)
const selectedPatient = ref<any>(null)
const activeTab = ref('active')

// 组件挂载时加载患者数据
onMounted(async () => {
  await patientStore.fetchPatients()
})

// 监听标签页切换，切换到出院患者时刷新数据
watch(activeTab, async (newTab) => {
  if (newTab === 'discharged') {
    await patientStore.fetchPatients()
  }
})

// 获取所有患者
const allPatients = computed(() => patientStore.patients || [])

// 筛选在院患者（没有出院日期的）
const activePatients = computed(() => {
  if (!allPatients.value || !Array.isArray(allPatients.value)) return []
  return allPatients.value.filter(p => !p.discharge_date)
})

const sortedPatients = computed(() => {
  if (!activePatients.value || !Array.isArray(activePatients.value)) return []

  return [...activePatients.value].sort((a, b) => {
    // 按优先级排序：紧急 > 高 > 普通
    const priorityMap = { urgent: 3, high: 2, normal: 1 }
    const priorityA = getPriority(a)
    const priorityB = getPriority(b)
    return priorityB - priorityA
  })
})

function getPriority(patient: any): string {
  const days = patient.days_in_hospital
  if (days >= 85) return 'urgent'
  if (days <= 3) return 'high'
  return 'normal'
}

function getPriorityIcon(patient: any): string {
  const priority = getPriority(patient)
  const icons = { urgent: '🚨', high: '🟡', normal: '🟢' }
  return icons[priority]
}

function getPriorityClass(patient: any): string {
  return `priority-${getPriority(patient)}`
}

function selectPatient(patient: any) {
  patientStore.selectPatient(patient)
}

function showEditDialog(patient: any) {
  selectedPatient.value = patient
  editDialogVisible.value = true
}

async function handleEditSuccess() {
  // 重新加载患者列表
  await patientStore.fetchPatients()
  ElMessage.success('患者信息已更新')
}

function handleDischarged() {
  // 切换到出院患者标签页
  activeTab.value = 'discharged'
}

function handleUndoDischarge() {
  console.log('[PatientList] 收到撤销出院事件，切换到在院患者标签页')
  // 切换回在院患者标签页
  activeTab.value = 'active'
}
</script>

<style scoped>
/* iOS风格患者卡片样式 */
.patient-list {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.patient-tabs {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.patient-tabs :deep(.el-tabs__content) {
  flex: 1;
  overflow-y: auto;
}

.patient-tabs :deep(.el-tab-pane) {
  height: 100%;
}

.list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
  padding: 0 5px;
}

.list-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
}

.patient-cards {
  flex: 1;
  overflow-y: auto;
}

.patient-card {
  background: white;
  border-radius: 12px;
  padding: 10px 12px;
  margin-bottom: 10px;
  cursor: pointer;
  transition: all 0.2s ease;
  border: 2px solid transparent;
}

.patient-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 6px;
}

.priority-icon {
  font-size: 16px;
}

.patient-name {
  font-size: 14px;
  font-weight: 600;
  color: #333;
}

.patient-meta {
  font-size: 12px;
  color: #999;
  margin-top: 2px;
}

.patient-diagnosis {
  font-size: 13px;
  color: #666;
  padding-left: 24px;
  cursor: pointer;
}

.card-actions {
  display: flex;
  justify-content: flex-end;
  padding-top: 8px;
  border-top: 1px solid #f0f0f0;
  margin-top: 8px;
}

/* 优先级样式 */
.priority-urgent {
  background: #FFF5F5;
  border-color: #FF3B30;
}

.priority-high {
  background: #FFFBF5;
  border-color: #FF9500;
}

.priority-normal {
  background: #F0FFF4;
  border-color: #34C759;
}

/* 自定义滚动条 - 细小美观 */
.patient-tabs :deep(.el-tabs__content) {
  padding-right: 4px;
}

.patient-tabs :deep(.el-tabs__content::-webkit-scrollbar) {
  width: 6px;
}

.patient-tabs :deep(.el-tabs__content::-webkit-scrollbar-track) {
  background: transparent;
}

.patient-tabs :deep(.el-tabs__content::-webkit-scrollbar-thumb) {
  background: rgba(144, 147, 153, 0.3);
  border-radius: 3px;
  transition: background 0.3s;
}

.patient-tabs :deep(.el-tabs__content::-webkit-scrollbar-thumb:hover) {
  background: rgba(144, 147, 153, 0.5);
}

.patient-cards {
  padding-right: 4px;
}

.patient-cards::-webkit-scrollbar {
  width: 6px;
}

.patient-cards::-webkit-scrollbar-track {
  background: transparent;
}

.patient-cards::-webkit-scrollbar-thumb {
  background: rgba(144, 147, 153, 0.3);
  border-radius: 3px;
  transition: background 0.3s;
}

.patient-cards::-webkit-scrollbar-thumb:hover {
  background: rgba(144, 147, 153, 0.5);
}
</style>
