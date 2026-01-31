<template>
  <div class="template-manager">
    <div class="manager-header">
      <h3 class="manager-title">模板管理</h3>
      <el-button type="primary" :icon="Plus" @click="showAddDialog">
        添加模板
      </el-button>
    </div>

    <!-- 分类筛选 -->
    <div class="filter-section">
      <el-select
        v-model="selectedCategory"
        placeholder="全部分类"
        clearable
        @change="loadTemplates"
        class="category-filter"
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

      <el-input
        v-model="searchKeyword"
        placeholder="搜索模板内容"
        :prefix-icon="Search"
        clearable
        @input="handleSearch"
        class="search-input"
      />
    </div>

    <!-- 模板列表 -->
    <div class="template-list">
      <el-empty v-if="filteredTemplates.length === 0" description="暂无模板" />

      <div
        v-for="template in filteredTemplates"
        :key="template.id"
        class="template-card"
      >
        <div class="template-header">
          <el-tag size="small" type="info">{{ template.category }}</el-tag>
          <div class="template-actions">
            <el-button
              type="primary"
              size="small"
              :icon="CopyDocument"
              @click="copyTemplate(template)"
            >
              复制
            </el-button>
            <el-button
              v-if="!template.is_system"
              type="warning"
              size="small"
              :icon="Edit"
              @click="editTemplate(template)"
            >
              编辑
            </el-button>
            <el-button
              v-if="!template.is_system"
              type="danger"
              size="small"
              :icon="Delete"
              @click="deleteTemplate(template)"
            >
              删除
            </el-button>
          </div>
        </div>

        <div class="template-content">
          {{ template.content }}
        </div>

        <div class="template-footer">
          <span class="usage-count">使用次数: {{ template.usage_count }}</span>
        </div>
      </div>
    </div>

    <!-- 添加/编辑模板对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="editingTemplate ? '编辑模板' : '添加模板'"
      width="600px"
    >
      <el-form :model="templateForm" label-width="100px">
        <el-form-item label="分类">
          <el-select v-model="templateForm.category" placeholder="选择分类">
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
        </el-form-item>

        <el-form-item label="模板名称">
          <el-input
            v-model="templateForm.template_name"
            placeholder="请输入模板名称"
          />
        </el-form-item>

        <el-form-item label="模板内容">
          <el-input
            v-model="templateForm.content"
            type="textarea"
            :rows="4"
            placeholder="请输入模板内容"
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveTemplate">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Search, CopyDocument, Edit, Delete } from '@element-plus/icons-vue'
import axios from 'axios'
import { eventBus } from '@/utils/eventBus'

const selectedCategory = ref('')
const searchKeyword = ref('')
const templates = ref<any[]>([])
const dialogVisible = ref(false)
const editingTemplate = ref<any>(null)

const templateForm = ref({
  category: '',
  template_name: '',
  content: ''
})

// 处理模板更新事件
function handleTemplatesUpdated() {
  loadTemplates()
}

// 组件挂载时监听事件
onMounted(() => {
  loadTemplates()
  eventBus.on('templates-updated', handleTemplatesUpdated)
})

// 组件卸载时移除监听
onUnmounted(() => {
  eventBus.off('templates-updated', handleTemplatesUpdated)
})

// 过滤后的模板列表
const filteredTemplates = computed(() => {
  let result = templates.value

  // 按分类过滤
  if (selectedCategory.value) {
    result = result.filter(t => t.category === selectedCategory.value)
  }

  // 按关键词搜索
  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase()
    result = result.filter(t =>
      t.content.toLowerCase().includes(keyword) ||
      t.template_name.toLowerCase().includes(keyword)
    )
  }

  return result
})

// 加载所有模板
async function loadTemplates() {
  try {
    const response = await axios.get('http://127.0.0.1:8000/api/templates/')
    templates.value = response.data
  } catch (error: any) {
    ElMessage.error('加载模板失败: ' + (error.response?.data?.detail || error.message))
  }
}

// 搜索处理
function handleSearch() {
  // computed 会自动处理
}

// 复制模板
async function copyTemplate(template: any) {
  try {
    await navigator.clipboard.writeText(template.content)
    ElMessage.success('已复制到剪贴板')

    // 增加使用次数
    await axios.post(`http://127.0.0.1:8000/api/templates/${template.id}/use`)
    loadTemplates()
  } catch (error: any) {
    ElMessage.error('复制失败')
  }
}

// 显示添加对话框
function showAddDialog() {
  editingTemplate.value = null
  templateForm.value = {
    category: '',
    template_name: '',
    content: ''
  }
  dialogVisible.value = true
}

// 编辑模板
function editTemplate(template: any) {
  editingTemplate.value = template
  templateForm.value = {
    category: template.category,
    template_name: template.template_name,
    content: template.content
  }
  dialogVisible.value = true
}

// 保存模板
async function saveTemplate() {
  if (!templateForm.value.category || !templateForm.value.content) {
    ElMessage.warning('请填写分类和内容')
    return
  }

  // 生成模板名称（如果未填写）
  if (!templateForm.value.template_name) {
    templateForm.value.template_name = templateForm.value.content.substring(0, 20)
  }

  try {
    if (editingTemplate.value) {
      // 更新
      await axios.put(`http://127.0.0.1:8000/api/templates/${editingTemplate.value.id}`, {
        template_name: templateForm.value.template_name,
        content: templateForm.value.content
      })
      ElMessage.success('更新成功')
    } else {
      // 新建
      await axios.post('http://127.0.0.1:8000/api/templates/', {
        category: templateForm.value.category,
        template_name: templateForm.value.template_name,
        content: templateForm.value.content,
        is_system: false
      })
      ElMessage.success('添加成功')
    }

    dialogVisible.value = false
    loadTemplates()
  } catch (error: any) {
    ElMessage.error('保存失败: ' + (error.response?.data?.detail || error.message))
  }
}

// 删除模板
async function deleteTemplate(template: any) {
  try {
    await ElMessageBox.confirm(
      `确定要删除模板"${template.template_name}"吗？`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    await axios.delete(`http://127.0.0.1:8000/api/templates/${template.id}`)
    ElMessage.success('删除成功')
    loadTemplates()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败: ' + (error.response?.data?.detail || error.message))
    }
  }
}

// 组件挂载时加载模板
onMounted(() => {
  loadTemplates()
})
</script>

<style scoped>
.template-manager {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.manager-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.manager-title {
  font-size: 18px;
  font-weight: 600;
  color: #333;
  margin: 0;
}

.filter-section {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
}

.category-filter {
  width: 300px;
}

.search-input {
  flex: 1;
  max-width: 400px;
}

.template-list {
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.template-card {
  background: white;
  border: 1px solid #E5E5EA;
  border-radius: 8px;
  padding: 16px;
  transition: all 0.2s;
}

.template-card:hover {
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.template-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.template-actions {
  display: flex;
  gap: 8px;
}

.template-content {
  font-size: 14px;
  color: #333;
  line-height: 1.6;
  margin-bottom: 12px;
  white-space: pre-wrap;
  word-break: break-word;
}

.template-footer {
  display: flex;
  justify-content: flex-end;
  align-items: center;
}

.usage-count {
  font-size: 12px;
  color: #999;
}

/* 优化分组标签样式 */
.category-filter :deep(.el-select-group__title),
.template-form :deep(.el-select-group__title) {
  font-weight: 600;
  color: #409EFF;
  font-size: 13px;
  padding: 8px 12px;
}

.category-filter :deep(.el-select-group__wrap),
.template-form :deep(.el-select-group__wrap) {
  padding: 0;
  margin: 0;
}
</style>
