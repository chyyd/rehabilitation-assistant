<template>
  <div class="discharged-patient-list">
    <div v-if="loading" class="loading">
      <el-skeleton :rows="3" animated />
    </div>

    <div v-else-if="dischargedPatients.length > 0" class="patient-cards">
      <div
        v-for="patient in sortedPatients"
        :key="patient.id"
        class="patient-card"
      >
        <div class="card-header" @click="selectPatient(patient)">
          <div class="patient-info">
            <div class="patient-name">{{ patient.name || '未知' }}</div>
            <div class="patient-meta">
              {{ patient.hospital_number }} | 住院{{ patient.days_in_hospital }}天
            </div>
          </div>
        </div>
        <div class="card-body">
          <div class="patient-diagnosis" @click="selectPatient(patient)">
            {{ patient.diagnosis || '未填写诊断' }}
          </div>
          <div class="discharge-info">
            <el-tag size="small" type="warning">已出院</el-tag>
            <span class="discharge-date">出院日期：{{ formatDate(patient.discharge_date) }}</span>
          </div>
        </div>
        <div class="card-actions">
          <el-button
            :icon="View"
            size="small"
            @click="selectPatient(patient)"
          >
            查看详情
          </el-button>
          <el-button
            type="danger"
            :icon="Delete"
            size="small"
            @click="handleDelete(patient)"
          >
            删除
          </el-button>
        </div>
      </div>
    </div>

    <el-empty v-else description="暂无出院患者" />

    <!-- 患者详情抽屉 -->
    <el-drawer
      v-model="drawerVisible"
      title="患者详情"
      direction="rtl"
      size="50%"
    >
      <div v-if="selectedPatient" class="patient-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="住院号">{{ selectedPatient.hospital_number }}</el-descriptions-item>
          <el-descriptions-item label="姓名">{{ selectedPatient.name || '未填写' }}</el-descriptions-item>
          <el-descriptions-item label="性别">{{ selectedPatient.gender || '未填写' }}</el-descriptions-item>
          <el-descriptions-item label="年龄">{{ selectedPatient.age || '未填写' }}岁</el-descriptions-item>
          <el-descriptions-item label="入院日期">{{ formatDate(selectedPatient.admission_date) }}</el-descriptions-item>
          <el-descriptions-item label="出院日期">{{ formatDate(selectedPatient.discharge_date) }}</el-descriptions-item>
          <el-descriptions-item label="住院天数">{{ selectedPatient.days_in_hospital }}天</el-descriptions-item>
          <el-descriptions-item label="诊断" :span="2">{{ selectedPatient.diagnosis || '未填写' }}</el-descriptions-item>
          <el-descriptions-item label="主诉" :span="2">{{ selectedPatient.chief_complaint || '未填写' }}</el-descriptions-item>
          <el-descriptions-item label="既往史" :span="2">
            {{ selectedPatient.past_history || '无' }}
          </el-descriptions-item>
          <el-descriptions-item label="过敏史" :span="2">
            {{ selectedPatient.allergy_history || '无' }}
          </el-descriptions-item>
          <el-descriptions-item label="专科检查" :span="2">
            <div class="specialist-exam">{{ selectedPatient.specialist_exam || '无' }}</div>
          </el-descriptions-item>
        </el-descriptions>

        <div class="drawer-actions">
          <el-button @click="drawerVisible = false">关闭</el-button>
          <el-button type="success" :icon="RefreshLeft" @click="handleUndoDischarge(selectedPatient)">撤销出院</el-button>
          <el-button type="danger" :icon="Delete" @click="handleDelete(selectedPatient)">删除患者</el-button>
        </div>
      </div>
    </el-drawer>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, nextTick } from 'vue'
import { View, Delete, RefreshLeft } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { usePatientStore } from '@/stores/patient'
import axios from 'axios'

// 使用与 store 相同的 axios 配置
const api = axios.create({
  baseURL: 'http://127.0.0.1:8000/api'
})

const patientStore = usePatientStore()
const loading = ref(false)
const drawerVisible = ref(false)
const selectedPatient = ref<any>(null)

// 定义 emit，用于通知父组件
const emit = defineEmits(['undoDischarge'])

// 获取所有患者（包括已出院）
const allPatients = computed(() => patientStore.patients || [])

// 筛选出已出院的患者
const dischargedPatients = computed(() => {
  if (!allPatients.value || !Array.isArray(allPatients.value)) return []
  return allPatients.value.filter(p => p.discharge_date)
})

