import { defineStore } from 'pinia'
import { documentAPI } from '../utils/api.js'

// 数据库接口预留方法 - 使用localStorage模拟数据库操作
const DB_KEYS = {
  DRAFT_FILES: 'draft_files',
  FILE_PREFERENCES: 'file_preferences',
  UPLOAD_HISTORY: 'upload_history'
}

export const useDocumentStore = defineStore('document', {
  state: () => ({
    documents: [],
    uploadedFiles: [],
    currentDocument: null,
    loading: false,
    uploading: false,
    error: null,
    uploadError: null
  }),
  
  getters: {
    getDocuments: (state) => state.documents,
    getUploadedFiles: (state) => state.uploadedFiles,
    getCurrentDocument: (state) => state.currentDocument,
    isLoading: (state) => state.loading,
    isUploading: (state) => state.uploading,
    getError: (state) => state.error,
    getUploadError: (state) => state.uploadError,
    getAllFiles: (state) => [...state.documents, ...state.uploadedFiles]
  },
  
  actions: {
    async fetchDocuments() {
      this.loading = true
      this.error = null
      try {
        const response = await documentAPI.getDocuments()
        this.documents = response.data || []
      } catch (error) {
        this.error = error.message
        console.error('获取文档失败:', error)
        // 如果API调用失败，使用模拟数据
        this.documents = [
          { id: 1, name: '审计报告初稿.docx', type: '报告', size: '2.3MB' },
          { id: 2, name: '财务数据表.xlsx', type: '表格', size: '1.1MB' },
          { id: 3, name: '会议纪要.pdf', type: 'PDF', size: '0.5MB' }
        ]
      } finally {
        this.loading = false
      }
    },
    
    async fetchUploadedFiles() {
      this.loading = true
      this.error = null
      try {
        const response = await documentAPI.getUploadedFiles()
        // 后端返回格式: { success: true, files: [...] }
        const files = response.files || response.data || response || []
        this.uploadedFiles = files
        return files
      } catch (error) {
        this.error = error.message
        console.error('获取上传文件失败:', error)
        // 返回空数组而不是抛出错误
        return []
      } finally {
        this.loading = false
      }
    },
    
    addUploadedFile(file) {
      // 添加上传成功的文件到store
      const fileData = {
        id: file.serverId || Date.now(),
        serverId: file.serverId,
        name: file.name,
        originalName: file.originalName || file.name,
        size: file.size,
        type: file.type,
        url: file.url,
        uploadTime: new Date().toISOString(),
        status: 'completed'
      }
      
      // 检查是否已存在，避免重复添加
      const existingIndex = this.uploadedFiles.findIndex(f => f.serverId === file.serverId)
      if (existingIndex >= 0) {
        this.uploadedFiles[existingIndex] = fileData
      } else {
        this.uploadedFiles.push(fileData)
      }
    },
    
    removeUploadedFile(fileId) {
      const index = this.uploadedFiles.findIndex(f => f.id === fileId || f.serverId === fileId)
      if (index >= 0) {
        this.uploadedFiles.splice(index, 1)
      }
    },
    
    async deleteFile(fileId, isUploaded = true) {
      try {
        await documentAPI.deleteFile(fileId)
        if (isUploaded) {
          this.removeUploadedFile(fileId)
        } else {
          const index = this.documents.findIndex(d => d.id === fileId)
          if (index >= 0) {
            this.documents.splice(index, 1)
          }
        }
      } catch (error) {
        this.error = error.message
        console.error('删除文件失败:', error)
        throw error
      }
    },
    
    setCurrentDocument(document) {
      this.currentDocument = document
    },
    
    clearUploadedFiles() {
      this.uploadedFiles = []
    },
    
    setUploading(status) {
      this.uploading = status
    },
    
    setUploadError(error) {
      this.uploadError = error
    },
    
    clearErrors() {
      this.error = null
      this.uploadError = null
    },

    // ==================== 数据库接口预留方法 ====================
    // 使用localStorage模拟数据库操作，预留实际数据库API调用位置
    
    /**
     * 保存底稿文件信息到数据库
     * @param {Object} fileData - 文件数据对象
     * @returns {Promise<Object>} 保存结果
     */
    async saveDraftFileToDatabase(fileData) {
      try {
        // TODO: 替换为实际数据库API调用
        // const response = await databaseAPI.saveDraftFile(fileData)
        
        // 使用localStorage模拟数据库操作
        const existingFiles = this.getDraftFilesFromDatabase()
        const fileWithId = {
          ...fileData,
          id: fileData.id || Date.now(),
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString()
        }
        
        const updatedFiles = [...existingFiles.filter(f => f.id !== fileWithId.id), fileWithId]
        localStorage.setItem(DB_KEYS.DRAFT_FILES, JSON.stringify(updatedFiles))
        
        return { success: true, data: fileWithId }
      } catch (error) {
        console.error('保存底稿文件到数据库失败:', error)
        throw error
      }
    },

    /**
     * 从数据库获取底稿文件列表
     * @returns {Array} 底稿文件列表
     */
    getDraftFilesFromDatabase() {
      try {
        // TODO: 替换为实际数据库API调用
        // const response = await databaseAPI.getDraftFiles()
        // return response.data
        
        // 使用localStorage模拟数据库操作
        const files = localStorage.getItem(DB_KEYS.DRAFT_FILES)
        return files ? JSON.parse(files) : []
      } catch (error) {
        console.error('从数据库获取底稿文件失败:', error)
        return []
      }
    },

    /**
     * 从数据库删除底稿文件
     * @param {string|number} fileId - 文件ID
     * @returns {Promise<Object>} 删除结果
     */
    async deleteDraftFileFromDatabase(fileId) {
      try {
        // TODO: 替换为实际数据库API调用
        // const response = await databaseAPI.deleteDraftFile(fileId)
        
        // 使用localStorage模拟数据库操作
        const existingFiles = this.getDraftFilesFromDatabase()
        const updatedFiles = existingFiles.filter(f => f.id !== fileId)
        localStorage.setItem(DB_KEYS.DRAFT_FILES, JSON.stringify(updatedFiles))
        
        return { success: true, deletedId: fileId }
      } catch (error) {
        console.error('从数据库删除底稿文件失败:', error)
        throw error
      }
    },

    /**
     * 保存用户文件选择偏好到数据库
     * @param {Object} preferences - 用户偏好数据
     * @returns {Promise<Object>} 保存结果
     */
    async saveFilePreferencesToDatabase(preferences) {
      try {
        // TODO: 替换为实际数据库API调用
        // const response = await databaseAPI.saveFilePreferences(preferences)
        
        // 使用localStorage模拟数据库操作
        const preferencesWithTimestamp = {
          ...preferences,
          updatedAt: new Date().toISOString()
        }
        localStorage.setItem(DB_KEYS.FILE_PREFERENCES, JSON.stringify(preferencesWithTimestamp))
        
        return { success: true, data: preferencesWithTimestamp }
      } catch (error) {
        console.error('保存文件偏好到数据库失败:', error)
        throw error
      }
    },

    /**
     * 从数据库获取用户文件选择偏好
     * @returns {Object} 用户偏好数据
     */
    getFilePreferencesFromDatabase() {
      try {
        // TODO: 替换为实际数据库API调用
        // const response = await databaseAPI.getFilePreferences()
        // return response.data
        
        // 使用localStorage模拟数据库操作
        const preferences = localStorage.getItem(DB_KEYS.FILE_PREFERENCES)
        return preferences ? JSON.parse(preferences) : {}
      } catch (error) {
        console.error('从数据库获取文件偏好失败:', error)
        return {}
      }
    },

    /**
     * 保存文件上传历史记录到数据库
     * @param {Object} uploadRecord - 上传记录数据
     * @returns {Promise<Object>} 保存结果
     */
    async saveUploadHistoryToDatabase(uploadRecord) {
      try {
        // TODO: 替换为实际数据库API调用
        // const response = await databaseAPI.saveUploadHistory(uploadRecord)
        
        // 使用localStorage模拟数据库操作
        const existingHistory = this.getUploadHistoryFromDatabase()
        const recordWithId = {
          ...uploadRecord,
          id: uploadRecord.id || Date.now(),
          timestamp: new Date().toISOString()
        }
        
        const updatedHistory = [recordWithId, ...existingHistory.slice(0, 99)] // 保留最近100条记录
        localStorage.setItem(DB_KEYS.UPLOAD_HISTORY, JSON.stringify(updatedHistory))
        
        return { success: true, data: recordWithId }
      } catch (error) {
        console.error('保存上传历史到数据库失败:', error)
        throw error
      }
    },

    /**
     * 从数据库获取文件上传历史记录
     * @param {number} limit - 限制返回记录数量
     * @returns {Array} 上传历史记录列表
     */
    getUploadHistoryFromDatabase(limit = 50) {
      try {
        // TODO: 替换为实际数据库API调用
        // const response = await databaseAPI.getUploadHistory(limit)
        // return response.data
        
        // 使用localStorage模拟数据库操作
        const history = localStorage.getItem(DB_KEYS.UPLOAD_HISTORY)
        const records = history ? JSON.parse(history) : []
        return records.slice(0, limit)
      } catch (error) {
        console.error('从数据库获取上传历史失败:', error)
        return []
      }
    },

    /**
     * 清空数据库中的所有底稿文件数据（用于测试或重置）
     * @returns {Promise<Object>} 清空结果
     */
    async clearDraftFilesDatabase() {
      try {
        // TODO: 替换为实际数据库API调用
        // const response = await databaseAPI.clearDraftFiles()
        
        // 使用localStorage模拟数据库操作
        localStorage.removeItem(DB_KEYS.DRAFT_FILES)
        localStorage.removeItem(DB_KEYS.FILE_PREFERENCES)
        localStorage.removeItem(DB_KEYS.UPLOAD_HISTORY)
        
        return { success: true, message: '数据库已清空' }
      } catch (error) {
        console.error('清空数据库失败:', error)
        throw error
      }
    }
  }
})