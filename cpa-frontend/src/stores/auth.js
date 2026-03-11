/**
 * stores/auth.js - 用户认证状态管理
 * 
 * 功能说明：
 * 1. 管理用户登录状态和用户信息
 * 2. 处理用户认证token的存储和管理
 * 3. 提供登录、登出、状态初始化等操作
 * 4. 实现数据持久化，支持页面刷新后状态恢复
 * 5. 提供数据库接口预留方法，支持用户验证和密码重置
 * 6. 实现登录失败次数限制和账号锁定功能
 * 
 * 状态管理逻辑：
 * - 使用Pinia进行状态管理，提供响应式的用户状态
 * - 状态变更会自动触发相关组件的重新渲染
 * - 通过getters提供计算属性，便于组件访问状态
 * 
 * 存储与数据持久化逻辑：
 * - 用户信息和token存储在localStorage中
 * - 应用启动时自动从localStorage恢复状态
 * - 登出时清除所有本地存储的认证信息
 * - 使用localStorage模拟数据库操作，预留实际API调用位置
 * 
 * 组件与交互逻辑：
 * - 登录组件调用authenticateUser方法进行用户验证
 * - 路由守卫通过isAuthenticated检查登录状态
 * - 导航组件通过getters获取用户信息显示
 * - 支持登录失败次数限制和账号锁定机制
 */

// 导入Pinia的defineStore函数
import { defineStore } from 'pinia'

/**
 * 用户认证状态管理Store
 * 
 * 使用Pinia的defineStore创建认证相关的状态管理
 * Store名称: 'auth'
 */
