<template>
  <!-- 默认复核设置组件 - 用于配置智能体交互超时处理策略 -->
  <div class="default-review-settings">
    <!-- 模块头部 - 显示标题、状态和操作按钮 -->
    <div class="module-header">
      <div class="module-icon">⚙️</div>
      <h3>默认复核设置</h3>
      <div class="module-status" :class="status">{{ statusText }}</div>
      <button class="close-btn" @click="closeModule" title="关闭">
        ✕
      </button>
    </div>
    
    <!-- 设置向导提示 - 首次访问时显示的引导信息 -->
    <div v-if="showWizard" class="wizard-banner">
      <div class="wizard-icon">💡</div>
      <div class="wizard-content">
        <h4>设置向导</h4>
        <p>欢迎使用默认复核设置！请配置智能体交互超时处理策略，这些设置将应用于该项目的所有复核流程。</p>
        <button class="wizard-close" @click="closeWizard">我知道了</button>
      </div>
    </div>
    
    <!-- 主要内容区域 -->
    <div class="module-content">
      
      <!-- 智能体交互超时处理策略设置区域 - 配置超时时间和处理方式 -->
      <div class="settings-section">
        <h4 class="section-title">
          智能体交互超时处理策略
          <span class="section-description">设置智能体在各种场景下的超时处理方式</span>
        </h4>
        <div class="settings-form">
          <!-- 超时时间设置 - 用户可选择5秒到永不超时的不同选项 -->
          <div class="form-group">
            <label>
              超时时间设置
              <span class="field-description">设置智能体等待响应的最大时间</span>
            </label>
            <select v-model="settings.timeout.duration" class="form-control">
              <option value="5">5秒</option>
              <option value="10">10秒</option>
              <option value="20">20秒（推荐）</option>
              <option value="30">30秒</option>
              <option value="0">永不超时</option>
            </select>
          </div>
          
          <!-- 超时处理方式 - 等待继续或记录超时信息并继续 -->
          <div class="form-group">
            <label>
              超时处理方式
              <span class="field-description">选择超时后的处理策略</span>
            </label>
            <div class="radio-group">
              <label class="radio-item">
                <input type="radio" v-model="settings.timeout.action" value="wait" />
                等待继续（推荐）
                <span class="option-description">超时后继续等待用户操作</span>
              </label>
              <label class="radio-item">
                <input type="radio" v-model="settings.timeout.action" value="warn_continue" />
                记录"超时信息"并继续
                <span class="option-description">记录超时信息并自动继续流程</span>
              </label>
            </div>
          </div>
          
          <!-- 适用场景配置 - 选择超时处理策略的具体应用场景 -->
          <div class="form-group">
            <label>
              适用场景配置
              <span class="field-description">选择超时处理策略的适用场景</span>
            </label>
            <div class="checkbox-group">
              <label class="checkbox-item">
                <input type="checkbox" v-model="settings.timeout.scenarios.documentTransfer" />
                底稿传输超时
                <span class="scenario-description">文档上传或传输过程中的超时处理</span>
              </label>
              <label class="checkbox-item">
                <input type="checkbox" v-model="settings.timeout.scenarios.infoRetrieval" />
                超时回溯分析处理
                <span class="scenario-description">复核过程中超时情况的回溯分析处理</span>
              </label>
              <label class="checkbox-item">
                <input type="checkbox" v-model="settings.timeout.scenarios.analysisUncertain" />
                复核分析不确定时的处理
                <span class="scenario-description">分析结果不明确时的处理策略</span>
              </label>
            </div>
          </div>
          
          <!-- 防死循环保护机制 - 防止同一超时处理重复执行的保护设置 -->
          <div class="form-group protection-settings">
            <label>
              防死循环保护机制
              <span class="field-description">防止同一超时处理重复执行的保护设置</span>
            </label>
            <div class="protection-config">
              <div class="config-item">
                <label>最大重试次数</label>
                <select v-model="settings.timeout.protection.maxRetries" class="form-control small">
                  <option value="3">3次（推荐）</option>
                  <option value="5">5次</option>
                  <option value="10">10次</option>
                </select>
              </div>
              <div class="config-item">
                <label>强制暂停阈值</label>
                <select v-model="settings.timeout.protection.pauseThreshold" class="form-control small">
                  <option value="4">第4次自动暂停（推荐）</option>
                  <option value="6">第6次自动暂停</option>
                  <option value="10">第10次自动暂停</option>
                </select>
              </div>
            </div>
            <div class="protection-note">
              <span class="note-icon">⚠️</span>
              当同一类型超时处理重复发生时，系统将自动暂停并要求用户介入
            </div>
          </div>
        </div>
      </div>
      
      <!-- 设置预览和影响说明区域 - 显示当前配置摘要和影响说明 -->
      <div class="settings-section preview-section">
        <h4 class="section-title">设置预览</h4>
        <div class="preview-content">
          <div class="preview-item">
            <strong>当前配置摘要：</strong>
            <ul>
              <li>超时时间：{{ getTimeoutDurationText() }}</li>
              <li>超时处理：{{ getTimeoutActionText() }}</li>
              <li>适用场景：{{ getApplicableScenariosText() }}</li>
              <li>保护机制：最多重试{{ settings.timeout.protection.maxRetries }}次，第{{ settings.timeout.protection.pauseThreshold }}次自动暂停</li>
            </ul>
          </div>
          <div class="preview-item impact-note">
            <span class="impact-icon">📋</span>
            <strong>影响说明：</strong>这些设置将应用于该项目后续的所有复核流程，确保智能体交互的稳定性和可靠性。
          </div>
        </div>
      </div>
      
      <!-- 操作按钮区域 - 提供保存、重置、导入导出、日志查看等功能操作 -->
      <div class="action-buttons">
        <button class="btn btn-outline" @click="showHistory" title="查看设置变更历史">
          📋 查看历史
        </button>
        <button class="btn btn-outline" @click="exportSettings" title="导出设置配置">
          📤 导出配置
        </button>
        <button class="btn btn-outline" @click="importSettings" title="导入设置配置">
          📥 导入配置
        </button>
        <button class="btn btn-outline" @click="viewWarningLogs" title="查看超时和错误处理日志">
          📊 警告日志
        </button>
        <button class="btn btn-outline" @click="resetTimeoutCounter" title="重置超时计数器">
          🔄 重置计数器
        </button>
        <button class="btn btn-outline" @click="testTimeoutProtection" title="测试超时保护机制">
          🧪 测试保护
        </button>
        <button class="btn btn-secondary" @click="resetSettings">恢复默认</button>
        <button class="btn btn-primary" @click="saveSettings" :disabled="!isValidSettings">
          {{ isSaving ? '保存中...' : '保存设置' }}
        </button>
      </div>
      
      <!-- 验证错误提示区域 - 显示配置验证失败的错误信息 -->
      <div v-if="validationErrors.length > 0" class="validation-errors">
        <div class="error-header">
          <span class="error-icon">⚠️</span>
          <strong>配置验证失败</strong>
        </div>
        <ul class="error-list">
          <li v-for="error in validationErrors" :key="error.field" class="error-item">
            {{ error.message }}
          </li>
        </ul>
      </div>
    </div>
    
    <!-- 设置历史记录弹窗 - 显示设置变更历史和恢复功能 -->
    <div v-if="showHistoryModal" class="modal-overlay" @click="closeHistoryModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h4>设置变更历史</h4>
          <button class="modal-close" @click="closeHistoryModal">✕</button>
        </div>
        <div class="modal-body">
          <div v-if="settingsHistory.length === 0" class="empty-history">
            暂无设置变更记录
          </div>
          <div v-else class="history-list">
            <div v-for="record in settingsHistory" :key="record.id" class="history-item">
              <div class="history-time">{{ formatTime(record.timestamp) }}</div>
              <div class="history-changes">{{ record.description }}</div>
              <button class="btn btn-small" @click="restoreSettings(record.settings)">
                恢复此配置
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
// 导入Vue 3组合式API和工作区状态管理
import { ref, computed, onMounted, watch } from 'vue'
import { useWorkspaceStore } from '@/stores/workspace'

