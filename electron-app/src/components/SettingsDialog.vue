<template>
  <el-dialog
    v-model="visible"
    title="系统设置"
    width="800px"
    @close="handleClose"
  >
    <el-tabs v-model="activeTab" class="settings-tabs">
      <!-- AI服务配置 -->
      <el-tab-pane label="AI服务" name="ai">
        <el-form :model="aiConfig" label-width="120px">
          <el-form-item label="默认服务">
            <el-select v-model="aiConfig.default_service">
              <el-option label="DeepSeek" value="deepseek" />
              <el-option label="ModelScope" value="modelscope" />
              <el-option label="Ollama" value="ollama" />
            </el-select>
            <div class="form-tip">选择默认的AI服务提供商</div>
          </el-form-item>

          <el-divider content-position="left">DeepSeek 配置</el-divider>

          <el-form-item label="API密钥">
            <el-input
              v-model="aiConfig.deepseek_api_key"
              type="password"
              placeholder="请输入DeepSeek API密钥"
              show-password
            />
          </el-form-item>

          <el-form-item label="Base URL">
            <el-input
              v-model="aiConfig.deepseek_base_url"
              placeholder="https://api.deepseek.com/v1"
            />
          </el-form-item>

          <el-form-item label="模型名称">
            <el-input
              v-model="aiConfig.deepseek_model"
              placeholder="deepseek-chat"
            />
          </el-form-item>

          <el-divider content-position="left">ModelScope 配置</el-divider>

          <el-form-item label="API密钥">
            <el-input
              v-model="aiConfig.modelscope_api_key"
              type="password"
              placeholder="请输入ModelScope API密钥"
              show-password
            />
          </el-form-item>

          <el-form-item label="Base URL">
            <el-input
              v-model="aiConfig.modelscope_base_url"
              placeholder="https://api-inference.modelscope.cn/v1"
            />
          </el-form-item>

          <el-form-item label="模型名称">
            <el-input
              v-model="aiConfig.modelscope_model"
              placeholder="deepseek-ai/DeepSeek-V3"
            />
          </el-form-item>

          <el-divider content-position="left">Ollama 配置</el-divider>

          <el-form-item label="Base URL">
            <el-input
              v-model="aiConfig.ollama_base_url"
              placeholder="http://localhost:11434"
            />
          </el-form-item>

          <el-form-item label="模型名称">
            <el-input
              v-model="aiConfig.ollama_model"
              placeholder="llama3.2"
            />
          </el-form-item>
        </el-form>
      </el-tab-pane>

      <!-- 知识库管理 -->
      <el-tab-pane label="知识库" name="knowledge">
        <div class="knowledge-section">
          <div class="section-header">
            <h4>知识库文档</h4>
            <el-button :icon="Upload" type="primary" @click="handleUpload">
              上传文档
            </el-button>
          </div>

          <el-table :data="knowledgeFiles" style="width: 100%">
            <el-table-column prop="name" label="文件名" />
            <el-table-column prop="type" label="类型" width="120" />
            <el-table-column prop="upload_date" label="上传时间" width="180" />
            <el-table-column prop="size" label="大小" width="100" />
            <el-table-column label="操作" width="120">
              <template #default="scope">
                <el-button
                  link
                  type="danger"
                  :icon="Delete"
                  @click="handleDeleteFile(scope.row)"
                >
                  删除
                </el-button>
              </template>
            </el-table-column>
          </el-table>

          <el-empty
            v-if="knowledgeFiles.length === 0"
            description="暂无知识库文档"
            :image-size="80"
          />
        </div>
      </el-tab-pane>

      <!-- 模板管理 -->
      <el-tab-pane label="模板管理" name="templates">
        <div class="template-section">
          <!-- 文件上传和分析 -->
          <div class="upload-section">
            <h4>从病程记录文件提取模板</h4>
            <p class="section-tip">上传包含多人病程记录的.md或.txt文件，AI将自动提取常用语句并分类</p>

            <el-upload
              class="upload-area"
              drag
              :auto-upload="false"
              :on-change="handleFileSelect"
              accept=".md,.txt"
              :show-file-list="false"
            >
              <el-icon :size="60" class="upload-icon"><Upload /></el-icon>
              <div class="upload-text">
                <p>拖拽文件到此处或</p>
                <p class="upload-tip">支持 .md 和 .txt 文件</p>
              </div>
            </el-upload>

            <div v-if="selectedFile" class="selected-file">
              <div class="file-info">
                <span>{{ selectedFile.name }}</span>
                <el-button :icon="Close" circle text @click="clearFile" />
              </div>
              <el-button
                type="primary"
                :icon="MagicStick"
                :loading="analyzing"
                @click="analyzeFile"
                :disabled="!selectedFile"
              >
                AI分析提取
              </el-button>
            </div>
          </div>

          <!-- 分析结果 -->
          <div v-if="extractedPhrases.length > 0" class="analysis-result">
            <el-divider content-position="left">提取结果（可编辑）</el-divider>

            <div class="phrases-list">
              <div
                v-for="(phrase, index) in extractedPhrases"
                :key="index"
                class="phrase-item"
              >
                <div class="phrase-header">
                  <el-tag
                    :type="getCategoryType(phrase.category)"
                    size="small"
                    closable
                    @close="removePhrase(index)"
                  >
                    {{ phrase.category || '未分类' }}
                  </el-tag>
                  <el-button
                    :icon="Delete"
                    size="small"
                    text
                    @click="removePhrase(index)"
                  />
                </div>
                <el-input
                  v-model="phrase.content"
                  type="textarea"
                  :rows="2"
                  placeholder="语句内容"
                />
              </div>
            </div>

            <div class="action-buttons">
              <el-button @click="addNewPhrase">
                <el-icon><Plus /></el-icon>
                添加语句
              </el-button>
              <el-button
                type="primary"
                :icon="Check"
                :loading="saving"
                @click="saveTemplates"
              >
                批量保存为模板
              </el-button>
            </div>
          </div>
        </div>
      </el-tab-pane>

      <!-- 医生信息 -->
      <el-tab-pane label="医生信息" name="doctor">
        <el-form :model="doctorInfo" label-width="120px">
          <el-form-item label="住院医师">
            <el-input v-model="doctorInfo.resident" placeholder="请输入住院医师姓名" />
          </el-form-item>

          <el-form-item label="主治医师">
            <el-input v-model="doctorInfo.attending" placeholder="请输入主治医师姓名" />
          </el-form-item>

          <el-form-item label="主任医师">
            <el-input v-model="doctorInfo.chief" placeholder="请输入主任医师姓名" />
          </el-form-item>
        </el-form>
      </el-tab-pane>

      <!-- 通用设置 -->
      <el-tab-pane label="通用" name="general">
        <el-form label-width="180px">
          <el-form-item label="自动保存病程记录">
            <el-switch v-model="generalSettings.autoSave" />
            <div class="form-tip">生成病程记录后自动保存到数据库</div>
          </el-form-item>

          <el-form-item label="每日自动创建提醒">
            <el-switch v-model="generalSettings.autoReminders" />
            <div class="form-tip">每天自动为住院患者创建病程记录提醒</div>
          </el-form-item>

          <el-form-item label="复制后自动清空">
            <el-switch v-model="generalSettings.clearAfterCopy" />
            <div class="form-tip">复制内容后自动清空输入框</div>
          </el-form-item>

          <el-form-item label="历史记录保留天数">
            <el-input-number
              v-model="generalSettings.historyDays"
              :min="7"
              :max="365"
            />
            <div class="form-tip">系统自动清理超过此天数的历史记录</div>
          </el-form-item>
        </el-form>
      </el-tab-pane>
    </el-tabs>

    <template #footer>
      <span class="dialog-footer">
        <el-button @click="handleClose">取消</el-button>
        <el-button type="primary" :loading="saving" @click="handleSave">保存设置</el-button>
      </span>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, watch, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Upload, Delete, Check, Plus, Close, MagicStick } from '@element-plus/icons-vue'
