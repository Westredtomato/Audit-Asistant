<template>
  <div class="major-event-template-manager">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <button class="back-btn" @click="goBack">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M19 12H5M12 19L5 12L12 5" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          返回
        </button>
        <div class="header-content">
          <h1 class="page-title">重大事项模板管理</h1>
          <p class="page-description">管理重大事项模板，包括创建、编辑、删除和查看模板</p>
        </div>
      </div>
      <div class="header-actions">
        <el-button type="primary" @click="createTemplate">
          <el-icon><Plus /></el-icon>
          创建模板
        </el-button>
      </div>
    </div>

    <!-- 筛选和搜索 -->
    <div class="filter-section">
      <el-card shadow="never">
        <el-form :model="filterForm" inline class="filter-form">
          <el-form-item label="模板名称">
            <el-input
              v-model="filterForm.name"
              placeholder="请输入模板名称"
              clearable
              style="width: 200px"
              @keyup.enter="searchTemplates"
            />
          </el-form-item>
          <el-form-item label="模板类型">
            <el-select
              v-model="filterForm.type"
              placeholder="请选择模板类型"
              clearable
              style="width: 150px"
            >
              <el-option
                v-for="type in templateTypes"
                :key="type.value"
                :label="type.label"
                :value="type.value"
              />
            </el-select>
          </el-form-item>
          <el-form-item label="创建人">
            <el-input
              v-model="filterForm.creator"
              placeholder="请输入创建人"
              clearable
              style="width: 150px"
            />
          </el-form-item>
          <el-form-item label="创建时间">
            <el-date-picker
              v-model="filterForm.createTimeRange"
              type="daterange"
              range-separator="至"
              start-placeholder="开始日期"
              end-placeholder="结束日期"
              format="YYYY-MM-DD"
              value-format="YYYY-MM-DD"
              style="width: 240px"
            />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="searchTemplates" :loading="loading">
              <el-icon><Search /></el-icon>
              搜索
            </el-button>
            <el-button @click="resetFilter">
              <el-icon><Refresh /></el-icon>
              重置
            </el-button>
          </el-form-item>
        </el-form>
      </el-card>
    </div>

    <!-- 工具栏 -->
    <div class="toolbar">
      <div class="toolbar-left">
        <el-checkbox
          v-model="selectAll"
          :indeterminate="isIndeterminate"
          @change="handleSelectAll"
        >
          全选
        </el-checkbox>
        <el-button
          type="danger"
          :disabled="!selectedTemplates.length"
          @click="batchDelete"
        >
          <el-icon><Delete /></el-icon>
          批量删除
        </el-button>
        <el-button
          :disabled="!selectedTemplates.length"
          @click="batchExport"
        >
          <el-icon><Download /></el-icon>
          批量导出
        </el-button>
      </div>
      <div class="toolbar-right">
        <span class="total-count">共 {{ pagination.total }} 个模板</span>
        <el-divider direction="vertical" />
        <el-button-group>
          <el-button
            :type="viewMode === 'card' ? 'primary' : 'default'"
            @click="viewMode = 'card'"
          >
            <el-icon><Grid /></el-icon>
          </el-button>
          <el-button
            :type="viewMode === 'table' ? 'primary' : 'default'"
            @click="viewMode = 'table'"
          >
            <el-icon><List /></el-icon>
          </el-button>
        </el-button-group>
      </div>
    </div>

    <!-- 模板列表 -->
    <div class="templates-container">
      <!-- 加载状态 -->
      <div v-if="loading" class="loading-container">
        <el-skeleton :rows="6" animated />
      </div>

      <!-- 卡片视图 -->
      <div v-else-if="viewMode === 'card'" class="card-view">
        <div class="templates-grid">
          <div
            v-for="template in templateList"
            :key="template.id"
            class="template-card"
          >
            <el-card shadow="hover" class="template-item">
              <div class="card-header">
                <el-checkbox
                  v-model="selectedTemplates"
                  :label="template.id"
                  @change="handleSelectionChange"
                />
                <el-dropdown @command="(command) => handleCommand(command, template)">
                  <el-button type="text" class="more-btn">
                    <el-icon><MoreFilled /></el-icon>
                  </el-button>
                  <template #dropdown>
                    <el-dropdown-menu>
                      <el-dropdown-item command="view">查看详情</el-dropdown-item>
                      <el-dropdown-item command="edit">编辑模板</el-dropdown-item>
                      <el-dropdown-item command="copy">复制模板</el-dropdown-item>
                      <el-dropdown-item command="export">导出模板</el-dropdown-item>
                      <el-dropdown-item command="delete" divided>删除模板</el-dropdown-item>
                    </el-dropdown-menu>
                  </template>
                </el-dropdown>
              </div>
              
              <div class="card-content" @click="viewTemplate(template.id)">
                <div class="template-info">
                  <h3 class="template-name">{{ template.name }}</h3>
                  <el-tag :type="getTypeTagType(template.type)" size="small">
                    {{ template.typeName }}
                  </el-tag>
                </div>
                
                <p class="template-description">
                  {{ template.description || '暂无描述' }}
                </p>
                
                <div class="template-stats">
                  <div class="stat-item">
                    <span class="stat-label">字段数：</span>
                    <span class="stat-value">{{ template.fieldCount }}</span>
                  </div>
                  <div class="stat-item">
                    <span class="stat-label">使用次数：</span>
                    <span class="stat-value">{{ template.useCount }}</span>
                  </div>
                </div>
                
                <div class="template-meta">
                  <div class="meta-item">
                    <span class="meta-label">创建人：</span>
                    <span class="meta-value">{{ template.creator }}</span>
                  </div>
                  <div class="meta-item">
                    <span class="meta-label">创建时间：</span>
                    <span class="meta-value">{{ formatDate(template.createTime) }}</span>
                  </div>
                </div>
              </div>
              
              <div class="card-actions">
                <el-button type="primary" size="small" @click="useTemplate(template)">
                  使用模板
                </el-button>
                <el-button size="small" @click="editTemplate(template.id)">
                  编辑
                </el-button>
              </div>
            </el-card>
          </div>
        </div>
      </div>

      <!-- 表格视图 -->
      <div v-else class="table-view">
        <el-table
          :data="templateList"
          @selection-change="handleTableSelectionChange"
          stripe
          style="width: 100%"
        >
          <el-table-column type="selection" width="55" />
          <el-table-column prop="name" label="模板名称" min-width="200">
            <template #default="{ row }">
              <el-button type="text" @click="viewTemplate(row.id)">
                {{ row.name }}
              </el-button>
            </template>
          </el-table-column>
          <el-table-column prop="typeName" label="模板类型" width="120">
            <template #default="{ row }">
              <el-tag :type="getTypeTagType(row.type)" size="small">
                {{ row.typeName }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip />
          <el-table-column prop="fieldCount" label="字段数" width="80" align="center" />
          <el-table-column prop="useCount" label="使用次数" width="100" align="center" />
          <el-table-column prop="creator" label="创建人" width="120" />
          <el-table-column prop="createTime" label="创建时间" width="180">
            <template #default="{ row }">
              {{ formatDate(row.createTime) }}
            </template>
          </el-table-column>
          <el-table-column label="操作" width="200" fixed="right">
            <template #default="{ row }">
              <el-button type="text" size="small" @click="useTemplate(row)">
                使用
              </el-button>
              <el-button type="text" size="small" @click="viewTemplate(row.id)">
                查看
              </el-button>
              <el-button type="text" size="small" @click="editTemplate(row.id)">
                编辑
              </el-button>
              <el-button type="text" size="small" @click="deleteTemplate(row)" class="danger">
                删除
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <!-- 空状态 -->
      <div v-if="!loading && !templateList.length" class="empty-state">
        <el-empty description="暂无模板数据">
          <el-button type="primary" @click="createTemplate">创建第一个模板</el-button>
        </el-empty>
      </div>
    </div>

    <!-- 分页 -->
    <div v-if="templateList.length" class="pagination-container">
      <el-pagination
        v-model:current-page="pagination.currentPage"
        v-model:page-size="pagination.pageSize"
        :page-sizes="[10, 20, 50, 100]"
        :total="pagination.total"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Plus,
  Search,
  Refresh,
  Delete,
  Download,
  Grid,
  List,
  MoreFilled
} from '@element-plus/icons-vue'

