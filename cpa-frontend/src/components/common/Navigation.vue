<template>
  <div class="navigation-layout">
    <!-- 顶部导航栏 -->
    <nav class="top-navigation" v-if="shouldShowTopNavigation">
      <div class="nav-container">
        <!-- 左侧品牌信息 -->
        <div class="nav-brand">
          <h3>CPA助手系统</h3>
        </div>
        
        <!-- 右侧导航链接 -->
        <div class="nav-links">
          <!-- 如果用户已登录但未选择项目，显示项目管理链接 -->
          <router-link 
            v-if="authStore.isAuthenticated && !projectStore.currentProject" 
            to="/project" 
            class="nav-link"
          >
            <i class="icon">📁</i>
            项目管理
          </router-link>
          
          <!-- 用户信息和登出 -->
          <div v-if="authStore.isAuthenticated" class="user-section">
            <span class="username">{{ authStore.user?.username }}</span>
            <button @click="handleLogout" class="logout-btn">
              <i class="icon">🚪</i>
              登出
            </button>
          </div>
          
          <!-- 未登录时显示登录链接 -->
          <router-link 
            v-if="!authStore.isAuthenticated" 
            to="/login" 
            class="nav-link login-link"
          >
            <i class="icon">🔑</i>
            登录
          </router-link>
        </div>
      </div>
    </nav>

    <!-- 主要内容区域 -->
    <div class="main-layout" v-if="shouldShowSidebar">
      <!-- 左侧导航栏 -->
      <aside class="sidebar">
        <nav class="sidebar-nav">
          <!-- 主要功能 -->
          <div class="nav-section">
            <h3 class="nav-title">主要功能</h3>
            <ul class="nav-list">
              <li class="nav-item" :class="{ active: $route.name === 'Workbench' }">
                <button @click="navigateToPage('Workbench')" class="nav-link">
                  <i class="nav-icon">📊</i>
                  <span>工作台概览</span>
                </button>
              </li>
              <li class="nav-item" :class="{ active: $route.name === 'Document' }">
                <button @click="navigateToPage('Document')" class="nav-link">
                  <i class="nav-icon">📄</i>
                  <span>文档管理</span>
                </button>
              </li>
              <li class="nav-item" :class="{ active: $route.name === 'Events' || $route.name === 'MajorEvents' || $route.name === 'MajorJudgments' }">
                <button @click="navigateToPage('Events')" class="nav-link">
                  <i class="nav-icon">📅</i>
                  <span>事件管理</span>
                </button>
              </li>
              <li class="nav-item" :class="{ active: $route.name === 'Message' }">
                <button @click="navigateToPage('Message')" class="nav-link">
                  <i class="nav-icon">💬</i>
                  <span>消息中心</span>
                  <span v-if="messageStore.unreadCount > 0" class="badge">
                    {{ messageStore.unreadCount }}
                  </span>
                </button>
              </li>
            </ul>
          </div>
          
          <!-- 系统设置 -->
          <div class="nav-section">
            <h3 class="nav-title">系统设置</h3>
            <ul class="nav-list">
              <li class="nav-item" :class="{ active: $route.name === 'Setting' }">
                <button @click="navigateToPage('Setting')" class="nav-link">
                  <i class="nav-icon">⚙️</i>
                  <span>基础设置</span>
                </button>
              </li>
              <li class="nav-item">
                <button @click="switchProject" class="nav-link">
                  <i class="nav-icon">🔄</i>
                  <span>切换项目</span>
                </button>
              </li>
            </ul>
          </div>
        </nav>
      </aside>

      <!-- 右侧内容区域 -->
      <main class="content-area">
        <slot></slot>
      </main>
    </div>

    <!-- 无侧边栏的内容区域 -->
    <div v-else class="simple-layout">
      <slot></slot>
    </div>
  </div>
</template>

<script>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useProjectStore } from '@/stores/project'
import { useMessageStore } from '@/stores/message'

