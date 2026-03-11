/**
 * main.js - Vue应用的入口文件
 * 
 * 功能说明：
 * 1. 创建Vue应用实例并配置核心插件
 * 2. 初始化路由系统（Vue Router）
 * 3. 初始化状态管理系统（Pinia）
 * 4. 将应用挂载到DOM元素上
 * 
 * 应用启动流程：
 * 1. 导入必要的依赖和组件
 * 2. 创建Vue应用实例
 * 3. 创建并配置Pinia状态管理
 * 4. 注册路由和状态管理插件
 * 5. 挂载应用到页面的#app元素
 */

// 导入Vue 3的createApp函数 - 用于创建Vue应用实例
import { createApp } from 'vue'

// 导入根组件App.vue - 应用的主要组件，包含整体布局和导航
import App from './App.vue'

// 导入路由配置 - 管理页面导航和URL映射
import router from './router'

// 导入Pinia状态管理库 - Vue 3推荐的状态管理解决方案
import { createPinia } from 'pinia'
import piniaPluginPersistedstate from 'pinia-plugin-persistedstate'

import axios from 'axios';

// *安全认证
// Axios 全局配置
axios.defaults.baseURL = 'http://127.0.0.1:8000/api/v1'; // 后端API基础URL

// 请求拦截器：添加JWT（统一使用 authToken）
axios.interceptors.request.use(config => {
  const token = localStorage.getItem('authToken');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
}, error => Promise.reject(error));

// 响应拦截器：处理401（统一清理 authToken）
axios.interceptors.response.use(response => response, error => {
  if (error.response && error.response.status === 401) {
    localStorage.removeItem('authToken');
    router.push('/login');
  }
  return Promise.reject(error);
});

/**
 * 创建Vue应用实例
 * 
 * createApp()是Vue 3的新API，用于创建应用实例
 * 相比Vue 2的new Vue()，提供了更好的TypeScript支持和插件隔离
 */
const app = createApp(App)

/**
 * 创建Pinia状态管理实例
 * 
 * Pinia是Vue 3官方推荐的状态管理库，用于：
 * 1. 管理应用的全局状态（用户信息、项目信息等）
 * 2. 提供响应式的状态更新
 * 3. 支持TypeScript和开发工具
 * 4. 替代Vuex，提供更简洁的API
 */
const pinia = createPinia()
pinia.use(piniaPluginPersistedstate)

/**
 * 注册Pinia插件
 * 
 * 必须在使用任何store之前注册Pinia插件
 * 注册后，所有组件都可以通过useXxxStore()访问状态管理
 */
app.use(pinia)

/**
 * 注册Vue Router插件
 * 
 * 注册后，应用获得以下功能：
 * 1. 路由导航能力（$router.push()等）
 * 2. 当前路由信息访问（$route.params等）
 * 3. <router-view>和<router-link>组件
 * 4. 路由守卫功能（beforeEach等）
 */
app.use(router)

/**
 * 挂载应用到DOM
 * 
 * 将Vue应用实例挂载到页面中id为'app'的元素上
 * 这个元素通常在public/index.html中定义
 * 挂载后，Vue开始接管DOM并渲染应用界面
 */
app.mount('#app')