<template>
  <div class="base-setting-view">
    <!-- 页面标题 -->
    <div class="page-header">
      <h1 class="page-title">基础设置</h1>
      <p class="page-description">查看和管理项目的基础配置信息</p>
    </div>

    <!-- 加载状态 -->
    <div v-if="baseSettingStore.loading" class="loading-container">
      <div class="loading-spinner"></div>
      <p>正在加载基础设置数据...</p>
    </div>

    <!-- 错误状态 -->
    <div v-else-if="baseSettingStore.hasError" class="error-container">
      <div class="error-message">
        <i class="error-icon">⚠️</i>
        <p>{{ baseSettingStore.error }}</p>
        <button @click="handleReload" class="reload-btn">重新加载</button>
      </div>
    </div>

    <!-- 主要内容 -->
    <div v-else class="content-container">
      <!-- 企业基本信息区域 -->
      <section class="info-section">
        <div class="section-header">
          <h2 class="section-title">企业基本信息</h2>
        </div>
        <div class="section-content">
          <!-- 企业名称（只读） -->
          <div class="form-group">
            <label class="form-label">企业名称</label>
            <div class="readonly-field">
              {{ baseSettingStore.companyBasicInfo.companyName }}
            </div>
          </div>

          <!-- 企业简称列表（支持CRUD） -->
          <div class="form-group">
            <label class="form-label">
              企业简称
              <span class="alias-count">({{ baseSettingStore.aliasCount }}个)</span>
            </label>
            
            <!-- 简称列表 -->
            <div class="alias-list">
              <div 
                v-for="(alias, index) in baseSettingStore.companyBasicInfo.companyAliases" 
                :key="index"
                class="alias-item"
              >
                <input 
                  v-if="editingIndex === index"
                  v-model="editingAlias"
                  @keyup.enter="handleSaveEdit(index)"
                  @keyup.escape="handleCancelEdit"
                  @blur="handleSaveEdit(index)"
                  class="alias-input"
                  ref="editInput"
                />
                <span v-else class="alias-text">{{ alias }}</span>
                
                <div class="alias-actions">
                  <button 
                    v-if="editingIndex !== index"
                    @click="handleStartEdit(index, alias)"
                    class="action-btn edit-btn"
                    title="编辑"
                  >
                    ✏️
                  </button>
                  <button 
                    v-if="editingIndex === index"
                    @click="handleSaveEdit(index)"
                    class="action-btn save-btn"
                    title="保存"
                  >
                    ✅
                  </button>
                  <button 
                    v-if="editingIndex === index"
                    @click="handleCancelEdit"
                    class="action-btn cancel-btn"
                    title="取消"
                  >
                    ❌
                  </button>
                  <button 
                    v-if="editingIndex !== index"
                    @click="handleDeleteAlias(index)"
                    class="action-btn delete-btn"
                    title="删除"
                  >
                    🗑️
                  </button>
                </div>
              </div>
            </div>

            <!-- 添加新简称 -->
            <div class="add-alias-container">
              <div v-if="!showAddForm" class="add-alias-trigger">
                <button @click="handleShowAddForm" class="add-btn">
                  + 添加简称
                </button>
              </div>
              <div v-else class="add-alias-form">
                <input 
                  v-model="newAlias"
                  @keyup.enter="handleAddAlias"
                  @keyup.escape="handleCancelAdd"
                  placeholder="请输入企业简称"
                  class="alias-input"
                  ref="addInput"
                />
                <div class="add-alias-actions">
                  <button @click="handleAddAlias" class="action-btn save-btn">✅</button>
                  <button @click="handleCancelAdd" class="action-btn cancel-btn">❌</button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- 企业属性信息区域（所有字段只读） -->
      <section class="info-section">
        <div class="section-header">
          <h2 class="section-title">企业属性信息</h2>
        </div>
        <div class="section-content">
          <div class="readonly-grid">
            <div class="form-group">
              <label class="form-label">财务报表年份</label>
              <div class="readonly-field">
                {{ baseSettingStore.companyAttributes.financialYear }}
              </div>
            </div>
            
            <div class="form-group">
              <label class="form-label">是否为境内企业</label>
              <div class="readonly-field">
                {{ baseSettingStore.companyAttributes.isDomestic ? '是' : '否' }}
              </div>
            </div>
            
            <div class="form-group">
              <label class="form-label">企业规模</label>
              <div class="readonly-field">
                {{ baseSettingStore.companyAttributes.companySize }}
              </div>
            </div>
            
            <div class="form-group">
              <label class="form-label">所属行业</label>
              <div class="readonly-field">
                {{ baseSettingStore.companyAttributes.industry }}
              </div>
            </div>
            
            <div class="form-group">
              <label class="form-label">上市情况</label>
              <div class="readonly-field">
                {{ baseSettingStore.listingStatusText }}
              </div>
            </div>
            
            <div class="form-group">
              <label class="form-label">是否为国有企业</label>
              <div class="readonly-field">
                {{ baseSettingStore.companyAttributes.isStateOwned ? '是' : '否' }}
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- 审计依据方案区域（所有字段只读） -->
      <section class="info-section">
        <div class="section-header">
          <h2 class="section-title">审计依据方案</h2>
        </div>
        <div class="section-content">
          <!-- 方案基本信息 -->
          <div class="subsection">
            <h3 class="subsection-title">方案基本信息</h3>
            <div class="readonly-grid">
              <div class="form-group">
                <label class="form-label">方案标识</label>
                <div class="readonly-field">
                  {{ baseSettingStore.auditBasisScheme.schemeId }}
                </div>
              </div>
              <div class="form-group full-width">
                <label class="form-label">适用企业类型说明</label>
                <div class="readonly-field">
                  {{ baseSettingStore.auditBasisScheme.applicableCompanyType }}
                </div>
              </div>
            </div>
          </div>

          <!-- 方案构成详情 -->
          <div class="subsection">
            <h3 class="subsection-title">方案构成详情</h3>
            
            <!-- 会计准则 -->
            <div class="regulation-category">
              <h4 class="category-title">会计准则</h4>
              <div class="regulation-list">
                <div 
                  v-for="standard in baseSettingStore.auditBasisScheme.accountingStandards" 
                  :key="standard.id"
                  class="regulation-item"
                  @click="handleShowRegulationDetail('accountingStandards', standard.id)"
                >
                  {{ standard.name }}
                </div>
              </div>
            </div>

            <!-- 审计准则 -->
            <div class="regulation-category">
              <h4 class="category-title">审计准则</h4>
              <div class="regulation-list">
                <div 
                  v-for="standard in baseSettingStore.auditBasisScheme.auditingStandards" 
                  :key="standard.id"
                  class="regulation-item"
                  @click="handleShowRegulationDetail('auditingStandards', standard.id)"
                >
                  {{ standard.name }}
                </div>
              </div>
            </div>

            <!-- 基础法律 -->
            <div class="regulation-category">
              <h4 class="category-title">基础法律</h4>
              <div class="regulation-list">
                <div 
                  v-for="law in baseSettingStore.auditBasisScheme.basicLaws" 
                  :key="law.id"
                  class="regulation-item"
                  @click="handleShowRegulationDetail('basicLaws', law.id)"
                >
                  {{ law.name }}
                </div>
              </div>
            </div>

            <!-- 专项法规 -->
            <div class="regulation-category">
              <h4 class="category-title">专项法规</h4>
              <div class="regulation-list">
                <div 
                  v-for="regulation in baseSettingStore.auditBasisScheme.specialRegulations" 
                  :key="regulation.id"
                  class="regulation-item"
                  @click="handleShowRegulationDetail('specialRegulations', regulation.id)"
                >
                  {{ regulation.name }}
                </div>
              </div>
            </div>

            <!-- 基础监管规范 -->
            <div class="regulation-category">
              <h4 class="category-title">基础监管规范</h4>
              <div class="regulation-list">
                <div 
                  v-for="standard in baseSettingStore.auditBasisScheme.basicRegulatoryStandards" 
                  :key="standard.id"
                  class="regulation-item"
                  @click="handleShowRegulationDetail('basicRegulatoryStandards', standard.id)"
                >
                  {{ standard.name }}
                </div>
              </div>
            </div>

            <!-- 专项监管规范 -->
            <div class="regulation-category">
              <h4 class="category-title">专项监管规范</h4>
              <div class="regulation-list">
                <div 
                  v-for="standard in baseSettingStore.auditBasisScheme.specialRegulatoryStandards" 
                  :key="standard.id"
                  class="regulation-item"
                  @click="handleShowRegulationDetail('specialRegulatoryStandards', standard.id)"
                >
                  {{ standard.name }}
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>

    <!-- 条文详情弹窗 -->
    <div v-if="showRegulationDetail" class="modal-overlay" @click="handleCloseRegulationDetail">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3 class="modal-title">条文详细信息</h3>
          <button @click="handleCloseRegulationDetail" class="close-btn">×</button>
        </div>
        <div class="modal-body">
          <div v-if="loadingRegulationDetail" class="loading-text">
            正在加载条文详情...
          </div>
          <div v-else-if="regulationDetail">
            <div class="detail-item">
              <label class="detail-label">条文名称</label>
              <div class="detail-value">{{ regulationDetail.name }}</div>
            </div>
            <div class="detail-item">
              <label class="detail-label">发文机构</label>
              <div class="detail-value">{{ regulationDetail.issuer }}</div>
            </div>
            <div class="detail-item">
              <label class="detail-label">发文时间</label>
              <div class="detail-value">{{ regulationDetail.issueDate }}</div>
            </div>
            <div class="detail-item">
              <label class="detail-label">条文内容</label>
              <div class="detail-content">
                <div 
                  class="content-text"
                  :class="{ 'expanded': contentExpanded }"
                >
                  {{ regulationDetail.content }}
                </div>
                <button 
                  @click="contentExpanded = !contentExpanded"
                  class="expand-btn"
                >
                  {{ contentExpanded ? '收起' : '展开' }}
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 消息提示 -->
    <div v-if="message" class="message-toast" :class="messageType">
      {{ message }}
    </div>
  </div>
