<template>
  <el-card class="note-card" shadow="never">
    <template #header>
      <div class="card-header">
        <span class="card-title">病程记录</span>
        <el-radio-group v-model="recordMode" size="small">
          <el-radio-button label="scheduled">按日补记录</el-radio-button>
          <el-radio-button label="temporary">临时记录</el-radio-button>
        </el-radio-group>
      </div>
    </template>

    <!-- 按日补记录模式 - 时间轴 -->
    <div v-if="recordMode === 'scheduled'" class="scheduled-mode">
      <!-- 统计信息 -->
      <div v-if="timelineData.length > 0" class="timeline-stats">
        <el-tag type="info">入院：{{ formatDate(admissionDate) }}</el-tag>
        <el-tag type="success">应记录：{{ timelineData.length }}次</el-tag>
        <el-tag type="success">已记录：{{ recordCount }}次</el-tag>
        <el-tag type="warning">缺失：{{ missingCount }}次</el-tag>
        <el-tag>住院第{{ daysInHospital }}天</el-tag>
      </div>

      <!-- 时间轴 -->
      <div v-loading="loadingHistory" class="timeline-container">
        <div
          v-for="(item, index) in timelineData"
          :key="index"
          class="timeline-item"
          :class="{
            'has-record': item.hasRecord,
            'missing-record': !item.hasRecord
          }"
        >
          <div class="timeline-dot"></div>
          <div class="timeline-date">
            <div class="date-text">{{ formatDate(item.date) }}</div>
            <div class="day-number">第{{ item.dayNumber }}天</div>
          </div>
          <div class="timeline-content">
            <!-- 有记录的日期 -->
            <el-card v-if="item.hasRecord" class="record-card" shadow="hover">
              <template #header>
                <div class="record-header">
                  <span class="record-type">{{ item.note?.record_type }}</span>
                  <div class="header-actions">
                    <el-tag v-if="item.note?.is_edited" type="warning" size="small">已编辑</el-tag>
                    <el-button
                      link
                      type="primary"
                      size="small"
                      @click="openGenerateDialog(item)"
                      :icon="Edit"
                    >
                      重新生成
                    </el-button>
                    <el-button
                      link
                      type="primary"
                      size="small"
                      @click="viewFullRecord(item.note)"
                      :icon="Document"
                    >
                      查看完整
                    </el-button>
                  </div>
                </div>
              </template>
              <div class="record-preview">
                <div class="preview-section">
                  <span class="section-label">情况：</span>
                  <span class="section-text">{{ truncateText(item.note?.daily_condition, 50) }}</span>
                </div>
              </div>
            </el-card>

            <!-- 缺失记录的日期 -->
            <el-card v-else class="missing-card" shadow="hover">
              <template #header>
                <div class="missing-header">
                  <span class="expected-type">{{ item.expectedType }}</span>
                  <el-button
                    :type="isCardExpanded(index) ? 'warning' : 'primary'"
                    size="small"
                    @click="toggleCardExpand(index)"
                    :icon="isCardExpanded(index) ? ArrowUp : ArrowDown"
                  >
                    {{ isCardExpanded(index) ? '收起' : '补记录' }}
                  </el-button>
                </div>
              </template>

              <!-- 未展开状态 -->
              <div v-if="!isCardExpanded(index)" class="missing-content">
                <el-icon class="missing-icon"><Warning /></el-icon>
                <span class="missing-text">该日期应该有{{ item.expectedType }}但未创建，点击上方按钮补录</span>
              </div>

              <!-- 展开状态 - 补记录表单 -->
              <div v-else class="generate-form-content">
                <el-form :model="getCardForm(index)" label-width="100px">
                  <el-form-item label="记录日期">
                    <el-date-picker
                      :model-value="item.date"
                      type="date"
                      placeholder="选择日期"
                      disabled
                      style="width: 100%"
                    />
                  </el-form-item>

                  <el-form-item label="记录类型">
                    <el-select :model-value="getCardForm(index).recordType" @change="(val) => updateCardForm(index, 'recordType', val)" style="width: 100%">
                      <el-option label="住院医师查房" value="住院医师查房" />
                      <el-option label="主治医师查房" value="主治医师查房" />
                      <el-option label="主任医师查房" value="主任医师查房" />
                      <el-option label="阶段小结" value="阶段小结" />
                    </el-select>
                  </el-form-item>

                  <el-form-item label="当日情况">
                    <el-input
                      :model-value="getCardForm(index).dailyCondition"
                      @input="(val) => updateCardForm(index, 'dailyCondition', val)"
                      type="textarea"
                      :rows="5"
                      placeholder="已自动填充主诉和随机生命体征信息，可根据实际情况修改或补充..."
                    />
                    <div class="form-tip">包含：主诉 + 生命体征（体温、脉搏、呼吸、血压，随机正常值）</div>
                  </el-form-item>

                  <el-form-item label="AI生成预览">
                    <el-input
                      :model-value="getCardForm(index).generatedContent"
                      @input="(val) => updateCardForm(index, 'generatedContent', val)"
                      type="textarea"
                      :rows="8"
                      placeholder="AI生成的病程记录将显示在这里..."
                    />
                  </el-form-item>

                  <el-form-item>
                    <el-button
                      type="primary"
                      :loading="isCardGenerating(index)"
                      :icon="MagicStick"
                      @click="handleGenerateForCard(index)"
                    >
                      AI生成
                    </el-button>
                    <el-button
                      type="success"
                      :loading="isCardSaving(index)"
                      :icon="Check"
                      @click="handleSaveForCard(index)"
                      :disabled="!getCardForm(index).generatedContent"
                    >
                      保存记录
                    </el-button>
                  </el-form-item>
                </el-form>
              </div>
            </el-card>
          </div>
        </div>

        <el-empty v-if="timelineData.length === 0" description="暂无住院记录" />
      </div>
    </div>

    <!-- 临时记录模式 -->
    <div v-else class="temporary-mode">
      <div class="mode-description">
        <el-icon><InfoFilled /></el-icon>
        <span>记录患者当前的临时变化或特殊情况（住院医师查房）</span>
      </div>

      <div class="form-content">
        <div class="form-section">
          <label>记录日期：</label>
          <el-date-picker
            v-model="temporaryDate"
            type="date"
            placeholder="选择日期"
            :disabled-date="disabledDate"
            value-format="YYYY-MM-DD"
          />
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
          <el-button type="primary" :icon="MagicStick" :loading="generating" @click="handleGenerate">
            AI生成
          </el-button>
          <el-button :icon="DocumentCopy" @click="handleSave">保存</el-button>
        </div>

        <div v-if="generatedContent" class="preview-section">
          <label>AI生成预览：</label>
          <el-input
            v-model="generatedContent"
            type="textarea"
            :rows="8"
            placeholder="AI生成的病程记录将显示在这里..."
          />
        </div>
      </div>
    </div>

    <!-- 历史记录对话框 -->
    <el-dialog
      v-model="historyDialogVisible"
      title="住院病程时间轴"
      width="800px"
    >
      <div v-loading="loadingHistory">
        <!-- 统计信息 -->
        <div v-if="timelineData.length > 0" class="timeline-stats">
          <el-tag type="info">入院：{{ formatDate(admissionDate) }}</el-tag>
          <el-tag type="success">应记录：{{ timelineData.length }}次</el-tag>
          <el-tag type="success">已记录：{{ recordCount }}次</el-tag>
          <el-tag type="warning">缺失：{{ missingCount }}次</el-tag>
          <el-tag>住院第{{ daysInHospital }}天</el-tag>
        </div>

        <!-- 时间轴 -->
        <div class="timeline-container">
          <div
            v-for="(item, index) in timelineData"
            :key="index"
            class="timeline-item"
            :class="{
              'has-record': item.hasRecord,
              'missing-record': !item.hasRecord
            }"
          >
            <div class="timeline-dot"></div>
            <div class="timeline-date">
              <div class="date-text">{{ formatDate(item.date) }}</div>
              <div class="day-number">第{{ item.dayNumber }}天</div>
            </div>
            <div class="timeline-content">
              <!-- 有记录的日期 -->
              <el-card v-if="item.hasRecord" class="record-card" shadow="hover">
                <template #header>
                  <div class="record-header">
                    <span class="record-type">{{ item.note?.record_type }}</span>
                    <div class="header-actions">
                      <el-tag v-if="item.note?.is_edited" type="warning" size="small">已编辑</el-tag>
                      <el-button
                        link
                        type="primary"
                        size="small"
                        @click="openGenerateDialog(item)"
                        :icon="Edit"
                      >
                        重新生成
                      </el-button>
                    </div>
                  </div>
                </template>
                <div class="record-preview">
                  <div class="preview-section">
                    <span class="section-label">情况：</span>
                    <span class="section-text">{{ truncateText(item.note?.daily_condition, 50) }}</span>
                  </div>
                  <div class="preview-section">
                    <span class="section-label">病程：</span>
                    <span class="section-text">{{ truncateText(item.note?.generated_content, 80) }}</span>
                  </div>
                  <div class="preview-actions">
                    <el-button
                      link
                      type="primary"
                      size="small"
                      @click="viewFullRecord(item.note)"
                    >
                      查看完整记录 →
                    </el-button>
                  </div>
                </div>
              </el-card>

              <!-- 缺失记录的日期 -->
              <el-card v-else class="missing-card" shadow="hover">
                <template #header>
                  <div class="missing-header">
                    <span class="expected-type">{{ item.expectedType }}</span>
                    <el-button
                      type="primary"
                      size="small"
                      @click="openGenerateDialog(item)"
                      :icon="Plus"
                    >
                      补记录
                    </el-button>
                  </div>
                </template>
                <div class="missing-content">
                  <el-icon class="missing-icon"><Warning /></el-icon>
                  <span class="missing-text">该日期应该有{{ item.expectedType }}但未创建，点击上方按钮补录</span>
                </div>
              </el-card>
            </div>
          </div>
        </div>

        <el-empty v-if="timelineData.length === 0" description="暂无住院记录" />
      </div>
    </el-dialog>

    <!-- 完整记录详情对话框 -->
    <el-dialog
      v-model="fullRecordDialogVisible"
      :title="`完整病程记录 - ${formatDate(selectedNote?.record_date)}`"
      width="700px"
    >
      <div v-if="selectedNote">
        <div class="full-record-header">
          <el-tag>{{ selectedNote.record_type }}</el-tag>
          <span class="day-badge">住院第{{ selectedNote.day_number }}天</span>
          <el-tag v-if="selectedNote.is_edited" type="warning" size="small">已编辑</el-tag>
        </div>
        <div class="full-record-content">
          <div class="record-section">
            <strong>当日情况：</strong>
            <p>{{ selectedNote.daily_condition }}</p>
          </div>
          <div class="record-section">
            <div class="section-header">
              <strong>病程记录：</strong>
              <el-button
                :icon="DocumentCopy"
                size="small"
                @click="copyRecordContent"
              >
                复制
              </el-button>
            </div>
            <p>{{ selectedNote.generated_content }}</p>
          </div>
        </div>
      </div>
    </el-dialog>

    <!-- 补录/重新生成病程记录对话框 -->
    <el-dialog
      v-model="generateDialogVisible"
      :title="generateDialogTitle"
      width="600px"
    >
      <el-form :model="generateForm" label-width="100px">
        <el-form-item label="记录日期">
          <el-date-picker
            v-model="generateForm.recordDate"
            type="date"
            placeholder="选择日期"
            disabled
            style="width: 100%"
          />
        </el-form-item>

        <el-form-item label="记录类型">
          <el-select v-model="generateForm.recordType" style="width: 100%">
            <el-option label="住院医师查房" value="住院医师查房" />
            <el-option label="主治医师查房" value="主治医师查房" />
            <el-option label="主任医师查房" value="主任医师查房" />
            <el-option label="阶段小结" value="阶段小结" />
          </el-select>
        </el-form-item>

        <el-form-item label="当日情况">
          <el-input
            v-model="generateForm.dailyCondition"
            type="textarea"
            :rows="5"
            placeholder="已自动填充主诉和随机生命体征信息，可根据实际情况修改或补充..."
          />
          <div class="form-tip">包含：主诉 + 生命体征（体温、脉搏、呼吸、血压，随机正常值）</div>
        </el-form-item>

        <el-form-item label="AI生成预览">
          <el-input
            v-model="generateForm.generatedContent"
            type="textarea"
            :rows="8"
            placeholder="AI生成的病程记录将显示在这里..."
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <span class="dialog-footer">
          <el-button @click="generateDialogVisible = false">取消</el-button>
          <el-button
            type="primary"
            :loading="generating"
            :icon="MagicStick"
            @click="handleGenerateForDate"
          >
            AI生成
          </el-button>
          <el-button
            type="success"
            :loading="saving"
            :icon="Check"
            @click="handleSaveGenerated"
            :disabled="!generateForm.generatedContent"
          >
            保存记录
          </el-button>
        </span>
      </template>
    </el-dialog>
  </el-card>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { Document, Search, MagicStick, DocumentCopy, Download, Warning, Edit, Plus, Check, InfoFilled, Calendar, ArrowUp, ArrowDown } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'
