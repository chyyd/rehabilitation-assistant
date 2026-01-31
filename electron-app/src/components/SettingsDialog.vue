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
        <el-form :model="aiConfig" label-width="140px">
          <el-form-item label="默认服务">
            <el-select v-model="aiConfig.default_service" @change="handleServiceChange">
              <el-option label="DeepSeek" value="deepseek" />
              <el-option label="ModelScope" value="modelscope" />
              <el-option label="Kimi" value="kimi" />
              <el-option label="自定义" value="custom" />
            </el-select>
            <div class="form-tip">选择默认的AI服务提供商</div>
          </el-form-item>

          <!-- DeepSeek 配置 -->
          <div v-if="aiConfig.default_service === 'deepseek' || aiConfig.default_service === 'modelscope' || aiConfig.default_service === 'kimi'">
            <el-divider content-position="left">
              {{ getServiceLabel(aiConfig.default_service) }} 配置
            </el-divider>

            <el-form-item label="API密钥">
              <el-input
                v-model="aiConfig[`${aiConfig.default_service}_api_key`]"
                type="password"
                :placeholder="`请输入${getServiceLabel(aiConfig.default_service)} API密钥`"
                show-password
              />
            </el-form-item>

            <el-form-item label="Base URL">
              <el-input
                v-model="aiConfig[`${aiConfig.default_service}_base_url`]"
                :placeholder="getDefaultBaseUrl(aiConfig.default_service)"
              />
            </el-form-item>

            <el-form-item label="模型名称">
              <el-input
                v-model="aiConfig[`${aiConfig.default_service}_model`]"
                :placeholder="getDefaultModel(aiConfig.default_service)"
              />
            </el-form-item>

            <el-form-item>
              <el-button type="primary" @click="testAIService" :loading="testing">
                <el-icon><MagicStick /></el-icon>
                测试连接
              </el-button>
            </el-form-item>
          </div>

          <!-- 自定义服务配置 -->
          <div v-if="aiConfig.default_service === 'custom'">
            <el-divider content-position="left">自定义服务配置</el-divider>

            <el-form-item label="服务名称">
              <el-input
                v-model="aiConfig.custom_name"
                placeholder="例如：我的AI服务"
              />
            </el-form-item>

            <el-form-item label="API密钥">
              <el-input
                v-model="aiConfig.custom_api_key"
                type="password"
                placeholder="请输入API密钥"
                show-password
              />
            </el-form-item>

            <el-form-item label="Base URL">
              <el-input
                v-model="aiConfig.custom_base_url"
                placeholder="https://api.example.com/v1"
              />
            </el-form-item>

            <el-form-item label="模型名称">
              <el-input
                v-model="aiConfig.custom_model"
                placeholder="model-name"
              />
            </el-form-item>

            <el-form-item>
              <el-button type="primary" @click="testAIService" :loading="testing">
                <el-icon><MagicStick /></el-icon>
                测试连接
              </el-button>
            </el-form-item>
          </div>

          <el-divider content-position="left">嵌入式模型设置</el-divider>

          <el-form-item label="Embedding服务">
            <el-select v-model="aiConfig.embedding_service">
              <el-option label="硅基流动" value="siliconflow" />
              <el-option label="ModelScope" value="modelscope_embed" />
              <el-option label="自定义" value="custom_embed" />
            </el-select>
            <div class="form-tip">用于知识库向量化</div>
          </el-form-item>

          <!-- 硅基流动配置 -->
          <div v-if="aiConfig.embedding_service === 'siliconflow'">
            <el-form-item label="API密钥">
              <el-input
                v-model="aiConfig.siliconflow_api_key"
                type="password"
                placeholder="请输入硅基流动API密钥"
                show-password
              />
            </el-form-item>

            <el-form-item label="Base URL">
              <el-input
                v-model="aiConfig.siliconflow_base_url"
                placeholder="https://api.siliconflow.cn/v1"
              />
            </el-form-item>

            <el-form-item label="模型名称">
              <el-input
                v-model="aiConfig.siliconflow_model"
                placeholder="BAAI/bge-large-zh-v1.5"
              />
            </el-form-item>
          </div>

          <!-- ModelScope Embedding配置 -->
          <div v-if="aiConfig.embedding_service === 'modelscope_embed'">
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
                v-model="aiConfig.modelscope_embed_model"
                placeholder="BAAI/bge-large-zh-v1.5"
              />
            </el-form-item>
          </div>

          <!-- 自定义Embedding配置 -->
          <div v-if="aiConfig.embedding_service === 'custom_embed'">
            <el-form-item label="API密钥">
              <el-input
                v-model="aiConfig.custom_embed_api_key"
                type="password"
                placeholder="请输入API密钥"
                show-password
              />
            </el-form-item>

            <el-form-item label="Base URL">
              <el-input
                v-model="aiConfig.custom_embed_base_url"
                placeholder="https://api.example.com/v1"
              />
            </el-form-item>

            <el-form-item label="模型名称">
              <el-input
                v-model="aiConfig.custom_embed_model"
                placeholder="embedding-model"
              />
            </el-form-item>
          </div>

          <el-form-item>
            <el-button @click="testEmbeddingService" :loading="testingEmbed">
              <el-icon><MagicStick /></el-icon>
              测试Embedding
            </el-button>
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
      <el-tab-pane label="提取模板" name="templates">
        <div class="template-section">
          <!-- 文件上传和分析 -->
          <div class="upload-section">
            <h4>从病程记录文件提取模板</h4>
            <p class="section-tip">支持批量上传多个.md或.txt文件，AI将自动提取常用语句并分类</p>

            <el-upload
              class="upload-area"
              drag
              multiple
              :auto-upload="false"
              :on-change="handleFileSelect"
              :on-remove="handleFileRemove"
              accept=".md,.txt"
              :file-list="fileList"
            >
              <el-icon :size="60" class="upload-icon"><Upload /></el-icon>
              <div class="upload-text">
                <p>拖拽文件到此处或点击上传</p>
                <p class="upload-tip">支持多文件上传，仅支持 .md 和 .txt 文件</p>
              </div>
            </el-upload>

            <!-- 已选文件列表 -->
            <div v-if="selectedFiles.length > 0" class="selected-files-section">
              <div class="files-header">
                <span class="files-count">已选择 {{ selectedFiles.length }} 个文件</span>
                <el-button link type="danger" size="small" @click="clearFiles">清空全部</el-button>
              </div>

              <!-- 紧凑的文件列表 -->
              <div class="files-list-compact">
                <el-tag
                  v-for="(file, index) in selectedFiles"
                  :key="index"
                  closable
                  @close="removeFile(index)"
                  :type="getFileStatusType(file.name)"
                  class="file-tag"
                  size="default"
                >
                  <el-icon class="tag-icon"><Document /></el-icon>
                  {{ file.name }}
                  <span class="file-size-tiny">({{ formatFileSize(file.size) }})</span>
                  <span v-if="fileStatus[file.name]" class="file-status">
                    {{ fileStatus[file.name] === 'analyzing' ? '⏳' : fileStatus[file.name] === 'done' ? '✓' : '✗' }}
                  </span>
                </el-tag>
              </div>

              <!-- 分析进度 -->
              <div v-if="analyzing" class="progress-section">
                <el-progress
                  :percentage="analysisProgress.percentage"
                  :format="() => analysisProgress.current"
                  :stroke-width="20"
                  :status="analysisProgress.status"
                />
                <div class="progress-info">
                  <span>正在分析: {{ analysisProgress.currentFile }}</span>
                  <span>{{ analysisProgress.completed }}/{{ analysisProgress.total }}</span>
                </div>
              </div>

              <el-button
                type="primary"
                :icon="MagicStick"
                :loading="analyzing"
                :disabled="analyzing"
                @click="analyzeAllFiles"
                size="large"
                class="analyze-button"
              >
                {{ analyzing ? `分析中... (${analysisProgress.completed}/${analysisProgress.total})` : `一键分析所有文件 (${selectedFiles.length})` }}
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
import { Upload, Delete, Check, Plus, Close, MagicStick, Document } from '@element-plus/icons-vue'
import axios from 'axios'
import { eventBus } from '@/utils/eventBus'

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

  // DeepSeek配置
  deepseek_api_key: '',
  deepseek_base_url: 'https://api.deepseek.com/v1',
  deepseek_model: 'deepseek-chat',

  // ModelScope配置
  modelscope_api_key: '',
  modelscope_base_url: 'https://api-inference.modelscope.cn/v1',
  modelscope_model: 'deepseek-ai/DeepSeek-V3',

  // Kimi配置
  kimi_api_key: '',
  kimi_base_url: 'https://api.moonshot.cn/v1',
  kimi_model: 'moonshot-v1-8k',

  // 自定义服务配置
  custom_name: '',
  custom_api_key: '',
  custom_base_url: '',
  custom_model: '',

  // 嵌入式模型配置
  embedding_service: 'siliconflow',

  // 硅基流动
  siliconflow_api_key: '',
  siliconflow_base_url: 'https://api.siliconflow.cn/v1',
  siliconflow_model: 'BAAI/bge-large-zh-v1.5',

  // ModelScope Embedding
  modelscope_embed_model: 'BAAI/bge-large-zh-v1.5',

  // 自定义Embedding
  custom_embed_api_key: '',
  custom_embed_base_url: '',
  custom_embed_model: ''
})

