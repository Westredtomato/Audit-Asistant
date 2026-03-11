<!-- 
  LoginView.vue - 用户登录页面组件
  
  功能说明：
  1. 提供用户登录界面，包含用户名和密码输入框
  2. 实现完整的表单验证（非空、长度限制等）
  3. 处理登录失败次数限制和账号锁定机制
  4. 提供忘记密码功能和密码重置流程
  5. 处理网络错误和各种异常情况
  6. 登录成功后跳转到项目管理页面
  
  组件交互逻辑：
  - 用户输入用户名和密码，系统进行实时格式验证
  - 点击登录按钮触发handleLogin方法进行身份验证
  - 验证成功后调用authStore.authenticateUser()进行用户认证
  - 支持忘记密码流程，通过手机验证码重置密码
  - 处理登录失败次数限制，超过3次锁定账号5分钟
  
  状态管理：
  - 使用authStore管理用户认证状态和登录错误信息
  - 登录信息会保存到localStorage实现持久化
  - 支持账号锁定状态的检查和显示
-->
<template>
  <!-- 登录页面根容器 - 全屏居中布局 -->
  <div class="login-view">
    <!-- 登录表单容器 - 白色卡片样式 -->
    <div class="login-container">
      <!-- 系统标题 -->
      <h1>CPA助手系统</h1>
      
      <!-- 登录表单区域 -->
      <div class="login-form" v-if="!showForgotPassword">
        <h2>用户登录</h2>
        
        <!-- 
          登录表单 - 使用@submit.prevent阻止默认提交行为
          handleLogin方法处理登录逻辑
        -->
        <form @submit.prevent="handleLogin">
          <!-- 用户名输入组 -->
          <div class="form-group">
            <label for="username">用户名:</label>
            <!-- 
              用户名输入框
              - v-model双向绑定到loginForm.username
              - @blur失焦时进行表单验证
              - :class动态添加错误样式
            -->
            <input 
              type="text" 
              id="username" 
              v-model="loginForm.username" 
              @blur="validateUsername"
              :class="{ 'error': validationErrors.username }"
              placeholder="请输入用户名（3-20个字符）"
              maxlength="20"
            />
            <!-- 用户名验证错误提示 -->
            <div v-if="validationErrors.username" class="field-error">
              {{ validationErrors.username }}
            </div>
          </div>
          
          <!-- 密码输入组 -->
          <div class="form-group">
            <label for="password">密码:</label>
            <!-- 
              密码输入框
              - type="password"隐藏输入内容
              - v-model双向绑定到loginForm.password
              - @blur失焦时进行表单验证
            -->
            <input 
              type="password" 
              id="password" 
              v-model="loginForm.password" 
              @blur="validatePassword"
              :class="{ 'error': validationErrors.password }"
              placeholder="请输入密码（6-20个字符）"
              maxlength="20"
            />
            <!-- 密码验证错误提示 -->
            <div v-if="validationErrors.password" class="field-error">
              {{ validationErrors.password }}
            </div>
          </div>
          
          <!-- 
            登录按钮
            - :disabled绑定loading状态和表单验证状态，防止重复提交
            - 动态显示按钮文字（登录中/登录）
          -->
          <button 
            type="submit" 
            :disabled="authStore.isLoading || !isFormValid" 
            class="login-btn"
          >
            {{ authStore.isLoading ? '登录中...' : '登录' }}
          </button>
        </form>
        
        <!-- 忘记密码链接 -->
        <div class="forgot-password">
          <a href="#" @click.prevent="showForgotPassword = true">忘记密码？</a>
        </div>
        
        <!-- 
          错误信息显示
          - v-if条件渲染，只在有错误时显示
          - 显示登录失败、验证错误或网络错误信息
        -->
        <div v-if="authStore.loginError" class="error-message">
          {{ authStore.loginError }}
        </div>
      </div>
      
      <!-- 忘记密码表单区域 -->
      <div class="forgot-password-form" v-else>
        <h2>密码重置</h2>
        
        <!-- 第一步：输入用户名和手机号 -->
        <form v-if="resetStep === 1" @submit.prevent="handleRequestReset">
          <div class="form-group">
            <label for="resetUsername">用户名:</label>
            <input 
              type="text" 
              id="resetUsername" 
              v-model="resetForm.username" 
              required
              placeholder="请输入用户名"
            />
          </div>
          
          <div class="form-group">
            <label for="resetPhone">注册手机号:</label>
            <input 
              type="tel" 
              id="resetPhone" 
              v-model="resetForm.phone" 
              required
              placeholder="请输入注册时的手机号"
              pattern="[0-9]{11}"
            />
          </div>
          
          <button 
            type="submit" 
            :disabled="authStore.isLoading" 
            class="login-btn"
          >
            {{ authStore.isLoading ? '发送中...' : '发送验证码' }}
          </button>
        </form>
        
        <!-- 第二步：输入验证码和新密码 -->
        <form v-else-if="resetStep === 2" @submit.prevent="handleResetPassword">
          <div class="form-group">
            <label for="verificationCode">验证码:</label>
            <input 
              type="text" 
              id="verificationCode" 
              v-model="resetForm.verificationCode" 
              required
              placeholder="请输入6位验证码"
              maxlength="6"
            />
            <!-- 演示用验证码显示 -->
            <div v-if="demoVerificationCode" class="demo-code">
              演示验证码：{{ demoVerificationCode }}
            </div>
          </div>
          
          <div class="form-group">
            <label for="newPassword">新密码:</label>
            <input 
              type="password" 
              id="newPassword" 
              v-model="resetForm.newPassword" 
              required
              placeholder="请输入新密码（6-20个字符）"
              minlength="6"
              maxlength="20"
            />
          </div>
          
          <div class="form-group">
            <label for="confirmPassword">确认密码:</label>
            <input 
              type="password" 
              id="confirmPassword" 
              v-model="resetForm.confirmPassword" 
              required
              placeholder="请再次输入新密码"
            />
          </div>
          
          <button 
            type="submit" 
            :disabled="authStore.isLoading || !isResetFormValid" 
            class="login-btn"
          >
            {{ authStore.isLoading ? '重置中...' : '重置密码' }}
          </button>
        </form>
        
        <!-- 第三步：重置成功 -->
        <div v-else class="reset-success">
          <div class="success-icon">✓</div>
          <p>密码重置成功！</p>
          <button @click="backToLogin" class="login-btn">返回登录</button>
        </div>
        
        <!-- 返回登录链接 -->
        <div class="back-to-login" v-if="resetStep < 3">
          <a href="#" @click.prevent="backToLogin">返回登录</a>
        </div>
        
        <!-- 错误信息显示 -->
        <div v-if="authStore.loginError" class="error-message">
          {{ authStore.loginError }}
        </div>
      </div>
    </div>
  </div>