</template>

<script>
import { useBaseSettingStore } from '@/stores/baseSetting'
import { onMounted, ref, nextTick } from 'vue'

export default {
  name: 'BaseSettingView',
  setup() {
    // 使用基础设置store
    const baseSettingStore = useBaseSettingStore()
    
    // 企业简称编辑相关状态
    const editingIndex = ref(-1) // 当前编辑的简称索引
    const editingAlias = ref('') // 编辑中的简称值
    const showAddForm = ref(false) // 是否显示添加表单
    const newAlias = ref('') // 新增简称值
    
    // 条文详情弹窗相关状态
    const showRegulationDetail = ref(false)
    const loadingRegulationDetail = ref(false)
    const regulationDetail = ref(null)
    const contentExpanded = ref(false)
    
    // 消息提示相关状态
    const message = ref('')
    const messageType = ref('info') // 'success', 'error', 'info'
    
    // DOM引用
    const editInput = ref(null)
    const addInput = ref(null)
    
    /**
     * 组件挂载时获取数据
     */
    onMounted(async () => {
      await baseSettingStore.fetchBaseSettingData()
    })
    
    /**
     * 重新加载数据
     */
    const handleReload = async () => {
      baseSettingStore.clearError()
      await baseSettingStore.reloadData()
    }
    
    /**
     * 开始编辑简称
     */
    const handleStartEdit = async (index, alias) => {
      editingIndex.value = index
      editingAlias.value = alias
      await nextTick()
      // 聚焦到编辑输入框
      if (editInput.value && editInput.value[0]) {
        editInput.value[0].focus()
        editInput.value[0].select()
      }
    }
    
    /**
     * 保存编辑的简称
     */
    const handleSaveEdit = async (index) => {
      if (editingAlias.value.trim() === '') {
        showMessage('企业简称不能为空', 'error')
        return
      }
      
      try {
        await baseSettingStore.updateCompanyAlias(index, editingAlias.value)
        editingIndex.value = -1
        editingAlias.value = ''
        showMessage('企业简称更新成功', 'success')
      } catch (error) {
        showMessage(error.message, 'error')
      }
    }
    
    /**
     * 取消编辑简称
     */
    const handleCancelEdit = () => {
      editingIndex.value = -1
      editingAlias.value = ''
    }
    
    /**
     * 删除简称
     */
    const handleDeleteAlias = async (index) => {
      if (confirm('确定要删除这个企业简称吗？')) {
        try {
          await baseSettingStore.deleteCompanyAlias(index)
          showMessage('企业简称删除成功', 'success')
        } catch (error) {
          showMessage(error.message, 'error')
        }
      }
    }
    
    /**
     * 显示添加简称表单
     */
    const handleShowAddForm = async () => {
      showAddForm.value = true
      newAlias.value = ''
      await nextTick()
      // 聚焦到添加输入框
      if (addInput.value) {
        addInput.value.focus()
      }
    }
    
    /**
     * 添加新简称
     */
    const handleAddAlias = async () => {
      if (newAlias.value.trim() === '') {
        showMessage('企业简称不能为空', 'error')
        return
      }
      
      try {
        await baseSettingStore.addCompanyAlias(newAlias.value)
        showAddForm.value = false
        newAlias.value = ''
        showMessage('企业简称添加成功', 'success')
      } catch (error) {
        showMessage(error.message, 'error')
      }
    }
    
    /**
     * 取消添加简称
     */
    const handleCancelAdd = () => {
      showAddForm.value = false
      newAlias.value = ''
    }
    
    /**
     * 显示条文详情
     */
    const handleShowRegulationDetail = async (type, itemId) => {
      showRegulationDetail.value = true
      loadingRegulationDetail.value = true
      regulationDetail.value = null
      contentExpanded.value = false
      
      try {
        const detail = await baseSettingStore.getRegulationDetail(type, itemId)
        regulationDetail.value = detail
      } catch (error) {
        showMessage(error.message, 'error')
        showRegulationDetail.value = false
      } finally {
        loadingRegulationDetail.value = false
      }
    }
    
    /**
     * 关闭条文详情弹窗
     */
    const handleCloseRegulationDetail = () => {
      showRegulationDetail.value = false
      regulationDetail.value = null
      contentExpanded.value = false
    }
    
    /**
     * 显示消息提示
     */
    const showMessage = (msg, type = 'info') => {
      message.value = msg
      messageType.value = type
      
      // 3秒后自动隐藏消息
      setTimeout(() => {
        message.value = ''
      }, 3000)
    }
    
    return {
      baseSettingStore,
      editingIndex,
      editingAlias,
      showAddForm,
      newAlias,
      showRegulationDetail,
      loadingRegulationDetail,
      regulationDetail,
      contentExpanded,
      message,
      messageType,
      editInput,
      addInput,
      handleReload,
      handleStartEdit,
      handleSaveEdit,
      handleCancelEdit,
      handleDeleteAlias,
      handleShowAddForm,
      handleAddAlias,
      handleCancelAdd,
      handleShowRegulationDetail,
      handleCloseRegulationDetail
    }
  }
}
</script>