// 测试状态
const testing = ref(false)
const testingEmbed = ref(false)

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
const selectedFiles = ref<File[]>([])
const fileList = ref<any[]>([])
const analyzing = ref(false)
const analyzingFileName = ref('')
const fileStatus = ref<Record<string, 'pending' | 'analyzing' | 'done' | 'failed'>>({})
const analysisProgress = ref({
  percentage: 0,
  current: '',
  currentFile: '',
  completed: 0,
  total: 0,
  status: '' as any
})
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

    // 同步AI配置到后端
    try {
      // 构建后端期望的服务配置格式
      const servicesConfig: any = {}

      // DeepSeek配置
      if (aiConfig.value.deepseek_api_key) {
        servicesConfig.deepseek = {
          api_key: aiConfig.value.deepseek_api_key,
          model: aiConfig.value.deepseek_model || 'deepseek-chat',
          is_default: aiConfig.value.default_service === 'deepseek'
        }
      }

      // ModelScope配置
      if (aiConfig.value.modelscope_api_key) {
        servicesConfig.modelscope = {
          api_key: aiConfig.value.modelscope_api_key,
          model: aiConfig.value.modelscope_model || 'deepseek-ai/DeepSeek-V3',
          is_default: aiConfig.value.default_service === 'modelscope'
        }
      }

      // Kimi配置
      if (aiConfig.value.kimi_api_key) {
        servicesConfig.kimi = {
          api_key: aiConfig.value.kimi_api_key,
          model: aiConfig.value.kimi_model || 'moonshot-v1-8k',
          is_default: aiConfig.value.default_service === 'kimi'
        }
      }

      // 自定义配置
      if (aiConfig.value.custom_api_key && aiConfig.value.custom_name) {
        servicesConfig.custom = {
          api_key: aiConfig.value.custom_api_key,
          model: aiConfig.value.custom_model || 'custom-model',
          is_default: aiConfig.value.default_service === 'custom'
        }
      }

      // 调用后端API更新配置
      await axios.post('http://127.0.0.1:8000/api/ai/update-config', {
        default_service: aiConfig.value.default_service,
        services: servicesConfig
      })
    } catch (error) {
      console.error('后端AI配置更新失败:', error)
      // 不阻断保存流程，继续保存到localStorage
    }

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
  // 检查文件类型
  const validTypes = ['text/markdown', 'text/plain', 'md', 'txt']
  const fileExtension = file.name.split('.').pop()?.toLowerCase()

  if (fileExtension !== 'md' && fileExtension !== 'txt') {
    ElMessage.error('只支持 .md 和 .txt 文件')
    return
  }

  // 检查是否已存在
  const exists = selectedFiles.value.some(f => f.name === file.name)
  if (exists) {
    ElMessage.warning(`文件 ${file.name} 已存在`)
    return
  }

  // 添加到已选文件列表
  selectedFiles.value.push(file.raw)
  fileList.value.push({
    name: file.name,
    size: file.size,
    raw: file.raw
  })

  ElMessage.success(`已添加文件: ${file.name}`)
}