import { eventBus } from '@/utils/eventBus'

interface Props {
  patient: any
}

const props = defineProps<Props>()

// 记录模式：scheduled=按日补记录（时间轴），temporary=临时记录
const recordMode = ref('scheduled')

// 组件挂载时自动加载时间轴
onMounted(() => {
  if (recordMode.value === 'scheduled') {
    loadTimelineData()
  }
})

// 监听模式切换和患者变化
watch(recordMode, (newMode) => {
  if (newMode === 'scheduled') {
    loadTimelineData()
  }
})

watch(() => props.patient?.hospital_number, () => {
  if (recordMode.value === 'scheduled') {
    loadTimelineData()
  }
})

// 加载时间轴数据
async function loadTimelineData() {
  if (!props.patient?.admission_date) return

  loadingHistory.value = true
  try {
    admissionDate.value = props.patient.admission_date

    // 获取所有病程记录
    const response = await axios.get(
      `http://127.0.0.1:8000/api/notes/patient/${props.patient.hospital_number}`
    )
    historyNotes.value = response.data

    // 构建完整时间轴
    buildTimeline()
  } catch (error: any) {
    ElMessage.error('加载时间轴失败: ' + (error.response?.data?.detail || error.message))
  } finally {
    loadingHistory.value = false
  }
}

