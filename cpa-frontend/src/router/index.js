/**
 * router/index.js - Vue Router路由配置文件
 *
 * 功能说明：
 * 1. 创建和配置Vue Router实例
 * 2. 设置路由导航守卫，控制页面访问权限
 * 3. 实现基于用户认证状态和项目状态的路由保护
 * 4. 确保用户按照正确的流程访问应用页面
 *
 * 路由与页面跳转逻辑：
 * - 用户必须先登录才能访问其他页面
 * - 登录后必须选择项目才能进入工作台等功能页面
 * - 已登录用户访问登录页会自动重定向
 * - 未认证用户访问受保护页面会重定向到登录页
 *
 * 状态管理逻辑：
 * - 与authStore交互检查用户认证状态
 * - 与projectStore交互检查当前项目状态
 * - 支持从localStorage恢复认证状态
 */

// 导入Vue Router的核心函数
import { createRouter, createWebHistory } from "vue-router";

// 导入路由配置定义
import routes from "./routes";

// 导入状态管理stores
import { useAuthStore } from "@/stores/auth"; // 用户认证状态管理
import { useProjectStore } from "@/stores/project"; // 项目状态管理

/**
 * 创建Vue Router实例
 *
 * 配置说明：
 * - history: 使用HTML5 History模式，URL更美观且支持服务端渲染
 * - routes: 从routes.js导入的路由配置数组
 */
const router = createRouter({
  history: createWebHistory(), // 使用HTML5 History API，支持干净的URL
  routes, // 路由配置数组，定义URL与组件的映射关系
});

/**
 * 全局前置路由守卫
 *
 * 在每次路由跳转前执行，用于：
 * 1. 检查用户认证状态
 * 2. 验证页面访问权限
 * 3. 实现自动重定向逻辑
 * 4. 确保应用的访问流程正确
 *
 * 参数说明：
 * @param {Object} to - 即将进入的目标路由对象
 * @param {Object} from - 当前导航正要离开的路由对象
 * @param {Function} next - 控制导航的函数
 */
router.beforeEach((to, from, next) => {
  /**
   * 获取状态管理实例
   *
   * 注意：在路由守卫中使用store需要在函数内部调用
   * 因为此时Pinia已经初始化完成
   */
  const authStore = useAuthStore(); // 获取认证状态管理实例
  const projectStore = useProjectStore(); // 获取项目状态管理实例

  /**
   * 初始化认证状态
   *
   * 从localStorage恢复用户登录状态
   * 这确保了页面刷新后用户仍然保持登录状态
   */
  if (!authStore.isAuthenticated) {
    authStore.initializeAuth();
  }
  /**
   * 初始化项目状态
   * 如果用户已登录但当前项目为空，尝试从localStorage恢复
   */
  if (authStore.isAuthenticated && !projectStore.currentProject) {
    projectStore.initializeProject();
  }

  /**
   * 定义页面访问权限级别
   *
   * requiresAuth: 需要用户登录的页面
   * requiresProject: 需要选择项目的页面（更高级别的权限）
   */
  const requiresAuth = [
    "project",
    "workbench",
    "document",
    "event",
    "message",
    "setting",
  ];
  const requiresProject = [
    "workbench",
    "document",
    "event",
    "message",
    "setting",
  ];

  // 获取目标路由的名称
  const routeName = to.name;

  /**
   * 处理登录页面的访问逻辑
   *
   * 如果用户已经登录，根据项目状态重定向到合适的页面：
   * - 有当前项目：重定向到工作台
   * - 无当前项目：重定向到项目管理页面
   */
  if (routeName === "login") {
    if (authStore.isAuthenticated) {
      // 用户已登录，根据项目状态决定重定向目标
      if (projectStore.currentProject) {
        next({ name: "workbench" }); // 有项目，进入工作台
      } else {
        next({ name: "project" }); // 无项目，进入项目管理
      }
    } else {
      next(); // 未登录，允许访问登录页
    }
    return;
  }

  /**
   * 处理需要认证的页面访问逻辑
   *
   * 检查用户是否已登录，未登录则重定向到登录页
   */
  if (requiresAuth.includes(routeName)) {
    if (!authStore.isAuthenticated) {
      // 用户未登录，重定向到登录页面
      next({ name: "login" });
      return;
    }

    /**
     * 处理需要项目的页面访问逻辑
     *
     * 某些页面不仅需要登录，还需要选择项目
     * 如工作台、文档管理、事件管理等核心功能页面
     */
    if (requiresProject.includes(routeName)) {
      if (!projectStore.currentProject) {
        // 用户已登录但未选择项目，重定向到项目管理页面
        next({ name: "project" });
        return;
      }
    }
  }

  /**
   * 处理项目管理页面的访问逻辑
   *
   * 项目管理页面需要登录但不需要选择项目
   * 这是用户选择或创建项目的地方
   */
  if (routeName === "project") {
    if (!authStore.isAuthenticated) {
      // 用户未登录，重定向到登录页面
      next({ name: "login" });
      return;
    }
  }

  /**
   * 允许访问目标页面
   *
   * 如果通过了所有权限检查，允许用户访问目标页面
   * next()不带参数表示继续当前的导航
   */
  next();
});

// 导出路由实例，供main.js使用
export default router;
