<!--
  执行复核组件
  - 显示未复核的重大事项列表，支持选择事项启动复核
  - 提供创建新重大事项的入口，支持直接创建和模板创建
  - 集成复核流程启动逻辑，与智能体状态管理深度集成
  - 支持复核确认对话框和状态反馈
-->
<template>
  <div class="execute-review">
    <!-- 组件头部 -->
    <div class="review-header">
      <h3>执行复核</h3>
      <p class="header-description">选择未复核的重大事项开始复核，或创建新的重大事项</p>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-container">
      <div class="loading-spinner"></div>
      <p>正在获取未复核事项...</p>
    </div>

    <!-- 错误状态 -->
    <div v-else-if="error" class="error-container">
      <div class="error-icon">⚠️</div>
      <p class="error-message">{{ error }}</p>
      <button class="retry-btn" @click="loadUnreviewedEvents">重试</button>
    </div>

    <!-- 主要内容区域 -->
    <div v-else class="review-content">
      <!-- 未复核事项列表 -->
      <div class="events-section">
        <h4 class="section-title">
          <span class="title-icon">📋</span>
          未复核的重大事项 ({{ unreviewedEvents.length }})
        </h4>
        
        <!-- 空状态 -->
        <div v-if="unreviewedEvents.length === 0" class="empty-state">
          <div class="empty-icon">📝</div>
          <p class="empty-message">暂无未复核的重大事项</p>
          <p class="empty-hint">您可以创建新的重大事项开始复核流程</p>
        </div>

        <!-- 事项列表 -->
        <div v-else class="events-list">
          <div 
            v-for="event in unreviewedEvents" 
            :key="event.id"
            class="event-item"
            @click="selectEvent(event)"
          >
            <div class="event-content">
              <div class="event-header">
                <h5 class="event-title">{{ event.title }}</h5>
                <span class="event-status unreviewed">未复核</span>
              </div>
              <p class="event-description">{{ event.description }}</p>
              <div class="event-meta">
                <span class="meta-item">
                  <span class="meta-icon">📅</span>
                  创建时间: {{ formatDate(event.createdAt) }}
                </span>
                <span class="meta-item">
                  <span class="meta-icon">🎯</span>
                  审计目标: {{ event.auditObjectives || '未设置' }}
                </span>
              </div>
            </div>
            <div class="event-actions">
              <button class="action-btn primary" @click.stop="confirmStartReview(event)">
                <span class="btn-icon">🚀</span>
                开始复核
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- 创建新事项区域 -->
      <div class="create-section">
        <h4 class="section-title">
          <span class="title-icon">➕</span>
          创建新的重大事项
        </h4>
        <div class="create-options">
          <div class="create-option" @click="createNewEvent('direct')">
            <div class="option-icon">📄</div>
            <div class="option-content">
              <h5>直接创建</h5>
              <p>从空白表单开始创建重大事项</p>
            </div>
            <div class="option-arrow">→</div>
          </div>
          <div class="create-option" @click="createNewEvent('template')">
            <div class="option-icon">📋</div>
            <div class="option-content">
              <h5>由模板创建</h5>
              <p>基于预设模板快速创建重大事项</p>
            </div>
            <div class="option-arrow">→</div>
          </div>
        </div>
      </div>
    </div>

    <!-- 复核确认对话框 -->
    <div v-if="showConfirmDialog" class="modal-overlay" @click="closeConfirmDialog">
      <div class="modal-content confirm-dialog" @click.stop>
        <div class="modal-header">
          <h3>确认开始复核</h3>
          <button class="close-btn" @click="closeConfirmDialog">×</button>
        </div>
        <div class="modal-body">
          <div class="confirm-event-info">
            <h4>{{ selectedEvent?.title }}</h4>
            <p>{{ selectedEvent?.description }}</p>
            <div class="event-details">
              <div class="detail-item">
                <span class="detail-label">审计目标:</span>
                <span class="detail-value">{{ selectedEvent?.auditObjectives || '未设置' }}</span>
              </div>
              <div class="detail-item">
                <span class="detail-label">创建时间:</span>
                <span class="detail-value">{{ formatDate(selectedEvent?.createdAt) }}</span>
              </div>
            </div>
          </div>
          <p class="confirm-message">确认要开始复核此重大事项吗？复核过程将由智能体引导完成。</p>
        </div>
        <div class="modal-actions">
          <button class="btn-secondary" @click="closeConfirmDialog">取消</button>
          <button class="btn-primary" @click="startReview" :disabled="starting">
            {{ starting ? '启动中...' : '确认开始复核' }}
          </button>
        </div>
      </div>
    </div>

    <!-- 操作按钮区域 -->
    <div class="component-actions">
      <button class="btn-secondary" @click="$emit('close')">
        关闭
      </button>
      <button class="btn-primary" @click="loadUnreviewedEvents" :disabled="loading">
        <span class="btn-icon">🔄</span>
        刷新列表
      </button>
    </div>
  </div>