// 临时记录相关
const temporaryDate = ref(new Date().toISOString().split('T')[0])

// 通用变量
const dailyCondition = ref('')
const recordType = ref('住院医师查房')
const generatedContent = ref('')
const generating = ref(false)
const saving = ref(false)
const historyDialogVisible = ref(false)
const fullRecordDialogVisible = ref(false)
const generateDialogVisible = ref(false)
const historyNotes = ref<any[]>([])
const loadingHistory = ref(false)
const selectedNote = ref<any>(null)
const admissionDate = ref('')
const timelineData = ref<any[]>([])

// 展开的卡片（用于补记录功能）
const expandedCards = ref<Set<number>>(new Set())

// 每个卡片的表单数据
const cardForms = ref<Map<number, any>>(new Map())

// 每个卡片的生成和保存状态
const cardGeneratingStates = ref<Map<number, boolean>>(new Map())
const cardSavingStates = ref<Map<number, boolean>>(new Map())

// 生成记录表单
const generateForm = ref({
  recordDate: '',
  recordType: '',
  dailyCondition: '',
  generatedContent: '',
  dayNumber: 0,
  existingNoteId: null as number | null
})

// 计算属性
const recordCount = computed(() => historyNotes.value.length)
const missingCount = computed(() => timelineData.value.filter(item => !item.hasRecord).length)
const daysInHospital = computed(() => {
  if (!admissionDate.value) return 0
  const admission = new Date(admissionDate.value)
  const today = new Date()
  const diffTime = today.getTime() - admission.getTime()
  return Math.floor(diffTime / (1000 * 60 * 60 * 24)) + 1
})

