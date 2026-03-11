<template>
  <!-- 超时回溯组件 - 用于查看和分析复核过程中的超时处理记录 -->
  <div class="timeout-review">
    <!-- 组件头部 - 显示标题和描述信息 -->
    <div class="header">
      <h3>超时回溯分析</h3>
      <p class="description">查看复核过程中的超时处理记录，分析超时原因并提供优化建议</p>
    </div>

    <!-- 超时统计概览 - 显示超时处理的整体统计信息 -->
    <div class="timeout-overview">
      <div class="overview-header">
        <h4>超时统计概览</h4>
        <el-tag :type="getOverallStatusType()" size="small">
          {{ getOverallStatusText() }}
        </el-tag>
      </div>
      
      <!-- 统计卡片 - 显示各类超时的数量统计 -->
      <div class="stats-cards">
        <div class="stat-card">
          <div class="stat-icon">📄</div>
          <div class="stat-content">
            <div class="stat-number">{{ timeoutStats.documentTransfer }}</div>
            <div class="stat-label">底稿传输超时</div>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon">🔍</div>
          <div class="stat-content">
            <div class="stat-number">{{ timeoutStats.infoRetrieval }}</div>
            <div class="stat-label">超时回溯分析</div>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon">❓</div>
          <div class="stat-content">
            <div class="stat-number">{{ timeoutStats.analysisUncertain }}</div>
            <div class="stat-label">分析不确定</div>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon">⚠️</div>
          <div class="stat-content">
            <div class="stat-number">{{ timeoutStats.total }}</div>
            <div class="stat-label">总超时次数</div>
          </div>
        </div>
      </div>
    </div>

    <!-- 超时记录列表 - 显示详细的超时处理记录 -->
    <div class="timeout-records">
      <div class="records-header">
        <h4>超时记录详情</h4>
        <!-- 筛选控件 - 按类型和时间筛选超时记录 -->
        <div class="filter-controls">
          <el-select v-model="selectedType" placeholder="选择超时类型" size="small" clearable>
            <el-option label="全部类型" value="" />
            <el-option label="底稿传输超时" value="documentTransfer" />
            <el-option label="超时回溯分析" value="infoRetrieval" />
            <el-option label="分析不确定" value="analysisUncertain" />
          </el-select>
          <el-date-picker
            v-model="dateRange"
            type="datetimerange"
            range-separator="至"
            start-placeholder="开始时间"
            end-placeholder="结束时间"
            size="small"
            format="YYYY-MM-DD HH:mm"
            value-format="YYYY-MM-DD HH:mm:ss"
          />
          <el-button @click="refreshRecords" size="small" type="primary">
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
        </div>
      </div>
      
      <!-- 记录列表 - 显示过滤后的超时记录 -->
      <div class="records-list" v-loading="loading">
        <div 
          v-for="record in filteredRecords" 
          :key="record.id"
          class="record-item"
          :class="`record-${record.type}`"
        >
          <!-- 记录头部 - 显示超时类型、时间和处理状态 -->
          <div class="record-header">
            <div class="record-type">
              <el-tag :type="getTypeTagColor(record.type)" size="small">
                {{ getTypeLabel(record.type) }}
              </el-tag>
            </div>
            <div class="record-time">{{ formatDateTime(record.timestamp) }}</div>
            <div class="record-status">
              <el-tag :type="getStatusTagColor(record.status)" size="small">
                {{ getStatusLabel(record.status) }}
              </el-tag>
            </div>
          </div>
          
          <!-- 记录内容 - 显示超时详情和处理结果 -->
          <div class="record-content">
            <div class="record-description">{{ record.description }}</div>
            <div class="record-details" v-if="record.details">
              <p><strong>超时原因：</strong>{{ record.details.reason }}</p>
              <p><strong>等待时长：</strong>{{ record.details.waitDuration }}秒</p>
              <p><strong>处理方式：</strong>{{ record.details.action }}</p>
              <p v-if="record.details.retryCount"><strong>重试次数：</strong>{{ record.details.retryCount }}</p>
            </div>
          </div>
          
          <!-- 记录操作 - 提供查看详情、重新处理等操作 -->
          <div class="record-actions">
            <el-button @click="viewRecordDetail(record)" size="small" type="text">
              查看详情
            </el-button>
            <el-button 
              @click="retryRecord(record)" 
              size="small" 
              type="text"
              v-if="record.status === 'failed'"
            >
              重新处理
            </el-button>
          </div>
        </div>
        
        <!-- 空状态 - 当没有超时记录时显示 -->
        <div v-if="filteredRecords.length === 0 && !loading" class="empty-state">
          <el-empty description="暂无超时记录" />
        </div>
      </div>
    </div>

    <!-- 优化建议 - 基于超时记录提供的改进建议 -->
    <div class="optimization-suggestions" v-if="suggestions.length > 0">
      <div class="suggestions-header">
        <h4>优化建议</h4>
        <el-tag type="info" size="small">基于超时记录分析</el-tag>
      </div>
      
      <div class="suggestions-list">
        <div 
          v-for="suggestion in suggestions" 
          :key="suggestion.id"
          class="suggestion-item"
        >
          <div class="suggestion-icon">
            <el-icon><InfoFilled /></el-icon>
          </div>
          <div class="suggestion-content">
            <div class="suggestion-title">{{ suggestion.title }}</div>
            <div class="suggestion-description">{{ suggestion.description }}</div>
            <div class="suggestion-impact">
              <el-tag :type="getImpactColor(suggestion.impact)" size="small">
                {{ getImpactLabel(suggestion.impact) }}
              </el-tag>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 操作按钮区域 - 提供主要功能操作 -->
    <div class="actions">
      <el-button @click="exportReport" type="primary">
        <el-icon><Download /></el-icon>
        导出报告
      </el-button>
      <el-button @click="clearTimeoutRecords" :disabled="timeoutRecords.length === 0">
        <el-icon><Delete /></el-icon>
        清空记录
      </el-button>
      <el-button @click="refreshData">
        <el-icon><Refresh /></el-icon>
        刷新数据
      </el-button>
    </div>

    <!-- 记录详情对话框 - 显示单个超时记录的完整信息 -->
    <el-dialog
      v-model="showDetailDialog"
      title="超时记录详情"
      width="600px"
      :close-on-click-modal="false"
    >
      <div class="detail-content" v-if="selectedRecord">
        <div class="detail-section">
          <h5>基本信息</h5>
          <el-descriptions :column="2" border>
            <el-descriptions-item label="记录ID">{{ selectedRecord.id }}</el-descriptions-item>
            <el-descriptions-item label="超时类型">{{ getTypeLabel(selectedRecord.type) }}</el-descriptions-item>
            <el-descriptions-item label="发生时间">{{ formatDateTime(selectedRecord.timestamp) }}</el-descriptions-item>
            <el-descriptions-item label="处理状态">{{ getStatusLabel(selectedRecord.status) }}</el-descriptions-item>
          </el-descriptions>
        </div>
        
        <div class="detail-section" v-if="selectedRecord.context">
          <h5>上下文信息</h5>
          <pre class="context-data">{{ JSON.stringify(selectedRecord.context, null, 2) }}</pre>
        </div>
      </div>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showDetailDialog = false">关闭</el-button>
          <el-button type="primary" @click="exportSingleRecord" v-if="selectedRecord">
            导出此记录
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script>
// ==================== 状态管理和UI组件导入 ====================
import { useWorkspaceStore } from '@/stores/workspace'  // 工作空间状态管理
import { ElMessage, ElMessageBox } from 'element-plus'  // Element Plus消息组件
import {
  Refresh,      // 刷新图标
  Download,     // 下载图标
  Delete,       // 删除图标
  InfoFilled    // 信息图标（用于建议）
} from '@element-plus/icons-vue'

