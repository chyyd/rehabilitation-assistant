<template>
  <div class="main-container">
    <!-- 顶部导航栏 -->
    <div class="navbar">
      <div class="navbar-left">
        <span class="app-title">康复科助手</span>
      </div>
      <div class="navbar-center">
        <span class="current-date">{{ currentDate }}</span>
      </div>
      <div class="navbar-right">
        <el-badge :value="reminderCount" class="reminder-badge">
          <el-button :icon="Bell" circle @click="showReminderDialog = true" />
        </el-badge>
        <el-button type="primary" :icon="Plus" @click="showNewPatientDialog = true">
          新患者
        </el-button>
        <el-button :icon="Setting" circle @click="showSettingsDialog = true" />
      </div>
    </div>

    <!-- 三栏布局 -->
    <div class="content-area">
      <!-- 左栏：患者列表 -->
      <PatientList class="left-sidebar" />

      <!-- 中栏：工作区 -->
      <Workspace class="workspace" />

      <!-- 右栏：快速工具 -->
      <QuickTools ref="quickToolsRef" class="right-sidebar" />
    </div>

    <!-- 新建患者对话框 -->
    <NewPatientDialog v-model="showNewPatientDialog" @success="handleNewPatient" />

    <!-- 设置对话框 -->
    <SettingsDialog v-model="showSettingsDialog" />

    <!-- 常用短语管理对话框 -->
    <ManagePhrasesDialog v-model="showManagePhrasesDialog" @saved="handlePhrasesSaved" />

    <!-- 提醒列表对话框 -->
    <el-dialog
      v-model="showReminderDialog"
      width="650px"
      @open="fetchReminders"
    >
      <template #header>
        <div class="reminder-dialog-header">
          <span>今日提醒</span>
          <el-button
            type="primary"
            size="small"
            :icon="Plus"
            @click="showAddTomorrowReminderDialog"
          >
            添加提醒
          </el-button>
        </div>
      </template>
      <div v-loading="loadingReminders" class="reminder-list">
        <el-empty v-if="reminders.length === 0" description="暂无今日提醒" />
        <div v-else>
          <div
            v-for="reminder in reminders"
            :key="reminder.id"
            class="reminder-item"
            :class="{ 'completed': reminder.is_completed, 'clickable': !reminder.is_completed }"
            @click="handleReminderClick(reminder)"
          >
            <div class="reminder-content">
              <div class="reminder-header">
                <el-tag
                  :type="reminder.priority === '紧急' ? 'danger' : reminder.priority === '高' ? 'warning' : 'info'"
                  size="small"
                >
                  {{ reminder.priority === '紧急' ? '紧急' : reminder.priority === '高' ? '重要' : '普通' }}
                </el-tag>
                <span class="reminder-type">{{ reminder.reminder_type }}</span>
                <span class="reminder-time" v-if="reminder.day_number">第{{ reminder.day_number }}天</span>
              </div>
              <div class="reminder-text">{{ reminder.description }}</div>
              <div class="reminder-patient">
                患者：{{ reminder.hospital_number }}
              </div>
            </div>
            <div class="reminder-actions">
              <el-button
                v-if="!reminder.is_completed"
                type="success"
                size="small"
                :icon="Check"
                @click="markReminderCompleted(reminder.id)"
              >
                标记完成
              </el-button>
              <el-tag v-else type="success" size="small">
                已完成
              </el-tag>
            </div>
          </div>
        </div>
      </div>
    </el-dialog>

    <!-- 添加提醒对话框 -->
    <el-dialog
      v-model="showTomorrowReminderDialog"
      title="添加提醒"
      width="500px"
    >
      <el-form :model="tomorrowReminderForm" label-width="80px">
        <el-form-item label="患者">
          <el-select
            v-model="tomorrowReminderForm.hospitalNumber"
            placeholder="选择患者"
            style="width: 100%"
            filterable
          >
            <el-option
              v-for="patient in patientStore.patients.filter(p => !p.discharge_date)"
              :key="patient.id"
              :label="`${patient.name || patient.hospital_number} (${patient.hospital_number})`"
              :value="patient.hospital_number"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="提醒内容">
          <el-input
            v-model="tomorrowReminderForm.description"
            type="textarea"
            :rows="4"
            placeholder="请输入提醒内容"
          />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="createTomorrowReminder" :loading="creatingTomorrowReminder">
            创建提醒
          </el-button>
          <el-button @click="showTomorrowReminderDialog = false">取消</el-button>
        </el-form-item>
      </el-form>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { Bell, Plus, Setting, Check } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'