function handleFileRemove(file: any) {
  const index = selectedFiles.value.findIndex(f => f.name === file.name)
  if (index > -1) {
    selectedFiles.value.splice(index, 1)
    fileList.value = fileList.value.filter(f => f.name !== file.name)
  }
}

function removeFile(index: number) {
  const file = selectedFiles.value[index]
  selectedFiles.value.splice(index, 1)
  fileList.value = fileList.value.filter(f => f.name !== file.name)
  // 删除状态
  if (fileStatus.value[file.name]) {
    delete fileStatus.value[file.name]
  }
  ElMessage.info(`已移除文件: ${file.name}`)
}

function clearFiles() {
  selectedFiles.value = []
  fileList.value = []
  extractedPhrases.value = []
  fileStatus.value = {}
  analysisProgress.value = {
    percentage: 0,
    current: '',
    currentFile: '',
    completed: 0,
    total: 0,
    status: ''
  }
  ElMessage.info('已清空所有文件')
}

function getFileStatusType(filename: string): string {
  const status = fileStatus.value[filename]
  const typeMap: Record<string, string> = {
    'analyzing': 'warning',
    'done': 'success',
    'failed': 'danger'
  }
  return typeMap[status] || 'info'
}

async function analyzeAllFiles() {
  if (selectedFiles.value.length === 0) {
    ElMessage.warning('请先选择文件')
    return
  }

  analyzing.value = true
  const allPhrases: Array<{ content: string; category: string }> = []
  let successCount = 0
  let failCount = 0
  const total = selectedFiles.value.length

  // 初始化进度
  analysisProgress.value = {
    percentage: 0,
    current: '0%',
    currentFile: '',
    completed: 0,
    total: total,
    status: ''
  }

  try {
    ElMessage.info(`开始分析 ${total} 个文件...`)

    // 逐个分析文件
    for (let i = 0; i < total; i++) {
      const file = selectedFiles.value[i]
      analyzingFileName.value = file.name

      // 更新进度
      analysisProgress.value.completed = i
      analysisProgress.value.currentFile = file.name
      analysisProgress.value.percentage = Math.round((i / total) * 100)
      analysisProgress.value.current = `${Math.round((i / total) * 100)}%`
      analysisProgress.value.status = 'warning'

      // 标记为分析中
      fileStatus.value[file.name] = 'analyzing'

      try {
        // 读取文件内容
        const fileContent = await readFileContent(file)

        // 调用后端AI分析API
        const response = await axios.post('http://127.0.0.1:8000/api/templates/extract-phrases', {
          content: fileContent,
          filename: file.name
        })

        if (response.data.success && response.data.phrases) {
          // 合并语句，去重
          response.data.phrases.forEach((phrase: { content: string; category: string }) => {
            const exists = allPhrases.some(p =>
              p.content === phrase.content && p.category === phrase.category
            )
            if (!exists) {
              allPhrases.push(phrase)
            }
          })
          successCount++

          // 标记为完成
          fileStatus.value[file.name] = 'done'
        } else {
          failCount++
          fileStatus.value[file.name] = 'failed'
        }
      } catch (error: any) {
        console.error(`分析文件 ${file.name} 失败:`, error)
        failCount++
        fileStatus.value[file.name] = 'failed'
      }

      // 更新进度
      analysisProgress.value.percentage = Math.round(((i + 1) / total) * 100)
      analysisProgress.value.current = `${Math.round(((i + 1) / total) * 100)}%`
    }

    // 完成进度
    analysisProgress.value.completed = total
    analysisProgress.value.percentage = 100
    analysisProgress.value.status = successCount === total ? 'success' : 'warning'
    analysisProgress.value.current = '完成'

    // 更新提取的语句列表
    extractedPhrases.value = allPhrases

    // 显示结果
    if (successCount > 0) {
      ElMessage.success(
        `分析完成！成功 ${successCount} 个文件，失败 ${failCount} 个文件，共提取 ${allPhrases.length} 条语句`
      )
    } else {
      ElMessage.error('所有文件分析失败，请检查文件格式和网络连接')
      analysisProgress.value.status = 'exception'
    }
  } catch (error: any) {
    console.error('批量分析失败:', error)
    ElMessage.error('批量分析失败: ' + (error.response?.data?.detail || error.message))
    analysisProgress.value.status = 'exception'
  } finally {
    analyzing.value = false
    analyzingFileName.value = ''
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

    // 通知快速模板组件刷新
    eventBus.emit('templates-updated')

    // 清空提取结果和文件列表
    extractedPhrases.value = []
    selectedFiles.value = []
    fileList.value = []
  } catch (error: any) {
    console.error('保存失败:', error)
    ElMessage.error('保存失败: ' + (error.response?.data?.detail || error.message))
  } finally {
    saving.value = false
  }
}

