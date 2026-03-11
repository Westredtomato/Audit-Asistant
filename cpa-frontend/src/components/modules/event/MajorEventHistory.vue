<template>
  <div class="major-event-history">
    <div class="header">
      <div class="header-left">
        <button class="back-btn" @click="goBack">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M19 12H5M12 19L5 12L12 5" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          返回
        </button>
        <div class="header-info">
          <h1>历史版本</h1>
          <p v-if="event">{{ event.title }}</p>
        </div>
      </div>
      <div class="header-actions">
        <button class="action-btn" @click="refreshHistory">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <polyline points="23 4 23 10 17 10" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <polyline points="1 20 1 14 7 14" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M20.49 9C20.0295 7.47079 19.1956 6.09637 18.0618 5.00365C16.9281 3.91093 15.5358 3.13616 14.0102 2.75C12.4846 2.36384 10.8851 2.38245 9.36772 2.80402C7.85034 3.22559 6.47203 4.03518 5.36772 5.15C4.26341 6.26482 3.47203 7.65034 3.06772 9.17402C2.66341 10.6977 2.66341 12.3023 3.06772 13.826C3.47203 15.3497 4.26341 16.7352 5.36772 17.85C6.47203 18.9648 7.85034 19.7744 9.36772 20.196" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          刷新
        </button>
        <button class="action-btn" @click="viewCurrentVersion" v-if="event">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M1 12S5 4 12 4S23 12 23 12S19 20 12 20S1 12 1 12Z" stroke="currentColor" stroke-width="2"/>
            <circle cx="12" cy="12" r="3" stroke="currentColor" stroke-width="2"/>
          </svg>
          查看当前版本
        </button>
      </div>
    </div>

    <!-- 加载状态 -->
    <div class="loading" v-if="loading">
      <div class="loading-spinner"></div>
      <p>加载历史版本中...</p>
    </div>

    <!-- 历史版本内容 -->
    <div class="history-content" v-if="!loading">
      <!-- 版本筛选 -->
      <div class="filter-section">
        <div class="filter-group">
          <label>时间范围</label>
          <div class="date-range">
            <input
              v-model="filters.startDate"
              type="date"
              placeholder="开始日期"
              @change="applyFilters"
            />
            <span class="date-separator">至</span>
            <input
              v-model="filters.endDate"
              type="date"
              placeholder="结束日期"
              @change="applyFilters"
            />
          </div>
        </div>
        
        <div class="filter-group">
          <label>操作类型</label>
          <select v-model="filters.actionType" @change="applyFilters">
            <option value="">全部操作</option>
            <option value="创建">创建</option>
            <option value="更新">更新</option>
            <option value="状态变更">状态变更</option>
            <option value="附件操作">附件操作</option>
            <option value="人员变更">人员变更</option>
          </select>
        </div>
        
        <div class="filter-group">
          <label>操作人</label>
          <select v-model="filters.operator" @change="applyFilters">
            <option value="">全部人员</option>
            <option v-for="operator in operators" :key="operator" :value="operator">
              {{ operator }}
            </option>
          </select>
        </div>
        
        <div class="filter-actions">
          <button class="filter-btn" @click="clearFilters">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <line x1="18" y1="6" x2="6" y2="18" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <line x1="6" y1="6" x2="18" y2="18" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            清除筛选
          </button>
        </div>
      </div>

      <!-- 版本对比模式切换 -->
      <div class="view-mode-section">
        <div class="mode-tabs">
          <button
            class="mode-tab"
            :class="{ active: viewMode === 'timeline' }"
            @click="viewMode = 'timeline'"
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <line x1="12" y1="2" x2="12" y2="6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <line x1="12" y1="18" x2="12" y2="22" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <line x1="4.93" y1="4.93" x2="7.76" y2="7.76" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <line x1="16.24" y1="16.24" x2="19.07" y2="19.07" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <line x1="2" y1="12" x2="6" y2="12" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <line x1="18" y1="12" x2="22" y2="12" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <line x1="4.93" y1="19.07" x2="7.76" y2="16.24" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <line x1="16.24" y1="7.76" x2="19.07" y2="4.93" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            时间线视图
          </button>
          <button
            class="mode-tab"
            :class="{ active: viewMode === 'compare' }"
            @click="viewMode = 'compare'"
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <rect x="3" y="3" width="18" height="18" rx="2" ry="2" stroke="currentColor" stroke-width="2"/>
              <line x1="12" y1="3" x2="12" y2="21" stroke="currentColor" stroke-width="2"/>
            </svg>
            对比视图
          </button>
        </div>
        
        <div class="compare-controls" v-if="viewMode === 'compare'">
          <div class="compare-selectors">
            <div class="selector-group">
              <label>版本A</label>
              <select v-model="compareVersions.versionA">
                <option value="">选择版本</option>
                <option v-for="version in filteredVersions" :key="version.id" :value="version.id">
                  {{ formatDateTime(version.timestamp) }} - {{ version.operator }}
                </option>
              </select>
            </div>
            <div class="selector-group">
              <label>版本B</label>
              <select v-model="compareVersions.versionB">
                <option value="">选择版本</option>
                <option v-for="version in filteredVersions" :key="version.id" :value="version.id">
                  {{ formatDateTime(version.timestamp) }} - {{ version.operator }}
                </option>
              </select>
            </div>
          </div>
          <button
            class="compare-btn"
            @click="performCompare"
            :disabled="!compareVersions.versionA || !compareVersions.versionB"
          >
            开始对比
          </button>
        </div>
      </div>

      <!-- 时间线视图 -->
      <div class="timeline-view" v-if="viewMode === 'timeline'">
        <div class="timeline-container">
          <div class="timeline-item" v-for="version in filteredVersions" :key="version.id">
            <div class="timeline-marker">
              <div class="timeline-dot" :class="getActionTypeClass(version.actionType)"></div>
              <div class="timeline-line" v-if="version !== filteredVersions[filteredVersions.length - 1]"></div>
            </div>
            
            <div class="timeline-content">
              <div class="version-card">
                <div class="version-header">
                  <div class="version-info">
                    <h3>{{ version.actionType }}</h3>
                    <div class="version-meta">
                      <span class="version-time">{{ formatDateTime(version.timestamp) }}</span>
                      <span class="version-operator">{{ version.operator }}</span>
                      <span class="version-number">v{{ version.version }}</span>
                    </div>
                  </div>
                  <div class="version-actions">
                    <button class="version-btn" @click="viewVersion(version)">
                      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M1 12S5 4 12 4S23 12 23 12S19 20 12 20S1 12 1 12Z" stroke="currentColor" stroke-width="2"/>
                        <circle cx="12" cy="12" r="3" stroke="currentColor" stroke-width="2"/>
                      </svg>
                      查看
                    </button>
                    <button class="version-btn" @click="restoreVersion(version)" v-if="!version.isCurrent">
                      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <polyline points="23 4 23 10 17 10" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                        <polyline points="1 20 1 14 7 14" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                        <path d="M20.49 9C20.0295 7.47079 19.1956 6.09637 18.0618 5.00365C16.9281 3.91093 15.5358 3.13616 14.0102 2.75C12.4846 2.36384 10.8851 2.38245 9.36772 2.80402C7.85034 3.22559 6.47203 4.03518 5.36772 5.15C4.26341 6.26482 3.47203 7.65034 3.06772 9.17402C2.66341 10.6977 2.66341 12.3023 3.06772 13.826C3.47203 15.3497 4.26341 16.7352 5.36772 17.85C6.47203 18.9648 7.85034 19.7744 9.36772 20.196" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                      </svg>
                      恢复
                    </button>
                    <span class="current-badge" v-if="version.isCurrent">当前版本</span>
                  </div>
                </div>
                
                <div class="version-changes" v-if="version.changes && version.changes.length > 0">
                  <h4>变更内容</h4>
                  <div class="changes-list">
                    <div class="change-item" v-for="change in version.changes" :key="change.field">
                      <div class="change-field">{{ change.field }}</div>
                      <div class="change-values">
                        <span class="old-value" v-if="change.oldValue">{{ change.oldValue }}</span>
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="arrow-icon">
                          <line x1="5" y1="12" x2="19" y2="12" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                          <polyline points="12,5 19,12 12,19" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                        </svg>
                        <span class="new-value">{{ change.newValue }}</span>
                      </div>
                    </div>
                  </div>
                </div>
                
                <div class="version-comment" v-if="version.comment">
                  <h4>备注</h4>
                  <p>{{ version.comment }}</p>
                </div>
              </div>
            </div>
          </div>
          
          <div class="no-versions" v-if="filteredVersions.length === 0">
            <svg width="64" height="64" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2"/>
              <path d="M8 12L12 16L16 12" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M12 8V16" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            <h3>暂无历史版本</h3>
            <p>{{ filters.startDate || filters.endDate || filters.actionType || filters.operator ? '当前筛选条件下没有找到历史版本' : '该事项暂无历史版本记录' }}</p>
          </div>
        </div>
      </div>

      <!-- 对比视图 -->
      <div class="compare-view" v-if="viewMode === 'compare' && compareResult">
        <div class="compare-header">
          <h3>版本对比结果</h3>
          <button class="close-compare-btn" @click="closeCompare">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <line x1="18" y1="6" x2="6" y2="18" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <line x1="6" y1="6" x2="18" y2="18" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            关闭对比
          </button>
        </div>
        
        <div class="compare-content">
          <div class="compare-panel">
            <div class="panel-header">
              <h4>版本A</h4>
              <div class="panel-meta">
                <span>{{ formatDateTime(compareResult.versionA.timestamp) }}</span>
                <span>{{ compareResult.versionA.operator }}</span>
              </div>
            </div>
            <div class="panel-content">
              <div class="field-group" v-for="field in compareResult.fields" :key="field.name">
                <label>{{ field.label }}</label>
                <div class="field-value" :class="{ changed: field.changed }">
                  {{ field.valueA || '(空)' }}
                </div>
              </div>
            </div>
          </div>
          
          <div class="compare-divider">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <polyline points="9,18 15,12 9,6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
          
          <div class="compare-panel">
            <div class="panel-header">
              <h4>版本B</h4>
              <div class="panel-meta">
                <span>{{ formatDateTime(compareResult.versionB.timestamp) }}</span>
                <span>{{ compareResult.versionB.operator }}</span>
              </div>
            </div>
            <div class="panel-content">
              <div class="field-group" v-for="field in compareResult.fields" :key="field.name">
                <label>{{ field.label }}</label>
                <div class="field-value" :class="{ changed: field.changed }">
                  {{ field.valueB || '(空)' }}
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <div class="compare-summary" v-if="compareResult.summary">
          <h4>变更摘要</h4>
          <div class="summary-stats">
            <div class="stat-item">
              <span class="stat-number">{{ compareResult.summary.totalChanges }}</span>
              <span class="stat-label">项变更</span>
            </div>
            <div class="stat-item">
              <span class="stat-number">{{ compareResult.summary.addedFields }}</span>
              <span class="stat-label">新增字段</span>
            </div>
            <div class="stat-item">
              <span class="stat-number">{{ compareResult.summary.modifiedFields }}</span>
              <span class="stat-label">修改字段</span>
            </div>
            <div class="stat-item">
              <span class="stat-number">{{ compareResult.summary.removedFields }}</span>
              <span class="stat-label">删除字段</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 错误状态 -->
    <div class="error-state" v-if="!loading && !event">
      <svg width="64" height="64" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2"/>
        <line x1="15" y1="9" x2="9" y2="15" stroke="currentColor" stroke-width="2"/>
        <line x1="9" y1="9" x2="15" y2="15" stroke="currentColor" stroke-width="2"/>
      </svg>
      <h3>事项不存在</h3>
      <p>您访问的重大事项不存在或已被删除</p>
      <button class="back-btn" @click="goBack">返回列表</button>
    </div>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useEventStore } from '@/stores/event'