import PatientList from '@/components/PatientList.vue'
import Workspace from '@/components/Workspace.vue'
import QuickTools from '@/components/QuickTools.vue'
import NewPatientDialog from '@/components/NewPatientDialog.vue'
import SettingsDialog from '@/components/SettingsDialog.vue'
import ManagePhrasesDialog from '@/components/ManagePhrasesDialog.vue'
import { usePatientStore } from '@/stores/patient'
import { eventBus } from '@/utils/eventBus'

const patientStore = usePatientStore()
const quickToolsRef = ref<InstanceType<typeof QuickTools>>()
const reminderCount = ref(0)
const currentDate = ref('')
const showNewPatientDialog = ref(false)
const showSettingsDialog = ref(false)
const showManagePhrasesDialog = ref(false)
const showReminderDialog = ref(false)
const reminders = ref<any[]>([])
const loadingReminders = ref(false)
const showTomorrowReminderDialog = ref(false)
const creatingTomorrowReminder = ref(false)
const tomorrowReminderForm = ref({
  hospitalNumber: '',
  description: ''
})

// 计算明日的日期
const tomorrowDate = ref('')
function updateTomorrowDate() {
  const tomorrow = new Date()
  tomorrow.setDate(tomorrow.getDate() + 1)
  tomorrowDate.value = tomorrow.toISOString().split('T')[0]
}

// 处理显示明日提醒对话框事件
function handleShowTomorrowReminderDialog() {
  showAddTomorrowReminderDialog()
}

// 处理显示常用短语管理对话框事件
function handleShowManagePhrasesDialog() {
  showManagePhrasesDialog.value = true
}

// 处理常用短语保存成功
function handlePhrasesSaved() {
  ElMessage.success('常用短语已更新')
  // 刷新 QuickTools 中的短语列表
  quickToolsRef.value?.loadPhrases()
}

onMounted(async () => {
  updateDate()
  updateTomorrowDate()
  // 加载患者列表
  await patientStore.fetchPatients()
  // 加载今日提醒数量
  await fetchReminderCount()
  // 监听显示明日提醒对话框事件
  eventBus.on('show-tomorrow-reminder-dialog', handleShowTomorrowReminderDialog)
  // 监听显示常用短语管理对话框事件
  eventBus.on('show-manage-phrases-dialog', handleShowManagePhrasesDialog)
})

onUnmounted(() => {
  // 移除事件监听
  eventBus.off('show-tomorrow-reminder-dialog', handleShowTomorrowReminderDialog)
  eventBus.off('show-manage-phrases-dialog', handleShowManagePhrasesDialog)
})

async function fetchReminderCount() {
  try {
    // 先确保所有患者都有今日提醒
    await axios.post('http://127.0.0.1:8000/api/reminders/initialize-all-today').catch(() => {})

    // 再获取提醒数量
    const response = await axios.get('http://127.0.0.1:8000/api/reminders/today')
    reminderCount.value = response.data.length
  } catch (error) {
    console.error('获取提醒数量失败:', error)
  }
}

function updateDate() {
  const now = new Date()
  const options: Intl.DateTimeFormatOptions = {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    weekday: 'long'
  }
  currentDate.value = now.toLocaleDateString('zh-CN', options)
}

function handleNewPatient() {
  // 刷新患者列表
  patientStore.fetchPatients()
  // 刷新提醒数量
  fetchReminderCount()
}

// 获取今日提醒列表
async function fetchReminders() {
  loadingReminders.value = true
  try {
    const response = await axios.get('http://127.0.0.1:8000/api/reminders/today')
    reminders.value = response.data
  } catch (error) {
    console.error('获取提醒列表失败:', error)
    ElMessage.error('获取提醒列表失败')
  } finally {
    loadingReminders.value = false
  }
}

// 标记提醒为已完成
async function markReminderCompleted(reminderId: number) {
  try {
    await axios.put(`http://127.0.0.1:8000/api/reminders/${reminderId}/complete`)
    ElMessage.success('已标记为完成')
    // 重新获取提醒列表
    await fetchReminders()
    // 更新提醒数量
    await fetchReminderCount()
  } catch (error) {
    console.error('标记提醒失败:', error)
    ElMessage.error('标记提醒失败')
  }
}

// 点击提醒跳转到患者
async function handleReminderClick(reminder: any) {
  try {
    // 如果已完成则不跳转
    if (reminder.is_completed) return

    // 根据住院号获取患者信息
    const response = await axios.get(`http://127.0.0.1:8000/api/patients/${reminder.hospital_number}`)
    const patient = response.data

    // 设置为当前患者
    patientStore.selectPatient(patient)

    // 关闭提醒对话框
    showReminderDialog.value = false

    ElMessage.success(`已跳转到患者：${patient.name || reminder.hospital_number}`)
  } catch (error) {
    console.error('跳转到患者失败:', error)
    ElMessage.error('跳转失败，请手动选择患者')
  }
}

