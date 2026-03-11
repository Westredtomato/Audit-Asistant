<!--
  MajorEvents.vue - 重大事项管理主页面
  
  功能概述：
  这是重大事项管理的主入口页面，提供了模板管理和记录管理两个核心功能的导航。
  页面采用卡片式布局，展示各功能模块的统计信息和快捷操作。
  
  页面结构：
  1. 页面头部：包含返回按钮、标题和描述
  2. 功能模块网格：模板管理和记录管理两个主要功能卡片
  3. 空状态提示：当没有数据时显示引导操作
  
  路由与页面跳转逻辑：
  - 返回按钮：跳转回事件管理主页面 (/events)
  - 模板管理：跳转到模板管理页面 (/events/major-events/templates)
  - 记录管理：跳转到记录列表页面 (/events/major-events/list)
  - 创建操作：跳转到创建页面 (/events/create-major-event)
  
  状态管理逻辑：
  - 通过useEventStore获取事件数据
  - 计算属性实时更新统计信息
  - 组件挂载时自动获取数据
-->
<template>
  <!-- 重大事项管理主容器 -->
  <div class="major-events">
    <!-- 页面头部区域 -->
    <div class="header">
      <div class="header-left">
        <!-- 返回按钮：导航回事件管理主页面 -->
        <button class="back-btn" @click="goBack">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M19 12H5M12 19L5 12L12 5" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          返回
        </button>
        <!-- 页面标题和描述 -->
        <div class="header-content">
          <h1>重大事项管理</h1>
          <p class="subtitle">管理重大事项模板和记录</p>
        </div>
      </div>
    </div>

    <!-- 功能模块网格布局 -->
    <div class="module-grid">
      <!-- 重大事项模板管理卡片 -->
      <!-- 
        点击事件：@click="navigateToTemplates"
        功能：导航到模板管理页面
        路由目标：/events/major-events/templates
      -->
      <div class="module-card" @click="navigateToTemplates">
        <!-- 模板管理图标 -->
        <div class="module-icon">
          <svg width="48" height="48" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M14 2H6C5.46957 2 4.96086 2.21071 4.58579 2.58579C4.21071 2.96086 4 3.46957 4 4V20C4 20.5304 4.21071 21.0391 4.58579 21.4142C4.96086 21.7893 5.46957 22 6 22H18C18.5304 22 19.0391 21.7893 19.4142 21.4142C19.7893 21.0391 20 20.5304 20 20V8L14 2Z" stroke="#1976d2" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M14 2V8H20" stroke="#1976d2" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M16 13H8" stroke="#1976d2" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M16 17H8" stroke="#1976d2" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M10 9H9H8" stroke="#1976d2" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </div>
        <!-- 模块标题 -->
        <h3>重大事项模板</h3>
        <!-- 模块功能描述 -->
        <p>管理重大事项模板，包括创建、编辑、删除和查看模板</p>
        <!-- 统计信息：显示模板数量 -->
        <div class="module-stats">
          <span class="stat-item">{{ templateCount }} 个模板</span>
        </div>
        <!-- 导航箭头：悬停时显示 -->
        <div class="module-arrow">→</div>
      </div>
      
      <!-- 重大事项记录管理卡片 -->
      <!-- 
        点击事件：@click="navigateToEventsList"
        功能：导航到记录列表页面
        路由目标：/events/major-events/list
      -->
      <div class="module-card" @click="navigateToEventsList">
        <!-- 记录管理图标 -->
        <div class="module-icon">
          <svg width="48" height="48" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M19 3H5C3.9 3 3 3.9 3 5V19C3 20.1 3.9 21 5 21H19C20.1 21 21 20.1 21 19V5C21 3.9 20.1 3 19 3ZM19 19H5V8H19V19ZM7 10H9V12H7V10ZM11 10H17V12H11V10ZM7 14H9V16H7V14ZM11 14H17V16H11V14Z" fill="#f57c00"/>
          </svg>
        </div>
        <!-- 模块标题 -->
        <h3>重大事项列表</h3>
        <!-- 模块功能描述 -->
        <p>查看和管理项目中的所有重大事项记录</p>
        <!-- 统计信息：显示记录数量（来自状态管理） -->
        <div class="module-stats">
          <span class="stat-item">{{ eventsCount }} 条记录</span>
        </div>
        <!-- 导航箭头：悬停时显示 -->
        <div class="module-arrow">→</div>
      </div>
    </div>

    <!-- 空状态提示：当没有重大事项记录时显示 -->
    <!-- 
      条件渲染：v-if="eventsCount === 0"
      功能：引导用户创建第一个重大事项记录
      数据来源：eventsCount来自状态管理的计算属性
    -->
    <div class="empty-state" v-if="eventsCount === 0">
      <div class="empty-content">
        <!-- 空状态图标 -->
        <svg width="64" height="64" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M19 3H5C3.9 3 3 3.9 3 5V19C3 20.1 3.9 21 5 21H19C20.1 21 21 20.1 21 19V5C21 3.9 20.1 3 19 3ZM19 19H5V8H19V19Z" fill="#e0e0e0"/>
        </svg>
        <!-- 空状态标题 -->
        <h3>暂无重大事项记录</h3>
        <!-- 空状态描述 -->
        <p>您还没有创建任何重大事项记录</p>
        <!-- 快捷操作按钮组 -->
        <div class="empty-actions">
          <!-- 使用模板创建按钮 -->
          <button class="primary-btn" @click="navigateToTemplates">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M14 2H6C5.46957 2 4.96086 2.21071 4.58579 2.58579C4.21071 2.96086 4 3.46957 4 4V20C4 20.5304 4.21071 21.0391 4.58579 21.4142C4.96086 21.7893 5.46957 22 6 22H18C18.5304 22 19.0391 21.7893 19.4142 21.4142C19.7893 21.0391 20 20.5304 20 20V8L14 2Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M14 2V8H20" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            使用模板创建
          </button>
          <!-- 直接创建按钮 -->
          <button class="secondary-btn" @click="navigateToCreate">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M12 5V19M5 12H19" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            直接创建
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { useEventStore } from '@/stores/event'
import { computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'

export default {
  name: 'MajorEvents',
  
  setup() {
    // 状态管理和路由实例
    const eventStore = useEventStore()
    const router = useRouter()
    
    // ==================== 计算属性 ====================
    
    /**
     * 重大事项记录数量
     * 
     * 数据来源：eventStore.majorEvents
     * 功能：实时计算并显示当前项目的重大事项记录总数
     * 用途：统计信息展示、空状态判断
     */
    const eventsCount = computed(() => eventStore.majorEvents.length)
    
    /**
     * 重大事项模板数量
     * 
     * 数据来源：临时硬编码数据（待实现模板状态管理）
     * 功能：显示可用的重大事项模板数量
     * 用途：统计信息展示
     * 
     * TODO: 实现模板状态管理后，改为从store获取真实数据
     */
    const templateCount = computed(() => {
      // 这里可以添加模板数量的计算逻辑
      // 例如：return eventStore.getMajorEventTemplates.length
      return 5 // 临时数据
    })
    
    // ==================== 导航方法 ====================
    
    /**
     * 返回事件管理主页面
     * 
     * 路由目标：/events
     * 对应组件：EventView.vue
     * 功能：提供面包屑导航，返回上级页面
     */
    const goBack = () => {
      router.push('/events')
    }
    
    /**
     * 导航到模板管理页面
     * 
     * 路由目标：/events/major-events/templates
     * 对应组件：MajorEventTemplateManager.vue
     * 功能：管理重大事项模板的增删改查
     */
    const navigateToTemplates = () => {
      router.push('/events/major-events/templates')
    }
    
    /**
     * 导航到事项记录列表页面
     * 
     * 路由目标：/events/major-events/list
     * 对应组件：MajorEventsList.vue
     * 功能：查看和管理所有重大事项记录
     */
    const navigateToEventsList = () => {
      router.push('/events/major-events/list')
    }
    
    /**
     * 导航到创建重大事项页面
     * 
     * 路由目标：/events/create-major-event
     * 对应组件：CreateMajorEvent.vue
     * 功能：创建新的重大事项记录
     */
    const navigateToCreate = () => {
      router.push('/events/create-major-event')
    }
    
    // ==================== 生命周期 ====================
    
    /**
     * 组件挂载时的数据初始化
     * 
     * 功能：
     * 1. 获取最新的重大事项数据
     * 2. 更新统计信息
     * 3. 确保页面显示最新状态
     * 
     * 数据流：
     * eventStore.fetchMajorEvents() -> 更新store状态 -> 触发计算属性更新 -> 更新UI
     */
    onMounted(() => {
      eventStore.fetchMajorEvents()
    })
    
    // ==================== 返回响应式数据和方法 ====================
    
    return {
      // 计算属性
      eventsCount,
      templateCount,
      
      // 导航方法
      goBack,
      navigateToTemplates,
      navigateToEventsList,
      navigateToCreate
    }
  }
}
</script>

<style scoped>
.major-events {
  padding: 24px;
  max-width: 1200px;
  margin: 0 auto;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 48px;
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

.header-content h1 {
  font-size: 28px;
  font-weight: 600;
  color: #1a1a1a;
  margin: 0 0 4px 0;
}

.subtitle {
  font-size: 14px;
  color: #666;
  margin: 0;
}

.module-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 24px;
  max-width: 800px;
  margin: 0 auto;
}

.module-card {
  background: #fff;
  border: 1px solid #e0e0e0;
  border-radius: 12px;
  padding: 32px 24px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.module-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
  border-color: #1976d2;
}

.module-icon {
  margin-bottom: 16px;
  display: flex;
  justify-content: center;
}

.module-card h3 {
  font-size: 20px;
  font-weight: 600;
  color: #1a1a1a;
  margin: 0 0 12px 0;
}

.module-card p {
  font-size: 14px;
  color: #666;
  line-height: 1.5;
  margin: 0 0 16px 0;
}

.module-stats {
  margin-bottom: 20px;
}

.stat-item {
  display: inline-block;
  padding: 4px 12px;
  background: #f0f7ff;
  color: #1976d2;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.module-arrow {
  font-size: 18px;
  color: #1976d2;
  font-weight: 600;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.module-card:hover .module-arrow {
  opacity: 1;
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
  margin-top: 40px;
}

.empty-content {
  max-width: 400px;
  margin: 0 auto;
}

.empty-content h3 {
  font-size: 20px;
  color: #666;
  margin: 16px 0 8px 0;
}

.empty-content p {
  font-size: 14px;
  color: #999;
  margin: 0 0 24px 0;
}

.empty-actions {
  display: flex;
  gap: 12px;
  justify-content: center;
  flex-wrap: wrap;
}

.primary-btn, .secondary-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.2s;
}

.primary-btn {
  background: #1976d2;
  color: white;
}

.primary-btn:hover {
  background: #1565c0;
}

.secondary-btn {
  background: #f5f5f5;
  color: #666;
  border: 1px solid #ddd;
}

.secondary-btn:hover {
  background: #e0e0e0;
}

@media (max-width: 768px) {
  .major-events {
    padding: 16px;
  }
  
  .header {
    flex-direction: column;
    gap: 16px;
    align-items: stretch;
  }
  
  .module-grid {
    grid-template-columns: 1fr;
    gap: 16px;
  }
  
  .module-card {
    padding: 24px 20px;
  }
  
  .empty-actions {
    flex-direction: column;
    align-items: center;
  }
  
  .primary-btn, .secondary-btn {
    width: 100%;
    max-width: 200px;
  }
}
</style>