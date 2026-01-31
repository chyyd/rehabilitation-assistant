<template>
  <div class="quick-tools">
    <h3 class="tools-title">快速模板</h3>

    <!-- 模板类别选择 -->
    <el-select
      v-model="selectedCategory"
      placeholder="选择模板类别"
      class="template-selector"
      @change="loadTemplates"
    >
      <el-option label="诊断模板" value="diagnosis" />
      <el-option label="处理意见" value="treatment" />
      <el-option label="宣教内容" value="education" />
    </el-select>

    <!-- 模板列表 -->
    <div v-if="selectedCategory && templates.length > 0" class="templates-section">
      <h4>模板列表</h4>
      <div
        v-for="template in templates"
        :key="template.id"
        class="template-item"
        @click="useTemplate(template)"
      >
        <div class="template-name">{{ template.template_name }}</div>
        <div class="template-content">{{ template.content }}</div>
      </div>
    </div>

    <!-- 常用短语 -->
    <div class="phrases-section">
      <h4>常用短语</h4>
      <div
        v-for="phrase in commonPhrases"
        :key="phrase"
        class="phrase-item"
        @click="insertPhrase(phrase)"
      >
        {{ phrase }}
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'
import { eventBus } from '@/utils/eventBus'

const selectedCategory = ref('')
const templates = ref<any[]>([])

const commonPhrases = ref([
  '患者神志清，精神可',
  '继续康复训练',
  '家属配合',
  '查体同前',
  '生命体征平稳',
  '无明显不适',
  '肢体功能较前改善',
  '伤口敷料干燥',
  '无特殊不适主诉',
  '饮食睡眠尚可'
])

// 加载模板
async function loadTemplates() {
  if (!selectedCategory.value) {
    templates.value = []
    return
  }

  try {
    const response = await axios.get('http://127.0.0.1:8000/api/templates/', {
      params: { category: selectedCategory.value }
    })

    templates.value = response.data

    if (templates.value.length === 0) {
      ElMessage.info('该分类暂无模板')
    }
  } catch (error: any) {
    ElMessage.error('加载模板失败: ' + (error.response?.data?.detail || error.message))
  }
}

// 使用模板
async function useTemplate(template: any) {
  // 复制到剪贴板
  navigator.clipboard.writeText(template.content).then(() => {
    ElMessage.success('已复制到剪贴板')

    // 增加使用次数
    incrementTemplateUsage(template.id)
  }).catch(() => {
    ElMessage.error('复制失败')
  })
}

// 增加模板使用次数
async function incrementTemplateUsage(templateId: number) {
  try {
    await axios.post(`http://127.0.0.1:8000/api/templates/${templateId}/use`)
  } catch (error) {
    // 静默失败，不影响用户体验
    console.error('更新模板使用次数失败:', error)
  }
}

// 插入常用短语
function insertPhrase(phrase: string) {
  // 触发事件，让NoteGenerationCard接收
  eventBus.emit('insert-phrase', phrase)
  ElMessage.success('已插入到当日情况')
}
</script>

<style scoped>
.quick-tools {
  height: 100%;
  overflow-y: auto;
}

.tools-title {
  font-size: 16px;
  font-weight: 600;
  color: #333;
  margin-bottom: 16px;
}

.template-selector {
  width: 100%;
  margin-bottom: 20px;
}

.templates-section {
  margin-bottom: 20px;
}

.templates-section h4 {
  font-size: 14px;
  font-weight: 600;
  color: #666;
  margin-bottom: 12px;
}

.template-item {
  background: white;
  padding: 10px 12px;
  margin-bottom: 10px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  border: 1px solid #E5E5EA;
}

.template-item:hover {
  background: #F0F9FF;
  border-color: #007AFF;
}

.template-name {
  font-size: 13px;
  font-weight: 600;
  color: #333;
  margin-bottom: 6px;
}

.template-content {
  font-size: 12px;
  color: #666;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.phrases-section {
  margin-top: 20px;
}

.phrases-section h4 {
  font-size: 14px;
  font-weight: 600;
  color: #666;
  margin-bottom: 12px;
}

.phrase-item {
  background: white;
  padding: 8px 12px;
  margin-bottom: 8px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 13px;
  color: #333;
  border: 1px solid #E5E5EA;
}

.phrase-item:hover {
  background: #E5E5EA;
  border-color: #007AFF;
}
</style>
