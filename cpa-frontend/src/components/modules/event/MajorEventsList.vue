<!--
  MajorEventsList.vue - 重大事项列表页面
-->
<template>
  <div class="major-events-list">
    <!-- 页面头部 -->
    <div class="header">
      <div class="header-left">
        <!-- 返回按钮 -->
        <button class="back-btn" @click="goBack">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M19 12H5M12 19L5 12L12 5" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          返回
        </button>
        <div class="header-content">
          <h1>重大事项列表</h1>
          <p class="subtitle">查看和管理项目中的重大事项记录</p>
        </div>
      </div>
      <div class="header-actions">
        <!-- 模板按钮 -->
        <button class="template-btn" @click="navigateToTemplates">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M14 2H6C5.46957 2 4.96086 2.21071 4.58579 2.58579C4.21071 2.96086 4 3.46957 4 4V20C4 20.5304 4.21071 21.0391 4.58579 21.4142C4.96086 21.7893 5.46957 22 6 22H18C18.5304 22 19.0391 21.7893 19.4142 21.4142C19.7893 21.0391 20 20.5304 20 20V8L14 2Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M14 2V8H20" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          模板
        </button>
        <!-- 创建按钮 -->
        <button class="create-btn" @click="navigateToCreate">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M12 5V19M5 12H19" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          创建
        </button>
      </div>
    </div>

    <!-- 状态筛选标签页 -->
    <div class="status-tabs">
      <button 
        class="status-tab" 
        :class="{ active: activeStatusFilter === 'all' }"
        @click="setStatusFilter('all')"
      >
        全部
        <span class="count">{{ eventStore.eventCount }}</span>
      </button>
      <button 
        class="status-tab" 
        :class="{ active: activeStatusFilter === 'pending' }"
        @click="setStatusFilter('pending')"
      >
        未复核
        <span class="count">{{ eventStore.unReviewedEvents.length }}</span>
      </button>
      <button 
        class="status-tab" 
        :class="{ active: activeStatusFilter === 'reviewing' }"
        @click="setStatusFilter('reviewing')"
      >
        复核中
        <span class="count">{{ eventStore.reviewingEvents.length }}</span>
      </button>
      <button 
        class="status-tab" 
        :class="{ active: activeStatusFilter === 'reviewed' }"
        @click="setStatusFilter('reviewed')"
      >
        已复核
        <span class="count">{{ eventStore.reviewedEvents.length }}</span>
      </button>
    </div>

    <!-- 加载状态 -->
    <div class="loading-container" v-if="loading">
      <div class="loading-spinner"></div>
      <p>正在加载重大事项数据...</p>
    </div>

    <!-- 错误状态 -->
    <div class="error-container" v-if="error && !loading">
      <div class="error-icon">
        <svg width="48" height="48" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <circle cx="12" cy="12" r="10" stroke="#f56565" stroke-width="2"/>
          <path d="M15 9L9 15M9 9L15 15" stroke="#f56565" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </div>
      <h3>数据加载失败</h3>
      <p>{{ error }}</p>
      <div class="error-actions">
        <button class="retry-btn" @click="handleRetry">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M1 4V10H7" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M23 20V14H17" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M20.49 9A9 9 0 0 0 5.64 5.64L1 10M3.51 15A9 9 0 0 0 18.36 18.36L23 14" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          重新加载
        </button>
        <button class="check-network-btn" @click="checkNetworkStatus">
          检查网络连接
        </button>
        <button class="dismiss-btn" @click="clearError">
          关闭
        </button>
      </div>
    </div>

    <!-- 事项列表 -->
    <div class="events-container" v-if="!loading && !error">
      <!-- 空状态 -->
      <div class="empty-state" v-if="filteredEvents.length === 0">
        <div class="empty-icon">
          <svg width="64" height="64" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M19 3H5C3.9 3 3 3.9 3 5V19C3 20.1 3.9 21 5 21H19C20.1 21 21 20.1 21 19V5C21 3.9 20.1 3 19 3ZM19 19H5V8H19V19Z" fill="#e2e8f0"/>
          </svg>
        </div>
        <h3>{{ getEmptyStateTitle() }}</h3>
        <p>{{ getEmptyStateDescription() }}</p>
        <div class="empty-actions">
          <button class="template-btn" @click="navigateToTemplates">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M14 2H6C5.46957 2 4.96086 2.21071 4.58579 2.58579C4.21071 2.96086 4 3.46957 4 4V20C4 20.5304 4.21071 21.0391 4.58579 21.4142C4.96086 21.7893 5.46957 22 6 22H18C18.5304 22 19.0391 21.7893 19.4142 21.4142C19.7893 21.0391 20 20.5304 20 20V8L14 2Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M14 2V8H20" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            使用模板创建
          </button>
          <button class="create-btn" @click="navigateToCreate">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M12 5V19M5 12H19" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            直接创建
          </button>
        </div>
      </div>

      <!-- 事项列表 -->
      <div class="events-list" v-if="filteredEvents.length > 0">
        <div 
          class="event-item" 
          v-for="event in filteredEvents" 
          :key="event.id"
          @click="viewEventDetail(event)"
        >
          <div class="event-content">
            <div class="event-header">
              <h3 class="event-title">{{ event.title }}</h3>
              <span class="status-badge" :class="getStatusClass(event.status)">
                {{ getStatusText(event.status) }}
              </span>
            </div>
            <p class="event-description">{{ event.description }}</p>
            <div class="event-meta">
              <span class="meta-item">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2"/>
                  <polyline points="12,6 12,12 16,14" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
                最后更新：{{ formatDate(event.updatedAt) }}
              </span>
              <span class="meta-item">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M14 2H6C5.46957 2 4.96086 2.21071 4.58579 2.58579C4.21071 2.96086 4 3.46957 4 4V20C4 20.5304 4.21071 21.0391 4.58579 21.4142C4.96086 21.7893 5.46957 22 6 22H18C18.5304 22 19.0391 21.7893 19.4142 21.4142C19.7893 21.0391 20 20.5304 20 20V8L14 2Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  <path d="M14 2V8H20" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
                版本：{{ event.version }}
              </span>
            </div>
          </div>
          <div class="event-actions">
            <!-- 查看按钮 -->
            <button class="action-btn with-text" @click.stop="viewEventDetail(event)">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <circle cx="12" cy="12" r="3" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
              <span>查看</span>
            </button>
            <!-- 复核按钮 -->
            <button class="action-btn with-text" @click.stop="reviewEvent(event)">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M9 11l3 3L22 4" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M21 12v7a2 2 0 01-2 2H5a2 2 0 01-2-2V5a2 2 0 012-2h11" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
              <span>复核</span>
            </button>
            <!-- 编辑按钮 -->
            <button class="action-btn with-text" @click.stop="editEvent(event)">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M11 4H4a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M18.5 2.5a2.121 2.121 0 013 3L12 15l-4 1 1-4 9.5-9.5z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
              <span>编辑</span>
            </button>
            <!-- 版本按钮 -->
            <button class="action-btn with-text" @click.stop="viewVersions(event)">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M18 21v-8M12 21v-8M6 21v-8M3 7l9-4 9 4M3 7v2M21 9V7" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
              <span>版本</span>
            </button>
            <!-- 删除按钮 -->
            <button class="action-btn with-text delete-btn" @click.stop="deleteEvent(event)">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M3 6h18M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M10 11v6M14 11v6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
              <span>删除</span>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 刷新按钮 -->
    <div class="refresh-container" v-if="!loading">
      <button class="refresh-btn" @click="refreshData" :disabled="loading">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M1 4V10H7" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          <path d="M23 20V14H17" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          <path d="M20.49 9A9 9 0 0 0 5.64 5.64L1 10M3.51 15A9 9 0 0 0 18.36 18.36L23 14" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
        刷新列表
      </button>
    </div>

    <!-- 删除确认对话框 -->
     <DeleteConfirmDialog
       v-if="showDeleteDialog"
       :visible="showDeleteDialog"
       :event-data="deleteTargetEvent"
       :loading="deleteLoading"
       :is-first-time="isFirstTimeDelete"
       @confirm="handleDeleteConfirm"
       @cancel="handleDeleteCancel"
       @backup="handleBackup"
     />
  </div>