// 默认复核设置组件 - 用于配置智能体的默认复核参数和行为策略
export default {
  name: 'DefaultReviewSettings',
  props: {
    status: {
      type: String,
      default: 'pending' // pending, active, completed
    }
  },
  emits: ['settings-updated', 'module-completed', 'close'],
  setup(props, { emit }) {
    const workspaceStore = useWorkspaceStore()
    
    // ==================== 响应式数据定义 ====================
    const showWizard = ref(true) // 首次访问显示向导
    const showHistoryModal = ref(false) // 历史记录弹窗显示状态
    const isSaving = ref(false) // 保存状态标识
    const validationErrors = ref([]) // 验证错误列表
    const settingsHistory = ref([]) // 设置变更历史记录
    
    // 完整的设置配置对象 - 专注于智能体交互超时处理策略
    const settings = ref({
      // 智能体交互超时处理策略
      timeout: {
        duration: '20', // 超时时间（秒）
        action: 'wait', // 超时处理方式：wait | warn_continue
        scenarios: {
          documentTransfer: true, // 底稿传输超时
          infoRetrieval: true, // 超时回溯分析处理
          analysisUncertain: true // 复核分析不确定时的处理
        },
        protection: {
          maxRetries: '3', // 最大重试次数
          pauseThreshold: '4' // 强制暂停阈值
        }
      }
    })
    
    // ==================== 计算属性 ====================
    
    // 状态文本映射
    const statusText = computed(() => {
      const statusMap = {
        'pending': '待配置',
        'active': '配置中',
        'completed': '已完成'
      }
      return statusMap[props.status] || '未知状态'
    })
    
    // 验证设置的有效性 - 检查是否有验证错误
    const isValidSettings = computed(() => {
      return validationErrors.value.length === 0
    })
    
    // ==================== 验证函数 ====================
    
    // 设置验证函数 - 验证超时处理策略配置的有效性
    const validateSettings = () => {
      const errors = []
      
      // 验证超时场景至少选择一项
      const scenariosSelected = Object.values(settings.value.timeout.scenarios).some(v => v)
      if (!scenariosSelected) {
        errors.push({
          field: 'timeout.scenarios',
          message: '请至少选择一个超时处理适用场景'
        })
      }
      
      // 检查设置冲突
      if (settings.value.timeout.action === 'warn_continue' && 
          parseInt(settings.value.timeout.protection.maxRetries) > 10) {
        errors.push({
          field: 'timeout.protection',
          message: '当选择"记录超时信息并继续"时，建议最大重试次数不超过10次'
        })
      }
      
      validationErrors.value = errors
      return errors.length === 0
    }
    
    // ==================== 文本获取函数 ====================
    
    // 获取超时时间文本显示
    const getTimeoutDurationText = () => {
      return settings.value.timeout.duration === '0' ? '永不超时' : `${settings.value.timeout.duration}秒`
    }
    
    // 获取超时处理方式文本显示
    const getTimeoutActionText = () => {
      return settings.value.timeout.action === 'wait' ? '等待继续' : '记录超时信息并继续'
    }
    
    // 获取适用场景文本显示
    const getApplicableScenariosText = () => {
      const scenarios = []
      if (settings.value.timeout.scenarios.documentTransfer) scenarios.push('底稿传输超时')
      if (settings.value.timeout.scenarios.infoRetrieval) scenarios.push('超时回溯分析')
      if (settings.value.timeout.scenarios.analysisUncertain) scenarios.push('复核分析不确定')
      return scenarios.length > 0 ? scenarios.join('、') : '未选择场景'
    }
    
    // 格式化时间戳为本地时间字符串
    const formatTime = (timestamp) => {
      return new Date(timestamp).toLocaleString('zh-CN')
    }
    
    // ==================== 核心操作函数 ====================
    
    // 保存设置 - 验证并保存配置到数据库
    const saveSettings = async () => {
      if (!validateSettings()) {
        return
      }
      
      isSaving.value = true
      
      try {
        // 构建设置数据
        const settingsData = {
          ...settings.value,
          timestamp: new Date().toISOString()
        }
        
        console.log('保存设置:', settingsData)
        
        // 调用数据库保存接口
        await workspaceStore.saveDefaultReviewSettings(settingsData)
        
        // 检查是否有正在执行的复核流程
        const hasActiveReview = checkActiveReviewProcess()
        
        if (hasActiveReview) {
          alert('当前有复核流程正在执行，新设置将在后续流程中生效')
        }
        
        // 记录设置变更历史
        addToHistory('保存默认复核设置', settings.value)
        
        // 发送设置更新事件
        emit('settings-updated', settingsData)
        emit('module-completed', 'default-review-settings')
        
        alert('默认复核设置已更新')
        
      } catch (error) {
        console.error('保存设置失败:', error)
        alert('保存设置失败，请检查网络连接或稍后再试')
      } finally {
        isSaving.value = false
      }
    }
    
    // 检查是否有活跃的复核流程 - 用于判断设置变更的影响范围
    const checkActiveReviewProcess = () => {
      // 检查workspace store中的复核流程状态
      return workspaceStore.reviewProcess.status === 'running'
    }
    
    // ==================== 防死循环保护机制 ====================
    
    // 重置超时计数器 - 清除所有超时处理历史记录
    const resetTimeoutCounter = async () => {
      if (confirm('确定要重置超时计数器吗？这将清除所有超时处理历史记录。')) {
        try {
          await workspaceStore.resetTimeoutCounter()
          
          // 记录重置操作到历史
          addToHistory('重置超时计数器', settings.value)
          
          // 记录警告日志
          await workspaceStore.logWarning({
            type: 'counter_reset',
            message: '用户手动重置超时计数器',
            details: '清除所有超时处理历史记录',
            timestamp: new Date().toISOString()
          })
          
          alert('超时计数器已重置，所有超时处理历史记录已清除。')
          
        } catch (error) {
          console.error('重置超时计数器失败:', error)
          alert('重置失败，请稍后再试。')
        }
      }
    }
    
    // 查看警告日志 - 显示超时和错误处理日志
    const viewWarningLogs = async () => {
      try {
        const logs = await workspaceStore.getWarningLogs({
          limit: 50,
          offset: 0,
          types: ['timeout', 'error', 'protection', 'counter_reset']
        })
        
        if (logs.length === 0) {
          alert('暂无警告日志记录。')
          return
        }
        
        // 格式化日志信息显示
        const logMessages = logs.map(log => 
          `[${formatTime(log.timestamp)}] ${log.type.toUpperCase()}: ${log.message}${log.details ? ' - ' + log.details : ''}`
        ).join('\n\n')
        
        // 显示日志内容（实际项目中可以用更好的弹窗组件）
        alert(`最近50条警告日志：\n\n${logMessages}`)
        
      } catch (error) {
        console.error('获取警告日志失败:', error)
        alert('获取日志失败，请稍后再试。')
      }
    }
    
    // 测试超时保护机制 - 模拟超时场景用于测试
    const testTimeoutProtection = async () => {
      if (!confirm('这将模拟超时场景来测试保护机制，确定继续吗？')) {
        return
      }
      
      try {
        // 模拟连续超时处理
        for (let i = 1; i <= 5; i++) {
          await workspaceStore.logWarning({
            type: 'timeout',
            message: `模拟超时测试 - 第${i}次`,
            details: `场景：超时回溯分析，处理方式：${settings.value.timeout.action}`,
            timestamp: new Date().toISOString(),
            scenario: 'infoRetrieval',
            taskId: 'test_task_' + Date.now()
          })
          
          // 检查是否触发保护机制
          if (i >= parseInt(settings.value.timeout.protection.pauseThreshold)) {
            await workspaceStore.logWarning({
              type: 'protection',
              message: '触发防死循环保护机制',
              details: `连续超时${i}次，自动暂停处理`,
              timestamp: new Date().toISOString()
            })
            break
          }
        }
        
        alert('超时保护机制测试完成，请查看警告日志了解详情。')
        
      } catch (error) {
        console.error('测试超时保护机制失败:', error)
        alert('测试失败，请稍后再试。')
      }
    }
    
    // 重置设置到默认值 - 恢复所有配置项到初始状态
    const resetSettings = () => {
      if (confirm('确定要恢复默认设置吗？当前的修改将会丢失。')) {
        settings.value = {
          timeout: {
            duration: '20',
            action: 'wait',
            scenarios: {
              documentTransfer: true,
              infoRetrieval: true,
              analysisUncertain: true
            },
            protection: {
              maxRetries: '3',
              pauseThreshold: '4'
            }
          }
        }
        
        validationErrors.value = []
        addToHistory('恢复默认设置', settings.value)
      }
    }
    
    // ==================== 界面操作函数 ====================
    
    // 关闭模块 - 触发关闭事件
    const closeModule = () => {
      emit('close')
    }
    
    // 关闭向导 - 隐藏首次访问提示并记录状态
    const closeWizard = () => {
      showWizard.value = false
      // 记录用户已查看过向导
      localStorage.setItem('reviewSettingsWizardSeen', 'true')
    }
    
    // 显示历史记录弹窗
    const showHistory = () => {
      showHistoryModal.value = true
    }
    
    // 关闭历史记录弹窗
    const closeHistoryModal = () => {
      showHistoryModal.value = false
    }
    
    // ==================== 历史记录管理 ====================
    
    // 添加到历史记录 - 记录设置变更历史
    const addToHistory = (description, settingsData) => {
      const record = {
        id: Date.now(),
        timestamp: new Date(),
        description,
        settings: JSON.parse(JSON.stringify(settingsData))
      }
      
      settingsHistory.value.unshift(record)
      
      // 只保留最近20条记录
      if (settingsHistory.value.length > 20) {
        settingsHistory.value = settingsHistory.value.slice(0, 20)
      }
      
      // 保存到本地存储
      localStorage.setItem('reviewSettingsHistory', JSON.stringify(settingsHistory.value))
    }
    
    // 恢复历史设置 - 从历史记录中恢复指定配置
    const restoreSettings = (historicalSettings) => {
      if (confirm('确定要恢复到此配置吗？当前的修改将会丢失。')) {
        settings.value = JSON.parse(JSON.stringify(historicalSettings))
        addToHistory('恢复历史配置', settings.value)
        closeHistoryModal()
      }
    }
    
    // ==================== 导入导出功能 ====================
    
    // 导出设置配置 - 将当前配置导出为JSON文件
    const exportSettings = () => {
      try {
        const configData = {
          version: '1.0',
          timestamp: new Date().toISOString(),
          settings: settings.value
        }
        
        const dataStr = JSON.stringify(configData, null, 2)
        const dataBlob = new Blob([dataStr], { type: 'application/json' })
        
        const link = document.createElement('a')
        link.href = URL.createObjectURL(dataBlob)
        link.download = `复核设置配置_${new Date().toISOString().split('T')[0]}.json`
        link.click()
        
        URL.revokeObjectURL(link.href)
        
      } catch (error) {
        console.error('导出配置失败:', error)
        alert('导出配置失败，请稍后再试')
      }
    }
    
    // 导入设置配置 - 从JSON文件导入配置
    const importSettings = () => {
      const input = document.createElement('input')
      input.type = 'file'
      input.accept = '.json'
      
      input.onchange = (event) => {
        const file = event.target.files[0]
        if (!file) return
        
        const reader = new FileReader()
        reader.onload = (e) => {
          try {
            const configData = JSON.parse(e.target.result)
            
            if (configData.settings) {
              settings.value = { ...settings.value, ...configData.settings }
              addToHistory('导入配置文件', settings.value)
              alert('配置导入成功')
            } else {
              alert('配置文件格式不正确')
            }
          } catch (error) {
            console.error('导入配置失败:', error)
            alert('配置文件解析失败，请检查文件格式')
          }
        }
        
        reader.readAsText(file)
      }
      
      input.click()
    }
    
    // ==================== 监听器和生命周期 ====================
    
    // 监听设置变化进行实时验证 - 深度监听配置对象变化
    watch(settings, () => {
      validateSettings()
    }, { deep: true })
    
    // 组件挂载时初始化 - 加载保存的设置和历史记录
    onMounted(async () => {
      try {
        // 从数据库加载设置
        const savedSettings = await workspaceStore.loadDefaultReviewSettings()
        if (savedSettings) {
          // 恢复保存的设置
          Object.assign(settings.value, savedSettings)
          console.log('已加载保存的设置:', savedSettings)
        }
      } catch (error) {
        console.error('加载设置失败:', error)
      }
      
      // 检查是否已查看过向导
      const wizardSeen = localStorage.getItem('reviewSettingsWizardSeen')
      if (wizardSeen) {
        showWizard.value = false
      }
      
      // 加载历史记录
      const savedHistory = localStorage.getItem('reviewSettingsHistory')
      if (savedHistory) {
        try {
          settingsHistory.value = JSON.parse(savedHistory)
        } catch (error) {
          console.error('加载历史记录失败:', error)
        }
      }
      
      // 初始验证
      validateSettings()
    })
    
    // ==================== 返回组件接口 ====================
    
    return {
      // 响应式数据
      settings,
      showWizard,
      showHistoryModal,
      isSaving,
      validationErrors,
      settingsHistory,
      
      // 计算属性
      statusText,
      isValidSettings,
      
      // 核心操作方法
      saveSettings,
      resetSettings,
      closeModule,
      closeWizard,
      
      // 界面交互方法
      showHistory,
      closeHistoryModal,
      restoreSettings,
      exportSettings,
      importSettings,
      
      // 防死循环保护机制方法
      resetTimeoutCounter,
      viewWarningLogs,
      testTimeoutProtection,
      
      // 文本获取方法
      getTimeoutDurationText,
      getTimeoutActionText,
      getApplicableScenariosText,
      formatTime
    }
  }
}
</script>