const generateDialogTitle = computed(() => {
  return generateForm.value.existingNoteId ? '重新生成病程记录' : '补录病程记录'
})

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

    // 根据模式确定记录类型和日期
    let actualRecordType = '住院医师查房'
    let actualDate = new Date().toISOString().split('T')[0]

    if (recordMode.value === 'temporary' && temporaryDate.value) {
      // 临时记录模式：固定为住院医师查房，使用选择的日期
      actualRecordType = '住院医师查房'
      actualDate = temporaryDate.value
    }

    const response = await axios.post('http://127.0.0.1:8000/api/ai/generate-note', {
      hospital_number: props.patient.hospital_number,
      daily_condition: dailyCondition.value,
      record_type: actualRecordType,
      doctor_info: doctorInfo
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

  saving.value = true
  try {
    // 根据模式确定记录类型和日期
    let actualRecordType = '住院医师查房'
    let actualDate = new Date().toISOString().split('T')[0]

    if (recordMode.value === 'temporary' && temporaryDate.value) {
      // 临时记录模式：固定为住院医师查房，使用选择的日期
      actualRecordType = '住院医师查房'
      actualDate = temporaryDate.value
    }

    const response = await axios.post('http://127.0.0.1:8000/api/notes/', {
      hospital_number: props.patient.hospital_number,
      record_date: actualDate,
      record_type: actualRecordType,
      daily_condition: dailyCondition.value,
      generated_content: generatedContent.value
    })

    if (response.data) {
      ElMessage.success('保存成功')
      // 清空输入
      dailyCondition.value = ''
      generatedContent.value = ''
      // 如果是按日补记录模式，刷新时间轴
      if (recordMode.value === 'scheduled') {
        await loadTimelineData()
      }
    }
  } catch (error: any) {
    ElMessage.error('保存失败: ' + (error.response?.data?.detail || error.message))
  } finally {
    saving.value = false
  }
}

// 禁用未来的日期（临时记录）
function disabledDate(time: Date) {
  return time.getTime() > Date.now()
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
    // 获取入院日期
    admissionDate.value = props.patient.admission_date

    // 获取所有病程记录
    const response = await axios.get(
      `http://127.0.0.1:8000/api/notes/patient/${props.patient.hospital_number}`
    )
    historyNotes.value = response.data

    // 构建完整时间轴
    buildTimeline()
  } catch (error: any) {
    ElMessage.error('加载历史记录失败: ' + (error.response?.data?.detail || error.message))
  } finally {
    loadingHistory.value = false
  }
}

