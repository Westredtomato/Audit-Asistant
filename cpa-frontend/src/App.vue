<!-- 
  App.vue - Vue应用的根组件
  
  功能说明：
  1. 作为整个应用的入口组件，包含所有页面的公共布局
  2. 引入Navigation导航组件，提供统一的导航栏和侧边栏
  3. 使用router-view作为路由出口，动态渲染不同页面组件
  4. 设置全局样式，确保应用的一致性外观
  
  组件交互逻辑：
  - Navigation组件负责处理页面导航和用户状态显示
  - router-view根据当前路由动态切换显示的页面组件
  - 所有子页面都会被Navigation组件包裹，继承统一的布局结构
-->
<template>
  <!-- 应用根容器 - 包含整个应用的所有内容 -->
  <div id="app">
    <!-- 
      Navigation导航组件 - 提供应用的导航功能
      - 包含顶部导航栏（显示用户信息、登出按钮等）
      - 包含侧边栏导航（工作台、文档管理、事件管理等功能模块）
      - 根据用户登录状态和当前页面动态显示不同的导航内容
    -->
    <Navigation>
      <!-- 
        router-view路由出口 - Vue Router的核心组件
        - 根据当前URL路径动态渲染对应的页面组件
        - 所有页面组件（LoginView、ProjectView、WorkbenchView等）都会在这里显示
        - 页面切换时会自动销毁旧组件并创建新组件
      -->
      <router-view />
    </Navigation>
  </div>
</template>

<script>
// 导入Navigation导航组件 - 提供应用的统一导航布局
import Navigation from "./components/common/Navigation.vue";

/**
 * App根组件配置
 * 
 * 作为Vue应用的根组件，负责：
 * 1. 定义应用的整体结构和布局
 * 2. 引入和注册全局使用的组件
 * 3. 提供应用级别的样式设置
 */
export default {
  name: "App", // 组件名称，用于调试和开发工具识别
  
  // 注册子组件 - 在模板中可以直接使用
  components: {
    Navigation, // Navigation导航组件，提供应用的导航功能
  },
};
</script>

<!-- 
  全局样式定义
  
  这些样式会应用到整个应用，确保：
  1. 统一的字体和颜色主题
  2. 重置默认的浏览器样式
  3. 设置合适的布局基础
-->
<style>
/* 应用根容器样式 */
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif; /* 设置应用的主要字体族 */
  -webkit-font-smoothing: antialiased; /* 在Webkit浏览器中启用字体平滑 */
  -moz-osx-font-smoothing: grayscale; /* 在Firefox中启用字体平滑 */
  color: #2c3e50; /* 设置应用的主要文字颜色 */
  height: 100vh; /* 设置应用高度为视窗高度，确保全屏显示 */
}

/* 全局样式重置 - 消除浏览器默认样式差异 */
* {
  margin: 0; /* 重置所有元素的外边距 */
  padding: 0; /* 重置所有元素的内边距 */
  box-sizing: border-box; /* 设置盒模型为border-box，便于布局计算 */
}

/* body元素样式重置 */
body {
  margin: 0; /* 重置body的外边距 */
  padding: 0; /* 重置body的内边距 */
}
</style>