/**
 * 超时回溯组件
 * 功能：查看和分析复核过程中的超时处理记录
 * 特性：
 * - 超时记录统计和可视化展示
 * - 按类型和时间筛选超时记录
 * - 基于超时模式的优化建议
 * - 超时记录的导出和管理
 * - 支持重新处理失败的超时记录
 */
export default {
  name: 'TimeoutReview',
  components: {
    Refresh,
    Download,
    Delete,
    InfoFilled
  },
  emits: ['timeout-reviewed', 'close'], // 向父组件发送的事件
  data() {
    return {
      // ==================== 数据加载状态 ====================
      loading: false,              // 数据加载状态
      
      // ==================== 超时记录数据 ====================
      timeoutRecords: [],          // 所有超时记录列表
      timeoutStats: {              // 超时统计数据
        documentTransfer: 0,       // 底稿传输超时次数
        infoRetrieval: 0,          // 超时回溯分析次数
        analysisUncertain: 0,      // 分析不确定次数
        total: 0                   // 总超时次数
      },
      
      // ==================== 筛选和显示控制 ====================
      selectedType: '',            // 选中的超时类型筛选
      dateRange: [],               // 时间范围筛选
      
      // ==================== 优化建议数据 ====================
      suggestions: [],             // 优化建议列表
      
      // ==================== 对话框控制 ====================
      showDetailDialog: false,     // 是否显示详情对话框
      selectedRecord: null         // 选中的记录详情
    }
  },
  computed: {
    /**
     * 过滤后的超时记录列表
     * 根据类型和时间范围筛选记录
     */
    filteredRecords() {
      let records = [...this.timeoutRecords]
      
      // 按类型筛选
      if (this.selectedType) {
        records = records.filter(record => record.type === this.selectedType)
      }
      
      // 按时间范围筛选
      if (this.dateRange && this.dateRange.length === 2) {
        const [startTime, endTime] = this.dateRange
        records = records.filter(record => {
          const recordTime = new Date(record.timestamp)
          return recordTime >= new Date(startTime) && recordTime <= new Date(endTime)
        })
      }
      
      // 按时间倒序排列
      return records.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp))
    }
  },
  async mounted() {
    // 组件挂载时加载超时记录数据
    await this.loadTimeoutData()
  },
  methods: {
    // ==================== 数据加载方法 ====================
    
    /**
     * 加载超时数据
     * 从workspace store获取超时记录和统计信息
     */
    async loadTimeoutData() {
      this.loading = true
      try {
        const workspaceStore = useWorkspaceStore()
        
        // 获取警告日志作为超时记录的数据源
        const logsResult = await workspaceStore.getWarningLogs({
          type: 'timeout',
          limit: 100
        })
        
        if (logsResult.success) {
          // 转换警告日志为超时记录格式
          this.timeoutRecords = logsResult.data.map(log => ({
            id: log.id,
            type: this.extractTimeoutType(log.context),
            timestamp: log.timestamp,
            description: log.message,
            status: this.determineRecordStatus(log.context),
            details: {
              reason: log.context?.reason || '未知原因',
              waitDuration: log.context?.waitDuration || 0,
              action: log.context?.action || '继续执行',
              retryCount: log.context?.retryCount || 0
            },
            context: log.context
          }))
          
          // 计算统计数据
          this.calculateStats()
          
          // 生成优化建议
          this.generateSuggestions()
        }
      } catch (error) {
        console.error('加载超时数据失败:', error)
        ElMessage.error('加载超时数据失败，请稍后重试')
      } finally {
        this.loading = false
      }
    },
    
    /**
     * 从日志上下文中提取超时类型
     */
    extractTimeoutType(context) {
      if (!context) return 'unknown'
      
      // 根据上下文信息判断超时类型
      if (context.scenario === 'documentTransfer') return 'documentTransfer'
      if (context.scenario === 'infoRetrieval') return 'infoRetrieval'
      if (context.scenario === 'analysisUncertain') return 'analysisUncertain'
      
      return 'unknown'
    },
    
    /**
     * 确定记录处理状态
     */
    determineRecordStatus(context) {
      if (!context) return 'unknown'
      
      if (context.resolved) return 'resolved'
      if (context.failed) return 'failed'
      if (context.retryCount > 0) return 'retried'
      
      return 'pending'
    },
    
    /**
     * 计算超时统计数据
     */
    calculateStats() {
      this.timeoutStats = {
        documentTransfer: this.timeoutRecords.filter(r => r.type === 'documentTransfer').length,
        infoRetrieval: this.timeoutRecords.filter(r => r.type === 'infoRetrieval').length,
        analysisUncertain: this.timeoutRecords.filter(r => r.type === 'analysisUncertain').length,
        total: this.timeoutRecords.length
      }
    },
    
    /**
     * 生成优化建议
     * 基于超时记录的模式分析生成改进建议
     */
    generateSuggestions() {
      this.suggestions = []
      
      // 如果底稿传输超时较多，建议优化网络或文件大小
      if (this.timeoutStats.documentTransfer > 3) {
        this.suggestions.push({
          id: 'doc-transfer-opt',
          title: '优化底稿传输',
          description: '检测到多次底稿传输超时，建议检查网络连接或压缩文件大小',
          impact: 'high'
        })
      }
      
      // 如果超时回溯分析较多，建议完善底稿
      if (this.timeoutStats.infoRetrieval > 2) {
        this.suggestions.push({
          id: 'info-completeness',
          title: '完善底稿信息',
          description: '检测到多次超时回溯分析，建议补充相关底稿文件',
          impact: 'medium'
        })
      }
      
      // 如果分析不确定较多，建议调整设置
      if (this.timeoutStats.analysisUncertain > 2) {
        this.suggestions.push({
          id: 'analysis-settings',
          title: '调整分析参数',
          description: '检测到多次分析不确定，建议调整复核设置或提供更多指导',
          impact: 'medium'
        })
      }
    },
    
    // ==================== 用户交互方法 ====================
    
    /**
     * 刷新记录数据
     */
    async refreshRecords() {
      await this.loadTimeoutData()
      ElMessage.success('数据已刷新')
    },
    
    /**
     * 刷新所有数据
     */
    async refreshData() {
      await this.loadTimeoutData()
    },
    
    /**
     * 查看记录详情
     */
    viewRecordDetail(record) {
      this.selectedRecord = record
      this.showDetailDialog = true
    },
    
    /**
     * 重新处理失败的记录
     */
    async retryRecord(record) {
      try {
        // TODO: 实现重新处理逻辑
        ElMessage.success(`正在重新处理记录 ${record.id}`)
        
        // 模拟处理延迟
        setTimeout(() => {
          record.status = 'retried'
          ElMessage.success('记录已重新处理')
        }, 2000)
      } catch (error) {
        console.error('重新处理记录失败:', error)
        ElMessage.error('重新处理失败，请稍后重试')
      }
    },
    
    /**
     * 导出超时报告
     */
    async exportReport() {
      try {
        const reportData = {
          exportTime: new Date().toISOString(),
          statistics: this.timeoutStats,
          records: this.filteredRecords,
          suggestions: this.suggestions
        }
        
        const blob = new Blob([JSON.stringify(reportData, null, 2)], {
          type: 'application/json'
        })
        const url = URL.createObjectURL(blob)
        const filename = `timeout-report-${Date.now()}.json`
        
        const link = document.createElement('a')
        link.href = url
        link.download = filename
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
        URL.revokeObjectURL(url)
        
        ElMessage.success('报告已导出')
      } catch (error) {
        console.error('导出报告失败:', error)
        ElMessage.error('导出失败，请稍后重试')
      }
    },
    
    /**
     * 导出单个记录
     */
    async exportSingleRecord() {
      if (!this.selectedRecord) return
      
      try {
        const blob = new Blob([JSON.stringify(this.selectedRecord, null, 2)], {
          type: 'application/json'
        })
        const url = URL.createObjectURL(blob)
        const filename = `timeout-record-${this.selectedRecord.id}.json`
        
        const link = document.createElement('a')
        link.href = url
        link.download = filename
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
        URL.revokeObjectURL(url)
        
        ElMessage.success('记录已导出')
      } catch (error) {
        console.error('导出记录失败:', error)
        ElMessage.error('导出失败，请稍后重试')
      }
    },
    
    /**
     * 清空超时记录
     */
    async clearTimeoutRecords() {
      try {
        await ElMessageBox.confirm(
          '确定要清空所有超时记录吗？此操作不可恢复。',
          '确认清空',
          {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning'
          }
        )
        
        // TODO: 实现清空记录的API调用
        this.timeoutRecords = []
        this.calculateStats()
        this.generateSuggestions()
        
        ElMessage.success('超时记录已清空')
      } catch {
        // 用户取消操作
      }
    },
    
    // ==================== 工具方法 ====================
    
    /**
     * 格式化日期时间
     */
    formatDateTime(timestamp) {
      return new Date(timestamp).toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
      })
    },
    
    /**
     * 获取超时类型的标签文本
     */
    getTypeLabel(type) {
      const typeMap = {
        'documentTransfer': '底稿传输超时',
        'infoRetrieval': '超时回溯分析',
        'analysisUncertain': '分析不确定',
        'unknown': '未知类型'
      }
      return typeMap[type] || type
    },
    
    /**
     * 获取超时类型的标签颜色
     */
    getTypeTagColor(type) {
      const colorMap = {
        'documentTransfer': 'warning',
        'infoRetrieval': 'info',
        'analysisUncertain': 'danger',
        'unknown': 'default'
      }
      return colorMap[type] || 'default'
    },
    
    /**
     * 获取处理状态的标签文本
     */
    getStatusLabel(status) {
      const statusMap = {
        'resolved': '已解决',
        'failed': '处理失败',
        'retried': '已重试',
        'pending': '待处理',
        'unknown': '未知状态'
      }
      return statusMap[status] || status
    },
    
    /**
     * 获取处理状态的标签颜色
     */
    getStatusTagColor(status) {
      const colorMap = {
        'resolved': 'success',
        'failed': 'danger',
        'retried': 'warning',
        'pending': 'info',
        'unknown': 'default'
      }
      return colorMap[status] || 'default'
    },
    
    /**
     * 获取整体状态类型
     */
    getOverallStatusType() {
      if (this.timeoutStats.total === 0) return 'success'
      if (this.timeoutStats.total > 10) return 'danger'
      if (this.timeoutStats.total > 5) return 'warning'
      return 'info'
    },
    
    /**
     * 获取整体状态文本
     */
    getOverallStatusText() {
      if (this.timeoutStats.total === 0) return '无超时记录'
      if (this.timeoutStats.total > 10) return '超时频繁'
      if (this.timeoutStats.total > 5) return '超时较多'
      return '超时正常'
    },
    
    /**
     * 获取影响程度的颜色
     */
    getImpactColor(impact) {
      const colorMap = {
        'high': 'danger',
        'medium': 'warning',
        'low': 'info'
      }
      return colorMap[impact] || 'info'
    },
    
    /**
     * 获取影响程度的标签
     */
    getImpactLabel(impact) {
      const labelMap = {
        'high': '高影响',
        'medium': '中等影响',
        'low': '低影响'
      }
      return labelMap[impact] || impact
    }
  },
  
  // ==================== 组件销毁时的清理 ====================
  beforeUnmount() {
    // 通知父组件超时回溯完成
    this.$emit('timeout-reviewed', {
      recordsCount: this.timeoutRecords.length,
      suggestions: this.suggestions.length
    })
  }
}
</script>

