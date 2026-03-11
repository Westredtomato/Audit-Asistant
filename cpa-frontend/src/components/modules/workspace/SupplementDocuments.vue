<template>
  <!-- 补充底稿模块 - 智能体驱动的文件补充和管理系统 -->
  <div class="supplement-documents">
    <!-- 模块头部 - 显示当前状态和操作按钮 -->
    <div class="module-header">
      <div class="module-icon">📄</div>
      <h3>补充底稿</h3>
      <div class="header-actions">
        <!-- 智能体请求测试按钮 -->
        <button 
          class="btn-icon" 
          @click="startAgentRequest" 
          :disabled="isAgentRequesting || isUploading"
          title="启动智能体文件请求（测试）"
        >
          🤖
        </button>
        <button 
          class="btn-icon" 
          @click="resetSession" 
          :disabled="isUploading"
          title="重置会话统计（管理员）"
        >
          🔄
        </button>
        <button 
          class="btn-icon" 
          @click="unblockRequests" 
          :disabled="isUploading || !workspaceStore?.fileRequest?.isBlocked"
          title="解除阻止状态（管理员）"
        >
          🔓
        </button>
        <!-- 刷新文件列表按钮 -->
        <button 
          class="btn-icon" 
          @click="refreshFileList" 
          :disabled="isRefreshing"
          title="刷新文件列表">
          {{ isRefreshing ? '🔄' : '🔄' }}
        </button>
        <!-- 批量清空按钮 -->
        <button 
          class="btn-icon btn-danger" 
          @click="batchClearFiles" 
          :disabled="isUploading || allFiles.length === 0"
          title="清空所有文件">
          🗑️
        </button>
      </div>
      <!-- 模块状态指示器 -->
      <div class="module-status" :class="moduleStatus">{{ statusText }}</div>
      <button class="close-btn" @click="closeModule">✕</button>
    </div>

    <div class="module-content">
      <!-- 智能体状态面板 -->
      <div v-if="workspaceStore?.agent?.status !== 'ready' || workspaceStore?.fileRequest?.isBlocked" class="agent-status-panel">
        <div class="status-header">
           <span class="status-icon" :class="getAgentStatusIconClass(workspaceStore?.agent?.status)">{{ getAgentStatusIcon(workspaceStore?.agent?.status) }}</span>
          <div class="status-info">
            <h4>智能体状态: {{ getAgentStatusText(workspaceStore?.agent?.status) }}</h4>
            <p v-if="workspaceStore?.agent?.currentTask" class="status-message">{{ workspaceStore?.agent?.currentTask }}</p>
            <div class="status-stats">
              <span>请求次数: {{ workspaceStore?.fileRequest?.requestCount || 0 }}/{{ workspaceStore?.fileRequest?.maxRequestCount || 0 }}</span>
        <span>错误次数: {{ workspaceStore?.fileRequest?.errorCount || 0 }}/{{ workspaceStore?.fileRequest?.maxErrorCount || 0 }}</span>
              <span v-if="workspaceStore?.agent?.recoveryAttempts > 0">恢复尝试: {{ workspaceStore?.agent?.recoveryAttempts || 0 }}/{{ workspaceStore?.agent?.maxRecoveryAttempts || 0 }}</span>
            </div>
          </div>
        </div>
        
        <!-- 阻止状态警告 -->
        <div v-if="workspaceStore?.fileRequest?.isBlocked" class="block-warning">
          <span class="warning-icon">⚠️</span>
          <span class="warning-text">文件请求已被阻止: {{ workspaceStore?.fileRequest?.blockReason || '未知原因' }}</span>
        </div>
      </div>

      <!-- 智能体文件请求横幅 - 当智能体需要特定文件时显示 -->
      <div v-if="isAgentRequesting" class="agent-request-banner">
        <div class="request-header">
          <div class="request-icon">🤖</div>
          <h4>智能体文件请求</h4>
          <div class="request-status">{{ agentRequestInfo.status }}</div>
        </div>
        
        <!-- 需要手动提供的文件（不显示具体类型列表） -->
        <div>
          <p class="request-message">{{ agentRequestInfo.message }}</p>
          <p class="request-hint">请上传或选择合适的文件，智能体将自动识别并继续复核</p>
          
          <!-- 超时倒计时显示和跳过按钮 -->
          <div class="request-footer">
            <div v-if="timeoutCountdown > 0" class="timeout-countdown">
              <span class="countdown-icon">⏰</span>
              <span class="countdown-text">超时处理倒计时：{{ timeoutCountdown }}秒</span>
              <div class="countdown-bar">
                <div class="countdown-fill" :style="{ width: (timeoutCountdown / defaultTimeout) * 100 + '%' }"></div>
              </div>
            </div>
            <button 
              class="btn-skip" 
              @click="skipFileRequest"
              title="跳过文件请求">
              跳过请求
            </button>
          </div>
        </div>
      </div>

      <!-- 文件上传区域 -->
      <div 
        class="upload-area" 
        :class="{ 
          'drag-over': isDragOver, 
          'agent-requesting': isAgentRequesting
        }"
        @click="triggerFileInput"
        @drop="handleDrop"
        @dragover="handleDragOver"
        @dragleave="handleDragLeave">
        <div class="upload-icon">{{ isAgentRequesting ? '🤖📄' : '📁' }}</div>
        <p class="upload-text">
          {{ isAgentRequesting ? '智能体正在等待文件' : '点击或拖拽上传底稿文件' }}
        </p>
        <p class="upload-hint">
          {{ isAgentRequesting ? 
            '智能体正在等待文件，支持 PDF、Word、Excel 等格式' : 
            '支持 PDF、Word、Excel 等格式，单个文件最大 50MB' 
          }}
        </p>
        <input 
          ref="fileInput" 
          type="file" 
          multiple 
          accept=".pdf,.doc,.docx,.xls,.xlsx,.txt,.png,.jpg,.jpeg"
          style="display: none"
          @change="handleFileSelect">
      </div>

      <!-- 上传进度条 -->
      <div v-if="isUploading" class="upload-progress">
        <div class="progress-bar">
          <div class="progress-fill" :style="{ width: uploadProgress + '%' }"></div>
        </div>
        <p class="progress-text">上传进度：{{ uploadProgress }}%</p>
      </div>

      <!-- 错误信息显示 -->
      <div v-if="uploadErrors.length > 0" class="upload-errors">
        <h4>上传错误</h4>
        <div v-for="error in uploadErrors" :key="error.fileName" class="error-item">
          <span class="error-file">{{ error.fileName }}:</span>
          <span class="error-message">{{ error.error }}</span>
        </div>
      </div>

      <!-- 文件列表 -->
      <div v-if="allFiles.length > 0" class="file-list">
        <div class="list-header">
          <h4>文件列表 ({{ allFiles.length }})</h4>
          <div class="list-actions">
            <button 
              class="btn-small" 
              @click="loadServerFiles" 
              :disabled="isRefreshing"
              title="刷新列表">
              刷新
            </button>
            <button 
              class="btn-small btn-danger" 
              @click="clearFiles" 
              :disabled="isUploading || uploadedFiles.length === 0"
              title="清空待上传文件">
              清空
            </button>
          </div>
        </div>
        
        <!-- 文件项列表 -->
        <div 
          v-for="file in filteredFiles" 
          :key="file.id" 
          class="file-item" 
          :class="{
            'uploading': file.status === 'uploading',
            'completed': file.status === 'completed' || file.status === 'server',
            'error': file.status === 'error',
            'agent-selected': isFileSelectedByAgent(file)
          }">
          <div class="file-info">
            <div class="file-icon">{{ getFileIcon(file.name) }}</div>
            <div class="file-details">
              <div class="file-name">
                {{ file.name }}
                <span v-if="isFileSelectedByAgent(file)" class="agent-badge">智能体已选择</span>
              </div>
              <div class="file-meta">
                {{ formatFileSize(file.size) }} • {{ getFileTypeFromName(file.name) }} • {{ file.uploadTime }}
              </div>
              <div class="file-status">
                <span class="status-icon">{{ getStatusIcon(file.status) }}</span>
                <span :class="'status-' + file.status">{{ getStatusText(file.status) }}</span>
              </div>
              <!-- 上传进度条 -->
              <div v-if="file.status === 'uploading'" class="file-progress">
                <div class="progress-bar-small">
                  <div class="progress-fill-small" :style="{ width: file.progress + '%' }"></div>
                </div>
              </div>
            </div>
          </div>
          
          <!-- 文件操作按钮 -->
          <div class="file-actions">
            <!-- 智能体选择按钮 -->
            <button 
              v-if="canSelectForAgent(file)" 
              class="btn-icon btn-agent" 
              @click="selectFileForAgent(file, agentRequestInfo.pendingRequestId)"
              title="提供给智能体">
              🤖
            </button>
            <!-- 预览按钮 -->
            <button 
              class="btn-icon" 
              @click="previewFile(file)" 
              :disabled="file.status !== 'completed' && file.status !== 'server'"
              title="预览文件">
              👁️
            </button>
            <!-- 下载按钮 -->
            <button 
              class="btn-icon" 
              @click="downloadFile(file)" 
              :disabled="file.status !== 'completed' && file.status !== 'server'"
              title="下载文件">
              💾
            </button>
            <!-- 删除按钮 -->
            <button 
              class="btn-icon btn-danger" 
              @click="removeFile(file.id)" 
              :disabled="file.status === 'uploading'"
              title="删除文件">
              🗑️
            </button>
          </div>
        </div>
      </div>

      <!-- 底部操作按钮 -->
      <div class="action-buttons">
        <button 
          class="btn btn-secondary" 
          @click="clearFiles" 
          :disabled="isUploading || uploadedFiles.length === 0">
          清空文件
        </button>
        <button 
          class="btn btn-primary" 
          @click="confirmUpload" 
          :disabled="isUploading || uploadedFiles.filter(f => f.status === 'pending').length === 0">
          {{ isUploading ? '上传中...' : '确认上传' }}
        </button>
        <button 
          v-if="uploadErrors.length > 0" 
          class="btn btn-success" 
          @click="retryFailedUploads" 
          :disabled="isUploading">
          重试失败
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, watch } from 'vue'
import { useDocumentStore } from '@/stores/document'
import { useWorkspaceStore } from '@/stores/workspace'
import fileManager from '@/utils/fileManager'

