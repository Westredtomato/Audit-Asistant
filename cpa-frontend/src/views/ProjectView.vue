<template>
  <!-- 项目管理主页面 - 企业审计项目的统一入口-->
  <div class="project-view">
    <!-- 页面头部：标题和欢迎信息 -->
    <div class="project-header">
      <h1>项目管理</h1>
      <!-- 显示当前登录用户名，使用可选链操作符防止undefined错误 -->
      <p class="welcome-text">欢迎, {{ authStore.user?.username }}！请选择一个项目进入工作台</p>
    </div>
    
    <!-- 操作按钮区域 -->
    <div class="project-actions">
      <!-- 创建新项目按钮：点击开始创建流程 -->
      <button @click="startCreateProject" class="create-btn">
        <i class="icon">+</i> 创建新项目
      </button>
      <!-- 刷新项目列表按钮：重新获取项目数据 -->
      <button @click="loadProjects" class="refresh-btn">
        <i class="icon">↻</i> 刷新项目
      </button>
    </div>

    <!-- 项目创建流程模态框：多步骤创建流程 -->
    <div v-if="showCreateForm" class="create-form-overlay">
      <div class="create-form">
        <!-- 创建流程步骤指示器 -->
        <div class="step-indicator">
          <div class="step" :class="{ active: projectStore.createStep >= 1, completed: projectStore.createStep > 1 }">
            <span class="step-number">1</span>
            <span class="step-label">企业信息</span>
          </div>
          <div class="step-line" :class="{ completed: projectStore.createStep > 1 }"></div>
          <div class="step" :class="{ active: projectStore.createStep >= 2, completed: projectStore.createStep > 2 }">
            <span class="step-number">2</span>
            <span class="step-label">企业属性</span>
          </div>
          <div class="step-line" :class="{ completed: projectStore.createStep > 2 }"></div>
          <div class="step" :class="{ active: projectStore.createStep >= 3 }">
            <span class="step-number">3</span>
            <span class="step-label">审计依据</span>
          </div>
        </div>

        <!-- 步骤1：企业基本信息录入 -->
        <div v-if="projectStore.createStep === 1" class="step-content">
          <h3>企业基本信息</h3>
          <form @submit.prevent="nextStep">
            <!-- 企业名称输入 -->
            <div class="form-group">
              <label>企业名称 <span class="required">*</span>:</label>
              <input 
                v-model="projectStore.enterpriseInfo.name" 
                type="text" 
                placeholder="请输入企业名称"
                :class="{ error: projectStore.validationErrors.name }"
                @input="validateNameInput"
              />
              <span v-if="projectStore.validationErrors.name" class="error-message">
                {{ projectStore.validationErrors.name }}
              </span>
            </div>
            
            <!-- 企业简称输入（支持多个） -->
            <div class="form-group">
              <label>企业简称 <span class="required">*</span>:</label>
              <div v-for="(shortName, index) in projectStore.enterpriseInfo.shortNames" :key="index" class="short-name-item">
                <input 
                  v-model="projectStore.enterpriseInfo.shortNames[index]" 
                  type="text" 
                  :placeholder="`企业简称 ${index + 1}`"
                  :class="{ error: projectStore.validationErrors.shortNames }"
                  @input="validateShortNameInput"
                />
                <!-- 删除简称按钮（至少保留一个） -->
                <button 
                  v-if="projectStore.enterpriseInfo.shortNames.length > 1" 
                  type="button" 
                  @click="removeShortName(index)" 
                  class="remove-btn"
                >
                  ×
                </button>
              </div>
              <!-- 添加简称按钮 -->
              <button type="button" @click="addShortName" class="add-btn">
                + 添加简称
              </button>
              <span v-if="projectStore.validationErrors.shortNames" class="error-message">
                {{ projectStore.validationErrors.shortNames }}
              </span>
            </div>
            
            <!-- 表单操作按钮 -->
            <div class="form-actions">
              <button type="button" @click="cancelCreate" class="cancel-btn">取消</button>
              <button type="submit" class="next-btn">下一步</button>
            </div>
          </form>
        </div>

        <!-- 步骤2：企业属性选择 -->
        <div v-if="projectStore.createStep === 2" class="step-content">
          <h3>企业属性信息</h3>
          <form @submit.prevent="nextStep">
            <!-- 财务报表年份选择 -->
            <div class="form-group">
              <label>财务报表年份 <span class="required">*</span>:</label>
              <select 
                v-model="projectStore.enterpriseAttributes.reportYear" 
                :class="{ error: projectStore.validationErrors.reportYear }"
                @change="validateAttributeInput('reportYear')"
              >
                <option value="">请选择年份</option>
                <option v-for="year in reportYears" :key="year" :value="year">{{ year }}年</option>
              </select>
              <span v-if="projectStore.validationErrors.reportYear" class="error-message">
                {{ projectStore.validationErrors.reportYear }}
              </span>
            </div>
            
            <!-- 是否为境内企业 -->
            <div class="form-group checkbox-group">
              <label class="checkbox-label">
                <input 
                  type="checkbox" 
                  v-model="projectStore.enterpriseAttributes.isDomestic"
                />
                <span class="checkmark"></span>
                是否为境内企业
              </label>
            </div>
            
            <!-- 企业规模选择 -->
            <div class="form-group">
              <label>企业规模 <span class="required">*</span>:</label>
              <select 
                v-model="projectStore.enterpriseAttributes.scale" 
                :class="{ error: projectStore.validationErrors.scale }"
                @change="validateAttributeInput('scale')"
              >
                <option value="">请选择企业规模</option>
                <option value="大型">大型企业</option>
                <option value="中型">中型企业</option>
                <option value="小型">小型企业</option>
                <option value="微型">微型企业</option>
              </select>
              <span v-if="projectStore.validationErrors.scale" class="error-message">
                {{ projectStore.validationErrors.scale }}
              </span>
            </div>
            
            <!-- 所属行业选择 -->
            <div class="form-group">
              <label>所属行业 <span class="required">*</span>:</label>
              <select 
                v-model="projectStore.enterpriseAttributes.industry" 
                :class="{ error: projectStore.validationErrors.industry }"
                @change="validateAttributeInput('industry')"
              >
                <option value="">请选择行业</option>
                <option value="制造业">制造业</option>
                <option value="金融业">金融业</option>
                <option value="房地产业">房地产业</option>
                <option value="批发和零售业">批发和零售业</option>
                <option value="建筑业">建筑业</option>
                <option value="信息技术业">信息技术业</option>
                <option value="其他">其他</option>
              </select>
              <span v-if="projectStore.validationErrors.industry" class="error-message">
                {{ projectStore.validationErrors.industry }}
              </span>
            </div>
            
            <!-- 上市情况选择 -->
            <div class="form-group">
              <label>上市情况 <span class="required">*</span>:</label>
              <select 
                v-model="projectStore.enterpriseAttributes.listingStatus" 
                :class="{ error: projectStore.validationErrors.listingStatus }"
                @change="validateAttributeInput('listingStatus')"
              >
                <option value="">请选择上市情况</option>
                <option value="未上市">未上市</option>
                <option value="境内上市">境内上市</option>
                <option value="境外上市">境外上市</option>
              </select>
              <span v-if="projectStore.validationErrors.listingStatus" class="error-message">
                {{ projectStore.validationErrors.listingStatus }}
              </span>
            </div>
            
            <!-- 上市地点选择（条件显示） -->
            <div v-if="isListed" class="form-group">
              <label>上市地点 <span class="required">*</span>:</label>
              <select 
                v-model="projectStore.enterpriseAttributes.listingLocation" 
                :class="{ error: projectStore.validationErrors.listingLocation }"
                @change="validateAttributeInput('listingLocation')"
              >
                <option value="">请选择上市地点</option>
                <template v-if="projectStore.enterpriseAttributes.listingStatus === '境内上市'">
                  <option value="上海证券交易所">上海证券交易所</option>
                  <option value="深圳证券交易所">深圳证券交易所</option>
                  <option value="北京证券交易所">北京证券交易所</option>
                </template>
                <template v-if="projectStore.enterpriseAttributes.listingStatus === '境外上市'">
                  <option value="香港联交所">香港联交所</option>
                  <option value="纽约证券交易所">纽约证券交易所</option>
                  <option value="纳斯达克">纳斯达克</option>
                  <option value="伦敦证券交易所">伦敦证券交易所</option>
                  <option value="其他">其他</option>
                </template>
              </select>
              <span v-if="projectStore.validationErrors.listingLocation" class="error-message">
                {{ projectStore.validationErrors.listingLocation }}
              </span>
            </div>
            
            <!-- 是否为国有企业 -->
            <div class="form-group checkbox-group">
              <label class="checkbox-label">
                <input 
                  type="checkbox" 
                  v-model="projectStore.enterpriseAttributes.isStateOwned"
                />
                <span class="checkmark"></span>
                是否为国有企业
              </label>
            </div>
            
            <!-- 表单操作按钮 -->
            <div class="form-actions">
              <button type="button" @click="prevStep" class="prev-btn">上一步</button>
              <button type="button" @click="cancelCreate" class="cancel-btn">取消</button>
              <button type="submit" class="next-btn">下一步</button>
            </div>
          </form>
        </div>

        <!-- 步骤3：审计依据方案推荐 -->
        <div v-if="projectStore.createStep === 3" class="step-content">
          <h3>审计依据方案</h3>
          
          <!-- 加载推荐方案 -->
          <div v-if="projectStore.loading" class="loading-standards">
            <div class="spinner"></div>
            <p>正在为您推荐审计依据方案...</p>
          </div>
          
          <!-- 推荐方案列表 -->
          <div v-else-if="projectStore.auditStandards.length > 0" class="standards-list">
            <p class="standards-intro">根据您的企业属性，系统为您推荐以下审计依据方案：</p>
            
            <div v-for="(standard, index) in projectStore.auditStandards" :key="index" class="standard-option">
              <label class="standard-label">
                <input 
                  type="radio" 
                  :value="standard" 
                  v-model="projectStore.selectedStandards"
                  name="auditStandards"
                />
                <div class="standard-content">
                  <h4>推荐方案 {{ index + 1 }}</h4>
                  <div class="standard-details">
                    <div class="standard-item">
                      <strong>会计准则：</strong>{{ standard.accountingStandards }}
                    </div>
                    <div class="standard-item">
                      <strong>审计准则：</strong>{{ standard.auditingStandards }}
                    </div>
                    <div class="standard-item">
                      <strong>基础法律：</strong>{{ standard.basicLaws.join('、') }}
                    </div>
                    <div v-if="standard.specialRegulations.length > 0" class="standard-item">
                      <strong>专项法规：</strong>{{ standard.specialRegulations.join('、') }}
                    </div>
                    <div class="standard-item">
                      <strong>基础监管规范：</strong>{{ standard.basicSupervision.join('、') }}
                    </div>
                    <div v-if="standard.specialSupervision.length > 0" class="standard-item">
                      <strong>专项监管规范：</strong>{{ standard.specialSupervision.join('、') }}
                    </div>
                  </div>
                </div>
              </label>
            </div>
          </div>
          
          <!-- 无推荐方案 -->
          <div v-else class="no-standards">
            <div class="no-standards-icon">⚠️</div>
            <h4>当前企业类型暂不支持</h4>
            <p>很抱歉，系统暂时无法为您的企业类型推荐合适的审计依据方案。</p>
            <p>请联系管理员获取帮助。</p>
          </div>
          
          <!-- 表单操作按钮 -->
          <div class="form-actions">
            <button type="button" @click="prevStep" class="prev-btn">上一步</button>
            <button type="button" @click="cancelCreate" class="cancel-btn">取消</button>
            <button 
              v-if="projectStore.auditStandards.length > 0" 
              type="button" 
              @click="createProject" 
              :disabled="!projectStore.selectedStandards || projectStore.loading"
              class="create-btn"
            >
              {{ projectStore.loading ? '创建中...' : '创建项目' }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 项目内容主区域 -->
    <div class="project-content">
      <!-- 加载状态：当projectStore.loading为true时显示 -->
      <div v-if="projectStore.loading" class="loading">
        <div class="spinner"></div>
        <p>加载中...</p>
      </div>
      <!-- 错误状态：当有错误且不在加载中时显示 -->
      <div v-else-if="projectStore.error" class="error">
        <p>错误: {{ projectStore.error }}</p>
        <!-- 重试按钮：点击重新加载项目列表 -->
        <button @click="loadProjects" class="retry-btn">重试</button>
      </div>
      <!-- 正常状态：数据加载成功且无错误时显示 -->
      <div v-else>
        <!-- 项目统计卡片区域 -->
        <div class="project-stats">
          <div class="stat-card">
            <!-- 显示项目总数：来自store的计算属性 -->
            <h3>{{ projectStore.projectCount }}</h3>
            <p>项目总数</p>
          </div>
          <div class="stat-card">
            <!-- 显示活跃项目数：来自本地计算属性 -->
            <h3>{{ activeProjectsCount }}</h3>
            <p>活跃项目</p>
          </div>
        </div>
        
        <!-- 项目网格布局：显示所有项目卡片 -->
        <div class="project-grid">
          <!-- 项目卡片循环：遍历store中的projects数组 -->
          <div 
            v-for="project in projectStore.projects" 
            :key="project.id"
            class="project-card"
            @click="selectProject(project)"
          >
            <!-- 项目名称：直接显示在卡片顶部 -->
            <h3 class="project-title">{{ project.name }}</h3>
            <!-- 状态徽章：动态class绑定项目状态，显示中文状态文本，放在卡片右上角 -->
            <span class="status-badge" :class="project.status">
              {{ getStatusText(project.status) }}
            </span>
            <!-- 项目描述：使用逻辑或操作符提供默认值 -->
            <p class="project-description">{{ project.description || '暂无描述' }}</p>
            <!-- 项目卡片底部：创建时间和操作按钮 -->
            <div class="project-footer">
              <!-- 格式化显示创建时间 -->
              <span class="project-date">创建时间: {{ formatDate(project.createdAt) }}</span>
              <!-- 进入工作台按钮：使用stop修饰符阻止事件冒泡，避免触发卡片点击事件 -->
              <button class="enter-btn" @click.stop="enterWorkbench(project)">
                进入工作台
              </button>
            </div>
          </div>
        </div>
        
        <!-- 空状态显示：当项目列表为空时显示 -->
        <div v-if="projectStore.projects.length === 0" class="empty-state">
          <div class="empty-icon">📁</div>
          <h3>暂无项目</h3>
          <p>点击"创建新项目"开始您的第一个项目</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
// Vue 3 Composition API 相关导入
import { ref, computed, onMounted } from 'vue'
// Vue Router 路由导航
import { useRouter } from 'vue-router'
// 项目状态管理
import { useProjectStore } from '@/stores/project'
// 用户认证状态管理
import { useAuthStore } from '@/stores/auth'

/**
 * 项目管理页面组件
 * 功能：显示项目列表、创建新项目、选择项目、跳转到工作台
 * 路由：/projects
 */
export default {
  name: 'ProjectView',
  setup() {
    // 路由实例：用于页面跳转
    const router = useRouter()
    // 项目状态管理实例：管理项目相关数据和操作
    const projectStore = useProjectStore()
    // 认证状态管理实例：管理用户登录状态
    const authStore = useAuthStore()
    
    // ==================== 响应式数据定义 ====================
    // 控制创建项目表单的显示/隐藏
    const showCreateForm = ref(false)
    
    // ==================== 计算属性 ====================
    // 计算活跃项目数量（状态为'active'的项目）
    const activeProjectsCount = computed(() => {
      return projectStore.projects.filter(p => p.status === 'active').length
    })
    
    // 计算属性：生成财务报表年份选项（当前年份往前推10年）
    const reportYears = computed(() => {
      const currentYear = new Date().getFullYear()
      const years = []
      for (let i = 0; i < 10; i++) {
        years.push(currentYear - i)
      }
      return years
    })
    
    // 计算属性：判断企业是否上市（用于条件显示上市地点选择）
    const isListed = computed(() => {
      const status = projectStore.enterpriseAttributes.listingStatus
      return status === '境内上市' || status === '境外上市'
    })
    
    // ==================== 业务方法定义 ====================
    /**
     * 加载项目列表
     * 调用store中的fetchProjects方法获取项目数据
     */
    const loadProjects = async () => {
      await projectStore.fetchProjects()
    }
    
    /**
     * 开始创建项目流程
     * 重置创建状态并显示创建表单
     */
    const startCreateProject = () => {
      projectStore.resetCreateState()
      showCreateForm.value = true
    }
    
    /**
     * 进入下一步
     * 验证当前步骤的表单数据，通过后进入下一步
     */
    const nextStep = async () => {
      try {
        let stepName = ''
        if (projectStore.createStep === 1) {
          stepName = 'basic'
        } else if (projectStore.createStep === 2) {
          stepName = 'attributes'
        } else if (projectStore.createStep === 3) {
          stepName = 'standards'
        }
        
        // 验证当前步骤的表单数据
        const isValid = projectStore.validateForm(stepName)
        if (!isValid) {
          return // 验证失败，停留在当前步骤
        }
        
        // 保存当前创建状态到localStorage
        projectStore.saveCreateState()
        
        // 如果是第2步，需要获取审计依据推荐
        if (projectStore.createStep === 2) {
          await projectStore.fetchAuditStandards()
        }
        
        // 进入下一步
        projectStore.setCreateStep(projectStore.createStep + 1)
      } catch (error) {
        console.error('进入下一步失败:', error)
        alert('操作失败，请重试')
      }
    }
    
    /**
     * 返回上一步
     * 回到上一个创建步骤
     */
    const prevStep = () => {
      if (projectStore.createStep > 1) {
        projectStore.setCreateStep(projectStore.createStep - 1)
      }
    }
    
    /**
     * 添加企业简称
     * 在企业简称列表中添加新的空白简称输入框
     */
    const addShortName = () => {
      projectStore.addShortName()
    }
    
    /**
     * 删除企业简称
     * 从企业简称列表中删除指定索引的简称
     * @param {number} index - 要删除的简称索引
     */
    const removeShortName = (index) => {
      projectStore.removeShortName(index)
    }
    
    /**
     * 清除验证错误
     * 清除指定字段的验证错误信息
     * @param {string} field - 字段名
     */
    const clearError = (field) => {
      projectStore.clearValidationError(field)
    }
    
    /**
     * 实时验证企业名称
     * 当用户输入企业名称时，实时清除错误并进行基础验证
     */
    const validateNameInput = () => {
      clearError('name')
      // 可以在这里添加实时验证逻辑
      if (projectStore.enterpriseInfo.name && projectStore.enterpriseInfo.name.trim()) {
        // 基础长度验证
        if (projectStore.enterpriseInfo.name.trim().length >= 2 && 
            projectStore.enterpriseInfo.name.trim().length <= 100) {
          // 字符格式验证
          if (!/^[\u4e00-\u9fa5a-zA-Z0-9\s\(\)（）\-_]+$/.test(projectStore.enterpriseInfo.name.trim())) {
            projectStore.validationErrors.name = '企业名称只能包含中文、英文、数字、空格、括号和连字符'
          }
        }
      }
    }
    
    /**
     * 实时验证企业简称
     * 当用户输入企业简称时，实时清除错误
     */
    const validateShortNameInput = () => {
      clearError('shortNames')
    }
    
    /**
     * 实时验证企业属性字段
     * @param {string} field - 字段名
     */
    const validateAttributeInput = (field) => {
      clearError(field)
      
      // 特殊处理上市情况变化
      if (field === 'listingStatus') {
        // 如果改为未上市，清空上市地点
        if (projectStore.enterpriseAttributes.listingStatus === '未上市') {
          projectStore.enterpriseAttributes.listingLocation = ''
          clearError('listingLocation')
        }
      }
    }
    
    /**
     * 创建项目
     * 完成所有步骤后创建项目，包含完整的错误处理和成功提示
     */
    const createProject = async () => {
      try {
        // 验证是否选择了审计依据方案
        if (!projectStore.selectedStandards) {
          alert('请选择审计依据方案')
          return
        }
        
        // 设置加载状态
        projectStore.loading = true
        
        // 构建项目数据
        const projectData = {
          // 使用企业名称作为项目名称
          name: projectStore.enterpriseInfo.name,
          // 企业基本信息
          enterpriseInfo: { ...projectStore.enterpriseInfo },
          // 企业属性信息
          enterpriseAttributes: { ...projectStore.enterpriseAttributes },
          // 选择的审计依据方案
          auditStandards: projectStore.selectedStandards,
          // 创建时间
          createdAt: new Date().toISOString(),
          // 项目状态
          status: 'active'
        }
        
        // 调用store方法创建项目
        const newProject = await projectStore.createProject(projectData)
        
        // 项目创建成功提示
        alert(`项目"${newProject.name}"创建成功！\n\n项目ID: ${newProject.id}\n创建时间: ${formatDate(newProject.createdAt)}\n\n即将进入项目工作区...`)
        
        // 关闭创建表单
        cancelCreate()
        
        // 刷新项目列表
        await loadProjects()
        
        // TODO: 跳转到项目工作区
        // 这里应该实现项目工作区的路由跳转
        // router.push(`/project/${newProject.id}/workspace`)
        console.log('项目创建成功，准备进入工作区:', newProject)
        
        // 模拟跳转延迟
        setTimeout(() => {
          console.log(`进入项目"${newProject.name}"的工作区，项目数据已完全隔离`)
        }, 1000)
        
      } catch (error) {
        console.error('创建项目失败:', error)
        
        // 显示详细的错误信息
        let errorMessage = '创建项目失败'
        
        if (error.message.includes('网络连接异常')) {
          errorMessage = '网络连接异常，请检查网络连接后重试'
        } else if (error.message.includes('服务器异常')) {
          errorMessage = '服务器异常，请稍后重试或联系管理员'
        } else if (error.message.includes('验证失败')) {
          errorMessage = '项目信息验证失败，请检查所有必填项'
        } else if (error.message.includes('当前企业类型暂不支持')) {
          errorMessage = '当前企业类型暂不支持，请联系管理员'
        } else {
          errorMessage = error.message || '创建项目失败，请稍后重试'
        }
        
        alert(`创建项目失败\n\n错误信息: ${errorMessage}\n\n请检查输入信息或稍后重试`)
        
        // 如果是网络错误，可以提供重试选项
        if (error.message.includes('网络') || error.message.includes('服务器')) {
          const retry = confirm('是否要重试创建项目？')
          if (retry) {
            // 延迟重试
            setTimeout(() => {
              createProject()
            }, 2000)
          }
        }
      } finally {
        // 确保加载状态被清除
        projectStore.loading = false
      }
    }
    
    /**
     * 取消创建项目
     * 重置创建状态并关闭创建表单
     */
    const cancelCreate = () => {
      // 重置创建状态
      projectStore.resetCreateState()
      // 隐藏创建表单
      showCreateForm.value = false
    }
    
    /**
     * 选择已有项目
     * 进入项目工作区，确保数据隔离
     * @param {Object} project - 项目对象
     */
    const selectProject = async (project) => {
      try {
        // 显示加载状态
        projectStore.loading = true
        
        // 确认进入项目
        const confirmed = confirm(`确定要进入项目"${project.name}"吗？\n\n项目ID: ${project.id}\n创建时间: ${formatDate(project.createdAt)}\n\n进入后将加载该项目的独立工作环境。`)
        
        if (!confirmed) {
          return
        }
        
        // 选择项目并进入工作区
        const selectedProject = await projectStore.selectProject(project.id)
        
        // 成功提示
        alert(`已成功进入项目"${selectedProject.name}"的工作区！\n\n项目数据已完全隔离，您现在可以安全地进行项目相关操作。\n\n工作区路径: ${selectedProject.workspacePath}`)
        
        // TODO: 跳转到项目工作区页面
        // 这里应该实现路由跳转到项目工作区
        // router.push(`/project/${selectedProject.id}/workspace`)
        console.log('已进入项目工作区:', selectedProject)
        
        // 模拟工作区加载
        setTimeout(() => {
          console.log(`项目"${selectedProject.name}"工作区加载完成，数据隔离已生效`)
        }, 1000)
        
      } catch (error) {
        console.error('选择项目失败:', error)
        
        // 显示详细的错误信息
        let errorMessage = '进入项目失败'
        
        if (error.message.includes('网络连接异常')) {
          errorMessage = '网络连接异常，请检查网络连接后重试'
        } else if (error.message.includes('无权访问')) {
          errorMessage = '无权访问该项目，请联系项目管理员'
        } else if (error.message.includes('项目不存在')) {
          errorMessage = '项目不存在或已被删除'
        } else if (error.message.includes('项目状态异常')) {
          errorMessage = '项目状态异常，无法进入工作区'
        } else {
          errorMessage = error.message || '进入项目失败，请稍后重试'
        }
        
        alert(`进入项目失败\n\n错误信息: ${errorMessage}\n\n请检查项目状态或稍后重试`)
        
        // 如果是网络错误，提供重试选项
        if (error.message.includes('网络') || error.message.includes('连接')) {
          const retry = confirm('是否要重试进入项目？')
          if (retry) {
            setTimeout(() => {
              selectProject(project)
            }, 2000)
          }
        }
      } finally {
        // 确保加载状态被清除
        projectStore.loading = false
      }
    }
    
    /**
     * 进入工作台
     * 路由跳转逻辑：设置当前项目并跳转到工作台页面
     * @param {Object} project - 要进入的项目对象
     */
    const enterWorkbench = async (project) => {
      try {
        // 1. 选择项目并初始化工作区（替代已删除的setCurrentProject方法）
        await projectStore.selectProject(project.id)
        
        // 2. 路由跳转到工作台页面
        // 路径：/workbench，对应 WorkbenchView.vue 组件
        await router.push('/workbench')
      } catch (error) {
        console.error('进入工作台失败:', error)
        // 显示用户友好的错误提示
        ElMessage.error('进入工作台失败，请重试')
      }
    }
    
    /**
     * 获取状态文本
     * 将英文状态码转换为中文显示文本
     * @param {string} status - 项目状态码
     * @returns {string} 中文状态文本
     */
    const getStatusText = (status) => {
      const statusMap = {
        'active': '进行中',     // 项目正在进行
        'completed': '已完成',  // 项目已完成
        'paused': '已暂停',    // 项目已暂停
        'archived': '已归档'   // 项目已归档
      }
      return statusMap[status] || '未知'  // 未知状态的默认显示
    }
    
    /**
     * 格式化日期
     * 将ISO日期字符串转换为本地化日期显示
     * @param {string} dateString - ISO格式的日期字符串
     * @returns {string} 格式化后的日期字符串
     */
    const formatDate = (dateString) => {
      if (!dateString) return '未知'
      const date = new Date(dateString)
      return date.toLocaleDateString('zh-CN')  // 转换为中文日期格式
    }
    
    // ==================== 生命周期钩子 ====================
    /**
     * 组件挂载时的初始化逻辑
     * 1. 检查用户登录状态
     * 2. 未登录则跳转到登录页
     * 3. 已登录则加载项目列表
     * 4. 恢复未完成的创建流程
     */
    onMounted(async () => {
      // 路由守卫：检查用户是否已登录
      if (!authStore.isAuthenticated) {
        // 未登录则跳转到登录页面
        router.push('/login')
        return
      }
      
      // 已登录用户：加载项目列表数据
      await loadProjects()
      
      // 如果有未完成的创建流程，恢复状态
      const savedState = localStorage.getItem('project_create_state')
      if (savedState) {
        try {
          const state = JSON.parse(savedState)
          // 询问用户是否继续之前的创建流程
          if (confirm('检测到未完成的项目创建流程，是否继续？')) {
            Object.assign(projectStore.enterpriseInfo, state.enterpriseInfo || {})
            Object.assign(projectStore.enterpriseAttributes, state.enterpriseAttributes || {})
            projectStore.setCreateStep(state.createStep || 1)
            showCreateForm.value = true
          } else {
            // 用户选择不继续，清除保存的状态
            localStorage.removeItem('project_create_state')
          }
        } catch (error) {
          console.error('恢复创建状态失败:', error)
          localStorage.removeItem('project_create_state')
        }
      }
    })
    
    // ==================== 返回模板可用的数据和方法 ====================
    return {
      // Store实例
      projectStore,        // 项目状态管理
      authStore,          // 认证状态管理
      
      // 响应式数据
      showCreateForm,     // 创建表单显示状态
      
      // 计算属性
      activeProjectsCount, // 活跃项目数量
      reportYears,        // 财务报表年份选项
      isListed,           // 是否上市判断
      
      // 业务方法
      loadProjects,       // 加载项目列表
      startCreateProject, // 开始创建项目流程
      nextStep,           // 下一步
      prevStep,           // 上一步
      addShortName,       // 添加企业简称
      removeShortName,    // 删除企业简称
      clearError,         // 清除验证错误
      createProject,      // 创建项目
      cancelCreate,       // 取消创建
      selectProject,      // 选择项目
      enterWorkbench,     // 进入工作台（路由跳转）
      
      // 工具方法
      getStatusText,      // 状态文本转换
      formatDate,         // 日期格式化
      
      // 实时验证方法
      validateNameInput,      // 实时验证企业名称
      validateShortNameInput, // 实时验证企业简称
      validateAttributeInput  // 实时验证企业属性
    }
  }
}
</script>

<style scoped>
/* ==================== 页面布局样式 ==================== */
.project-view {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
  background-color: #f8f9fa;
  min-height: 100vh;
}

/* 页面头部样式 */
.project-header {
  text-align: center;
  margin-bottom: 30px;
  padding: 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px;
  color: white;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
}

.project-header h1 {
  margin: 0 0 10px 0;
  font-size: 2.5rem;
  font-weight: 600;
}

.welcome-text {
  margin: 0;
  font-size: 1.1rem;
  opacity: 0.9;
}

/* ==================== 操作按钮区域样式 ==================== */
.project-actions {
  display: flex;
  gap: 15px;
  margin-bottom: 30px;
  justify-content: center;
}

.create-btn, .refresh-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 24px;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.create-btn {
  background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
  color: white;
}

.create-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(76, 175, 80, 0.3);
}

