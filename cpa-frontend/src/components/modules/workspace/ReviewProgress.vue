<template>
  <div class="review-progress-container">
    <!-- 复核进度标题栏 -->
    <div class="progress-header">
      <h3 class="progress-title">
        <i class="fas fa-tasks"></i>
        复核进度
      </h3>
      <div class="progress-status">
        <span class="status-badge" :class="statusClass">{{ statusText }}</span>
        <span v-if="reviewProcess.isActive" class="elapsed-time">{{ elapsedTime }}</span>
      </div>
    </div>

    <!-- 整体进度条 -->
    <div class="overall-progress">
      <div class="progress-info">
        <span class="progress-label">整体进度</span>
        <span class="progress-percentage">{{ Math.round(reviewProcess.progress) }}%</span>
      </div>
      <div class="progress-bar">
        <div 
          class="progress-fill" 
          :style="{ width: reviewProcess.progress + '%' }"
          :class="progressBarClass"
        ></div>
      </div>
    </div>

    <!-- 阶段列表 -->
    <div class="stages-container">
      <div class="stages-header">
        <h4>复核阶段</h4>
        <span class="current-stage">当前: {{ currentStageName }}</span>
      </div>
      
      <div class="stages-list">
        <div 
          v-for="(stage, index) in reviewProcess.stages" 
          :key="index"
          class="stage-item"
          :class="{
            'stage-current': index === reviewProcess.currentStageIndex,
            'stage-completed': stage.status === 'completed',
            'stage-error': stage.status === 'error',
            'stage-running': stage.status === 'running'
          }"
        >
          <!-- 阶段图标 -->
          <div class="stage-icon">
            <i v-if="stage.status === 'completed'" class="fas fa-check-circle"></i>
            <i v-else-if="stage.status === 'error'" class="fas fa-exclamation-circle"></i>
            <i v-else-if="stage.status === 'running'" class="fas fa-spinner fa-spin"></i>
            <i v-else class="fas fa-circle"></i>
          </div>
          
          <!-- 阶段信息 -->
          <div class="stage-content">
            <div class="stage-header">
              <span class="stage-name">{{ stage.name }}</span>
              <span class="stage-progress">{{ Math.round(stage.progress) }}%</span>
            </div>
            <div class="stage-description">{{ stage.description }}</div>
            
            <!-- 阶段进度条 -->
            <div class="stage-progress-bar">
              <div 
                class="stage-progress-fill" 
                :style="{ width: stage.progress + '%' }"
                :class="getStageProgressClass(stage.status)"
              ></div>
            </div>
            
            <!-- 阶段时间信息 -->
            <div v-if="stage.startTime" class="stage-time">
              <span>开始时间: {{ formatTime(stage.startTime) }}</span>
              <span v-if="stage.endTime">完成时间: {{ formatTime(stage.endTime) }}</span>
              <span v-else-if="stage.status === 'running'">耗时: {{ getStageElapsedTime(stage.startTime) }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 用户输入对话框 -->
    <div v-if="reviewProcess.userInputRequired" class="user-input-dialog">
      <div class="dialog-overlay" @click="closeUserInputDialog"></div>
      <div class="dialog-content">
        <div class="dialog-header">
          <h4>智能体请求输入</h4>
          <div class="timeout-timer" v-if="timeoutRemaining > 0">
            <i class="fas fa-clock"></i>
            <span>{{ Math.ceil(timeoutRemaining / 1000) }}秒后自动继续</span>
          </div>
        </div>
        
        <div class="dialog-body">
          <p class="input-prompt">{{ reviewProcess.userInputPrompt }}</p>
          <textarea 
            v-model="userInput" 
            class="input-textarea"
            placeholder="请输入您的回复..."
            rows="4"
            @keydown.ctrl.enter="submitUserInput"
          ></textarea>
        </div>
        
        <div class="dialog-footer">
          <button class="btn btn-secondary" @click="skipUserInput">跳过</button>
          <button class="btn btn-primary" @click="submitUserInput" :disabled="!userInput.trim()">发送 (Ctrl+Enter)</button>
        </div>
      </div>
    </div>

    <!-- 错误信息显示 -->
    <div v-if="reviewProcess.status === 'error'" class="error-panel">
      <div class="error-header">
        <i class="fas fa-exclamation-triangle"></i>
        <span>复核过程出现错误</span>
      </div>
      <div class="error-content">
        <p class="error-message">{{ reviewProcess.errorMessage }}</p>
        <div class="error-actions">
          <button class="btn btn-outline" @click="retryReview">重试</button>
          <button class="btn btn-secondary" @click="resetReview">重置</button>
        </div>
      </div>
    </div>

    <!-- 复核完成面板 -->
    <div v-if="reviewProcess.status === 'completed'" class="completion-panel">
      <div class="completion-header">
        <i class="fas fa-check-circle"></i>
        <span>复核已完成</span>
      </div>
      <div class="completion-content">
        <p>复核分析已成功完成，耗时 {{ totalElapsedTime }}</p>
        <div class="completion-actions">
          <button class="btn btn-primary" @click="viewResults">查看结果</button>
          <button class="btn btn-outline" @click="downloadResults">下载报告</button>
        </div>
      </div>
    </div>

    <!-- 操作按钮区域 -->
    <div class="action-buttons">
      <button 
        v-if="reviewProcess.status === 'paused'"
        class="btn btn-primary"
        @click="resumeReview"
      >
        <i class="fas fa-play"></i>
        继续复核
      </button>
      
      <button 
        v-if="reviewProcess.isActive && reviewProcess.status !== 'paused'"
        class="btn btn-warning"
        @click="pauseReview"
      >
        <i class="fas fa-pause"></i>
        暂停复核
      </button>
      
      <button 
        v-if="reviewProcess.isActive"
        class="btn btn-danger"
        @click="stopReview"
      >
        <i class="fas fa-stop"></i>
        停止复核
      </button>
    </div>
  </div>
</template>

<script>
import { computed, ref, onMounted, onUnmounted } from 'vue'
import { useWorkspaceStore } from '@/stores/workspace'

export default {
  name: 'ReviewProgress',
  emits: ['add-message'],
  setup(props, { emit }) {
    const workspaceStore = useWorkspaceStore()
    const userInput = ref('')
    const timeoutRemaining = ref(0)
    let timeoutInterval = null
    let elapsedTimeInterval = null

    // 计算属性
    const reviewProcess = computed(() => workspaceStore.reviewProcess)
    
    const statusClass = computed(() => {
      const status = reviewProcess.value.status
      return {
        'status-idle': status === 'idle',
        'status-analyzing': status === 'analyzing',
        'status-paused': status === 'paused',
        'status-completed': status === 'completed',
        'status-error': status === 'error'
      }
    })
    
    const statusText = computed(() => {
      const statusMap = {
        'idle': '待开始',
        'analyzing': '分析中',
        'paused': '已暂停',
        'completed': '已完成',
        'error': '出现错误'
      }
      return statusMap[reviewProcess.value.status] || '未知状态'
    })
    
    const progressBarClass = computed(() => {
      const status = reviewProcess.value.status
      return {
        'progress-analyzing': status === 'analyzing',
        'progress-paused': status === 'paused',
        'progress-completed': status === 'completed',
        'progress-error': status === 'error'
      }
    })
    
    const currentStageName = computed(() => {
      const currentIndex = reviewProcess.value.currentStageIndex
      const stages = reviewProcess.value.stages
      return stages[currentIndex]?.name || '无'
    })
    
    const elapsedTime = computed(() => {
      if (!reviewProcess.value.startTime) return '00:00:00'
      const start = new Date(reviewProcess.value.startTime)
      const now = new Date()
      return formatDuration(now - start)
    })
    
    const totalElapsedTime = computed(() => {
      if (!reviewProcess.value.startTime) return '00:00:00'
      const start = new Date(reviewProcess.value.startTime)
      const end = reviewProcess.value.endTime ? new Date(reviewProcess.value.endTime) : new Date()
      return formatDuration(end - start)
    })

    // 方法
    const formatTime = (timestamp) => {
      return new Date(timestamp).toLocaleTimeString('zh-CN')
    }
    
    const formatDuration = (milliseconds) => {
      const seconds = Math.floor(milliseconds / 1000)
      const hours = Math.floor(seconds / 3600)
      const minutes = Math.floor((seconds % 3600) / 60)
      const secs = seconds % 60
      return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
    }
    
    const getStageElapsedTime = (startTime) => {
      const start = new Date(startTime)
      const now = new Date()
      return formatDuration(now - start)
    }
    
    const getStageProgressClass = (status) => {
      return {
        'stage-progress-running': status === 'running',
        'stage-progress-completed': status === 'completed',
        'stage-progress-error': status === 'error'
      }
    }
    
    const closeUserInputDialog = () => {
      // 点击遮罩层不关闭对话框，需要用户主动操作
    }
    
    const submitUserInput = async () => {
      if (!userInput.value.trim()) return
      
      try {
        // 发送用户输入到WebSocket
        workspaceStore.sendWebSocketMessage({
          type: 'user_input',
          data: {
            input: userInput.value,
            timestamp: new Date().toISOString()
          }
        })
        
        // 向父组件发送添加感谢消息的请求
        emit('add-message', {
          type: 'ai',
          content: '感谢您补充的信息。继续复核……'
        })
        
        // 清空输入框
        userInput.value = ''
        
        // 更新状态
        workspaceStore.reviewProcess.userInputRequired = false
        workspaceStore.reviewProcess.userInputPrompt = null
        workspaceStore.reviewProcess.status = 'analyzing'
        
        // 清除超时计时器
        clearTimeoutTimer()
        
      } catch (error) {
        console.error('发送用户输入失败:', error)
      }
    }
    
    const skipUserInput = () => {
      // 跳过用户输入，继续流程
      workspaceStore.sendWebSocketMessage({
        type: 'user_input_skip',
        data: {
          timestamp: new Date().toISOString()
        }
      })
      
      workspaceStore.reviewProcess.userInputRequired = false
      workspaceStore.reviewProcess.userInputPrompt = null
      workspaceStore.reviewProcess.status = 'analyzing'
      
      clearTimeoutTimer()
    }
    
    const retryReview = async () => {
      try {
        // 重置错误状态
        workspaceStore.reviewProcess.status = 'idle'
        workspaceStore.reviewProcess.errorMessage = null
        
        // 重新开始复核（前端状态恢复 + 继续执行）
        workspaceStore.reviewProcess.isActive = true
        workspaceStore.reviewProcess.progress = 0
        await workspaceStore.resumeReviewProcess()
      } catch (error) {
        console.error('重试复核失败:', error)
      }
    }
    
    const resetReview = () => {
      // 重置复核状态
      workspaceStore.reviewProcess.status = 'idle'
      workspaceStore.reviewProcess.isActive = false
      workspaceStore.reviewProcess.progress = 0
      workspaceStore.reviewProcess.currentStageIndex = 0
      workspaceStore.reviewProcess.errorMessage = null
      workspaceStore.reviewProcess.userInputRequired = false
      workspaceStore.reviewProcess.userInputPrompt = null
      
      // 重置所有阶段
      workspaceStore.reviewProcess.stages.forEach(stage => {
        stage.status = 'pending'
        stage.progress = 0
        stage.startTime = null
        stage.endTime = null
      })
    }
    
    const resumeReview = async () => {
      try {
        await workspaceStore.resumeReviewProcess()
      } catch (error) {
        console.error('恢复复核失败:', error)
      }
    }
    
    const pauseReview = async () => {
      try {
        await workspaceStore.pauseReviewProcess()
      } catch (error) {
        console.error('暂停复核失败:', error)
      }
    }
    
    const stopReview = async () => {
      try {
        // 停止复核并清理资源
        workspaceStore.reviewProcess.status = 'idle'
        workspaceStore.reviewProcess.isActive = false
        
        // 发送停止消息
        workspaceStore.sendWebSocketMessage({
          type: 'stop_review',
          data: {
            timestamp: new Date().toISOString()
          }
        })
        
        // 清理计时器
        workspaceStore.clearAllTimeouts()
        
      } catch (error) {
        console.error('停止复核失败:', error)
      }
    }
    
    const viewResults = () => {
      // 跳转到结果确认页面
      this.$emit('view-results')
    }
    
    const downloadResults = () => {
      // 下载复核结果报告
      this.$emit('download-results')
    }
    
    const startTimeoutTimer = (duration) => {
      timeoutRemaining.value = duration
      timeoutInterval = setInterval(() => {
        timeoutRemaining.value -= 1000
        if (timeoutRemaining.value <= 0) {
          clearTimeoutTimer()
        }
      }, 1000)
    }
    
    const clearTimeoutTimer = () => {
      if (timeoutInterval) {
        clearInterval(timeoutInterval)
        timeoutInterval = null
      }
      timeoutRemaining.value = 0
    }
    
    const startElapsedTimeUpdate = () => {
      elapsedTimeInterval = setInterval(() => {
        // 触发计算属性更新
      }, 1000)
    }
    
    const stopElapsedTimeUpdate = () => {
      if (elapsedTimeInterval) {
        clearInterval(elapsedTimeInterval)
        elapsedTimeInterval = null
      }
    }

    // 生命周期
    onMounted(() => {
      startElapsedTimeUpdate()
      
      // 监听用户输入超时
      if (reviewProcess.value.userInputRequired) {
        const defaultTimeout = workspaceStore.timeout.defaultDuration
        startTimeoutTimer(defaultTimeout)
      }
    })
    
    onUnmounted(() => {
      clearTimeoutTimer()
      stopElapsedTimeUpdate()
    })

    return {
      // 响应式数据
      reviewProcess,
      userInput,
      timeoutRemaining,
      
      // 计算属性
      statusClass,
      statusText,
      progressBarClass,
      currentStageName,
      elapsedTime,
      totalElapsedTime,
      
      // 方法
      formatTime,
      getStageElapsedTime,
      getStageProgressClass,
      closeUserInputDialog,
      submitUserInput,
      skipUserInput,
      retryReview,
      resetReview,
      resumeReview,
      pauseReview,
      stopReview,
      viewResults,
      downloadResults
    }
  }
}
</script>

<style scoped>
.review-progress-container {
  padding: 20px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

/* 进度标题栏 */
.progress-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid #e8e8e8;
}

.progress-title {
  margin: 0;
  color: #333;
  font-size: 18px;
  font-weight: 600;
}

.progress-title i {
  margin-right: 8px;
  color: #1890ff;
}

.progress-status {
  display: flex;
  align-items: center;
  gap: 12px;
}

.status-badge {
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.status-idle {
  background: #f0f0f0;
  color: #666;
}

.status-analyzing {
  background: #e6f7ff;
  color: #1890ff;
}

.status-paused {
  background: #fff7e6;
  color: #fa8c16;
}

.status-completed {
  background: #f6ffed;
  color: #52c41a;
}

.status-error {
  background: #fff2f0;
  color: #ff4d4f;
}

.elapsed-time {
  font-family: 'Courier New', monospace;
  font-size: 14px;
  color: #666;
}

/* 整体进度条 */
.overall-progress {
  margin-bottom: 24px;
}

.progress-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.progress-label {
  font-weight: 500;
  color: #333;
}

.progress-percentage {
  font-weight: 600;
  color: #1890ff;
}

.progress-bar {
  height: 8px;
  background: #f0f0f0;
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  border-radius: 4px;
  transition: width 0.3s ease;
}

.progress-analyzing {
  background: linear-gradient(90deg, #1890ff, #40a9ff);
}

.progress-paused {
  background: #fa8c16;
}

.progress-completed {
  background: #52c41a;
}

.progress-error {
  background: #ff4d4f;
}

/* 阶段容器 */
.stages-container {
  margin-bottom: 24px;
}

.stages-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.stages-header h4 {
  margin: 0;
  color: #333;
  font-size: 16px;
  font-weight: 600;
}

.current-stage {
  font-size: 14px;
  color: #666;
}

/* 阶段列表 */
.stages-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.stage-item {
  display: flex;
  align-items: flex-start;
  padding: 16px;
  border: 1px solid #e8e8e8;
  border-radius: 6px;
  transition: all 0.3s ease;
}

.stage-current {
  border-color: #1890ff;
  background: #f6ffed;
}

.stage-completed {
  border-color: #52c41a;
  background: #f6ffed;
}

.stage-error {
  border-color: #ff4d4f;
  background: #fff2f0;
}

.stage-running {
  border-color: #1890ff;
  background: #e6f7ff;
}

.stage-icon {
  margin-right: 12px;
  margin-top: 2px;
}

.stage-icon i {
  font-size: 16px;
}

.stage-completed .stage-icon i {
  color: #52c41a;
}

.stage-error .stage-icon i {
  color: #ff4d4f;
}

.stage-running .stage-icon i {
  color: #1890ff;
}

.stage-content {
  flex: 1;
}

.stage-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 4px;
}

.stage-name {
  font-weight: 500;
  color: #333;
}

.stage-progress {
  font-size: 12px;
  color: #666;
}

.stage-description {
  font-size: 12px;
  color: #999;
  margin-bottom: 8px;
}

.stage-progress-bar {
  height: 4px;
  background: #f0f0f0;
  border-radius: 2px;
  overflow: hidden;
  margin-bottom: 8px;
}

.stage-progress-fill {
  height: 100%;
  border-radius: 2px;
  transition: width 0.3s ease;
}

.stage-progress-running {
  background: #1890ff;
}

.stage-progress-completed {
  background: #52c41a;
}

.stage-progress-error {
  background: #ff4d4f;
}

.stage-time {
  display: flex;
  gap: 16px;
  font-size: 11px;
  color: #999;
}

/* 用户输入对话框 */
.user-input-dialog {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
}

.dialog-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
}

.dialog-content {
  position: relative;
  width: 500px;
  max-width: 90vw;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
}

.dialog-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid #e8e8e8;
}

