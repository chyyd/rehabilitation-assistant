<template>
  <div class="quick-tools">
    <h3 class="tools-title">快速工具</h3>

    <!-- 明日提醒 -->
    <div class="tomorrow-reminder-section">
      <el-button
        type="primary"
        size="small"
        :icon="Plus"
        @click="showAddTomorrowReminder"
        style="width: 100%"
      >
        添加提醒
      </el-button>
    </div>

    <!-- 常用短语 -->
    <div class="phrases-section">
      <div class="section-header">
        <h4>常用短语</h4>
        <el-button
          link
          type="primary"
          size="small"
          @click="showManagePhrases"
        >
          管理
        </el-button>
      </div>
      <div
        v-for="phrase in commonPhrases"
        :key="phrase"
        class="phrase-item"
        @click="insertPhrase(phrase)"
      >
        {{ phrase }}
      </div>
      <el-empty
        v-if="commonPhrases.length === 0"
        description="暂无常用短语"
        :image-size="80"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { eventBus } from '@/utils/eventBus'

// 从 localStorage 加载常用短语
const commonPhrases = ref<string[]>([])

// 组件挂载时加载常用短语
onMounted(() => {
  loadPhrases()
})

// 加载常用短语
function loadPhrases() {
  const saved = localStorage.getItem('common_phrases')
  if (saved) {
    try {
      commonPhrases.value = JSON.parse(saved)
    } catch (e) {
      console.error('加载常用短语失败:', e)
      commonPhrases.value = getDefaultPhrases()
      savePhrases()
    }
  } else {
    // 首次加载，使用默认短语并保存到 localStorage
    commonPhrases.value = getDefaultPhrases()
    savePhrases()
  }
}

// 保存常用短语到 localStorage
function savePhrases() {
  localStorage.setItem('common_phrases', JSON.stringify(commonPhrases.value))
}

// 获取默认常用短语
function getDefaultPhrases(): string[] {
  return [
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
  ]
}

// 插入常用短语
function insertPhrase(phrase: string) {
  eventBus.emit('insert-phrase', phrase)
  ElMessage.success('已插入到当日情况')
}

// 显示管理常用短语对话框
function showManagePhrases() {
  eventBus.emit('show-manage-phrases-dialog')
}

// 显示添加明日提醒对话框
function showAddTomorrowReminder() {
  eventBus.emit('show-tomorrow-reminder-dialog')
}

// 暴露刷新方法，供外部调用
defineExpose({
  loadPhrases
})
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

/* 明日提醒section */
.tomorrow-reminder-section {
  margin-bottom: 20px;
}

/* 常用短语section */
.phrases-section {
  margin-bottom: 20px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.section-header h4 {
  font-size: 14px;
  font-weight: 600;
  color: #666;
  margin: 0;
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
