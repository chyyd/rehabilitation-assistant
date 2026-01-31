<template>
  <el-dialog
    v-model="visible"
    title="常用短语管理"
    width="600px"
    @close="handleClose"
  >
    <div class="manage-phrases">
      <!-- 添加新短语 -->
      <div class="add-phrase-section">
        <el-input
          v-model="newPhrase"
          placeholder="输入新的常用短语..."
          @keyup.enter="addPhrase"
        >
          <template #append>
            <el-button :icon="Plus" @click="addPhrase">添加</el-button>
          </template>
        </el-input>
      </div>

      <!-- 短语列表 -->
      <div class="phrases-list">
        <el-empty
          v-if="phrases.length === 0"
          description="暂无常用短语"
          :image-size="100"
        />
        <div
          v-for="(phrase, index) in phrases"
          :key="index"
          class="phrase-item"
        >
          <span class="phrase-text">{{ phrase }}</span>
          <div class="phrase-actions">
            <el-button
              link
              type="primary"
              size="small"
              @click="editPhrase(index)"
            >
              编辑
            </el-button>
            <el-button
              link
              type="danger"
              size="small"
              @click="deletePhrase(index)"
            >
              删除
            </el-button>
          </div>
        </div>
      </div>
    </div>

    <template #footer>
      <span class="dialog-footer">
        <el-button @click="handleClose">关闭</el-button>
      </span>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'

const props = defineProps<{
  modelValue: boolean
}>()

const emit = defineEmits(['update:modelValue', 'saved'])

const visible = ref(props.modelValue)
const phrases = ref<string[]>([])
const newPhrase = ref('')

watch(() => props.modelValue, (val) => {
  visible.value = val
  if (val) {
    loadPhrases()
  }
})

watch(visible, (val) => {
  emit('update:modelValue', val)
})

// 加载常用短语
function loadPhrases() {
  const saved = localStorage.getItem('common_phrases')
  if (saved) {
    try {
      phrases.value = JSON.parse(saved)
    } catch (e) {
      console.error('加载常用短语失败:', e)
      phrases.value = []
    }
  } else {
    phrases.value = []
  }
}

// 保存常用短语
function savePhrases() {
  localStorage.setItem('common_phrases', JSON.stringify(phrases.value))
  emit('saved')
}

// 添加短语
function addPhrase() {
  const text = newPhrase.value.trim()
  if (!text) {
    ElMessage.warning('请输入短语内容')
    return
  }

  if (phrases.value.includes(text)) {
    ElMessage.warning('该短语已存在')
    return
  }

  phrases.value.push(text)
  savePhrases()
  newPhrase.value = ''
  ElMessage.success('添加成功')
}

// 编辑短语
function editPhrase(index: number) {
  ElMessageBox.prompt('请输入新的短语内容', '编辑短语', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    inputValue: phrases.value[index],
    inputPattern: /\S+/,
    inputErrorMessage: '短语内容不能为空'
  }).then(({ value }) => {
    const trimmed = value.trim()
    if (phrases.value.includes(trimmed) && phrases.value[index] !== trimmed) {
      ElMessage.warning('该短语已存在')
      return
    }
    phrases.value[index] = trimmed
    savePhrases()
    ElMessage.success('修改成功')
  }).catch(() => {
    // 用户取消
  })
}

// 删除短语
function deletePhrase(index: number) {
  ElMessageBox.confirm('确定要删除这条短语吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    phrases.value.splice(index, 1)
    savePhrases()
    ElMessage.success('删除成功')
  }).catch(() => {
    // 用户取消
  })
}

function handleClose() {
  visible.value = false
  newPhrase.value = ''
}
</script>

<style scoped>
.manage-phrases {
  padding: 10px 0;
}

.add-phrase-section {
  margin-bottom: 20px;
}

.phrases-list {
  max-height: 400px;
  overflow-y: auto;
}

.phrase-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  margin-bottom: 8px;
  background: #F5F7FA;
  border-radius: 8px;
  transition: all 0.2s;
}

.phrase-item:hover {
  background: #E6F7FF;
}

.phrase-text {
  flex: 1;
  font-size: 14px;
  color: #333;
  margin-right: 12px;
}

.phrase-actions {
  display: flex;
  gap: 8px;
}

/* 自定义滚动条 */
.phrases-list::-webkit-scrollbar {
  width: 6px;
}

.phrases-list::-webkit-scrollbar-track {
  background: transparent;
}

.phrases-list::-webkit-scrollbar-thumb {
  background: rgba(144, 147, 153, 0.3);
  border-radius: 3px;
  transition: background 0.3s;
}

.phrases-list::-webkit-scrollbar-thumb:hover {
  background: rgba(144, 147, 153, 0.5);
}
</style>