</template>

<script>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useWorkspaceStore } from '@/stores/workspace'
import { useEventStore } from '@/stores/event'

export default {
  name: 'ExecuteReview',
  emits: ['close', 'review-started', 'event-created'],
  setup(props, { emit }) {
    const router = useRouter()
    const workspaceStore = useWorkspaceStore()
    const eventStore = useEventStore()

    // 响应式数据
    const loading = ref(false)
    const error = ref('')
    const unreviewedEvents = ref([])
    const showConfirmDialog = ref(false)
    const selectedEvent = ref(null)
    const starting = ref(false)

    // 组件挂载时加载未复核事项
    onMounted(() => {
      loadUnreviewedEvents()
    })

    /**
     * 加载未复核的重大事项列表
     * 从workspace store获取当前项目的未复核事项数据
     */
    const loadUnreviewedEvents = async () => {
      try {
        loading.value = true
        error.value = ''
        
        // 调用workspace store的数据库接口方法
        const result = await workspaceStore.getUnreviewedMajorEvents()
        
        if (result.success) {
          unreviewedEvents.value = result.data
        } else {
          throw new Error('获取数据失败')
        }
      } catch (err) {
        console.error('加载未复核事项失败:', err)
        error.value = err.message || '加载失败，请稍后重试'
      } finally {
        loading.value = false
      }
    }

    /**
     * 选择事项（点击事项卡片时触发）
     * @param {Object} event - 选中的重大事项对象
     */
    const selectEvent = (event) => {
      selectedEvent.value = event
      // 可以在这里添加选中状态的视觉反馈
      console.log('选中事项:', event.title)
    }

    /**
     * 确认开始复核（点击开始复核按钮时触发）
     * @param {Object} event - 要复核的重大事项对象
     */
    const confirmStartReview = (event) => {
      selectedEvent.value = event
      showConfirmDialog.value = true
    }

    /**
     * 关闭确认对话框
     */
    const closeConfirmDialog = () => {
      showConfirmDialog.value = false
      selectedEvent.value = null
      starting.value = false
    }

    /**
     * 启动复核流程
     * 调用workspace store的复核启动方法，开始智能体复核流程
     */
    const startReview = async () => {
      if (!selectedEvent.value) return
      
      try {
        starting.value = true
        
        // 调用workspace store启动复核流程
        const result = await workspaceStore.startMajorEventReview(
          selectedEvent.value.id,
          {
            // 复核配置参数
            autoAnalysis: true,
            includeEvidenceCheck: true,
            generateReport: true
          }
        )
        
        if (result.success) {
          // 通知父组件复核已启动
          emit('review-started', {
            event: selectedEvent.value,
            reviewId: result.data.reviewId
          })
          
          // 关闭对话框和组件
          closeConfirmDialog()
          emit('close')
        } else {
          throw new Error(result.message || '启动复核失败')
        }
      } catch (err) {
        console.error('启动复核失败:', err)
        error.value = err.message || '启动复核失败，请稍后重试'
      } finally {
        starting.value = false
      }
    }

    /**
     * 创建新的重大事项
     * 跳转到重大事项创建页面，支持直接创建和模板创建两种方式
     * @param {string} mode - 创建模式：'direct' | 'template'
     */
    const createNewEvent = (mode) => {
      // 保存当前创建模式到sessionStorage，供创建页面使用
      sessionStorage.setItem('createMode', mode)
      sessionStorage.setItem('returnToWorkbench', 'true')
      
      // 跳转到重大事项创建页面
      router.push({
        name: 'CreateMajorEvent',
        query: {
          mode: mode,
          from: 'workbench'
        }
      })
      
      // 通知父组件事项创建已开始
      emit('event-created', { mode })
      
      // 关闭当前组件
      emit('close')
    }

    /**
     * 格式化日期显示
     * @param {string} dateString - ISO日期字符串
     * @returns {string} 格式化后的日期字符串
     */
    const formatDate = (dateString) => {
      if (!dateString) return '未知'
      
      try {
        const date = new Date(dateString)
        return date.toLocaleDateString('zh-CN', {
          year: 'numeric',
          month: '2-digit',
          day: '2-digit',
          hour: '2-digit',
          minute: '2-digit'
        })
      } catch (err) {
        return '日期格式错误'
      }
    }

    return {
      // 响应式数据
      loading,
      error,
      unreviewedEvents,
      showConfirmDialog,
      selectedEvent,
      starting,
      
      // 方法
      loadUnreviewedEvents,
      selectEvent,
      confirmStartReview,
      closeConfirmDialog,
      startReview,
      createNewEvent,
      formatDate
    }
  }
}
</script>