export default {
  name: 'Navigation',
  setup() {
    const route = useRoute()
    const router = useRouter()
    const authStore = useAuthStore()
    const projectStore = useProjectStore()
    const messageStore = useMessageStore()

    // 计算是否应该显示顶部导航栏
    const shouldShowTopNavigation = computed(() => {
      const currentPath = route.path
      // 在登录页面不显示顶部导航
      return currentPath !== '/login'
    })

    // 计算是否应该显示左侧导航栏
    const shouldShowSidebar = computed(() => {
      const currentRouteName = route.name
      // 只在已登录且已选择项目的功能页面显示左侧导航
      const functionalPages = ['Workbench', 'Document', 'Events', 'MajorEvents', 'MajorJudgments', 'Message', 'Setting', 'CreateMajorEvent', 'MajorEventTemplateManager', 'MajorEventsList', 'MajorEventDetail', 'EditMajorEvent', 'MajorEventHistory', 'MajorEventTemplateDetail', 'CreateMajorEventTemplate']
      return authStore.isAuthenticated && 
             projectStore.currentProject && 
             functionalPages.includes(currentRouteName)
    })

    // 页面导航方法
    const navigateToPage = async (routeName) => {
      try {
        // 如果当前已经在目标页面，则不进行跳转
        if (router.currentRoute.value.name === routeName) {
          return
        }
        await router.push({ name: routeName })
      } catch (error) {
        console.error('页面跳转失败:', error)
      }
    }

    // 切换项目
    const switchProject = async () => {
      try {
        await router.push('/project')
      } catch (error) {
        console.error('跳转到项目管理失败:', error)
      }
    }

    // 处理登出
    const handleLogout = async () => {
      try {
        // 清除认证状态
        authStore.logout()
        // 清除当前项目
        projectStore.setCurrentProject(null)
        // 跳转到登录页面
        await router.push('/login')
      } catch (error) {
        console.error('登出失败:', error)
      }
    }

    return {
      authStore,
      projectStore,
      messageStore,
      shouldShowTopNavigation,
      shouldShowSidebar,
      navigateToPage,
      switchProject,
      handleLogout
    }
  }
}
</script>

<style scoped>
/* 整体布局 */
.navigation-layout {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f8f9fa;
}

/* 顶部导航栏 */
.top-navigation {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  position: sticky;
  top: 0;
  z-index: 1000;
}

/* 主要布局容器 */
.main-layout {
  flex: 1;
  display: flex;
  overflow: hidden;
}

/* 简单布局（无侧边栏） */
.simple-layout {
  flex: 1;
  overflow-y: auto;
}

.nav-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 60px;
}

.nav-brand h3 {
  margin: 0;
  color: white;
  font-size: 20px;
  font-weight: 600;
  letter-spacing: 0.5px;
}

.nav-links {
  display: flex;
  align-items: center;
  gap: 20px;
}

.nav-link {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  color: white;
  text-decoration: none;
  border-radius: 6px;
  transition: all 0.3s ease;
  font-weight: 500;
  background: rgba(255, 255, 255, 0.1);
}

.nav-link:hover {
  background: rgba(255, 255, 255, 0.2);
  transform: translateY(-1px);
}

.nav-link.router-link-active {
  background: rgba(255, 255, 255, 0.25);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

.login-link {
  background: rgba(255, 255, 255, 0.15);
  border: 1px solid rgba(255, 255, 255, 0.3);
}

.login-link:hover {
  background: rgba(255, 255, 255, 0.25);
}

.user-section {
  display: flex;
  align-items: center;
  gap: 15px;
}

.username {
  color: white;
  font-weight: 500;
  font-size: 14px;
}

.logout-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  background: rgba(231, 76, 60, 0.8);
  color: white;
  border: none;
  padding: 8px 12px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.3s ease;
}

.logout-btn:hover {
  background: rgba(231, 76, 60, 1);
  transform: translateY(-1px);
}

.icon {
  font-size: 16px;
  display: inline-block;
}

/* 左侧导航栏 */
.sidebar {
  width: 260px;
  background: white;
  border-right: 1px solid #e1e8ed;
  overflow-y: auto;
  box-shadow: 2px 0 4px rgba(0, 0, 0, 0.1);
}

.sidebar-nav {
  padding: 20px 0;
}

.nav-section {
  margin-bottom: 30px;
}

.nav-title {
  padding: 0 20px;
  margin: 0 0 15px 0;
  font-size: 12px;
  font-weight: 600;
  color: #7f8c8d;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.nav-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.nav-item {
  margin-bottom: 2px;
}

.sidebar .nav-link {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 20px;
  border: none;
  background: none;
  color: #2c3e50;
  text-align: left;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 14px;
  position: relative;
  text-decoration: none;
}

.sidebar .nav-link:hover {
  background: #f8f9fa;
  color: #667eea;
}

.nav-item.active .nav-link {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  font-weight: 500;
}

.nav-item.active .nav-link::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 4px;
  background: #667eea;
}

.nav-icon {
  font-size: 16px;
  width: 20px;
  text-align: center;
}

.badge {
  background: #e74c3c;
  color: white;
  border-radius: 10px;
  padding: 2px 6px;
  font-size: 10px;
  font-weight: 600;
  margin-left: auto;
}

/* 内容区域 */
.content-area {
  flex: 1;
  overflow-y: auto;
  background: #f8f9fa;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .nav-container {
    padding: 0 15px;
    height: 50px;
  }
  
  .nav-brand h3 {
    font-size: 16px;
  }
  
  .nav-links {
    gap: 10px;
  }
  
  .nav-link {
    padding: 6px 12px;
    font-size: 14px;
  }
  
  .username {
    display: none;
  }
  
  .logout-btn {
    padding: 6px 10px;
    font-size: 12px;
  }
  
  .main-layout {
    flex-direction: column;
  }
  
  .sidebar {
    width: 100%;
    height: auto;
    order: 2;
  }
  
  .content-area {
    order: 1;
  }
}
</style>
