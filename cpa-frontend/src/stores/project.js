import { defineStore } from "pinia";

/* 项目管理 Store - 企业审计项目的核心状态管理
 * 
 * API 接口设计：
 * ├── GET  /api/projects          - 获取项目列表
 * ├── POST /api/projects          - 创建新项目
 * ├── GET  /api/projects/:id      - 获取项目详情
 * ├── POST /api/audit-standards   - 获取审计依据推荐
 * └── 所有 TODO 标记位置为 API 接口预留位置
 * 
 * 提醒：
 * - 当前使用 localStorage 模拟数据库，生产环境应该替换为真实 API
 * - 项目数据隔离是安全要求，切勿在实现中破坏隔离机制
 * - 表单验证规则需要与后端保持一致
 * - 错误处理需要覆盖网络异常、权限验证、业务逻辑等各种场景
 */
export const useProjectStore = defineStore("project", {
  // 状态定义：存储项目相关的所有状态数据
  state: () => ({
    projects: [],              // 项目列表数组，存储所有项目数据
    currentProject: null,      // 当前选中的项目对象，用于跨页面共享当前项目信息
    loading: false,           // 加载状态标识，用于显示加载动画
    error: null,              // 错误信息，存储操作失败时的错误消息
    
    // 项目创建流程相关状态
    createStep: 1,            // 创建步骤：1-基本信息，2-企业属性，3-审计依据
    enterpriseInfo: {         // 企业基本信息
      name: '',               // 企业名称
      shortNames: [''],       // 企业简称数组，支持多个简称
    },
    enterpriseAttributes: {   // 企业属性信息
      reportYear: '',         // 财务报表年份
      isDomestic: true,       // 是否为境内企业
      scale: '',              // 企业规模
      industry: '',           // 所属行业
      listingStatus: '',      // 上市情况
      listingLocation: '',    // 上市地点（如果上市）
      isStateOwned: false,    // 是否为国有企业
    },
    auditStandards: [],       // 推荐的审计依据方案
    selectedStandards: null,  // 用户选择的审计依据方案
    validationErrors: {},     // 表单验证错误信息
  }),

  // 计算属性：基于状态数据计算派生值，具有缓存特性
  getters: {
    // 获取项目总数
    projectCount: (state) => state.projects.length,
    // 获取当前选中的项目
    getCurrentProject: (state) => state.currentProject,
    // 获取所有项目列表
    getProjects: (state) => state.projects,
    // 获取加载状态
    isLoading: (state) => state.loading,
    // 获取错误信息
    getError: (state) => state.error,
    
    // 项目创建流程相关计算属性
    getCurrentStep: (state) => state.createStep,
    getEnterpriseInfo: (state) => state.enterpriseInfo,
    getEnterpriseAttributes: (state) => state.enterpriseAttributes,
    getAuditStandards: (state) => state.auditStandards,
    getValidationErrors: (state) => state.validationErrors,
    
    // 检查基本信息是否完整
    isBasicInfoValid: (state) => {
      return state.enterpriseInfo.name.trim() !== '' && 
             state.enterpriseInfo.shortNames.some(name => name.trim() !== '');
    },
    
    // 检查企业属性是否完整
    isAttributesValid: (state) => {
      const attrs = state.enterpriseAttributes;
      return attrs.reportYear !== '' && attrs.scale !== '' && 
             attrs.industry !== '' && attrs.listingStatus !== '';
    },
  },

  // 动作方法：定义修改状态的方法，支持异步操作
  actions: {
    /**
     * 获取项目列表
     * 数据来源：localStorage模拟数据库，预留后端API调用位置
     * 接口说明：应对应后端的 GET /api/projects 接口
     */
    async fetchProjects() {
      this.loading = true;
      this.error = null;
      try {
        // TODO: 实际项目中应调用真实API接口
        // const response = await api.getProjects()
        // this.projects = response.data

        // 使用localStorage模拟数据库操作
        const savedProjects = localStorage.getItem('projects');
        if (savedProjects) {
          this.projects = JSON.parse(savedProjects);
        } else {
          // 初始化默认项目数据
          this.projects = [];
          this._saveProjectsToStorage();
        }
      } catch (error) {
        this.error = error.message;
        console.error("获取项目失败:", error);
      } finally {
        this.loading = false;
      }
    },

    /**
     * 初始化项目状态
     * 从localStorage恢复之前选中的项目和创建流程状态
     * 实现页面刷新后状态持久化
     */
    initializeProject() {
      // 恢复当前项目
      const savedProject = localStorage.getItem("currentProject");
      if (savedProject) {
        try {
          this.currentProject = JSON.parse(savedProject);
        } catch (error) {
          console.error("恢复项目状态失败:", error);
          localStorage.removeItem("currentProject");
        }
      }
      
      // 恢复创建流程状态
      const savedCreateState = localStorage.getItem("projectCreateState");
      if (savedCreateState) {
        try {
          const createState = JSON.parse(savedCreateState);
          this.createStep = createState.createStep || 1;
          this.enterpriseInfo = { ...this.enterpriseInfo, ...createState.enterpriseInfo };
          this.enterpriseAttributes = { ...this.enterpriseAttributes, ...createState.enterpriseAttributes };
        } catch (error) {
          console.error("恢复创建状态失败:", error);
          localStorage.removeItem("projectCreateState");
        }
      }
    },

    // 注意：setCurrentProject 方法已被 selectProject 方法替代
    // selectProject 方法提供了更完善的项目选择、权限验证和数据隔离功能

    /**
     * 创建新项目
     * 将企业信息和审计依据保存为新项目，确保项目数据隔离
     * 接口说明：应对应后端的 POST /api/projects 接口
     * @returns {Object} 创建的项目对象
     */
    async createProject() {
      this.loading = true;
      this.error = null;
      try {
        // 最终验证所有步骤的数据
        const basicValid = this.validateForm('basic');
        const attributesValid = this.validateForm('attributes');
        const standardsValid = this.validateForm('standards');
        
        if (!basicValid || !attributesValid || !standardsValid) {
          throw new Error('项目信息验证失败，请检查所有必填项');
        }
        
        // 生成唯一的项目ID，确保项目隔离
        const projectId = this._generateUniqueProjectId();
        
        // TODO: 实际项目中应调用真实API接口
        // const response = await api.createProject({
        //   id: projectId,
        //   enterpriseInfo: this.enterpriseInfo,
        //   enterpriseAttributes: this.enterpriseAttributes,
        //   selectedStandards: this.selectedStandards
        // })
        // 
        // if (!response.success) {
        //   throw new Error(response.message || '服务器创建项目失败')
        // }
        
        // 模拟网络延迟
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        // 创建项目对象，深拷贝确保数据隔离
        const newProject = {
          id: projectId,
          name: this.enterpriseInfo.name.trim(),
          shortNames: this.enterpriseInfo.shortNames
            .filter(name => name && name.trim())
            .map(name => name.trim()),
          enterpriseInfo: JSON.parse(JSON.stringify(this.enterpriseInfo)),
          enterpriseAttributes: JSON.parse(JSON.stringify(this.enterpriseAttributes)),
          auditStandards: JSON.parse(JSON.stringify(this.selectedStandards)),
          status: 'active',
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString(),
          // 项目隔离标识
          isolated: true,
          // 项目工作区路径（用于数据隔离）
          workspacePath: `/projects/${projectId}`,
          // 项目访问权限
          accessLevel: 'private'
        };
        
        // 验证项目ID唯一性
        if (this.projects.some(p => p.id === projectId)) {
          throw new Error('项目ID冲突，请重试');
        }
        
        // 添加到项目列表
        this.projects.push(newProject);
        
        // 保存到localStorage
        this._saveProjectsToStorage();
        
        // 清除创建状态的localStorage缓存（统一键名）
        localStorage.removeItem('projectCreateState');
        
        // 重置创建流程状态
        this.resetCreateState();
        
        // 设置当前项目（实现项目隔离）
        this.currentProject = newProject;
        // 持久化当前项目对象，支持刷新恢复
        try {
          localStorage.setItem('currentProject', JSON.stringify(this.currentProject));
        } catch (e) {
          console.error('保存当前项目到本地存储失败:', e);
        }
        
        return newProject;
      } catch (error) {
        this.error = error.message;
        console.error("创建项目失败:", error);
        
        // 根据错误类型提供不同的错误信息
        if (error.message.includes('网络') || error.message.includes('连接')) {
          throw new Error('网络连接异常，请检查网络连接后重试');
        } else if (error.message.includes('服务器')) {
          throw new Error('服务器异常，请稍后重试或联系管理员');
        } else if (error.message.includes('验证失败')) {
          throw error; // 保持原始验证错误信息
        } else {
          throw new Error('创建项目失败，请稍后重试');
        }
      } finally {
        this.loading = false;
      }
    },

    /**
     * 生成唯一的项目ID
     * 确保项目间的数据隔离
     * @private
     */
    _generateUniqueProjectId() {
      const timestamp = Date.now();
      const random = Math.random().toString(36).substr(2, 9);
      return `project_${timestamp}_${random}`;
    },

    /**
     * 选择项目
     * 加载指定项目的环境和数据，确保项目间数据隔离
     * @param {string} projectId - 项目ID
     */
    async selectProject(projectId) {
      this.loading = true
      this.error = null
      
      try {
        // 验证项目ID
        if (!projectId) {
          throw new Error('项目ID不能为空')
        }
        
        // TODO: 这里应该调用后端API加载项目详情和权限验证
        // const response = await api.get(`/projects/${projectId}`, {
        //   headers: {
        //     'Authorization': `Bearer ${userToken}`,
        //     'X-Project-Access': 'read'
        //   }
        // })
        // 
        // if (!response.success) {
        //   throw new Error(response.message || '无权访问该项目')
        // }
        // 
        // const project = response.data
        
        // 从本地项目列表中查找项目
        const project = this.projects.find(p => p.id === projectId)
        
        if (!project) {
          throw new Error('项目不存在或已被删除')
        }
        
        // 验证项目访问权限
        if (project.accessLevel === 'private' && !project.isolated) {
          throw new Error('无权访问该项目')
        }
        
        // 验证项目状态
        if (project.status !== 'active') {
          throw new Error(`项目状态异常: ${project.status}`)
        }
        
        // 清除当前项目的工作区数据（确保隔离）
        this._clearCurrentWorkspace()
        
        // 设置当前项目
        this.currentProject = JSON.parse(JSON.stringify(project)) // 深拷贝确保数据隔离
        // 持久化当前项目对象，支持刷新恢复
        try {
          localStorage.setItem('currentProject', JSON.stringify(this.currentProject))
        } catch (e) {
          console.error('保存当前项目到本地存储失败:', e)
        }
        
        // 初始化项目工作区
        await this._initializeProjectWorkspace(project)
        
        // 保存当前项目ID到localStorage（用于页面刷新恢复）
        localStorage.setItem('current_project_id', projectId)
        
        console.log(`已进入项目"${project.name}"的工作区，数据已完全隔离`)
        
        return this.currentProject
        
      } catch (error) {
        this.error = error.message
        console.error('选择项目失败:', error)
        
        // 根据错误类型提供不同的错误信息
        if (error.message.includes('网络') || error.message.includes('连接')) {
          throw new Error('网络连接异常，请检查网络连接后重试')
        } else if (error.message.includes('权限') || error.message.includes('无权访问')) {
          throw new Error('无权访问该项目，请联系项目管理员')
        } else if (error.message.includes('不存在')) {
          throw new Error('项目不存在或已被删除')
        } else {
          throw new Error('加载项目失败，请稍后重试')
        }
      } finally {
        this.loading = false
      }
    },

    /**
     * 清除当前工作区数据
     * 确保项目间数据隔离
     * @private
     */
    _clearCurrentWorkspace() {
      // 清除当前项目相关的localStorage数据（保护关键键不被误删）
      const protectedKeys = new Set([
        'projects',
        'currentProject',
        'projectCreateState',
        'authToken',
        'userInfo',
        'current_project_id'
      ])
      const keysToRemove = []
      for (let i = 0; i < localStorage.length; i++) {
        const key = localStorage.key(i)
        if (!key) continue
        if (protectedKeys.has(key)) continue
        if (key.startsWith('project_') || key.startsWith('workspace_')) {
          keysToRemove.push(key)
        }
      }
      
      keysToRemove.forEach(key => {
        localStorage.removeItem(key)
      })
      
      console.log('已清除当前工作区数据，确保项目隔离')
    },

    /**
     * 初始化项目工作区
     * 为项目创建独立的数据空间
     * @param {Object} project - 项目对象
     * @private
     */
    async _initializeProjectWorkspace(project) {
      try {
        // 创建项目工作区标识
        const workspaceKey = `workspace_${project.id}`
        const workspaceData = {
          projectId: project.id,
          projectName: project.name,
          workspacePath: project.workspacePath,
          createdAt: new Date().toISOString(),
          isolated: true
        }
        
        // 保存工作区数据
        localStorage.setItem(workspaceKey, JSON.stringify(workspaceData))
        
        // 初始化项目特定的数据存储空间
        const projectDataKey = `project_${project.id}_data`
        if (!localStorage.getItem(projectDataKey)) {
          const initialProjectData = {
            ...project,
            workData: {},
            settings: {},
            cache: {}
          }
          localStorage.setItem(projectDataKey, JSON.stringify(initialProjectData))
        }
        
        console.log(`项目"${project.name}"工作区初始化完成`)
        
      } catch (error) {
        console.error('初始化项目工作区失败:', error)
        throw new Error('初始化项目工作区失败')
      }
    },

    /**
     * 保存项目数据到localStorage
     * 模拟数据库存储操作
     * @private
     */
    _saveProjectsToStorage() {
      try {
        localStorage.setItem('projects', JSON.stringify(this.projects));
      } catch (error) {
        console.error('保存项目数据失败:', error);
      }
    },

    /**
     * 保存创建流程状态
     * 支持用户在创建过程中刷新页面后恢复状态
     */
    saveCreateState() {
      const createState = {
        createStep: this.createStep,
        enterpriseInfo: this.enterpriseInfo,
        enterpriseAttributes: this.enterpriseAttributes,
      };
      localStorage.setItem('projectCreateState', JSON.stringify(createState));
    },

    /**
     * 重置创建流程状态
     * 在项目创建完成或取消时调用
     */
    resetCreateState() {
      this.createStep = 1;
      this.enterpriseInfo = { name: '', shortNames: [''] };
      this.enterpriseAttributes = {
        reportYear: '',
        isDomestic: true,
        scale: '',
        industry: '',
        listingStatus: '',
        listingLocation: '',
        isStateOwned: false,
      };
      this.auditStandards = [];
      this.selectedStandards = null;
      this.validationErrors = {};
      localStorage.removeItem('projectCreateState');
    },

    /**
     * 设置创建步骤
     * @param {number} step - 步骤号（1-3）
     */
    setCreateStep(step) {
      this.createStep = step;
      this.saveCreateState();
    },

    /**
     * 更新企业基本信息
     * @param {Object} info - 企业基本信息
     */
    updateEnterpriseInfo(info) {
      this.enterpriseInfo = { ...this.enterpriseInfo, ...info };
      this.saveCreateState();
    },

    /**
     * 添加企业简称
     */
    addShortName() {
      this.enterpriseInfo.shortNames.push('');
      this.saveCreateState();
    },

    /**
     * 删除企业简称
     * @param {number} index - 要删除的简称索引
     */
    removeShortName(index) {
      if (this.enterpriseInfo.shortNames.length > 1) {
        this.enterpriseInfo.shortNames.splice(index, 1);
        this.saveCreateState();
      }
    },

    /**
     * 更新企业属性信息
     * @param {Object} attributes - 企业属性信息
     */
    updateEnterpriseAttributes(attributes) {
      this.enterpriseAttributes = { ...this.enterpriseAttributes, ...attributes };
      this.saveCreateState();
    },

    /**
     * 获取审计依据推荐方案
     * 根据企业属性信息从后端获取推荐的审计依据
     * 接口说明：应对应后端的 POST /api/audit-standards/recommend 接口
     */
    async fetchAuditStandards() {
      this.loading = true;
      this.error = null;
      try {
        // TODO: 实际项目中应调用真实API接口
        // const response = await api.getAuditStandardsRecommendation(this.enterpriseAttributes)
        // this.auditStandards = response.data

        // 模拟根据企业属性推荐审计依据
        await new Promise(resolve => setTimeout(resolve, 1000)); // 模拟网络延迟
        
        // 根据企业属性生成模拟推荐方案
        const mockStandards = this._generateMockAuditStandards();
        this.auditStandards = mockStandards;
        
        return mockStandards;
      } catch (error) {
        this.error = error.message;
        console.error("获取审计依据失败:", error);
        throw error;
      } finally {
        this.loading = false;
      }
    },

    /**
     * 生成模拟审计依据方案
     * 根据企业属性生成相应的审计依据推荐
     * @private
     */
    _generateMockAuditStandards() {
      const { scale, industry, listingStatus, isDomestic } = this.enterpriseAttributes;
      
      // 基础审计依据
      const baseStandards = {
        accountingStandards: isDomestic ? '企业会计准则' : '国际财务报告准则',
        auditingStandards: '中国注册会计师审计准则',
        basicLaws: ['公司法', '会计法', '审计法'],
        specialRegulations: [],
        basicSupervision: ['财政部监管规范'],
        specialSupervision: [],
      };
      
      // 根据上市情况添加特殊法规
      if (listingStatus === '境内上市') {
        baseStandards.specialRegulations.push('证券法', '上市公司信息披露管理办法');
        baseStandards.specialSupervision.push('证监会监管规范');
      } else if (listingStatus === '境外上市') {
        baseStandards.specialRegulations.push('境外上市相关法规');
        baseStandards.specialSupervision.push('境外监管机构规范');
      }
      
      // 根据行业添加专项法规
      if (industry === '金融业') {
        baseStandards.specialRegulations.push('银行业监督管理法', '保险法');
        baseStandards.specialSupervision.push('银保监会监管规范');
      } else if (industry === '制造业') {
        baseStandards.specialRegulations.push('环境保护法', '安全生产法');
      }
      
      return [baseStandards]; // 返回数组，支持多个方案
    },

    /**
     * 选择审计依据方案
     * @param {Object} standards - 选择的审计依据方案
     */
    selectAuditStandards(standards) {
      this.selectedStandards = standards;
      this.saveCreateState();
    },

    /**
     * 验证表单数据
     * 根据当前步骤验证相应的表单字段，提供详细的验证规则和错误提示
     * @param {string} step - 验证的步骤（'basic' | 'attributes' | 'standards'）
     * @returns {boolean} 验证是否通过
     */
    validateForm(step) {
      this.validationErrors = {}; // 清空之前的错误
      let isValid = true;
      
      if (step === 'basic') {
        // 验证企业基本信息
        
        // 企业名称验证
        if (!this.enterpriseInfo.name || !this.enterpriseInfo.name.trim()) {
          this.validationErrors.name = '企业名称不能为空';
          isValid = false;
        } else if (this.enterpriseInfo.name.trim().length < 2) {
          this.validationErrors.name = '企业名称至少需要2个字符';
          isValid = false;
        } else if (this.enterpriseInfo.name.trim().length > 100) {
          this.validationErrors.name = '企业名称不能超过100个字符';
          isValid = false;
        } else if (!/^[\u4e00-\u9fa5a-zA-Z0-9\s\(\)（）\-_]+$/.test(this.enterpriseInfo.name.trim())) {
          this.validationErrors.name = '企业名称只能包含中文、英文、数字、空格、括号和连字符';
          isValid = false;
        }
        
        // 企业简称验证
        const validShortNames = this.enterpriseInfo.shortNames.filter(name => name && name.trim());
        if (validShortNames.length === 0) {
          this.validationErrors.shortNames = '至少需要一个企业简称';
          isValid = false;
        } else {
          // 检查每个简称的有效性
          for (let i = 0; i < this.enterpriseInfo.shortNames.length; i++) {
            const shortName = this.enterpriseInfo.shortNames[i];
            if (shortName && shortName.trim()) {
              if (shortName.trim().length < 1) {
                this.validationErrors.shortNames = '企业简称不能为空';
                isValid = false;
                break;
              } else if (shortName.trim().length > 50) {
                this.validationErrors.shortNames = '企业简称不能超过50个字符';
                isValid = false;
                break;
              } else if (!/^[\u4e00-\u9fa5a-zA-Z0-9\s\(\)（）\-_]+$/.test(shortName.trim())) {
                this.validationErrors.shortNames = '企业简称只能包含中文、英文、数字、空格、括号和连字符';
                isValid = false;
                break;
              }
            }
          }
          
          // 检查简称是否重复
          const uniqueShortNames = [...new Set(validShortNames.map(name => name.trim().toLowerCase()))];
          if (uniqueShortNames.length !== validShortNames.length) {
            this.validationErrors.shortNames = '企业简称不能重复';
            isValid = false;
          }
        }
        
      } else if (step === 'attributes') {
        // 验证企业属性信息
        const attrs = this.enterpriseAttributes;
        
        // 财务报表年份验证
        if (!attrs.reportYear) {
          this.validationErrors.reportYear = '请选择财务报表年份';
          isValid = false;
        } else {
          const currentYear = new Date().getFullYear();
          const selectedYear = parseInt(attrs.reportYear);
          if (selectedYear > currentYear) {
            this.validationErrors.reportYear = '财务报表年份不能超过当前年份';
            isValid = false;
          } else if (selectedYear < currentYear - 10) {
            this.validationErrors.reportYear = '财务报表年份不能早于10年前';
            isValid = false;
          }
        }
        
        // 企业规模验证
        if (!attrs.scale) {
          this.validationErrors.scale = '请选择企业规模';
          isValid = false;
        } else {
          const validScales = ['大型', '中型', '小型', '微型'];
          if (!validScales.includes(attrs.scale)) {
            this.validationErrors.scale = '请选择有效的企业规模';
            isValid = false;
          }
        }
        
        // 所属行业验证
        if (!attrs.industry) {
          this.validationErrors.industry = '请选择所属行业';
          isValid = false;
        } else {
          const validIndustries = ['制造业', '金融业', '房地产业', '批发和零售业', '建筑业', '信息技术业', '其他'];
          if (!validIndustries.includes(attrs.industry)) {
            this.validationErrors.industry = '请选择有效的行业类型';
            isValid = false;
          }
        }
        
        // 上市情况验证
        if (!attrs.listingStatus) {
          this.validationErrors.listingStatus = '请选择上市情况';
          isValid = false;
        } else {
          const validStatuses = ['未上市', '境内上市', '境外上市'];
          if (!validStatuses.includes(attrs.listingStatus)) {
            this.validationErrors.listingStatus = '请选择有效的上市情况';
            isValid = false;
          }
          
          // 如果选择了上市，必须选择上市地点
          if ((attrs.listingStatus === '境内上市' || attrs.listingStatus === '境外上市')) {
            if (!attrs.listingLocation) {
              this.validationErrors.listingLocation = '请选择上市地点';
              isValid = false;
            } else {
              // 验证上市地点的有效性
              const domesticLocations = ['上海证券交易所', '深圳证券交易所', '北京证券交易所'];
              const overseasLocations = ['香港联交所', '纽约证券交易所', '纳斯达克', '伦敦证券交易所', '其他'];
              
              if (attrs.listingStatus === '境内上市' && !domesticLocations.includes(attrs.listingLocation)) {
                this.validationErrors.listingLocation = '请选择有效的境内上市地点';
                isValid = false;
              } else if (attrs.listingStatus === '境外上市' && !overseasLocations.includes(attrs.listingLocation)) {
                this.validationErrors.listingLocation = '请选择有效的境外上市地点';
                isValid = false;
              }
            }
          }
        }
        
      } else if (step === 'standards') {
        // 验证审计依据选择
        if (!this.selectedStandards) {
          this.validationErrors.auditStandards = '请选择审计依据方案';
          isValid = false;
        } else {
          // 验证选择的审计依据方案是否在推荐列表中
          const isValidSelection = this.auditStandards.some(standard => 
            JSON.stringify(standard) === JSON.stringify(this.selectedStandards)
          );
          if (!isValidSelection) {
            this.validationErrors.auditStandards = '请选择有效的审计依据方案';
            isValid = false;
          }
        }
      }
      
      return isValid;
    },

    /**
     * 清除验证错误
     * @param {string} field - 要清除错误的字段名
     */
    clearValidationError(field) {
      if (this.validationErrors[field]) {
        delete this.validationErrors[field];
      }
    },
  },
});
