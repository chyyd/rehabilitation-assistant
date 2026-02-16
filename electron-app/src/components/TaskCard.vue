<template>
  <el-card class="task-card" shadow="never">
    <template #header>
      <span class="card-title">今日任务</span>
    </template>

    <div v-loading="loading" class="task-list">
      <div v-if="urgentReminders.length > 0" class="task-group">
        <div class="task-group-title">紧急</div>
        <div
          v-for="reminder in urgentReminders"
          :key="reminder.id"
          class="task-item urgent"
        >
          <span class="task-icon">🚨</span>
          <span class="task-text">{{ reminder.description }}</span>
          <el-button
            :icon="Check"
            size="small"
            type="success"
            text
            @click="handleComplete(reminder)"
          >
            完成
          </el-button>
        </div>
      </div>

      <div v-if="highReminders.length > 0" class="task-group">
        <div class="task-group-title">重要</div>
        <div
          v-for="reminder in highReminders"
          :key="reminder.id"
          class="task-item high"
        >
          <span class="task-icon">🟡</span>
          <span class="task-text">{{ reminder.description }}</span>
          <el-button
            :icon="Check"
            size="small"
            type="success"
            text
            @click="handleComplete(reminder)"
          >
            完成
          </el-button>
        </div>
      </div>

      <div v-if="normalReminders.length > 0" class="task-group">
        <div class="task-group-title">常规</div>
        <div
          v-for="reminder in normalReminders"
          :key="reminder.id"
          class="task-item normal"
        >
          <span class="task-icon">🟢</span>
          <span class="task-text">{{ reminder.description }}</span>
          <el-button
            :icon="Check"
            size="small"
            type="success"
            text
            @click="handleComplete(reminder)"
          >
            完成
          </el-button>
        </div>
      </div>

      <el-empty v-if="allReminders.length === 0" description="今日暂无任务" :image-size="60" />
    </div>
  </el-card>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { Check } from '@element-plus/icons-vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'

interface Props {
  patient: any
}

const props = defineProps<Props>()

const reminders = ref<any[]>([])
const loading = ref(false)

const urgentReminders = computed(() =>
  reminders.value.filter(r => r.priority === '紧急')
)

const highReminders = computed(() =>
  reminders.value.filter(r => r.priority === '高')
)

const normalReminders = computed(() =>
  reminders.value.filter(r => !['紧急', '高'].includes(r.priority))
)

const allReminders = computed(() => reminders.value)

// 监听患者变化
watch(() => props.patient, (newPatient) => {
  if (newPatient && newPatient.hospital_number) {
    fetchReminders()
  }
}, { immediate: true })

onMounted(async () => {
  // onMounted现在不需要手动调用，因为watch有immediate: true
})

async function fetchReminders() {
  if (!props.patient || !props.patient.hospital_number) {
    return
  }

  loading.value = true
  try {
    // 只获取未完成的提醒
    const response = await axios.get(`http://127.0.0.1:8000/api/reminders/patient/${props.patient.hospital_number}`, {
      params: { upcoming: true }
    })
    reminders.value = response.data

    // 如果没有提醒，自动初始化
    if (reminders.value.length === 0) {
      await initializeReminders()
    }
  } catch (error) {
    console.error('获取提醒失败:', error)
  } finally {
    loading.value = false
  }
}

async function initializeReminders() {
  try {
    const response = await axios.post(`http://127.0.0.1:8000/api/reminders/patient/${props.patient.hospital_number}/initialize`)
    if (response.data.success && response.data.created_count > 0) {
      // 重新加载提醒（只获取未完成的）
      const reminderResponse = await axios.get(`http://127.0.0.1:8000/api/reminders/patient/${props.patient.hospital_number}`, {
        params: { upcoming: true }
      })
      reminders.value = reminderResponse.data
    }
  } catch (error) {
    console.error('初始化提醒失败:', error)
  }
}

async function handleComplete(reminder: any) {
  try {
    await axios.put(`http://127.0.0.1:8000/api/reminders/${reminder.id}/complete`)
    ElMessage.success('待办事项已完成')

    // 从列表中移除已完成的提醒
    reminders.value = reminders.value.filter(r => r.id !== reminder.id)
  } catch (error: any) {
    ElMessage.error('操作失败: ' + (error.response?.data?.detail || error.message))
  }
}
</script>

<style scoped>
.task-card {
  border-radius: 12px;
  border: none;
}

.task-card :deep(.el-card__header) {
  padding: 12px 16px;
  border-bottom: 1px solid #E5E5EA;
}

.card-title {
  font-size: 16px;
  font-weight: 600;
  color: #333;
}

.task-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  min-height: 100px;
}

.task-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.task-group-title {
  font-size: 12px;
  font-weight: 600;
  color: #666;
  padding-left: 4px;
}

.task-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  border-radius: 8px;
  background: #F9F9F9;
}

.task-item.urgent {
  background: #FFF5F5;
  border-left: 3px solid #FF3B30;
}

.task-item.high {
  background: #FFFBF5;
  border-left: 3px solid #FF9500;
}

.task-item.normal {
  background: #F0FFF4;
  border-left: 3px solid #34C759;
}

.task-icon {
  font-size: 14px;
}

.task-text {
  font-size: 13px;
  color: #333;
  flex: 1;
}

:deep(.el-button--small) {
  padding: 4px 8px;
}
</style>