<style scoped>
/* 组件主容器样式 */
.execute-review {
  padding: 24px;
  background: #ffffff;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  max-width: 800px;
  margin: 0 auto;
}

/* 头部样式 */
.review-header {
  margin-bottom: 24px;
  text-align: center;
}

.review-header h3 {
  margin: 0 0 8px 0;
  color: #1a1a1a;
  font-size: 24px;
  font-weight: 600;
}

.header-description {
  margin: 0;
  color: #666;
  font-size: 14px;
}

/* 加载状态样式 */
.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 40px 20px;
  color: #666;
}

.loading-spinner {
  width: 32px;
  height: 32px;
  border: 3px solid #f3f3f3;
  border-top: 3px solid #007bff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 16px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* 错误状态样式 */
.error-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 40px 20px;
  text-align: center;
}

.error-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.error-message {
  color: #dc3545;
  margin-bottom: 16px;
  font-size: 16px;
}

.retry-btn {
  padding: 8px 16px;
  background: #007bff;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
}

.retry-btn:hover {
  background: #0056b3;
}

/* 主要内容区域样式 */
.review-content {
  display: flex;
  flex-direction: column;
  gap: 32px;
}

/* 区域标题样式 */
.section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0 0 16px 0;
  color: #1a1a1a;
  font-size: 18px;
  font-weight: 600;
}

.title-icon {
  font-size: 20px;
}

/* 空状态样式 */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 40px 20px;
  text-align: center;
  background: #f8f9fa;
  border-radius: 8px;
  border: 2px dashed #dee2e6;
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.empty-message {
  margin: 0 0 8px 0;
  color: #495057;
  font-size: 16px;
  font-weight: 500;
}

.empty-hint {
  margin: 0;
  color: #6c757d;
  font-size: 14px;
}

/* 事项列表样式 */
.events-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.event-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px;
  background: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.event-item:hover {
  background: #e9ecef;
  border-color: #007bff;
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.event-content {
  flex: 1;
  min-width: 0;
}

.event-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
}

