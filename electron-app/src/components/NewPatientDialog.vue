<template>
  <el-dialog
    v-model="visible"
    title="新建患者"
    width="600px"
    @close="handleClose"
  >
    <el-steps :active="currentStep" finish-status="success" class="steps">
      <el-step title="输入住院号" />
      <el-step title="粘贴病程记录" />
      <el-step title="确认信息" />
    </el-steps>

    <div class="dialog-content">
      <!-- 步骤1：输入住院号 -->
      <div v-if="currentStep === 0" class="step-content">
        <el-form :model="form" label-width="100px">
          <el-form-item label="住院号" required>
            <el-input v-model="form.hospital_number" placeholder="请输入住院号" />
          </el-form-item>
        </el-form>
      </div>

      <!-- 步骤2：粘贴病程记录 -->
      <div v-if="currentStep === 1" class="step-content">
        <el-input
          v-model="form.initial_note"
          type="textarea"
          :rows="10"
          placeholder="请粘贴首次病程记录..."
        />
      </div>

      <!-- 步骤3：确认信息 -->
      <div v-if="currentStep === 2" class="step-content">
        <el-descriptions :column="2" border v-if="extractedInfo.name">
          <el-descriptions-item label="住院号">{{ form.hospital_number }}</el-descriptions-item>
          <el-descriptions-item label="姓名">{{ extractedInfo.name }}</el-descriptions-item>
          <el-descriptions-item label="性别">{{ extractedInfo.gender }}</el-descriptions-item>
          <el-descriptions-item label="年龄">{{ extractedInfo.age }}</el-descriptions-item>
          <el-descriptions-item label="入院日期">{{ extractedInfo.admission_date }}</el-descriptions-item>
          <el-descriptions-item label="诊断">{{ extractedInfo.diagnosis }}</el-descriptions-item>
          <el-descriptions-item label="主诉" :span="2">{{ extractedInfo.chief_complaint }}</el-descriptions-item>
        </el-descriptions>
        <el-empty v-else description="未提取到患者信息" />
      </div>
    </div>

    <template #footer>
      <span class="dialog-footer">
        <el-button @click="handleClose">取消</el-button>
        <el-button v-if="currentStep > 0" @click="previousStep">上一步</el-button>
        <el-button v-if="currentStep < 2" type="primary" @click="nextStep">下一步</el-button>
        <el-button v-else type="primary" :loading="saving" @click="handleSave">完成并保存</el-button>
      </span>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'

const props = defineProps<{
  modelValue: boolean
}>()

const emit = defineEmits(['update:modelValue', 'success'])

const visible = ref(props.modelValue)
const currentStep = ref(0)
const saving = ref(false)
const form = ref({
  hospital_number: '',
  initial_note: ''
})
const extractedInfo = ref<any>({})

watch(() => props.modelValue, (val) => {
  visible.value = val
})

watch(visible, (val) => {
  emit('update:modelValue', val)
})

async function nextStep() {
  if (currentStep.value === 0) {
    if (!form.value.hospital_number) {
      ElMessage.warning('请输入住院号')
      return
    }
  } else if (currentStep.value === 1) {
    // 调用AI提取信息
    if (!form.value.initial_note) {
      ElMessage.warning('请粘贴首次病程记录')
      return
    }
    await extractPatientInfo()
  }
  currentStep.value++
}

async function extractPatientInfo() {
  try {
    const response = await axios.post('http://127.0.0.1:8000/api/ai/extract-patient-info', {
      initial_note: form.value.initial_note
    })

    if (response.data.success) {
      extractedInfo.value = response.data.data
      ElMessage.success('信息提取成功')
    }
  } catch (error: any) {
    ElMessage.error('提取失败: ' + (error.response?.data?.detail || error.message))
  }
}

async function handleSave() {
  saving.value = true
  try {
    const response = await axios.post('http://127.0.0.1:8000/api/patients/', {
      hospital_number: form.value.hospital_number,
      ...extractedInfo.value,
      initial_note: form.value.initial_note
    })

    if (response.data) {
      // 初始化患者提醒
      await initializeReminders(form.value.hospital_number)

      ElMessage.success('患者创建成功')
      emit('success')
      handleClose()
    }
  } catch (error: any) {
    ElMessage.error('保存失败: ' + (error.response?.data?.detail || error.message))
  } finally {
    saving.value = false
  }
}

async function initializeReminders(hospitalNumber: string) {
  try {
    await axios.post(`http://127.0.0.1:8000/api/reminders/patient/${hospitalNumber}/initialize`)
  } catch (error) {
    console.error('初始化提醒失败:', error)
  }
}

function handleClose() {
  visible.value = false
  currentStep.value = 0
  form.value = {
    hospital_number: '',
    initial_note: ''
  }
  extractedInfo.value = {}
}

function previousStep() {
  currentStep.value--
}
</script>

<style scoped>
.steps {
  margin-bottom: 24px;
}

.dialog-content {
  min-height: 200px;
}

.step-content {
  padding: 20px;
}
</style>
