/**
 * Review Result Store - 复核结果展示状态管理
 * 
 * 负责管理复核结果的展示和归档功能，包括：
 * - 复核结果数据加载和展示
 * - 归档操作和版本管理
 * - localStorage模拟数据库操作
 */
import { defineStore } from 'pinia'
import { useWorkspaceStore } from './workspace'

export const useReviewResultStore = defineStore('reviewResult', {
  // ===== 状态定义 =====
  state: () => ({
    // 复核结果数据
    reviewResult: {
      data: null,                    // 复核结果JSON数据F
      loading: false,                // 数据加载状态
      error: null,                   // 错误信息
      lastUpdated: null,             // 最后更新时间
      status: 'draft'                // 状态：draft(草稿), archived(已归档)
    },



    // 归档管理
    archiving: {
      isArchiving: false,            // 是否正在归档
      archiveError: null,            // 归档错误信息
      versions: [],                  // 归档版本列表
      currentVersion: null           // 当前版本号
    }
  }),

  // ===== 计算属性 =====
  getters: {
    // 获取复核结果数据
    getReviewResultData: (state) => state.reviewResult.data,
    
    // 获取加载状态
    isLoading: (state) => state.reviewResult.loading,
    
    // 获取错误信息
    getError: (state) => state.reviewResult.error,
    

    
    // 获取归档版本列表
    getArchiveVersions: (state) => state.archiving.versions,
    
    // 获取当前版本
    getCurrentVersion: (state) => state.archiving.currentVersion
  },

  // ===== 操作方法 =====
  actions: {
    // ===== 数据加载 =====
    
    /**
     * 从本地JSON文件加载复核结果数据
     * @param {string} eventId - 重大事项ID
     */
    async loadReviewResult(eventId) {
      this.reviewResult.loading = true
      this.reviewResult.error = null
      
      try {
        // 仅解析后端持久化的真实复核结果
        const workspaceStore = useWorkspaceStore()
        const persisted = await workspaceStore.queryReviewResult(eventId)

        if (persisted && persisted.data) {
          const backendData = persisted.data || {}
          this.reviewResult.data = backendData
          this.reviewResult.lastUpdated = new Date()

          // 保存复核配置到元数据（不展示，仅存储）
          this.reviewResult.data_meta = {
            ...(this.reviewResult.data_meta || {}),
            review_config: persisted.review_config || {}
          }
        } else {
          // 无后端数据时保持为空并提示错误（不再使用mock数据）
          this.reviewResult.data = {}
          this.reviewResult.error = '未查询到复核结果'
        }

        // 加载已保存的版本列表
        try {
          const savedVersions = localStorage.getItem('reviewResult_versions')
          if (savedVersions) {
            this.archiving.versions = JSON.parse(savedVersions)
            if (this.archiving.versions.length > 0) {
              this.archiving.currentVersion = this.archiving.versions[0].version
            }
          }
        } catch (error) {
          console.error('加载版本列表失败:', error)
        }
        
        console.log('复核结果数据加载成功:', this.reviewResult.data)
        
      } catch (error) {
        this.reviewResult.error = error.message
        console.error('加载复核结果失败:', error)
        throw error
      } finally {
        this.reviewResult.loading = false
      }
    },



    // ===== 归档管理 =====
    

    
    /**
     * 保存并归档当前结果
     * @param {Object} archiveData - 归档数据
     */
    async saveAndArchive(archiveData = {}) {
      this.archiving.isArchiving = true
      
      try {
        // 生成版本号
        const versionNumber = this.generateVersionNumber()
        
        // 创建归档包
        const archivePackage = {
          version: versionNumber,
          timestamp: new Date().toISOString(),
          data: JSON.parse(JSON.stringify(this.reviewResult.data)),
          metadata: {
            comments: archiveData.comments || '',

          }
        }
        
        // 保存到版本列表
        this.archiving.versions.unshift(archivePackage)
        if (this.archiving.versions.length > 10) {
          this.archiving.versions = this.archiving.versions.slice(0, 10)
        }
        
        // 保存到localStorage并更新状态
        localStorage.setItem('reviewResult_versions', JSON.stringify(this.archiving.versions))
        this.archiving.currentVersion = versionNumber
        this.reviewResult.status = 'archived'
        this.reviewResult.version = versionNumber
        
        // 触发复核结束的消息事件
        this.triggerReviewCompletedMessage(versionNumber)
        
        return { success: true, version: versionNumber }
      } catch (error) {
        console.error('归档失败:', error)
        throw new Error('归档失败')
      } finally {
        this.archiving.isArchiving = false
      }
    },
    
    /**
     * 触发复核结束的消息事件
     * 通过全局事件系统通知workbenchview显示复核结束消息
     */
    triggerReviewCompletedMessage(versionNumber) {
      try {
        // 创建自定义事件
        const event = new CustomEvent('reviewCompleted', {
          detail: {
            version: versionNumber,
            timestamp: new Date().toISOString(),
            message: '复核工作已全部完成'
          }
        })
        
        // 分发事件
        window.dispatchEvent(event)
        
        console.log('复核结束消息事件已触发:', { version: versionNumber })
      } catch (error) {
        console.error('触发复核结束消息失败:', error)
      }
    },
    
    /**
     * 更新全局状态
     * 归档成功后更新重大事项状态为"已复核"
     */
    async updateGlobalStatus() {
      try {
        const workspaceStore = useWorkspaceStore()
        
        // 获取当前复核的事项ID
        let currentEventId = null
        
        // 尝试从workspace store获取当前复核事项
        if (workspaceStore.currentReviewEvent?.id) {
          currentEventId = workspaceStore.currentReviewEvent.id
        } else {
          // 从localStorage获取当前复核事项
          const savedEvent = localStorage.getItem('currentReviewEvent')
          if (savedEvent) {
            const eventData = JSON.parse(savedEvent)
            currentEventId = eventData.id
          }
        }
        
        // 如果找到了事项ID，更新其状态
        if (currentEventId && workspaceStore.updateMajorEventStatus) {
          await workspaceStore.updateMajorEventStatus(
            currentEventId,
            'reviewed', // 状态更新为"已复核"
            { 
              version: this.archiving.currentVersion,
              timestamp: new Date().toISOString(),
              reviewCompleted: true
            }
          )
          
          console.log(`重大事项 ${currentEventId} 状态已更新为"已复核"`)
        } else {
          console.warn('未找到当前复核事项ID，跳过状态更新')
        }
        
        console.log('全局状态更新成功')
      } catch (error) {
        console.error('更新全局状态失败:', error)
        // 不抛出错误，避免影响归档流程
      }
    },
    
    /**
     * 获取指定版本的数据
     * @param {string} version - 版本号
     */
    getVersionData(version) {
      const versionData = this.archiving.versions.find(v => v.version === version)
      return versionData ? versionData.data : null
    },
    
    /**
     * 恢复到指定版本
     * @param {string} version - 版本号
     */
    restoreVersion(version) {
      const versionData = this.getVersionData(version)
      if (versionData) {
        this.reviewResult.data = JSON.parse(JSON.stringify(versionData))
        this.reviewResult.version = version

        console.log('恢复到版本:', version)
      } else {
        throw new Error(`版本 ${version} 不存在`)
      }
    },

    // ===== 工具方法 =====
    
    /**
     * 生成版本号
     * 格式：V + 年月日时分秒 + 3位随机数
     * 例如：V202403211435001
     */
    generateVersionNumber() {
      const now = new Date()
      const datePart = now.getFullYear().toString().slice(-2) +
        String(now.getMonth() + 1).padStart(2, '0') +
        String(now.getDate()).padStart(2, '0') +
        String(now.getHours()).padStart(2, '0') +
        String(now.getMinutes()).padStart(2, '0') +
        String(now.getSeconds()).padStart(2, '0')
      const randomPart = Math.floor(Math.random() * 1000).toString().padStart(3, '0')
      return `V${datePart}${randomPart}`
    },

    /**
     * 保存版本列表到localStorage
     */
    saveVersionsToStorage() {
      try {
        localStorage.setItem('reviewResult_versions', JSON.stringify(this.archiving.versions))
        console.log('版本列表已保存到localStorage')
      } catch (error) {
        console.error('保存版本列表失败:', error)
      }
    },

    /**
     * 重置状态
     */
    resetState() {
      this.reviewResult.data = null
      this.reviewResult.loading = false
      this.reviewResult.error = null
      this.reviewResult.lastUpdated = null
      this.reviewResult.version = null
      this.reviewResult.status = 'draft'
      

      
      this.archiving.currentVersion = null
      this.archiving.isArchiving = false
      this.archiving.archiveError = null
    },
    
    /**
     * 清除localStorage中的数据
     */
    clearStorageData() {
      try {
        localStorage.removeItem('reviewResult_versions')
        this.archiving.versions = []
        console.log('localStorage数据已清除')
      } catch (error) {
        console.error('清除localStorage数据失败:', error)
      }
    }
  }
})