<style scoped>
.default-review-settings {
  background: white;
  border-radius: 12px;
  border: 1px solid #e9ecef;
  margin-bottom: 16px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  max-height: 90vh;
  overflow-y: auto;
}

/* 模块头部样式 */
.module-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 20px 24px;
  border-bottom: 1px solid #e9ecef;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 12px 12px 0 0;
  position: relative;
}

.module-icon {
  font-size: 24px;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  backdrop-filter: blur(10px);
}

.module-header h3 {
  flex: 1;
  margin: 0;
  font-size: 18px;
  font-weight: 600;
}

.module-status {
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
  background: rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(10px);
}

.close-btn {
  position: absolute;
  right: 20px;
  top: 50%;
  transform: translateY(-50%);
  background: rgba(255, 255, 255, 0.2);
  border: none;
  font-size: 20px;
  color: white;
  cursor: pointer;
  padding: 8px;
  border-radius: 8px;
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
}

.close-btn:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: translateY(-50%) scale(1.1);
}

/* 设置向导样式 */
.wizard-banner {
  background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
  padding: 20px 24px;
  display: flex;
  align-items: center;
  gap: 16px;
  border-bottom: 1px solid #e9ecef;
}

.wizard-icon {
  font-size: 32px;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.1); }
}

.wizard-content {
  flex: 1;
}