</template>

<script>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useEventStore } from '@/stores/event'
import DeleteConfirmDialog from '@/components/common/DeleteConfirmDialog.vue'

export default {
  name: 'MajorEventsList',
  
  components: {
    DeleteConfirmDialog
  },
  
  setup() {
    const router = useRouter()
    const eventStore = useEventStore()
    
    // ==================== 响应式数据 ====================
    
    // 当前激活的状态筛选器
    const activeStatusFilter = ref('all')
    
    // 网络状态检测
    const isOnline = ref(navigator.onLine)
    
    // 删除确认对话框相关
     const showDeleteDialog = ref(false)
     const deleteTargetEvent = ref(null)
     const deleteLoading = ref(false)
     const isFirstTimeDelete = ref(false)
    
    // ==================== 计算属性 ====================
    
    /**
     * 加载状态
     * 从store获取重大事项的加载状态
     */
    const loading = computed(() => eventStore.isMajorEventsLoading)
    
    /**
     * 错误状态
     * 从store获取错误信息
     */
    const error = computed(() => eventStore.error)
    
    /**
     * 根据当前状态筛选器过滤事项列表
     * 支持：全部、未复核、复核中、已复核
     */
    const filteredEvents = computed(() => {
      switch (activeStatusFilter.value) {
        case 'pending':
          return eventStore.unReviewedEvents
        case 'reviewing':
          return eventStore.reviewingEvents
        case 'reviewed':
          return eventStore.reviewedEvents
        case 'all':
        default:
          return eventStore.majorEvents
      }
    })
    
    // ==================== 导航方法 ====================
    
    /**
     * 返回重大事项管理主页面
     */
    const goBack = () => {
      router.push('/events/major-events')
    }
    
    /**
     * 导航到模板管理页面
     */
    const navigateToTemplates = () => {
      router.push('/events/major-events/templates')
    }
    
    /**
     * 导航到创建重大事项页面
     */
    const navigateToCreate = () => {
      router.push('/events/create-major-event')
    }
    
    /**
     * 查看事项详情
     * 执行状态检查：若事项处于"复核中"状态，显示确认对话框
     * 否则直接跳转到详情页面
     * @param {Object} event - 事项对象
     */
    const viewEventDetail = (event) => {
      // 状态检查：若选定的重大事项条目处于"复核中"状态
      if (event.status === 'reviewing') {
        // 显示确认对话框
        const userChoice = confirm(
          '该重大事项正在复核中，建议前往工作台查看实时进度。\n\n点击"确定"跳转到工作台，点击"取消"查看详情页面。'
        )
        
        if (userChoice) {
          // 用户选择"确定"：跳转到工作台界面
          router.push('/workbench')
        } else {
          // 用户选择"取消"：跳转到详情页面
          router.push(`/events/major-events/${event.id}`)
        }
      } else {
        // 若事项处于"未复核"或"已复核"状态，直接跳转到详情页面
        router.push(`/events/major-events/${event.id}`)
      }
    }
    
    /**
     * 复核事项
     * @param {Object} event - 事项对象
     */
    const reviewEvent = (event) => {
      // 导航到事项复核页面
      router.push(`/events/major-events/${event.id}/review`)
    }
    
    /**
     * 编辑事项
     * @param {Object} event - 事项对象
     */
    const editEvent = (event) => {
      // 导航到事项编辑页面
      router.push(`/events/major-events/${event.id}/edit`)
    }
    
    /**
     * 查看事项版本历史
     * @param {Object} event - 事项对象
     */
    const viewVersions = (event) => {
      // 导航到事项版本历史页面
      router.push(`/events/major-events/${event.id}/versions`)
    }
    
    /**
     * 删除事项 - 使用DeleteConfirmDialog组件
     * @param {Object} event - 事项对象
     */
    const deleteEvent = async (event) => {
      try {
        // 1. 状态检查：如果事项处于"复核中"状态，阻止删除
        if (event.status === 'reviewing') {
          alert('该重大事项正在复核中，暂不支持删除操作，建议前往工作台查看实时进度')
          return
        }
        
        // 2. 检查是否为首次删除并设置删除目标
         isFirstTimeDelete.value = await eventStore.isFirstTimeDelete()
         deleteTargetEvent.value = event
         showDeleteDialog.value = true
        
      } catch (error) {
        console.error('删除事项预处理失败:', error)
        alert(`删除操作失败：${error.message || '未知错误'}`)
      }
    }
    
    /**
     * 处理删除确认
     * @param {Object} confirmData - 确认数据，包含删除原因等
     */
    const handleDeleteConfirm = async (confirmData) => {
      try {
        deleteLoading.value = true
        
        // 检查是否为首次删除
        const isFirstTime = await eventStore.isFirstTimeDelete()
        
        // 执行删除操作
        await eventStore.deleteMajorEvent(
          deleteTargetEvent.value.id, 
          confirmData.deleteReason || '用户主动删除'
        )
        
        // 标记用户已执行过删除操作
        if (isFirstTime) {
          await eventStore.markUserHasDeleted()
        }
        
        // 关闭对话框
        showDeleteDialog.value = false
        deleteTargetEvent.value = null
        
        // 显示成功消息
        alert(`重大事项"${confirmData.eventData.title}"已成功删除`)
        
        console.log(`[MajorEventsList] 删除事项成功: ${confirmData.eventData.id} - ${confirmData.eventData.title}`)
        
      } catch (error) {
        console.error('[MajorEventsList] 删除事项失败:', error)
        
        // 根据错误类型提供不同的处理方案
        if (error.message && error.message.includes('reviewing')) {
          alert('该重大事项正在复核中，无法删除')
        } else if (error.message && (error.message.includes('网络') || error.message.includes('服务器'))) {
          // 网络或服务器错误，提供重试选项
          const retryConfirm = confirm(
            '删除操作失败，可能是网络连接问题或服务器暂时无响应。请检查网络连接后重试。\n\n是否要重试？'
          )
          
          if (retryConfirm) {
            // 用户选择重试，递归调用确认删除方法
            await handleDeleteConfirm({
              deleteReason: '用户主动删除（重试）',
              eventData: deleteTargetEvent.value
            })
          }
        } else {
          alert(`删除失败：${error.message || '未知错误'}`)
        }
      } finally {
        deleteLoading.value = false
      }
    }
    
    /**
     * 处理删除取消
     */
    const handleDeleteCancel = () => {
      showDeleteDialog.value = false
      deleteTargetEvent.value = null
      deleteLoading.value = false
    }
    
    /**
     * 处理备份操作（暂未实现）
     * @param {Object} eventData - 事项数据
     */
    const handleBackup = (eventData) => {
      alert('备份功能正在开发中，敬请期待')
      console.log('[MajorEventsList] 备份功能调用:', eventData)
    }
    
    /**
     * 检查是否为首次删除操作
     * @returns {Promise<boolean>} 是否为首次删除
     */
    const checkIsFirstTimeDelete = async () => {
      try {
        return await eventStore.isFirstTimeDelete()
      } catch (error) {
        console.error('[MajorEventsList] 检查首次删除状态失败:', error)
        return false
      }
    }
    
    // ==================== 筛选方法 ====================
    
    /**
     * 设置状态筛选器
     * @param {string} status - 状态值 ('all', 'pending', 'reviewing', 'reviewed')
     */
    const setStatusFilter = (status) => {
      activeStatusFilter.value = status
    }
    
    // ==================== 状态处理方法 ====================
    
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
     * 获取空状态标题
     * @returns {string} 空状态标题
     */
    const getEmptyStateTitle = () => {
      const titles = {
        'all': '暂无重大事项记录',
        'pending': '暂无未复核事项',
        'reviewing': '暂无复核中事项',
        'reviewed': '暂无已复核事项'
      }
      return titles[activeStatusFilter.value] || '暂无数据'
    }
    
    /**
     * 获取空状态描述
     * @returns {string} 空状态描述
     */
    const getEmptyStateDescription = () => {
      const descriptions = {
        'all': '您还没有创建任何重大事项记录',
        'pending': '当前没有需要复核的重大事项',
        'reviewing': '当前没有正在复核的重大事项',
        'reviewed': '当前没有已完成复核的重大事项'
      }
      return descriptions[activeStatusFilter.value] || '暂无相关数据'
    }
    
    // ==================== 工具方法 ====================
    
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
    
    // ==================== 数据操作方法 ====================
    
    /**
     * 刷新数据
     * 重新从服务器获取最新的重大事项数据
     */
    const refreshData = async () => {
      try {
        eventStore.clearError()
        await eventStore.reloadMajorEvents()
      } catch (error) {
        console.error('刷新数据失败:', error)
      }
    }
    
    /**
     * 处理重试按钮点击
     * 用于错误状态下的重新加载
     */
    const handleRetry = async () => {
      await eventStore.reloadMajorEvents()
    }

    /**
     * 清除错误状态
     */
    const clearError = () => {
      eventStore.clearError()
    }
    
    /**
     * 检查网络状态
     * 提供网络连接检查功能
     */
    const checkNetworkStatus = () => {
      if (navigator.onLine) {
        alert('网络连接正常，请尝试重新加载数据')
      } else {
        alert('网络连接异常，请检查您的网络设置')
      }
    }
    
    // ==================== 生命周期和监听 ====================
    
    /**
     * 组件挂载时初始化数据
     */
    onMounted(async () => {
      // 清除之前的错误状态
      eventStore.clearError()
      
      // 获取重大事项数据
      try {
        await eventStore.reloadMajorEvents()
      } catch (error) {
        console.error('初始化数据失败:', error)
      }
    })
    
    /**
     * 监听网络状态变化
     */
    const updateOnlineStatus = () => {
      isOnline.value = navigator.onLine
    }
    
    // 添加网络状态监听器
    window.addEventListener('online', updateOnlineStatus)
    window.addEventListener('offline', updateOnlineStatus)
    
    // ==================== 返回组件接口 ====================
    
    return {
      // Store实例
      eventStore,
      
      // 响应式数据
      activeStatusFilter,
      isOnline,
      showDeleteDialog,
       deleteTargetEvent,
       deleteLoading,
       isFirstTimeDelete,
      
      // 计算属性
      loading,
      error,
      filteredEvents,
      
      // 导航方法
      goBack,
      navigateToTemplates,
      navigateToCreate,
      viewEventDetail,
      
      // 事项操作方法
      reviewEvent,
      editEvent,
      viewVersions,
      deleteEvent,
      handleDeleteConfirm,
      handleDeleteCancel,
      handleBackup,
      checkIsFirstTimeDelete,
      
      // 筛选方法
      setStatusFilter,
      
      // 状态处理方法
      getStatusClass,
      getStatusText,
      getEmptyStateTitle,
      getEmptyStateDescription,
      
      // 工具方法
      formatDate,
      
      // 数据操作方法
      refreshData,
      handleRetry,
      clearError,
      checkNetworkStatus
    }
  }
}
</script>