export default {
  name: 'MajorEventHistory',
  setup() {
    const route = useRoute()
    const router = useRouter()
    const eventStore = useEventStore()
    
    // 响应式数据
    const loading = ref(true)
    const viewMode = ref('timeline')
    const versions = ref([])
    const operators = ref([])
    const compareResult = ref(null)
    
    // 筛选条件
    const filters = reactive({
      startDate: '',
      endDate: '',
      actionType: '',
      operator: ''
    })
    
    // 对比版本
    const compareVersions = reactive({
      versionA: '',
      versionB: ''
    })
    
    // 计算属性
    const event = computed(() => {
      const eventId = parseInt(route.params.id)
      return eventStore.majorEvents.find(e => e.id === eventId)
    })
    
    const filteredVersions = computed(() => {
      let filtered = [...versions.value]
      
      if (filters.startDate) {
        filtered = filtered.filter(v => new Date(v.timestamp) >= new Date(filters.startDate))
      }
      
      if (filters.endDate) {
        filtered = filtered.filter(v => new Date(v.timestamp) <= new Date(filters.endDate))
      }
      
      if (filters.actionType) {
        filtered = filtered.filter(v => v.actionType === filters.actionType)
      }
      
      if (filters.operator) {
        filtered = filtered.filter(v => v.operator === filters.operator)
      }
      
      return filtered.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp))
    })
    
    // 方法
    const goBack = () => {
      router.push('/events/major-events')
    }
    
    const viewCurrentVersion = () => {
      router.push(`/events/major-event/${event.value.id}`)
    }
    
    const refreshHistory = async () => {
      await loadVersionHistory()
    }
    
    const applyFilters = () => {
      // 筛选逻辑已通过计算属性实现
    }
    
    const clearFilters = () => {
      filters.startDate = ''
      filters.endDate = ''
      filters.actionType = ''
      filters.operator = ''
    }
    
    const getActionTypeClass = (actionType) => {
      const classMap = {
        '创建': 'create',
        '更新': 'update',
        '状态变更': 'status',
        '附件操作': 'attachment',
        '人员变更': 'participant'
      }
      return classMap[actionType] || 'default'
    }
    
    const viewVersion = (version) => {
      // TODO: 实现版本详情查看逻辑
      console.log('查看版本:', version)
    }
    
    const restoreVersion = async (version) => {
      if (confirm(`确定要恢复到版本 v${version.version} 吗？此操作将创建一个新的版本。`)) {
        try {
          // TODO: 调用store方法恢复版本
          await eventStore.restoreEventVersion(event.value.id, version.id)
          await loadVersionHistory()
        } catch (error) {
          console.error('恢复版本失败:', error)
          // TODO: 显示错误提示
        }
      }
    }
    
    const performCompare = () => {
      const versionA = versions.value.find(v => v.id === compareVersions.versionA)
      const versionB = versions.value.find(v => v.id === compareVersions.versionB)
      
      if (!versionA || !versionB) {
        return
      }
      
      // 生成对比结果
      compareResult.value = generateCompareResult(versionA, versionB)
    }
    
    const generateCompareResult = (versionA, versionB) => {
      const fields = [
        { name: 'title', label: '标题', valueA: versionA.data?.title, valueB: versionB.data?.title },
        { name: 'type', label: '类型', valueA: versionA.data?.type, valueB: versionB.data?.type },
        { name: 'priority', label: '优先级', valueA: versionA.data?.priority, valueB: versionB.data?.priority },
        { name: 'status', label: '状态', valueA: versionA.data?.status, valueB: versionB.data?.status },
        { name: 'date', label: '日期', valueA: versionA.data?.date, valueB: versionB.data?.date },
        { name: 'description', label: '描述', valueA: versionA.data?.description, valueB: versionB.data?.description }
      ]
      
      // 标记变更字段
      fields.forEach(field => {
        field.changed = field.valueA !== field.valueB
      })
      
      const changedFields = fields.filter(f => f.changed)
      
      return {
        versionA,
        versionB,
        fields,
        summary: {
          totalChanges: changedFields.length,
          addedFields: changedFields.filter(f => !f.valueA && f.valueB).length,
          modifiedFields: changedFields.filter(f => f.valueA && f.valueB).length,
          removedFields: changedFields.filter(f => f.valueA && !f.valueB).length
        }
      }
    }
    
    const closeCompare = () => {
      compareResult.value = null
      compareVersions.versionA = ''
      compareVersions.versionB = ''
    }
    
    const formatDateTime = (dateString) => {
      const date = new Date(dateString)
      return date.toLocaleString('zh-CN')
    }
    
    // 加载版本历史
    const loadVersionHistory = async () => {
      loading.value = true
      try {
        // 确保事项数据已加载
        if (eventStore.majorEvents.length === 0) {
          await eventStore.fetchMajorEvents()
        }
        
        // TODO: 从API加载真实的版本历史数据
        // 这里使用模拟数据
        const eventId = parseInt(route.params.id)
        versions.value = [
          {
            id: 1,
            version: '1.0',
            timestamp: new Date().toISOString(),
            operator: '张三',
            actionType: '创建',
            isCurrent: true,
            comment: '初始创建事项',
            data: event.value,
            changes: []
          },
          {
            id: 2,
            version: '1.1',
            timestamp: new Date(Date.now() - 86400000).toISOString(),
            operator: '李四',
            actionType: '更新',
            isCurrent: false,
            comment: '更新事项描述和优先级',
            data: { ...event.value, description: '旧的描述', priority: '中' },
            changes: [
              { field: '描述', oldValue: '旧的描述', newValue: event.value?.description },
              { field: '优先级', oldValue: '中', newValue: event.value?.priority }
            ]
          },
          {
            id: 3,
            version: '1.2',
            timestamp: new Date(Date.now() - 172800000).toISOString(),
            operator: '王五',
            actionType: '状态变更',
            isCurrent: false,
            comment: '变更事项状态',
            data: { ...event.value, status: '进行中' },
            changes: [
              { field: '状态', oldValue: '进行中', newValue: event.value?.status }
            ]
          }
        ]
        
        // 提取操作人员列表
        operators.value = [...new Set(versions.value.map(v => v.operator))]
        
      } catch (error) {
        console.error('加载版本历史失败:', error)
      } finally {
        loading.value = false
      }
    }
    
    // 生命周期
    onMounted(() => {
      loadVersionHistory()
    })
    
    return {
      // 数据
      loading,
      viewMode,
      versions,
      operators,
      compareResult,
      filters,
      compareVersions,
      
      // 计算属性
      event,
      filteredVersions,
      
      // 方法
      goBack,
      viewCurrentVersion,
      refreshHistory,
      applyFilters,
      clearFilters,
      getActionTypeClass,
      viewVersion,
      restoreVersion,
      performCompare,
      closeCompare,
      formatDateTime
    }
  }
}
</script>