.dialog-header h4 {
  margin: 0;
  color: #333;
}

.timeout-timer {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: #fa8c16;
}

.dialog-body {
  padding: 20px;
}

.input-prompt {
  margin-bottom: 12px;
  color: #333;
  line-height: 1.5;
}

.input-textarea {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
  resize: vertical;
  font-family: inherit;
}

.input-textarea:focus {
  border-color: #1890ff;
  outline: none;
  box-shadow: 0 0 0 2px rgba(24, 144, 255, 0.2);
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  padding: 16px 20px;
  border-top: 1px solid #e8e8e8;
}

/* 错误面板 */
.error-panel {
  margin-bottom: 20px;
  padding: 16px;
  background: #fff2f0;
  border: 1px solid #ffccc7;
  border-radius: 6px;
}

.error-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
  color: #ff4d4f;
  font-weight: 500;
}

.error-message {
  margin-bottom: 12px;
  color: #333;
  line-height: 1.5;
}

.error-actions {
  display: flex;
  gap: 8px;
}

/* 完成面板 */
.completion-panel {
  margin-bottom: 20px;
  padding: 16px;
  background: #f6ffed;
  border: 1px solid #b7eb8f;
  border-radius: 6px;
}

.completion-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
  color: #52c41a;
  font-weight: 500;
}

