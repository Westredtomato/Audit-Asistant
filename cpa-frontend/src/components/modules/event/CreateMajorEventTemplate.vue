<template>
  <div class="create-major-event-template">
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
        <h1 class="page-title">创建重大事项模板</h1>
      </div>
      <div class="header-actions">
        <el-button @click="saveDraft" :loading="saving">保存草稿</el-button>
        <el-button type="primary" @click="saveTemplate" :loading="saving">保存模板</el-button>
      </div>
    </div>

    <!-- 表单内容 -->
    <div class="form-container">
      <el-form
        ref="templateFormRef"
        :model="templateForm"
        :rules="templateRules"
        label-width="120px"
        class="template-form"
      >
        <!-- 基本信息 -->
        <el-card class="form-section" shadow="never">
          <template #header>
            <div class="section-header">
              <span class="section-title">基本信息</span>
            </div>
          </template>
          
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="模板名称" prop="name">
                <el-input 
                  v-model="templateForm.name" 
                  placeholder="请输入模板名称"
                  maxlength="50"
                  show-word-limit
                />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="模板类型" prop="type">
                <el-select 
                  v-model="templateForm.type" 
                  placeholder="请选择模板类型"
                  style="width: 100%"
                >
                  <el-option 
                    v-for="type in templateTypes" 
                    :key="type.value" 
                    :label="type.label" 
                    :value="type.value"
                  />
                </el-select>
              </el-form-item>
            </el-col>
          </el-row>
          
          <el-form-item label="模板描述" prop="description">
            <el-input 
              v-model="templateForm.description" 
              type="textarea" 
              :rows="3"
              placeholder="请输入模板描述"
              maxlength="200"
              show-word-limit
            />
          </el-form-item>
        </el-card>

        <!-- 字段配置 -->
        <el-card class="form-section" shadow="never">
          <template #header>
            <div class="section-header">
              <span class="section-title">字段配置</span>
              <el-button type="primary" size="small" @click="addField">
                <el-icon><Plus /></el-icon>
                添加字段
              </el-button>
            </div>
          </template>
          
          <div class="fields-container">
            <div 
              v-for="(field, index) in templateForm.fields" 
              :key="field.id"
              class="field-item"
            >
              <div class="field-header">
                <span class="field-index">字段 {{ index + 1 }}</span>
                <div class="field-actions">
                  <el-button 
                    type="text" 
                    size="small" 
                    @click="moveFieldUp(index)"
                    :disabled="index === 0"
                  >
                    <el-icon><ArrowUp /></el-icon>
                  </el-button>
                  <el-button 
                    type="text" 
                    size="small" 
                    @click="moveFieldDown(index)"
                    :disabled="index === templateForm.fields.length - 1"
                  >
                    <el-icon><ArrowDown /></el-icon>
                  </el-button>
                  <el-button 
                    type="text" 
                    size="small" 
                    @click="removeField(index)"
                    class="delete-btn"
                  >
                    <el-icon><Delete /></el-icon>
                  </el-button>
                </div>
              </div>
              
              <div class="field-config">
                <el-row :gutter="16">
                  <el-col :span="8">
                    <el-form-item 
                      :prop="`fields.${index}.name`" 
                      :rules="fieldRules.name"
                      label="字段名称"
                    >
                      <el-input 
                        v-model="field.name" 
                        placeholder="请输入字段名称"
                        maxlength="20"
                      />
                    </el-form-item>
                  </el-col>
                  <el-col :span="8">
                    <el-form-item 
                      :prop="`fields.${index}.type`" 
                      :rules="fieldRules.type"
                      label="字段类型"
                    >
                      <el-select 
                        v-model="field.type" 
                        placeholder="请选择字段类型"
                        @change="onFieldTypeChange(field)"
                        style="width: 100%"
                      >
                        <el-option 
                          v-for="type in fieldTypes" 
                          :key="type.value" 
                          :label="type.label" 
                          :value="type.value"
                        />
                      </el-select>
                    </el-form-item>
                  </el-col>
                  <el-col :span="8">
                    <el-form-item label="是否必填">
                      <el-switch v-model="field.required" />
                    </el-form-item>
                  </el-col>
                </el-row>
                
                <el-form-item label="字段描述">
                  <el-input 
                    v-model="field.description" 
                    placeholder="请输入字段描述"
                    maxlength="100"
                  />
                </el-form-item>
                
                <el-form-item label="默认值" v-if="showDefaultValue(field.type)">
                  <el-input 
                    v-model="field.defaultValue" 
                    placeholder="请输入默认值"
                  />
                </el-form-item>
                
                <!-- 选项配置（仅选择类型字段） -->
                <div v-if="field.type === 'select'" class="options-config">
                  <div class="options-header">
                    <span>选项配置</span>
                    <el-button type="text" size="small" @click="addOption(field)">
                      <el-icon><Plus /></el-icon>
                      添加选项
                    </el-button>
                  </div>
                  <div class="options-list">
                    <div 
                      v-for="(option, optionIndex) in field.options" 
                      :key="option.id"
                      class="option-item"
                    >
                      <el-input 
                        v-model="option.label" 
                        placeholder="选项标签"
                        size="small"
                        style="margin-right: 8px;"
                      />
                      <el-input 
                        v-model="option.value" 
                        placeholder="选项值"
                        size="small"
                        style="margin-right: 8px;"
                      />
                      <el-button 
                        type="text" 
                        size="small" 
                        @click="removeOption(field, optionIndex)"
                        class="delete-btn"
                      >
                        <el-icon><Delete /></el-icon>
                      </el-button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            
            <div v-if="!templateForm.fields.length" class="no-fields">
              <el-empty description="暂无字段，请添加字段">
                <el-button type="primary" @click="addField">添加字段</el-button>
              </el-empty>
            </div>
          </div>
        </el-card>

        <!-- 预览区域 -->
        <el-card class="form-section" shadow="never">
          <template #header>
            <div class="section-header">
              <span class="section-title">模板预览</span>
            </div>
          </template>
          
          <div class="template-preview">
            <div class="preview-header">
              <h3>{{ templateForm.name || '模板名称' }}</h3>
              <p>{{ templateForm.description || '模板描述' }}</p>
            </div>
            <div class="preview-fields">
              <div 
                v-for="field in templateForm.fields" 
                :key="field.id"
                class="preview-field"
              >
                <label class="preview-label">
                  {{ field.name }}
                  <span v-if="field.required" class="required">*</span>
                </label>
                <div class="preview-input" :class="`preview-${field.type}`">
                  <span v-if="field.type === 'text'">文本输入框</span>
                  <span v-else-if="field.type === 'textarea'">多行文本框</span>
                  <span v-else-if="field.type === 'number'">数字输入框</span>
                  <span v-else-if="field.type === 'date'">日期选择器</span>
                  <span v-else-if="field.type === 'datetime'">日期时间选择器</span>
                  <span v-else-if="field.type === 'select'">下拉选择框</span>
                  <span v-else>{{ field.type }}</span>
                </div>
                <div v-if="field.description" class="preview-description">
                  {{ field.description }}
                </div>
              </div>
            </div>
          </div>
        </el-card>
      </el-form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ArrowLeft, Plus, ArrowUp, ArrowDown, Delete } from '@element-plus/icons-vue'