export const useAuthStore = defineStore('auth', {
  /**
   * 状态定义
   * 
   * 定义认证相关的响应式状态数据
   * 这些状态会在整个应用中共享，并且状态变更会触发相关组件更新
   */
  state: () => ({
    /**
     * 用户信息对象
     * 
     * 存储当前登录用户的详细信息
     * 类型: Object | null
     * 初始值: null（未登录状态）
     * 包含字段: username, email, role等用户属性
     */
    user: null,
    
    /**
     * 用户认证状态标识
     * 
     * 标识用户是否已经通过身份验证
     * 类型: Boolean
     * 初始值: false（未认证状态）
     * 用途: 路由守卫、条件渲染、权限控制
     */
    isAuthenticated: false,
    
    /**
     * 认证令牌
     * 
     * 存储用户的身份验证token，用于API请求认证
     * 类型: String | null
     * 初始值: 从localStorage恢复或null
     * 用途: API请求头、身份验证、会话管理
     */
    token: localStorage.getItem('authToken') || null,
    
    /**
     * 登录错误信息
     * 
     * 存储登录过程中的错误信息
     * 类型: String
     * 初始值: 空字符串
     * 用途: 显示登录失败原因给用户
     */
    loginError: '',
    
    /**
     * 登录加载状态
     * 
     * 标识是否正在进行登录验证
     * 类型: Boolean
     * 初始值: false
     * 用途: 控制登录按钮状态，防止重复提交
     */
    isLoading: false
  }),
  
  /**
   * 计算属性（Getters）
   * 
   * 提供基于state的计算属性，类似于Vue组件中的computed
   * 这些属性会根据state的变化自动重新计算
   */
  getters: {
    /**
     * 获取当前用户信息
     * 
     * @param {Object} state - 当前store的state
     * @returns {Object|null} 用户信息对象或null
     * 
     * 使用场景：
     * - 在组件中显示用户名、头像等信息
     * - 根据用户角色显示不同的界面元素
     */
    getUser: (state) => state.user,
    
    /**
     * 检查用户是否已登录
     * 
     * @param {Object} state - 当前store的state
     * @returns {Boolean} 登录状态
     * 
     * 使用场景：
     * - 条件渲染登录/登出按钮
     * - 路由守卫中的权限检查
     * - 组件中的逻辑判断
     */
    isLoggedIn: (state) => state.isAuthenticated
  },
  
  /**
   * 操作方法（Actions）
   * 
   * 定义修改state的方法，类似于Vuex中的mutations和actions
   * 这些方法可以是同步或异步的
   */
  actions: {
    /**
     * 数据库接口预留方法 - 用户认证
     * 
     * 向服务器发送用户认证请求，验证用户名和密码
     * 当前使用localStorage模拟数据库操作
     * 
     * @param {string} username - 用户名
     * @param {string} password - 密码
     * @returns {Promise<Object>} 认证结果
     * 
     * TODO: 替换为实际的API调用
     * 实际实现时应调用: await api.post('/auth/login', { username, password })
     */
    async authenticateUser(username, password) {
      try {
        this.isLoading = true
        this.loginError = ''
        
        // 检查账号是否被锁定
        const lockInfo = this.checkAccountLock(username)
        if (lockInfo.isLocked) {
          throw new Error(`账号已被锁定，请在${Math.ceil(lockInfo.remainingTime / 60000)}分钟后重试`)
        }
        
        // 模拟网络请求和错误处理
        await this.simulateNetworkRequest()
        
        // 使用localStorage模拟数据库用户验证
        const isValid = await this.validateUserCredentials(username, password)
        
        if (isValid) {
          // 验证成功，清除失败记录
          this.clearLoginFailures(username)
          
          // 模拟从数据库获取用户信息
          const userData = await this.getUserFromDatabase(username)
          
          // 设置用户登录状态
          this.setUser(userData)
          
          return { success: true, user: userData }
        } else {
          // 验证失败，记录失败次数
          this.recordLoginFailure(username)
          throw new Error('用户名或密码错误')
        }
      } catch (error) {
        // 处理不同类型的错误
        this.loginError = this.handleError(error)
        throw error
      } finally {
        this.isLoading = false
      }
    },
    
    /**
     * 数据库接口预留方法 - 验证用户凭据
     * 
     * 使用localStorage模拟数据库用户验证
     * 
     * @param {string} username - 用户名
     * @param {string} password - 密码
     * @returns {Promise<boolean>} 验证结果
     * 
     * TODO: 替换为实际的数据库查询
     */
    async validateUserCredentials(username, password) {
      // 模拟数据库中的用户数据
      const users = JSON.parse(localStorage.getItem('mockUsers') || '[]')
      
      // 如果没有模拟用户数据，创建默认用户
      if (users.length === 0) {
        const defaultUsers = [
          { username: 'admin', password: 'admin123', email: 'admin@cpa.com', role: 'admin' },
          { username: 'user', password: 'user123', email: 'user@cpa.com', role: 'user' }
        ]
        localStorage.setItem('mockUsers', JSON.stringify(defaultUsers))
        return defaultUsers.some(user => user.username === username && user.password === password)
      }
      
      return users.some(user => user.username === username && user.password === password)
    },
    
    /**
     * 数据库接口预留方法 - 获取用户信息
     * 
     * 从数据库获取用户详细信息
     * 
     * @param {string} username - 用户名
     * @returns {Promise<Object>} 用户信息
     * 
     * TODO: 替换为实际的数据库查询
     */
    async getUserFromDatabase(username) {
      const users = JSON.parse(localStorage.getItem('mockUsers') || '[]')
      const user = users.find(u => u.username === username)
      
      if (user) {
        return {
          id: Date.now(), // 模拟用户ID
          username: user.username,
          email: user.email,
          role: user.role
        }
      }
      
      throw new Error('用户不存在')
    },
    
    /**
     * 检查账号锁定状态
     * 
     * @param {string} username - 用户名
     * @returns {Object} 锁定信息
     */
    checkAccountLock(username) {
      const lockKey = `accountLock_${username}`
      const lockData = localStorage.getItem(lockKey)
      
      if (lockData) {
        const { lockTime, failures } = JSON.parse(lockData)
        const now = Date.now()
        const lockDuration = 5 * 60 * 1000 // 5分钟
        
        if (failures >= 3 && (now - lockTime) < lockDuration) {
          return {
            isLocked: true,
            remainingTime: lockDuration - (now - lockTime)
          }
        }
      }
      
      return { isLocked: false }
    },
    
    /**
     * 记录登录失败
     * 
     * @param {string} username - 用户名
     */
    recordLoginFailure(username) {
      const lockKey = `accountLock_${username}`
      const lockData = localStorage.getItem(lockKey)
      
      let failures = 1
      if (lockData) {
        const data = JSON.parse(lockData)
        failures = data.failures + 1
      }
      
      localStorage.setItem(lockKey, JSON.stringify({
        failures,
        lockTime: Date.now()
      }))
    },
    
    /**
     * 清除登录失败记录
     * 
     * @param {string} username - 用户名
     */
    clearLoginFailures(username) {
      const lockKey = `accountLock_${username}`
      localStorage.removeItem(lockKey)
    },
    
    /**
     * 模拟网络请求和错误处理
     * 
     * 模拟真实网络环境中可能出现的各种情况
     * 包括网络延迟、超时、连接失败等
     */
    async simulateNetworkRequest() {
      // 模拟网络延迟（500-2000ms）
      const delay = Math.random() * 1500 + 500
      
      // 模拟网络错误概率（5%的概率出现网络错误）
      const errorProbability = Math.random()
      
      await new Promise((resolve, reject) => {
        setTimeout(() => {
          if (errorProbability < 0.05) {
            // 模拟网络连接失败
            reject(new Error('NETWORK_ERROR'))
          } else if (errorProbability < 0.08) {
            // 模拟服务器无响应
            reject(new Error('SERVER_TIMEOUT'))
          } else if (errorProbability < 0.1) {
            // 模拟服务器内部错误
            reject(new Error('SERVER_ERROR'))
          } else {
            resolve()
          }
        }, delay)
      })
    },
    
    /**
     * 统一错误处理方法
     * 
     * 根据不同的错误类型返回用户友好的错误信息
     * 
     * @param {Error} error - 错误对象
     * @returns {string} 用户友好的错误信息
     */
    handleError(error) {
      const errorMessage = error.message
      
      // 网络相关错误
      if (errorMessage === 'NETWORK_ERROR') {
        return '网络连接失败，请检查网络连接后重试'
      }
      
      if (errorMessage === 'SERVER_TIMEOUT') {
        return '服务器响应超时，请稍后再试'
      }
      
      if (errorMessage === 'SERVER_ERROR') {
        return '服务器内部错误，请稍后再试或联系管理员'
      }
      
      // 账号锁定相关错误
      if (errorMessage.includes('账号已被锁定')) {
        return errorMessage
      }
      
      // 验证相关错误
      if (errorMessage.includes('用户名或密码错误')) {
        return errorMessage
      }
      
      if (errorMessage.includes('用户不存在')) {
        return '用户不存在，请检查用户名是否正确'
      }
      
      // 密码重置相关错误
      if (errorMessage.includes('验证码')) {
        return errorMessage
      }
      
      if (errorMessage.includes('手机号')) {
        return errorMessage
      }
      
      // 默认错误信息
      return '操作失败，请重试或联系管理员'
    },
    
    /**
     * 设置用户信息
     * 
     * 用于更新用户信息并设置认证状态
     * 通常在用户信息更新时调用
     * 
     * @param {Object} userData - 用户数据对象
     * @param {string} userData.username - 用户名
     * @param {string} userData.email - 用户邮箱
     * @param {string} userData.role - 用户角色
     * 
     * 存储与数据持久化：
     * - 将用户信息保存到localStorage
     * - 确保页面刷新后用户信息不丢失
     */
    setUser(userData) {
      // 更新store中的用户信息
      this.user = userData
      // 设置认证状态为已认证
      this.isAuthenticated = true
      // 清除登录错误信息
      this.loginError = ''
      // 持久化用户信息到本地存储
      localStorage.setItem('userInfo', JSON.stringify(userData))
    },
    
    /**
     * 用户登录
     * 
     * 处理用户登录逻辑，设置用户状态和认证信息
     * 这是认证流程的核心方法
     * 
     * @param {Object} userData - 登录成功后的用户数据
     * @param {string} userData.username - 用户名
     * @param {string} userData.email - 用户邮箱
     * @param {string} [userData.token] - 认证token（可选）
     * @param {string} userData.role - 用户角色
     * 
     * 状态管理逻辑：
     * - 更新用户信息和认证状态
     * - 触发相关组件的重新渲染
     * 
     * 存储与数据持久化：
     * - 保存token和用户信息到localStorage
     * - 支持会话持久化和状态恢复
     */
    login(userData) {
      // 设置用户信息
      this.user = userData
      // 设置认证状态
      this.isAuthenticated = true
      
      // 处理认证token
      if (userData.token) {
        this.token = userData.token
        // 持久化token到本地存储
        localStorage.setItem('authToken', userData.token)
      }
      
      // 持久化用户信息到本地存储
      localStorage.setItem('userInfo', JSON.stringify(userData))
    },
    
    /**
     * 用户登出
     * 
     * 清除所有用户相关的状态和本地存储数据
     * 将应用恢复到未认证状态
     * 
     * 状态管理逻辑：
     * - 重置所有认证相关的状态
     * - 触发组件重新渲染，显示未登录状态
     * 
     * 存储与数据持久化：
     * - 清除localStorage中的所有认证信息
     * - 确保用户隐私和安全
     * 
     * 组件与交互逻辑：
     * - 通常在用户点击登出按钮时调用
     * - 登出后重定向到登录页面
     */
    logout() {
      // 清除用户信息
      this.user = null
      // 重置认证状态
      this.isAuthenticated = false
      // 清除认证token
      this.token = null
      
      // 清除本地存储的认证信息
      localStorage.removeItem('authToken')
      localStorage.removeItem('userInfo')
    },
    
    /**
     * 数据库接口预留方法 - 密码重置请求
     * 
     * 发送密码重置请求，验证用户身份并发送验证码
     * 
     * @param {string} username - 用户名
     * @param {string} phone - 注册手机号
     * @returns {Promise<Object>} 重置结果
     * 
     * TODO: 替换为实际的API调用
     */
    async requestPasswordReset(username, phone) {
      try {
        this.isLoading = true
        this.loginError = ''
        
        // 模拟网络请求和错误处理
        await this.simulateNetworkRequest()
        
        // 验证用户和手机号是否匹配
        const users = JSON.parse(localStorage.getItem('mockUsers') || '[]')
        const user = users.find(u => u.username === username)
        
        if (!user) {
          throw new Error('用户不存在')
        }
        
        // 模拟手机号验证（实际应从数据库获取用户注册手机号）
        const userPhone = user.phone || '138****8888' // 模拟数据
        if (phone !== userPhone) {
          throw new Error('手机号与注册信息不匹配')
        }
        
        // 生成验证码（实际应发送短信）
        const verificationCode = Math.floor(100000 + Math.random() * 900000).toString()
        
        // 保存验证码到localStorage（实际应保存到服务器）
        localStorage.setItem(`resetCode_${username}`, JSON.stringify({
          code: verificationCode,
          timestamp: Date.now(),
          phone: phone
        }))
        
        return {
          success: true,
          message: `验证码已发送到手机号 ${phone.replace(/(\d{3})\d{4}(\d{4})/, '$1****$2')}`,
          verificationCode // 仅用于演示，实际不应返回
        }
      } catch (error) {
        this.loginError = this.handleError(error)
        throw error
      } finally {
        this.isLoading = false
      }
    },
    
    /**
     * 数据库接口预留方法 - 验证重置码并更新密码
     * 
     * @param {string} username - 用户名
     * @param {string} verificationCode - 验证码
     * @param {string} newPassword - 新密码
     * @returns {Promise<Object>} 重置结果
     * 
     * TODO: 替换为实际的API调用
     */
    async resetPassword(username, verificationCode, newPassword) {
      try {
        this.isLoading = true
        this.loginError = ''
        
        // 验证验证码
        const resetData = localStorage.getItem(`resetCode_${username}`)
        if (!resetData) {
          throw new Error('验证码已过期，请重新获取')
        }
        
        const { code, timestamp } = JSON.parse(resetData)
        const now = Date.now()
        const codeExpiry = 5 * 60 * 1000 // 5分钟有效期
        
        if (now - timestamp > codeExpiry) {
          localStorage.removeItem(`resetCode_${username}`)
          throw new Error('验证码已过期，请重新获取')
        }
        
        if (code !== verificationCode) {
          throw new Error('验证码错误')
        }
        
        // 更新用户密码
        const users = JSON.parse(localStorage.getItem('mockUsers') || '[]')
        const userIndex = users.findIndex(u => u.username === username)
        
        if (userIndex === -1) {
          throw new Error('用户不存在')
        }
        
        users[userIndex].password = newPassword
        localStorage.setItem('mockUsers', JSON.stringify(users))
        
        // 清除验证码
        localStorage.removeItem(`resetCode_${username}`)
        
        return {
          success: true,
          message: '密码重置成功，请使用新密码登录'
        }
      } catch (error) {
        this.loginError = this.handleError(error)
        throw error
      } finally {
        this.isLoading = false
      }
    },
    
    /**
     * 初始化认证状态
     * 
     * 应用启动时调用，从localStorage恢复用户登录状态
     * 实现会话持久化，用户刷新页面后仍保持登录状态
     * 
     * 存储与数据持久化：
     * - 从localStorage读取保存的用户信息和token
     * - 验证数据完整性后恢复认证状态
     * 
     * 状态管理逻辑：
     * - 只有在token和用户信息都存在时才恢复登录状态
     * - 确保状态的一致性和安全性
     * 
     * 调用时机：
     * - 应用初始化时（main.js）
     * - 路由守卫中检查认证状态时
     */
    initializeAuth() {
      // 从本地存储获取用户信息与认证token（统一使用 authToken）
      const storedUser = localStorage.getItem('userInfo')
      const storedToken = localStorage.getItem('authToken')

      // 仅当两者都存在时恢复登录状态
      if (storedUser && storedToken) {
        try {
          this.user = JSON.parse(storedUser)
          this.token = storedToken
          this.isAuthenticated = true
          this.loginError = ''
        } catch (error) {
          console.error('Failed to parse user info from localStorage:', error)
          this.logout()
        }
      } else {
        // 保持未认证状态，清理残留内存态
        this.token = null
        this.isAuthenticated = false
      }
    }
  }
})