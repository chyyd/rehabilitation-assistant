<template>
  <div class="patient-list">
    <el-tabs v-model="activeTab" class="patient-tabs">
      <el-tab-pane label="在院患者" name="active">
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
              <el-button
                :icon="Edit"
                size="small"
                text
                class="edit-button"
                @click.stop="showEditDialog(patient)"
              />
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
import { computed, ref, watch, onMounted, onUnmounted } from 'vue'
import { Edit } from '@element-plus/icons-vue'
import { usePatientStore } from '@/stores/patient'
import EditPatientDialog from './EditPatientDialog.vue'
import DischargedPatientList from './DischargedPatientList.vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'

const patientStore = usePatientStore()
const editDialogVisible = ref(false)
const selectedPatient = ref<any>(null)
const activeTab = ref('active')

// 存储每个患者的今日未完成提醒数量
const patientReminderCount = ref<Record<number, number>>({})

// 定时刷新提醒
let refreshTimer: ReturnType<typeof setInterval> | null = null

// 组件挂载时加载患者数据
onMounted(async () => {
  // 先为所有在院患者创建今日提醒
  await ensureTodayReminders()
  await patientStore.fetchPatients()
  await loadTodayReminders()

  // 每30秒自动刷新今日提醒，确保优先级实时更新
  refreshTimer = setInterval(async () => {
    if (activeTab.value === 'active') {
      await loadTodayReminders()
    }
  }, 30000)
})

// 确保所有在院患者都有今日提醒
async function ensureTodayReminders() {
  try {
    await axios.post('http://127.0.0.1:8000/api/reminders/initialize-all-today')
  } catch (error) {
    // 静默失败，不影响用户体验
    console.warn('初始化今日提醒失败:', error)
  }
}

// 组件卸载时清理定时器
onUnmounted(() => {
  if (refreshTimer) {
    clearInterval(refreshTimer)
  }
})

// 监听标签页切换，切换时刷新数据
watch(activeTab, async (newTab) => {
  // 切换到在院患者时，刷新今日提醒以更新优先级
  if (newTab === 'active') {
    await loadTodayReminders()
  }
  // 切换到出院患者时，刷新患者列表
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
    // 按优先级排序：紧急 > 高 > 正常
    const priorityOrder = { urgent: 0, high: 1, normal: 2 }
    const priorityA = priorityOrder[getPriority(a)] ?? 3
    const priorityB = priorityOrder[getPriority(b)] ?? 3

    if (priorityA !== priorityB) {
      return priorityA - priorityB
    }

    // 同优先级按住院天数倒序排列
    return b.days_in_hospital - a.days_in_hospital
  })
})

// 加载今日及未来的所有未完成提醒
async function loadTodayReminders() {
  try {
    // 获取所有未完成的提醒（不限日期）
    const response = await axios.get('http://127.0.0.1:8000/api/reminders/today')

    console.log('[PatientList] 加载提醒成功，数量:', response.data.length)

    // 统计每个患者的未完成提醒数量
    const counts: Record<number, number> = {}

    response.data.forEach((reminder: any) => {
      console.log(`[PatientList] 提醒: ${reminder.description}, 日期: ${reminder.reminder_date}, 患者ID: ${reminder.patient_id}`)

      // 统计所有未完成的提醒
      if (!reminder.is_completed) {
        counts[reminder.patient_id] = (counts[reminder.patient_id] || 0) + 1
      }
    })

    console.log('[PatientList] 患者提醒统计:', counts)
    patientReminderCount.value = counts
  } catch (error) {
    console.error('加载提醒失败:', error)
  }
}

function getPriority(patient: any): string {
  const days = patient.days_in_hospital

  // 优先级判断：
  // 1. 住院85天以上 = 紧急（红色）🚨
  if (days >= 85) return 'urgent'

  // 2. 检查是否有未完成的今日提醒
  const hasPendingReminders = (patientReminderCount.value[patient.id] || 0) > 0

  // 3. 有未完成任务 = 高（黄色）🟡
  if (hasPendingReminders) return 'high'

  // 4. 所有任务完成 = 正常（绿色）🟢
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
  // 重新加载患者列表和提醒
  await patientStore.fetchPatients()
  await loadTodayReminders()
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
  position: relative;
}

.priority-icon {
  font-size: 16px;
  flex-shrink: 0;
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

.edit-button {
  position: absolute;
  top: 0;
  right: 0;
  padding: 4px !important;
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
