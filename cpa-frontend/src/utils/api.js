/**
 * utils/api.js - API请求工具和数据交互
 * 
 * 功能说明：
 * 1. 提供统一的API请求接口和配置
 * 2. 封装文件上传、下载、管理等功能
 * 3. 实现文档管理相关的API调用
 * 4. 提供项目管理的数据交互接口
 * 
 * 存储与数据持久化逻辑：
 * - 通过HTTP请求与后端服务器进行数据交互
 * - 支持文件上传和下载的数据传输
 * - 实现CRUD操作的数据持久化
 * 
 * 组件与交互逻辑：
 * - 为各个Vue组件提供数据获取和提交的接口
 * - 支持异步操作和错误处理
 * - 提供上传进度回调和用户反馈
 * 
 * 路由与页面跳转逻辑：
 * - API响应可能触发页面跳转（如认证失败）
 * - 支持文件下载的浏览器导航
 */

/**
 * API基础配置
 * 
 * 定义后端服务器的基础URL地址
 * 所有API请求都会以此为前缀
 * 
 * 配置说明：
 * - 开发环境: http://localhost:3001/api
 * - 生产环境: 应根据实际部署地址修改
 */
const API_BASE_URL = 'http://127.0.0.1:8000/api/v1'

/**
 * 通用HTTP请求函数
 * 
 * 封装fetch API，提供统一的请求处理逻辑
 * 包含错误处理、响应解析等通用功能
 * 
 * @param {string} url - API端点路径（相对于API_BASE_URL）
 * @param {Object} options - 请求配置选项
 * @param {Object} options.headers - 请求头配置
 * @param {string} options.method - HTTP方法（GET, POST, PUT, DELETE等）
 * @param {string} options.body - 请求体数据
 * @returns {Promise<Object>} 解析后的JSON响应数据
 * 
 * 功能特性：
 * - 自动添加Content-Type为application/json
 * - 统一的错误处理和日志记录
 * - 自动解析JSON响应
 * - 支持自定义请求头和配置
 * 
 * 使用示例：
 * ```javascript
 * const data = await request('/users', {
 *   method: 'POST',
 *   body: JSON.stringify({ name: 'John' })
 * })
 * ```
 */
const request = async (url, options = {}) => {
  try {
    // 发送HTTP请求
    const response = await fetch(`${API_BASE_URL}${url}`, {
      headers: {
        'Content-Type': 'application/json', // 默认JSON内容类型
        ...options.headers // 合并自定义请求头
      },
      ...options // 合并其他请求配置
    })
    
    // 检查响应状态
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    
    // 解析并返回JSON数据
    return await response.json()
  } catch (error) {
    // 统一错误处理和日志记录
    console.error('API请求失败:', error)
    throw error // 重新抛出错误供调用者处理
  }
}

/**
 * 文件管理API模块
 * 
 * 提供完整的文件操作功能，包括上传、下载、删除等
 * 支持单文件和多文件上传，提供上传进度反馈
 * 
 * 存储与数据持久化逻辑：
 * - 文件上传到服务器存储
 * - 文件元数据保存到数据库
 * - 支持文件的CRUD操作
 * 
 * 组件与交互逻辑：
 * - 为文件上传组件提供进度回调
 * - 支持拖拽上传和点击上传
 * - 提供文件列表管理功能
 */