function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
}

// AI服务配置相关函数
function getServiceLabel(service: string): string {
  const labelMap: Record<string, string> = {
    'deepseek': 'DeepSeek',
    'modelscope': 'ModelScope',
    'kimi': 'Kimi'
  }
  return labelMap[service] || service
}

function getDefaultBaseUrl(service: string): string {
  const urlMap: Record<string, string> = {
    'deepseek': 'https://api.deepseek.com/v1',
    'modelscope': 'https://api-inference.modelscope.cn/v1',
    'kimi': 'https://api.moonshot.cn/v1'
  }
  return urlMap[service] || ''
}

function getDefaultModel(service: string): string {
  const modelMap: Record<string, string> = {
    'deepseek': 'deepseek-chat',
    'modelscope': 'deepseek-ai/DeepSeek-V3',
    'kimi': 'moonshot-v1-8k'
  }
  return modelMap[service] || ''
}

function handleServiceChange() {
  // 当切换默认服务时，初始化对应服务的默认值
  const service = aiConfig.value.default_service

  if (service !== 'custom') {
    // 如果没有配置过，设置默认值
    const baseUrlKey = `${service}_base_url`
    const modelKey = `${service}_model`

    if (!aiConfig.value[baseUrlKey]) {
      aiConfig.value[baseUrlKey] = getDefaultBaseUrl(service)
    }
    if (!aiConfig.value[modelKey]) {
      aiConfig.value[modelKey] = getDefaultModel(service)
    }
  }
}

