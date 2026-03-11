<template>
  <div class="major-event-detail">
    <!-- 页面头部 -->
    <div class="header">
      <div class="header-left">
        <button class="back-btn" @click="goBack">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M19 12H5M12 19L5 12L12 5" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          返回
        </button>
        <h1>重大事项详情</h1>
      </div>
    </div>

    <!-- 加载状态 -->
    <div class="loading" v-if="loading">
      <div class="loading-spinner"></div>
      <p>加载中...</p>
    </div>

    <!-- 错误状态 -->
    <div class="error-state" v-if="!loading && error">
      <div class="error-icon">
        <svg width="64" height="64" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <circle cx="12" cy="12" r="10" stroke="#ef4444" stroke-width="2"/>
          <line x1="15" y1="9" x2="9" y2="15" stroke="#ef4444" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          <line x1="9" y1="9" x2="15" y2="15" stroke="#ef4444" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </div>
      <h3>加载失败</h3>
      <p>{{ error }}</p>
      <div class="error-actions">
        <button class="retry-btn" @click="loadEventDetail">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M1 4V10H7" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M23 20V14H17" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M20.49 9A9 9 0 0 0 5.64 5.64L1 10M3.51 15A9 9 0 0 0 18.36 18.36L23 14" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          重新加载
        </button>
        <button class="back-btn-error" @click="goBack">
          返回列表
        </button>
      </div>
    </div>

    <!-- 事项详情内容 -->
    <div class="detail-content" v-if="!loading && !error && eventDetail">
      <!-- 模块1: 重大事项标题 -->
      <div class="info-card title-card">
        <div class="card-content">
          <h2 class="event-title">{{ eventDetail.title }}</h2>
        </div>
      </div>

      <!-- 模块2: 版本信息 -->
      <div class="info-card version-card">
        <div class="card-header">
          <h3>版本信息</h3>
        </div>
        <div class="card-content">
          <div class="version-info">
            <span class="version-label">当前版本:</span>
            <span class="version-number">{{ eventDetail.version }}</span>
          </div>
        </div>
      </div>

      <!-- 模块3: 状态 -->
      <div class="info-card status-card">
        <div class="card-header">
          <h3>复核状态</h3>
        </div>
        <div class="card-content">
          <div class="status-display">
            <span class="status-badge" :class="getStatusClass(eventDetail.status)">
              {{ getStatusText(eventDetail.status) }}
            </span>
          </div>
        </div>
      </div>

      <!-- 模块4: 重大事项内容与复核设置 -->
      <div class="info-card content-settings-card">
        <div class="card-header">
          <h3>重大事项内容与复核设置</h3>
          <button class="toggle-btn" @click="toggleContentExpanded">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path :d="contentExpanded ? 'M18 15L12 9L6 15' : 'M6 9L12 15L18 9'" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            {{ contentExpanded ? '收起' : '展开' }}
          </button>
        </div>
        <div class="card-content" v-show="contentExpanded">
          <!-- 创建时间 -->
          <div class="info-section">
            <label class="section-label">创建时间</label>
            <div class="section-content">
              {{ formatDateTime(eventDetail.createdAt) }}
            </div>
          </div>

          <!-- 重大事项概述 -->
          <div class="info-section" v-if="reviewSettings">
            <label class="section-label">重大事项概述</label>
            <div class="section-content expandable-content">
              <div class="content-text" :class="{ 'expanded': overviewExpanded }">
                {{ reviewSettings['重大事项概述'] }}
              </div>
              <button class="expand-btn" @click="overviewExpanded = !overviewExpanded" v-if="isContentLong(reviewSettings['重大事项概述'])">
                {{ overviewExpanded ? '收起' : '展开' }}
              </button>
            </div>
          </div>

          <!-- 审计目标 -->
          <div class="info-section" v-if="reviewSettings">
            <label class="section-label">审计目标</label>
            <div class="section-content expandable-content">
              <div class="content-text" :class="{ 'expanded': objectiveExpanded }">
                {{ reviewSettings['审计目标'] }}
              </div>
              <button class="expand-btn" @click="objectiveExpanded = !objectiveExpanded" v-if="isContentLong(reviewSettings['审计目标'])">
                {{ objectiveExpanded ? '收起' : '展开' }}
              </button>
            </div>
          </div>

          <!-- 审计证据标准 -->
          <div class="info-section" v-if="reviewSettings && reviewSettings['审计证据标准']">
            <label class="section-label">审计证据标准</label>
            <div class="section-content">
              <div class="evidence-standards">
                <div class="evidence-situation" v-for="(situation, key) in filteredEvidenceStandards" :key="key">
                  <h4 class="situation-title">{{ key }}</h4>
                  <div class="situation-content">
                    <div class="conclusion">
                      <strong>审计结论:</strong>
                      <p>{{ situation['审计结论'] }}</p>
                    </div>
                    <div class="criteria" v-if="situation['充分、适当评判标准']">
                      <strong>充分、适当评判标准:</strong>
                      <p>{{ situation['充分、适当评判标准'] }}</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 模块5: 重大事项复核结果 -->
      <div class="info-card review-results-card">
        <div class="card-header">
          <h3>重大事项复核结果</h3>
          <button class="toggle-btn" @click="toggleResultsExpanded">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path :d="resultsExpanded ? 'M18 15L12 9L6 15' : 'M6 9L12 15L18 9'" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            {{ resultsExpanded ? '收起' : '展开' }}
          </button>
        </div>
        <div class="card-content" v-show="resultsExpanded">
          <!-- 未复核状态 -->
          <div class="empty-results" v-if="eventDetail.status === 'pending'">
            <svg width="48" height="48" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2"/>
              <path d="M12 6V12L16 14" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            <p>暂无复核结果，请先执行复核操作</p>
          </div>

          <!-- 复核中状态 -->
          <div class="reviewing-results" v-else-if="eventDetail.status === 'reviewing'">
            <svg width="48" height="48" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2"/>
              <path d="M12 6V12L16 14" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            <p>复核正在进行中，请前往工作台查看实时进度</p>
            <button class="workbench-btn" @click="goToWorkbench">
              前往工作台
            </button>
          </div>

          <!-- 已复核状态 -->
          <div class="completed-results" v-else-if="eventDetail.status === 'reviewed' && reviewResults">
            <!-- 复核时间 -->
            <div class="info-section">
              <label class="section-label">复核时间</label>
              <div class="section-content">
                {{ reviewResults['复核时间'] }}
              </div>
            </div>

            <!-- 复核结果明细 -->
            <div class="info-section">
              <label class="section-label">复核结果明细</label>
              <div class="section-content">
                <div class="result-details">
                  <div class="result-item">
                    <strong>审计结论:</strong>
                    <p>{{ reviewResults['审计结论'] }}</p>
                  </div>
                  <div class="result-item" v-if="reviewResults['复核结果明细']">
                    <strong>统计整理:</strong>
                    <p>{{ reviewResults['复核结果明细']['统计整理'] }}</p>
                  </div>
                  <div class="result-item" v-if="reviewResults['复核结果明细']">
                    <strong>结论与原因:</strong>
                    <p>{{ reviewResults['复核结果明细']['结论与原因'] }}</p>
                  </div>
                  <div class="result-item" v-if="reviewResults['复核人员']">
                    <strong>复核人员:</strong>
                    <p>{{ reviewResults['复核人员'] }}</p>
                  </div>
                </div>
              </div>
            </div>

            <!-- 复核日志入口 -->
            <div class="info-section">
              <label class="section-label">复核日志</label>
              <div class="section-content">
                <button class="log-entry-btn" @click="viewReviewLogs" disabled>
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M14 2H6C5.46957 2 4.96086 2.21071 4.58579 2.58579C4.21071 2.96086 4 3.46957 4 4V20C4 20.5304 4.21071 21.0391 4.58579 21.4142C4.96086 21.7893 5.46957 22 6 22H18C18.5304 22 19.0391 21.7893 19.4142 21.4142C19.7893 21.0391 20 20.5304 20 20V8L14 2Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    <polyline points="14,2 14,8 20,8" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  </svg>
                  查看复核日志
                  <span class="coming-soon">(功能开发中)</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 确认对话框 -->
    <div class="dialog-overlay" v-if="showConfirmDialog" @click="closeConfirmDialog">
      <div class="confirm-dialog" @click.stop>
        <div class="dialog-header">
          <h3>提示</h3>
          <button class="close-btn" @click="closeConfirmDialog">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <line x1="18" y1="6" x2="6" y2="18" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <line x1="6" y1="6" x2="18" y2="18" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </button>
        </div>
        <div class="dialog-content">
          <p>该重大事项正在复核中，建议前往工作台查看实时进度</p>
        </div>
        <div class="dialog-actions">
          <button class="cancel-btn" @click="closeConfirmDialog">取消</button>
          <button class="confirm-btn" @click="goToWorkbench">前往工作台</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useEventStore } from '@/stores/event'