export default {
  name: 'SupplementDocuments',
  emits: ['close', 'module-completed', 'files-uploaded', 'supplement-completed'],
  
  setup(props, { emit }) {
    // ===== 响应式数据定义 =====
    const fileInput = ref(null)
    const uploadedFiles = ref([]) // 本地待上传/已上传文件列表
    const serverFiles = ref([])   // 服务器已存在文件列表
    const isDragOver = ref(false)
    const isUploading = ref(false)
    const isRefreshing = ref(false)
    const uploadProgress = ref(0)
    const uploadErrors = ref([])
    
    // 智能体文件请求相关状态
    const isAgentRequesting = ref(false)
    const requestedFileTypes = ref([])
    const timeoutCountdown = ref(0)
    const defaultTimeout = ref(20) // 默认超时时间（秒）
    const timeoutTimer = ref(null)
    
    // 从默认设置中获取超时配置
    const getTimeoutDuration = () => {
      if (!defaultSettings.value?.settings?.timeout) return 20
      const duration = parseInt(defaultSettings.value.settings.timeout.duration)
      return duration === 0 ? 0 : duration // 0表示永不超时
    }
    
    // 从默认设置中获取超时处理方式
    const getTimeoutAction = () => {
      return defaultSettings.value?.settings?.timeout?.action || 'wait'
    }
    
    // 检查是否启用特定场景的超时处理
    const isTimeoutScenarioEnabled = (scenario) => {
      return defaultSettings.value?.settings?.timeout?.scenarios?.[scenario] || false
    }
    
    // 获取数据存储实例
    const documentStore = useDocumentStore()
    const workspaceStore = useWorkspaceStore()
    
    // ===== 默认复核设置相关 =====
    const defaultSettings = ref(null) // 存储从DefaultReviewSettings读取的配置
    const settingsLoaded = ref(false) // 设置是否已加载完成
    
    // ===== 计算属性 =====
    // 模块当前状态
    const moduleStatus = computed(() => {
      if (isAgentRequesting.value) return 'active'
      if (isUploading.value) return 'active'
      if (uploadErrors.value.length > 0) return 'error'
      if (allFiles.value.some(f => f.status === 'completed')) return 'completed'
      return 'pending'
    })
    
    // 状态文本描述
    const statusText = computed(() => {
      if (isAgentRequesting.value) return '智能体请求中'
      if (isUploading.value) return '上传中'
      if (uploadErrors.value.length > 0) return '上传错误'
      if (allFiles.value.some(f => f.status === 'completed')) return '已完成'
      return '等待上传'
    })
    
    // 合并所有文件列表
    const allFiles = computed(() => {
      return [...uploadedFiles.value, ...serverFiles.value]
    })
    
    // 过滤后的文件列表（用于显示）
    const filteredFiles = computed(() => {
      return allFiles.value.sort((a, b) => {
        // 智能体选中的文件排在前面
        const aSelected = isFileSelectedByAgent(a)
        const bSelected = isFileSelectedByAgent(b)
        if (aSelected && !bSelected) return -1
        if (!aSelected && bSelected) return 1
        
        // 按状态排序：uploading > pending > completed > error
        const statusOrder = { uploading: 0, pending: 1, completed: 2, server: 2, error: 3 }
        return statusOrder[a.status] - statusOrder[b.status]
      })
    })
    
    // 智能体请求信息
    const agentRequestInfo = computed(() => {
      if (!workspaceStore?.fileRequest?.isRequesting) {
        return {
          status: '无请求',
          message: '',
          pendingRequestId: null
        }
      }
      
      const request = workspaceStore.fileRequest
      const pending = request?.requestedFiles?.filter(f => f.status === 'pending') || []
      
      return {
        status: pending.length > 0 ? '等待文件' : '已满足',
        message: pending.length > 0 ? 
          `智能体需要以下类型的文件来继续复核流程：` : 
          '所有请求的文件已提供',
        pendingRequestId: pending[0]?.id || null
      }
    })
    
    // ===== 文件处理方法 =====
    const triggerFileInput = () => {
      fileInput.value?.click()
    }
    
    const handleFileSelect = (event) => {
      const files = Array.from(event.target.files)
      processFiles(files)
      event.target.value = '' // 清空input，允许重复选择同一文件
    }
    
    const handleDrop = (event) => {
      event.preventDefault()
      isDragOver.value = false
      const files = Array.from(event.dataTransfer.files)
      processFiles(files)
    }
    
    const handleDragOver = (event) => {
      event.preventDefault()
      isDragOver.value = true
    }
    
    const handleDragLeave = () => {
      isDragOver.value = false
    }
    
    // 处理文件列表，验证并添加到待上传队列
    const processFiles = (files) => {
      const validFiles = []
      const invalidFiles = []
      
      files.forEach(file => {
        if (fileManager.validateFileType(file) && fileManager.validateFileSize(file)) {
          validFiles.push(file)
        } else {
          invalidFiles.push(file)
        }
      })
      
      // 添加有效文件到待上传列表
      validFiles.forEach(file => {
        const fileObj = {
          id: Date.now() + Math.random(),
          name: file.name,
          size: file.size,
          type: file.type,
          uploadTime: new Date().toLocaleString(),
          file: file,
          status: 'pending', // pending, uploading, completed, error
          progress: 0,
          serverId: null,
          url: null
        }
        uploadedFiles.value.push(fileObj)
      })
      
      // 显示无效文件错误
      if (invalidFiles.length > 0) {
        const errorMsg = `${invalidFiles.length}个文件不符合要求：\n${invalidFiles.map(f => `${f.name} - ${!fileManager.validateFileType(f) ? '格式不支持' : '文件过大'}`).join('\n')}`
        alert(errorMsg)
      }
      
      // 如果智能体正在请求文件，自动开始上传
      if (isAgentRequesting.value && validFiles.length > 0) {
        setTimeout(() => {
          confirmUpload()
        }, 500)
      }
    }
    
    // ===== 文件操作方法 =====
    const getFileIcon = (fileName) => {
      return fileManager.getFileIcon(fileName)
    }
    
    const formatFileSize = (bytes) => {
      return fileManager.formatFileSize(bytes)
    }
    
    const getFileTypeFromName = (fileName) => {
      const ext = fileName.split('.').pop()?.toLowerCase()
      const typeMap = {
        'pdf': '审计报告',
        'doc': '工作底稿',
        'docx': '工作底稿',
        'xls': '财务数据',
        'xlsx': '财务数据'
      }
      return typeMap[ext] || '其他文档'
    }
    
    const getStatusIcon = (status) => {
      const iconMap = {
        pending: '⏳',
        uploading: '⬆️',
        completed: '✅',
        server: '☁️',
        error: '❌'
      }
      return iconMap[status] || '❓'
    }
    
    const getStatusText = (status) => {
      const textMap = {
        pending: '等待上传',
        uploading: '上传中',
        completed: '已完成',
        server: '服务器文件',
        error: '上传失败'
      }
      return textMap[status] || '未知状态'
    }
    
    // ===== 智能体交互方法 =====
    // 选择文件提供给智能体
    const selectFileForAgent = (file, requestedFileId) => {
      if (!file || !requestedFileId) return
      
      // 通知workspace store文件已提供
      workspaceStore.provideRequestedFile(requestedFileId, {
        id: file.serverId || file.id,
        name: file.name,
        type: getFileTypeFromName(file.name),
        url: file.url,
        size: file.size
      })
      
      // 检查是否所有文件都已提供
      checkSupplementCompletion()
    }
    
    // 检查文件是否被智能体选择
    const isFileSelectedByAgent = (file) => {
      if (!workspaceStore?.fileRequest?.isRequesting) return false
      
      return workspaceStore?.fileRequest?.requestedFiles?.some(rf => 
        rf.status === 'provided' && rf.fileInfo && 
        (rf.fileInfo.id === file.id || rf.fileInfo.id === file.serverId)
      )
    }
    
    // 检查文件是否可以被智能体选择
    const canSelectForAgent = (file) => {
      if (!isAgentRequesting.value || file.status === 'uploading') return false
      
      const fileType = getFileTypeFromName(file.name)
      return requestedFileTypes.value.includes(fileType)
    }
    
    // 检查补充是否完成
    const checkSupplementCompletion = () => {
      if (!workspaceStore?.fileRequest?.isRequesting) return
      
      const pendingFiles = workspaceStore?.fileRequest?.requestedFiles?.filter(f => f.status === 'pending') || []
      if (pendingFiles.length === 0) {
        // 所有文件都已提供，完成补充
        emit('supplement-completed', {
          providedFiles: workspaceStore?.fileRequest?.requestedFiles?.filter(f => f.status === 'provided') || [],
          message: '已完成文件补充，谢谢您的帮助！'
        })
        
        // 重置请求状态
        isAgentRequesting.value = false
        requestedFileTypes.value = []
        clearTimeout(timeoutTimer.value)
        timeoutCountdown.value = 0
      }
    }
    
    // ===== 超时处理方法 =====
    // 开始超时倒计时
    const startTimeoutCountdown = async () => {
      const timeoutDuration = getTimeoutDuration()
      
      // 如果设置为永不超时，则不启动计时器
      if (timeoutDuration === 0) {
        timeoutCountdown.value = 0
        return
      }
      
      timeoutCountdown.value = timeoutDuration
      
      timeoutTimer.value = setInterval(() => {
        timeoutCountdown.value--
        if (timeoutCountdown.value <= 0) {
          handleTimeout()
        }
      }, 1000)
    }
    
    // 处理超时
    const handleTimeout = async () => {
      clearTimeout(timeoutTimer.value)
      timeoutCountdown.value = 0
      
      const timeoutAction = getTimeoutAction()
      const timeoutDuration = getTimeoutDuration()
      
      // 记录超时日志到workspace store
      await workspaceStore.logWarning('timeout', '智能体文件请求超时', {
        requestedFiles: agentRequestInfo.value?.files || [],
        timeoutDuration: timeoutDuration,
        timeoutAction: timeoutAction,
        scenario: 'documentTransfer'
      })
      
      // 根据默认设置中的超时处理策略执行相应操作
      if (timeoutAction === 'wait') {
        // 等待继续策略
        console.log('超时处理：继续等待用户操作')
      } else if (timeoutAction === 'warn_continue') {
        // 记录超时信息并继续策略
        emit('supplement-completed', {
          providedFiles: [],
          message: '请求超时，系统已记录超时信息并将继续流程',
          timeout: true
        })
      } else {
        // 默认跳过
        workspaceStore.skipFileRequest('超时处理策略未定义')
        emit('supplement-completed', {
          providedFiles: [],
          message: '超时未响应，已跳过文件请求继续流程',
          timeout: true
        })
      }
    }
    
    // ===== 文件上传方法 =====
    const confirmUpload = async () => {
      const pendingFiles = uploadedFiles.value.filter(file => file.status === 'pending')
      if (pendingFiles.length === 0) return

      isUploading.value = true
      uploadProgress.value = 0
      uploadErrors.value = []

      try {
        // 设置store上传状态
        documentStore.setUploading(true)
        documentStore.clearErrors()

        // 不再调用后端 /files/upload，直接使用原始 File 对象完成后续流程
        const results = pendingFiles.map(fileObj => {
          // 标记为完成并更新进度
          fileObj.progress = 100
          fileObj.status = 'completed'

          // 构造与先前一致的结果结构（但不包含服务器URL）
          const f = fileObj.file
          const localId = `local-${Date.now()}-${Math.random().toString(16).slice(2)}`
          return {
            success: true,
            originalFile: f,
            file: {
              id: localId,
              name: f.name,
              originalName: f.name,
              size: f.size,
              type: f.type,
              url: '',
              uploadTime: new Date().toISOString()
            },
            error: null
          }
        })

        // 触发上传完成事件，交由父组件继续复核并调用 /workspace/continue_review
        emit('files-uploaded', results)


        // 不在组件内直接关闭模块，等待父组件确认复核继续成功后再关闭

      } catch (error) {
        console.error('上传文件失败:', error)
        documentStore.setUploadError(error.message || '上传文件过程中发生错误')
        uploadErrors.value.push({
          fileName: '文件处理',
          error: error.message
        })
      } finally {
        isUploading.value = false
        documentStore.setUploading(false)
      }
    }
    
    
    
    // ===== 智能体状态显示方法 =====
    const getAgentStatusIcon = (status) => {
      const iconMap = {
        'ready': '✅',
        'working': '⚙️',
        'requesting': '🤖',
        'error': '❌',
        'blocked': '🚫',
        'recovering': '🔄'
      }
      return iconMap[status] || '❓'
    }
    
    const getAgentStatusIconClass = (status) => {
      return `status-${status}`
    }
    
    const getAgentStatusText = (status) => {
      const textMap = {
        'ready': '就绪',
        'working': '工作中',
        'requesting': '请求文件',
        'error': '错误',
        'blocked': '已阻止',
        'recovering': '恢复中'
      }
      return textMap[status] || '未知状态'
    }
    
    // ===== 其他操作方法 =====
    const previewFile = (file) => {
      if (file.url) {
        window.open(file.url, '_blank')
      } else {
        console.log('预览文件:', file.name)
        alert('文件预览功能开发中')
      }
    }
    
    const downloadFile = (file) => {
      if (file.serverId && file.name) {
        fileManager.downloadFile(file.serverId, file.name)
      } else {
        alert('文件下载失败：文件信息不完整')
      }
    }
    
    const retryFailedUploads = async () => {
      const failedFiles = uploadedFiles.value.filter(file => file.status === 'error')
      if (failedFiles.length === 0) return
      
      // 重置失败文件状态
      failedFiles.forEach(file => {
        file.status = 'pending'
        file.progress = 0
      })
      
      // 清空错误列表
      uploadErrors.value = []
      
      // 重新上传
      await confirmUpload()
    }
    
    const removeFile = async (fileId) => {
      // 先在本地上传文件中查找
      let file = uploadedFiles.value.find(f => f.id === fileId)
      let isServerFile = false
      
      // 如果在本地文件中没找到，在服务器文件中查找
      if (!file) {
        file = serverFiles.value.find(f => f.id === fileId)
        isServerFile = true
      }
      
      if (!file) {
        console.error('文件未找到:', fileId)
        return
      }
      
      // 如果是服务器文件或已上传的文件，需要删除服务器文件
      if ((file.serverId && file.status === 'completed') || isServerFile) {
        try {
          const serverFileId = file.serverId || file.id
          await documentStore.deleteFile(serverFileId, true)
        } catch (error) {
          console.error('删除服务器文件失败:', error)
          alert('删除文件失败: ' + error.message)
          return
        }
      }
      
      // 从相应的列表中移除
      if (isServerFile) {
        serverFiles.value = serverFiles.value.filter(f => f.id !== fileId)
      } else {
        uploadedFiles.value = uploadedFiles.value.filter(f => f.id !== fileId)
      }
    }
    
    const clearFiles = async () => {
      // 删除所有已上传的文件
      const uploadedServerFiles = uploadedFiles.value.filter(file => 
        file.serverId && file.status === 'completed'
      )
      
      for (const file of uploadedServerFiles) {
        try {
          await documentStore.deleteFile(file.serverId, true)
        } catch (error) {
          console.error('删除服务器文件失败:', error)
        }
      }
      
      // 清空本地列表
      uploadedFiles.value = []
      uploadErrors.value = []
    }
    
    // 加载服务器文件列表
    const loadServerFiles = async () => {
      try {
        isRefreshing.value = true
        const files = await documentStore.fetchUploadedFiles()
        // 确保 files 是数组
        const fileArray = Array.isArray(files) ? files : []
        serverFiles.value = fileArray.map(file => ({
          ...file,
          status: 'server', // 标记为服务器文件
          uploadTime: file.uploadTime || new Date(file.createdAt || Date.now()).toLocaleString()
        }))
      } catch (error) {
        console.error('加载文件列表失败:', error)
        uploadErrors.value.push({
          fileName: '文件列表',
          error: '加载失败: ' + error.message
        })
      } finally {
        isRefreshing.value = false
      }
    }
    
    // 刷新文件列表
    const refreshFileList = async () => {
      await loadServerFiles()
    }
    
    // 批量清空所有文件
    const batchClearFiles = async () => {
      if (!confirm('确定要清空所有文件吗？此操作不可恢复。')) {
        return
      }
      
      try {
        isUploading.value = true
        
        // 删除所有服务器文件
        const allServerFiles = [...serverFiles.value, ...uploadedFiles.value.filter(f => f.serverId)]
        
        for (const file of allServerFiles) {
          try {
            const fileId = file.serverId || file.id
            if (fileId) {
              await documentStore.deleteFile(fileId, true)
            }
          } catch (error) {
            console.error('删除文件失败:', file.name, error)
          }
        }
        
        // 清空本地列表
        uploadedFiles.value = []
        serverFiles.value = []
        uploadErrors.value = []
        
        // 重新加载文件列表
        await loadServerFiles()
        
      } catch (error) {
        console.error('批量清空失败:', error)
        uploadErrors.value.push({
          fileName: '批量清空',
          error: error.message
        })
      } finally {
        isUploading.value = false
      }
    }
    
    const closeModule = () => {
      // 清理定时器
      if (timeoutTimer.value) {
        clearTimeout(timeoutTimer.value)
      }
      emit('close')
    }
    
    // ===== 加载默认复核设置 =====
    const loadDefaultSettings = async () => {
      try {
        console.log('正在加载默认复核设置...')
        const response = await workspaceStore.loadDefaultReviewSettings()
        
        if (response.success && response.data) {
          defaultSettings.value = response.data
          console.log('默认复核设置加载成功:', defaultSettings.value)
          
          // 应用设置到当前组件
          applyDefaultSettings()
        } else {
          console.warn('未找到默认复核设置，使用默认配置')
          defaultSettings.value = workspaceStore.getDefaultReviewSettingsTemplate()
        }
      } catch (error) {
        console.error('加载默认复核设置失败:', error)
        // 使用默认模板作为后备
        defaultSettings.value = workspaceStore.getDefaultReviewSettingsTemplate()
      } finally {
        settingsLoaded.value = true
      }
    }
    
    // 应用默认设置到当前组件
    const applyDefaultSettings = () => {
      if (!defaultSettings.value?.settings) return
      
      const settings = defaultSettings.value.settings
      
      // 应用超时设置
      if (settings.timeout) {
        console.log('应用超时设置:', {
          duration: settings.timeout.duration,
          action: settings.timeout.action,
          scenarios: settings.timeout.scenarios
        })
        
        // 如果当前有智能体请求且启用了相应场景的超时处理，重新启动超时计时
        if (isAgentRequesting.value && isTimeoutScenarioEnabled('documentTransfer')) {
          startTimeoutCountdown()
        }
      }
    }
    
    // ===== 智能体请求模拟方法 =====
    // 启动智能体文件请求（用于测试）
    const startAgentRequest = async () => {
      if (isAgentRequesting.value) {
        console.log('智能体已在请求文件中，无法重复启动')
        return
      }
      
      // 模拟智能体请求特定类型的文件
      const fileTypes = ['审计报告', '工作底稿', '财务数据']
      const reason = '复核流程需要以下文件来完成分析'
      
      console.log('启动智能体文件请求:', fileTypes)
      await workspaceStore.requestFiles(fileTypes, reason)
    }
    
    // 跳过当前文件请求
    const skipFileRequest = () => {
      if (!isAgentRequesting.value) return
      
      workspaceStore.skipFileRequest('用户选择跳过文件请求')
      emit('supplement-completed', {
        providedFiles: [],
        message: '已跳过文件请求，继续复核流程',
        skipped: true
      })
    }
    
    // 重置会话统计（管理员功能）
    const resetSession = () => {
      if (confirm('确定要重置会话统计吗？这将清除所有请求计数和错误记录。')) {
        workspaceStore.resetSessionStatistics()
        console.log('会话统计已重置')
      }
    }

    // 解除阻止状态（管理员功能）
    const unblockRequests = () => {
      if (confirm('确定要解除文件请求阻止状态吗？')) {
        workspaceStore.unblockRequests()
        console.log('文件请求阻止状态已解除')
      }
    }
    
    // ===== 组件生命周期 =====
    onMounted(async () => {
      // 首先加载默认复核设置
      await loadDefaultSettings()
      
      // 然后加载服务器文件
      loadServerFiles()
      
      // 监听智能体文件请求
      watch(
        () => workspaceStore?.fileRequest?.isRequesting,
        (isRequesting) => {
          isAgentRequesting.value = isRequesting
          if (isRequesting) {
            requestedFileTypes.value = workspaceStore?.fileRequest?.requestedFiles
              ?.filter(f => f.status === 'pending')
              ?.map(f => f.type) || []
            
            // 开始超时倒计时
            startTimeoutCountdown()
          } else {
            requestedFileTypes.value = []
            clearTimeout(timeoutTimer.value)
            timeoutCountdown.value = 0
          }
        },
        { immediate: true }
      )
    })
    
    return {
      fileInput,
      uploadedFiles,
      serverFiles,
      allFiles,
      filteredFiles,
      isDragOver,
      isUploading,
      isRefreshing,
      uploadProgress,
      uploadErrors,
      moduleStatus,
      statusText,
      requestedFileTypes,
      isAgentRequesting,
      agentRequestInfo,
      timeoutCountdown,
      defaultTimeout,
      defaultSettings,
      settingsLoaded,
      triggerFileInput,
      handleFileSelect,
      handleDrop,
      handleDragOver,
      handleDragLeave,
      getFileIcon,
      formatFileSize,
      getFileTypeFromName,
      getStatusIcon,
      getStatusText,
      selectFileForAgent,
      isFileSelectedByAgent,
      canSelectForAgent,
      previewFile,
      downloadFile,
      removeFile,
      clearFiles,
      confirmUpload,
      retryFailedUploads,
      loadServerFiles,
      refreshFileList,
      batchClearFiles,
      closeModule,
      loadDefaultSettings,
      getTimeoutDuration,
      getTimeoutAction,
      isTimeoutScenarioEnabled,
      startAgentRequest,
      skipFileRequest,
       resetSession,
       unblockRequests,
       getAgentStatusIcon,
       getAgentStatusIconClass,
       getAgentStatusText
    }
  }
}
</script>

