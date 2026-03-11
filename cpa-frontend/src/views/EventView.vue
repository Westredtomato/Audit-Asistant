<!--
  EventView.vue - 事件管理主页面
  事件管理模块的入口页面，提供了一个清晰的导航界面，
  让用户可以选择进入不同的事件管理功能模块。
  
  页面结构：
  1. 页面标题和描述区域
  2. 功能模块网格布局
  3. 两个主要功能模块卡片：重大事项和重大判断
  
  路由与页面跳转逻辑：
  - 通过Vue Router进行页面导航
  - 点击模块卡片触发路由跳转
  - 使用编程式导航（this.$router.push）
  
  组件与交互逻辑：
  - 响应式网格布局适配不同屏幕尺寸
  - 卡片悬停效果提供视觉反馈
  - 点击事件处理器触发页面跳转
-->
<template>
  <!-- 事件管理主容器 -->
  <div class="event-view">
    <!-- 页面头部区域：包含标题和描述 -->
    <div class="header">
      <h1>事件管理</h1>
      <p class="subtitle">管理项目中的重大事项和重大判断</p>
    </div>
    
    <!-- 功能模块网格布局 -->
    <div class="module-grid">
      <!-- 重大事项模块卡片 -->
      <!-- 
        点击事件：@click="navigateToMajorEvents"
        功能：导航到重大事项管理页面
        路由目标：/events/major-events
      -->
      <div class="module-card" @click="navigateToMajorEvents">
        <!-- 模块图标：使用SVG图标表示文档/事项概念 -->
        <div class="module-icon">
          <svg width="48" height="48" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M19 3H5C3.9 3 3 3.9 3 5V19C3 20.1 3.9 21 5 21H19C20.1 21 21 20.1 21 19V5C21 3.9 20.1 3 19 3ZM19 19H5V8H19V19ZM7 10H9V12H7V10ZM11 10H17V12H11V10ZM7 14H9V16H7V14ZM11 14H17V16H11V14Z" fill="#1976d2"/>
          </svg>
        </div>
        <!-- 模块标题 -->
        <h3>重大事项</h3>
        <!-- 模块功能描述 -->
        <p>记录和管理项目执行过程中的重要事件和里程碑</p>
        <!-- 导航箭头：悬停时显示 -->
        <div class="module-arrow">→</div>
      </div>
      
      <!-- 重大判断模块卡片 -->
      <!-- 
        点击事件：@click="navigateToMajorJudgments"
        功能：导航到重大判断管理页面
        路由目标：/events/major-judgments
      -->
      <div class="module-card" @click="navigateToMajorJudgments">
        <!-- 模块图标：使用SVG图标表示判断/决策概念 -->
        <div class="module-icon">
          <svg width="48" height="48" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M12 2C6.48 2 2 6.48 2 12C2 17.52 6.48 22 12 22C17.52 22 22 17.52 22 12C22 6.48 17.52 2 12 2ZM13 17H11V15H13V17ZM13 13H11V7H13V13Z" fill="#f57c00"/>
          </svg>
        </div>
        <!-- 模块标题 -->
        <h3>重大判断</h3>
        <!-- 模块功能描述 -->
        <p>记录项目中的关键决策和专业判断过程</p>
        <!-- 导航箭头：悬停时显示 -->
        <div class="module-arrow">→</div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'EventView',
  
  methods: {
    /**
     * 导航到重大事项管理页面
     * 
     * 功能说明：
     * - 跳转到重大事项管理的主页面
     * - 该页面包含模板管理和记录管理两个子功能
     * 
     * 路由目标：/events/major-events
     * 对应组件：MajorEvents.vue
     */
    navigateToMajorEvents() {
      // 使用编程式导航跳转到重大事项页面
      this.$router.push('/events/major-events')
    },
    
    /**
     * 导航到重大判断管理页面
     * 
     * 功能说明：
     * - 跳转到重大判断管理页面
     * - 该页面包含判断记录的增删改查功能
     * 
     * 路由目标：/events/major-judgments
     * 对应组件：MajorJudgments.vue
     */
    navigateToMajorJudgments() {
      // 使用编程式导航跳转到重大判断页面
      this.$router.push('/events/major-judgments')
    }
  }
}
</script>

<style scoped>
.event-view {
  padding: 24px;
  max-width: 1200px;
  margin: 0 auto;
}

.header {
  text-align: center;
  margin-bottom: 48px;
}

.header h1 {
  font-size: 32px;
  font-weight: 600;
  color: #1a1a1a;
  margin: 0 0 12px 0;
}

.subtitle {
  font-size: 16px;
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
  margin: 0 0 20px 0;
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

@media (max-width: 768px) {
  .event-view {
    padding: 16px;
  }
  
  .module-grid {
    grid-template-columns: 1fr;
    gap: 16px;
  }
  
  .module-card {
    padding: 24px 20px;
  }
}
</style>