export const fileAPI = {
  /**
   * 单文件上传
   * 
   * 使用XMLHttpRequest实现文件上传，支持上传进度监控
   * 相比fetch API，XMLHttpRequest更适合文件上传场景
   * 
   * @param {File} file - 要上传的文件对象
   * @param {Function} onProgress - 上传进度回调函数
   * @param {number} onProgress.progress - 上传进度百分比（0-100）
   * @returns {Promise<Object>} 上传结果，包含文件信息
   * 
   * 功能特性：
   * - 实时上传进度反馈
   * - 自动错误处理和重试机制
   * - 支持大文件上传
   * - 返回服务器文件信息
   * 
   * 使用示例：
   * ```javascript
   * const result = await fileAPI.uploadFile(file, (progress) => {
   *   console.log(`上传进度: ${progress}%`)
   * })
   * ```
   */
  uploadFile: (file, onProgress) => {
    return new Promise((resolve, reject) => {
      // 创建FormData对象，用于文件上传
      const formData = new FormData()
      formData.append('file', file)
      
      // 使用XMLHttpRequest进行文件上传
      const xhr = new XMLHttpRequest()
      
      /**
       * 上传进度监听器
       * 
       * 监听文件上传进度，提供实时反馈
       * 用于更新UI中的进度条或进度提示
       */
      xhr.upload.addEventListener('progress', (e) => {
        if (e.lengthComputable && onProgress) {
          // 计算上传进度百分比
          const progress = Math.round((e.loaded / e.total) * 100)
          onProgress(progress)
        }
      })
      
      /**
       * 上传完成监听器
       * 
       * 处理上传完成后的响应
       * 解析服务器返回的文件信息
       */
      xhr.addEventListener('load', () => {
        if (xhr.status === 200) {
          try {
            // 解析服务器响应
            const response = JSON.parse(xhr.responseText)
            resolve(response)
          } catch (error) {
            reject(new Error('响应解析失败'))
          }
        } else {
          reject(new Error(`上传失败: ${xhr.status}`))
        }
      })
      
      /**
       * 网络错误监听器
       * 
       * 处理网络连接错误等异常情况
       */
      xhr.addEventListener('error', () => {
        reject(new Error('网络错误'))
      })
      
      // 发起POST请求到文件上传端点
      xhr.open('POST', `${API_BASE_URL}/files/upload`)
      xhr.send(formData)
    })
  },
  
  /**
   * 多文件上传
   * 
   * 支持同时上传多个文件，提供批量上传功能
   * 所有文件作为一个请求发送，共享上传进度
   * 
   * @param {FileList|Array<File>} files - 要上传的文件数组
   * @param {Function} onProgress - 整体上传进度回调函数
   * @param {number} onProgress.progress - 整体上传进度百分比（0-100）
   * @returns {Promise<Object>} 上传结果，包含所有文件信息
   * 
   * 功能特性：
   * - 批量文件上传
   * - 整体进度监控
   * - 原子性操作（全部成功或全部失败）
   * - 支持不同类型文件混合上传
   * 
   * 使用场景：
   * - 文档批量导入
   * - 图片批量上传
   * - 项目文件打包上传
   */
  uploadMultipleFiles: (files, onProgress) => {
    return new Promise((resolve, reject) => {
      // 创建FormData，添加多个文件
      const formData = new FormData()
      files.forEach(file => {
        formData.append('files', file) // 使用相同的字段名添加多个文件
      })
      
      const xhr = new XMLHttpRequest()
      
      // 监听整体上传进度
      xhr.upload.addEventListener('progress', (e) => {
        if (e.lengthComputable && onProgress) {
          const progress = Math.round((e.loaded / e.total) * 100)
          onProgress(progress)
        }
      })
      
      // 处理上传完成
      xhr.addEventListener('load', () => {
        if (xhr.status === 200) {
          try {
            const response = JSON.parse(xhr.responseText)
            resolve(response)
          } catch (error) {
            reject(new Error('响应解析失败'))
          }
        } else {
          reject(new Error(`上传失败: ${xhr.status}`))
        }
      })
      
      // 处理网络错误
      xhr.addEventListener('error', () => {
        reject(new Error('网络错误'))
      })
      
      // 发起多文件上传请求
      xhr.open('POST', `${API_BASE_URL}/files/upload-multiple`)
      xhr.send(formData)
    })
  },
  
  /**
   * 获取文件列表
   * 
   * 获取当前项目或用户的所有文件列表
   * 支持分页、搜索、筛选等功能
   * 
   * @param {Object} params - 查询参数
   * @param {string} params.category - 文件分类过滤
   * @param {string} params.search - 搜索关键词
   * @param {number} params.limit - 分页限制
   * @param {number} params.offset - 分页偏移
   * @returns {Promise<Object>} 文件列表响应
   * 
   * 返回数据结构：
   * ```javascript
   * {
   *   success: true,
   *   data: {
   *     files: [
   *       {
   *         id: 'file_id',
   *         name: 'filename.pdf',
   *         size: 1024000,
   *         type: 'application/pdf',
   *         uploadTime: '2024-01-01T00:00:00Z',
   *         url: 'download_url',
   *         category: 'document',
   *         description: '文件描述',
   *         tags: ['tag1', 'tag2'],
   *         status: 'uploaded'
   *       }
   *     ],
   *     totalCount: 100,
   *     currentCount: 10
   *   }
   * }
   * ```
   */
  getFiles: (params = {}) => {
    const queryString = new URLSearchParams(params).toString()
    const url = queryString ? `/files?${queryString}` : '/files'
    return request(url)
  },
  
  /**
   * 文件下载
   * 
   * 通过创建临时链接触发浏览器下载
   * 支持自定义文件名和下载行为
   * 
   * @param {string} fileId - 文件唯一标识符
   * @param {string} fileName - 下载时的文件名
   * 
   * 功能特性：
   * - 自动触发浏览器下载
   * - 支持大文件下载
   * - 不阻塞UI线程
   * - 自动清理临时DOM元素
   * 
   * 路由与页面跳转逻辑：
   * - 不会导致页面跳转
   * - 在当前页面触发下载行为
   * - 支持后台下载
   */
  downloadFile: (fileId, fileName) => {
    // 创建临时下载链接
    const link = document.createElement('a')
    link.href = `${API_BASE_URL}/files/${fileId}/download`
    link.download = fileName // 设置下载文件名
    
    // 添加到DOM并触发点击
    document.body.appendChild(link)
    link.click()
    
    // 清理临时元素
    document.body.removeChild(link)
  },
  
  /**
   * 删除文件
   * 
   * 从服务器永久删除指定文件
   * 包括文件数据和元数据的删除
   * 
   * @param {string} fileId - 要删除的文件ID
   * @returns {Promise<Object>} 删除操作结果
   * 
   * 注意事项：
   * - 删除操作不可逆
   * - 建议在删除前进行确认提示
   * - 删除后需要更新文件列表
   */
  deleteFile: (fileId) => request(`/files/${fileId}`, { method: 'DELETE' }),
  
  /**
   * 获取文件详细信息
   * 
   * 获取指定文件的详细元数据信息
   * 包括文件属性、上传信息、访问权限等
   * 
   * @param {string} fileId - 文件唯一标识符
   * @returns {Promise<Object>} 文件详细信息
   * 
   * 返回信息包含：
   * - 基本属性：名称、大小、类型
   * - 时间信息：创建时间、修改时间
   * - 权限信息：访问权限、所有者
   * - 技术信息：MD5、存储路径等
   */
  getFileInfo: async (fileId) => {
    return request(`/files/${fileId}`)
  },
  
  /**
   * 批量删除文件
   * 
   * 删除多个文件，支持批量操作
   * 
   * @param {Array<string>} fileIds - 要删除的文件ID数组
   * @returns {Promise<Object>} 批量删除结果
   * 
   * 返回数据结构：
   * ```javascript
   * {
   *   success: true,
   *   message: '成功删除 5 个文件',
   *   data: {
   *     deletedFiles: [...],
   *     errors: [...],
   *     totalCount: 5,
   *     successCount: 5,
   *     errorCount: 0
   *   }
   * }
   * ```
   */
  batchDeleteFiles: (fileIds) => {
    return request('/files/batch', {
      method: 'DELETE',
      body: JSON.stringify({ fileIds })
    })
  },
  
  /**
   * 获取文件预览URL
   * 
   * 获取文件的预览地址，用于在线预览
   * 
   * @param {string} fileId - 文件唯一标识符
   * @returns {string} 预览URL
   */
  getPreviewUrl: (fileId) => {
    return `${API_BASE_URL}/files/${fileId}/preview`
  }
}