async function testAIService() {
  const service = aiConfig.value.default_service

  // 根据不同服务获取配置
  let apiKey: string = ''
  let baseUrl: string = ''
  let model: string = ''
  let serviceName: string = ''

  if (service === 'custom') {
    apiKey = aiConfig.value.custom_api_key
    baseUrl = aiConfig.value.custom_base_url
    model = aiConfig.value.custom_model
    serviceName = aiConfig.value.custom_name || '自定义服务'
  } else {
    apiKey = aiConfig.value[`${service}_api_key`]
    baseUrl = aiConfig.value[`${service}_base_url`]
    model = aiConfig.value[`${service}_model`]
    serviceName = getServiceLabel(service)
  }

  // 验证必填字段
  if (!apiKey) {
    ElMessage.warning(`请先输入${serviceName}的API密钥`)
    return
  }
  if (!baseUrl) {
    ElMessage.warning(`请先输入${serviceName}的Base URL`)
    return
  }
  if (!model) {
    ElMessage.warning(`请先输入${serviceName}的模型名称`)
    return
  }

  testing.value = true
  try {
    // 调用后端测试API
    await axios.post('http://127.0.0.1:8000/api/ai/test', {
      service,
      api_key: apiKey,
      base_url: baseUrl,
      model
    })

    ElMessage.success(`${serviceName}连接测试成功！`)
  } catch (error: any) {
    console.error('AI服务测试失败:', error)
    ElMessage.error(`连接测试失败: ${error.response?.data?.detail || error.message}`)
  } finally {
    testing.value = false
  }
}

