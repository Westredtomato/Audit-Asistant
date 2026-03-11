<template>
  <div class="edit-major-event">
    <div class="header">
      <div class="header-left">
        <button class="back-btn" @click="goBack">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M19 12H5M12 19L5 12L12 5" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          返回
        </button>
        <h1>编辑重大事项</h1>
      </div>
      <div class="header-actions">
        <button class="action-btn secondary" @click="resetForm">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <polyline points="23 4 23 10 17 10" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <polyline points="1 20 1 14 7 14" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M20.49 9C20.0295 7.47079 19.1956 6.09637 18.0618 5.00365C16.9281 3.91093 15.5358 3.13616 14.0102 2.75C12.4846 2.36384 10.8851 2.38245 9.36772 2.80402C7.85034 3.22559 6.47203 4.03518 5.36772 5.15C4.26341 6.26482 3.47203 7.65034 3.06772 9.17402C2.66341 10.6977 2.66341 12.3023 3.06772 13.826C3.47203 15.3497 4.26341 16.7352 5.36772 17.85C6.47203 18.9648 7.85034 19.7744 9.36772 20.196" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          重置
        </button>
        <button class="action-btn primary" @click="saveEvent" :disabled="!isFormValid || saving">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" v-if="!saving">
            <path d="M19 21H5C4.46957 21 3.96086 20.7893 3.58579 20.4142C3.21071 20.0391 3 19.5304 3 19V5C3 4.46957 3.21071 3.96086 3.58579 3.58579C3.96086 3.21071 4.46957 3 5 3H16L21 8V19C21 19.5304 20.7893 20.0391 20.4142 20.4142C20.0391 20.7893 19.5304 21 19 21Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <polyline points="9,9 9,15 15,15 15,9" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          <div class="loading-spinner" v-if="saving"></div>
          {{ saving ? '保存中...' : '保存' }}
        </button>
      </div>
    </div>

    <!-- 加载状态 -->
    <div class="loading" v-if="loading">
      <div class="loading-spinner"></div>
      <p>加载中...</p>
    </div>

    <!-- 编辑表单 -->
    <div class="form-container" v-if="!loading">
      <form @submit.prevent="saveEvent" class="event-form">
        <!-- 基本信息 -->
        <div class="form-section">
          <div class="section-header">
            <h2>基本信息</h2>
            <span class="required-indicator">* 为必填项</span>
          </div>
          
          <div class="form-grid">
            <div class="form-group">
              <label for="title" class="required">事项标题</label>
              <input
                id="title"
                v-model="formData.title"
                type="text"
                placeholder="请输入事项标题"
                :class="{ error: errors.title }"
                @blur="validateField('title')"
              />
              <span class="error-message" v-if="errors.title">{{ errors.title }}</span>
            </div>
            
            <div class="form-group">
              <label for="type" class="required">事项类型</label>
              <select
                id="type"
                v-model="formData.type"
                :class="{ error: errors.type }"
                @change="validateField('type')"
              >
                <option value="">请选择事项类型</option>
                <option value="重大决策">重大决策</option>
                <option value="重大投资">重大投资</option>
                <option value="重大合作">重大合作</option>
                <option value="重大变更">重大变更</option>
                <option value="其他">其他</option>
              </select>
              <span class="error-message" v-if="errors.type">{{ errors.type }}</span>
            </div>
            
            <div class="form-group">
              <label for="priority" class="required">优先级</label>
              <select
                id="priority"
                v-model="formData.priority"
                :class="{ error: errors.priority }"
                @change="validateField('priority')"
              >
                <option value="">请选择优先级</option>
                <option value="高">高</option>
                <option value="中">中</option>
                <option value="低">低</option>
              </select>
              <span class="error-message" v-if="errors.priority">{{ errors.priority }}</span>
            </div>
            
            <div class="form-group">
              <label for="status" class="required">状态</label>
              <select
                id="status"
                v-model="formData.status"
                :class="{ error: errors.status }"
                @change="validateField('status')"
              >
                <option value="">请选择状态</option>
                <option value="进行中">进行中</option>
                <option value="已完成">已完成</option>
                <option value="已取消">已取消</option>
              </select>
              <span class="error-message" v-if="errors.status">{{ errors.status }}</span>
            </div>
            
            <div class="form-group">
              <label for="date" class="required">事项日期</label>
              <input
                id="date"
                v-model="formData.date"
                type="date"
                :class="{ error: errors.date }"
                @change="validateField('date')"
              />
              <span class="error-message" v-if="errors.date">{{ errors.date }}</span>
            </div>
          </div>
          
          <div class="form-group full-width">
            <label for="description">事项描述</label>
            <textarea
              id="description"
              v-model="formData.description"
              placeholder="请输入事项描述"
              rows="4"
              :class="{ error: errors.description }"
              @blur="validateField('description')"
            ></textarea>
            <span class="error-message" v-if="errors.description">{{ errors.description }}</span>
          </div>
        </div>

        <!-- 参与人员 -->
        <div class="form-section">
          <div class="section-header">
            <h2>参与人员</h2>
            <button type="button" class="add-btn" @click="addParticipant">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <line x1="12" y1="5" x2="12" y2="19" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <line x1="5" y1="12" x2="19" y2="12" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
              添加人员
            </button>
          </div>
          
          <div class="participants-list">
            <div class="participant-item" v-for="(participant, index) in formData.participants" :key="index">
              <input
                v-model="formData.participants[index]"
                type="text"
                placeholder="请输入参与人员姓名"
                class="participant-input"
              />
              <button type="button" class="remove-btn" @click="removeParticipant(index)">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <line x1="18" y1="6" x2="6" y2="18" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  <line x1="6" y1="6" x2="18" y2="18" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
              </button>
            </div>
            <div class="no-participants" v-if="formData.participants.length === 0">
              <p>暂无参与人员，点击上方按钮添加</p>
            </div>
          </div>
        </div>

        <!-- 附件管理 -->
        <div class="form-section">
          <div class="section-header">
            <h2>相关附件</h2>
            <button type="button" class="add-btn" @click="triggerFileUpload">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M21 15V19C21 20.1 20.1 21 19 21H5C3.9 21 3 20.1 3 19V15M17 8L12 3L7 8M12 3V15" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
              上传附件
            </button>
          </div>
          
          <input
            ref="fileInput"
            type="file"
            multiple
            @change="handleFileUpload"
            style="display: none;"
            accept=".pdf,.doc,.docx,.xls,.xlsx,.ppt,.pptx,.txt,.jpg,.jpeg,.png,.gif"
          />
          
          <div class="attachments-list">
            <div class="attachment-item" v-for="(attachment, index) in formData.attachments" :key="index">
              <div class="attachment-icon">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M14 2H6C5.46957 2 4.96086 2.21071 4.58579 2.58579C4.21071 2.96086 4 3.46957 4 4V20C4 20.5304 4.21071 21.0391 4.58579 21.4142C4.96086 21.7893 5.46957 22 6 22H18C18.5304 22 19.0391 21.7893 19.4142 21.4142C19.7893 21.0391 20 20.5304 20 20V8L14 2Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  <polyline points="14,2 14,8 20,8" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
              </div>
              <div class="attachment-info">
                <span class="attachment-name">{{ attachment.name || attachment }}</span>
                <span class="attachment-size" v-if="attachment.size">{{ formatFileSize(attachment.size) }}</span>
              </div>
              <div class="attachment-actions">
                <button type="button" class="attachment-btn" @click="previewAttachment(attachment)" v-if="canPreview(attachment)">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M1 12S5 4 12 4S23 12 23 12S19 20 12 20S1 12 1 12Z" stroke="currentColor" stroke-width="2"/>
                    <circle cx="12" cy="12" r="3" stroke="currentColor" stroke-width="2"/>
                  </svg>
                  预览
                </button>
                <button type="button" class="attachment-btn remove" @click="removeAttachment(index)">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <line x1="18" y1="6" x2="6" y2="18" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    <line x1="6" y1="6" x2="18" y2="18" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  </svg>
                  删除
                </button>
              </div>
            </div>
            <div class="no-attachments" v-if="formData.attachments.length === 0">
              <p>暂无附件，点击上方按钮上传</p>
            </div>
          </div>
        </div>

        <!-- 变更记录 -->
        <div class="form-section" v-if="changeHistory.length > 0">
          <div class="section-header">
            <h2>变更记录</h2>
            <span class="count-badge">{{ changeHistory.length }}条记录</span>
          </div>
          
          <div class="change-history">
            <div class="change-item" v-for="change in changeHistory" :key="change.id">
              <div class="change-time">{{ formatDateTime(change.timestamp) }}</div>
              <div class="change-content">
                <span class="change-user">{{ change.user }}</span>
                <span class="change-action">{{ change.action }}</span>
                <div class="change-details" v-if="change.details">
                  <div class="change-field" v-for="detail in change.details" :key="detail.field">
                    <strong>{{ detail.field }}:</strong>
                    <span class="old-value">{{ detail.oldValue }}</span>
                    <span class="arrow">→</span>
                    <span class="new-value">{{ detail.newValue }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </form>
    </div>

    <!-- 错误状态 -->
    <div class="error-state" v-if="!loading && !originalEvent">
      <svg width="64" height="64" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2"/>
        <line x1="15" y1="9" x2="9" y2="15" stroke="currentColor" stroke-width="2"/>
        <line x1="9" y1="9" x2="15" y2="15" stroke="currentColor" stroke-width="2"/>
      </svg>
      <h3>事项不存在</h3>
      <p>您要编辑的重大事项不存在或已被删除</p>
      <button class="back-btn" @click="goBack">返回列表</button>
    </div>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useEventStore } from '@/stores/event'