<style scoped>
/* ==================== 主容器样式 ==================== */
.major-events-list {
  padding: 24px;
  max-width: 1200px;
  margin: 0 auto;
  min-height: calc(100vh - 100px);
}

/* ==================== 页面头部样式 ==================== */
.header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 32px;
  padding-bottom: 20px;
  border-bottom: 1px solid #e2e8f0;
}

.header-left {
  display: flex;
  align-items: flex-start;
  gap: 16px;
}

.back-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  background: #f7fafc;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
  color: #4a5568;
  font-size: 14px;
}

.back-btn:hover {
  background: #edf2f7;
  border-color: #cbd5e0;
}

.header-content h1 {
  font-size: 28px;
  font-weight: 600;
  color: #1a202c;
  margin: 0 0 4px 0;
}

.subtitle {
  font-size: 14px;
  color: #718096;
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.template-btn, .create-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 500;
  font-size: 14px;
  transition: all 0.2s ease;
}

.template-btn {
  background: #f7fafc;
  color: #4a5568;
  border: 1px solid #e2e8f0;
}

.template-btn:hover {
  background: #edf2f7;
  border-color: #cbd5e0;
}

.create-btn {
  background: #3182ce;
  color: white;
}

.create-btn:hover {
  background: #2c5aa0;
}