async function testEmbeddingService() {
  const embedService = aiConfig.value.embedding_service

  let apiKey: string = ''
  let baseUrl: string = ''
  let model: string = ''
  let serviceName: string = ''

  // 根据不同嵌入服务获取配置
  if (embedService === 'siliconflow') {
    apiKey = aiConfig.value.siliconflow_api_key
    baseUrl = aiConfig.value.siliconflow_base_url
    model = aiConfig.value.siliconflow_model
    serviceName = '硅基流动'
  } else if (embedService === 'modelscope_embed') {
    apiKey = aiConfig.value.modelscope_api_key
    baseUrl = aiConfig.value.modelscope_base_url
    model = aiConfig.value.modelscope_embed_model
    serviceName = 'ModelScope'
  } else if (embedService === 'custom_embed') {
    apiKey = aiConfig.value.custom_embed_api_key
    baseUrl = aiConfig.value.custom_embed_base_url
    model = aiConfig.value.custom_embed_model
    serviceName = '自定义嵌入服务'
  }

  // 验证必填字段
  if (!apiKey) {
    ElMessage.warning(`请先输入${serviceName}的API密钥`)
    return
  }
  if (!baseUrl) {
    ElMessage.warning(`请先输入${serviceName}的Base URL`)
    return
  }
  if (!model) {
    ElMessage.warning(`请先输入${serviceName}的模型名称`)
    return
  }

  testingEmbed.value = true
  try {
    // 调用后端测试嵌入服务API
    await axios.post('http://127.0.0.1:8000/api/ai/test-embedding', {
      service: embedService,
      api_key: apiKey,
      base_url: baseUrl,
      model
    })

    ElMessage.success(`${serviceName} Embedding连接测试成功！`)
  } catch (error: any) {
    console.error('Embedding服务测试失败:', error)
    ElMessage.error(`连接测试失败: ${error.response?.data?.detail || error.message}`)
  } finally {
    testingEmbed.value = false
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

.selected-files-section {
  margin-top: 16px;
  padding: 16px;
  background: #F5F7FA;
  border-radius: 8px;
}

.files-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 1px solid #DCDFE6;
}

.files-count {
  font-size: 14px;
  font-weight: 600;
  color: #409EFF;
}

.files-list-compact {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 16px;
  max-height: 150px;
  overflow-y: auto;
  padding: 8px;
  background: #FAFAFA;
  border-radius: 6px;
}

.file-tag {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 4px 8px;
  max-width: 100%;
  font-size: 12px;
}

.tag-icon {
  font-size: 14px;
  color: inherit;
  flex-shrink: 0;
}

.file-size-tiny {
  font-size: 11px;
  color: #909399;
  margin-left: 2px;
}

.file-status {
  margin-left: 4px;
  font-size: 14px;
  font-weight: bold;
}

.progress-section {
  margin-bottom: 16px;
  padding: 12px;
  background: #F5F7FA;
  border-radius: 6px;
}

.progress-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 8px;
  font-size: 12px;
  color: #606266;
}

.progress-info span:first-child {
  font-weight: 500;
  color: #409EFF;
}

.analyze-button {
  width: 100%;
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