export default {
  name: 'EditMajorEvent',
  setup() {
    const route = useRoute()
    const router = useRouter()
    const eventStore = useEventStore()
    
    // 响应式数据
    const loading = ref(true)
    const saving = ref(false)
    const fileInput = ref(null)
    const originalEvent = ref(null)
    const changeHistory = ref([])
    
    // 表单数据
    const formData = reactive({
      title: '',
      type: '',
      priority: '',
      status: '',
      date: '',
      description: '',
      participants: [],
      attachments: []
    })
    
    // 表单验证错误
    const errors = reactive({
      title: '',
      type: '',
      priority: '',
      status: '',
      date: '',
      description: ''
    })
    
    // 计算属性
    const isFormValid = computed(() => {
      return formData.title.trim() &&
             formData.type &&
             formData.priority &&
             formData.status &&
             formData.date &&
             !Object.values(errors).some(error => error)
    })
    
    // 验证方法
    const validateField = (field) => {
      errors[field] = ''
      
      switch (field) {
        case 'title':
          if (!formData.title.trim()) {
            errors.title = '请输入事项标题'
          } else if (formData.title.length > 100) {
            errors.title = '标题长度不能超过100个字符'
          }
          break
        case 'type':
          if (!formData.type) {
            errors.type = '请选择事项类型'
          }
          break
        case 'priority':
          if (!formData.priority) {
            errors.priority = '请选择优先级'
          }
          break
        case 'status':
          if (!formData.status) {
            errors.status = '请选择状态'
          }
          break
        case 'date':
          if (!formData.date) {
            errors.date = '请选择事项日期'
          }
          break
        case 'description':
          if (formData.description && formData.description.length > 1000) {
            errors.description = '描述长度不能超过1000个字符'
          }
          break
      }
    }
    
    const validateForm = () => {
      Object.keys(errors).forEach(field => {
        validateField(field)
      })
      return isFormValid.value
    }
    
    // 表单操作方法
    const resetForm = () => {
      if (originalEvent.value) {
        Object.assign(formData, {
          title: originalEvent.value.title || '',
          type: originalEvent.value.type || '',
          priority: originalEvent.value.priority || '',
          status: originalEvent.value.status || '',
          date: originalEvent.value.date || '',
          description: originalEvent.value.description || '',
          participants: [...(originalEvent.value.participants || [])],
          attachments: [...(originalEvent.value.attachments || [])]
        })
        
        // 清除错误信息
        Object.keys(errors).forEach(key => {
          errors[key] = ''
        })
      }
    }
    
    const saveEvent = async () => {
      if (!validateForm()) {
        return
      }
      
      saving.value = true
      try {
        const eventData = {
          ...formData,
          id: originalEvent.value.id,
          updatedAt: new Date().toISOString()
        }
        
        // TODO: 调用store方法更新事项
        await eventStore.updateMajorEvent(eventData)
        
        // 跳转到详情页
        router.push(`/events/major-event/${originalEvent.value.id}`)
      } catch (error) {
        console.error('保存失败:', error)
        // TODO: 显示错误提示
      } finally {
        saving.value = false
      }
    }
    
    // 参与人员管理
    const addParticipant = () => {
      formData.participants.push('')
    }
    
    const removeParticipant = (index) => {
      formData.participants.splice(index, 1)
    }
    
    // 附件管理
    const triggerFileUpload = () => {
      fileInput.value?.click()
    }
    
    const handleFileUpload = (event) => {
      const files = Array.from(event.target.files)
      files.forEach(file => {
        formData.attachments.push({
          name: file.name,
          size: file.size,
          type: file.type,
          file: file
        })
      })
      
      // 清空input
      event.target.value = ''
    }
    
    const removeAttachment = (index) => {
      formData.attachments.splice(index, 1)
    }
    
    const previewAttachment = (attachment) => {
      // TODO: 实现文件预览逻辑
      console.log('预览文件:', attachment)
    }
    
    const canPreview = (attachment) => {
      const previewableTypes = ['image/jpeg', 'image/png', 'image/gif', 'application/pdf']
      return previewableTypes.includes(attachment.type)
    }
    
    // 工具方法
    const formatFileSize = (bytes) => {
      if (bytes === 0) return '0 Bytes'
      const k = 1024
      const sizes = ['Bytes', 'KB', 'MB', 'GB']
      const i = Math.floor(Math.log(bytes) / Math.log(k))
      return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
    }
    
    const formatDateTime = (dateString) => {
      const date = new Date(dateString)
      return date.toLocaleString('zh-CN')
    }
    
    const goBack = () => {
      router.push('/events/major-events')
    }
    
    // 加载事项数据
    const loadEventData = async () => {
      loading.value = true
      try {
        const eventId = parseInt(route.params.id)
        
        // 确保事项数据已加载
        if (eventStore.majorEvents.length === 0) {
          await eventStore.fetchMajorEvents()
        }
        
        // 查找要编辑的事项
        const event = eventStore.majorEvents.find(e => e.id === eventId)
        if (event) {
          originalEvent.value = event
          
          // 填充表单数据
          Object.assign(formData, {
            title: event.title || '',
            type: event.type || '',
            priority: event.priority || '',
            status: event.status || '',
            date: event.date || '',
            description: event.description || '',
            participants: [...(event.participants || [])],
            attachments: [...(event.attachments || [])]
          })
          
          // TODO: 加载变更记录
          changeHistory.value = [
            {
              id: 1,
              timestamp: new Date().toISOString(),
              user: '张三',
              action: '创建了事项',
              details: []
            }
          ]
        }
      } catch (error) {
        console.error('加载事项数据失败:', error)
      } finally {
        loading.value = false
      }
    }
    
    // 监听表单变化，记录变更
    watch(
      () => ({ ...formData }),
      (newData, oldData) => {
        if (originalEvent.value && oldData) {
          // TODO: 记录字段变更
        }
      },
      { deep: true }
    )
    
    // 生命周期
    onMounted(() => {
      loadEventData()
    })
    
    return {
      // 数据
      loading,
      saving,
      fileInput,
      originalEvent,
      changeHistory,
      formData,
      errors,
      
      // 计算属性
      isFormValid,
      
      // 方法
      validateField,
      validateForm,
      resetForm,
      saveEvent,
      addParticipant,
      removeParticipant,
      triggerFileUpload,
      handleFileUpload,
      removeAttachment,
      previewAttachment,
      canPreview,
      formatFileSize,
      formatDateTime,
      goBack
    }
  }
}
</script>

