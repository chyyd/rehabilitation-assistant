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
          <el-descriptions-item label="既往史" :span="2">{{ extractedInfo.past_history || '无' }}</el-descriptions-item>
          <el-descriptions-item label="过敏史" :span="2">{{ extractedInfo.allergy_history || '无' }}</el-descriptions-item>
          <el-descriptions-item label="专科检查" :span="2">
            <div class="specialist-exam">{{ extractedInfo.specialist_exam || '无' }}</div>
          </el-descriptions-item>
        </el-descriptions>
        <el-empty v-else description="未提取到患者信息" />
      </div>
    </div>

    <template #footer>
      <span class="dialog-footer">
        <el-button @click="handleClose">取消</el-button>
        <el-button v-if="currentStep > 0" @click="previousStep">上一步</el-button>
        <el-button v-if="currentStep < 2" type="primary" :loading="checking || extracting" :disabled="extracting" @click="nextStep">
          {{
            currentStep === 0 && checking ? '检查中...' :
            currentStep === 1 && extracting ? '信息提取中...' :
            '下一步'
          }}
        </el-button>
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
const checking = ref(false)
const extracting = ref(false)
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
    // 第一步：验证住院号
    if (!form.value.hospital_number) {
      ElMessage.warning('请输入住院号')
      return
    }

    // 检查住院号是否已存在
    checking.value = true
    try {
      const response = await axios.get(`http://127.0.0.1:8000/api/patients/${form.value.hospital_number}`)
      // 如果能获取到患者信息，说明住院号已存在
      if (response.data) {
        ElMessage.error(`住院号 ${form.value.hospital_number} 已存在，请使用其他住院号`)
        checking.value = false
        return
      }
    } catch (error: any) {
      // 404错误表示住院号不存在，可以继续
      if (error.response?.status === 404) {
        // 住院号可用，继续下一步
      } else {
        // 其他错误
        ElMessage.error('检查住院号失败: ' + (error.response?.data?.detail || error.message))
        checking.value = false
        return
      }
    } finally {
      checking.value = false
    }

    // 住院号检查通过，进入下一步
    currentStep.value++
  } else if (currentStep.value === 1) {
    // 第二步：调用AI提取信息
    if (!form.value.initial_note) {
      ElMessage.warning('请粘贴首次病程记录')
      return
    }

    // 先设置提取状态，然后提取信息，最后跳转
    extracting.value = true
    try {
      await extractPatientInfo()
      // 提取成功后跳转到下一步
      currentStep.value++
    } catch (error: any) {
      // 提取失败，停留在当前步骤
      console.error('提取患者信息失败:', error)
    } finally {
      extracting.value = false
    }
  }
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
    // 验证必需字段
    if (!extractedInfo.value.admission_date) {
      ElMessage.error('缺少入院日期，请重新提取患者信息')
      return
    }

    // 构建请求数据，确保 admission_date 格式正确
    const requestData = {
      hospital_number: form.value.hospital_number,
      name: extractedInfo.value.name || '',
      gender: extractedInfo.value.gender || '',
      age: extractedInfo.value.age || 0,
      admission_date: extractedInfo.value.admission_date, // 确保是 YYYY-MM-DD 格式
      chief_complaint: extractedInfo.value.chief_complaint || '',
      diagnosis: extractedInfo.value.diagnosis || '',
      past_history: extractedInfo.value.past_history || '',
      allergy_history: extractedInfo.value.allergy_history || '',
      specialist_exam: extractedInfo.value.specialist_exam || '',
      initial_note: form.value.initial_note
    }

    console.log('[DEBUG] 发送患者创建请求:', requestData)

    const response = await axios.post('http://127.0.0.1:8000/api/patients/', requestData)

    if (response.data) {
      // 初始化患者提醒
      await initializeReminders(form.value.hospital_number)

      ElMessage.success('患者创建成功')
      emit('success')
      handleClose()
    }
  } catch (error: any) {
    console.error('[ERROR] 创建患者失败:', error.response?.data)
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
  saving.value = false
  checking.value = false
  extracting.value = false
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

.specialist-exam {
  max-height: 200px;
  overflow-y: auto;
  white-space: pre-wrap;
  word-break: break-word;
  line-height: 1.6;
  font-size: 13px;
  padding: 8px;
  background-color: #f5f7fa;
  border-radius: 4px;
}
</style>