// 构建时间轴数据
function buildTimeline() {
  if (!admissionDate.value) return

  const timeline: any[] = []
  const admission = new Date(admissionDate.value)
  const today = new Date()
  const totalDays = Math.floor((today.getTime() - admission.getTime()) / (1000 * 60 * 60 * 24)) + 1

  // 创建日期到记录的映射
  const recordMap = new Map<string, any>()
  historyNotes.value.forEach(note => {
    const dateStr = note.record_date.split('T')[0]
    recordMap.set(dateStr, note)
  })

  // 判断某天是否应该有查房记录
  // 规则：
  // - 第2天：主治医师查房
  // - 第3天：主任医师查房
  // - 从第6天开始，每3天一次（即6,9,12,15...），3种医师轮换
  //   所以实际是9天一个完整周期（住院→主治→主任）
  // - 每30天：阶段小结
  function shouldHaveRounds(day: number): { shouldHave: boolean; expectedType?: string } {
    // 阶段小结：每30天
    if (day % 30 === 0) {
      return { shouldHave: true, expectedType: '阶段小结' }
    }

    // 第2天：主治医师查房
    if (day === 2) {
      return { shouldHave: true, expectedType: '主治医师查房' }
    }

    // 第3天：主任医师查房
    if (day === 3) {
      return { shouldHave: true, expectedType: '主任医师查房' }
    }

    // 从第6天开始，每3天一次（day % 3 == 0）
    // 三种医师轮换，9天一个完整周期
    if (day >= 6 && day % 3 === 0) {
      const cycleIndex = Math.floor((day - 6) / 3) % 3
      if (cycleIndex === 0) {
        return { shouldHave: true, expectedType: '住院医师查房' }
      } else if (cycleIndex === 1) {
        return { shouldHave: true, expectedType: '主治医师查房' }
      } else {
        return { shouldHave: true, expectedType: '主任医师查房' }
      }
    }

    // 其他日期不应该有查房记录
    return { shouldHave: false }
  }

  // 为每一天创建时间轴项（只显示应该有记录的日期）
  for (let i = 0; i < totalDays; i++) {
    const dayNumber = i + 1
    const roundsInfo = shouldHaveRounds(dayNumber)

    // 只有应该有记录的日期才显示在时间轴上
    if (roundsInfo.shouldHave) {
      const currentDate = new Date(admission)
      currentDate.setDate(admission.getDate() + i)
      const dateStr = currentDate.toISOString().split('T')[0]

      const note = recordMap.get(dateStr)
      timeline.push({
        date: dateStr,
        dayNumber: dayNumber,
        hasRecord: !!note,
        note: note || null,
        expectedType: roundsInfo.expectedType
      })
    }
  }

  // 按日期倒序排列（最新的在前面）
  timeline.reverse()
  timelineData.value = timeline
}

// 截断文本
function truncateText(text: string | undefined, maxLength: number): string {
  if (!text) return '无'
  if (text.length <= maxLength) return text
  return text.substring(0, maxLength) + '...'
}

// 查看完整记录
function viewFullRecord(note: any) {
  selectedNote.value = note
  fullRecordDialogVisible.value = true
}

// 打开生成记录对话框
function openGenerateDialog(item: any) {
  // 生成基本的生命体征模板
  const vitalSignsTemplate = generateVitalSignsTemplate(item.dayNumber)

  // 如果已有记录，保留原有的当日情况；否则使用模板
  const existingCondition = item.note?.daily_condition || ''

  generateForm.value = {
    recordDate: item.date,
    recordType: item.expectedType || (item.note?.record_type || '住院医师查房'),
    dailyCondition: existingCondition || vitalSignsTemplate,
    generatedContent: item.note?.generated_content || '',
    dayNumber: item.dayNumber,
    existingNoteId: item.note?.id || null
  }
  generateDialogVisible.value = true
}

// ========== 卡片展开式补记录功能 ==========

// 检查卡片是否展开
function isCardExpanded(index: number): boolean {
  return expandedCards.value.has(index)
}

// 切换卡片展开状态
function toggleCardExpand(index: number) {
  if (expandedCards.value.has(index)) {
    expandedCards.value.delete(index)
  } else {
    expandedCards.value.add(index)
    // 初始化卡片表单数据
    initCardForm(index)
  }
}

// 初始化卡片表单数据
function initCardForm(index: number) {
  if (cardForms.value.has(index)) return

  const item = timelineData.value[index]
  const vitalSignsTemplate = generateVitalSignsTemplate(item.dayNumber)
  const existingCondition = item.note?.daily_condition || ''

  cardForms.value.set(index, {
    recordDate: item.date,
    recordType: item.expectedType || (item.note?.record_type || '住院医师查房'),
    dailyCondition: existingCondition || vitalSignsTemplate,
    generatedContent: item.note?.generated_content || '',
    dayNumber: item.dayNumber,
    existingNoteId: item.note?.id || null
  })
}

// 获取卡片表单数据
function getCardForm(index: number): any {
  if (!cardForms.value.has(index)) {
    initCardForm(index)
  }
  return cardForms.value.get(index) || {}
}

// 更新卡片表单字段
function updateCardForm(index: number, field: string, value: any) {
  const form = getCardForm(index)
  form[field] = value
  cardForms.value.set(index, { ...form })
}

// 检查卡片是否正在生成
function isCardGenerating(index: number): boolean {
  return cardGeneratingStates.value.get(index) || false
}