import axios from 'axios'

const props = defineProps<{
  modelValue: boolean
}>()

const emit = defineEmits(['update:modelValue'])

const visible = ref(props.modelValue)
const activeTab = ref('ai')
const saving = ref(false)

// AI服务配置
const aiConfig = ref({
  default_service: 'deepseek',
  deepseek_api_key: '',
  deepseek_base_url: 'https://api.deepseek.com/v1',
  deepseek_model: 'deepseek-chat',
  modelscope_api_key: '',
  modelscope_base_url: 'https://api-inference.modelscope.cn/v1',
  modelscope_model: 'deepseek-ai/DeepSeek-V3',
  ollama_base_url: 'http://localhost:11434',
  ollama_model: 'llama3.2'
})

// 医生信息
const doctorInfo = ref({
  resident: '',    // 住院医师姓名
  attending: '',   // 主治医师姓名
  chief: ''        // 主任医师姓名
})

// 通用设置
const generalSettings = ref({
  autoSave: true,
  autoReminders: true,
  clearAfterCopy: false,
  historyDays: 90
})

// 知识库文件列表
const knowledgeFiles = ref<any[]>([])

// 模板管理相关
const selectedFile = ref<File | null>(null)
const analyzing = ref(false)
const extractedPhrases = ref<Array<{ content: string; category: string }>>([])