// 路由
const router = useRouter()

// 响应式数据
const loading = ref(false)
const viewMode = ref('card') // 'card' | 'table'
const selectedTemplates = ref([])
const templateList = ref([])

// 筛选表单
const filterForm = reactive({
  name: '',
  type: '',
  creator: '',
  createTimeRange: []
})

// 分页
const pagination = reactive({
  currentPage: 1,
  pageSize: 20,
  total: 0
})

// 模板类型选项
const templateTypes = ref([
  { label: '会议类', value: 'meeting' },
  { label: '公告类', value: 'announcement' },
  { label: '决策类', value: 'decision' },
  { label: '其他', value: 'other' }
])

// 计算属性
const selectAll = computed({
  get() {
    return selectedTemplates.value.length === templateList.value.length && templateList.value.length > 0
  },
  set(value) {
    if (value) {
      selectedTemplates.value = templateList.value.map(item => item.id)
    } else {
      selectedTemplates.value = []
    }
  }
})

const isIndeterminate = computed(() => {
  const selectedCount = selectedTemplates.value.length
  return selectedCount > 0 && selectedCount < templateList.value.length
})

// 生命周期
onMounted(() => {
  loadTemplates()
})

// 方法
const goBack = () => {
  router.push('/events/major-events')
}

const loadTemplates = async () => {
  try {
    loading.value = true
    
    // TODO: 调用API获取模板列表
    // const response = await templateApi.getList({
    //   ...filterForm,
    //   page: pagination.currentPage,
    //   pageSize: pagination.pageSize
    // })
    // templateList.value = response.data.list
    // pagination.total = response.data.total
    
    // 模拟数据
    setTimeout(() => {
      templateList.value = [
        {
          id: '1',
          name: '年度股东大会模板',
          type: 'meeting',
          typeName: '会议类',
          description: '用于创建年度股东大会相关的重大事项',
          fieldCount: 8,
          useCount: 15,
          creator: '张三',
          createTime: '2024-01-15 10:30:00'
        },
        {
          id: '2',
          name: '重大投资决策模板',
          type: 'decision',
          typeName: '决策类',
          description: '用于重大投资决策事项的标准化处理',
          fieldCount: 12,
          useCount: 8,
          creator: '李四',
          createTime: '2024-01-10 14:20:00'
        }
      ]
      pagination.total = 2
      loading.value = false
    }, 1000)
  } catch (err) {
    console.error('加载模板列表失败:', err)
    ElMessage.error('加载模板列表失败')
    loading.value = false
  }
}