export default {
  name: 'MajorEventDetail',
  setup() {
    const route = useRoute()
    const router = useRouter()
    const eventStore = useEventStore()
    
    // 响应式数据
    const loading = ref(true)
    const error = ref('')
    const eventDetail = ref(null)
    const reviewSettings = ref(null)
    const reviewResults = ref(null)
    const showConfirmDialog = ref(false)
    
    // 展开/收起状态
    const contentExpanded = ref(true)
    const resultsExpanded = ref(true)
    const overviewExpanded = ref(false)
    const objectiveExpanded = ref(false)
    
    // 计算属性
    const eventId = computed(() => route.params.id)
    
    // 过滤审计证据标准，排除'标准制定依据'
    const filteredEvidenceStandards = computed(() => {
      if (!reviewSettings.value || !reviewSettings.value['审计证据标准']) {
        return {}
      }
      const standards = reviewSettings.value['审计证据标准']
      const filtered = {}
      for (const [key, value] of Object.entries(standards)) {
        if (key !== '标准制定依据') {
          filtered[key] = value
        }
      }
      return filtered
    })
    
    // 方法
    
    /**
     * 返回上一页
     */
    const goBack = () => {
      router.push('/events/major-events/list')
    }
    
    /**
     * 前往工作台
     */
    const goToWorkbench = () => {
      closeConfirmDialog()
      router.push('/workbench')
    }
    
    /**
     * 关闭确认对话框
     */
    const closeConfirmDialog = () => {
      showConfirmDialog.value = false
    }
    
    /**
     * 获取状态样式类
     * @param {string} status - 状态值
     * @returns {string} 样式类名
     */
    const getStatusClass = (status) => {
      const statusMap = {
        'pending': 'status-pending',
        'reviewing': 'status-reviewing', 
        'reviewed': 'status-reviewed'
      }
      return statusMap[status] || 'status-unknown'
    }
    
    /**
     * 获取状态显示文本
     * @param {string} status - 状态值
     * @returns {string} 显示文本
     */
    const getStatusText = (status) => {
      const statusMap = {
        'pending': '未复核',
        'reviewing': '复核中',
        'reviewed': '已复核'
      }
      return statusMap[status] || '未知状态'
    }
    
    /**
     * 格式化日期时间
     * @param {string} dateString - 日期字符串
     * @returns {string} 格式化后的日期时间
     */
    const formatDateTime = (dateString) => {
      if (!dateString) return ''
      const date = new Date(dateString)
      return date.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
      })
    }
    
    /**
     * 判断内容是否过长需要展开/收起功能
     * @param {string} content - 内容文本
     * @returns {boolean} 是否需要展开功能
     */
    const isContentLong = (content) => {
      return content && content.length > 100
    }
    
    /**
     * 切换内容展开状态
     */
    const toggleContentExpanded = () => {
      contentExpanded.value = !contentExpanded.value
    }
    
    /**
     * 切换结果展开状态
     */
    const toggleResultsExpanded = () => {
      resultsExpanded.value = !resultsExpanded.value
    }
    
    /**
     * 查看复核日志（预留功能）
     */
    const viewReviewLogs = () => {
      // TODO: 实现复核日志查看功能
      console.log('查看复核日志功能开发中')
    }
    
    /**
     * 处理超链接点击事件
     * 在侧边栏或新窗口中展示文档详情
     * @param {Event} event - 点击事件
     * @param {string} docUrl - 文档链接
     */
    const handleLinkClick = (event, docUrl) => {
      event.preventDefault()
      
      try {
        // 检查文档链接是否有效
        if (!docUrl || docUrl.trim() === '') {
          throw new Error('文档链接无效')
        }
        
        // 记录访问日志
        console.log(`[MajorEventDetail] 访问文档: ${docUrl}`)
        
        // 检查文档是否存在（模拟检查）
        if (docUrl.includes('deleted') || docUrl.includes('not-found')) {
          throw new Error('文档不存在')
        }
        
        // TODO: 实现侧边栏文档详情展示功能
        // 当前暂时在新窗口打开
        window.open(docUrl, '_blank')
        
      } catch (err) {
        console.error('文档访问失败:', err)
        
        if (err.message.includes('不存在')) {
          alert('文档不存在或已被删除')
          // 记录访问日志
          console.log(`[MajorEventDetail] 文档访问失败 - 文档不存在: ${docUrl}`)
        } else {
          alert(`文档访问失败: ${err.message}`)
        }
      }
    }
    
    /**
     * 切换概述展开状态
     */
    const toggleOverviewExpanded = () => {
      overviewExpanded.value = !overviewExpanded.value
    }
    
    /**
     * 切换目标展开状态
     */
    const toggleObjectiveExpanded = () => {
      objectiveExpanded.value = !objectiveExpanded.value
    }
    
    /**
     * 加载事项详情数据
     * 包含完整的异常情况处理
     */
    const loadEventDetail = async () => {
      loading.value = true
      error.value = ''
      
      try {
        // 检查网络连接状态
        if (!navigator.onLine) {
          throw new Error('网络连接已断开，请检查网络连接后重试')
        }
        
        // 获取事项基本信息
        eventDetail.value = await eventStore.fetchMajorEventDetail(eventId.value)
        
        // 检查事项是否存在
        if (!eventDetail.value) {
          throw new Error('重大事项不存在或已被删除')
        }
        
        // 获取复核设置
        reviewSettings.value = await eventStore.fetchMajorEventReviewSettings(eventId.value)
        
        // 获取复核结果（仅已复核状态）
        if (eventDetail.value.status === 'reviewed') {
          try {
            reviewResults.value = await eventStore.fetchMajorEventReviewResults(eventId.value)
          } catch (resultErr) {
            console.warn('复核结果加载失败:', resultErr)
            // 复核结果加载失败不影响主要内容显示
            reviewResults.value = null
          }
        }
        
      } catch (err) {
        console.error('加载事项详情失败:', err)
        
        // 根据错误类型提供不同的错误信息
        if (err.message.includes('网络')) {
          error.value = '网络连接异常，请检查网络连接或稍后再试'
        } else if (err.message.includes('服务器')) {
          error.value = '服务器暂时无响应，请稍后再试'
        } else if (err.message.includes('不存在')) {
          error.value = '重大事项不存在或已被删除'
        } else if (err.message.includes('权限')) {
          error.value = '您没有权限查看此重大事项'
        } else if (err.message.includes('格式异常')) {
          error.value = '底稿文件访问异常，请联系系统管理员'
        } else if (err.message.includes('数据异常')) {
          error.value = '数据存在异常，请联系技术支持'
        } else {
          error.value = err.message || '加载事项详情失败，请稍后重试'
        }
      } finally {
        loading.value = false
      }
    }
    
    /**
     * 检查状态并显示确认对话框（从列表页面进入时）
     */
    const checkStatusAndShowDialog = () => {
      // 如果是从列表页面跳转过来且状态为复核中，显示确认对话框
      const fromList = route.query.from === 'list'
      if (fromList && eventDetail.value && eventDetail.value.status === 'reviewing') {
        showConfirmDialog.value = true
      }
    }
    
    // 生命周期
    onMounted(async () => {
      await loadEventDetail()
      // 加载完成后检查是否需要显示确认对话框
      nextTick(() => {
        checkStatusAndShowDialog()
      })
    })
    
    return {
      // 数据
      loading,
      error,
      eventDetail,
      reviewSettings,
      reviewResults,
      showConfirmDialog,
      contentExpanded,
      resultsExpanded,
      overviewExpanded,
      objectiveExpanded,
      
      // 计算属性
      filteredEvidenceStandards,
      
      // 方法
      goBack,
      goToWorkbench,
      closeConfirmDialog,
      getStatusClass,
      getStatusText,
      formatDateTime,
      isContentLong,
      toggleContentExpanded,
      toggleResultsExpanded,
      toggleOverviewExpanded,
      toggleObjectiveExpanded,
      handleLinkClick,
      viewReviewLogs,
      loadEventDetail
    }
  }
}
</script>

