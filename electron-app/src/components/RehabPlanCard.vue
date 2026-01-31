<template>
  <el-card class="rehab-plan-card" shadow="never">
    <template #header>
      <div class="card-header">
        <span class="card-title">康复计划</span>
        <el-button
          :icon="MagicStick"
          size="small"
          type="primary"
          :loading="generating"
          @click="handleGenerate"
        >
          AI生成
        </el-button>
      </div>
    </template>

    <div v-if="!plan && !generating" class="empty-state">
      <el-empty
        description="暂无康复计划"
        :image-size="80"
      >
        <el-button type="primary" :icon="MagicStick" @click="handleGenerate">
          AI生成康复计划
        </el-button>
      </el-empty>
    </div>

    <div v-else class="plan-content">
      <!-- 康复目标 -->
      <div class="plan-section">
        <div class="section-title">
          <span class="title-icon">🎯</span>
          <span>康复目标</span>
        </div>

        <div class="goal-group">
          <h4 class="goal-title">短期目标（1-2周）</h4>
          <p class="goal-text">{{ plan?.short_term_goals || '暂无' }}</p>
        </div>

        <div class="goal-group">
          <h4 class="goal-title">长期目标（1-3个月）</h4>
          <p class="goal-text">{{ plan?.long_term_goals || '暂无' }}</p>
        </div>
      </div>

      <!-- 训练计划 -->
      <div class="plan-section">
        <div class="section-title">
          <span class="title-icon">🏋️</span>
          <span>训练计划</span>
        </div>

        <div class="training-list">
          <div
            v-for="(item, index) in trainingItems"
            :key="index"
            class="training-item"
          >
            <div class="training-header">
              <span class="training-name">{{ item.name }}</span>
              <el-tag size="small" :type="getFrequencyType(item.frequency)">
                {{ item.frequency }}
              </el-tag>
            </div>
            <div class="training-details">
              <span>时长：{{ item.duration }}</span>
              <span>组数：{{ item.sets }}</span>
              <span>强度：{{ item.intensity }}</span>
            </div>
            <div class="training-notes">注意事项：{{ item.notes }}</div>
          </div>
        </div>
      </div>

      <!-- 进展记录 -->
      <div class="plan-section">
        <div class="section-title">
          <span class="title-icon">📊</span>
          <span>进展记录</span>
        </div>

        <el-table :data="progressRecords" style="width: 100%" size="small">
          <el-table-column prop="record_date" label="日期" width="120" />
          <el-table-column prop="content" label="记录内容" />
          <el-table-column prop="score" label="评分" width="80">
            <template #default="scope">
              <el-rate v-model="scope.row.score" disabled />
            </template>
          </el-table-column>
        </el-table>

        <el-button
          v-if="!showProgressForm"
          class="add-progress-btn"
          :icon="Plus"
          @click="showProgressForm = true"
        >
          添加进展记录
        </el-button>

        <div v-else class="progress-form">
          <el-input
            v-model="newProgress.content"
            type="textarea"
            :rows="3"
            placeholder="请输入进展记录..."
          />
          <div class="form-actions">
            <el-rate v-model="newProgress.score" />
            <div class="buttons">
              <el-button size="small" @click="showProgressForm = false">取消</el-button>
              <el-button type="primary" size="small" @click="handleAddProgress">保存</el-button>
            </div>
          </div>
        </div>
      </div>

      <!-- 操作按钮 -->
      <div class="action-buttons">
        <el-button :icon="Edit" @click="handleEdit">编辑计划</el-button>
        <el-button :icon="Download" @click="handleExport">导出PDF</el-button>
      </div>
    </div>
  </el-card>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { MagicStick, Edit, Download, Plus } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'

interface Props {
  patient: any
}

const props = defineProps<Props>()

const generating = ref(false)
const plan = ref<any>(null)
const progressRecords = ref<any[]>([])
const showProgressForm = ref(false)
const newProgress = ref({
  content: '',
  score: 3
})

const trainingItems = computed(() => {
  if (!plan.value?.training_plan) return []
  try {
    return JSON.parse(plan.value.training_plan)
  } catch {
    return []
  }
})