const searchTemplates = () => {
  pagination.currentPage = 1
  loadTemplates()
}

const resetFilter = () => {
  Object.assign(filterForm, {
    name: '',
    type: '',
    creator: '',
    createTimeRange: []
  })
  searchTemplates()
}

const handleSelectAll = (value) => {
  selectAll.value = value
}

const handleSelectionChange = () => {
  // 处理选择变化
}

const handleTableSelectionChange = (selection) => {
  selectedTemplates.value = selection.map(item => item.id)
}

const createTemplate = () => {
  router.push({ name: 'CreateMajorEventTemplate' })
}

const viewTemplate = (templateId) => {
  router.push({
    name: 'MajorEventTemplateDetail',
    params: { id: templateId }
  })
}

const editTemplate = (templateId) => {
  router.push({
    name: 'EditMajorEventTemplate',
    params: { id: templateId }
  })
}

const useTemplate = (template) => {
  router.push({
    name: 'CreateMajorEvent',
    query: { templateId: template.id }
  })
}

const handleCommand = (command, template) => {
  switch (command) {
    case 'view':
      viewTemplate(template.id)
      break
    case 'edit':
      editTemplate(template.id)
      break
    case 'copy':
      copyTemplate(template)
      break
    case 'export':
      exportTemplate(template)
      break
    case 'delete':
      deleteTemplate(template)
      break
  }
}

const copyTemplate = async (template) => {
  try {
    // TODO: 调用API复制模板
    ElMessage.success('模板复制成功')
    loadTemplates()
  } catch (err) {
    console.error('复制模板失败:', err)
    ElMessage.error('复制模板失败')
  }
}