// 路由
const router = useRouter()

// 表单引用
const templateFormRef = ref()

// 响应式数据
const saving = ref(false)

// 表单数据
const templateForm = reactive({
  name: '',
  type: '',
  description: '',
  fields: []
})

// 模板类型选项
const templateTypes = ref([
  { label: '会议类', value: 'meeting' },
  { label: '公告类', value: 'announcement' },
  { label: '决策类', value: 'decision' },
  { label: '其他', value: 'other' }
])

// 字段类型选项
const fieldTypes = ref([
  { label: '单行文本', value: 'text' },
  { label: '多行文本', value: 'textarea' },
  { label: '数字', value: 'number' },
  { label: '日期', value: 'date' },
  { label: '日期时间', value: 'datetime' },
  { label: '下拉选择', value: 'select' }
])

// 表单验证规则
const templateRules = {
  name: [
    { required: true, message: '请输入模板名称', trigger: 'blur' },
    { min: 2, max: 50, message: '长度在 2 到 50 个字符', trigger: 'blur' }
  ],
  type: [
    { required: true, message: '请选择模板类型', trigger: 'change' }
  ]
}

const fieldRules = {
  name: [
    { required: true, message: '请输入字段名称', trigger: 'blur' },
    { min: 1, max: 20, message: '长度在 1 到 20 个字符', trigger: 'blur' }
  ],
  type: [
    { required: true, message: '请选择字段类型', trigger: 'change' }
  ]
}

// 生命周期
onMounted(() => {
  // 初始化时添加一个默认字段
  addField()
})

// 方法
const goBack = () => {
  router.back()
}

const addField = () => {
  const newField = {
    id: Date.now().toString(),
    name: '',
    type: '',
    required: false,
    description: '',
    defaultValue: '',
    options: []
  }
  templateForm.fields.push(newField)
}