// 显示添加提醒对话框
function showAddTomorrowReminderDialog() {
  // 如果有当前患者，自动选中
  if (patientStore.currentPatient) {
    tomorrowReminderForm.value.hospitalNumber = patientStore.currentPatient.hospital_number
  }
  tomorrowReminderForm.value.description = ''
  showTomorrowReminderDialog.value = true
}

// 创建提醒
async function createTomorrowReminder() {
  if (!tomorrowReminderForm.value.hospitalNumber) {
    ElMessage.warning('请选择患者')
    return
  }

  if (!tomorrowReminderForm.value.description.trim()) {
    ElMessage.warning('请输入提醒内容')
    return
  }

  try {
    creatingTomorrowReminder.value = true

    await axios.post('http://127.0.0.1:8000/api/reminders/custom', {
      hospital_number: tomorrowReminderForm.value.hospitalNumber,
      reminder_date: tomorrowDate.value,
      description: tomorrowReminderForm.value.description
    })

    ElMessage.success('提醒创建成功')
    showTomorrowReminderDialog.value = false
    tomorrowReminderForm.value = {
      hospitalNumber: '',
      description: ''
    }
  } catch (error: any) {
    ElMessage.error('创建提醒失败: ' + (error.response?.data?.detail || error.message))
  } finally {
    creatingTomorrowReminder.value = false
  }
}

</script>

<style scoped>
.main-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  width: 100vw;
}

.navbar {
  height: 60px;
  background: #666;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  color: white;
}

.navbar-left .app-title {
  font-size: 18px;
  font-weight: 600;
}

.navbar-center {
  font-size: 14px;
}

.navbar-right {
  display: flex;
  gap: 10px;
}

.content-area {
  flex: 1;
  display: grid;
  grid-template-columns: 280px 1fr 300px;
  gap: 10px;
  padding: 10px;
  overflow: hidden;
}

.left-sidebar {
  overflow-y: auto;
  padding-right: 4px;
}

.workspace {
  overflow-y: auto;
  padding-right: 4px;
}

.right-sidebar {
  overflow-y: auto;
  padding-right: 4px;
}

/* 自定义滚动条 - 细小美观 */
.left-sidebar::-webkit-scrollbar,
.workspace::-webkit-scrollbar,
.right-sidebar::-webkit-scrollbar {
  width: 6px;
}

.left-sidebar::-webkit-scrollbar-track,
.workspace::-webkit-scrollbar-track,
.right-sidebar::-webkit-scrollbar-track {
  background: transparent;
}

.left-sidebar::-webkit-scrollbar-thumb,
.workspace::-webkit-scrollbar-thumb,
.right-sidebar::-webkit-scrollbar-thumb {
  background: rgba(144, 147, 153, 0.3);
  border-radius: 3px;
  transition: background 0.3s;
}

.left-sidebar::-webkit-scrollbar-thumb:hover,
.workspace::-webkit-scrollbar-thumb:hover,
.right-sidebar::-webkit-scrollbar-thumb:hover {
  background: rgba(144, 147, 153, 0.5);
}

/* 提醒列表样式 */
.reminder-list {
  max-height: 400px;
  overflow-y: auto;
  padding-right: 4px;
}

.reminder-item {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 12px;
  margin-bottom: 12px;
  background: #F7F8FA;
  border-radius: 8px;
  border-left: 3px solid #409EFF;
  transition: all 0.3s;
}

.reminder-item:hover {
  background: #FFFFFF;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.reminder-item.completed {
  opacity: 0.6;
  border-left-color: #67C23A;
}

.reminder-item.completed .reminder-text {
  text-decoration: line-through;
}

.reminder-item.clickable {
  cursor: pointer;
}

.reminder-item.clickable:hover {
  transform: translateX(4px);
  background: #FFFFFF;
  box-shadow: 0 2px 12px rgba(64, 158, 255, 0.15);
}

.reminder-content {
  flex: 1;
  padding-right: 12px;
}

.reminder-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 6px;
}

.reminder-type {
  font-size: 12px;
  color: #606266;
  background: #E4E7ED;
  padding: 2px 8px;
  border-radius: 4px;
}

.reminder-time {
  font-size: 12px;
  color: #909399;
}

.reminder-text {
  font-size: 14px;
  color: #303133;
  line-height: 1.6;
  margin-bottom: 4px;
}

.reminder-patient {
  font-size: 12px;
  color: #606266;
}

.reminder-actions {
  display: flex;
  align-items: center;
}

/* 提醒对话框头部样式 */
.reminder-dialog-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.reminder-dialog-header span {
  font-size: 18px;
  font-weight: 600;
}
</style>