<style scoped>
/* 主容器样式 */
.major-event-detail {
  padding: 24px;
  max-width: 1200px;
  margin: 0 auto;
  background: #f5f5f5;
  min-height: 100vh;
}

/* 页面头部样式 */
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 32px;
  padding: 20px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
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
  font-size: 14px;
}

.back-btn:hover {
  background: #e0e0e0;
  transform: translateX(-2px);
}

.header h1 {
  font-size: 28px;
  font-weight: 600;
  color: #1a1a1a;
  margin: 0;
}

/* 加载和错误状态样式 */
.loading, .error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  text-align: center;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid #f3f3f3;
  border-top: 3px solid #1976d2;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 16px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error-state svg {
  color: #d32f2f;
  margin-bottom: 16px;
}

.error-state h3 {
  font-size: 18px;
  margin: 0 0 8px 0;
  color: #333;
}

.error-state p {
  margin: 0 0 24px 0;
  color: #666;
  font-size: 14px;
}

.error-icon {
  margin-bottom: 16px;
}

.error-actions {
  display: flex;
  gap: 12px;
  margin-top: 24px;
}

.retry-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: #1976d2;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.2s;
}

.retry-btn:hover {
  background: #1565c0;
}

.back-btn-error {
  padding: 8px 16px;
  background: #f5f5f5;
  color: #666;
  border: 1px solid #ddd;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
}