/* ==================== 状态筛选标签页样式 ==================== */
.status-tabs {
  display: flex;
  gap: 4px;
  margin-bottom: 32px;
  background: #f7fafc;
  padding: 4px;
  border-radius: 12px;
  border: 1px solid #e2e8f0;
}

.status-tab {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 20px;
  background: transparent;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 500;
  font-size: 14px;
  color: #4a5568;
  transition: all 0.2s ease;
  flex: 1;
  justify-content: center;
}

.status-tab:hover {
  background: #edf2f7;
}

.status-tab.active {
  background: white;
  color: #3182ce;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.status-tab .count {
  background: #e2e8f0;
  color: #4a5568;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
  min-width: 20px;
  text-align: center;
}

.status-tab.active .count {
  background: #bee3f8;
  color: #3182ce;
}

/* ==================== 加载和错误状态样式 ==================== */
.loading-container, .error-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  text-align: center;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid #e2e8f0;
  border-top: 3px solid #3182ce;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 16px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.loading-container p {
  color: #718096;
  font-size: 16px;
  margin: 0;
}

.error-container h3 {
  color: #e53e3e;
  font-size: 20px;
  margin: 16px 0 8px 0;
}

.error-container p {
  color: #718096;
  font-size: 14px;
  margin: 0 0 24px 0;
}