<style scoped>
.edit-major-event {
  padding: 24px;
  max-width: 1000px;
  margin: 0 auto;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 32px;
  padding-bottom: 16px;
  border-bottom: 1px solid #e0e0e0;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.back-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: #f5f5f5;
  border: 1px solid #ddd;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
}

.back-btn:hover {
  background: #e0e0e0;
}

.header h1 {
  font-size: 28px;
  font-weight: 600;
  color: #1a1a1a;
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  border: 1px solid #ddd;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 14px;
}

.action-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.action-btn.secondary {
  background: white;
  color: #666;
}

.action-btn.secondary:hover:not(:disabled) {
  background: #f0f0f0;
}

.action-btn.primary {
  background: #1976d2;
  color: white;
  border-color: #1976d2;
}

.action-btn.primary:hover:not(:disabled) {
  background: #1565c0;
}

.loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px;
  color: #666;
}

.loading-spinner {
  width: 20px;
  height: 20px;
  border: 2px solid #f3f3f3;
  border-top: 2px solid #1976d2;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.form-container {
  background: white;
}

.event-form {
  display: flex;
  flex-direction: column;
  gap: 32px;
}

.form-section {
  background: white;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  overflow: hidden;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  background: #f8f9fa;
  border-bottom: 1px solid #e0e0e0;
}