.back-btn-error:hover {
  background: #e0e0e0;
  color: #333;
}

/* 详情内容样式 */
.detail-content {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

/* 信息卡片样式 */
.info-card {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  transition: box-shadow 0.2s;
}

.info-card:hover {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  background: #f8f9fa;
  border-bottom: 1px solid #e0e0e0;
}

.card-header h3 {
  font-size: 18px;
  font-weight: 600;
  color: #1a1a1a;
  margin: 0;
}

.toggle-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 6px 12px;
  background: white;
  border: 1px solid #ddd;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  transition: all 0.2s;
}

.toggle-btn:hover {
  background: #f0f0f0;
}

.card-content {
  padding: 24px;
}

/* 标题卡片特殊样式 */
.title-card .card-content {
  text-align: center;
  padding: 32px 24px;
}

.event-title {
  font-size: 32px;
  font-weight: 700;
  color: #1a1a1a;
  margin: 0;
  line-height: 1.2;
}

/* 版本信息样式 */
.version-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.version-label {
  font-size: 14px;
  color: #666;
  font-weight: 500;
}

.version-number {
  font-size: 16px;
  font-weight: 600;
  color: #1976d2;
  background: #e3f2fd;
  padding: 4px 12px;
  border-radius: 12px;
}

/* 状态显示样式 */
.status-display {
  display: flex;
  align-items: center;
}