<style scoped>
/* ==================== 组件整体样式 ==================== */
.timeout-review {
  padding: 20px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

/* ==================== 头部样式 ==================== */
.header {
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid #e8e8e8;
}

.header h3 {
  margin: 0 0 8px 0;
  color: #333;
  font-size: 18px;
  font-weight: 600;
}

.description {
  margin: 0;
  color: #666;
  font-size: 14px;
  line-height: 1.5;
}

/* ==================== 超时统计概览样式 ==================== */
.timeout-overview {
  margin-bottom: 24px;
}

.overview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.overview-header h4 {
  margin: 0;
  color: #333;
  font-size: 16px;
  font-weight: 600;
}

.stats-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
}

.stat-card {
  display: flex;
  align-items: center;
  padding: 16px;
  background: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #e9ecef;
}

.stat-icon {
  font-size: 24px;
  margin-right: 12px;
}

.stat-content {
  flex: 1;
}

.stat-number {
  font-size: 24px;
  font-weight: 700;
  color: #333;
  line-height: 1;
}

.stat-label {
  font-size: 12px;
  color: #666;
  margin-top: 4px;
}

/* ==================== 超时记录列表样式 ==================== */
.timeout-records {
  margin-bottom: 24px;
}

.records-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  flex-wrap: wrap;
  gap: 12px;
}