<style scoped>
/* 基础样式 */
.supplement-documents {
  background: white;
  border-radius: 8px;
  border: 1px solid #e9ecef;
  margin-bottom: 16px;
}

.module-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px 20px;
  border-bottom: 1px solid #e9ecef;
  background: #f8f9fa;
  border-radius: 8px 8px 0 0;
  position: relative;
}

.module-icon {
  font-size: 20px;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: white;
  border-radius: 6px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

.module-header h3 {
  flex: 1;
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #333;
}

.header-actions {
  display: flex;
  gap: 8px;
  margin-right: 12px;
}

.header-actions .btn-icon {
  padding: 6px 8px;
  border: 1px solid #ddd;
  background: white;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s;
}

.header-actions .btn-icon:hover:not(:disabled) {
  background: #f0f0f0;
  border-color: #ccc;
}

.header-actions .btn-icon:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.module-status {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.module-status.pending {
  background: #fff3cd;
  color: #856404;
}

.module-status.active {
  background: #d4edda;
  color: #155724;
}

.module-status.completed {
  background: #d1ecf1;
  color: #0c5460;
}

.module-status.error {
  background: #f8d7da;
  color: #721c24;
}

.close-btn {
  position: absolute;
  right: 16px;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  font-size: 18px;
  color: #6c757d;
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
  transition: all 0.2s;
}

.close-btn:hover {
  background: #e9ecef;
  color: #495057;
}

.module-content {
  padding: 20px;
}

/* 智能体请求横幅样式 */
.agent-request-banner {
  background: linear-gradient(135deg, #e3f2fd 0%, #f3e5f5 100%);
  border: 2px solid #2196f3;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 20px;
  box-shadow: 0 4px 12px rgba(33, 150, 243, 0.15);
}

.request-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.request-icon {
  font-size: 24px;
}

.request-header h4 {
  margin: 0;
  color: #1976d2;
  font-weight: 600;
  flex: 1;
}

.request-status {
  background: #ff9800;
  color: white;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
}

.request-message {
  margin: 0 0 12px 0;
  color: #424242;
  font-weight: 500;
}

.requested-types {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 12px;
}

.type-tag {
  background: #2196f3;
  color: white;
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 500;
}

.request-hint {
  margin: 0;
  color: #666;
  font-size: 14px;
  font-style: italic;
}

/* 超时倒计时样式 */
.request-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-top: 12px;
}

.timeout-countdown {
  margin-top: 16px;
  padding: 12px;
  background: rgba(255, 152, 0, 0.1);
  border-radius: 8px;
  border-left: 4px solid #ff9800;
  flex: 1;
}

.countdown-icon {
  font-size: 16px;
  margin-right: 8px;
}

.countdown-text {
  font-weight: 600;
  color: #f57c00;
}

.countdown-bar {
  margin-top: 8px;
  height: 4px;
  background: #ffcc80;
  border-radius: 2px;
  overflow: hidden;
}

.countdown-fill {
  height: 100%;
  background: #ff9800;
  transition: width 1s linear;
}

.btn-skip {
  padding: 6px 12px;
  background: #ff5722;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  font-weight: 500;
  transition: all 0.2s ease;
}

.btn-skip:hover {
  background: #d84315;
  transform: translateY(-1px);
}

.btn-skip:active {
  transform: translateY(0);
}

/* 上传区域样式 */
.upload-area {
  border: 2px dashed #ddd;
  border-radius: 8px;
  padding: 40px 20px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s;
  margin-bottom: 20px;
}

.upload-area:hover,
.upload-area.drag-over {
  border-color: #007bff;
  background: #f8f9ff;
}

.upload-area.agent-requesting {
  border-color: #9c27b0;
  background: linear-gradient(135deg, #f3e5f5 0%, #fce4ec 100%);
}

.upload-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.upload-text {
  font-size: 16px;
  font-weight: 500;
  color: #333;
  margin: 0 0 8px;
}

.upload-hint {
  font-size: 14px;
  color: #666;
  margin: 0;
}

/* 文件列表样式 */
.file-list {
  margin-bottom: 20px;
}

.list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.list-header h4 {
  margin: 0;
  font-size: 14px;
  font-weight: 600;
  color: #333;
}

.list-actions {
  display: flex;
  gap: 8px;
}

.btn-small {
  padding: 4px 8px;
  font-size: 12px;
  border: 1px solid #ddd;
  background: white;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-small:hover:not(:disabled) {
  background: #f0f0f0;
  border-color: #ccc;
}

.btn-small:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-small.btn-danger {
  color: #dc3545;
  border-color: #dc3545;
}

.btn-small.btn-danger:hover:not(:disabled) {
  background: #dc3545;
  color: white;
}

.file-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px;
  border: 1px solid #e9ecef;
  border-radius: 6px;
  margin-bottom: 8px;
  transition: all 0.3s ease;
}

.file-item.uploading {
  border-color: #007bff;
  background: #f8f9ff;
}

.file-item.completed {
  border-color: #28a745;
  background: #f8fff9;
}

.file-item.error {
  border-color: #dc3545;
  background: #fff8f8;
}

.file-item.agent-selected {
  border-color: #9c27b0;
  background: linear-gradient(135deg, #f3e5f5 0%, #e1bee7 100%);
  box-shadow: 0 2px 12px rgba(156, 39, 176, 0.2);
}

.agent-badge {
  background: #9c27b0;
  color: white;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 500;
  margin-left: 8px;
}

.file-info {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
}

.file-icon {
  font-size: 24px;
}

.file-details {
  flex: 1;
}

.file-name {
  font-weight: 500;
  color: #333;
  margin-bottom: 4px;
  display: flex;
  align-items: center;
}

.file-meta {
  font-size: 12px;
  color: #666;
}

.file-status {
  font-size: 11px;
  margin-top: 4px;
  display: flex;
  align-items: center;
  gap: 4px;
}

.status-icon {
  font-size: 14px;
}

.status-uploading {
  color: #007bff;
  font-weight: 500;
}

.status-completed {
  color: #28a745;
  font-weight: 500;
}

.status-error {
  color: #dc3545;
  font-weight: 500;
}

.status-pending {
  color: #ffc107;
  font-weight: 500;
}

.status-server {
  color: #6c757d;
  font-weight: 500;
}

.file-progress {
  margin-top: 6px;
}

.progress-bar-small {
  width: 100%;
  height: 4px;
  background: #e9ecef;
  border-radius: 2px;
  overflow: hidden;
}

.progress-fill-small {
  height: 100%;
  background: #007bff;
  transition: width 0.3s ease;
}

.file-actions {
  display: flex;
  gap: 8px;
}

.btn-icon {
  background: none;
  border: none;
  font-size: 16px;
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
  transition: all 0.2s;
}

.btn-icon:hover:not(:disabled) {
  background: #f8f9fa;
}

.btn-icon:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-icon.btn-danger:hover:not(:disabled) {
  background: #ffe6e6;
  color: #dc3545;
}

.btn-agent {
  border: 1px solid #9c27b0;
  color: #9c27b0;
  background: rgba(156, 39, 176, 0.05);
  border-radius: 4px;
}

.btn-agent:hover:not(:disabled) {
  background: rgba(156, 39, 176, 0.1);
  border-color: #7b1fa2;
  transform: scale(1.05);
}

/* 上传进度样式 */
.upload-progress {
  margin-bottom: 20px;
}

.progress-bar {
  width: 100%;
  height: 8px;
  background: #e9ecef;
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 8px;
}

.progress-fill {
  height: 100%;
  background: #007bff;
  transition: width 0.3s;
}

.progress-text {
  text-align: center;
  font-size: 14px;
  color: #666;
  margin: 0;
}

/* 错误信息样式 */
.upload-errors {
  margin-bottom: 20px;
  padding: 16px;
  background: #fff5f5;
  border: 1px solid #fed7d7;
  border-radius: 6px;
}

.upload-errors h4 {
  font-size: 14px;
  font-weight: 600;
  color: #c53030;
  margin: 0 0 12px;
}

.error-item {
  margin-bottom: 8px;
  font-size: 12px;
}

.error-file {
  font-weight: 500;
  color: #2d3748;
}

.error-message {
  color: #c53030;
  margin-left: 8px;
}

/* 智能体状态面板样式 */
.agent-status-panel {
  background: linear-gradient(135deg, #fff3e0 0%, #ffecb3 100%);
  border: 2px solid #ff9800;
  border-radius: 12px;
  padding: 16px;
  margin-bottom: 20px;
  box-shadow: 0 4px 12px rgba(255, 152, 0, 0.15);
}

.status-header {
  display: flex;
  align-items: flex-start;
  gap: 12px;
}

.status-icon {
  font-size: 24px;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background: white;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.status-icon.status-ready {
  background: #e8f5e8;
}

.status-icon.status-working {
  background: #e3f2fd;
}

.status-icon.status-requesting {
  background: #f3e5f5;
}

.status-icon.status-error {
  background: #ffebee;
}

.status-icon.status-blocked {
  background: #fafafa;
}

.status-icon.status-recovering {
  background: #fff3e0;
}

.status-info {
  flex: 1;
}

.status-info h4 {
  margin: 0 0 8px 0;
  color: #e65100;
  font-weight: 600;
  font-size: 16px;
}

.status-message {
  margin: 0 0 12px 0;
  color: #424242;
  font-size: 14px;
}

.status-stats {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  font-size: 12px;
  color: #666;
}

.status-stats span {
  background: rgba(255, 255, 255, 0.8);
  padding: 4px 8px;
  border-radius: 12px;
  font-weight: 500;
}

.block-warning {
  margin-top: 12px;
  padding: 12px;
  background: rgba(244, 67, 54, 0.1);
  border-radius: 8px;
  border-left: 4px solid #f44336;
  display: flex;
  align-items: center;
  gap: 8px;
}

.warning-icon {
  font-size: 16px;
}

.warning-text {
  color: #c62828;
  font-weight: 600;
  font-size: 14px;
}

/* 操作按钮样式 */
.action-buttons {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
}

.btn {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-secondary {
  background: #6c757d;
  color: white;
}

.btn-secondary:hover:not(:disabled) {
  background: #5a6268;
}

.btn-primary {
  background: #007bff;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #0056b3;
}

.btn-success {
  background: #28a745;
  color: white;
}

.btn-success:hover:not(:disabled) {
  background: #218838;
}
</style>