.section-header h2 {
  font-size: 18px;
  font-weight: 600;
  color: #1a1a1a;
  margin: 0;
}

.required-indicator {
  font-size: 12px;
  color: #666;
}

.add-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 6px 12px;
  background: #1976d2;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  transition: all 0.2s;
}

.add-btn:hover {
  background: #1565c0;
}

.count-badge {
  background: #e3f2fd;
  color: #1976d2;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  padding: 24px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.form-group.full-width {
  grid-column: 1 / -1;
  padding: 0 24px 24px;
}

.form-group label {
  font-size: 14px;
  font-weight: 500;
  color: #333;
}

.form-group label.required::after {
  content: ' *';
  color: #d32f2f;
}

.form-group input,
.form-group select,
.form-group textarea {
  padding: 10px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  transition: border-color 0.2s;
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #1976d2;
}

.form-group input.error,
.form-group select.error,
.form-group textarea.error {
  border-color: #d32f2f;
}

.error-message {
  font-size: 12px;
  color: #d32f2f;
}

.participants-list {
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.participant-item {
  display: flex;
  gap: 8px;
  align-items: center;
}

.participant-input {
  flex: 1;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.remove-btn {
  padding: 6px;
  background: #ffebee;
  color: #d32f2f;
  border: 1px solid #ffcdd2;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;
}

.remove-btn:hover {
  background: #d32f2f;
  color: white;
}

.no-participants,
.no-attachments {
  text-align: center;
  padding: 20px;
  color: #666;
  font-style: italic;
}

.attachments-list {
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.attachment-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: #f8f9fa;
  border-radius: 6px;
  transition: background 0.2s;
}

.attachment-item:hover {
  background: #e3f2fd;
}

.attachment-icon {
  color: #1976d2;
}

.attachment-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.attachment-name {
  font-size: 14px;
  font-weight: 500;
  color: #333;
}

.attachment-size {
  font-size: 12px;
  color: #666;
}

.attachment-actions {
  display: flex;
  gap: 8px;
}

.attachment-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 4px 8px;
  background: white;
  border: 1px solid #ddd;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  transition: all 0.2s;
}

.attachment-btn:hover {
  background: #1976d2;
  color: white;
  border-color: #1976d2;
}

.attachment-btn.remove {
  color: #d32f2f;
  border-color: #d32f2f;
}

.attachment-btn.remove:hover {
  background: #d32f2f;
  color: white;
}

.change-history {
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.change-item {
  display: flex;
  gap: 12px;
  padding: 16px;
  background: #f8f9fa;
  border-radius: 6px;
  border-left: 3px solid #1976d2;
}

.change-time {
  font-size: 12px;
  color: #666;
  white-space: nowrap;
  min-width: 120px;
}

.change-content {
  flex: 1;
}

.change-user {
  font-weight: 500;
  color: #1976d2;
}

.change-action {
  color: #333;
  margin-left: 4px;
}

.change-details {
  margin-top: 8px;
  padding-top: 8px;
  border-top: 1px solid #e0e0e0;
}

.change-field {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 4px;
  font-size: 12px;
}

.old-value {
  color: #d32f2f;
  text-decoration: line-through;
}

.arrow {
  color: #666;
}

.new-value {
  color: #388e3c;
  font-weight: 500;
}

.error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  text-align: center;
  color: #666;
}

.error-state svg {
  margin-bottom: 16px;
  color: #d32f2f;
}

.error-state h3 {
  font-size: 18px;
  margin: 0 0 8px 0;
  color: #333;
}

.error-state p {
  margin: 0 0 24px 0;
  font-size: 14px;
}

@media (max-width: 768px) {
  .edit-major-event {
    padding: 16px;
  }
  
  .header {
    flex-direction: column;
    gap: 16px;
    align-items: stretch;
  }
  
  .header-actions {
    justify-content: space-between;
  }
  
  .form-grid {
    grid-template-columns: 1fr;
  }
  
  .participant-item {
    flex-direction: column;
    align-items: stretch;
    gap: 8px;
  }
  
  .attachment-item {
    flex-direction: column;
    align-items: stretch;
    gap: 8px;
  }
  
  .attachment-actions {
    justify-content: center;
  }
  
  .change-item {
    flex-direction: column;
    gap: 8px;
  }
  
  .change-time {
    min-width: auto;
  }
}
</style>