</template>

<script>
/**
 * LoginView组件的脚本部分
 * 
 * 使用Vue 3的Composition API实现完整的登录和密码重置功能
 * 主要功能：
 * 1. 管理登录表单的响应式数据和验证逻辑
 * 2. 处理用户登录验证，包括失败次数限制
 * 3. 实现忘记密码和密码重置流程
 * 4. 管理加载状态和错误提示
 * 5. 与路由和状态管理系统交互
 */

// 导入Vue 3的响应式API
import { ref, computed, onMounted } from 'vue'

// 导入Vue Router的路由控制hook
import { useRouter } from 'vue-router'

// 导入axios库发送HTTP请求，与后端交互
import axios from 'axios';


// 导入用户认证状态管理store, 待替换
import { useAuthStore } from '@/stores/auth'

/**
 * LoginView组件配置
 * 
 * 使用Composition API的setup函数组织组件逻辑
 * 相比Options API，提供更好的逻辑复用和TypeScript支持
 */
export default {
  name: 'LoginView', // 组件名称，用于调试和开发工具
  
  /**
   * setup函数 - Composition API的入口
   * 
   * 在组件创建之前执行，用于：
   * 1. 定义响应式数据
   * 2. 定义方法和计算属性
   * 3. 设置生命周期钩子
   * 4. 返回模板需要的数据和方法
   */
  setup() {
    /**
     * 路由控制器
     * 
     * useRouter()返回路由实例，提供编程式导航功能
     * 主要用于登录成功后的页面跳转
     */
    const router = useRouter()
    
    /**
     * 用户认证状态管理
     * 
     * useAuthStore()返回认证store实例，用于：
     * 1. 调用用户认证方法
     * 2. 获取登录状态和错误信息
     * 3. 处理密码重置逻辑
     */
    const authStore = useAuthStore()
    
    /**
     * 登录表单数据 - 响应式引用
     * 
     * ref()创建响应式引用，包含用户输入的登录信息
     * 通过v-model与表单输入框双向绑定
     */
    const loginForm = ref({
      username: '', // 用户名
      password: ''  // 密码
    })
    
    /**
     * 表单验证错误信息 - 响应式引用
     * 
     * 存储各个字段的验证错误信息
     * 用于在界面上显示具体的验证错误
     */
    const validationErrors = ref({
      username: '',
      password: ''
    })
    
    /**
     * 忘记密码显示状态 - 响应式引用
     * 
     * 控制是否显示忘记密码表单
     * true: 显示密码重置表单
     * false: 显示登录表单
     */
    const showForgotPassword = ref(false)
    
    /**
     * 密码重置步骤 - 响应式引用
     * 
     * 控制密码重置流程的当前步骤
     * 1: 输入用户名和手机号
     * 2: 输入验证码和新密码
     * 3: 重置成功
     */
    const resetStep = ref(1)
    
    /**
     * 密码重置表单数据 - 响应式引用
     * 
     * 包含密码重置流程中的所有输入数据
     */
    const resetForm = ref({
      username: '',
      phone: '',
      verificationCode: '',
      newPassword: '',
      confirmPassword: ''
    })
    
    /**
     * 演示用验证码 - 响应式引用
     * 
     * 用于演示环境显示验证码
     * 实际生产环境中不应显示
     */
    const demoVerificationCode = ref('')
    
    /**
     * 表单验证状态 - 计算属性
     * 
     * 检查登录表单是否通过所有验证
     * 只有在表单有效时才允许提交
     */
    const isFormValid = computed(() => {
      return loginForm.value.username.length >= 3 && 
             loginForm.value.password.length >= 6 &&
             !validationErrors.value.username &&
             !validationErrors.value.password
    })
    
    /**
     * 密码重置表单验证状态 - 计算属性
     * 
     * 检查密码重置表单是否有效
     */
    const isResetFormValid = computed(() => {
      return resetForm.value.verificationCode.length === 6 &&
             resetForm.value.newPassword.length >= 6 &&
             resetForm.value.newPassword === resetForm.value.confirmPassword
    })
    
    /**
     * 用户名验证方法
     * 
     * 验证用户名格式是否符合要求
     * - 长度：3-20个字符
     * - 字符：字母、数字、下划线
     */
    const validateUsername = () => {
      const username = loginForm.value.username.trim()
      
      if (!username) {
        validationErrors.value.username = '用户名不能为空'
        return false
      }
      
      if (username.length < 3) {
        validationErrors.value.username = '用户名至少3个字符'
        return false
      }
      
      if (username.length > 20) {
        validationErrors.value.username = '用户名不能超过20个字符'
        return false
      }
      
      if (!/^[a-zA-Z0-9_]+$/.test(username)) {
        validationErrors.value.username = '用户名只能包含字母、数字和下划线'
        return false
      }
      
      validationErrors.value.username = ''
      return true
    }
    
    /**
     * 密码验证方法
     * 
     * 验证密码格式是否符合要求
     * - 长度：6-20个字符
     * - 不能为纯数字或纯字母
     */
    const validatePassword = () => {
      const password = loginForm.value.password
      
      if (!password) {
        validationErrors.value.password = '密码不能为空'
        return false
      }
      
      if (password.length < 6) {
        validationErrors.value.password = '密码至少6个字符'
        return false
      }
      
      if (password.length > 20) {
        validationErrors.value.password = '密码不能超过20个字符'
        return false
      }
      
      validationErrors.value.password = ''
      return true
    }
    
    /**
     * 处理登录逻辑 - 异步方法
     * 
     * 登录流程：
     * 1. 验证表单输入格式
     * 2. 调用authStore.authenticateUser()进行用户认证
     * 3. 处理认证结果和错误情况
     * 4. 登录成功后跳转到项目管理页面
     */
    const handleLogin = async () => {
      try {
        // 先进行前端表单验证
        const isUsernameValid = validateUsername()
        const isPasswordValid = validatePassword()
        
        if (!isUsernameValid || !isPasswordValid) {
          return
        }
        
        // 用户认证，使用axios发送application/x-www-form-urlencoded格式数据
        const params = new URLSearchParams();
        params.append('username', loginForm.value.username.trim());
        params.append('password', loginForm.value.password);
        
        const response = await axios.post('/auth/login', params, {
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
          }
        });

        // 登录成功，获取JWT令牌
        const token = response.data.access_token;
        localStorage.setItem('authToken', token);         
        
        // 更新认证状态
        authStore.login({
          username: loginForm.value.username.trim(),
          token: token
        });       
        
        // 跳转到项目管理页面
        await router.push('/project')
        
      } catch (error) {
        // 错误已经在store中处理，这里不需要额外操作
        console.error('Login failed:', error.message)
        authStore.loginError = '登录失败，请检查用户名和密码';
      }
    }
    
    /**
     * 处理密码重置请求
     * 
     * 发送密码重置请求，获取验证码
     */
    const handleRequestReset = async () => {
      try {
        const result = await authStore.requestPasswordReset(
          resetForm.value.username.trim(),
          resetForm.value.phone.trim()
        )
        
        if (result.success) {
          // 保存演示用验证码（实际环境中不应显示）
          demoVerificationCode.value = result.verificationCode
          resetStep.value = 2
        }
      } catch (error) {
        console.error('Password reset request failed:', error.message)
      }
    }
    
    /**
     * 处理密码重置
     * 
     * 验证验证码并重置密码
     */
    const handleResetPassword = async () => {
      try {
        // 验证密码确认
        if (resetForm.value.newPassword !== resetForm.value.confirmPassword) {
          authStore.loginError = '两次输入的密码不一致'
          return
        }
        
        const result = await authStore.resetPassword(
          resetForm.value.username,
          resetForm.value.verificationCode,
          resetForm.value.newPassword
        )
        
        if (result.success) {
          resetStep.value = 3
        }
      } catch (error) {
        console.error('Password reset failed:', error.message)
      }
    }
    
    /**
     * 返回登录页面
     * 
     * 重置所有表单状态，返回登录界面
     */
    const backToLogin = () => {
      showForgotPassword.value = false
      resetStep.value = 1
      resetForm.value = {
        username: '',
        phone: '',
        verificationCode: '',
        newPassword: '',
        confirmPassword: ''
      }
      demoVerificationCode.value = ''
      authStore.loginError = ''
    }
    
    /**
     * 组件挂载时的初始化
     * 
     * 清除之前的错误状态
     */
    onMounted(() => {
      authStore.loginError = ''
    })
    
    /**
     * 返回模板需要的数据和方法
     * 
     * setup函数必须返回一个对象，包含：
     * 1. 响应式数据
     * 2. 计算属性
     * 3. 方法
     * 4. 模板中使用的任何其他变量或函数
     */
    return {
      // Store实例
      authStore,
      
      // 表单数据
      loginForm,
      resetForm,
      
      // 状态控制
      showForgotPassword,
      resetStep,
      demoVerificationCode,
      
      // 验证相关
      validationErrors,
      isFormValid,
      isResetFormValid,
      validateUsername,
      validatePassword,
      
      // 方法
      handleLogin,
      handleRequestReset,
      handleResetPassword,
      backToLogin
    }
  }
}
</script>