// 检查卡片是否正在保存
function isCardSaving(index: number): boolean {
  return cardSavingStates.value.get(index) || false
}

// 为卡片生成AI内容
async function handleGenerateForCard(index: number) {
  const form = getCardForm(index)

  if (!form.dailyCondition.trim()) {
    ElMessage.warning('请输入当日情况')
    return
  }

  cardGeneratingStates.value.set(index, true)
  try {
    // 读取医生信息
    const doctorInfoStr = localStorage.getItem('doctor_info')
    const doctorInfo = doctorInfoStr ? JSON.parse(doctorInfoStr) : null

    const response = await axios.post('http://127.0.0.1:8000/api/ai/generate-note', {
      hospital_number: props.patient.hospital_number,
      daily_condition: form.dailyCondition,
      record_type: form.recordType,
      doctor_info: doctorInfo
    })

    if (response.data && response.data.data && response.data.data.content) {
      updateCardForm(index, 'generatedContent', response.data.data.content)
      ElMessage.success('AI生成成功')
    }
  } catch (error: any) {
    ElMessage.error('AI生成失败: ' + (error.response?.data?.detail || error.message))
  } finally {
    cardGeneratingStates.value.set(index, false)
  }
}

// 保存卡片记录
async function handleSaveForCard(index: number) {
  const form = getCardForm(index)

  if (!form.generatedContent.trim()) {
    ElMessage.warning('请先生成病程记录')
    return
  }

  cardSavingStates.value.set(index, true)
  try {
    await axios.post('http://127.0.0.1:8000/api/notes/', {
      hospital_number: props.patient.hospital_number,
      record_date: form.recordDate,
      record_type: form.recordType,
      daily_condition: form.dailyCondition,
      generated_content: form.generatedContent
    })

    ElMessage.success('保存成功')
    // 收起卡片
    expandedCards.value.delete(index)
    // 刷新时间轴
    await loadTimelineData()
  } catch (error: any) {
    ElMessage.error('保存失败: ' + (error.response?.data?.detail || error.message))
  } finally {
    cardSavingStates.value.set(index, false)
  }
}

// ==========================================


// 简化专科检查信息，移除生命体征等重复内容
function simplifySpecialistInfo(fullInfo: string): string {
  // 移除生命体征相关的内容（已在模板中）
  let simplified = fullInfo
    .replace(/体温?\d+\.?\d*℃[，,]?/g, '')
    .replace(/脉搏?\d+次\/分[，,]?/g, '')
    .replace(/呼吸?\d+次\/分[，,]?/g, '')
    .replace(/血压?\d+\/?\d*mmHg[，,]?/g, '')
    .replace(/T：?\d+\.?\d*℃[，,]?/g, '')
    .replace(/P：?\d+次\/分[，,]?/g, '')
    .replace(/R：?\d+次\/分[，,]?/g, '')
    .replace(/BP：?\d+\/?\d*mmHg[，,]?/g, '')
    .replace(/查体：/g, '')  // 移除开头的"查体："标签
    .trim()

  // 清理多余的标点符号
  simplified = simplified
    .replace(/[，,]{2,}/g, '，')
    .replace(/^[，,]/, '')  // 移除开头的逗号
    .trim()

  // 如果内容为空，返回空字符串
  if (!simplified || simplified.length < 5) {
    return ''
  }

  // 确保以正确的标点结尾
  if (!simplified.endsWith('。') && !simplified.endsWith('，')) {
    simplified += '。'
  }

  return simplified
}

// 从历史记录中提取专科检查信息
function extractSpecialistInfo(): string {
  const patient = props.patient

  // 1. 首先从历史记录中查找专科检查信息
  if (historyNotes.value && historyNotes.value.length > 0) {
    // 按日期降序排序，从最近的记录开始查找
    const sortedNotes = [...historyNotes.value].sort((a, b) =>
      new Date(b.record_date).getTime() - new Date(a.record_date).getTime()
    )

    for (const note of sortedNotes) {
      // 在当日情况中查找
      if (note.daily_condition) {
        const specialistMatch = note.daily_condition.match(/查体：.*?腹软无压痛[。，](.*?)(?=\n|$|分析)/s)
        if (specialistMatch && specialistMatch[1] && specialistMatch[1].trim()) {
          const specialistInfo = specialistMatch[1].trim()
          // 过滤掉太短或无意义的内容
          if (specialistInfo.length > 10) {
            console.log('[INFO] 从历史记录中提取到专科检查信息:', specialistInfo)
            return simplifySpecialistInfo(specialistInfo)
          }
        }
      }

      // 在生成的病程记录中查找
      if (note.generated_content) {
        const specialistMatch = note.generated_content.match(/查体：.*?腹软无压痛[。，](.*?)(?=\n\n|分析|处理)/s)
        if (specialistMatch && specialistMatch[1] && specialistMatch[1].trim()) {
          const specialistInfo = specialistMatch[1].trim()
          if (specialistInfo.length > 10) {
            console.log('[INFO] 从生成内容中提取到专科检查信息:', specialistInfo)
            return simplifySpecialistInfo(specialistInfo)
          }
        }
      }
    }
  }

  // 2. 如果历史记录中找不到，使用患者的专科检查信息（来自首程记录）
  if (patient.specialist_exam && patient.specialist_exam.trim()) {
    console.log('[INFO] 使用患者首程记录的专科检查信息')
    return simplifySpecialistInfo(patient.specialist_exam.trim())
  }

  console.log('[INFO] 未找到专科检查信息')
  return ''
}