<style scoped>
/* 基础设置页面样式 */
.base-setting-view {
  padding: 24px;
  max-width: 1200px;
  margin: 0 auto;
  background-color: #f8fafc;
  min-height: 100vh;
}

/* 页面标题区域 */
.page-header {
  margin-bottom: 32px;
  padding: 24px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px;
  color: white;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.page-title {
  margin: 0 0 8px 0;
  font-size: 28px;
  font-weight: 600;
}

.page-description {
  margin: 0;
  font-size: 16px;
  opacity: 0.9;
}

/* 加载状态 */
.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  text-align: center;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #e2e8f0;
  border-top: 4px solid #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 16px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* 错误状态 */
.error-container {
  display: flex;
  justify-content: center;
  padding: 60px 20px;
}

.error-message {
  background: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: 8px;
  padding: 24px;
  text-align: center;
  max-width: 400px;
}

.error-icon {
  font-size: 24px;
  margin-bottom: 12px;
  display: block;
}

.reload-btn {
  background: #dc2626;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
  margin-top: 12px;
  transition: background-color 0.2s;
}

.reload-btn:hover {
  background: #b91c1c;
}

/* 主要内容区域 */
.content-container {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

/* 信息区块 */
.info-section {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  overflow: hidden;
  border: 1px solid #e2e8f0;
}

.section-header {
  background: #f8fafc;
  padding: 20px 24px;
  border-bottom: 1px solid #e2e8f0;
}

.section-title {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  color: #1e293b;
}

.section-content {
  padding: 24px;
}

/* 表单组件 */
.form-group {
  margin-bottom: 20px;
}

.form-group:last-child {
  margin-bottom: 0;
}

.form-label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: #374151;
  font-size: 14px;
}

.readonly-field {
  background: #f9fafb;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  padding: 12px;
  color: #6b7280;
  font-size: 14px;
  min-height: 20px;
}

.readonly-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
}