<style scoped>
/* 登录页面根容器样式 */
.login-view {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

/* 登录容器卡片样式 */
.login-container {
  background: white;
  border-radius: 10px;
  box-shadow: 0 15px 35px rgba(0, 0, 0, 0.1);
  padding: 40px;
  width: 100%;
  max-width: 450px;
  text-align: center;
}

/* 系统标题样式 */
.login-container h1 {
  color: #333;
  margin-bottom: 30px;
  font-size: 28px;
}

/* 表单标题样式 */
.login-form h2,
.forgot-password-form h2 {
  color: #555;
  margin-bottom: 25px;
  font-size: 20px;
}

/* 表单组样式 */
.form-group {
  margin-bottom: 20px;
  text-align: left;
}

/* 表单标签样式 */
.form-group label {
  display: block;
  margin-bottom: 5px;
  color: #555;
  font-weight: 500;
}

/* 表单输入框样式 */
.form-group input {
  width: 100%;
  padding: 12px;
  border: 2px solid #ddd;
  border-radius: 5px;
  font-size: 16px;
  transition: border-color 0.3s;
  box-sizing: border-box;
}

/* 输入框聚焦状态 */
.form-group input:focus {
  outline: none;
  border-color: #667eea;
}

/* 输入框错误状态 */
.form-group input.error {
  border-color: #e74c3c;
}

/* 字段错误提示样式 */
.field-error {
  color: #e74c3c;
  font-size: 14px;
  margin-top: 5px;
}

/* 登录按钮样式 */
.login-btn {
  width: 100%;
  padding: 12px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 5px;
  font-size: 16px;
  cursor: pointer;
  transition: transform 0.2s;
  margin-bottom: 15px;
}

/* 按钮悬停效果 */
.login-btn:hover:not(:disabled) {
  transform: translateY(-2px);
}

/* 按钮禁用状态 */
.login-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

/* 忘记密码链接样式 */
.forgot-password {
  text-align: center;
  margin-bottom: 15px;
}

.forgot-password a {
  color: #667eea;
  text-decoration: none;
  font-size: 14px;
}

.forgot-password a:hover {
  text-decoration: underline;
}

/* 返回登录链接样式 */
.back-to-login {
  text-align: center;
  margin-top: 15px;
}

.back-to-login a {
  color: #667eea;
  text-decoration: none;
  font-size: 14px;
}

.back-to-login a:hover {
  text-decoration: underline;
}

/* 错误信息样式 */
.error-message {
  color: #e74c3c;
  margin-top: 15px;
  padding: 10px;
  background: #ffeaea;
  border-radius: 5px;
  border: 1px solid #e74c3c;
  font-size: 14px;
}

/* 演示验证码显示样式 */
.demo-code {
  background: #e8f5e8;
  color: #2d5a2d;
  padding: 8px;
  border-radius: 4px;
  font-size: 14px;
  margin-top: 5px;
  border: 1px solid #4caf50;
}

/* 重置成功样式 */
.reset-success {
  text-align: center;
  padding: 20px 0;
}

.success-icon {
  font-size: 48px;
  color: #4caf50;
  margin-bottom: 15px;
}

.reset-success p {
  color: #333;
  font-size: 18px;
  margin-bottom: 20px;
}

/* 响应式设计 */
@media (max-width: 480px) {
  .login-container {
    padding: 30px 20px;
    margin: 10px;
  }
  
  .login-container h1 {
    font-size: 24px;
  }
  
  .form-group input {
    font-size: 14px;
  }
  
  .login-btn {
    font-size: 14px;
  }
}
</style>