.error-actions {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  justify-content: center;
}

.retry-btn, .check-network-btn, .dismiss-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 500;
  font-size: 14px;
  transition: all 0.2s ease;
}

.retry-btn {
  background: #3182ce;
  color: white;
}

.retry-btn:hover {
  background: #2c5aa0;
}

.check-network-btn {
  background: #f7fafc;
  color: #4a5568;
  border: 1px solid #e2e8f0;
}

.check-network-btn:hover {
  background: #edf2f7;
}

.dismiss-btn {
  background: #f7fafc;
  color: #718096;
  border: 1px solid #e2e8f0;
}

.dismiss-btn:hover {
  background: #edf2f7;
  color: #4a5568;
}

/* ==================== 空状态样式 ==================== */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  text-align: center;
}

.empty-state h3 {
  color: #4a5568;
  font-size: 20px;
  margin: 16px 0 8px 0;
}

.empty-state p {
  color: #718096;
  font-size: 14px;
  margin: 0 0 32px 0;
}

.empty-actions {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  justify-content: center;
}

/* ==================== 事项列表样式 ==================== */
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
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.event-item:hover {
  border-color: #cbd5e0;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  transform: translateY(-1px);
}

.event-content {
  flex: 1;
}

.event-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
}

.event-title {
  font-size: 18px;
  font-weight: 600;
  color: #1a202c;
  margin: 0;
  flex: 1;
  margin-right: 16px;
}