.wizard-content h4 {
  margin: 0 0 8px 0;
  font-size: 16px;
  font-weight: 600;
  color: #8b4513;
}

.wizard-content p {
  margin: 0 0 12px 0;
  color: #8b4513;
  line-height: 1.5;
}

.wizard-close {
  background: #8b4513;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.3s ease;
}

.wizard-close:hover {
  background: #a0522d;
  transform: translateY(-1px);
}

/* 模块内容样式 */
.module-content {
  padding: 24px;
}

/* 设置区域样式 */
.settings-section {
  margin-bottom: 32px;
  border: 1px solid #f0f0f0;
  border-radius: 8px;
  overflow: hidden;
}

.section-title {
  background: #f8f9fa;
  padding: 16px 20px;
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #333;
  border-bottom: 1px solid #e9ecef;
  display: flex;
  align-items: center;
  gap: 8px;
}

.section-description {
  font-size: 12px;
  font-weight: 400;
  color: #6c757d;
  margin-left: auto;
}

.settings-form {
  padding: 20px;
}

/* 表单组件样式 */
.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 600;
  color: #333;
  font-size: 14px;
}

.field-description {
  display: block;
  font-size: 12px;
  font-weight: 400;
  color: #6c757d;
  margin-top: 2px;
}

.form-control {
  width: 100%;
  padding: 10px 14px;
  border: 2px solid #e9ecef;
  border-radius: 6px;
  font-size: 14px;
  transition: all 0.3s ease;
  background: white;
}

