/**
 * Workspace Store - 工作区状态管理
 * 
 * 负责管理审计复核工作区的核心状态，包括：
 * - 工作区基础信息管理
 * - 复核流程状态控制
 * - 智能体文件请求处理
 * - 智能体状态监控
 * - 默认复核设置的CRUD操作
 * 
 * 这是整个审计复核系统的核心状态管理模块
 */
import { defineStore } from 'pinia'

export const useWorkspaceStore = defineStore('workspace', {
  // 使用 pinia-plugin-persistedstate 自动持久化
  persist: {
    key: 'workspace_store',
    paths: ['chatMessages', 'reviewProcess', 'agent', 'fileRequest', 'pendingStandardMessageId', 'pendingStandardRequest', 'userContext']
  },
  // ===== 状态定义 =====
  state: () => ({
    // 工作区基础信息
    currentWorkspace: null,        // 当前活跃的工作区
    workspaces: [],               // 所有可用工作区列表
    loading: false,               // 加载状态
    error: null,                  // 错误信息
    
    // 复核流程状态管理 - 实现完整的状态机模式
    reviewProcess: {
      isActive: false,            // 复核流程是否激活
      status: 'idle',             // 流程状态：idle(初始), confirming（确认复核内容）, analyzing(分析中), paused(等待用户输入), completed(完成), error(异常)
      progress: 0,                // 进度百分比 (0-100)
      stages: [                   // 复核阶段列表
        { id: 1, name: '完整性检查', status: 'pending', progress: 0 },
        { id: 2, name: '准确性验证', status: 'pending', progress: 0 },
        { id: 3, name: '合规性审查', status: 'pending', progress: 0 },
        { id: 4, name: '风险评估', status: 'pending', progress: 0 },
        { id: 5, name: '结果生成', status: 'pending', progress: 0 }
      ],
      currentStageIndex: 0,       // 当前阶段索引
      startTime: null,            // 复核开始时间
      endTime: null,              // 复核结束时间
      errorMessage: null,         // 错误信息
      userInputRequired: false,   // 是否需要用户输入
      userInputPrompt: null,      // 用户输入提示
      timeoutCount: 0,            // 超时计数器
      maxTimeouts: 3              // 最大超时次数
    },
    
    // 当前复核事项信息
    currentReviewEvent: null,     // 当前正在复核的重大事项
    
    // 文件请求状态管理 - 智能体动态请求文件的核心逻辑
    fileRequest: {
      isRequesting: false,        // 是否正在请求文件
      requestedFiles: [],         // 智能体请求的文件列表
      waitingForUser: false,      // 是否等待用户提供文件
      waitTimeout: null,          // 等待超时定时器
      defaultWaitTime: 20000,     // 默认等待时间20秒
      warningLogs: [],            // 警告日志记录
      // 异常处理和防死循环机制
      requestCount: 0,            // 当前会话的请求次数
      maxRequestCount: 10,        // 最大请求次数限制
      lastRequestTime: null,      // 上次请求时间
      minRequestInterval: 5000,   // 最小请求间隔(毫秒)
      errorCount: 0,              // 错误计数
      maxErrorCount: 3,           // 最大错误次数
      isBlocked: false,           // 是否被阻止请求
      blockReason: null,          // 阻止原因
      sessionStartTime: null      // 会话开始时间
    },
    
    // 智能体状态监控
    agent: {
      status: 'ready',            // 智能体状态：ready(就绪), processing(处理中), waiting(等待), error(错误), blocked(被阻止)
      currentTask: null,          // 当前执行的任务描述
      lastActivity: null,         // 最后活动时间
      errorHistory: [],           // 错误历史记录
      recoveryAttempts: 0,        // 恢复尝试次数
      maxRecoveryAttempts: 3      // 最大恢复尝试次数
    },

    userContext: {
      projectId: null,
      functionalArea: null,
      latestSessionId: null
    },

    // 数据库接口预留 - 使用localStorage模拟数据库操作
    database: {
      connected: false,           // 数据库连接状态
      lastSync: null,             // 最后同步时间
      pendingOperations: [],      // 待处理的数据库操作
      errorLog: []                // 数据库操作错误日志
    },

    // 复核标准生成与恢复相关状态
    pendingStandardMessageId: null,   // 待回填的 Filecheck 消息 ID
    pendingStandardRequest: null,     // 生成标准的请求负载（用于刷新后恢复）
    // latestStandard 移除：避免冗余，统一通过 chatMessages.props.standard 持久化

    chatMessages: [
      {
        id: 1,
        role: 'ai',
        type: 'ai',
        content: '您好！我是CPA智能助手，将协助您完成审计复核工作。请点击下方的功能按钮开始操作，或直接与我对话。',
        isvaluable: false,
        timestamp: new Date().toISOString()
      }
    ],

    

    // 超时管理
    timeout: {
      timers: new Map(),          // 活跃的定时器
      defaultDuration: 20000,     // 默认超时时间(毫秒)
      strategy: 'wait',           // 超时策略：wait, warn_continue
      maxRetries: 3,              // 最大重试次数
      currentRetries: 0,          // 当前重试次数
      history: []                 // 超时历史记录
    }
  }),
  
  // ===== 计算属性 (Getters) =====
  // 提供对状态的只读访问和派生计算
  getters: {
    // 工作区基础信息访问器
    getCurrentWorkspace: (state) => state.currentWorkspace,     // 获取当前工作区
    getWorkspaces: (state) => state.workspaces,               // 获取所有工作区列表
    isLoading: (state) => state.loading,                      // 获取加载状态
    getError: (state) => state.error,                         // 获取错误信息
    
    // 复核流程状态访问器
    getReviewProcess: (state) => state.reviewProcess,          // 获取完整复核流程状态
    isReviewActive: (state) => state.reviewProcess.isActive,   // 检查复核流程是否激活
    getReviewStatus: (state) => state.reviewProcess.status,    // 获取复核流程状态
    getReviewStages: (state) => state.reviewProcess.stages,    // 获取复核阶段列表
    getCurrentStage: (state) => {
      const stages = state.reviewProcess.stages
      const index = state.reviewProcess.currentStageIndex
      return stages[index] || null
    },                                                          // 获取当前复核阶段
    
    // 数据库接口状态访问器
    getDatabaseStatus: (state) => state.database,              // 获取数据库连接状态
    
    

    // 超时管理状态访问器
    getTimeoutStatus: (state) => state.timeout,                 // 获取超时管理状态
    
    // 文件请求状态访问器
    getFileRequest: (state) => state.fileRequest,             // 获取完整文件请求状态
    isWaitingForFiles: (state) => state.fileRequest.waitingForUser,  // 检查是否等待用户提供文件
    getRequestedFiles: (state) => state.fileRequest.requestedFiles,  // 获取请求的文件列表
    getWarningLogsData: (state) => state.fileRequest.warningLogs,        // 获取警告日志
    
    // 智能体状态访问器
    getAgentStatus: (state) => state.agent.status,            // 获取智能体当前状态
    getCurrentTask: (state) => state.agent.currentTask,       // 获取智能体当前任务

    // 聊天消息访问器
    getChatMessages: (state) => state.chatMessages
  },
  
  // ===== 操作方法 (Actions) =====
  // 包含所有状态变更逻辑和异步操作
  actions: {
    buildItemKey(projectId, eventId) {
      const pid = projectId || this.userContext?.projectId || this.currentWorkspace?.id || 'default'
      const eid = eventId || this.currentReviewEvent?.id || 'unknown'
      return `${pid}:${eid}`
    },
    // ===== 工作区基础管理 =====
    
    /**
     * 加载所有可用工作区列表
     * 从服务器获取用户有权限访问的工作区
     */
    async loadWorkspaces() {
      this.loading = true
      this.error = null
      try {
        // TODO: 替换为实际的API调用
        // const response = await api.getWorkspaces()
        // this.workspaces = response.data
        
        // 模拟数据 - 实际项目中应从后端API获取
        this.workspaces = [
          { id: 1, name: '审计项目A工作区', description: '年度财务审计项目' },
          { id: 2, name: '审计项目B工作区', description: '专项合规审计项目' }
        ]
      } catch (error) {
        this.error = error.message
        console.error('获取工作区失败:', error)
      } finally {
        this.loading = false
      }
    },
    
    /**
     * 设置当前活跃工作区
     * @param {Object} workspace - 工作区对象
     */
    setCurrentWorkspace(workspace) {
      this.currentWorkspace = workspace
    },

    // ===== 复核流程管理 =====
    
    

    /**
     * 暂停复核流程
     * 通常在需要用户干预时调用
     */
    pauseReviewProcess() {
      this.reviewProcess.status = 'paused'
      this.agent.status = 'waiting'
    },

    /**
     * 恢复复核流程
     * 从暂停状态继续执行
     */
    resumeReviewProcess() {
      // 统一进行中状态为 'analyzing'，与后端消息语义保持一致
      this.reviewProcess.status = 'analyzing'
      this.agent.status = 'processing'
      this.agent.lastActivity = new Date()
    },

    setProjectId(projectId) {
      this.userContext.projectId = projectId
    },

    setFunctionalArea(area) {
      this.userContext.functionalArea = area
    },

    startSession(scope = {}) {
      const id = `sess_${Date.now()}_${Math.floor(Math.random() * 10000)}`
      const projectId = scope.projectId || this.currentWorkspace?.id || 'default'
      const area = scope.functionalArea || this.userContext.functionalArea || null
      const eventId = scope.eventId || null
      this.userContext.latestSessionId = id
      const index = JSON.parse(localStorage.getItem('session_index') || '[]')
      index.unshift({ id, projectId, area, eventId, startedAt: new Date().toISOString() })
      if (index.length > 500) {
        index.splice(500)
      }
      localStorage.setItem('session_index', JSON.stringify(index))
      return id
    },

    getLatestSession() {
      const id = this.userContext.latestSessionId
      const index = JSON.parse(localStorage.getItem('session_index') || '[]')
      return index.find(s => s.id === id) || null
    },

    /**
     * 完成复核流程
     * 清理所有相关状态并重置智能体
     */
    completeReviewProcess() {
      this.reviewProcess.isActive = false
      this.reviewProcess.status = 'completed'
      this.reviewProcess.progress = 100
      this.agent.status = 'ready'
      this.agent.currentTask = null
      this.clearFileRequest()  // 清理文件请求状态
    },
    
    /**
     * 设置复核状态
     * @param {string} status - 新的复核状态
     */
    setReviewStatus(status) {
      this.reviewProcess.status = status;
    },

    // ===== 聊天消息统一模型与持久化 =====
    addChatMessage(message) {
      const normalized = {
        id: message.id || (Date.now() + Math.random()),
        role: message.role || (message.type === 'user' ? 'user' : 'ai'),
        type: message.type || (message.role || 'ai'),
        content: message.content,
        data: message.data,
        title: message.title,
        component: message.component,
        props: message.props,
        isvaluable: message.isvaluable ?? (message.role === 'user'),
        status: this.reviewProcess.status,
        timestamp: (message.timestamp ? new Date(message.timestamp) : new Date()).toISOString()
      }
      this.chatMessages.push(normalized)
    },

    removeChatMessageById(messageId) {
      const idx = this.chatMessages.findIndex(m => m.id === messageId)
      if (idx !== -1) {
        this.chatMessages.splice(idx, 1)
      }
    },

    resetChatMessages() {
      this.chatMessages = [
        {
          id: 1,
          role: 'ai',
          type: 'ai',
          content: '您好！我是CPA智能助手，将协助您完成审计复核工作。请点击下方的功能按钮开始操作，或直接与我对话。',
          isvaluable: false,
          timestamp: new Date().toISOString()
        }
      ]
    },

    // ===== 标准生成与恢复逻辑 =====
    setPendingStandard(messageId, requestPayload) {
      this.pendingStandardMessageId = messageId
      this.pendingStandardRequest = requestPayload || null
    },
    clearPendingStandard() {
      this.pendingStandardMessageId = null
      this.pendingStandardRequest = null
    },
    updateStandardForPendingMessage(standardData) {
      const id = this.pendingStandardMessageId
      if (!id) return
      const target = (this.chatMessages || []).find(m => m.id === id)
      if (target) {
        target.props = target.props || {}
        target.props.standardReady = true
        target.props.standard = standardData?.审计证据标准 || standardData || null
      }
      this.clearPendingStandard()
    },
    async recoverStandardIfPending() {
      const pendingId = this.pendingStandardMessageId
      // 若无待回填则无需恢复
      if (!pendingId) return { success: false, reason: 'no_pending' }
      // 调用后端重新获取标准并回填
      const payload = this.pendingStandardRequest
      if (payload) {
        try {
          const axios = (await import('axios')).default
          const response = await axios.post('/workspace/standards', payload)
          this.updateStandardForPendingMessage(response.data)
          return { success: true, data: response.data, request: payload }
        } catch (error) {
          console.error('刷新恢复标准失败:', error)
          return { success: false, error: error?.message || String(error) }
        }
      }
      return { success: false, reason: 'no_payload' }
    },
    

    // ===== 默认复核设置管理 =====
    
    /**
     * 保存默认复核设置
     * 将用户配置的复核参数持久化存储
     * @param {Object} settings - 复核设置对象
     * @returns {Promise<Object>} 保存结果
     */
    async saveDefaultReviewSettings(settings) {
      try {
        // TODO: 替换为实际的数据库API调用
        // const response = await api.saveDefaultReviewSettings({
        //   projectId: this.currentWorkspace?.id,
        //   settings: settings
        // })
        
        // 模拟数据库保存操作延迟
        await new Promise(resolve => setTimeout(resolve, 500))
        
        // 构造设置数据对象
        const settingsData = {
          id: Date.now(),
          projectId: this.currentWorkspace?.id || 'default',
          settings: settings,
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString()
        }
        
        // 临时存储到localStorage作为数据库的替代
        // 实际项目中应调用后端API进行持久化
        localStorage.setItem('defaultReviewSettings', JSON.stringify(settingsData))
        
        // 记录设置变更历史，便于审计追踪
        this.addSettingsHistory('保存默认复核设置', settings)
        
        return {
          success: true,
          message: '默认复核设置已更新',
          data: settingsData
        }
      } catch (error) {
        console.error('保存默认复核设置失败:', error)
        throw new Error('保存设置失败，请稍后重试')
      }
    },

    /**
     * 加载默认复核设置
     * 从存储中获取指定项目的复核设置
     * @param {string|null} projectId - 项目ID，为空时使用当前工作区ID
     * @returns {Promise<Object>} 设置数据
     */
    async loadDefaultReviewSettings(projectId = null) {
      try {
        // TODO: 替换为实际的数据库API调用
        // const response = await api.getDefaultReviewSettings({
        //   projectId: projectId || this.currentWorkspace?.id
        // })
        
        // 模拟数据库读取操作延迟
        await new Promise(resolve => setTimeout(resolve, 300))
        
        // 从localStorage读取作为数据库的替代
        // 实际项目中应调用后端API获取数据
        const savedSettings = localStorage.getItem('defaultReviewSettings')
        
        if (savedSettings) {
          const settingsData = JSON.parse(savedSettings)
          return {
            success: true,
            data: settingsData
          }
        } else {
          // 如果没有保存的设置，返回默认模板
          return {
            success: true,
            data: this.getDefaultReviewSettingsTemplate()
          }
        }
      } catch (error) {
        console.error('加载默认复核设置失败:', error)
        throw new Error('加载设置失败，请稍后重试')
      }
    },

    /**
     * 获取默认复核设置模板
     * 返回智能体交互超时处理策略的默认配置模板
     * @returns {Object} 默认设置模板
     */
    getDefaultReviewSettingsTemplate() {
      return {
        id: null,
        projectId: this.currentWorkspace?.id || 'default',
        settings: {
          // 智能体交互超时处理策略 - 核心配置
          timeout: {
            duration: '20',              // 超时时间（秒）
            action: 'wait',              // 超时处理方式：wait | warn_continue
            scenarios: {
              documentTransfer: true,     // 底稿传输超时处理
              infoRetrieval: true,       // 信息检索缺失时的超时处理（用于超时回溯分析）
              analysisUncertain: true    // 复核分析不确定时的处理
            },
            protection: {
              maxRetries: '3',           // 同一类型超时最大重试次数
              pauseThreshold: '4',       // 第几次自动暂停并要求用户介入
              enableLogging: true        // 是否启用详细日志记录
            }
          }
        },
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString()
      }
    },

    async deleteDefaultReviewSettings(projectId = null) {
      try {
        // TODO: 替换为实际的数据库API调用
        // const response = await api.deleteDefaultReviewSettings({
        //   projectId: projectId || this.currentWorkspace?.id
        // })
        
        // 模拟数据库删除操作
        await new Promise(resolve => setTimeout(resolve, 300))
        
        // 从localStorage删除
        localStorage.removeItem('defaultReviewSettings')
        
        this.addSettingsHistory('删除默认复核设置', null)
        
        return {
          success: true,
          message: '默认复核设置已删除'
        }
      } catch (error) {
        console.error('删除默认复核设置失败:', error)
        throw new Error('删除设置失败，请稍后重试')
      }
    },

    //记录设置操作历史
    addSettingsHistory(action, settings) {
      try {
        const historyKey = 'reviewSettingsHistory'
        const existingHistory = JSON.parse(localStorage.getItem(historyKey) || '[]')
        
        const historyRecord = {
          id: Date.now(),
          action: action,
          settings: settings ? JSON.parse(JSON.stringify(settings)) : null,
          timestamp: new Date().toISOString(),
          projectId: this.currentWorkspace?.id || 'default'
        }
        
        existingHistory.unshift(historyRecord)
        
        // 只保留最近50条记录
        if (existingHistory.length > 50) {
          existingHistory.splice(50)
        }
        
        localStorage.setItem(historyKey, JSON.stringify(existingHistory))
      } catch (error) {
        console.error('记录设置历史失败:', error)
      }
    },

    async getSettingsHistory(projectId = null) {
      try {
        // TODO: 替换为实际的数据库API调用
        // const response = await api.getSettingsHistory({
        //   projectId: projectId || this.currentWorkspace?.id
        // })
        
        const historyKey = 'reviewSettingsHistory'
        const history = JSON.parse(localStorage.getItem(historyKey) || '[]')
        
        // 过滤当前项目的历史记录
        const currentProjectId = projectId || this.currentWorkspace?.id || 'default'
        const filteredHistory = history.filter(record => record.projectId === currentProjectId)
        
        return {
          success: true,
          data: filteredHistory
        }
      } catch (error) {
        console.error('获取设置历史失败:', error)
        throw new Error('获取历史记录失败，请稍后重试')
      }
    },

    /**
     * 处理默认复核设置更新通知
     * 当设置发生变更时触发，确保新设置能被其他模块读取
     * @param {Object} settings - 更新后的设置对象
     */
    async onDefaultReviewSettingsUpdated(settings) {
      try {
        // 更新当前的默认设置
        this.defaultReviewSettings = { ...settings }
        
        // 如果有正在进行的复核流程，标记需要在下次复核时应用新设置
        if (this.reviewProcess.isActive) {
          this.reviewProcess.pendingSettingsUpdate = true
          this.reviewProcess.newSettings = settings
          console.log('检测到活跃的复核流程，新设置将在下次复核时生效')
        }
        
        // 添加设置历史记录
        this.addSettingsHistory('设置更新', settings)
        
        console.log('默认复核设置已更新并应用')
      } catch (error) {
        console.error('处理设置更新失败:', error)
        throw error
      }
    },

    /**
     * 删除设置管理历史记录
     * 清理指定项目的设置变更历史，用于数据清理和隐私保护
     * @param {string|null} projectId - 项目ID，为空时清理当前项目
     * @returns {Promise<Object>} 删除结果
     */
    async deleteSettingsHistory(projectId = null) {
      try {
        // TODO: 替换为实际的数据库API调用
        // const response = await api.deleteSettingsHistory({
        //   projectId: projectId || this.currentWorkspace?.id
        // })
        
        const historyKey = 'reviewSettingsHistory'
        const currentProjectId = projectId || this.currentWorkspace?.id || 'default'
        const existingHistory = JSON.parse(localStorage.getItem(historyKey) || '[]')
        
        // 过滤掉指定项目的历史记录
        const filteredHistory = existingHistory.filter(record => record.projectId !== currentProjectId)
        localStorage.setItem(historyKey, JSON.stringify(filteredHistory))
        
        return {
          success: true,
          message: '设置历史记录已清理',
          deletedCount: existingHistory.length - filteredHistory.length
        }
      } catch (error) {
        console.error('删除设置历史失败:', error)
        throw new Error('清理历史记录失败，请稍后重试')
      }
    },

    /**
     * 记录警告日志
     * 用于记录超时处理、异常情况等警告信息，支持防死循环保护机制
     * @param {string} type - 警告类型：timeout | error | protection
     * @param {string} message - 警告消息
     * @param {Object} context - 上下文信息
     * @returns {Promise<Object>} 记录结果
     */
    async logWarning(type, message, context = {}) {
      try {
        // TODO: 替换为实际的数据库API调用
        // const response = await api.logWarning({
        //   type, message, context,
        //   projectId: this.currentWorkspace?.id
        // })
        
        const warningLog = {
          id: Date.now(),
          type: type,
          message: message,
          context: context,
          timestamp: new Date().toISOString(),
          projectId: this.currentWorkspace?.id || 'default'
        }
        
        // 存储到localStorage模拟数据库操作
        const warningKey = 'warningLogs'
        const existingLogs = JSON.parse(localStorage.getItem(warningKey) || '[]')
        existingLogs.unshift(warningLog)
        
        // 只保留最近1000条警告日志
        if (existingLogs.length > 1000) {
          existingLogs.splice(1000)
        }
        
        localStorage.setItem(warningKey, JSON.stringify(existingLogs))
        
        // 同时添加到内存中的警告日志数组
        this.fileRequest.warningLogs.unshift(warningLog)
        if (this.fileRequest.warningLogs.length > 100) {
          this.fileRequest.warningLogs.splice(100)
        }
        
        return {
          success: true,
          logId: warningLog.id
        }
      } catch (error) {
        console.error('记录警告日志失败:', error)
        throw new Error('日志记录失败')
      }
    },

    /**
     * 获取警告日志列表
     * 检索指定项目的警告日志，支持分页和过滤
     * @param {Object} options - 查询选项
     * @returns {Promise<Object>} 日志列表
     */
    async getWarningLogs(options = {}) {
      try {
        const {
          projectId = null,
          type = null,
          limit = 50,
          offset = 0
        } = options
        
        // TODO: 替换为实际的数据库API调用
        // const response = await api.getWarningLogs({
        //   projectId: projectId || this.currentWorkspace?.id,
        //   type, limit, offset
        // })
        
        const warningKey = 'warningLogs'
        const allLogs = JSON.parse(localStorage.getItem(warningKey) || '[]')
        const currentProjectId = projectId || this.currentWorkspace?.id || 'default'
        
        // 过滤项目和类型
        let filteredLogs = allLogs.filter(log => log.projectId === currentProjectId)
        if (type) {
          filteredLogs = filteredLogs.filter(log => log.type === type)
        }
        
        // 分页处理
        const paginatedLogs = filteredLogs.slice(offset, offset + limit)
        
        return {
          success: true,
          data: paginatedLogs,
          total: filteredLogs.length,
          hasMore: offset + limit < filteredLogs.length
        }
      } catch (error) {
        console.error('获取警告日志失败:', error)
        throw new Error('获取日志失败，请稍后重试')
      }
    },

     /**
      * 导出设置配置
      * 将当前项目的默认复核设置导出为JSON格式，便于项目间复用
      * @param {string|null} projectId - 项目ID，为空时导出当前项目设置
      * @returns {Promise<Object>} 导出结果
      */
     async exportSettings(projectId = null) {
       try {
         // 获取要导出的设置
         const settingsResult = await this.loadDefaultReviewSettings(projectId)
         if (!settingsResult.success) {
           throw new Error('无法获取设置数据')
         }

         const exportData = {
           version: '1.0',
           exportTime: new Date().toISOString(),
           projectId: projectId || this.currentWorkspace?.id || 'default',
           settings: settingsResult.data.settings,
           metadata: {
             exportedBy: 'workspace-store',
             description: '默认复核设置配置文件'
           }
         }

         // 生成下载文件
         const blob = new Blob([JSON.stringify(exportData, null, 2)], {
           type: 'application/json'
         })
         const url = URL.createObjectURL(blob)
         const filename = `review-settings-${projectId || 'current'}-${Date.now()}.json`

         // 触发下载
         const link = document.createElement('a')
         link.href = url
         link.download = filename
         document.body.appendChild(link)
         link.click()
         document.body.removeChild(link)
         URL.revokeObjectURL(url)

         return {
           success: true,
           message: '设置配置已导出',
           filename: filename
         }
       } catch (error) {
         console.error('导出设置失败:', error)
         throw new Error('导出配置失败，请稍后重试')
       }
     },

     // ===== 重大事项数据管理 =====
    
    /**
     * 获取未复核的重大事项列表
     * 从数据库获取当前项目中状态为"未复核"的重大事项
     * @param {string|null} projectId - 项目ID，为空时使用当前工作区ID
     * @returns {Promise<Object>} 未复核事项列表
     */
    async getUnreviewedMajorEvents(projectId = null) {
      try {
        // TODO: 替换为实际的数据库API调用
        // const response = await api.getUnreviewedMajorEvents({
        //   projectId: projectId || this.currentWorkspace?.id
        // })
        
        // 模拟数据库读取操作延迟
        await new Promise(resolve => setTimeout(resolve, 500))
        
        const currentProjectId = projectId || this.currentWorkspace?.id || 'default'
        
        // 从localStorage读取重大事项数据作为数据库的替代
        const majorEventsKey = `majorEvents_${currentProjectId}`
        const savedEvents = localStorage.getItem(majorEventsKey)
        
        let allEvents = []
        if (savedEvents) {
          allEvents = JSON.parse(savedEvents)
        } else {
          // 如果没有数据，创建一些模拟的未复核事项
          allEvents = [
            {
              id: 'event_001',
              title: '持续经营风险',
              description: '被审计单位所属行业发生重大变化，导致对持续经营能力产生重大不确定性。',
              status: 'unreviewed',
              createdAt: new Date(Date.now() - 86400000).toISOString(), // 1天前
              updatedAt: new Date(Date.now() - 86400000).toISOString(),
              projectId: currentProjectId,
              auditObjectives: '就是否存在可能导致对被审计单位持续经营能力产生重大疑虑的事项或情况得出结论。',
              evidenceStandards: {
                situation1: {
                  auditConclusion: '持续经营疑虑证据充分、适当',
                  evidenceCategories: [],
                  adequacyCriteria: ''
                },
                situation2: {
                  auditConclusion: '持续经营疑虑证据不充分',
                  evidenceCategories: [],
                  adequacyCriteria: ''
                },
                standardBasis: []
              }
            },
            {
              id: 'event_002', 
              title: '应收账款账龄异常',
              description: 'ABC公司客户资金紧张，导致回款延迟，账龄普遍超180天。',
              status: 'unreviewed',
              createdAt: new Date(Date.now() - 172800000).toISOString(), // 2天前
              updatedAt: new Date(Date.now() - 172800000).toISOString(),
              projectId: currentProjectId,
              auditObjectives: '评估应收账款的计价与分摊是否恰当。',
              evidenceStandards: {
                situation1: {
                  auditConclusion: '应收账款账龄测试合理',
                  evidenceCategories: [],
                  adequacyCriteria: ''
                },
                situation2: {
                  auditConclusion: '应收账款账龄测试存在异常',
                  evidenceCategories: [],
                  adequacyCriteria: ''
                },
                standardBasis: []
              }
            }
          ]
          // 保存模拟数据到localStorage
          localStorage.setItem(majorEventsKey, JSON.stringify(allEvents))
        }
        
        // 过滤出未复核的事项
        const unreviewedEvents = allEvents.filter(event => event.status === 'unreviewed')
        
        return {
          success: true,
          data: unreviewedEvents,
          total: unreviewedEvents.length
        }
      } catch (error) {
        console.error('获取未复核重大事项失败:', error)
        throw new Error('获取事项列表失败，请稍后重试')
      }
    },

    /**
     * 更新重大事项状态
     * 将指定重大事项的状态更新为"复核中"或其他状态
     * @param {string} eventId - 事项ID
     * @param {string} newStatus - 新状态：unreviewed | reviewing | reviewed | completed
     * @param {Object} reviewData - 复核相关数据
     * @returns {Promise<Object>} 更新结果
     */
    async updateMajorEventStatus(eventId, newStatus, reviewData = {}) {
      try {
        // TODO: 替换为实际的数据库API调用
        // const response = await api.updateMajorEventStatus({
        //   eventId,
        //   status: newStatus,
        //   reviewData,
        //   updatedBy: this.currentUser?.id
        // })
        
        // 模拟数据库更新操作延迟
        await new Promise(resolve => setTimeout(resolve, 300))
        
        // 根据当前项目从localStorage获取事项数据（按项目隔离）
        const currentProjectId = this.currentWorkspace?.id || 'default'
        const majorEventsKey = `majorEvents_${currentProjectId}`
        const savedEvents = localStorage.getItem(majorEventsKey)
        
        if (savedEvents) {
          const allEvents = JSON.parse(savedEvents)
          const eventIndex = allEvents.findIndex(event => event.id === eventId)
          
          if (eventIndex !== -1) {
            // 保存旧状态用于日志记录
            const oldStatus = allEvents[eventIndex].status
            
            // 更新事项状态和相关数据
            allEvents[eventIndex] = {
              ...allEvents[eventIndex],
              status: newStatus,
              updatedAt: new Date().toISOString(),
              reviewData: reviewData
            }
            
            // 保存更新后的数据到当前项目的存储键
            localStorage.setItem(majorEventsKey, JSON.stringify(allEvents))
            
            // 记录状态变更历史
            await this.logWarning('status_change', `重大事项状态更新: ${eventId} -> ${newStatus}`, {
              eventId,
              oldStatus,
              newStatus,
              reviewData
            })
            
            return {
              success: true,
              message: '事项状态已更新',
              data: allEvents[eventIndex]
            }
          } else {
            throw new Error('未找到指定的重大事项')
          }
        } else {
          throw new Error('未找到事项数据')
        }
      } catch (error) {
        console.error('更新重大事项状态失败:', error)
        throw new Error('状态更新失败，请稍后重试')
      }
    },

    /**
     * 设置当前复核的重大事项
     * 更新工作区状态，记录当前正在复核的事项信息
     * @param {Object} event - 重大事项对象
     * @returns {Promise<void>}
     */
    async setCurrentReviewEvent(event) {
      try {
        // 更新当前复核事项状态
        this.currentReviewEvent = {
          id: event.id,
          title: event.title,
          description: event.description,
          status: 'reviewing',
          startTime: new Date().toISOString(),
          auditObjectives: event.auditObjectives,
          createdAt: event.createdAt,
          itemKey: this.buildItemKey(this.userContext?.projectId || this.currentWorkspace?.id, event.id)
        }
        
        // 保存到localStorage作为数据库模拟
        localStorage.setItem('currentReviewEvent', JSON.stringify(this.currentReviewEvent))
        localStorage.setItem('currentReviewItemKey', this.currentReviewEvent.itemKey)
        
        // TODO: 替换为实际的数据库API调用
        // await api.setCurrentReviewEvent({
        //   workspaceId: this.currentWorkspace?.id,
        //   eventId: event.id,
        //   startTime: new Date().toISOString()
        // })
        
        console.log('当前复核事项已设置:', this.currentReviewEvent)
        
      } catch (error) {
        console.error('设置当前复核事项失败:', error)
        throw new Error('设置复核事项失败，请稍后重试')
      }
    },

    /**
     * 启动重大事项复核流程
     * 开始对指定重大事项进行智能复核分析
     * @param {string} eventId - 事项ID
     * @param {Object} reviewConfig - 复核配置参数
     * @returns {Promise<Object>} 启动结果
     */
    async startMajorEventReview(eventId, reviewConfig = {}) {
      try {
        // 检查事项当前状态，避免重复启动复核
        const currentProjectId = this.currentWorkspace?.id || 'default'
        const majorEventsKey = `majorEvents_${currentProjectId}`
        const savedEvents = localStorage.getItem(majorEventsKey)
        if (savedEvents) {
          const allEvents = JSON.parse(savedEvents)
          const currentEvent = allEvents.find(event => event.id === eventId)
          
          if (currentEvent && currentEvent.status === 'reviewing') {
            return {
              success: false,
              message: '该重大事项已在复核中，无需重复启动',
              data: { eventId, currentStatus: 'reviewing' }
            }
          }
        }
        
        // 从localStorage获取事件数据
        let event = null;
        if (savedEvents) {
          const allEvents = JSON.parse(savedEvents);
          event = allEvents.find(e => e.id === eventId);
        }
        
        // 如果找不到事件数据，返回错误
        if (!event) {
          throw new Error('未找到指定的重大事项');
        }
        
        // 构造复核数据，确保符合后端ReviewData模型要求
        // 提供最小有效结构以避免"list index out of range"错误
        const evidenceClassification = event.evidenceStandards?.审计证据分类与要求 || 
          [{ "默认分类": { "默认子分类": [{ "证据内容": "", "质量要求": "" }] } }];
        
        const reviewData = {
          重大事项概述: event.description || '',
          审计目标: event.auditObjectives || '',
          审计证据标准: {
            审计结论: event.evidenceStandards?.审计结论 || '',
            审计证据分类与要求: evidenceClassification,
            充分_适当评判标准: event.evidenceStandards?.充分_适当评判标准 || ''
          }
        };
        
        // 调用后端/workspace/execute_review接口
        const axios = (await import('axios')).default;
        const response = await axios.post('/workspace/execute_review', reviewData);
        
        // 更新事项状态为"复核中"
        await this.updateMajorEventStatus(eventId, 'reviewing', {
          startTime: new Date().toISOString(),
          reviewConfig: reviewConfig
        })
        
        // 启动复核流程
        this.reviewProcess.isActive = true
        this.reviewProcess.status = 'analyzing'
        // currentStep 字段已移除，使用 status/stages 表示流程进度
        this.reviewProcess.progress = 10
        this.reviewProcess.currentEventId = eventId
        
        // 设置智能体状态
        this.agent.status = 'processing'
        this.agent.currentTask = `正在复核重大事项: ${eventId}`
        this.agent.lastActivity = new Date()
        
        return {
          success: true,
          message: '重大事项复核流程已启动',
          data: response.data
        }
      } catch (error) {
        console.error('启动重大事项复核失败:', error)
        throw new Error('启动复核失败，请稍后重试')
      }
    },

    /**
     * 导入设置配置
     * 从JSON文件导入默认复核设置，支持配置验证和冲突处理
     * @param {File} file - 导入的JSON文件
      * @param {boolean} overwrite - 是否覆盖现有设置
      * @returns {Promise<Object>} 导入结果
      */
     async importSettings(file, overwrite = false) {
       try {
         // 验证文件类型
         if (!file || file.type !== 'application/json') {
           throw new Error('请选择有效的JSON配置文件')
         }

         // 读取文件内容
         const fileContent = await new Promise((resolve, reject) => {
           const reader = new FileReader()
           reader.onload = (e) => resolve(e.target.result)
           reader.onerror = () => reject(new Error('文件读取失败'))
           reader.readAsText(file)
         })

         // 解析JSON数据
         let importData
         try {
           importData = JSON.parse(fileContent)
         } catch (error) {
           throw new Error('配置文件格式错误，请检查JSON格式')
         }

         // 验证导入数据结构
         if (!importData.settings || !importData.settings.timeout) {
           throw new Error('配置文件缺少必要的设置数据')
         }

         // 检查是否存在现有设置
         if (!overwrite) {
           const existingSettings = localStorage.getItem('defaultReviewSettings')
           if (existingSettings) {
             throw new Error('已存在设置配置，请选择是否覆盖现有设置')
           }
         }

         // 保存导入的设置
         const saveResult = await this.saveDefaultReviewSettings(importData.settings)
         if (!saveResult.success) {
           throw new Error('保存导入设置失败')
         }

         // 记录导入历史
         this.addSettingsHistory('导入设置配置', importData.settings)

         return {
           success: true,
           message: '设置配置已成功导入',
           importedSettings: importData.settings
         }
       } catch (error) {
         console.error('导入设置失败:', error)
         throw error
       }
     },

     /**
      * 重置超时计数器
      * 手动清除防死循环保护机制的计数器，允许用户重新开始超时处理
      * @param {string} taskId - 任务ID
      * @returns {Promise<Object>} 重置结果
      */
     async resetTimeoutCounter(taskId = null) {
       try {
         // TODO: 替换为实际的数据库API调用
         // const response = await api.resetTimeoutCounter({
         //   taskId: taskId,
         //   projectId: this.currentWorkspace?.id
         // })

         const counterKey = 'timeoutCounters'
         const currentProjectId = this.currentWorkspace?.id || 'default'
         const counters = JSON.parse(localStorage.getItem(counterKey) || '{}')

         if (taskId) {
           // 重置特定任务的计数器
           delete counters[`${currentProjectId}_${taskId}`]
         } else {
           // 重置当前项目的所有计数器
           Object.keys(counters).forEach(key => {
             if (key.startsWith(`${currentProjectId}_`)) {
               delete counters[key]
             }
           })
         }

         localStorage.setItem(counterKey, JSON.stringify(counters))

         // 记录重置操作
         await this.logWarning('protection', '超时计数器已重置', {
           taskId: taskId,
           resetTime: new Date().toISOString()
         })

         return {
           success: true,
           message: taskId ? '指定任务的超时计数器已重置' : '所有超时计数器已重置'
         }
       } catch (error) {
         console.error('重置超时计数器失败:', error)
         throw new Error('重置计数器失败，请稍后重试')
       }
     },

     // ===== 文件请求管理 =====
     // 智能体动态请求文件的核心逻辑
    
    /**
     * 请求文件 - 智能体在复核过程中动态请求所需文件
     * 仅支持用户手动提供文件（移除自动匹配逻辑）
     * @param {Array<string>} fileTypes - 请求的文件类型列表
     * @param {string} reason - 请求文件的原因说明
     * @returns {Promise<Array>} 请求的文件列表
     */
    async requestFiles(fileTypes, reason = '') {
      try {
        // 异常处理和防死循环检查
        const validationResult = this.validateFileRequest(fileTypes, reason)
        if (!validationResult.isValid) {
          this.handleRequestError(validationResult.error, 'validation_failed')
          return []
        }

        // 更新请求统计
        this.updateRequestStatistics()
        
        // 设置请求状态
        this.fileRequest.isRequesting = true
        // 暂停复核流程，等待用户提供文件
        this.pauseReviewProcess()
      
      // 创建文件请求对象列表
      this.fileRequest.requestedFiles = fileTypes.map(type => ({
        id: Date.now() + Math.random(),  // 唯一标识
        type,                            // 文件类型
        reason,                          // 请求原因
        status: 'pending',               // 状态：pending(待提供), provided(已提供), skipped(已跳过)
        timestamp: new Date()            // 请求时间
      }))
      
      // 简化：不进行自动匹配，直接进入等待用户提供
      this.fileRequest.waitingForUser = true
      this.agent.status = 'waiting'
      const pendingTypes = this.fileRequest.requestedFiles.map(f => f.type).join(', ')
      this.agent.currentTask = `等待用户提供: ${pendingTypes}`
      
      // 启动等待超时机制
      this.startWaitTimeout()
      
      return this.fileRequest.requestedFiles
      
      } catch (error) {
        // 捕获并处理所有异常
        this.handleRequestError(error, 'request_failed')
        return []
      }
    },

    startWaitTimeout() {
      if (this.fileRequest.waitTimeout) {
        clearTimeout(this.fileRequest.waitTimeout)
      }
      
      // 记录等待开始时间
      this.fileRequest.waitStartTime = Date.now()
      
      this.fileRequest.waitTimeout = setTimeout(() => {
        this.handleWaitTimeout()
      }, this.fileRequest.defaultWaitTime)
    },

    handleWaitTimeout() {
      const pendingFiles = this.fileRequest.requestedFiles.filter(f => f.status === 'pending')
      if (pendingFiles.length > 0) {
        // 记录警告日志
        const warningLog = {
          id: Date.now(),
          timestamp: new Date(),
          type: 'timeout',
          message: `用户在${this.fileRequest.defaultWaitTime/1000}秒内未提供所需文件`,
          missingFiles: pendingFiles.map(f => f.type),
          action: 'continue_with_existing'
        }
        this.fileRequest.warningLogs.push(warningLog)
        
        // 标记文件为跳过状态
        pendingFiles.forEach(file => {
          file.status = 'skipped'
        })
        
        // 清理请求并继续复核流程（后端驱动）
        this.clearFileRequest()
        this.resumeReviewProcess()
      }
    },

    provideRequestedFile(fileId, fileInfo) {
      const file = this.fileRequest.requestedFiles.find(f => f.id === fileId)
      if (file) {
        file.status = 'provided'
        file.fileInfo = fileInfo
        file.providedAt = new Date()
        
        // 检查是否所有文件都已提供
        const allProvided = this.fileRequest.requestedFiles.every(f => 
          f.status === 'provided' || f.status === 'skipped'
        )
        
        if (allProvided) {
          this.clearFileRequest()
          this.resumeReviewProcess()
        }
      }
    },

    skipRequestedFile(fileId, reason = '') {
      const file = this.fileRequest.requestedFiles.find(f => f.id === fileId)
      if (file) {
        file.status = 'skipped'
        file.skipReason = reason
        file.skippedAt = new Date()
        
        // 记录跳过日志
        const warningLog = {
          id: Date.now(),
          timestamp: new Date(),
          type: 'user_skip',
          message: `用户选择跳过文件: ${file.type}`,
          reason: reason,
          action: 'continue_without_file'
        }
        this.fileRequest.warningLogs.push(warningLog)
      }
    },

    clearFileRequest() {
      this.fileRequest.isRequesting = false
      this.fileRequest.requestedFiles = []
      this.fileRequest.waitingForUser = false
      
      if (this.fileRequest.waitTimeout) {
        clearTimeout(this.fileRequest.waitTimeout)
        this.fileRequest.waitTimeout = null
      }
    },

    // 设置默认等待时间
    setDefaultWaitTime(seconds) {
      this.fileRequest.defaultWaitTime = seconds * 1000
    },

    // 清除警告日志
    clearWarningLogs() {
      this.fileRequest.warningLogs = []
    },


    // ===== 异常处理和防死循环机制 =====
    
    /**
     * 验证文件请求的合法性
     */
    validateFileRequest(fileTypes, reason) {
      // 初始化会话时间
      if (!this.fileRequest.sessionStartTime) {
        this.fileRequest.sessionStartTime = Date.now()
      }

      // 检查是否被阻止
      if (this.fileRequest.isBlocked) {
        return {
          isValid: false,
          error: `文件请求已被阻止: ${this.fileRequest.blockReason}`
        }
      }

      // 检查参数有效性
      if (!fileTypes || !Array.isArray(fileTypes) || fileTypes.length === 0) {
        return {
          isValid: false,
          error: '文件类型参数无效：必须是非空数组'
        }
      }

      // 检查请求次数限制
      if (this.fileRequest.requestCount >= this.fileRequest.maxRequestCount) {
        this.blockRequests('超出最大请求次数限制')
        return {
          isValid: false,
          error: `请求次数超限：已达到最大限制 ${this.fileRequest.maxRequestCount} 次`
        }
      }

      // 检查请求间隔
      const now = Date.now()
      if (this.fileRequest.lastRequestTime && 
          (now - this.fileRequest.lastRequestTime) < this.fileRequest.minRequestInterval) {
        return {
          isValid: false,
          error: `请求过于频繁：请等待 ${this.fileRequest.minRequestInterval/1000} 秒后再试`
        }
      }

      // 检查是否已有活跃请求
      if (this.fileRequest.isRequesting) {
        return {
          isValid: false,
          error: '已有活跃的文件请求，请等待当前请求完成'
        }
      }

      // 检查错误次数
      if (this.fileRequest.errorCount >= this.fileRequest.maxErrorCount) {
        this.blockRequests('错误次数过多')
        return {
          isValid: false,
          error: `错误次数超限：已达到最大限制 ${this.fileRequest.maxErrorCount} 次`
        }
      }

      return { isValid: true }
    },

    /**
     * 更新请求统计信息
     */
    updateRequestStatistics() {
      this.fileRequest.requestCount++
      this.fileRequest.lastRequestTime = Date.now()
      this.agent.lastActivity = new Date()
    },

    /**
     * 处理请求错误
     */
    handleRequestError(error, errorType) {
      this.fileRequest.errorCount++
      this.fileRequest.isRequesting = false
      
      // 记录错误历史
      const errorRecord = {
        id: Date.now() + Math.random(),
        timestamp: new Date(),
        type: errorType,
        message: error.message || error,
        stack: error.stack,
        requestCount: this.fileRequest.requestCount,
        errorCount: this.fileRequest.errorCount
      }
      
      this.agent.errorHistory.push(errorRecord)
      
      // 记录警告日志
      const warningLog = {
        id: Date.now(),
        timestamp: new Date(),
        type: 'error',
        message: `文件请求错误: ${error.message || error}`,
        errorType,
        action: 'error_handled'
      }
      this.fileRequest.warningLogs.push(warningLog)
      
      // 更新智能体状态
      this.agent.status = 'error'
      this.agent.currentTask = `处理错误: ${error.message || error}`
      
      // 尝试恢复
      this.attemptRecovery(errorType)
    },

    /**
     * 阻止文件请求
     */
    blockRequests(reason) {
      this.fileRequest.isBlocked = true
      this.fileRequest.blockReason = reason
      this.agent.status = 'blocked'
      this.agent.currentTask = `已阻止: ${reason}`
      
      // 记录阻止日志
      const blockLog = {
        id: Date.now(),
        timestamp: new Date(),
        type: 'blocked',
        message: `文件请求已被阻止: ${reason}`,
        action: 'requests_blocked'
      }
      this.fileRequest.warningLogs.push(blockLog)
    },

    /**
     * 尝试恢复
     */
    attemptRecovery(errorType) {
      if (this.agent.recoveryAttempts >= this.agent.maxRecoveryAttempts) {
        this.blockRequests('恢复尝试次数超限')
        return
      }
      
      this.agent.recoveryAttempts++
      
      // 根据错误类型执行不同的恢复策略
      setTimeout(() => {
        switch (errorType) {
          case 'validation_failed':
            // 验证失败，重置部分状态
            this.fileRequest.isRequesting = false
            break
          case 'request_failed':
            // 请求失败，清理当前请求
            this.clearFileRequest()
            break
          default:
            // 通用恢复
            this.resetToSafeState()
        }
        
        this.agent.status = 'ready'
        this.agent.currentTask = `恢复完成 (尝试 ${this.agent.recoveryAttempts}/${this.agent.maxRecoveryAttempts})`
      }, 2000) // 2秒后尝试恢复
    },

    /**
     * 重置到安全状态
     */
    resetToSafeState() {
      // 清理超时定时器
      if (this.fileRequest.waitTimeout) {
        clearTimeout(this.fileRequest.waitTimeout)
        this.fileRequest.waitTimeout = null
      }
      
      // 重置请求状态
      this.fileRequest.isRequesting = false
      this.fileRequest.waitingForUser = false
      this.fileRequest.requestedFiles = []
      
      // 重置智能体状态
      this.agent.status = 'ready'
      this.agent.currentTask = null
    },

    /**
     * 解除阻止状态（管理员功能）
     */
    unblockRequests() {
      this.fileRequest.isBlocked = false
      this.fileRequest.blockReason = null
      this.fileRequest.errorCount = 0
      this.agent.recoveryAttempts = 0
      this.agent.status = 'ready'
      this.agent.currentTask = null
      
      // 记录解除阻止日志
      const unblockLog = {
        id: Date.now(),
        timestamp: new Date(),
        type: 'unblocked',
        message: '文件请求阻止状态已解除',
        action: 'requests_unblocked'
      }
      this.fileRequest.warningLogs.push(unblockLog)
    },

    /**
     * 重置会话统计
     */
    resetSessionStatistics() {
      this.fileRequest.requestCount = 0
      this.fileRequest.errorCount = 0
      this.fileRequest.lastRequestTime = null
      this.fileRequest.sessionStartTime = Date.now()
      this.agent.recoveryAttempts = 0
      this.agent.errorHistory = []
      
      // 如果当前被阻止，也一并解除
      if (this.fileRequest.isBlocked) {
        this.unblockRequests()
      }
    },

    // ===== 数据库接口预留方法 =====
    
    /**
     * 初始化数据库连接 - 使用localStorage模拟
     * 实际项目中应替换为真实的数据库连接
     */
    async initDatabase() {
      try {
        // TODO: 替换为实际数据库连接逻辑
        // await database.connect(config)
        
        // 模拟数据库连接延迟
        await new Promise(resolve => setTimeout(resolve, 500))
        
        this.database.connected = true
        this.database.lastSync = new Date()
        
        // 检查localStorage可用性
        if (typeof Storage !== 'undefined') {
          console.log('数据库模拟器已连接 (localStorage)')
        } else {
          throw new Error('浏览器不支持localStorage')
        }
      } catch (error) {
        this.database.connected = false
        this.database.errorLog.push({
          timestamp: new Date(),
          error: error.message,
          operation: 'connect'
        })
        throw error
      }
    },

    /**
     * 保存底稿文件数据到数据库
     * @param {Object} fileData - 底稿文件数据
     * @returns {Promise<Object>} 保存结果
     */
    async saveWorkpaperData(fileData) {
      try {
        // TODO: 替换为实际数据库API调用
        // const result = await api.saveWorkpaper(fileData)
        
        // 使用localStorage模拟数据库存储
        const key = `workpaper_${fileData.id || Date.now()}`
        const data = {
          ...fileData,
          savedAt: new Date().toISOString(),
          version: 1
        }
        
        localStorage.setItem(key, JSON.stringify(data))
        
        // 更新索引
        const index = JSON.parse(localStorage.getItem('workpaper_index') || '[]')
        index.push({ key, id: data.id, name: data.name, savedAt: data.savedAt })
        localStorage.setItem('workpaper_index', JSON.stringify(index))
        
        return { success: true, id: data.id, message: '底稿数据已保存' }
      } catch (error) {
        this.database.errorLog.push({
          timestamp: new Date(),
          error: error.message,
          operation: 'saveWorkpaper'
        })
        throw error
      }
    },

    /**
     * 从数据库加载底稿文件数据
     * @param {string} fileId - 文件ID
     * @returns {Promise<Object>} 文件数据
     */
    async loadWorkpaperData(fileId) {
      try {
        // TODO: 替换为实际数据库API调用
        // const result = await api.getWorkpaper(fileId)
        
        // 使用localStorage模拟数据库读取
        const key = `workpaper_${fileId}`
        const data = localStorage.getItem(key)
        
        if (!data) {
          throw new Error(`底稿文件 ${fileId} 不存在`)
        }
        
        return JSON.parse(data)
      } catch (error) {
        this.database.errorLog.push({
          timestamp: new Date(),
          error: error.message,
          operation: 'loadWorkpaper'
        })
        throw error
      }
    },

    /**
     * 获取所有底稿文件列表
     * @returns {Promise<Array>} 文件列表
     */
    async getWorkpaperList() {
      try {
        // TODO: 替换为实际数据库API调用
        // const result = await api.getWorkpaperList()
        
        // 使用localStorage模拟数据库查询
        const index = JSON.parse(localStorage.getItem('workpaper_index') || '[]')
        return index
      } catch (error) {
        this.database.errorLog.push({
          timestamp: new Date(),
          error: error.message,
          operation: 'getWorkpaperList'
        })
        throw error
      }
    },

    /**
     * 查询复核结果数据
     * @param {string} eventId - 重大事项ID
     * @returns {Promise<Object>} 复核结果数据
     */
    async queryReviewResult(eventId) {
      try {
        // TODO: 替换为实际数据库API调用
        // const result = await api.getReviewResult(eventId)
        
        // 使用localStorage模拟数据库查询
        const key = `review_result_${eventId}`
        const data = localStorage.getItem(key)
        
        if (data) {
          return JSON.parse(data)
        }
        
        // 如果没有找到，返回null
        return null
      } catch (error) {
        this.database.errorLog.push({
          timestamp: new Date(),
          error: error.message,
          operation: 'queryReviewResult'
        })
        throw error
      }
    },

    /**
     * 保存复核结果数据
     * @param {string} eventId - 重大事项ID
     * @param {Object} reviewData - 复核结果数据
     * @returns {Promise<Object>} 保存结果
     */
    async saveReviewResult(eventId, reviewData) {
      try {
        // TODO: 替换为实际数据库API调用
        // const result = await api.saveReviewResult(eventId, reviewData)
        
        // 使用localStorage模拟数据库存储
        const key = `review_result_${eventId}`
        const data = {
          eventId: eventId,
          ...reviewData,
          savedAt: new Date().toISOString(),
          version: reviewData.version || '1.0'
        }
        
        localStorage.setItem(key, JSON.stringify(data))
        
        // 更新复核结果索引
        const index = JSON.parse(localStorage.getItem('review_result_index') || '[]')
        const existingIndex = index.findIndex(item => item.eventId === eventId)
        
        if (existingIndex >= 0) {
          index[existingIndex] = { eventId, savedAt: data.savedAt, version: data.version }
        } else {
          index.push({ eventId, savedAt: data.savedAt, version: data.version })
        }
        
        localStorage.setItem('review_result_index', JSON.stringify(index))
        
        return { success: true, eventId, message: '复核结果已保存' }
      } catch (error) {
        this.database.errorLog.push({
          timestamp: new Date(),
          error: error.message,
          operation: 'saveReviewResult'
        })
        throw error
      }
    },

    /**
     * 查询用户调整历史
     * @param {string} eventId - 重大事项ID
     * @param {Object} filters - 过滤条件
     * @returns {Promise<Array>} 调整历史列表
     */
    async queryAdjustmentHistory(eventId, filters = {}) {
      try {
        // TODO: 替换为实际数据库API调用
        // const result = await api.getAdjustmentHistory(eventId, filters)
        
        // 使用localStorage模拟数据库查询
        const key = `adjustment_history_${eventId}`
        const data = localStorage.getItem(key)
        
        if (data) {
          let history = JSON.parse(data)
          
          // 应用过滤条件
          if (filters.type) {
            history = history.filter(item => item.type === filters.type)
          }
          if (filters.startDate) {
            history = history.filter(item => new Date(item.timestamp) >= new Date(filters.startDate))
          }
          if (filters.endDate) {
            history = history.filter(item => new Date(item.timestamp) <= new Date(filters.endDate))
          }
          
          return history
        }
        
        return []
      } catch (error) {
        this.database.errorLog.push({
          timestamp: new Date(),
          error: error.message,
          operation: 'queryAdjustmentHistory'
        })
        throw error
      }
    },

    /**
     * 保存调整历史记录
     * @param {string} eventId - 重大事项ID
     * @param {Object} historyData - 历史记录数据
     * @returns {Promise<Object>} 保存结果
     */
    async saveAdjustmentHistory(eventId, historyData) {
      try {
        // TODO: 替换为实际数据库API调用
        // const result = await api.saveAdjustmentHistory(eventId, historyData)
        
        // 使用localStorage模拟数据库存储
        const key = `adjustment_history_${eventId}`
        const existingData = localStorage.getItem(key)
        let history = existingData ? JSON.parse(existingData) : []
        
        // 添加新的历史记录
        const record = {
          id: Date.now().toString(),
          timestamp: new Date().toISOString(),
          ...historyData
        }
        
        history.unshift(record) // 添加到开头
        
        // 限制历史记录数量（最多保存100条）
        if (history.length > 100) {
          history = history.slice(0, 100)
        }
        
        localStorage.setItem(key, JSON.stringify(history))
        
        return { success: true, id: record.id, message: '调整历史已保存' }
      } catch (error) {
        this.database.errorLog.push({
          timestamp: new Date(),
          error: error.message,
          operation: 'saveAdjustmentHistory'
        })
        throw error
      }
    },



    /**
     * 保存归档版本
     * @param {string} eventId - 重大事项ID
     * @param {Object} archiveData - 归档数据
     * @returns {Promise<Object>} 保存结果
     */
    async saveArchiveVersion(eventId, archiveData) {
      try {
        // TODO: 替换为实际数据库API调用
        // const result = await api.saveArchiveVersion(eventId, archiveData)
        
        // 使用localStorage模拟数据库存储
        const key = `archive_versions_${eventId}`
        const existingData = localStorage.getItem(key)
        let versions = existingData ? JSON.parse(existingData) : []
        
        // 添加新的归档版本
        const archive = {
          id: Date.now().toString(),
          eventId: eventId,
          archivedAt: new Date().toISOString(),
          ...archiveData
        }
        
        versions.unshift(archive) // 添加到开头
        
        // 限制归档版本数量（最多保存20个版本）
        if (versions.length > 20) {
          versions = versions.slice(0, 20)
        }
        
        localStorage.setItem(key, JSON.stringify(versions))
        
        return { success: true, id: archive.id, version: archive.version, message: '归档版本已保存' }
      } catch (error) {
        this.database.errorLog.push({
          timestamp: new Date(),
          error: error.message,
          operation: 'saveArchiveVersion'
        })
        throw error
      }
    },

    // ===== 复核流程状态机处理方法 =====
    
    /**
     * 更新复核进度
     * @param {Object} progressData - 进度数据
     */
    updateReviewProgress(progressData) {
      if (progressData.stageIndex !== undefined) {
        this.reviewProcess.currentStageIndex = progressData.stageIndex
      }
      
      if (progressData.stageProgress !== undefined) {
        const currentStage = this.reviewProcess.stages[this.reviewProcess.currentStageIndex]
        if (currentStage) {
          currentStage.progress = progressData.stageProgress
        }
      }
      
      if (progressData.overallProgress !== undefined) {
        this.reviewProcess.progress = progressData.overallProgress
      }
    },

    /**
     * 处理需要用户输入的情况
     * @param {Object} inputData - 输入请求数据
     */
    handleUserInputRequired(inputData) {
      this.reviewProcess.status = 'paused'
      this.reviewProcess.userInputRequired = true
      this.reviewProcess.userInputPrompt = inputData.prompt
      
      // 启动超时计时器
      this.startUserInputTimeout(inputData.timeout || this.timeout.defaultDuration)
    },

    /**
     * 处理阶段完成
     * @param {Object} stageData - 阶段数据
     */
    handleStageCompleted(stageData) {
      const stage = this.reviewProcess.stages[stageData.stageIndex]
      if (stage) {
        stage.status = 'completed'
        stage.progress = 100
      }
      
      // 移动到下一阶段
      if (stageData.stageIndex < this.reviewProcess.stages.length - 1) {
        this.reviewProcess.currentStageIndex = stageData.stageIndex + 1
        const nextStage = this.reviewProcess.stages[this.reviewProcess.currentStageIndex]
        if (nextStage) {
          nextStage.status = 'running'
        }
      }
    },

    /**
     * 处理复核完成
     * @param {Object} resultData - 结果数据
     */
    handleReviewCompleted(resultData) {
      this.reviewProcess.status = 'completed'
      this.reviewProcess.isActive = false
      this.reviewProcess.endTime = new Date()
      this.reviewProcess.progress = 100
      
      // 标记所有阶段为完成
      this.reviewProcess.stages.forEach(stage => {
        stage.status = 'completed'
        stage.progress = 100
      })
    },

    /**
     * 处理复核错误
     * @param {Object} errorData - 错误数据
     */
    handleReviewError(errorData) {
      this.reviewProcess.status = 'error'
      this.reviewProcess.errorMessage = errorData.message
      
      // 标记当前阶段为错误
      const currentStage = this.reviewProcess.stages[this.reviewProcess.currentStageIndex]
      if (currentStage) {
        currentStage.status = 'error'
      }
    },

    // ===== 超时处理机制 =====
    
    /**
     * 启动用户输入超时计时器
     * @param {number} duration - 超时时间(毫秒)
     */
    startUserInputTimeout(duration = this.timeout.defaultDuration) {
      const timerId = `user_input_${Date.now()}`
      
      const timer = setTimeout(() => {
        this.handleUserInputTimeout(timerId)
      }, duration)
      
      this.timeout.timers.set(timerId, {
        timer,
        type: 'user_input',
        startTime: Date.now(),
        duration
      })
      
      return timerId
    },

    /**
     * 处理用户输入超时
     * @param {string} timerId - 计时器ID
     */
    handleUserInputTimeout(timerId) {
      const timerInfo = this.timeout.timers.get(timerId)
      if (!timerInfo) return
      
      this.reviewProcess.timeoutCount++
      
      // 记录超时历史
      this.timeout.history.push({
        id: timerId,
        type: 'user_input',
        timestamp: new Date(),
        stage: this.reviewProcess.currentStageIndex,
        count: this.reviewProcess.timeoutCount
      })
      
      // 根据超时策略处理
      if (this.timeout.strategy === 'wait') {
        // 等待继续策略：记录警告，尝试继续
        this.logWarning('timeout', '用户输入超时，系统将继续执行', {
          stage: this.reviewProcess.currentStageIndex,
          timeoutCount: this.reviewProcess.timeoutCount
        })
        
        this.reviewProcess.status = 'analyzing'
        this.reviewProcess.userInputRequired = false
        this.reviewProcess.userInputPrompt = null
        
      } else if (this.timeout.strategy === 'warn_continue') {
        // 警告继续策略：记录超时消息，继续
        this.logWarning('timeout', '用户输入超时，系统已自动继续', {
          stage: this.reviewProcess.currentStageIndex,
          timeoutCount: this.reviewProcess.timeoutCount
        })
        
        this.reviewProcess.status = 'analyzing'
        this.reviewProcess.userInputRequired = false
        this.reviewProcess.userInputPrompt = null
      }
      
      // 检查是否需要暂停自动处理
      if (this.reviewProcess.timeoutCount >= this.reviewProcess.maxTimeouts) {
        this.reviewProcess.status = 'paused'
        this.logWarning('timeout', '超时次数过多，已暂停自动处理，需要用户介入', {
          stage: this.reviewProcess.currentStageIndex,
          timeoutCount: this.reviewProcess.timeoutCount
        })
      }
      
      // 清理计时器
      this.timeout.timers.delete(timerId)
    },

    /**
     * 清除指定计时器
     * @param {string} timerId - 计时器ID
     */
    clearTimeout(timerId) {
      const timerInfo = this.timeout.timers.get(timerId)
      if (timerInfo) {
        clearTimeout(timerInfo.timer)
        this.timeout.timers.delete(timerId)
      }
    },

    /**
     * 记录警告信息
     * @param {string} type - 警告类型
     * @param {string} message - 警告消息
     * @param {Object} context - 上下文信息
     */
    async addWarning(type, message, context = {}) {
      // 统一通过持久化日志入口，避免与内存警告列表重复维护
      try {
        const result = await this.logWarning(type, message, context)
        return result
      } catch (error) {
        // 仍在控制台输出，以便开发时可见
        console.warn(`[${type}] ${message}`, context)
        return { success: false, error: error?.message || String(error) }
      }
    },

    /**
     * 与后端进行聊天（意图识别/内容确认）
     * 收敛 /workspace/chat 调用为 store action
     * @param {string} status 当前复核状态
     * @param {any} content 对话内容（可为字符串或数组）
     * @returns {Promise<Object>} 后端响应数据
     */
    async chat(status, content) {
      try {
        const axios = (await import('axios')).default
        // 在调用后端前记录用户输入（当为纯字符串时）
        if (typeof content === 'string') {
          this.addChatMessage({ role: 'user', type: 'user', content, isvaluable: true })
        }
        // 在 idle 状态下，统一将上下文的可价值消息发送给后端进行意图识别
        let payloadContent = content
        if (status === 'idle') {
          const valuable = (this.chatMessages || [])
            .filter(m => m.isvaluable === true)
            .map(m => ({ type: m.type, content: m.content }))
          payloadContent = valuable
        }
        const response = await axios.post('/workspace/chat', { status, content: payloadContent })
        // /chat：AI消息的展示与组件触发由视图层处理
        return { success: true, data: response.data }
      } catch (error) {
        console.error('聊天接口调用失败:', error)
        throw new Error('聊天接口调用失败，请稍后重试')
      }
    },

    /**
     * 生成或检索复核标准
     * 收敛 /workspace/standards 调用为 store action
     * @param {Object} payload 请求负载，如 { status, type, content }
     * @returns {Promise<Object>} 后端响应数据
     */
  async fetchStandards(payload) {
    try {
      const axios = (await import('axios')).default
      const response = await axios.post('/workspace/standards', payload)
      // 在Store内回填到待更新的 Filecheck 消息
      this.updateStandardForPendingMessage(response.data)
      return { success: true, data: response.data }
    } catch (error) {
      console.error('获取复核标准失败:', error)
      throw new Error('获取复核标准失败，请稍后重试')
    }
  },

    /**
     * 执行复核流程
     * 收敛 /workspace/execute_review 调用为 store action
     * @param {Object} reviewData 复核数据
     * @returns {Promise<Object>} 后端响应数据
     */
    async executeReview(reviewData) {
      try {
        const axios = (await import('axios')).default
        const response = await axios.post('/workspace/execute_review', reviewData)
        const data = response.data
        return { success: true, data }
      } catch (error) {
        console.error('执行复核失败:', error)
        throw new Error('执行复核失败，请稍后重试')
      }
    },

    /**
     * 继续复核流程
     * 调用后端/workspace/continue_review接口，传递用户上传的文件信息或其它响应数据
     * @param {Object} responseData - 符合ResponseData类型要求的数据
     * @returns {Promise<Object>} 后端响应数据
     */
    async continueReview(responseData) {
      try {
        // 调用后端/workspace/continue_review接口
        const axios = (await import('axios')).default;
        const response = await axios.post('/workspace/continue_review', responseData);
        const data = response.data
        return { success: true, data }
      } catch (error) {
        console.error('继续复核流程失败:', error);
        throw new Error('继续复核流程失败，请稍后重试');
      }
    }
  }
})