.records-header h4 {
  margin: 0;
  color: #333;
  font-size: 16px;
  font-weight: 600;
}

.filter-controls {
  display: flex;
  gap: 12px;
  align-items: center;
  flex-wrap: wrap;
}

.records-list {
  max-height: 400px;
  overflow-y: auto;
}

.record-item {
  padding: 16px;
  margin-bottom: 12px;
  background: #fff;
  border: 1px solid #e8e8e8;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.record-item:hover {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  border-color: #d0d0d0;
}

.record-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  flex-wrap: wrap;
  gap: 8px;
}

.record-time {
  font-size: 12px;
  color: #999;
}

.record-content {
  margin-bottom: 12px;
}

.record-description {
  color: #333;
  font-size: 14px;
  margin-bottom: 8px;
}

.record-details {
  font-size: 12px;
  color: #666;
  background: #f8f9fa;
  padding: 8px;
  border-radius: 4px;
}

.record-details p {
  margin: 4px 0;
}

.record-actions {
  display: flex;
  gap: 8px;
}

.empty-state {
  text-align: center;
  padding: 40px 20px;
}

/* ==================== 优化建议样式 ==================== */
.optimization-suggestions {
  margin-bottom: 24px;
}

.suggestions-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.suggestions-header h4 {
  margin: 0;
  color: #333;
  font-size: 16px;
  font-weight: 600;
}

