import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

/**
 * 事件管理状态管理Store
 * - 管理重大事项的CRUD操作
 * - 重大判断功能暂时移除，后续重新设计
 * - 使用localStorage模拟数据库操作
 * - 预留实际数据库API调用位置
 */
export const useEventStore = defineStore('event', () => {
  // 状态管理
  const majorEvents = ref([])
  const majorEventTemplates = ref([])
  const currentEvent = ref(null)
  const loading = ref(false)
  const error = ref('')
  const drafts = ref([])

  // 计算属性
  const eventCount = computed(() => majorEvents.value.length)
  
  // 重大事项加载状态
  const isMajorEventsLoading = computed(() => loading.value)
  
  // 按复核状态分类的计算属性
  const unReviewedEvents = computed(() => 
    majorEvents.value.filter(event => event.status === 'pending')
  )
  const reviewingEvents = computed(() => 
    majorEvents.value.filter(event => event.status === 'reviewing')
  )
  const reviewedEvents = computed(() => 
    majorEvents.value.filter(event => event.status === 'reviewed')
  )
  
  const draftCount = computed(() => drafts.value.length)
  
  // 重大判断相关状态（暂时保留基本结构，功能待重新设计）
  const majorJudgments = ref([])
  const isMajorJudgmentsLoading = computed(() => loading.value)
  const currentMajorJudgment = ref(null)

  // 数据库接口预留方法 - localStorage模拟
  const STORAGE_KEYS = {
    MAJOR_EVENTS: 'majorEvents',
    TEMPLATES: 'majorEventTemplates',
    DRAFTS: 'majorEventDrafts',
    API_CONFIG: 'apiConfig',
    DELETE_LOGS: 'deleteOperationLogs', // 删除操作日志
    USER_PREFERENCES: 'userPreferences' // 用户偏好设置
  }

  /**
   * 初始化数据 - 从localStorage加载
   */
  const initializeData = () => {
    try {
      // 加载重大事项数据
      const storedEvents = localStorage.getItem(STORAGE_KEYS.MAJOR_EVENTS)
      if (storedEvents) {
        majorEvents.value = JSON.parse(storedEvents)
      }

      // 加载模板数据
      const storedTemplates = localStorage.getItem(STORAGE_KEYS.TEMPLATES)
      if (storedTemplates) {
        majorEventTemplates.value = JSON.parse(storedTemplates)
      }

      // 加载草稿数据
      const storedDrafts = localStorage.getItem(STORAGE_KEYS.DRAFTS)
      if (storedDrafts) {
        drafts.value = JSON.parse(storedDrafts)
      }
    } catch (err) {
      console.error('初始化数据失败:', err)
    }
  }

  /**
   * 保存数据到localStorage
   * @param {string} key - 存储键
   * @param {any} data - 要保存的数据
   */
  const saveToStorage = (key, data) => {
    try {
      localStorage.setItem(key, JSON.stringify(data))
    } catch (err) {
      console.error('保存数据失败:', err)
      throw new Error('数据保存失败')
    }
  }

  /**
   * 数据库API预留接口 - 获取重大事项列表
   * TODO: 替换为实际的数据库API调用
   */
  const fetchMajorEvents = async () => {
    loading.value = true
    try {
      // 模拟API延迟
      await new Promise(resolve => setTimeout(resolve, 500))
      
      // TODO: 替换为实际API调用
      // const response = await api.get('/major-events')
      // majorEvents.value = response.data
      
      // 当前使用localStorage模拟
      const storedEvents = localStorage.getItem(STORAGE_KEYS.MAJOR_EVENTS)
      if (storedEvents) {
        majorEvents.value = JSON.parse(storedEvents)
      } else {
        // 初始化示例数据
        majorEvents.value = [
          {
            id: '1',
            title: '重大关联方交易审计',
            description: '审计公司与关联方之间的重大交易事项',
            status: 'pending', // 未复核
            version: '1.0',
            createdAt: '2024-01-15',
            updatedAt: '2024-01-15',
            auditObjectives: '确保关联方交易的公允性和完整性',
            auditEvidenceStandards: {
              situation1: {
                auditConclusion: '关联方交易符合相关法规要求',
                evidenceCategories: [],
                adequacyCriteria: '证据充分且适当'
              }
            }
          },
          {
            id: '2',
            title: '重大投资决策审计',
            description: '对公司重大投资项目的决策过程进行审计',
            status: 'reviewing', // 复核中
            version: '1.0',
            createdAt: '2024-01-16',
            updatedAt: '2024-01-16',
            auditObjectives: '确保投资决策的合理性和风险控制',
            auditEvidenceStandards: {
              situation1: {
                auditConclusion: '投资决策程序符合公司制度要求',
                evidenceCategories: [],
                adequacyCriteria: '证据充分且适当'
              }
            }
          },
          {
            id: '3',
            title: '重大财务报告披露审计',
            description: '对重大财务信息披露的完整性和准确性进行审计',
            status: 'reviewed', // 已复核
            version: '1.0',
            createdAt: '2024-01-14',
            updatedAt: '2024-01-17',
            auditObjectives: '确保财务报告披露的真实性和完整性',
            auditEvidenceStandards: {
              situation1: {
                auditConclusion: '财务报告披露符合相关法规要求',
                evidenceCategories: [],
                adequacyCriteria: '证据充分且适当'
              }
            }
          }
        ]
        saveToStorage(STORAGE_KEYS.MAJOR_EVENTS, majorEvents.value)
      }
    } catch (err) {
      error.value = '获取重大事项失败'
      console.error('Error fetching major events:', err)
    } finally {
      loading.value = false
    }
  }

  /**
   * 数据库API预留接口 - 创建重大事项
   * TODO: 替换为实际的数据库API调用
   * @param {Object} eventData - 重大事项数据
   */
  const createMajorEvent = async (eventData) => {
    loading.value = true
    try {
      // 模拟API延迟
      await new Promise(resolve => setTimeout(resolve, 800))
      
      // 生成新事项数据
      const newEvent = {
        id: generateEventId(),
        ...eventData,
        status: 'pending', // 未复核状态（pending: 未复核, reviewing: 复核中, reviewed: 已复核）
        version: generateVersion(), // 版本号格式：a.0
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
        createdBy: getCurrentUser() // 创建用户信息
      }
      
      // TODO: 替换为实际API调用
      // const response = await api.post('/major-events', newEvent)
      // const savedEvent = response.data
      
      // 当前使用localStorage模拟
      majorEvents.value.push(newEvent)
      saveToStorage(STORAGE_KEYS.MAJOR_EVENTS, majorEvents.value)
      
      return newEvent
    } catch (err) {
      error.value = '创建重大事项失败'
      console.error('Error creating major event:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * 数据库API预留接口 - 更新重大事项
   * TODO: 替换为实际的数据库API调用
   * @param {string} id - 事项ID
   * @param {Object} eventData - 更新数据
   */
  const updateMajorEvent = async (id, eventData) => {
    loading.value = true
    try {
      // 模拟API延迟
      await new Promise(resolve => setTimeout(resolve, 500))
      
      // TODO: 替换为实际API调用
      // const response = await api.put(`/major-events/${id}`, eventData)
      // const updatedEvent = response.data
      
      // 当前使用localStorage模拟
      const index = majorEvents.value.findIndex(event => event.id === id)
      if (index !== -1) {
        majorEvents.value[index] = {
          ...majorEvents.value[index],
          ...eventData,
          updatedAt: new Date().toISOString()
        }
        saveToStorage(STORAGE_KEYS.MAJOR_EVENTS, majorEvents.value)
        return majorEvents.value[index]
      }
      throw new Error('事项不存在')
    } catch (err) {
      error.value = '更新重大事项失败'
      console.error('Error updating major event:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * 数据库API预留接口 - 删除重大事项（完整版本）
   * TODO: 替换为实际的数据库API调用
   * @param {string} id - 事项ID
   * @param {Object} options - 删除选项
   * @param {boolean} options.forceDelete - 是否强制删除（跳过状态检查）
   * @param {string} options.deleteReason - 删除原因
   * @returns {Promise<Object>} 删除结果
   */
  const deleteMajorEvent = async (id, options = {}) => {
    loading.value = true
    
    try {
      // 检查网络连接状态
      if (!isNetworkConnected()) {
        throw new Error('网络连接已断开，请检查网络设置后重试')
      }
      
      // 检查服务器连接状态
      const serverConnected = await checkServerConnection()
      if (!serverConnected) {
        throw new Error('服务器连接失败，请稍后再试')
      }
      
      // 查找要删除的事项
      const eventToDelete = majorEvents.value.find(event => event.id === id)
      if (!eventToDelete) {
        throw new Error('要删除的重大事项不存在')
      }
      
      // 状态检查：如果事项处于"复核中"状态且不是强制删除，则阻止删除
      if (eventToDelete.status === 'reviewing' && !options.forceDelete) {
        throw new Error('REVIEWING_STATUS')
      }
      
      // 模拟API延迟
      await new Promise(resolve => setTimeout(resolve, 500))
      
      // TODO: 替换为实际API调用
      // const response = await api.delete(`/major-events/${id}`, {
      //   data: {
      //     deleteReason: options.deleteReason,
      //     forceDelete: options.forceDelete
      //   }
      // })
      
      // 记录删除操作日志
      const deleteLog = {
        id: generateDeleteLogId(),
        eventId: id,
        eventTitle: eventToDelete.title,
        eventVersion: eventToDelete.version,
        deleteReason: options.deleteReason || '用户主动删除',
        deletedAt: new Date().toISOString(),
        deletedBy: getCurrentUser(),
        originalData: { ...eventToDelete }, // 保存原始数据用于可能的恢复
        operationType: 'DELETE_MAJOR_EVENT'
      }
      
      // 保存删除日志到localStorage
      await saveDeleteLog(deleteLog)
      
      // 从主列表中移除事项
      const index = majorEvents.value.findIndex(event => event.id === id)
      if (index !== -1) {
        majorEvents.value.splice(index, 1)
        saveToStorage(STORAGE_KEYS.MAJOR_EVENTS, majorEvents.value)
      }
      
      // 清理相关的草稿数据（如果存在）
      const relatedDrafts = drafts.value.filter(draft => draft.relatedEventId === id)
      if (relatedDrafts.length > 0) {
        drafts.value = drafts.value.filter(draft => draft.relatedEventId !== id)
        saveToStorage(STORAGE_KEYS.DRAFTS, drafts.value)
      }
      
      return {
        success: true,
        deletedEvent: eventToDelete,
        deleteLog: deleteLog,
        message: '重大事项删除成功'
      }
      
    } catch (err) {
      // 特殊错误处理：复核中状态
      if (err.message === 'REVIEWING_STATUS') {
        throw new Error('该重大事项正在复核中，暂不支持删除操作，建议前往工作台查看实时进度')
      }
      
      // 网络相关错误
      if (err.message.includes('网络') || err.message.includes('服务器')) {
        error.value = err.message
      } else {
        error.value = '删除重大事项失败：' + err.message
      }
      
      console.error('Error deleting major event:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * 数据库API预留接口 - 获取重大事项详情
   * TODO: 替换为实际的数据库API调用
   * @param {string} eventId - 重大事项ID
   * @returns {Promise<Object>} 重大事项详情数据
   */
  const fetchMajorEventDetail = async (eventId) => {
    loading.value = true
    try {
      // 模拟API延迟
      await new Promise(resolve => setTimeout(resolve, 300))
      
      // TODO: 替换为实际API调用
      // const response = await api.get(`/major-events/${eventId}/detail`)
      // return response.data
      
      // 当前使用localStorage模拟
      const storedEvents = localStorage.getItem(STORAGE_KEYS.MAJOR_EVENTS)
      if (storedEvents) {
        const events = JSON.parse(storedEvents)
        const event = events.find(e => e.id === eventId)
        if (event) {
          return event
        }
      }
      throw new Error('重大事项不存在')
    } catch (err) {
      error.value = '获取重大事项详情失败'
      console.error('Error fetching major event detail:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * 数据库API预留接口 - 获取重大事项复核设置
   * TODO: 替换为实际的数据库API调用
   * @param {string} eventId - 重大事项ID
   * @returns {Promise<Object>} 复核设置数据
   */
  const fetchMajorEventReviewSettings = async (eventId) => {
    loading.value = true
    try {
      // 模拟API延迟
      await new Promise(resolve => setTimeout(resolve, 200))
      
      // TODO: 替换为实际API调用
      // const response = await api.get(`/major-events/${eventId}/review-settings`)
      // return response.data
      
      // 当前使用localStorage模拟，从JSON文件结构获取数据
      const reviewSettings = {
        "重大事项概述": "被审计单位所属行业发生重大变化，导致对持续经营能力产生重大不确定性，可能导致收入舞弊风险等。",
        "审计目标": "根据获取的审计证据，就\"被审计单位所属行业发生重大变化\"是否作为\"可能导致对被审计单位持续经营能力产生重大疑虑的事项或情况\"得出结论。",
        "审计证据标准": {
          "情况一": {
            "审计结论": "根据获取的审计证据，认为\"被审计单位所属行业发生重大变化\"应作为\"可能导致对被审计单位持续经营能力产生重大疑虑的事项或情况\"。",
            "审计证据分类与要求": [],
            "充分、适当评判标准": "若审计记录中覆盖\"审计证据与分类\"的所有证据，且均达到设定\"质量要求\"时，则认为审计结论的审计证据充分、适当"
          },
          "情况二": {
            "审计结论": "根据获取的审计证据，没有充分理由认为\"被审计单位所属行业发生重大变化\"是\"可能导致对被审计单位持续经营能力产生重大疑虑的事项或情况\"。",
            "审计证据分类与要求": [],
            "充分、适当评判标准": "若审计记录中覆盖\"审计证据与分类\"的所有证据，且均达到设定\"质量要求\"时，则认为审计结论的审计证据充分、适当"
          }
        }
      }
      
      return reviewSettings
    } catch (err) {
      error.value = '获取复核设置失败'
      console.error('Error fetching review settings:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * 数据库API预留接口 - 获取重大事项复核结果
   * TODO: 替换为实际的数据库API调用
   * @param {string} eventId - 重大事项ID
   * @returns {Promise<Object|null>} 复核结果数据，未复核时返回null
   */
  const fetchMajorEventReviewResults = async (eventId) => {
    loading.value = true
    try {
      // 模拟API延迟
      await new Promise(resolve => setTimeout(resolve, 300))
      
      // TODO: 替换为实际API调用
      // const response = await api.get(`/major-events/${eventId}/review-results`)
      // return response.data
      
      // 当前使用localStorage模拟
      const storedEvents = localStorage.getItem(STORAGE_KEYS.MAJOR_EVENTS)
      if (storedEvents) {
        const events = JSON.parse(storedEvents)
        const event = events.find(e => e.id === eventId)
        
        // 只有已复核状态的事项才有复核结果
        if (event && event.status === 'reviewed') {
          return {
            "审计结论": "根据获取的审计证据，认为\"被审计单位所属行业发生重大变化\"应作为\"可能导致对被审计单位持续经营能力产生重大疑虑的事项或情况\"。",
            "复核时间": "2024-01-17 14:30:00",
            "复核结果明细": {
              "统计整理": "共获取审计证据15项，其中达标证据12项，未达标证据3项",
              "结论与原因": "基于充分适当的审计证据，确认行业重大变化对持续经营能力构成重大疑虑"
            },
            "复核人员": "张审计师",
            "复核状态": "已完成"
          }
        }
      }
      
      // 未复核或复核中状态返回null
      return null
    } catch (err) {
      error.value = '获取复核结果失败'
      console.error('Error fetching review results:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * 数据库API预留接口 - 获取重大事项模板
   * TODO: 替换为实际的数据库API调用
   */
  const fetchMajorEventTemplates = async () => {
    loading.value = true
    try {
      // 模拟API延迟
      await new Promise(resolve => setTimeout(resolve, 300))
      
      // TODO: 替换为实际API调用
      // const response = await api.get('/major-event-templates')
      // majorEventTemplates.value = response.data
      
      // 当前使用localStorage模拟
      const storedTemplates = localStorage.getItem(STORAGE_KEYS.TEMPLATES)
      if (storedTemplates) {
        majorEventTemplates.value = JSON.parse(storedTemplates)
      } else {
        // 初始化示例模板
        majorEventTemplates.value = [
          {
            id: '1',
            name: '关联方交易模板',
            description: '适用于关联方交易相关的重大事项审计',
            createdAt: '2024-01-10',
            template: {
              title: '关联方交易审计',
              auditObjectives: '确保关联方交易的公允性、完整性和合规性'
            }
          }
        ]
        saveToStorage(STORAGE_KEYS.TEMPLATES, majorEventTemplates.value)
      }
    } catch (err) {
      error.value = '获取模板失败'
      console.error('Error fetching templates:', err)
    } finally {
      loading.value = false
    }
  }

  /**
   * 数据库API预留接口 - 保存草稿
   * TODO: 替换为实际的数据库API调用
   * @param {Object} draftData - 草稿数据
   */
  const saveMajorEventDraft = async (draftData) => {
    try {
      // 模拟API延迟
      await new Promise(resolve => setTimeout(resolve, 300))
      
      const draft = {
        id: generateDraftId(),
        ...draftData,
        isDraft: true,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString()
      }
      
      // TODO: 替换为实际API调用
      // const response = await api.post('/major-event-drafts', draft)
      
      // 当前使用localStorage模拟
      drafts.value.push(draft)
      saveToStorage(STORAGE_KEYS.DRAFTS, drafts.value)
      
      return draft
    } catch (err) {
      console.error('Error saving draft:', err)
      throw new Error('保存草稿失败')
    }
  }

  /**
   * 数据库API预留接口 - 验证重大事项内容
   * TODO: 替换为实际的验证服务API调用
   * @param {Object} eventData - 事项数据
   */
  const validateMajorEvent = async (eventData) => {
    try {
      // 模拟API延迟
      await new Promise(resolve => setTimeout(resolve, 200))
      
      // TODO: 替换为实际验证API调用
      // const response = await api.post('/validate-major-event', eventData)
      // return response.data
      
      // 当前使用简单验证逻辑模拟
      const errors = []
      
      if (!eventData.title || eventData.title.trim().length < 10) {
        errors.push('重大事项概述内容过于简单，建议补充详细信息')
      }
      
      return {
        isValid: errors.length === 0,
        errors
      }
    } catch (err) {
      console.error('Error validating major event:', err)
      throw new Error('验证失败')
    }
  }

  /**
   * 数据库API预留接口 - 检查审计依据符合性
   * TODO: 替换为实际的智能检查API调用
   * @param {Object} eventData - 事项数据
   */
  const checkAuditComplianceAsync = async (eventData) => {
    try {
      // 模拟API延迟
      await new Promise(resolve => setTimeout(resolve, 1000))
      
      // TODO: 替换为实际智能检查API调用
      // 需要先向特定系统模块获取API密钥
      // const apiKey = await getAuditComplianceApiKey()
      // const response = await api.post('/check-audit-compliance', eventData, {
      //   headers: { 'X-API-Key': apiKey }
      // })
      // return response.data
      
      // 当前使用模拟检查逻辑
      const warnings = []
      
      // 模拟智能检查结果
      if (eventData.title && eventData.title.includes('关联方')) {
        // 模拟检查通过
        console.log('审计依据符合性检查通过')
      }
      
      return {
        isCompliant: true,
        warnings
      }
    } catch (err) {
      console.error('Error checking audit compliance:', err)
      throw new Error('审计依据检查失败')
    }
  }

  // 重大判断相关方法（暂时保留基本结构，功能待重新设计）
  const fetchMajorJudgments = async () => {
    // 功能待重新设计
    console.log('重大判断功能开发中')
  }
  
  const addMajorJudgment = async (judgmentData) => {
    // 功能待重新设计
    console.log('重大判断功能开发中')
  }
  
  const updateMajorJudgment = async (id, judgmentData) => {
    // 功能待重新设计
    console.log('重大判断功能开发中')
  }
  
  const deleteMajorJudgment = async (id) => {
    // 功能待重新设计
    console.log('重大判断功能开发中')
  }
  
  const setCurrentMajorJudgment = (judgment) => {
    currentMajorJudgment.value = judgment
  }
  
  const getMajorJudgments = computed(() => majorJudgments.value)

  // 辅助方法
  const getMajorEventById = (id) => {
    return majorEvents.value.find(event => event.id === id)
  }

  const setCurrentEvent = (event) => {
    currentEvent.value = event
  }

  const clearError = () => {
    error.value = ''
  }

  /**
   * 网络状态检测
   * @returns {boolean} 网络是否连接
   */
  const isNetworkConnected = () => {
    return navigator.onLine
  }

  /**
   * 检查服务器连接状态
   * TODO: 替换为实际的服务器健康检查API
   * @returns {Promise<boolean>} 服务器是否可达
   */
  const checkServerConnection = async () => {
    try {
      // 模拟服务器连接检查
      await new Promise(resolve => setTimeout(resolve, 100))
      
      // TODO: 替换为实际的健康检查API调用
      // const response = await fetch('/api/health', { method: 'HEAD' })
      // return response.ok
      
      // 当前模拟：随机返回连接状态（90%成功率）
      return Math.random() > 0.1
    } catch (err) {
      console.error('服务器连接检查失败:', err)
      return false
    }
  }

  /**
   * 重新加载数据（带错误处理）
   */
  const reloadMajorEvents = async () => {
    clearError()
    
    // 检查网络连接
    if (!isNetworkConnected()) {
      error.value = '网络连接已断开，请检查网络设置后重试'
      return
    }
    
    // 检查服务器连接
    const serverConnected = await checkServerConnection()
    if (!serverConnected) {
      error.value = '服务器连接失败，请稍后再试'
      return
    }
    
    // 重新获取数据
    await fetchMajorEvents()
  }

  /**
   * 生成事项唯一标识符
   * @returns {string} 事项ID
   */
  const generateEventId = () => {
    return 'ME_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9)
  }

  /**
   * 生成版本号（格式：a.0，其中a为正整数）
   * @returns {string} 版本号
   */
  const generateVersion = () => {
    const existingVersions = majorEvents.value
      .map(event => event.version)
      .filter(version => version && version.endsWith('.0'))
      .map(version => parseInt(version.split('.')[0]))
      .filter(num => !isNaN(num))
    
    const maxVersion = existingVersions.length > 0 ? Math.max(...existingVersions) : 0
    return `${maxVersion + 1}.0`
  }

  /**
   * 生成草稿ID
   * @returns {string} 草稿ID
   */
  const generateDraftId = () => {
    return 'DRAFT_' + Date.now() + '_' + Math.random().toString(36).substr(2, 6)
  }

  /**
   * 获取当前用户信息
   * TODO: 从认证store获取实际用户信息
   * @returns {string} 用户ID
   */
  const getCurrentUser = () => {
    // TODO: 从认证系统获取当前用户
    // return authStore.currentUser.id
    return 'user_' + Date.now()
  }

  /**
   * 生成删除日志唯一标识符
   * @returns {string} 删除日志ID
   */
  const generateDeleteLogId = () => {
    return 'DEL_LOG_' + Date.now() + '_' + Math.random().toString(36).substr(2, 8)
  }

  /**
   * 保存删除操作日志到localStorage
   * TODO: 替换为实际的日志服务API调用
   * @param {Object} deleteLog - 删除日志对象
   */
  const saveDeleteLog = async (deleteLog) => {
    try {
      // 获取现有的删除日志
      const existingLogs = localStorage.getItem(STORAGE_KEYS.DELETE_LOGS)
      const logs = existingLogs ? JSON.parse(existingLogs) : []
      
      // 添加新的删除日志
      logs.push(deleteLog)
      
      // 保持最近100条删除日志（避免localStorage过大）
      if (logs.length > 100) {
        logs.splice(0, logs.length - 100)
      }
      
      // 保存到localStorage
      localStorage.setItem(STORAGE_KEYS.DELETE_LOGS, JSON.stringify(logs))
      
      // TODO: 替换为实际的日志服务API调用
      // await api.post('/operation-logs', deleteLog)
      
      console.log('删除操作日志已保存:', deleteLog)
    } catch (err) {
      console.error('保存删除日志失败:', err)
      // 日志保存失败不应该影响删除操作的成功
    }
  }

  /**
   * 检查用户是否首次执行删除操作
   * @returns {boolean} 是否首次删除
   */
  const isFirstTimeDelete = () => {
    try {
      const userPrefs = localStorage.getItem(STORAGE_KEYS.USER_PREFERENCES)
      const preferences = userPrefs ? JSON.parse(userPrefs) : {}
      return !preferences.hasDeletedBefore
    } catch (err) {
      console.error('检查用户偏好失败:', err)
      return true // 默认认为是首次删除
    }
  }

  /**
   * 标记用户已执行过删除操作
   */
  const markUserHasDeleted = () => {
    try {
      const userPrefs = localStorage.getItem(STORAGE_KEYS.USER_PREFERENCES)
      const preferences = userPrefs ? JSON.parse(userPrefs) : {}
      preferences.hasDeletedBefore = true
      preferences.firstDeleteTime = new Date().toISOString()
      localStorage.setItem(STORAGE_KEYS.USER_PREFERENCES, JSON.stringify(preferences))
    } catch (err) {
      console.error('更新用户偏好失败:', err)
    }
  }

  /**
   * 获取删除操作日志
   * @param {number} limit - 返回的日志数量限制
   * @returns {Array} 删除日志数组
   */
  const getDeleteLogs = (limit = 50) => {
    try {
      const logs = localStorage.getItem(STORAGE_KEYS.DELETE_LOGS)
      const allLogs = logs ? JSON.parse(logs) : []
      return allLogs.slice(-limit).reverse() // 返回最新的日志
    } catch (err) {
      console.error('获取删除日志失败:', err)
      return []
    }
  }

  return {
    // 状态
    majorEvents,
    majorEventTemplates,
    currentEvent,
    loading,
    error,
    drafts,
    majorJudgments,
    currentMajorJudgment,
    
    // 计算属性
    eventCount,
    isMajorEventsLoading,
    unReviewedEvents,
    reviewingEvents,
    reviewedEvents,
    draftCount,
    isMajorJudgmentsLoading,
    getMajorJudgments,
    
    // 数据库接口方法
    initializeData,
    fetchMajorEvents,
    fetchMajorEventDetail,
    fetchMajorEventReviewSettings,
    fetchMajorEventReviewResults,
    createMajorEvent,
    updateMajorEvent,
    deleteMajorEvent,
    fetchMajorEventTemplates,
    saveMajorEventDraft,
    validateMajorEvent,
    checkAuditComplianceAsync,
    
    // 重大判断方法（暂时保留接口）
    fetchMajorJudgments,
    addMajorJudgment,
    updateMajorJudgment,
    deleteMajorJudgment,
    setCurrentMajorJudgment,
    
    // 辅助方法
    getMajorEventById,
    setCurrentEvent,
    clearError,
    isNetworkConnected,
    checkServerConnection,
    reloadMajorEvents,
    
    // 删除相关方法
    generateDeleteLogId,
    saveDeleteLog,
    isFirstTimeDelete,
    markUserHasDeleted,
    getDeleteLogs
  }
})