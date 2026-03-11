// 前端文件管理工具
import { fileAPI } from './api.js'

// 文件类型配置
const ALLOWED_FILE_TYPES = {
  'application/pdf': '.pdf',
  'application/msword': '.doc',
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document': '.docx',
  'application/vnd.ms-excel': '.xls',
  'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': '.xlsx',
  'text/plain': '.txt'
}

const MAX_FILE_SIZE = 50 * 1024 * 1024 // 50MB

export class FileManager {
  constructor() {
    this.allowedTypes = ALLOWED_FILE_TYPES
    this.maxFileSize = MAX_FILE_SIZE
  }

  // 验证文件类型
  validateFileType(file) {
    return Object.keys(this.allowedTypes).includes(file.type) ||
           Object.values(this.allowedTypes).some(ext => file.name.toLowerCase().endsWith(ext))
  }

  // 验证文件大小
  validateFileSize(file) {
    return file.size <= this.maxFileSize
  }

  // 格式化文件大小
  formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes'
    
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  // 获取文件图标
  getFileIcon(fileName) {
    const extension = fileName.split('.').pop()?.toLowerCase()
    
    const iconMap = {
      'pdf': '📄',
      'doc': '📝',
      'docx': '📝',
      'xls': '📊',
      'xlsx': '📊',
      'txt': '📄'
    }
    
    return iconMap[extension] || '📎'
  }

  // 单文件上传
  async uploadFile(file, onProgress) {
    try {
      if (!this.validateFileType(file)) {
        throw new Error('不支持的文件类型')
      }
      
      if (!this.validateFileSize(file)) {
        throw new Error('文件大小超过限制')
      }
      
      const result = await fileAPI.uploadFile(file, onProgress)
      return {
        success: true,
        data: result.data
      }
    } catch (error) {
      return {
        success: false,
        error: error.message
      }
    }
  }

  // 多文件上传
  async uploadMultipleFiles(files, onProgress) {
    const results = []
    let totalProgress = 0
    
    for (let i = 0; i < files.length; i++) {
      const file = files[i]
      
      try {
        if (!this.validateFileType(file)) {
          results.push({
            success: false,
            error: '不支持的文件类型',
            file: { name: file.name }
          })
          continue
        }
        
        if (!this.validateFileSize(file)) {
          results.push({
            success: false,
            error: '文件大小超过限制',
            file: { name: file.name }
          })
          continue
        }
        
        const result = await fileAPI.uploadFile(file, (progress) => {
          const currentFileProgress = progress / files.length
          const overallProgress = totalProgress + currentFileProgress
          if (onProgress) {
            onProgress(Math.round(overallProgress))
          }
        })
        
        results.push({
          success: true,
          data: result.data,
          file: result.data
        })
        
      } catch (error) {
        results.push({
          success: false,
          error: error.message,
          file: { name: file.name }
        })
      }
      
      totalProgress = ((i + 1) / files.length) * 100
      if (onProgress) {
        onProgress(Math.round(totalProgress))
      }
    }
    
    return results
  }

  // 下载文件
  downloadFile(fileId, fileName) {
    fileAPI.downloadFile(fileId, fileName)
  }

  // 删除文件
  async deleteFile(fileId) {
    try {
      await fileAPI.deleteFile(fileId)
      return { success: true }
    } catch (error) {
      return {
        success: false,
        error: error.message
      }
    }
  }

  /**
   * 获取文件列表
   * 
   * 从服务器获取当前用户的所有文件列表
   * 支持分页、搜索、筛选等功能
   * 
   * @param {Object} params - 查询参数
   * @param {string} params.category - 文件分类过滤
   * @param {string} params.search - 搜索关键词
   * @param {number} params.limit - 分页限制
   * @param {number} params.offset - 分页偏移
   * @returns {Promise<Object>} 文件列表响应对象
   * 
   * 使用示例：
   * ```javascript
   * const result = await fileManager.getFiles({ category: 'document', limit: 10 })
   * console.log('文件列表:', result.data.files)
   * console.log('总数量:', result.data.totalCount)
   * ```
   */
  async getFiles(params = {}) {
    try {
      const response = await fileAPI.getFiles(params)
      return response
    } catch (error) {
      console.error('获取文件列表失败:', error)
      throw new Error('获取文件列表失败')
    }
  }

  /**
   * 获取文件预览URL
   * 
   * 为图片文件创建预览URL，用于在界面中显示缩略图
   * 支持本地文件对象和服务器文件ID两种方式
   * 
   * @param {File|string} fileOrId - 文件对象或文件ID
   * @returns {string|null} 预览URL或null（非图片文件）
   * 
   * 使用示例：
   * ```javascript
   * // 本地文件预览
   * const previewUrl = fileManager.getPreviewUrl(file)
   * if (previewUrl) {
   *   imageElement.src = previewUrl
   * }
   * 
   * // 服务器文件预览
   * const serverPreviewUrl = fileManager.getPreviewUrl('file_id_123')
   * imageElement.src = serverPreviewUrl
   * ```
   * 
   * 注意事项：
   * - 本地文件仅支持图片文件类型
   * - 本地文件返回的URL需要在使用完毕后调用revokePreviewUrl释放
   * - 服务器文件直接返回预览API地址
   */
  getPreviewUrl(fileOrId) {
    // 如果是字符串，认为是服务器文件ID
    if (typeof fileOrId === 'string') {
      return fileAPI.getPreviewUrl(fileOrId)
    }
    
    // 如果是文件对象，创建本地预览URL
    if (fileOrId && fileOrId.type && fileOrId.type.startsWith('image/')) {
      return URL.createObjectURL(fileOrId)
    }
    
    return null
  }

  /**
   * 批量删除文件
   * 
   * 删除多个文件，支持批量操作
   * 
   * @param {Array<string>} fileIds - 要删除的文件ID数组
   * @returns {Promise<Object>} 批量删除结果
   * 
   * 使用示例：
   * ```javascript
   * const result = await fileManager.batchDeleteFiles(['id1', 'id2', 'id3'])
   * console.log('删除结果:', result.data)
   * ```
   */
  async batchDeleteFiles(fileIds) {
    try {
      const response = await fileAPI.batchDeleteFiles(fileIds)
      return response
    } catch (error) {
      console.error('批量删除文件失败:', error)
      throw new Error('批量删除文件失败')
    }
  }
}

// 导出单例实例
export const fileManager = new FileManager()
export default fileManager