watch(() => props.modelValue, (val) => {
  visible.value = val
  if (val) {
    loadSettings()
  }
})

watch(visible, (val) => {
  emit('update:modelValue', val)
})

onMounted(() => {
  loadSettings()
})

async function loadSettings() {
  try {
    // 加载配置（这里从localStorage读取，实际应该从后端API获取）
    const savedConfig = localStorage.getItem('ai_config')
    if (savedConfig) {
      aiConfig.value = JSON.parse(savedConfig)
    }

    const savedDoctor = localStorage.getItem('doctor_info')
    if (savedDoctor) {
      doctorInfo.value = JSON.parse(savedDoctor)
    }

    const savedGeneral = localStorage.getItem('general_settings')
    if (savedGeneral) {
      generalSettings.value = JSON.parse(savedGeneral)
    }

    // 加载知识库文件列表
    await loadKnowledgeFiles()
  } catch (error) {
    console.error('加载设置失败:', error)
  }
}

async function loadKnowledgeFiles() {
  try {
    const response = await axios.get('http://127.0.0.1:8000/api/knowledge/files')
    knowledgeFiles.value = response.data
  } catch (error) {
    console.error('加载知识库文件失败:', error)
  }
}

async function handleUpload() {
  ElMessage.info('知识库上传功能待实现')
}

async function handleDeleteFile(file: any) {
  try {
    await ElMessageBox.confirm('确定要删除这个文件吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    await axios.delete(`http://127.0.0.1:8000/api/knowledge/files/${file.id}`)
    ElMessage.success('删除成功')
    await loadKnowledgeFiles()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败: ' + (error.response?.data?.detail || error.message))
    }
  }
}

async function handleSave() {
  saving.value = true
  try {
    // 保存AI配置到localStorage
    localStorage.setItem('ai_config', JSON.stringify(aiConfig.value))
    localStorage.setItem('doctor_info', JSON.stringify(doctorInfo.value))
    localStorage.setItem('general_settings', JSON.stringify(generalSettings.value))

    ElMessage.success('设置保存成功')
    handleClose()
  } catch (error: any) {
    ElMessage.error('保存失败: ' + (error.message || '未知错误'))
  } finally {
    saving.value = false
  }
}

function handleClose() {
  visible.value = false
}

// 模板管理相关函数
function handleFileSelect(file: any) {
  selectedFile.value = file.raw
  ElMessage.success(`已选择文件: ${file.name}`)
}

function clearFile() {
  selectedFile.value = null
  extractedPhrases.value = []
}