// 生成生命体征模板
function generateVitalSignsTemplate(dayNumber: number): string {
  const patient = props.patient

  // 生成正常范围内的随机生命体征（参考rounds_generator.py）
  const temperature = (Math.random() * (37.0 - 36.2) + 36.2).toFixed(1)
  const pulse = Math.floor(Math.random() * (85 - 65) + 65)
  const respiration = Math.floor(Math.random() * (19 - 16) + 16)
  const systolicBp = Math.floor(Math.random() * (138 - 110) + 110)
  const diastolicBp = Math.floor(Math.random() * (88 - 72) + 72)

  // 获取专科检查信息
  const specialistInfo = extractSpecialistInfo()

  // 模板：主诉 + 生命体征 + 专科检查
  let template = `主诉：${patient.chief_complaint || '患者今日一般情况可，无明显不适。'}\n`

  template += `查体：患者神志清，精神可。T：${temperature}℃，P：${pulse}次/分，R：${respiration}次/分，BP：${systolicBp}/${diastolicBp}mmHg。心肺听诊未见异常，腹软无压痛。`

  // 如果有专科检查信息，追加在后面
  if (specialistInfo) {
    template += specialistInfo
  }

  return template
}

// 为特定日期生成病程记录
async function handleGenerateForDate() {
  if (!generateForm.value.dailyCondition.trim()) {
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
      daily_condition: generateForm.value.dailyCondition,
      record_type: generateForm.value.recordType,
      doctor_info: doctorInfo
    })

    if (response.data.success) {
      generateForm.value.generatedContent = response.data.data.content
      ElMessage.success('生成成功')
    }
  } catch (error: any) {
    ElMessage.error('生成失败: ' + (error.response?.data?.detail || error.message))
  } finally {
    generating.value = false
  }
}

// 保存生成的记录
async function handleSaveGenerated() {
  if (!generateForm.value.generatedContent.trim()) {
    ElMessage.warning('请先生成病程记录')
    return
  }

  saving.value = true
  try {
    if (generateForm.value.existingNoteId) {
      // 更新现有记录
      await axios.put(`http://127.0.0.1:8000/api/notes/${generateForm.value.existingNoteId}`, {
        daily_condition: generateForm.value.dailyCondition,
        generated_content: generateForm.value.generatedContent,
        is_edited: true
      })
      ElMessage.success('记录更新成功')
    } else {
      // 创建新记录
      await axios.post('http://127.0.0.1:8000/api/notes/', {
        hospital_number: props.patient.hospital_number,
        record_date: generateForm.value.recordDate,
        record_type: generateForm.value.recordType,
        daily_condition: generateForm.value.dailyCondition,
        generated_content: generateForm.value.generatedContent,
        day_number: generateForm.value.dayNumber
      })
      ElMessage.success('记录保存成功')
    }

    // 关闭对话框并刷新历史记录
    generateDialogVisible.value = false
    await showHistoryDialog()
  } catch (error: any) {
    ElMessage.error('保存失败: ' + (error.response?.data?.detail || error.message))
  } finally {
    saving.value = false
  }
}

function formatDate(dateStr: string) {
  return new Date(dateStr).toLocaleDateString('zh-CN')
}