.full-width {
  grid-column: 1 / -1;
}

/* 企业简称相关样式 */
.alias-count {
  color: #6b7280;
  font-weight: normal;
  font-size: 12px;
}

.alias-list {
  margin-bottom: 16px;
}

.alias-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px;
  background: #f9fafb;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  margin-bottom: 8px;
  transition: all 0.2s;
}

.alias-item:hover {
  background: #f3f4f6;
  border-color: #d1d5db;
}

.alias-text {
  flex: 1;
  color: #374151;
  font-size: 14px;
}

.alias-input {
  flex: 1;
  border: 1px solid #d1d5db;
  border-radius: 4px;
  padding: 8px 12px;
  font-size: 14px;
  margin-right: 12px;
  outline: none;
  transition: border-color 0.2s;
}

.alias-input:focus {
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.alias-actions {
  display: flex;
  gap: 4px;
}

.action-btn {
  background: none;
  border: none;
  padding: 4px 8px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.2s;
}

.action-btn:hover {
  background: #e5e7eb;
}

.edit-btn:hover {
  background: #dbeafe;
}

.save-btn:hover {
  background: #dcfce7;
}

.cancel-btn:hover {
  background: #fef2f2;
}

.delete-btn:hover {
  background: #fef2f2;
}

/* 添加简称相关样式 */
.add-alias-container {
  margin-top: 12px;
}

.add-btn {
  background: #667eea;
  color: white;
  border: none;
  padding: 10px 16px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.2s;
}

.add-btn:hover {
  background: #5a67d8;
}

.add-alias-form {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px;
  background: #f0f9ff;
  border: 1px solid #bae6fd;
  border-radius: 6px;
}

.add-alias-actions {
  display: flex;
  gap: 4px;
}

/* 子区块样式 */
.subsection {
  margin-bottom: 32px;
}

.subsection:last-child {
  margin-bottom: 0;
}

.subsection-title {
  margin: 0 0 16px 0;
  font-size: 18px;
  font-weight: 600;
  color: #1e293b;
  padding-bottom: 8px;
  border-bottom: 2px solid #e2e8f0;
}

/* 条文分类样式 */
.regulation-category {
  margin-bottom: 24px;
}

.category-title {
  margin: 0 0 12px 0;
  font-size: 16px;
  font-weight: 500;
  color: #374151;
}

.regulation-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 8px;
}

