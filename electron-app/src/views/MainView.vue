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
          <el-button :icon="Bell" circle />
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
      <QuickTools class="right-sidebar" />
    </div>

    <!-- 新建患者对话框 -->
    <NewPatientDialog v-model="showNewPatientDialog" @success="handleNewPatient" />

    <!-- 设置对话框 -->
    <SettingsDialog v-model="showSettingsDialog" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Bell, Plus, Setting } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'
import PatientList from '@/components/PatientList.vue'
import Workspace from '@/components/Workspace.vue'
import QuickTools from '@/components/QuickTools.vue'
import NewPatientDialog from '@/components/NewPatientDialog.vue'
import SettingsDialog from '@/components/SettingsDialog.vue'
import { usePatientStore } from '@/stores/patient'

const patientStore = usePatientStore()
const reminderCount = ref(0)
const currentDate = ref('')
const showNewPatientDialog = ref(false)
const showSettingsDialog = ref(false)

onMounted(async () => {
  updateDate()
  // 加载患者列表
  await patientStore.fetchPatients()
  // 加载今日提醒数量
  await fetchReminderCount()
})

async function fetchReminderCount() {
  try {
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
}

.workspace {
  overflow-y: auto;
}

.right-sidebar {
  overflow-y: auto;
}
</style>