// 复制病程记录内容
function copyRecordContent() {
  if (selectedNote.value?.generated_content) {
    // 使用 Clipboard API 复制内容
    navigator.clipboard.writeText(selectedNote.value.generated_content).then(() => {
      ElMessage.success('病程记录已复制到剪贴板')
    }).catch(() => {
      // 降级方案：使用传统方法
      const textarea = document.createElement('textarea')
      textarea.value = selectedNote.value.generated_content
      textarea.style.position = 'fixed'
      textarea.style.opacity = '0'
      document.body.appendChild(textarea)
      textarea.select()
      try {
        document.execCommand('copy')
        ElMessage.success('病程记录已复制到剪贴板')
      } catch (err) {
        ElMessage.error('复制失败，请手动复制')
      }
      document.body.removeChild(textarea)
    })
  } else {
    ElMessage.warning('没有可复制的内容')
  }
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

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
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

/* 模式描述 */
.mode-description {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px;
  background-color: #F0F9FF;
  border-left: 3px solid #3B82F6;
  border-radius: 4px;
  margin-bottom: 16px;
  font-size: 13px;
  color: #1E40AF;
}

/* 按日补记录模式 - 时间轴 */
.scheduled-mode {
  padding: 16px 0;
}

/* 临时记录模式 */
.temporary-mode {
  padding: 16px 0;
}

/* 表单内容 */
.form-content {
  animation: fadeIn 0.3s ease-in-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 卡片展开式补记录表单 */
.generate-form-content {
  padding: 16px 0;
  animation: slideDown 0.3s ease-in-out;
}

@keyframes slideDown {
  from {
    opacity: 0;
    max-height: 0;
  }
  to {
    opacity: 1;
    max-height: 1000px;
  }
}

.generate-form-content .el-form-item {
  margin-bottom: 18px;
}

.generate-form-content .form-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

/* 时间轴统计信息 */
.timeline-stats {
  display: flex;
  gap: 8px;
  margin-bottom: 20px;
  padding: 12px;
  background: #F5F7FA;
  border-radius: 8px;
  flex-wrap: wrap;
}

/* 时间轴容器 */
.timeline-container {
  /* 去掉最大高度限制和滚动条，让内容自然展示 */
  padding-right: 8px;
}

.timeline-item {
  display: flex;
  margin-bottom: 16px;
  position: relative;
}

.timeline-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: #DCDFE6;
  margin-right: 16px;
  flex-shrink: 0;
  position: relative;
  top: 20px;
  z-index: 1;
}

.timeline-item.has-record .timeline-dot {
  background: #67C23A;
  box-shadow: 0 0 0 4px rgba(103, 194, 58, 0.2);
}

.timeline-item.missing-record .timeline-dot {
  background: #E6A23C;
  box-shadow: 0 0 0 4px rgba(230, 162, 60, 0.2);
}

.timeline-item:not(:last-child)::before {
  content: '';
  position: absolute;
  left: 5px;
  top: 32px;
  width: 2px;
  height: calc(100% + 4px);
  background: #E5E5EA;
}

.timeline-item.has-record:not(:last-child)::before {
  background: linear-gradient(to bottom, #67C23A 0%, #E5E5EA 100%);
}

.timeline-date {
  min-width: 100px;
  margin-right: 12px;
}

.date-text {
  font-size: 14px;
  font-weight: 600;
  color: #333;
}

.day-number {
  font-size: 12px;
  color: #909399;
  margin-top: 2px;
}

.timeline-content {
  flex: 1;
  min-width: 0;
}

/* 记录卡片 */
.record-card {
  border-left: 3px solid #67C23A;
}

.record-card :deep(.el-card__header) {
  padding: 8px 12px;
  background: #F0F9FF;
}

.record-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.record-type {
  font-size: 13px;
  font-weight: 600;
  color: #409EFF;
  flex: 1;
}

.record-preview {
  font-size: 13px;
}

.preview-section {
  margin-bottom: 8px;
  display: flex;
  align-items: flex-start;
}

.section-label {
  color: #909399;
  flex-shrink: 0;
  margin-right: 4px;
}

.section-text {
  color: #606266;
  line-height: 1.5;
}

.preview-actions {
  display: flex;
  justify-content: flex-end;
}

/* 缺失记录卡片 */
.missing-card {
  border-left: 3px solid #E6A23C;
  background: #FFFBF0;
}

.missing-card :deep(.el-card__header) {
  padding: 8px 12px;
  background: #FFF7E6;
}

.missing-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.expected-type {
  font-size: 13px;
  font-weight: 600;
  color: #E6A23C;
  flex: 1;
}

.missing-content {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  color: #E6A23C;
  font-size: 13px;
}

.missing-icon {
  font-size: 16px;
}

.missing-text {
  font-weight: 500;
}

/* 完整记录详情 */
.full-record-header {
  display: flex;
  gap: 8px;
  align-items: center;
  margin-bottom: 16px;
}

.day-badge {
  background: #409EFF;
  color: white;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
}

.full-record-content {
  font-size: 14px;
}

.full-record-content .record-section {
  margin-bottom: 16px;
}

.full-record-content .record-section:last-child {
  margin-bottom: 0;
}

.full-record-content strong {
  color: #333;
  display: block;
  margin-bottom: 8px;
}

.full-record-content .section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.full-record-content p {
  color: #666;
  line-height: 1.8;
  margin: 0;
  white-space: pre-wrap;
}

/* 滚动条样式 */
.timeline-container::-webkit-scrollbar {
  width: 6px;
}

.timeline-container::-webkit-scrollbar-track {
  background: #F5F7FA;
  border-radius: 3px;
}

.timeline-container::-webkit-scrollbar-thumb {
  background: #DCDFE6;
  border-radius: 3px;
}

.timeline-container::-webkit-scrollbar-thumb:hover {
  background: #C0C4CC;
}

/* 生成记录对话框样式 */
.form-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}
</style>