.form-control:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.form-control.small {
  width: auto;
  min-width: 120px;
}

/* 复选框和单选框样式 */
.checkbox-group, .radio-group {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.checkbox-item, .radio-item {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  font-weight: normal;
  cursor: pointer;
  padding: 8px;
  border-radius: 6px;
  transition: all 0.3s ease;
}

.checkbox-item:hover, .radio-item:hover {
  background: #f8f9ff;
}

.checkbox-item input[type="checkbox"],
.radio-item input[type="radio"] {
  margin: 2px 0 0 0;
  transform: scale(1.2);
}

.option-description, .scenario-description {
  display: block;
  font-size: 12px;
  color: #6c757d;
  margin-top: 2px;
  line-height: 1.4;
}

/* 保护设置样式 */
.protection-settings {
  background: #fff8e1;
  border: 1px solid #ffcc02;
  border-radius: 8px;
  padding: 16px;
}

.protection-config {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  margin-bottom: 12px;
}

.config-item label {
  font-size: 12px;
  margin-bottom: 4px;
}

.protection-note {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: #f57c00;
  background: rgba(255, 193, 7, 0.1);
  padding: 8px 12px;
  border-radius: 6px;
}

.note-icon {
  font-size: 14px;
}

/* 预览区域样式 */
.preview-section {
  background: #f8f9ff;
  border-color: #667eea;
}

.preview-content {
  padding: 16px 20px;
}

.preview-item {
  margin-bottom: 16px;
}

.preview-item:last-child {
  margin-bottom: 0;
}

.preview-item ul {
  margin: 8px 0 0 20px;
  padding: 0;
}

.preview-item li {
  margin-bottom: 4px;
  color: #555;
}

.impact-note {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  background: rgba(102, 126, 234, 0.1);
  padding: 12px;
  border-radius: 6px;
  border-left: 4px solid #667eea;
}

.impact-icon {
  font-size: 16px;
  margin-top: 2px;
}

/* 按钮样式 */
.action-buttons {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  flex-wrap: wrap;
  margin-top: 24px;
  padding-top: 20px;
  border-top: 1px solid #e9ecef;
}

.btn {
  padding: 10px 20px;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 6px;
  min-width: 100px;
  justify-content: center;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none !important;
}

.btn-outline {
  background: white;
  color: #667eea;
  border: 2px solid #667eea;
}

.btn-outline:hover:not(:disabled) {
  background: #667eea;
  color: white;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.btn-secondary {
  background: #6c757d;
  color: white;
}

.btn-secondary:hover:not(:disabled) {
  background: #5a6268;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(108, 117, 125, 0.3);
}

.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
}

.btn-small {
  padding: 6px 12px;
  font-size: 12px;
  min-width: auto;
}

/* 验证错误样式 */
.validation-errors {
  background: #fff5f5;
  border: 1px solid #fed7d7;
  border-radius: 8px;
  padding: 16px;
  margin-top: 20px;
}

.error-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
  color: #c53030;
  font-weight: 600;
}

