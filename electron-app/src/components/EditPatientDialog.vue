<template>
  <el-dialog
    v-model="visible"
    title="编辑患者信息"
    width="700px"
    @close="handleClose"
  >
    <el-form :model="form" label-width="100px" v-loading="loading">
      <el-form-item label="住院号">
        <el-input v-model="form.hospital_number" disabled />
      </el-form-item>

      <el-row :gutter="16">
        <el-col :span="12">
          <el-form-item label="姓名">
            <el-input v-model="form.name" placeholder="请输入姓名" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="性别">
            <el-select v-model="form.gender" placeholder="请选择性别">
              <el-option label="男" value="男" />
              <el-option label="女" value="女" />
            </el-select>
          </el-form-item>
        </el-col>
      </el-row>

      <el-row :gutter="16">
        <el-col :span="12">
          <el-form-item label="年龄">
            <el-input-number v-model="form.age" :min="0" :max="150" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="入院日期">
            <el-date-picker
              v-model="form.admission_date"
              type="date"
              placeholder="选择日期"
              disabled
            />
          </el-form-item>
        </el-col>
      </el-row>

      <el-form-item label="出院日期">
        <el-date-picker
          v-model="form.discharge_date"
          type="date"
          placeholder="患者出院时选择"
          clearable
        />
        <div class="form-tip">设置出院日期后，患者将不再显示在住院列表中</div>
      </el-form-item>

      <el-form-item label="主诉">
        <el-input
          v-model="form.chief_complaint"
          type="textarea"
          :rows="2"
          placeholder="请输入主诉"
        />
      </el-form-item>

      <el-form-item label="诊断">
        <el-input
          v-model="form.diagnosis"
          type="textarea"
          :rows="2"
          placeholder="请输入诊断"
        />
      </el-form-item>

      <el-form-item label="既往史">
        <el-input
          v-model="form.past_history"
          type="textarea"
          :rows="2"
          placeholder="请输入既往史"
        />
      </el-form-item>

      <el-form-item label="过敏史">
        <el-input
          v-model="form.allergy_history"
          type="textarea"
          :rows="2"
          placeholder="请输入过敏史"
        />
      </el-form-item>

      <el-form-item label="专科检查">
        <el-input
          v-model="form.specialist_exam"
          type="textarea"
          :rows="3"
          placeholder="请输入专科检查"
        />
      </el-form-item>
    </el-form>

    <template #footer>
      <span class="dialog-footer">
        <el-button @click="handleClose">取消</el-button>
        <el-button type="primary" :loading="saving" @click="handleSave">保存修改</el-button>
      </span>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'

interface Props {
  modelValue: boolean
  patient: any
}

const props = defineProps<Props>()
const emit = defineEmits(['update:modelValue', 'success'])

const visible = ref(props.modelValue)
const loading = ref(false)
const saving = ref(false)
const form = ref({
  hospital_number: '',
  name: '',
  gender: '',
  age: 0,
  admission_date: '',
  discharge_date: null as Date | null,
  chief_complaint: '',
  diagnosis: '',
  past_history: '',
  allergy_history: '',
  specialist_exam: ''
})

watch(() => props.modelValue, (val) => {
  visible.value = val
  if (val && props.patient) {
    loadPatientData()
  }
})

watch(visible, (val) => {
  emit('update:modelValue', val)
})

async function loadPatientData() {
  loading.value = true
  try {
    const response = await axios.get(
      `http://127.0.0.1:8000/api/patients/${props.patient.hospital_number}`
    )

    const patient = response.data
    form.value = {
      hospital_number: patient.hospital_number,
      name: patient.name || '',
      gender: patient.gender || '',
      age: patient.age || 0,
      admission_date: patient.admission_date,
      discharge_date: patient.discharge_date ? new Date(patient.discharge_date) : null,
      chief_complaint: patient.chief_complaint || '',
      diagnosis: patient.diagnosis || '',
      past_history: patient.past_history || '',
      allergy_history: patient.allergy_history || '',
      specialist_exam: patient.specialist_exam || ''
    }
  } catch (error: any) {
    ElMessage.error('加载患者信息失败: ' + (error.response?.data?.detail || error.message))
  } finally {
    loading.value = false
  }
}

async function handleSave() {
  saving.value = true
  try {
    const updateData: any = {}

    // 只发送有值的字段
    if (form.value.name) updateData.name = form.value.name
    if (form.value.gender) updateData.gender = form.value.gender
    if (form.value.age) updateData.age = form.value.age
    if (form.value.discharge_date) updateData.discharge_date = form.value.discharge_date.toISOString().split('T')[0]
    if (form.value.chief_complaint) updateData.chief_complaint = form.value.chief_complaint
    if (form.value.diagnosis) updateData.diagnosis = form.value.diagnosis
    if (form.value.past_history) updateData.past_history = form.value.past_history
    if (form.value.allergy_history) updateData.allergy_history = form.value.allergy_history
    if (form.value.specialist_exam) updateData.specialist_exam = form.value.specialist_exam

    const response = await axios.put(
      `http://127.0.0.1:8000/api/patients/${form.value.hospital_number}`,
      updateData
    )

    if (response.data) {
      ElMessage.success('患者信息更新成功')
      emit('success')
      handleClose()
    }
  } catch (error: any) {
    ElMessage.error('保存失败: ' + (error.response?.data?.detail || error.message))
  } finally {
    saving.value = false
  }
}

function handleClose() {
  visible.value = false
  form.value = {
    hospital_number: '',
    name: '',
    gender: '',
    age: 0,
    admission_date: '',
    discharge_date: null,
    chief_complaint: '',
    diagnosis: '',
    past_history: '',
    allergy_history: '',
    specialist_exam: ''
  }
}
</script>

<style scoped>
.form-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

:deep(.el-form-item__label) {
  font-weight: 500;
}

:deep(.el-input-number) {
  width: 100%;
}
</style>