const removeField = (index) => {
  templateForm.fields.splice(index, 1)
}

const moveFieldUp = (index) => {
  if (index > 0) {
    const field = templateForm.fields.splice(index, 1)[0]
    templateForm.fields.splice(index - 1, 0, field)
  }
}

const moveFieldDown = (index) => {
  if (index < templateForm.fields.length - 1) {
    const field = templateForm.fields.splice(index, 1)[0]
    templateForm.fields.splice(index + 1, 0, field)
  }
}

const onFieldTypeChange = (field) => {
  // 清空选项配置
  field.options = []
  field.defaultValue = ''
  
  // 如果是选择类型，添加默认选项
  if (field.type === 'select') {
    addOption(field)
  }
}

const addOption = (field) => {
  const newOption = {
    id: Date.now().toString(),
    label: '',
    value: ''
  }
  if (!field.options) {
    field.options = []
  }
  field.options.push(newOption)
}

const removeOption = (field, index) => {
  field.options.splice(index, 1)
}

const showDefaultValue = (fieldType) => {
  return ['text', 'textarea', 'number'].includes(fieldType)
}

const saveDraft = async () => {
  try {
    saving.value = true
    
    // TODO: 调用API保存草稿
    // await templateApi.saveDraft(templateForm)
    
    ElMessage.success('草稿保存成功')
  } catch (err) {
    console.error('保存草稿失败:', err)
    ElMessage.error('保存草稿失败')
  } finally {
    saving.value = false
  }
}

const saveTemplate = async () => {
  try {
    // 表单验证
    const valid = await templateFormRef.value.validate()
    if (!valid) return
    
    // 验证字段配置
    if (!templateForm.fields.length) {
      ElMessage.warning('请至少添加一个字段')
      return
    }
    
    // 验证字段完整性
    for (let i = 0; i < templateForm.fields.length; i++) {
      const field = templateForm.fields[i]
      if (!field.name || !field.type) {
        ElMessage.warning(`请完善第 ${i + 1} 个字段的配置`)
        return
      }
      
      // 验证选择类型字段的选项
      if (field.type === 'select') {
        if (!field.options || !field.options.length) {
          ElMessage.warning(`第 ${i + 1} 个字段缺少选项配置`)
          return
        }
        
        for (let j = 0; j < field.options.length; j++) {
          const option = field.options[j]
          if (!option.label || !option.value) {
            ElMessage.warning(`第 ${i + 1} 个字段的第 ${j + 1} 个选项配置不完整`)
            return
          }
        }
      }
    }
    
    saving.value = true
    
    // TODO: 调用API保存模板
    // await templateApi.create(templateForm)
    
    ElMessage.success('模板创建成功')
    router.push({ name: 'MajorEventTemplateManager' })
  } catch (err) {
    console.error('保存模板失败:', err)
    ElMessage.error('保存模板失败')
  } finally {
    saving.value = false
  }
}
</script>

<style scoped>
.create-major-event-template {
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

.form-container {
  max-width: 1200px;
  margin: 0 auto;
}

.form-section {
  margin-bottom: 20px;
  border: none;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.fields-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.field-item {
  padding: 20px;
  background: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #e4e7ed;
}

.field-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.field-index {
  font-weight: 600;
  color: #303133;
}

.field-actions {
  display: flex;
  gap: 4px;
}

.delete-btn {
  color: #f56c6c;
}

.delete-btn:hover {
  color: #f56c6c;
}

.field-config {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.options-config {
  padding: 16px;
  background: white;
  border-radius: 6px;
  border: 1px solid #dcdfe6;
}

.options-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  font-weight: 600;
  color: #303133;
}

.options-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.option-item {
  display: flex;
  align-items: center;
}

.no-fields {
  text-align: center;
  padding: 40px;
}

.template-preview {
  padding: 20px;
  background: #f8f9fa;
  border-radius: 8px;
  border: 1px dashed #dcdfe6;
}

.preview-header {
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid #e4e7ed;
}

.preview-header h3 {
  margin: 0 0 8px 0;
  color: #303133;
}

.preview-header p {
  margin: 0;
  color: #606266;
  font-size: 14px;
}

.preview-fields {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.preview-field {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.preview-label {
  font-weight: 600;
  color: #303133;
}

.preview-label .required {
  color: #f56c6c;
  margin-left: 4px;
}

.preview-input {
  padding: 8px 12px;
  background: white;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  color: #909399;
  font-size: 14px;
}

.preview-description {
  font-size: 12px;
  color: #909399;
}
</style>