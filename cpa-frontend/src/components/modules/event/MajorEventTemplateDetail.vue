<template>
  <div class="major-event-template-detail">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <el-button 
          type="text" 
          @click="goBack"
          class="back-btn"
        >
          <el-icon><ArrowLeft /></el-icon>
          返回
        </el-button>
        <h1 class="page-title">模板详情</h1>
      </div>
      <div class="header-actions">
        <el-button 
          type="primary" 
          @click="useTemplate"
          :loading="loading"
        >
          使用模板
        </el-button>
        <el-button 
          type="default" 
          @click="editTemplate"
        >
          编辑模板
        </el-button>
        <el-dropdown @command="handleCommand">
          <el-button type="default">
            更多操作
            <el-icon class="el-icon--right"><arrow-down /></el-icon>
          </el-button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="copy">复制模板</el-dropdown-item>
              <el-dropdown-item command="export">导出模板</el-dropdown-item>
              <el-dropdown-item command="delete" divided>删除模板</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-container">
      <el-skeleton :rows="8" animated />
    </div>

    <!-- 错误状态 -->
    <div v-else-if="error" class="error-container">
      <el-empty description="加载失败">
        <el-button type="primary" @click="loadTemplateDetail">重新加载</el-button>
      </el-empty>
    </div>

    <!-- 模板详情内容 -->
    <div v-else class="template-content">
      <!-- 基本信息卡片 -->
      <el-card class="info-card" shadow="never">
        <template #header>
          <div class="card-header">
            <span class="card-title">基本信息</span>
          </div>
        </template>
        <div class="template-info">
          <div class="info-row">
            <div class="info-item">
              <label>模板名称：</label>
              <span>{{ templateDetail.name }}</span>
            </div>
            <div class="info-item">
              <label>模板类型：</label>
              <el-tag :type="getTypeTagType(templateDetail.type)">{{ templateDetail.typeName }}</el-tag>
            </div>
          </div>
          <div class="info-row">
            <div class="info-item">
              <label>创建人：</label>
              <span>{{ templateDetail.creator }}</span>
            </div>
            <div class="info-item">
              <label>创建时间：</label>
              <span>{{ formatDate(templateDetail.createTime) }}</span>
            </div>
          </div>
          <div class="info-row">
            <div class="info-item">
              <label>最后修改：</label>
              <span>{{ formatDate(templateDetail.updateTime) }}</span>
            </div>
            <div class="info-item">
              <label>使用次数：</label>
              <span>{{ templateDetail.useCount }} 次</span>
            </div>
          </div>
          <div class="info-row full-width">
            <div class="info-item">
              <label>模板描述：</label>
              <span>{{ templateDetail.description || '暂无描述' }}</span>
            </div>
          </div>
        </div>
      </el-card>

      <!-- 模板内容卡片 -->
      <el-card class="content-card" shadow="never">
        <template #header>
          <div class="card-header">
            <span class="card-title">模板内容</span>
          </div>
        </template>
        <div class="template-fields">
          <div class="field-item" v-for="field in templateDetail.fields" :key="field.id">
            <div class="field-header">
              <span class="field-name">{{ field.name }}</span>
              <el-tag size="small" :type="getFieldTypeTag(field.type)">{{ field.typeName }}</el-tag>
              <el-tag v-if="field.required" size="small" type="danger">必填</el-tag>
            </div>
            <div class="field-content">
              <div class="field-description">{{ field.description }}</div>
              <div v-if="field.defaultValue" class="field-default">
                <span class="label">默认值：</span>
                <span class="value">{{ field.defaultValue }}</span>
              </div>
              <div v-if="field.options && field.options.length" class="field-options">
                <span class="label">选项：</span>
                <el-tag 
                  v-for="option in field.options" 
                  :key="option.value" 
                  size="small" 
                  class="option-tag"
                >
                  {{ option.label }}
                </el-tag>
              </div>
            </div>
          </div>
        </div>
      </el-card>

      <!-- 使用记录卡片 -->
      <el-card class="usage-card" shadow="never">
        <template #header>
          <div class="card-header">
            <span class="card-title">使用记录</span>
            <el-button type="text" @click="viewAllUsage">查看全部</el-button>
          </div>
        </template>
        <div class="usage-list">
          <div class="usage-item" v-for="usage in templateDetail.recentUsage" :key="usage.id">
            <div class="usage-info">
              <div class="usage-title">{{ usage.eventTitle }}</div>
              <div class="usage-meta">
                <span class="usage-user">{{ usage.userName }}</span>
                <span class="usage-time">{{ formatDate(usage.createTime) }}</span>
              </div>
            </div>
            <el-button type="text" @click="viewEvent(usage.eventId)">查看详情</el-button>
          </div>
          <div v-if="!templateDetail.recentUsage || !templateDetail.recentUsage.length" class="no-usage">
            <el-empty description="暂无使用记录" :image-size="80" />
          </div>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ArrowLeft, ArrowDown } from '@element-plus/icons-vue'

// 路由相关
const route = useRoute()
const router = useRouter()

// 响应式数据
const loading = ref(false)
const error = ref(false)
const templateDetail = ref({
  id: '',
  name: '',
  type: '',
  typeName: '',
  description: '',
  creator: '',
  createTime: '',
  updateTime: '',
  useCount: 0,
  fields: [],
  recentUsage: []
})