async function analyzeFile() {
  if (!selectedFile.value) {
    ElMessage.warning('请先选择文件')
    return
  }

  analyzing.value = true
  try {
    // 读取文件内容
    const fileContent = await readFileContent(selectedFile.value)

    // 显示开始处理消息
    ElMessage.info('正在预处理文档，提取高频语句...')

    // 调用后端AI分析API
    const response = await axios.post('http://127.0.0.1:8000/api/templates/extract-phrases', {
      content: fileContent,
      filename: selectedFile.value.name
    })

    if (response.data.success) {
      extractedPhrases.value = response.data.phrases || []

      // 显示详细处理信息
      if (response.data.message) {
        ElMessage.success(response.data.message)
      } else {
        ElMessage.success(`成功提取并优化了 ${extractedPhrases.value.length} 条语句`)
      }
    }
  } catch (error: any) {
    console.error('AI分析失败:', error)
    ElMessage.error('分析失败: ' + (error.response?.data?.detail || error.message))
  } finally {
    analyzing.value = false
  }
}

function readFileContent(file: File): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onload = (e) => {
      resolve(e.target?.result as string)
    }
    reader.onerror = reject
    reader.readAsText(file, 'UTF-8')
  })
}

function getCategoryType(category: string): string {
  const categoryMap: Record<string, string> = {
    '症状描述': '',
    '检查结果': 'success',
    '治疗方案': 'warning',
    '康复训练': 'danger',
    '护理事项': 'info',
    '病情变化': 'warning',
    '用药记录': 'info'
  }
  return categoryMap[category] || ''
}

function addNewPhrase() {
  extractedPhrases.value.push({
    content: '',
    category: '未分类'
  })
}

function removePhrase(index: number) {
  extractedPhrases.value.splice(index, 1)
}

async function saveTemplates() {
  if (extractedPhrases.value.length === 0) {
    ElMessage.warning('没有可保存的模板')
    return
  }

  saving.value = true
  try {
    // 过滤掉空内容的语句
    const validPhrases = extractedPhrases.value.filter(p => p.content.trim())

    if (validPhrases.length === 0) {
      ElMessage.warning('请至少填写一条语句内容')
      return
    }

    // 批量保存模板
    await axios.post('http://127.0.0.1:8000/api/templates/batch', {
      phrases: validPhrases
    })

    ElMessage.success(`成功保存 ${validPhrases.length} 条模板`)
    // 清空提取结果
    extractedPhrases.value = []
    selectedFile.value = null
  } catch (error: any) {
    console.error('保存失败:', error)
    ElMessage.error('保存失败: ' + (error.response?.data?.detail || error.message))
  } finally {
    saving.value = false
  }
}
</script>

<style scoped>
.settings-tabs {
  min-height: 400px;
}

.form-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
  line-height: 1.4;
}

.knowledge-section {
  padding: 10px 0;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.section-header h4 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #333;
}

:deep(.el-form-item__label) {
  font-weight: 500;
}

:deep(.el-divider__text) {
  font-weight: 600;
  color: #409EFF;
}

:deep(.el-input-number) {
  width: 200px;
}

:deep(.el-select) {
  width: 100%;
}

.template-section {
  padding: 10px 0;
}

.upload-section {
  margin-bottom: 20px;
}

.upload-section h4 {
  margin: 0 0 8px 0;
  font-size: 15px;
  font-weight: 600;
  color: #333;
}

.section-tip {
  margin: 0 0 12px 0;
  font-size: 13px;
  color: #666;
  line-height: 1.5;
}

.upload-area {
  margin-bottom: 12px;
}

.upload-icon {
  color: #409EFF;
}

.upload-text p {
  margin: 8px 0 0 0;
  font-size: 14px;
  color: #333;
}

.upload-tip {
  font-size: 12px;
  color: #909399;
}

.selected-file {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px;
  background: #F5F7FA;
  border-radius: 8px;
  margin-top: 12px;
}

.file-info {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
}

.file-info span {
  font-size: 13px;
  color: #333;
}

.analysis-result {
  margin-top: 20px;
}

.phrases-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 16px;
}

.phrase-item {
  border: 1px solid #DCDFE6;
  border-radius: 8px;
  padding: 12px;
  background: #FAFAFA;
}

.phrase-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
}

.action-buttons {
  display: flex;
  gap: 12px;
}

:deep(.el-upload-dragger) {
  width: 100%;
  min-height: 120px;
}
</style>