.completion-content p {
  margin-bottom: 12px;
  color: #333;
  line-height: 1.5;
}

.completion-actions {
  display: flex;
  gap: 8px;
}

/* 操作按钮 */
.action-buttons {
  display: flex;
  gap: 8px;
  justify-content: flex-end;
}

.btn {
  padding: 8px 16px;
  border: 1px solid transparent;
  border-radius: 4px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s ease;
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-primary {
  background: #1890ff;
  border-color: #1890ff;
  color: #fff;
}

.btn-primary:hover:not(:disabled) {
  background: #40a9ff;
  border-color: #40a9ff;
}

.btn-secondary {
  background: #f5f5f5;
  border-color: #d9d9d9;
  color: #333;
}

.btn-secondary:hover:not(:disabled) {
  background: #e6f7ff;
  border-color: #91d5ff;
}

.btn-warning {
  background: #fa8c16;
  border-color: #fa8c16;
  color: #fff;
}

.btn-warning:hover:not(:disabled) {
  background: #ffa940;
  border-color: #ffa940;
}

.btn-danger {
  background: #ff4d4f;
  border-color: #ff4d4f;
  color: #fff;
}

.btn-danger:hover:not(:disabled) {
  background: #ff7875;
  border-color: #ff7875;
}

.btn-outline {
  background: transparent;
  border-color: #1890ff;
  color: #1890ff;
}

.btn-outline:hover:not(:disabled) {
  background: #e6f7ff;
}
</style>