// 按出院日期降序排序
const sortedPatients = computed(() => {
  return [...dischargedPatients.value].sort((a, b) => {
    const dateA = new Date(a.discharge_date).getTime()
    const dateB = new Date(b.discharge_date).getTime()
    return dateB - dateA
  })
})

function selectPatient(patient: any) {
  selectedPatient.value = patient
  drawerVisible.value = true
}

async function handleUndoDischarge(patient: any) {
  try {
    await ElMessageBox.confirm(
      `确定要撤销患者 ${patient.name || patient.hospital_number} 的出院状态吗？患者将重新回到在院患者列表。`,
      '撤销出院确认',
      {
        confirmButtonText: '确定撤销',
        cancelButtonText: '取消',
        type: 'info'
      }
    )

    loading.value = true

    console.log('[DischargedPatientList] 开始撤销出院，患者:', patient.name, '当前 discharge_date:', patient.discharge_date)

    // 清除出院日期（设置为 null）
    const updateResponse = await api.put(`/patients/${patient.hospital_number}`, {
      discharge_date: null
    })

    console.log('[DischargedPatientList] 更新 API 响应:', updateResponse.data)

    ElMessage.success('已撤销出院，患者已回到在院列表')

    // 刷新患者列表
    console.log('[DischargedPatientList] 开始刷新患者列表...')
    await patientStore.fetchPatients()
    console.log('[DischargedPatientList] 患者列表刷新完成，当前出院患者数量:', patientStore.patients.filter(p => p.discharge_date).length)

    // 等待 Vue 更新 DOM
    await nextTick()

    // 关闭抽屉
    drawerVisible.value = false
    selectedPatient.value = null

    // 通知父组件切换到在院患者标签页
    console.log('[DischargedPatientList] 触发 undoDischarge 事件')
    emit('undoDischarge')
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error('撤销出院失败: ' + (error.response?.data?.detail || error.message))
    }
  } finally {
    loading.value = false
  }
}

async function handleDelete(patient: any) {
  try {
    await ElMessageBox.confirm(
      `确定要删除患者 ${patient.name || patient.hospital_number} 吗？此操作不可恢复！`,
      '删除确认',
      {
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
        type: 'warning',
        confirmButtonClass: 'el-button--danger'
      }
    )

    loading.value = true
    await api.delete(`/patients/${patient.hospital_number}`)

    ElMessage.success('患者已删除')

    // 刷新患者列表
    await patientStore.fetchPatients()

    // 关闭抽屉
    if (selectedPatient.value?.hospital_number === patient.hospital_number) {
      drawerVisible.value = false
      selectedPatient.value = null
    }
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败: ' + (error.response?.data?.detail || error.message))
    }
  } finally {
    loading.value = false
  }
}

function formatDate(dateStr: string): string {
  if (!dateStr) return '未设置'
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN')
}
</script>

<style scoped>
.discharged-patient-list {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.patient-cards {
  flex: 1;
  overflow-y: auto;
  padding: 0 5px;
}

.patient-card {
  background: white;
  border-radius: 12px;
  padding: 12px;
  margin-bottom: 10px;
  border: 1px solid #E5E7EB;
  transition: all 0.2s ease;
}

.patient-card:hover {
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.card-header {
  margin-bottom: 8px;
}

.patient-info {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}

.patient-name {
  font-size: 14px;
  font-weight: 600;
  color: #333;
}

.patient-meta {
  font-size: 12px;
  color: #999;
}

.card-body {
  margin-bottom: 12px;
}

.patient-diagnosis {
  font-size: 13px;
  color: #666;
  margin-bottom: 8px;
  cursor: pointer;
}

.discharge-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.discharge-date {
  font-size: 12px;
  color: #999;
}

.card-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  padding-top: 8px;
  border-top: 1px solid #f0f0f0;
}

.specialist-exam {
  white-space: pre-wrap;
  word-break: break-word;
  line-height: 1.6;
  font-size: 13px;
  max-height: 300px;
  overflow-y: auto;
}

/* 自定义滚动条 - 细小美观 */
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

.specialist-exam::-webkit-scrollbar {
  width: 6px;
}

.specialist-exam::-webkit-scrollbar-track {
  background: transparent;
}

.specialist-exam::-webkit-scrollbar-thumb {
  background: rgba(144, 147, 153, 0.3);
  border-radius: 3px;
  transition: background 0.3s;
}

.specialist-exam::-webkit-scrollbar-thumb:hover {
  background: rgba(144, 147, 153, 0.5);
}
</style>