.error-icon {
  font-size: 18px;
}

.error-list {
  margin: 0;
  padding: 0 0 0 20px;
}

.error-item {
  color: #c53030;
  margin-bottom: 6px;
  line-height: 1.4;
}

/* 弹窗样式 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
  backdrop-filter: blur(4px);
}

.modal-content {
  background: white;
  border-radius: 12px;
  width: 90%;
  max-width: 600px;
  max-height: 80vh;
  overflow: hidden;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  animation: modalSlideIn 0.3s ease;
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

.modal-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 20px 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.modal-header h4 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
}

.modal-close {
  background: rgba(255, 255, 255, 0.2);
  border: none;
  color: white;
  font-size: 20px;
  cursor: pointer;
  padding: 8px;
  border-radius: 6px;
  transition: all 0.3s ease;
}

.modal-close:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: scale(1.1);
}

.modal-body {
  padding: 24px;
  max-height: 60vh;
  overflow-y: auto;
}

/* 历史记录样式 */
.empty-history {
  text-align: center;
  color: #6c757d;
  padding: 40px 20px;
  font-style: italic;
}

.history-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.history-item {
  background: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 8px;
  padding: 16px;
  transition: all 0.3s ease;
}

.history-item:hover {
  background: #f0f0f0;
  border-color: #667eea;
}

.history-time {
  font-size: 12px;
  color: #6c757d;
  margin-bottom: 4px;
}

.history-changes {
  font-weight: 500;
  color: #333;
  margin-bottom: 8px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .default-review-settings {
    margin: 8px;
    border-radius: 8px;
  }
  
  .module-header {
    padding: 16px 20px;
    border-radius: 8px 8px 0 0;
  }
  
  .module-content {
    padding: 16px;
  }
  
  .settings-form {
    padding: 16px;
  }
  
  .protection-config {
    grid-template-columns: 1fr;
  }
  
  .action-buttons {
    flex-direction: column;
  }
  
  .btn {
    width: 100%;
  }
  
  .modal-content {
    width: 95%;
    margin: 20px;
  }
  
  .modal-header {
    padding: 16px 20px;
  }
  
  .modal-body {
    padding: 20px;
  }
}

@media (max-width: 480px) {
  .wizard-banner {
    flex-direction: column;
    text-align: center;
  }
  
  .section-title {
    flex-direction: column;
    align-items: flex-start;
    gap: 4px;
  }
  
  .section-description {
    margin-left: 0;
  }
}
</style>