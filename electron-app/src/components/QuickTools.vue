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
      <!-- 1. 基础评估与诊断 -->
      <el-option-group label="📋 基础评估与诊断">
        <el-option label="症状采集" value="基础评估与诊断-症状采集" />
        <el-option label="体格检查" value="基础评估与诊断-体格检查" />
        <el-option label="辅助检查" value="基础评估与诊断-辅助检查" />
        <el-option label="诊断结论" value="基础评估与诊断-诊断结论" />
      </el-option-group>

      <!-- 2. 治疗方案制定 -->
      <el-option-group label="💉 治疗方案制定">
        <el-option label="中医特色治疗" value="治疗方案制定-中医特色治疗" />
        <el-option label="中药治疗" value="治疗方案制定-中药治疗" />
        <el-option label="西药治疗" value="治疗方案制定-西药治疗" />
        <el-option label="康复治疗" value="治疗方案制定-康复治疗" />
        <el-option label="护理操作" value="治疗方案制定-护理操作" />
      </el-option-group>

      <!-- 3. 管理与监测 -->
      <el-option-group label="🔍 管理与监测">
        <el-option label="医嘱与护理" value="管理与监测-医嘱与护理" />
        <el-option label="风险防控" value="管理与监测-风险防控" />
        <el-option label="病情监测" value="管理与监测-病情监测" />
        <el-option label="并发症处理" value="管理与监测-并发症处理" />
      </el-option-group>

      <!-- 4. 医患沟通与记录 -->
      <el-option-group label="💬 医患沟通与记录">
        <el-option label="医患沟通" value="医患沟通与记录-医患沟通" />
        <el-option label="健康宣教" value="医患沟通与记录-健康宣教" />
      </el-option-group>
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

    <!-- 明日提醒 -->
    <div class="tomorrow-reminder-section">
      <h4>明日提醒</h4>
      <el-button
        type="primary"
        size="small"
        :icon="Plus"
        @click="showAddTomorrowReminder"
        style="width: 100%"
      >
        添加明日提醒
      </el-button>
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
import { ref, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
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

// 处理模板更新事件
function handleTemplatesUpdated() {
  if (selectedCategory.value) {
    loadTemplates()
  }
}

// 组件挂载时监听事件
onMounted(() => {
  eventBus.on('templates-updated', handleTemplatesUpdated)
})

// 组件卸载时移除监听
onUnmounted(() => {
  eventBus.off('templates-updated', handleTemplatesUpdated)
})

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

// 显示添加明日提醒对话框
function showAddTomorrowReminder() {
  // 触发事件，让MainView打开明日提醒对话框
  eventBus.emit('show-tomorrow-reminder-dialog')
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

/* 优化分组标签样式 */
.template-selector :deep(.el-select-group__title) {
  font-weight: 600;
  color: #409EFF;
  font-size: 13px;
  padding: 8px 12px;
}

.template-selector :deep(.el-select-group__wrap) {
  padding: 0;
  margin: 0;
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

/* 明日提醒section */
.tomorrow-reminder-section {
  margin-top: 20px;
}

.tomorrow-reminder-section h4 {
  font-size: 14px;
  font-weight: 600;
  color: #666;
  margin-bottom: 12px;
}

/* 自定义滚动条 - 细小美观 */
.quick-tools {
  padding-right: 4px;
}

.quick-tools::-webkit-scrollbar {
  width: 6px;
}

.quick-tools::-webkit-scrollbar-track {
  background: transparent;
}

.quick-tools::-webkit-scrollbar-thumb {
  background: rgba(144, 147, 153, 0.3);
  border-radius: 3px;
  transition: background 0.3s;
}

.quick-tools::-webkit-scrollbar-thumb:hover {
  background: rgba(144, 147, 153, 0.5);
}
</style>