.refresh-btn {
  background: linear-gradient(135deg, #2196F3 0%, #1976D2 100%);
  color: white;
}

.refresh-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(33, 150, 243, 0.3);
}

.icon {
  font-size: 1.2rem;
  font-weight: bold;
}

/* ==================== 创建表单模态框样式 ==================== */
.create-form-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.6);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  backdrop-filter: blur(5px);
}

.create-form {
  background: white;
  border-radius: 16px;
  padding: 30px;
  width: 90%;
  max-width: 600px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  animation: modalSlideIn 0.3s ease-out;
}

@keyframes modalSlideIn {
  from {
    opacity: 0;
    transform: translateY(-50px) scale(0.9);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

/* ==================== 步骤指示器样式 ==================== */
.step-indicator {
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 30px;
  padding: 20px 0;
}

.step {
  display: flex;
  flex-direction: column;
  align-items: center;
  position: relative;
}

.step-number {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background-color: #e9ecef;
  color: #6c757d;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 1.1rem;
  transition: all 0.3s ease;
  margin-bottom: 8px;
}

.step-label {
  font-size: 0.9rem;
  color: #6c757d;
  font-weight: 500;
  transition: all 0.3s ease;
}

.step.active .step-number {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
}

.step.active .step-label {
  color: #667eea;
  font-weight: 600;
}

.step.completed .step-number {
  background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
  color: white;
}

.step.completed .step-label {
  color: #4CAF50;
}

.step-line {
  width: 80px;
  height: 2px;
  background-color: #e9ecef;
  margin: 0 20px;
  transition: all 0.3s ease;
}

.step-line.completed {
  background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
}

/* ==================== 步骤内容样式 ==================== */
.step-content {
  animation: stepSlideIn 0.3s ease-out;
}

@keyframes stepSlideIn {
  from {
    opacity: 0;
    transform: translateX(20px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

.step-content h3 {
  margin: 0 0 25px 0;
  font-size: 1.5rem;
  font-weight: 600;
  color: #333;
  text-align: center;
  padding-bottom: 15px;
  border-bottom: 2px solid #f0f0f0;
}

/* ==================== 表单样式 ==================== */
.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: #333;
  font-size: 0.95rem;
}

.required {
  color: #dc3545;
  font-weight: 600;
}

.form-group input,
.form-group select,
.form-group textarea {
  width: 100%;
  padding: 12px 16px;
  border: 2px solid #e9ecef;
  border-radius: 8px;
  font-size: 1rem;
  transition: all 0.3s ease;
  box-sizing: border-box;
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.form-group input.error,
.form-group select.error {
  border-color: #dc3545;
  box-shadow: 0 0 0 3px rgba(220, 53, 69, 0.1);
}

.error-message {
  color: #dc3545;
  font-size: 0.85rem;
  margin-top: 5px;
  display: block;
}

/* 企业简称输入样式 */
.short-name-item {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
}

.short-name-item input {
  flex: 1;
}

.remove-btn {
  width: 32px;
  height: 32px;
  border: none;
  background-color: #dc3545;
  color: white;
  border-radius: 50%;
  cursor: pointer;
  font-size: 1.2rem;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
}

.remove-btn:hover {
  background-color: #c82333;
  transform: scale(1.1);
}

.add-btn {
  background-color: #28a745;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: all 0.3s ease;
  margin-top: 5px;
}

.add-btn:hover {
  background-color: #218838;
}

/* 复选框样式 */
.checkbox-group {
  margin: 15px 0;
}

.checkbox-label {
  display: flex;
  align-items: center;
  cursor: pointer;
  font-weight: 500;
  color: #333;
}

.checkbox-label input[type="checkbox"] {
  width: auto;
  margin-right: 10px;
  transform: scale(1.2);
}

/* ==================== 审计依据方案样式 ==================== */
.loading-standards {
  text-align: center;
  padding: 40px 20px;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 20px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.standards-intro {
  font-size: 1rem;
  color: #666;
  margin-bottom: 20px;
  text-align: center;
}

.standard-option {
  margin-bottom: 15px;
  border: 2px solid #e9ecef;
  border-radius: 12px;
  overflow: hidden;
  transition: all 0.3s ease;
}

.standard-option:hover {
  border-color: #667eea;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.1);
}

.standard-label {
  display: block;
  cursor: pointer;
  padding: 20px;
  margin: 0;
}

.standard-label input[type="radio"] {
  margin-right: 15px;
  transform: scale(1.2);
}

.standard-content h4 {
  margin: 0 0 15px 0;
  color: #333;
  font-size: 1.2rem;
  font-weight: 600;
}

.standard-details {
  margin-left: 25px;
}

.standard-item {
  margin-bottom: 8px;
  font-size: 0.95rem;
  line-height: 1.4;
}

.standard-item strong {
  color: #333;
  font-weight: 600;
}

.no-standards {
  text-align: center;
  padding: 40px 20px;
  color: #666;
}

.no-standards-icon {
  font-size: 3rem;
  margin-bottom: 15px;
}

.no-standards h4 {
  color: #333;
  margin: 0 0 15px 0;
  font-size: 1.3rem;
}

.no-standards p {
  margin: 0 0 10px 0;
  line-height: 1.5;
}

/* ==================== 表单操作按钮样式 ==================== */
.form-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px solid #f0f0f0;
}

.prev-btn, .next-btn, .create-btn, .cancel-btn {
  padding: 12px 24px;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  min-width: 100px;
}

.next-btn, .create-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.next-btn:hover, .create-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
}

.create-btn:disabled {
  background: #6c757d;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.prev-btn {
  background: #f8f9fa;
  color: #6c757d;
  border: 2px solid #e9ecef;
}

.prev-btn:hover {
  background: #e9ecef;
  color: #495057;
}

.cancel-btn {
  background: #f8f9fa;
  color: #dc3545;
  border: 2px solid #dc3545;
}

.cancel-btn:hover {
  background: #dc3545;
  color: white;
}

/* ==================== 项目内容区域样式 ==================== */
.project-content {
  background: white;
  border-radius: 12px;
  padding: 30px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.loading {
  text-align: center;
  padding: 40px;
}

.error {
  text-align: center;
  padding: 40px;
  color: #e74c3c;
}

.retry-btn {
  background: #e74c3c;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 6px;
  cursor: pointer;
  margin-top: 15px;
}

.retry-btn:hover {
  background: #c0392b;
}

/* 项目统计卡片 */
.project-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.stat-card {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 25px;
  border-radius: 12px;
  text-align: center;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
}

.stat-card h3 {
  font-size: 36px;
  margin: 0 0 10px 0;
  font-weight: bold;
}

.stat-card p {
  margin: 0;
  font-size: 14px;
  opacity: 0.9;
}

/* 项目网格 */
.project-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.project-card {
  position: relative;
  background: white;
  border: 1px solid #e1e8ed;
  border-radius: 12px;
  padding: 20px;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.project-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
  border-color: #667eea;
}

.project-title {
  margin: 0 0 10px 0;
  color: #2c3e50;
  font-size: 18px;
  font-weight: 600;
}

.status-badge {
  position: absolute;
  top: 15px;
  right: 15px;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
}

.status-badge.active {
  background: #d4edda;
  color: #155724;
}

.status-badge.completed {
  background: #cce5ff;
  color: #004085;
}

.status-badge.paused {
  background: #fff3cd;
  color: #856404;
}

.status-badge.archived {
  background: #f8d7da;
  color: #721c24;
}

.project-description {
  color: #7f8c8d;
  font-size: 14px;
  line-height: 1.5;
  margin-bottom: 15px;
  min-height: 40px;
}

.project-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.project-date {
  font-size: 12px;
  color: #95a5a6;
}

.enter-btn {
  background: #27ae60;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 12px;
  transition: all 0.3s ease;
}

.enter-btn:hover {
  background: #229954;
  transform: scale(1.05);
}

/* 空状态 */
.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: #7f8c8d;
}

.empty-icon {
  font-size: 64px;
  margin-bottom: 20px;
}

.empty-state h3 {
  margin: 0 0 10px 0;
  color: #2c3e50;
}

.empty-state p {
  margin: 0;
  font-size: 14px;
}

/* ==================== 响应式设计 ==================== */
@media (max-width: 768px) {
  .project-view {
    padding: 15px;
  }
  
  .project-header h1 {
    font-size: 2rem;
  }
  
  .project-actions {
    flex-direction: column;
    align-items: center;
  }
  
  .project-grid {
    grid-template-columns: 1fr;
  }
  
  .create-form {
    width: 95%;
    padding: 20px;
    margin: 10px;
  }
  
  .step-indicator {
    flex-direction: column;
    gap: 15px;
  }
  
  .step-line {
    width: 2px;
    height: 30px;
    margin: 10px 0;
  }
  
  .form-actions {
    flex-direction: column;
  }
  
  .prev-btn, .next-btn, .create-btn, .cancel-btn {
    width: 100%;
  }
}

@media (max-width: 480px) {
  .project-header {
    padding: 15px;
  }
  
  .project-header h1 {
    font-size: 1.8rem;
  }
  
  .welcome-text {
    font-size: 1rem;
  }
  
  .create-btn, .refresh-btn {
    padding: 10px 20px;
    font-size: 0.9rem;
  }
  
  .step-number {
    width: 35px;
    height: 35px;
    font-size: 1rem;
  }
  
  .step-label {
    font-size: 0.8rem;
  }
}
</style>