.status-badge {
  padding: 8px 16px;
  border-radius: 16px;
  font-size: 14px;
  font-weight: 600;
  text-align: center;
}

.status-pending {
  background: #fff3e0;
  color: #f57c00;
  border: 1px solid #ffb74d;
}

.status-reviewing {
  background: #e3f2fd;
  color: #1976d2;
  border: 1px solid #64b5f6;
}

.status-reviewed {
  background: #e8f5e8;
  color: #2e7d32;
  border: 1px solid #81c784;
}

/* 信息区块样式 */
.info-section {
  margin-bottom: 24px;
}

.info-section:last-child {
  margin-bottom: 0;
}

.section-label {
  display: block;
  font-size: 14px;
  font-weight: 600;
  color: #333;
  margin-bottom: 8px;
  padding-bottom: 4px;
  border-bottom: 2px solid #1976d2;
  width: fit-content;
}

.section-content {
  font-size: 14px;
  line-height: 1.6;
  color: #555;
}

/* 可展开内容样式 */
.expandable-content {
  position: relative;
}

.content-text {
  max-height: 60px;
  overflow: hidden;
  transition: max-height 0.3s ease;
}

.content-text.expanded {
  max-height: none;
}

.expand-btn {
  margin-top: 8px;
  padding: 4px 8px;
  background: #f0f0f0;
  border: 1px solid #ddd;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  color: #1976d2;
  transition: all 0.2s;
}