const exportTemplate = async (template) => {
  try {
    // TODO: 调用API导出模板
    ElMessage.success('模板导出成功')
  } catch (err) {
    console.error('导出模板失败:', err)
    ElMessage.error('导出模板失败')
  }
}

const deleteTemplate = async (template) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除模板"${template.name}"吗？删除后不可恢复。`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    // TODO: 调用API删除模板
    ElMessage.success('模板删除成功')
    loadTemplates()
  } catch (err) {
    if (err !== 'cancel') {
      console.error('删除模板失败:', err)
      ElMessage.error('删除模板失败')
    }
  }
}

const batchDelete = async () => {
  try {
    await ElMessageBox.confirm(
      `确定要删除选中的 ${selectedTemplates.value.length} 个模板吗？删除后不可恢复。`,
      '确认批量删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    // TODO: 调用API批量删除模板
    ElMessage.success('批量删除成功')
    selectedTemplates.value = []
    loadTemplates()
  } catch (err) {
    if (err !== 'cancel') {
      console.error('批量删除失败:', err)
      ElMessage.error('批量删除失败')
    }
  }
}

const batchExport = async () => {
  try {
    // TODO: 调用API批量导出模板
    ElMessage.success('批量导出成功')
  } catch (err) {
    console.error('批量导出失败:', err)
    ElMessage.error('批量导出失败')
  }
}

const handleSizeChange = (size) => {
  pagination.pageSize = size
  pagination.currentPage = 1
  loadTemplates()
}

const handleCurrentChange = (page) => {
  pagination.currentPage = page
  loadTemplates()
}

const getTypeTagType = (type) => {
  const typeMap = {
    meeting: 'primary',
    announcement: 'success',
    decision: 'warning',
    other: 'info'
  }
  return typeMap[type] || 'info'
}

const formatDate = (dateString) => {
  if (!dateString) return '-'
  return new Date(dateString).toLocaleString('zh-CN')
}
</script>

<style scoped>
.major-event-template-manager {
  padding: 20px;
  background-color: #f5f5f5;
  min-height: 100vh;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 20px;
  padding: 20px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.header-left {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 16px;
}

.back-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: #f5f5f5;
  border: 1px solid #ddd;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
  color: #666;
}

.back-btn:hover {
  background: #e0e0e0;
  color: #333;
}

.header-content {
  flex: 1;
}

.page-title {
  margin: 0 0 8px 0;
  font-size: 24px;
  font-weight: 600;
  color: #303133;
}

.page-description {
  margin: 0;
  color: #606266;
  font-size: 14px;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.filter-section {
  margin-bottom: 20px;
}

.filter-form {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding: 16px 20px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.toolbar-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.toolbar-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.total-count {
  color: #606266;
  font-size: 14px;
}

.templates-container {
  margin-bottom: 20px;
}

.loading-container {
  padding: 20px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.card-view .templates-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 20px;
}

.template-card {
  height: 100%;
}

.template-item {
  height: 100%;
  display: flex;
  flex-direction: column;
  cursor: pointer;
  transition: all 0.3s ease;
}

.template-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.more-btn {
  color: #909399;
}

.card-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.template-info {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
}

.template-name {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  flex: 1;
}

.template-description {
  margin: 0;
  color: #606266;
  font-size: 14px;
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.template-stats {
  display: flex;
  gap: 16px;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 14px;
}

.stat-label {
  color: #909399;
}

.stat-value {
  color: #303133;
  font-weight: 600;
}

.template-meta {
  display: flex;
  flex-direction: column;
  gap: 4px;
  font-size: 12px;
}

.meta-item {
  display: flex;
  gap: 8px;
}

.meta-label {
  color: #909399;
}

.meta-value {
  color: #606266;
}

.card-actions {
  display: flex;
  gap: 8px;
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #f0f0f0;
}

.table-view {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.danger {
  color: #f56c6c;
}

.danger:hover {
  color: #f56c6c;
}

.empty-state {
  padding: 60px 20px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  text-align: center;
}

.pagination-container {
  display: flex;
  justify-content: center;
  padding: 20px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}
</style>