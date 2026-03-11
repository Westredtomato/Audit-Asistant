<!--
  DeleteConfirmDialog.vue - 删除确认对话框组件
  提供更友好的删除确认界面，包含详细信息展示和风险提示
-->
<template>
  <div class="delete-confirm-overlay" v-if="visible" @click="handleOverlayClick">
    <div class="delete-confirm-dialog" @click.stop>
      <!-- 对话框头部 -->
      <div class="dialog-header">
        <div class="warning-icon">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M12 9V13M12 17H12.01M21 12C21 16.9706 16.9706 21 12 21C7.02944 21 3 16.9706 3 12C3 7.02944 7.02944 3 12 3C16.9706 3 21 7.02944 21 12Z" stroke="#f56565" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </div>
        <h3 class="dialog-title">{{ dialogTitle }}</h3>
        <button class="close-btn" @click="handleCancel">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M18 6L6 18M6 6L18 18" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </button>
      </div>

      <!-- 对话框内容 -->
      <div class="dialog-content">
        <!-- 首次删除提示 -->
        <div class="first-time-warning" v-if="isFirstTime">
          <div class="warning-badge">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M12 9V13M12 17H12.01M21 12C21 16.9706 16.9706 21 12 21C7.02944 21 3 16.9706 3 12C3 7.02944 7.02944 3 12 3C16.9706 3 21 7.02944 21 12Z" stroke="#f56565" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            首次删除操作
          </div>
          <p class="warning-text">
            这是您首次执行删除操作，请仔细阅读以下风险提示和操作指引。
          </p>
        </div>

        <!-- 事项信息展示 -->
        <div class="event-info">
          <h4>待删除的重大事项信息：</h4>
          <div class="info-grid">
            <div class="info-item">
              <span class="label">事项标题：</span>
              <span class="value">{{ eventData.title }}</span>
            </div>
            <div class="info-item">
              <span class="label">事项ID：</span>
              <span class="value">{{ eventData.id }}</span>
            </div>
            <div class="info-item">
              <span class="label">当前版本：</span>
              <span class="value">{{ eventData.version }}</span>
            </div>
            <div class="info-item">
              <span class="label">当前状态：</span>
              <span class="value status" :class="getStatusClass(eventData.status)">
                {{ getStatusText(eventData.status) }}
              </span>
            </div>
            <div class="info-item">
              <span class="label">最后更新：</span>
              <span class="value">{{ formatDate(eventData.updatedAt) }}</span>
            </div>
          </div>
        </div>

        <!-- 风险提示 -->
        <div class="risk-warning">
          <h4>⚠️ 重要风险提示：</h4>
          <ul class="warning-list">
            <li>此操作将同时删除与该事项相关的所有历史版本信息</li>
            <li>相关的复核结果和操作日志记录也将被永久清理</li>
            <li>删除操作不可撤销，无法通过系统功能恢复</li>
            <li>建议在删除前确认已导出必要的备份数据</li>
          </ul>
        </div>

        <!-- 备份提示 -->
        <div class="backup-section">
          <h4>数据备份建议：</h4>
          <p>如需保留该事项的历史记录，建议在删除前进行数据导出。</p>
          <button class="backup-btn" @click="handleBackup" disabled>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M21 15V19C21 19.5304 20.7893 20.0391 20.4142 20.4142C20.0391 20.7893 19.5304 21 19 21H5C4.46957 21 3.96086 20.7893 3.58579 20.4142C3.21071 20.0391 3 19.5304 3 19V15" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M7 10L12 15L17 10" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M12 15V3" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            导出备份（功能开发中）
          </button>
        </div>

        <!-- 删除原因输入 -->
        <div class="delete-reason">
          <h4>删除原因（可选）：</h4>
          <textarea 
            v-model="deleteReason" 
            placeholder="请输入删除原因，这将有助于操作审计和问题追踪..."
            rows="3"
            maxlength="200"
          ></textarea>
          <div class="char-count">{{ deleteReason.length }}/200</div>
        </div>
      </div>

      <!-- 对话框底部操作按钮 -->
      <div class="dialog-footer">
        <button class="cancel-btn" @click="handleCancel">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M18 6L6 18M6 6L18 18" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          取消
        </button>
        <button class="confirm-btn" @click="handleConfirm" :disabled="loading">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" v-if="!loading">
            <path d="M3 6H5H21" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M19 6V20C19 20.5304 18.7893 21.0391 18.4142 21.4142C18.0391 21.7893 17.5304 22 17 22H7C6.46957 22 6.96086 21.7893 6.58579 21.4142C6.21071 21.0391 6 20.5304 6 20V6M8 6V4C8 3.46957 8.21071 2.96086 8.58579 2.58579C8.96086 2.21071 9.46957 2 10 2H14C14.5304 2 15.0391 2.21071 15.4142 2.58579C15.7893 2.96086 16 3.46957 16 4V6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M10 11V17" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M14 11V17" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          <div class="loading-spinner" v-if="loading"></div>
          {{ loading ? '删除中...' : '确认删除' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed } from 'vue'

export default {
  name: 'DeleteConfirmDialog',
  
  props: {
    // 对话框显示状态
    visible: {
      type: Boolean,
      default: false
    },
    // 要删除的事项数据
    eventData: {
      type: Object,
      required: true
    },
    // 是否为首次删除操作
    isFirstTime: {
      type: Boolean,
      default: false
    },
    // 加载状态
    loading: {
      type: Boolean,
      default: false
    }
  },
  
  emits: ['confirm', 'cancel', 'backup'],
  
  setup(props, { emit }) {
    // ==================== 响应式数据 ====================
    
    // 删除原因输入
    const deleteReason = ref('')
    
    // ==================== 计算属性 ====================
    
    /**
     * 对话框标题
     */
    const dialogTitle = computed(() => {
      return props.isFirstTime ? '首次删除操作确认' : '删除重大事项确认'
    })
    
    // ==================== 方法 ====================
    
    /**
     * 获取状态对应的CSS类名
     * @param {string} status - 状态值
     * @returns {string} CSS类名
     */
    const getStatusClass = (status) => {
      const statusClasses = {
        'pending': 'status-pending',    // 未复核 - 灰色
        'reviewing': 'status-reviewing', // 复核中 - 黄色
        'reviewed': 'status-reviewed'    // 已复核 - 绿色
      }
      return statusClasses[status] || 'status-default'
    }
    
    /**
     * 获取状态显示文本
     * @param {string} status - 状态值
     * @returns {string} 显示文本
     */
    const getStatusText = (status) => {
      const statusTexts = {
        'pending': '未复核',
        'reviewing': '复核中',
        'reviewed': '已复核'
      }
      return statusTexts[status] || '未知状态'
    }
    
    /**
     * 格式化日期显示
     * @param {string} dateString - 日期字符串
     * @returns {string} 格式化后的日期
     */
    const formatDate = (dateString) => {
      try {
        const date = new Date(dateString)
        return date.toLocaleDateString('zh-CN', {
          year: 'numeric',
          month: '2-digit',
          day: '2-digit',
          hour: '2-digit',
          minute: '2-digit'
        })
      } catch (error) {
        return '日期格式错误'
      }
    }
    
    /**
     * 处理遮罩层点击事件
     * @param {Event} event - 点击事件
     */
    const handleOverlayClick = (event) => {
      // 点击遮罩层关闭对话框
      if (event.target === event.currentTarget) {
        handleCancel()
      }
    }
    
    /**
     * 处理取消操作
     */
    const handleCancel = () => {
      // 清空删除原因
      deleteReason.value = ''
      // 触发取消事件
      emit('cancel')
    }
    
    /**
     * 处理确认删除操作
     */
    const handleConfirm = () => {
      // 触发确认事件，传递删除原因
      emit('confirm', {
        deleteReason: deleteReason.value.trim() || '用户主动删除',
        eventData: props.eventData
      })
    }
    
    /**
     * 处理备份操作
     */
    const handleBackup = () => {
      // 触发备份事件
      emit('backup', props.eventData)
    }
    
    // ==================== 返回组件接口 ====================
    
    return {
      // 响应式数据
      deleteReason,
      
      // 计算属性
      dialogTitle,
      
      // 方法
      getStatusClass,
      getStatusText,
      formatDate,
      handleOverlayClick,
      handleCancel,
      handleConfirm,
      handleBackup
    }
  }
}
</script>

<style scoped>
/* ==================== 对话框遮罩层 ==================== */
.delete-confirm-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  backdrop-filter: blur(4px);
}