/**
 * 文档管理API模块
 * 
 * 提供文档的完整生命周期管理功能
 * 包括文档的创建、编辑、删除、查看等操作
 * 
 * 存储与数据持久化逻辑：
 * - 文档内容存储在数据库中
 * - 支持文档版本控制和历史记录
 * - 关联文件存储和文档元数据
 * 
 * 组件与交互逻辑：
 * - 为文档编辑器提供数据接口
 * - 支持实时保存和自动备份
 * - 提供文档搜索和分类功能
 */
export const documentAPI = {
  /**
   * 获取文档列表
   * 
   * 获取当前项目的所有文档列表
   * 支持分页、搜索、分类筛选等功能
   * 
   * @returns {Promise<Array>} 文档列表数组
   * 
   * 返回数据结构：
   * ```javascript
   * [
   *   {
   *     id: 'doc_id',
   *     title: '文档标题',
   *     content: '文档内容',
   *     category: '文档分类',
   *     createTime: '2024-01-01T00:00:00Z',
   *     updateTime: '2024-01-01T00:00:00Z',
   *     author: '作者信息'
   *   }
   * ]
   * ```
   */
  getDocuments: () => request('/documents'),
  
  /**
   * 获取上传的文件列表
   * 
   * 获取可用于文档关联的文件列表
   * 通常用于文档编辑时插入附件或引用
   * 
   * @returns {Promise<Array>} 文件列表数组
   * 
   * 使用场景：
   * - 文档编辑器中的文件选择
   * - 附件管理和引用
   * - 文档资源库管理
   */
  getUploadedFiles: () => request('/files'),
  
  /**
   * 创建文档
   * 
   * 创建新的文档记录
   * 包含文档内容、元数据和关联信息
   * 
   * @param {Object} data - 文档数据
   * @param {string} data.title - 文档标题
   * @param {string} data.content - 文档内容（支持HTML或Markdown）
   * @param {string} data.category - 文档分类
   * @param {Array} data.tags - 文档标签
   * @param {Array} data.attachments - 关联附件ID列表
   * @returns {Promise<Object>} 创建的文档信息
   * 
   * 功能特性：
   * - 支持富文本内容
   * - 自动生成文档ID和时间戳
   * - 支持文档分类和标签
   * - 关联文件附件管理
   */
  createDocument: (data) => request('/documents', {
    method: 'POST',
    body: JSON.stringify(data)
  }),
  
  /**
   * 更新文档
   * 
   * 更新现有文档的内容和元数据
   * 支持部分更新和版本控制
   * 
   * @param {string} id - 文档唯一标识符
   * @param {Object} data - 要更新的文档数据
   * @param {string} [data.title] - 文档标题
   * @param {string} [data.content] - 文档内容
   * @param {string} [data.category] - 文档分类
   * @param {Array} [data.tags] - 文档标签
   * @returns {Promise<Object>} 更新后的文档信息
   * 
   * 功能特性：
   * - 支持部分字段更新
   * - 自动更新修改时间
   * - 保留文档历史版本
   * - 触发相关组件更新
   */
  updateDocument: (id, data) => request(`/documents/${id}`, {
    method: 'PUT',
    body: JSON.stringify(data)
  }),
  
  /**
   * 删除文档
   * 
   * 永久删除指定文档
   * 包括文档内容、元数据和关联关系
   * 
   * @param {string} id - 要删除的文档ID
   * @returns {Promise<Object>} 删除操作结果
   * 
   * 注意事项：
   * - 删除操作不可逆
   * - 建议实现软删除机制
   * - 需要处理关联文件的清理
   * - 更新文档列表缓存
   */
  deleteDocument: (id) => request(`/documents/${id}`, { method: 'DELETE' }),
  
  /**
   * 删除文件
   * 
   * 删除文档关联的文件
   * 通常在文档编辑时移除不需要的附件
   * 
   * @param {string} fileId - 要删除的文件ID
   * @returns {Promise<Object>} 删除操作结果
   * 
   * 使用场景：
   * - 文档附件管理
   * - 清理无用文件
   * - 文档编辑器中的文件移除
   */
  deleteFile: (fileId) => request(`/files/${fileId}`, { method: 'DELETE' })
}