<style scoped>
.major-event-history {
  padding: 24px;
  max-width: 1200px;
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

.header-info h1 {
  font-size: 28px;
  font-weight: 600;
  color: #1a1a1a;
  margin: 0 0 4px 0;
}

.header-info p {
  font-size: 14px;
  color: #666;
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
  background: white;
  border: 1px solid #ddd;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 14px;
}

.action-btn:hover {
  background: #f0f0f0;
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

.history-content {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.filter-section {
  background: white;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 20px;
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
  align-items: end;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
  min-width: 150px;
}

.filter-group label {
  font-size: 12px;
  font-weight: 500;
  color: #666;
  text-transform: uppercase;
}

.filter-group input,
.filter-group select {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.date-range {
  display: flex;
  align-items: center;
  gap: 8px;
}

.date-separator {
  font-size: 12px;
  color: #666;
}

.filter-actions {
  display: flex;
  gap: 8px;
}

.filter-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 8px 12px;
  background: #f5f5f5;
  border: 1px solid #ddd;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  transition: all 0.2s;
}

.filter-btn:hover {
  background: #e0e0e0;
}

.view-mode-section {
  background: white;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 20px;
}

.mode-tabs {
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
}

.mode-tab {
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

.mode-tab:hover {
  background: #e0e0e0;
}

.mode-tab.active {
  background: #1976d2;
  color: white;
  border-color: #1976d2;
}

.compare-controls {
  display: flex;
  align-items: end;
  gap: 16px;
}

.compare-selectors {
  display: flex;
  gap: 16px;
  flex: 1;
}

.selector-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
  flex: 1;
}

.selector-group label {
  font-size: 12px;
  font-weight: 500;
  color: #666;
}

.selector-group select {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.compare-btn {
  padding: 8px 16px;
  background: #1976d2;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s;
}

.compare-btn:hover:not(:disabled) {
  background: #1565c0;
}

.compare-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.timeline-view {
  background: white;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 24px;
}

.timeline-container {
  position: relative;
}

.timeline-item {
  display: flex;
  gap: 20px;
  margin-bottom: 24px;
}

.timeline-item:last-child {
  margin-bottom: 0;
}

.timeline-marker {
  display: flex;
  flex-direction: column;
  align-items: center;
  position: relative;
}

.timeline-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: #ddd;
  border: 2px solid white;
  box-shadow: 0 0 0 2px #ddd;
}

.timeline-dot.create {
  background: #4caf50;
  box-shadow: 0 0 0 2px #4caf50;
}

.timeline-dot.update {
  background: #2196f3;
  box-shadow: 0 0 0 2px #2196f3;
}

.timeline-dot.status {
  background: #ff9800;
  box-shadow: 0 0 0 2px #ff9800;
}

.timeline-dot.attachment {
  background: #9c27b0;
  box-shadow: 0 0 0 2px #9c27b0;
}

.timeline-dot.participant {
  background: #607d8b;
  box-shadow: 0 0 0 2px #607d8b;
}

.timeline-line {
  width: 2px;
  height: 40px;
  background: #e0e0e0;
  margin-top: 8px;
}

.timeline-content {
  flex: 1;
}

.version-card {
  background: #f8f9fa;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 20px;
}

.version-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.version-info h3 {
  font-size: 16px;
  font-weight: 600;
  color: #1a1a1a;
  margin: 0 0 8px 0;
}

.version-meta {
  display: flex;
  gap: 12px;
  font-size: 12px;
  color: #666;
}

.version-actions {
  display: flex;
  gap: 8px;
  align-items: center;
}

.version-btn {
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

.version-btn:hover {
  background: #1976d2;
  color: white;
  border-color: #1976d2;
}

.current-badge {
  background: #e8f5e8;
  color: #2e7d32;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 500;
}

.version-changes {
  margin-bottom: 16px;
}

.version-changes h4 {
  font-size: 14px;
  font-weight: 600;
  color: #333;
  margin: 0 0 8px 0;
}

.changes-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.change-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 12px;
  background: white;
  border-radius: 4px;
  font-size: 12px;
}

.change-field {
  font-weight: 500;
  color: #333;
  min-width: 60px;
}

.change-values {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
}

.old-value {
  color: #d32f2f;
  text-decoration: line-through;
}

.arrow-icon {
  color: #666;
}

.new-value {
  color: #388e3c;
  font-weight: 500;
}

.version-comment {
  border-top: 1px solid #e0e0e0;
  padding-top: 12px;
}

.version-comment h4 {
  font-size: 14px;
  font-weight: 600;
  color: #333;
  margin: 0 0 8px 0;
}

.version-comment p {
  font-size: 12px;
  color: #666;
  margin: 0;
  line-height: 1.4;
}

.no-versions {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  text-align: center;
  color: #666;
}

.no-versions svg {
  margin-bottom: 16px;
  color: #ccc;
}

.no-versions h3 {
  font-size: 18px;
  margin: 0 0 8px 0;
  color: #333;
}

.no-versions p {
  margin: 0;
  font-size: 14px;
}

.compare-view {
  background: white;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 24px;
}

.compare-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid #e0e0e0;
}

.compare-header h3 {
  font-size: 18px;
  font-weight: 600;
  color: #1a1a1a;
  margin: 0;
}

.close-compare-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 6px 12px;
  background: #f5f5f5;
  border: 1px solid #ddd;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  transition: all 0.2s;
}

.close-compare-btn:hover {
  background: #e0e0e0;
}

.compare-content {
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  gap: 24px;
  margin-bottom: 24px;
}

.compare-panel {
  background: #f8f9fa;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  overflow: hidden;
}

.panel-header {
  padding: 16px 20px;
  background: white;
  border-bottom: 1px solid #e0e0e0;
}

.panel-header h4 {
  font-size: 16px;
  font-weight: 600;
  color: #1a1a1a;
  margin: 0 0 8px 0;
}

.panel-meta {
  display: flex;
  gap: 12px;
  font-size: 12px;
  color: #666;
}

.panel-content {
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.field-group {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.field-group label {
  font-size: 12px;
  font-weight: 500;
  color: #666;
  text-transform: uppercase;
}

.field-value {
  padding: 8px 12px;
  background: white;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  font-size: 14px;
  color: #333;
  min-height: 20px;
}

.field-value.changed {
  background: #fff3e0;
  border-color: #ff9800;
}

.compare-divider {
  display: flex;
  align-items: center;
  justify-content: center;
  color: #666;
}

.compare-summary {
  border-top: 1px solid #e0e0e0;
  padding-top: 20px;
}

.compare-summary h4 {
  font-size: 16px;
  font-weight: 600;
  color: #1a1a1a;
  margin: 0 0 16px 0;
}

.summary-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 16px;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 16px;
  background: #f8f9fa;
  border-radius: 8px;
  text-align: center;
}

.stat-number {
  font-size: 24px;
  font-weight: 600;
  color: #1976d2;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 12px;
  color: #666;
  text-transform: uppercase;
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
  .major-event-history {
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
  
  .filter-section {
    flex-direction: column;
    align-items: stretch;
  }
  
  .filter-group {
    min-width: auto;
  }
  
  .date-range {
    flex-direction: column;
    align-items: stretch;
  }
  
  .compare-controls {
    flex-direction: column;
    align-items: stretch;
  }
  
  .compare-selectors {
    flex-direction: column;
  }
  
  .timeline-item {
    gap: 12px;
  }
  
  .version-header {
    flex-direction: column;
    gap: 12px;
    align-items: stretch;
  }
  
  .version-actions {
    justify-content: space-between;
  }
  
  .compare-content {
    grid-template-columns: 1fr;
    grid-template-rows: auto auto auto;
  }
  
  .compare-divider {
    transform: rotate(90deg);
  }
  
  .summary-stats {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>