.event-title {
  margin: 0;
  color: #1a1a1a;
  font-size: 16px;
  font-weight: 600;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.event-status {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.event-status.unreviewed {
  background: #fff3cd;
  color: #856404;
  border: 1px solid #ffeaa7;
}

.event-description {
  margin: 0 0 12px 0;
  color: #495057;
  font-size: 14px;
  line-height: 1.4;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
}

.event-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 4px;
  color: #6c757d;
  font-size: 12px;
}

.meta-icon {
  font-size: 14px;
}

.event-actions {
  margin-left: 16px;
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.2s ease;
}

.action-btn.primary {
  background: #007bff;
  color: white;
}

.action-btn.primary:hover {
  background: #0056b3;
  transform: translateY(-1px);
}

.btn-icon {
  font-size: 16px;
}

/* 创建选项样式 */
.create-options {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.create-option {
  display: flex;
  align-items: center;
  padding: 20px;
  background: #ffffff;
  border: 2px solid #e9ecef;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.create-option:hover {
  border-color: #007bff;
  background: #f8f9ff;
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(0, 123, 255, 0.1);
}

.option-icon {
  font-size: 32px;
  margin-right: 16px;
  color: #007bff;
}

.option-content {
  flex: 1;
}

.option-content h5 {
  margin: 0 0 4px 0;
  color: #1a1a1a;
  font-size: 16px;
  font-weight: 600;
}

.option-content p {
  margin: 0;
  color: #6c757d;
  font-size: 14px;
}

.option-arrow {
  font-size: 20px;
  color: #007bff;
  font-weight: bold;
}

/* 模态框样式 */
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
}

.modal-content {
  background: white;
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
  max-width: 500px;
  width: 90%;
  max-height: 80vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 24px 16px;
  border-bottom: 1px solid #e9ecef;
}

.modal-header h3 {
  margin: 0;
  color: #1a1a1a;
  font-size: 20px;
  font-weight: 600;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  color: #6c757d;
  cursor: pointer;
  padding: 0;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
}

.close-btn:hover {
  background: #f8f9fa;
  color: #495057;
}

.modal-body {
  padding: 20px 24px;
}

.confirm-event-info {
  margin-bottom: 20px;
  padding: 16px;
  background: #f8f9fa;
  border-radius: 8px;
}

.confirm-event-info h4 {
  margin: 0 0 8px 0;
  color: #1a1a1a;
  font-size: 16px;
  font-weight: 600;
}

.confirm-event-info p {
  margin: 0 0 12px 0;
  color: #495057;
  font-size: 14px;
  line-height: 1.4;
}

.event-details {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.detail-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
}

.detail-label {
  color: #6c757d;
  font-weight: 500;
  min-width: 80px;
}

.detail-value {
  color: #495057;
}

.confirm-message {
  margin: 0;
  color: #495057;
  font-size: 14px;
  line-height: 1.5;
}

.modal-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  padding: 16px 24px 20px;
  border-top: 1px solid #e9ecef;
}

/* 组件操作按钮样式 */
.component-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  margin-top: 24px;
  padding-top: 20px;
  border-top: 1px solid #e9ecef;
}

.btn-secondary {
  padding: 10px 20px;
  background: #6c757d;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.2s ease;
}

.btn-secondary:hover {
  background: #545b62;
}

.btn-primary {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 10px 20px;
  background: #007bff;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.2s ease;
}

.btn-primary:hover {
  background: #0056b3;
}

.btn-primary:disabled {
  background: #6c757d;
  cursor: not-allowed;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .execute-review {
    padding: 16px;
    margin: 0 8px;
  }
  
  .event-item {
    flex-direction: column;
    align-items: stretch;
    gap: 16px;
  }
  
  .event-actions {
    margin-left: 0;
  }
  
  .create-option {
    padding: 16px;
  }
  
  .option-icon {
    font-size: 28px;
    margin-right: 12px;
  }
  
  .modal-content {
    width: 95%;
    margin: 0 8px;
  }
  
  .modal-actions {
    flex-direction: column;
  }
  
  .component-actions {
    flex-direction: column;
  }
}
</style>