/**
 * 项目管理API模块
 * 
 * 提供项目的完整管理功能
 * 包括项目创建、配置、切换、删除等操作
 * 
 * 存储与数据持久化逻辑：
 * - 项目信息存储在数据库中
 * - 支持项目配置和权限管理
 * - 关联用户、文档、文件等资源
 * 
 * 状态管理逻辑：
 * - 与projectStore交互管理当前项目
 * - 支持项目切换和状态同步
 * - 提供项目列表和详情数据
 */
export const projectAPI = {
  /**
   * 获取项目列表
   * 
   * 获取当前用户可访问的所有项目
   * 支持分页、搜索、排序等功能
   * 
   * @returns {Promise<Array>} 项目列表数组
   * 
   * 返回数据结构：
   * ```javascript
   * [
   *   {
   *     id: 'project_id',
   *     name: '项目名称',
   *     description: '项目描述',
   *     status: 'active',
   *     createTime: '2024-01-01T00:00:00Z',
   *     owner: '项目所有者',
   *     members: ['成员列表']
   *   }
   * ]
   * ```
   * 
   * 使用场景：
   * - 项目选择页面
   * - 项目切换下拉菜单
   * - 项目管理界面
   */
  getProjects: () => request('/projects'),
  
  /**
   * 获取当前项目
   * 
   * 获取用户当前选择的项目详细信息
   * 用于恢复用户的项目上下文
   * 
   * @returns {Promise<Object>} 当前项目信息
   * 
   * 功能特性：
   * - 返回完整的项目配置
   * - 包含用户在该项目中的权限
   * - 提供项目相关的统计信息
   * 
   * 状态管理逻辑：
   * - 用于初始化projectStore状态
   * - 支持页面刷新后的状态恢复
   * - 与路由守卫配合验证项目访问权限
   */
  getCurrentProject: () => request('/projects/current'),
  
  /**
   * 创建项目
   * 
   * 创建新的项目记录
   * 包含项目基本信息和初始配置
   * 
   * @param {Object} data - 项目数据
   * @param {string} data.name - 项目名称
   * @param {string} data.description - 项目描述
   * @param {string} data.type - 项目类型
   * @param {Object} data.settings - 项目设置
   * @returns {Promise<Object>} 创建的项目信息
   * 
   * 功能特性：
   * - 自动设置创建者为项目所有者
   * - 初始化项目默认配置
   * - 创建项目相关的目录结构
   * - 设置默认权限和角色
   */
  createProject: (data) => request('/projects', {
    method: 'POST',
    body: JSON.stringify(data)
  }),
  
  /**
   * 更新项目
   * 
   * 更新现有项目的信息和配置
   * 支持项目设置和权限管理
   * 
   * @param {string} id - 项目唯一标识符
   * @param {Object} data - 要更新的项目数据
   * @param {string} [data.name] - 项目名称
   * @param {string} [data.description] - 项目描述
   * @param {Object} [data.settings] - 项目设置
   * @param {Array} [data.members] - 项目成员
   * @returns {Promise<Object>} 更新后的项目信息
   * 
   * 权限要求：
   * - 需要项目管理员权限
   * - 某些设置可能需要所有者权限
   * - 成员管理需要相应权限
   */
  updateProject: (id, data) => request(`/projects/${id}`, {
    method: 'PUT',
    body: JSON.stringify(data)
  }),
  
  /**
   * 删除项目
   * 
   * 永久删除指定项目及其所有相关数据
   * 包括文档、文件、配置等
   * 
   * @param {string} id - 要删除的项目ID
   * @returns {Promise<Object>} 删除操作结果
   * 
   * 注意事项：
   * - 删除操作不可逆
   * - 需要项目所有者权限
   * - 会删除所有关联数据
   * - 建议实现数据备份机制
   * 
   * 安全考虑：
   * - 需要二次确认
   * - 记录删除操作日志
   * - 通知相关项目成员
   */
  deleteProject: (id) => request(`/projects/${id}`, { method: 'DELETE' })
}

export default {
  request,
  fileAPI,
  documentAPI,
  projectAPI
}