onMounted(async () => {
  await loadPlan()
  await loadProgress()
})

async function loadPlan() {
  try {
    const response = await axios.get(
      `http://127.0.0.1:8000/api/rehab-plan/patient/${props.patient.hospital_number}`
    )
    plan.value = response.data
  } catch (error) {
    console.error('加载康复计划失败:', error)
  }
}

async function loadProgress() {
  try {
    const response = await axios.get(
      `http://127.0.0.1:8000/api/rehab-plan/${props.patient.hospital_number}/progress`
    )
    progressRecords.value = response.data
  } catch (error) {
    console.error('加载进展记录失败:', error)
  }
}

async function handleGenerate() {
  generating.value = true
  try {
    const response = await axios.post('http://127.0.0.1:8000/api/ai/generate-rehab-plan', {
      hospital_number: props.patient.hospital_number
    })

    if (response.data.success) {
      plan.value = response.data.data
      ElMessage.success('康复计划生成成功')
    }
  } catch (error: any) {
    ElMessage.error('生成失败: ' + (error.response?.data?.detail || error.message))
  } finally {
    generating.value = false
  }
}

async function handleAddProgress() {
  if (!newProgress.value.content.trim()) {
    ElMessage.warning('请输入进展记录')
    return
  }

  try {
    await axios.post(
      `http://127.0.0.1:8000/api/rehab-plan/${props.patient.hospital_number}/progress`,
      {
        record_date: new Date().toISOString().split('T')[0],
        content: newProgress.value.content,
        score: newProgress.value.score
      }
    )

    ElMessage.success('进展记录已添加')
    showProgressForm.value = false
    newProgress.value = { content: '', score: 3 }
    await loadProgress()
  } catch (error: any) {
    ElMessage.error('添加失败: ' + (error.response?.data?.detail || error.message))
  }
}

function handleEdit() {
  ElMessage.info('编辑功能待实现')
}

function handleExport() {
  ElMessage.info('导出PDF功能待实现')
}

function getFrequencyType(frequency: string) {
  if (frequency.includes('每日')) return 'success'
  if (frequency.includes('每周')) return 'warning'
  if (frequency.includes('每月')) return 'info'
  return ''
}
</script>

<style scoped>
.rehab-plan-card {
  border-radius: 12px;
  border: none;
  height: 100%;
  overflow-y: auto;
}

.rehab-plan-card :deep(.el-card__header) {
  padding: 12px 16px;
  border-bottom: 1px solid #E5E5EA;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-title {
  font-size: 16px;
  font-weight: 600;
  color: #333;
}

.empty-state {
  padding: 40px 0;
}

.plan-content {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.plan-section {
  background: #F9F9F9;
  border-radius: 8px;
  padding: 16px;
}

.section-title {
  font-size: 14px;
  font-weight: 600;
  color: #333;
  margin-bottom: 12px;
  display: flex;
  align-items: center;
  gap: 6px;
}

.title-icon {
  font-size: 16px;
}

.goal-group {
  margin-bottom: 16px;
}

.goal-group:last-child {
  margin-bottom: 0;
}

.goal-title {
  font-size: 13px;
  font-weight: 600;
  color: #409EFF;
  margin: 0 0 8px 0;
}

.goal-text {
  font-size: 13px;
  color: #666;
  line-height: 1.6;
  margin: 0;
  white-space: pre-wrap;
}

.training-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.training-item {
  background: white;
  border-radius: 6px;
  padding: 12px;
  border-left: 3px solid #409EFF;
}

.training-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.training-name {
  font-size: 14px;
  font-weight: 600;
  color: #333;
}

.training-details {
  display: flex;
  gap: 16px;
  font-size: 12px;
  color: #666;
  margin-bottom: 8px;
}

.training-notes {
  font-size: 12px;
  color: #999;
  font-style: italic;
}

.add-progress-btn {
  width: 100%;
  margin-top: 12px;
}

.progress-form {
  margin-top: 12px;
  padding: 12px;
  background: white;
  border-radius: 6px;
}

.form-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 12px;
}

.action-buttons {
  display: flex;
  gap: 8px;
  padding-top: 8px;
  border-top: 1px solid #E5E5EA;
}
</style>