/* ==================== 对话框主体 ==================== */
.delete-confirm-dialog {
  background: white;
  border-radius: 12px;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
  max-width: 600px;
  width: 90%;
  max-height: 90vh;
  overflow-y: auto;
  animation: dialogSlideIn 0.3s ease-out;
}

@keyframes dialogSlideIn {
  from {
    opacity: 0;
    transform: translateY(-20px) scale(0.95);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

/* ==================== 对话框头部 ==================== */
.dialog-header {
  display: flex;
  align-items: center;
  padding: 24px 24px 16px;
  border-bottom: 1px solid #e5e7eb;
}

.warning-icon {
  margin-right: 12px;
  flex-shrink: 0;
}

.dialog-title {
  flex: 1;
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #1f2937;
}

.close-btn {
  background: none;
  border: none;
  padding: 8px;
  cursor: pointer;
  color: #6b7280;
  border-radius: 6px;
  transition: all 0.2s;
}

.close-btn:hover {
  background-color: #f3f4f6;
  color: #374151;
}

/* ==================== 对话框内容 ==================== */
.dialog-content {
  padding: 24px;
}

/* 首次删除警告 */
.first-time-warning {
  background: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 24px;
}

.warning-badge {
  display: flex;
  align-items: center;
  font-weight: 600;
  color: #dc2626;
  margin-bottom: 8px;
}

.warning-badge svg {
  margin-right: 8px;
}

.warning-text {
  color: #7f1d1d;
  margin: 0;
  line-height: 1.5;
}

/* 事项信息展示 */
.event-info {
  margin-bottom: 24px;
}

.event-info h4 {
  margin: 0 0 16px 0;
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
}

.info-grid {
  display: grid;
  gap: 12px;
}

.info-item {
  display: flex;
  align-items: center;
  padding: 12px;
  background: #f9fafb;
  border-radius: 6px;
  border: 1px solid #e5e7eb;
}

.info-item .label {
  font-weight: 500;
  color: #6b7280;
  min-width: 80px;
  margin-right: 12px;
}

.info-item .value {
  color: #1f2937;
  flex: 1;
}

.info-item .value.status {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.status-pending {
  background: #f3f4f6;
  color: #6b7280;
}

.status-reviewing {
  background: #fef3c7;
  color: #d97706;
}

.status-reviewed {
  background: #d1fae5;
  color: #059669;
}

/* 风险提示 */
.risk-warning {
  margin-bottom: 24px;
}

.risk-warning h4 {
  margin: 0 0 12px 0;
  font-size: 16px;
  font-weight: 600;
  color: #dc2626;
}

.warning-list {
  margin: 0;
  padding-left: 20px;
  color: #7f1d1d;
  line-height: 1.6;
}

.warning-list li {
  margin-bottom: 8px;
}

/* 备份部分 */
.backup-section {
  margin-bottom: 24px;
  padding: 16px;
  background: #f0f9ff;
  border: 1px solid #bae6fd;
  border-radius: 8px;
}

.backup-section h4 {
  margin: 0 0 8px 0;
  font-size: 14px;
  font-weight: 600;
  color: #0369a1;
}

.backup-section p {
  margin: 0 0 12px 0;
  color: #075985;
  font-size: 14px;
  line-height: 1.5;
}

.backup-btn {
  display: flex;
  align-items: center;
  padding: 8px 12px;
  background: #0ea5e9;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
}

.backup-btn:disabled {
  background: #94a3b8;
  cursor: not-allowed;
}

.backup-btn:not(:disabled):hover {
  background: #0284c7;
}

.backup-btn svg {
  margin-right: 6px;
}

/* 删除原因输入 */
.delete-reason h4 {
  margin: 0 0 12px 0;
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
}

.delete-reason textarea {
  width: 100%;
  padding: 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 14px;
  line-height: 1.5;
  resize: vertical;
  min-height: 80px;
  font-family: inherit;
}

.delete-reason textarea:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.char-count {
  text-align: right;
  font-size: 12px;
  color: #6b7280;
  margin-top: 4px;
}

/* ==================== 对话框底部 ==================== */
.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 16px 24px 24px;
  border-top: 1px solid #e5e7eb;
}

.cancel-btn,
.confirm-btn {
  display: flex;
  align-items: center;
  padding: 10px 16px;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.cancel-btn {
  background: #f3f4f6;
  color: #374151;
}

.cancel-btn:hover {
  background: #e5e7eb;
}

.confirm-btn {
  background: #dc2626;
  color: white;
}

.confirm-btn:hover:not(:disabled) {
  background: #b91c1c;
}

.confirm-btn:disabled {
  background: #9ca3af;
  cursor: not-allowed;
}

.cancel-btn svg,
.confirm-btn svg {
  margin-right: 6px;
}

/* 加载动画 */
.loading-spinner {
  width: 16px;
  height: 16px;
  border: 2px solid transparent;
  border-top: 2px solid currentColor;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-right: 6px;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* ==================== 响应式设计 ==================== */
@media (max-width: 640px) {
  .delete-confirm-dialog {
    width: 95%;
    margin: 20px;
  }
  
  .dialog-header,
  .dialog-content,
  .dialog-footer {
    padding-left: 16px;
    padding-right: 16px;
  }
  
  .info-item {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .info-item .label {
    margin-bottom: 4px;
    margin-right: 0;
  }
}
</style>