.regulation-item {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  padding: 12px;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 14px;
  color: #374151;
}

.regulation-item:hover {
  background: #e0e7ff;
  border-color: #c7d2fe;
  color: #3730a3;
  transform: translateY(-1px);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

/* 弹窗样式 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
}

.modal-content {
  background: white;
  border-radius: 12px;
  max-width: 600px;
  width: 100%;
  max-height: 80vh;
  overflow: hidden;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 24px;
  border-bottom: 1px solid #e2e8f0;
  background: #f8fafc;
}

.modal-title {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #1e293b;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #6b7280;
  padding: 0;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  transition: all 0.2s;
}

.close-btn:hover {
  background: #e5e7eb;
  color: #374151;
}

.modal-body {
  padding: 24px;
  overflow-y: auto;
  max-height: calc(80vh - 80px);
}

.loading-text {
  text-align: center;
  color: #6b7280;
  padding: 40px 20px;
}

/* 详情项样式 */
.detail-item {
  margin-bottom: 20px;
}

.detail-item:last-child {
  margin-bottom: 0;
}

.detail-label {
  display: block;
  margin-bottom: 8px;
  font-weight: 600;
  color: #374151;
  font-size: 14px;
}

.detail-value {
  color: #6b7280;
  font-size: 14px;
  line-height: 1.5;
}

.detail-content {
  position: relative;
}

.content-text {
  color: #6b7280;
  font-size: 14px;
  line-height: 1.6;
  max-height: 120px;
  overflow: hidden;
  transition: max-height 0.3s ease;
}

.content-text.expanded {
  max-height: none;
}

.expand-btn {
  background: #667eea;
  color: white;
  border: none;
  padding: 6px 12px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  margin-top: 8px;
  transition: background-color 0.2s;
}

.expand-btn:hover {
  background: #5a67d8;
}

/* 消息提示样式 */
.message-toast {
  position: fixed;
  top: 20px;
  right: 20px;
  padding: 12px 20px;
  border-radius: 6px;
  color: white;
  font-size: 14px;
  z-index: 1001;
  animation: slideIn 0.3s ease;
  max-width: 300px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.message-toast.success {
  background: #10b981;
}

.message-toast.error {
  background: #ef4444;
}

.message-toast.info {
  background: #3b82f6;
}

@keyframes slideIn {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .base-setting-view {
    padding: 16px;
  }
  
  .page-header {
    padding: 20px;
    margin-bottom: 24px;
  }
  
  .page-title {
    font-size: 24px;
  }
  
  .section-content {
    padding: 20px;
  }
  
  .readonly-grid {
    grid-template-columns: 1fr;
  }
  
  .regulation-list {
    grid-template-columns: 1fr;
  }
  
  .modal-content {
    margin: 10px;
    max-height: 90vh;
  }
  
  .alias-item {
    flex-direction: column;
    align-items: stretch;
    gap: 8px;
  }
  
  .alias-actions {
    justify-content: flex-end;
  }
  
  .add-alias-form {
    flex-direction: column;
    align-items: stretch;
    gap: 12px;
  }
  
  .add-alias-actions {
    justify-content: flex-end;
  }
}

@media (max-width: 480px) {
  .base-setting-view {
    padding: 12px;
  }
  
  .page-header {
    padding: 16px;
  }
  
  .section-content {
    padding: 16px;
  }
  
  .message-toast {
    right: 12px;
    left: 12px;
    max-width: none;
  }
}
</style>