<template>
  <el-card class="note-card" shadow="never">
    <template #header>
      <span class="card-title">病程记录生成</span>
    </template>

    <div class="note-toolbar">
      <el-button :icon="Document" @click="showHistoryDialog">查看历史</el-button>
      <el-button :icon="Search">搜索资料</el-button>
    </div>

    <div class="form-section">
      <label>记录类型：</label>
      <el-select v-model="recordType" class="record-type-selector">
        <el-option label="住院医师查房" value="住院医师查房" />
        <el-option label="主治医师查房" value="主治医师查房" />
        <el-option label="主任医师查房" value="主任医师查房" />
        <el-option label="阶段小结" value="阶段小结" />
      </el-select>
    </div>

    <div class="form-section">
      <label>当日情况：</label>
      <el-input
        v-model="dailyCondition"
        type="textarea"
        :rows="4"
        placeholder="请输入患者今日情况..."
      />
    </div>

    <div class="action-buttons">
      <el-button
        type="primary"
        :icon="MagicStick"
        :loading="generating"
        @click="handleGenerate"
      >
        AI生成
      </el-button>
      <el-button :icon="DocumentCopy" @click="handleSave">保存</el-button>
      <el-button :icon="Download" @click="handleExport">导出txt</el-button>
    </div>

    <div class="preview-section">
      <label>AI生成预览：</label>
      <el-input
        v-model="generatedContent"
        type="textarea"
        :rows="8"
        placeholder="AI生成的病程记录将显示在这里..."
      />
    </div>

    <!-- 历史记录对话框 -->
    <el-dialog
      v-model="historyDialogVisible"
      title="历史病程记录"
      width="700px"
    >
      <div v-loading="loadingHistory">
        <el-timeline v-if="historyNotes.length > 0">
          <el-timeline-item
            v-for="note in historyNotes"
            :key="note.id"
            :timestamp="formatDate(note.record_date)"
            placement="top"
          >
            <el-card>
              <template #header>
                <div class="history-header">
                  <span>第{{ note.day_number }}天 - {{ note.record_type }}</span>
                  <el-tag v-if="note.is_edited" type="warning" size="small">已编辑</el-tag>
                </div>
              </template>
              <div class="history-content">
                <div class="history-section">
                  <strong>当日情况：</strong>
                  <p>{{ note.daily_condition }}</p>
                </div>
                <div class="history-section">
                  <strong>病程记录：</strong>
                  <p>{{ note.generated_content }}</p>
                </div>
              </div>
            </el-card>
          </el-timeline-item>
        </el-timeline>
        <el-empty v-else description="暂无历史记录" />
      </div>
    </el-dialog>
  </el-card>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { Document, Search, MagicStick, DocumentCopy, Download } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'
import { eventBus } from '@/utils/eventBus'

interface Props {
  patient: any
}

const props = defineProps<Props>()

const dailyCondition = ref('')
const recordType = ref('住院医师查房')
const generatedContent = ref('')
const generating = ref(false)
const historyDialogVisible = ref(false)
const historyNotes = ref<any[]>([])
const loadingHistory = ref(false)

async function handleGenerate() {
  if (!dailyCondition.value.trim()) {
    ElMessage.warning('请输入当日情况')
    return
  }

  generating.value = true
  try {
    // 读取医生信息
    const doctorInfoStr = localStorage.getItem('doctor_info')
    const doctorInfo = doctorInfoStr ? JSON.parse(doctorInfoStr) : null

    const response = await axios.post('http://127.0.0.1:8000/api/ai/generate-note', {
      hospital_number: props.patient.hospital_number,
      daily_condition: dailyCondition.value,
      record_type: recordType.value,
      doctor_info: doctorInfo  // 传递医生信息
    })

    if (response.data.success) {
      generatedContent.value = response.data.data.content
      ElMessage.success('生成成功')
    }
  } catch (error: any) {
    ElMessage.error('生成失败: ' + (error.response?.data?.detail || error.message))
  } finally {
    generating.value = false
  }
}

async function handleSave() {
  if (!generatedContent.value.trim()) {
    ElMessage.warning('请先生成病程记录')
    return
  }

  try {
    const response = await axios.post('http://127.0.0.1:8000/api/notes/', {
      hospital_number: props.patient.hospital_number,
      record_date: new Date().toISOString().split('T')[0],
      record_type: '住院医师查房',
      daily_condition: dailyCondition.value,
      generated_content: generatedContent.value
    })

    if (response.data) {
      ElMessage.success('保存成功')
      // 清空输入
      dailyCondition.value = ''
      generatedContent.value = ''
    }
  } catch (error: any) {
    ElMessage.error('保存失败: ' + (error.response?.data?.detail || error.message))
  }
}

function handleExport() {
  if (!generatedContent.value.trim()) {
    ElMessage.warning('请先生成病程记录')
    return
  }

  // 创建文本文件并下载
  const blob = new Blob([generatedContent.value], { type: 'text/plain;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `病程记录_${props.patient.hospital_number}_${new Date().toLocaleDateString('zh-CN')}.txt`
  link.click()
  URL.revokeObjectURL(url)

  ElMessage.success('导出成功')
}

async function showHistoryDialog() {
  historyDialogVisible.value = true
  loadingHistory.value = true

  try {
    const response = await axios.get(
      `http://127.0.0.1:8000/api/notes/patient/${props.patient.hospital_number}`
    )
    historyNotes.value = response.data
  } catch (error: any) {
    ElMessage.error('加载历史记录失败: ' + (error.response?.data?.detail || error.message))
  } finally {
    loadingHistory.value = false
  }
}

function formatDate(dateStr: string) {
  return new Date(dateStr).toLocaleDateString('zh-CN')
}

// 定义插入短语的回调函数
function insertPhraseHandler(phrase: string) {
  // 如果当前已有内容，在后面追加
  if (dailyCondition.value.trim()) {
    dailyCondition.value += '，' + phrase
  } else {
    dailyCondition.value = phrase
  }
}

// 组件挂载时监听事件
onMounted(() => {
  eventBus.on('insert-phrase', insertPhraseHandler)
})

// 组件卸载时取消监听
onUnmounted(() => {
  eventBus.off('insert-phrase', insertPhraseHandler)
})
</script>

<style scoped>
.note-card {
  border-radius: 12px;
  border: none;
}

.note-card :deep(.el-card__header) {
  padding: 12px 16px;
  border-bottom: 1px solid #E5E5EA;
}

.card-title {
  font-size: 16px;
  font-weight: 600;
  color: #333;
}

.note-toolbar {
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
}

.form-section, .preview-section {
  margin-bottom: 16px;
}

.form-section label, .preview-section label {
  display: block;
  font-size: 13px;
  font-weight: 500;
  color: #666;
  margin-bottom: 8px;
}

.action-buttons {
  display: flex;
  gap: 8px;
}

.record-type-selector {
  width: 100%;
}

/* 历史记录对话框样式 */
.history-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.history-content {
  font-size: 13px;
}

.history-section {
  margin-bottom: 12px;
}

.history-section:last-child {
  margin-bottom: 0;
}

.history-section strong {
  color: #333;
  display: block;
  margin-bottom: 6px;
}

.history-section p {
  color: #666;
  line-height: 1.6;
  margin: 0;
  white-space: pre-wrap;
}
</style>