.status-badge {
  padding: 4px 12px;
  border-radius: 16px;
  font-size: 12px;
  font-weight: 600;
  text-align: center;
  min-width: 60px;
}

/* 状态标签颜色 */
.status-pending {
  background: #f7fafc;
  color: #4a5568;
  border: 1px solid #e2e8f0;
}

.status-reviewing {
  background: #fffbeb;
  color: #d69e2e;
  border: 1px solid #fbd38d;
}

.status-reviewed {
  background: #f0fff4;
  color: #38a169;
  border: 1px solid #9ae6b4;
}

.event-description {
  color: #718096;
  font-size: 14px;
  line-height: 1.5;
  margin: 0 0 12px 0;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.event-meta {
  display: flex;
  gap: 24px;
  flex-wrap: wrap;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #718096;
  font-size: 12px;
}

.meta-item svg {
  color: #a0aec0;
}

.event-actions {
  margin-left: 16px;
  display: flex;
  gap: 8px;
}

.action-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  background: #f7fafc;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
  color: #4a5568;
}

.action-btn.with-text {
  width: auto;
  padding: 0 12px;
  gap: 6px;
}

.action-btn.with-text span {
  font-size: 14px;
  white-space: nowrap;
}

.action-btn:hover {
  background: #edf2f7;
  border-color: #cbd5e0;
}