// 生命周期
onMounted(() => {
  loadTemplateDetail()
})

// 方法
const loadTemplateDetail = async () => {
  try {
    loading.value = true
    error.value = false
    const templateId = route.params.id
    
    // TODO: 调用API获取模板详情
    // const response = await templateApi.getDetail(templateId)
    // templateDetail.value = response.data
    
    // 模拟数据
    setTimeout(() => {
      templateDetail.value = {
        id: templateId,
        name: '年度股东大会模板',
        type: 'meeting',
        typeName: '会议类',
        description: '用于创建年度股东大会相关的重大事项',
        creator: '张三',
        createTime: '2024-01-15 10:30:00',
        updateTime: '2024-01-20 14:20:00',
        useCount: 15,
        fields: [
          {
            id: '1',
            name: '会议主题',
            type: 'text',
            typeName: '文本',
            required: true,
            description: '股东大会的主要议题',
            defaultValue: '2024年度股东大会'
          },
          {
            id: '2',
            name: '会议时间',
            type: 'datetime',
            typeName: '日期时间',
            required: true,
            description: '会议召开的具体时间'
          }
        ],
        recentUsage: [
          {
            id: '1',
            eventId: 'event_001',
            eventTitle: '2024年度股东大会',
            userName: '李四',
            createTime: '2024-01-25 09:00:00'
          }
        ]
      }
      loading.value = false
    }, 1000)
  } catch (err) {
    console.error('加载模板详情失败:', err)
    error.value = true
    loading.value = false
    ElMessage.error('加载模板详情失败')
  }
}

const goBack = () => {
  router.back()
}

const useTemplate = () => {
  router.push({
    name: 'CreateMajorEvent',
    query: { templateId: templateDetail.value.id }
  })
}

const editTemplate = () => {
  router.push({
    name: 'EditMajorEventTemplate',
    params: { id: templateDetail.value.id }
  })
}

const handleCommand = async (command) => {
  switch (command) {
    case 'copy':
      await copyTemplate()
      break
    case 'export':
      await exportTemplate()
      break
    case 'delete':
      await deleteTemplate()
      break
  }
}

const copyTemplate = async () => {
  try {
    // TODO: 调用API复制模板
    ElMessage.success('模板复制成功')
  } catch (err) {
    console.error('复制模板失败:', err)
    ElMessage.error('复制模板失败')
  }
}

const exportTemplate = async () => {
  try {
    // TODO: 调用API导出模板
    ElMessage.success('模板导出成功')
  } catch (err) {
    console.error('导出模板失败:', err)
    ElMessage.error('导出模板失败')
  }
}

const deleteTemplate = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要删除此模板吗？删除后不可恢复。',
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    // TODO: 调用API删除模板
    ElMessage.success('模板删除成功')
    router.push({ name: 'MajorEventTemplateManager' })
  } catch (err) {
    if (err !== 'cancel') {
      console.error('删除模板失败:', err)
      ElMessage.error('删除模板失败')
    }
  }
}

const viewAllUsage = () => {
  router.push({
    name: 'MajorEventTemplateUsage',
    params: { id: templateDetail.value.id }
  })
}

const viewEvent = (eventId) => {
  router.push({
    name: 'MajorEventDetail',
    params: { id: eventId }
  })
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

const getFieldTypeTag = (type) => {
  const typeMap = {
    text: 'primary',
    textarea: 'success',
    number: 'warning',
    date: 'info',
    datetime: 'info',
    select: 'danger'
  }
  return typeMap[type] || 'info'
}

const formatDate = (dateString) => {
  if (!dateString) return '-'
  return new Date(dateString).toLocaleString('zh-CN')
}
</script>

<style scoped>
.major-event-template-detail {
  padding: 20px;
  background-color: #f5f5f5;
  min-height: 100vh;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding: 20px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.back-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 8px 12px;
  color: #606266;
}

.page-title {
  margin: 0;
  font-size: 24px;
  font-weight: 600;
  color: #303133;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.loading-container,
.error-container {
  padding: 40px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.template-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.info-card,
.content-card,
.usage-card {
  border: none;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.template-info {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.info-row {
  display: flex;
  gap: 40px;
}

.info-row.full-width {
  flex-direction: column;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 8px;
  min-width: 200px;
}

.info-item label {
  color: #909399;
  font-weight: 500;
  white-space: nowrap;
}

.template-fields {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.field-item {
  padding: 16px;
  background: #f8f9fa;
  border-radius: 6px;
  border-left: 4px solid #409eff;
}

.field-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.field-name {
  font-weight: 600;
  color: #303133;
}

.field-content {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.field-description {
  color: #606266;
  font-size: 14px;
}

.field-default,
.field-options {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
}

.field-default .label,
.field-options .label {
  color: #909399;
  font-weight: 500;
}

.option-tag {
  margin-right: 4px;
}

.usage-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.usage-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  background: #f8f9fa;
  border-radius: 6px;
}

.usage-info {
  flex: 1;
}

.usage-title {
  font-weight: 600;
  color: #303133;
  margin-bottom: 4px;
}

.usage-meta {
  display: flex;
  gap: 16px;
  font-size: 14px;
  color: #909399;
}

.no-usage {
  text-align: center;
  padding: 20px;
}
</style>