.expand-btn:hover {
  background: #e0e0e0;
}

/* 审计证据标准样式 */
.evidence-standards {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.evidence-situation {
  background: #f8f9fa;
  border-radius: 6px;
  padding: 16px;
  border-left: 4px solid #1976d2;
}

.situation-title {
  font-size: 16px;
  font-weight: 600;
  color: #1976d2;
  margin: 0 0 12px 0;
}

.situation-content {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.conclusion, .criteria {
  background: white;
  padding: 12px;
  border-radius: 4px;
}

.conclusion strong, .criteria strong {
  color: #333;
  display: block;
  margin-bottom: 4px;
}

.conclusion p, .criteria p {
  margin: 0;
  color: #555;
}

/* 复核结果样式 */
.empty-results, .reviewing-results {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px;
  text-align: center;
  color: #666;
}

.empty-results svg, .reviewing-results svg {
  color: #999;
  margin-bottom: 16px;
}

.empty-results p, .reviewing-results p {
  margin: 0;
  font-size: 16px;
}

.workbench-btn {
  margin-top: 16px;
  padding: 8px 16px;
  background: #1976d2;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.2s;
}

.workbench-btn:hover {
  background: #1565c0;
}

.result-details {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.result-item {
  background: #f8f9fa;
  padding: 16px;
  border-radius: 6px;
  border-left: 4px solid #4caf50;
}

.result-item strong {
  color: #333;
  display: block;
  margin-bottom: 8px;
}

.result-item p {
  margin: 0;
  color: #555;
  line-height: 1.6;
}

/* 复核日志入口样式 */
.log-entry-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: #f5f5f5;
  border: 1px solid #ddd;
  border-radius: 6px;
  cursor: not-allowed;
  font-size: 14px;
  color: #999;
  transition: all 0.2s;
}

.log-entry-btn:not(:disabled):hover {
  background: #e0e0e0;
  cursor: pointer;
  color: #333;
}

.coming-soon {
  font-size: 12px;
  color: #999;
  font-style: italic;
}

/* 确认对话框样式 */
.dialog-overlay {
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

.confirm-dialog {
  background: white;
  border-radius: 8px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
  max-width: 400px;
  width: 90%;
  overflow: hidden;
}

.dialog-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  background: #f8f9fa;
  border-bottom: 1px solid #e0e0e0;
}

.dialog-header h3 {
  font-size: 18px;
  font-weight: 600;
  color: #1a1a1a;
  margin: 0;
}

.close-btn {
  background: none;
  border: none;
  cursor: pointer;
  padding: 4px;
  color: #666;
  transition: color 0.2s;
}

.close-btn:hover {
  color: #333;
}

.dialog-content {
  padding: 24px;
}

.dialog-content p {
  margin: 0;
  font-size: 14px;
  line-height: 1.6;
  color: #555;
}

.dialog-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 20px 24px;
  background: #f8f9fa;
  border-top: 1px solid #e0e0e0;
}

.cancel-btn, .confirm-btn {
  padding: 8px 16px;
  border: 1px solid #ddd;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s;
}

.cancel-btn {
  background: white;
  color: #666;
}

.cancel-btn:hover {
  background: #f0f0f0;
}

.confirm-btn {
  background: #1976d2;
  color: white;
  border-color: #1976d2;
}

.confirm-btn:hover {
  background: #1565c0;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .major-event-detail {
    padding: 16px;
  }
  
  .header {
    padding: 16px;
  }
  
  .header h1 {
    font-size: 24px;
  }
  
  .event-title {
    font-size: 24px;
  }
  
  .card-content {
    padding: 16px;
  }
  
  .card-header {
    padding: 16px;
  }
  
  .confirm-dialog {
    margin: 16px;
  }
}

/* 滚动条样式 */
::-webkit-scrollbar {
  width: 8px;
}

::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}
</style>