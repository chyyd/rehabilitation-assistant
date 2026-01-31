<template>
  <el-card class="info-card" shadow="never">
    <template #header>
      <span class="card-title">患者信息</span>
    </template>

    <div class="info-grid">
      <div class="info-row">
        <span class="info-label">住院号：</span>
        <span class="info-value">{{ patient.hospital_number }}</span>
      </div>
      <div class="info-row">
        <span class="info-label">姓名：</span>
        <span class="info-value">{{ patient.name || '未填写' }}</span>
      </div>
      <div class="info-row">
        <span class="info-label">性别：</span>
        <span class="info-value">{{ patient.gender || '未填写' }}</span>
      </div>
      <div class="info-row">
        <span class="info-label">年龄：</span>
        <span class="info-value">{{ patient.age || '未填写' }}</span>
      </div>
      <div class="info-row">
        <span class="info-label">入院日期：</span>
        <span class="info-value">{{ formatDate(patient.admission_date) }}</span>
      </div>
      <div class="info-row">
        <span class="info-label">住院天数：</span>
        <span class="info-value">{{ patient.days_in_hospital }}天</span>
      </div>
      <div class="info-row full-width">
        <span class="info-label">诊断：</span>
        <span class="info-value">{{ patient.diagnosis || '未填写' }}</span>
      </div>
      <div class="info-row full-width">
        <span class="info-label">主诉：</span>
        <span class="info-value">{{ patient.chief_complaint || '未填写' }}</span>
      </div>
    </div>
  </el-card>
</template>

<script setup lang="ts">
interface Props {
  patient: any
}

defineProps<Props>()

function formatDate(date: string) {
  if (!date) return '未填写'
  return new Date(date).toLocaleDateString('zh-CN')
}
</script>

<style scoped>
.info-card {
  border-radius: 12px;
  border: none;
}

.info-card :deep(.el-card__header) {
  padding: 12px 16px;
  border-bottom: 1px solid #E5E5EA;
}

.card-title {
  font-size: 16px;
  font-weight: 600;
  color: #333;
}

.info-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px 16px;
}

.info-row {
  display: flex;
  align-items: flex-start;
}

.info-row.full-width {
  grid-column: 1 / -1;
}

.info-label {
  font-size: 13px;
  color: #666;
  min-width: 80px;
  flex-shrink: 0;
}

.info-value {
  font-size: 13px;
  color: #333;
  word-break: break-all;
}
</style>