/* 删除按钮特殊样式 */
.delete-btn {
  color: #e53e3e;
}

.delete-btn:hover {
  background: #fff5f5;
  border-color: #feb2b2;
}

/* ==================== 刷新按钮样式 ==================== */
.refresh-container {
  display: flex;
  justify-content: center;
  margin-top: 32px;
  padding-top: 24px;
  border-top: 1px solid #e2e8f0;
}

.refresh-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 24px;
  background: #f7fafc;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 500;
  font-size: 14px;
  color: #4a5568;
  transition: all 0.2s ease;
}

.refresh-btn:hover:not(:disabled) {
  background: #edf2f7;
  border-color: #cbd5e0;
}

.refresh-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* ==================== 响应式设计 ==================== */
@media (max-width: 768px) {
  .major-events-list {
    padding: 16px;
  }
  
  .header {
    flex-direction: column;
    gap: 16px;
    align-items: stretch;
  }
  
  .header-left {
    flex-direction: column;
    gap: 12px;
  }
  
  .header-actions {
    justify-content: stretch;
  }
  
  .template-btn, .create-btn {
    flex: 1;
    justify-content: center;
  }
  
  .status-tabs {
    flex-direction: column;
    gap: 2px;
  }
  
  .status-tab {
    justify-content: space-between;
    padding: 16px 20px;
  }
  
  .event-item {
    flex-direction: column;
    align-items: stretch;
    gap: 16px;
  }
  
  .event-header {
    flex-direction: column;
    align-items: stretch;
    gap: 8px;
  }
  
  .event-title {
    margin-right: 0;
  }
  
  .event-meta {
    gap: 16px;
  }
  
  .event-actions {
    margin-left: 0;
    align-self: flex-start;
    display: flex;
    flex-wrap: wrap;
    justify-content: flex-start;
    gap: 8px;
    margin-top: 12px;
    width: 100%;
  }
  
  .action-btn.with-text {
    flex: 1;
    min-width: 80px;
    justify-content: center;
  }
  
  .empty-actions {
    flex-direction: column;
    align-items: stretch;
    max-width: 200px;
  }
}

@media (max-width: 480px) {
  .major-events-list {
    padding: 12px;
  }
  
  .event-item {
    padding: 16px;
  }
  
  .event-title {
    font-size: 16px;
  }
  
  .event-meta {
    flex-direction: column;
    gap: 8px;
  }
}
</style>