.suggestions-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.suggestion-item {
  display: flex;
  align-items: flex-start;
  padding: 16px;
  background: #fff7e6;
  border: 1px solid #ffd591;
  border-radius: 8px;
}

.suggestion-icon {
  margin-right: 12px;
  color: #fa8c16;
  font-size: 18px;
}

.suggestion-content {
  flex: 1;
}

.suggestion-title {
  font-weight: 600;
  color: #333;
  margin-bottom: 4px;
}

.suggestion-description {
  color: #666;
  font-size: 14px;
  margin-bottom: 8px;
}

/* ==================== 操作按钮样式 ==================== */
.actions {
  display: flex;
  gap: 12px;
  padding-top: 16px;
  border-top: 1px solid #e8e8e8;
  flex-wrap: wrap;
}

/* ==================== 对话框样式 ==================== */
.detail-content {
  max-height: 400px;
  overflow-y: auto;
}

.detail-section {
  margin-bottom: 20px;
}

.detail-section h5 {
  margin: 0 0 12px 0;
  color: #333;
  font-size: 14px;
  font-weight: 600;
}

.context-data {
  background: #f8f9fa;
  padding: 12px;
  border-radius: 4px;
  font-size: 12px;
  color: #666;
  white-space: pre-wrap;
  word-break: break-all;
  max-height: 200px;
  overflow-y: auto;
}

/* ==================== 响应式设计 ==================== */
@media (max-width: 768px) {
  .timeout-review {
    padding: 16px;
  }
  
  .stats-cards {
    grid-template-columns: 1fr;
  }
  
  .records-header {
    flex-direction: column;
    align-items: stretch;
  }
  
  .filter-controls {
    flex-direction: column;
  }
  
  .record-header {
    flex-direction: column;
    align-items: stretch;
  }
  
  .actions {
    flex-direction: column;
  }
}
</style>