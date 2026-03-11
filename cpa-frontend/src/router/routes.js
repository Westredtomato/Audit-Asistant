// 导入主要视图组件
import LoginView from '@/views/LoginView.vue'
import ProjectView from '@/views/ProjectView.vue'
import DocumentView from '@/views/DocumentView.vue'
import EventView from '@/views/EventView.vue'
import WorkbenchView from '@/views/WorkbenchView.vue'
import MessageView from '@/views/MessageView.vue'
import BaseSettingView from '@/views/BaseSettingView.vue'

// 导入事件管理相关组件
import MajorEvents from '@/components/modules/event/MajorEvents.vue'
import MajorJudgments from '@/components/modules/event/MajorJudgments.vue'
import CreateMajorEvent from '@/components/modules/event/CreateMajorEvent.vue'
import MajorEventTemplateManager from '@/components/modules/event/MajorEventTemplateManager.vue'
import MajorEventsList from '@/components/modules/event/MajorEventsList.vue'
import MajorEventDetail from '@/components/modules/event/MajorEventDetail.vue'
import EditMajorEvent from '@/components/modules/event/EditMajorEvent.vue'
import MajorEventHistory from '@/components/modules/event/MajorEventHistory.vue'
import MajorEventTemplateDetail from '@/components/modules/event/MajorEventTemplateDetail.vue'
import CreateMajorEventTemplate from '@/components/modules/event/CreateMajorEventTemplate.vue'

// 导入文档管理相关组件
import AuditPapers from '@/components/modules/document/AuditPapers.vue'
import AuditReport from '@/components/modules/document/AuditReport.vue'
import FinancialStatements from '@/components/modules/document/FinancialStatements.vue'

/**
 * router/routes.js - 路由配置定义文件
 * 
 * 系统架构设计：
 * 1. 采用平铺式路由结构，避免深层嵌套带来的复杂性
 * 2. 使用静态导入确保所有组件在构建时可用
 * 3. 通过路由命名和参数实现组件间的数据传递
 * 4. 支持RESTful风格的URL设计模式
 * 
 * 路由与页面跳转逻辑：
 * - 根路径自动重定向到登录页，确保用户身份验证
 * - 基础页面路由提供应用的核心功能入口
 * - 事件管理模块采用分层路由设计：主模块 -> 功能模块 -> 具体操作
 * - 动态路由参数支持资源的CRUD操作（创建、读取、更新、删除）
 * 
 * 权限控制与导航策略：
 * - 所有业务页面都需要用户登录和项目选择
 * - 通过路由守卫（在router/index.js中配置）实现权限验证
 * - 支持面包屑导航和页面间的前进后退
 * 
 * 事件管理模块路由设计：
 * - 模板管理：/events/major-events/templates/* （模板的增删改查）
 * - 记录管理：/events/major-events/* （事项记录的增删改查）
 * - 采用RESTful设计：列表页、详情页、编辑页、历史页
 * - 通过URL参数传递资源ID，支持直接访问和书签收藏
 */

const routes = [
  /**
   * 根路径重定向
   * 
   * 设计目的：
   * - 当用户访问根路径 "/" 时，自动重定向到登录页面
   * - 确保应用有一个明确的入口点和统一的用户体验
   * - 避免用户直接访问根路径时看到空白页面
   * 
   * 用户流程：
   * 1. 用户访问应用根域名
   * 2. 自动跳转到登录页面
   * 3. 完成身份验证后进入项目选择或工作台
   */
  /**
   * 底稿查看页面路由
   * 
   * 路径: /spec-excel-view
   * 组件: SpecExcelView.vue
   * 功能: 查看特定底稿的详细内容
   * 权限: 需要用户登录且选择项目
   */
  {
    path: '/spec-excel-view',
    name: 'SpecExcelView',
    component: () => import('@/components/modules/workspace/SpecExcelView.vue')
  },

  {
    path: '/',
    redirect: '/login'
  },
  
  // ==================== 基础页面路由 ====================
  
  /**
   * 登录页面路由
   * 
   * 路径: /login
   * 组件: LoginView.vue
   * 功能: 用户身份验证和登录
   * 权限: 无需登录即可访问（公开页面）
   * 
   * 用户交互流程：
   * 1. 用户输入用户名和密码
   * 2. 系统验证用户凭据
   * 3. 登录成功后跳转到项目选择页面 (/project)
   * 4. 如果用户已有活跃项目，可直接跳转到工作台 (/workbench)
   * 
   * 导航逻辑：
   * - 已登录用户访问此页面会被重定向到工作台
   * - 登录失败显示错误信息，保持在当前页面
   * - 支持记住登录状态和自动登录功能
   */

  {
    path: '/login',
    name: 'Login',
    component: LoginView
  },
  
  /**
   * 项目管理页面路由
   * 
   * 路径: /project
   * 组件: ProjectView.vue
   * 功能: 项目列表展示、创建新项目、选择当前项目
   * 权限: 需要用户登录
   * 
   * 用户交互流程：
   * 1. 显示用户可访问的项目列表
   * 2. 支持创建新项目或加入现有项目
   * 3. 用户选择项目后设置为当前活跃项目
   * 4. 跳转到该项目的工作台页面
   * 
   * 导航逻辑：
   * - 用户首次登录后的必经页面
   * - 用户可随时返回此页面切换项目
   * - 选择项目后自动跳转到 /workbench
   * - 未选择项目时，其他业务页面会重定向回此页面
   */
  {
    path: '/project',
    name: 'Project',
    component: ProjectView
  },
  
  /**
   * 文档管理页面路由
   * 
   * 路径: /document
   * 组件: DocumentView.vue
   * 功能: 项目文档的查看、编辑和管理
   * 权限: 需要用户登录且选择项目
   */
  {
    path: '/document',
    name: 'Document',
    component: DocumentView
  },
  
  /**
   * 事件管理主页面路由
   * 
   * 路径: /events
   * 组件: EventView.vue
   * 功能: 事件管理模块的入口页面，提供导航到各个子功能
   * 权限: 需要用户登录且选择项目
   * 
   * 模块导航结构：
   * - 重大事项管理 (/events/major-events)
   * - 重大判断管理 (/events/major-judgments)
   * - 提供各模块的概览信息和快捷操作入口
   * 
   * 用户体验设计：
   * - 作为事件管理功能的统一入口
   * - 显示各子模块的状态概览和统计信息
   * - 提供快速创建和最近操作的便捷入口
   */
  {
    path: '/events',
    name: 'Events',
    component: EventView
  },
  
  /**
   * 工作台页面路由
   * 
   * 路径: /workbench
   * 组件: WorkbenchView.vue
   * 功能: 项目的主工作区域，包含仪表板、快捷操作等
   * 权限: 需要用户登录且选择项目
   * 
   * 页面特性：
   * - 作为用户的主要工作界面和默认着陆页
   * - 提供项目概览、待办事项、快捷操作入口
   * - 集成各模块的关键信息和操作入口
   * 
   * 导航逻辑：
   * - 用户选择项目后的默认跳转目标
   * - 通过顶部导航栏可快速切换到其他功能模块
   * - 提供到事件管理、文档管理等核心功能的快捷入口
   */
  {
    path: '/workbench',
    name: 'Workbench',
    component: WorkbenchView
  },
  
  /**
   * 消息中心页面路由
   * 
   * 路径: /message
   * 组件: MessageView.vue
   * 功能: 显示系统消息、通知、提醒等
   * 权限: 需要用户登录且选择项目
   * 
   * 消息类型：
   * - 系统通知（更新、维护等）
   * - 项目消息（任务分配、状态变更等）
   * - 审计提醒（截止日期、合规检查等）
   * 
   * 交互功能：
   * - 消息标记为已读/未读
   * - 消息分类和筛选
   * - 重要消息置顶显示
   */
  {
    path: '/message',
    name: 'Message',
    component: MessageView
  },
  
  /**
   * 系统设置页面路由
   * 
   * 路径: /setting
   * 组件: BaseSettingView.vue
   * 功能: 系统配置、用户偏好设置、账户管理等
   * 权限: 需要用户登录且选择项目
   * 
   * 设置分类：
   * - 个人设置：头像、密码、偏好等
   * - 项目设置：权限、成员、配置等
   * - 系统设置：主题、语言、通知等
   * 
   * 权限控制：
   * - 普通用户只能修改个人设置
   * - 项目管理员可修改项目设置
   * - 系统管理员可修改所有设置
   */
  {
    path: '/setting',
    name: 'Setting',
    component: BaseSettingView
  },
  
  // ==================== 事件管理模块路由 ====================
  
  /**
   * 重大事项管理页面路由
   * 
   * 路径: /events/major-events
   * 组件: MajorEvents.vue
   * 功能: 重大事项模块的主入口，包含模板管理和记录管理两个功能入口
   * 权限: 需要用户登录且选择项目
   * 
   * 功能模块划分：
   * - 模板管理：标准化的事项模板，支持快速创建
   * - 记录管理：具体的事项实例，包含完整的生命周期
   * 
   * 导航逻辑：
   * - 提供到模板管理 (/events/major-events/templates) 的入口
   * - 提供到记录列表 (/events/major-events/list) 的入口
   * - 提供快速创建事项 (/events/create-major-event) 的入口
   * - 显示模块概览和统计信息
   */
  {
    path: '/events/major-events',
    name: 'MajorEvents',
    component: MajorEvents
  },
  
  /**
   * 重大判断管理页面路由
   * 
   * 路径: /events/major-judgments
   * 组件: MajorJudgments.vue
   * 功能: 管理重大判断相关事项
   * 权限: 需要用户登录且选择项目
   * 
   * 业务特性：
   * - 专门处理需要重大判断的审计事项
   * - 支持判断依据的记录和追踪
   * - 提供判断结果的审核和确认流程
   * 
   * 与重大事项的关系：
   * - 重大判断是重大事项的一个特殊类别
   * - 具有更严格的审核流程和文档要求
   * - 支持判断过程的完整记录和回溯
   */
  {
    path: '/events/major-judgments',
    name: 'MajorJudgments',
    component: MajorJudgments
  },
  
  /**
   * 创建重大事项页面路由
   * 
   * 路径: /events/create-major-event
   * 组件: CreateMajorEvent.vue
   * 功能: 新建重大事项的表单页面，包含表单验证和数据提交
   * 权限: 需要用户登录且选择项目
   * 
   * 创建流程：
   * 1. 选择创建方式（空白创建、基于模板、基于草稿）
   * 2. 填写基本信息（标题、描述、重要程度等）
   * 3. 配置复核依据和子事项
   * 4. 关联相关的审计底稿文件
   * 5. 表单验证和合规性检查
   * 6. 提交保存并跳转到详情页面
   * 
   * 交互特性：
   * - 支持草稿自动保存功能
   * - 提供智能表单验证和提示
   * - 支持模板快速填充
   * - 表单提交后跳转到事项详情或列表页面
   */
  {
    path: '/events/create-major-event',
    name: 'CreateMajorEvent',
    component: CreateMajorEvent
  },
  
  // ==================== 重大事项模板管理路由 ====================
  
  /**
   * 重大事项模板管理页面路由
   * 
   * 路径: /events/major-events/templates
   * 组件: MajorEventTemplateManager.vue
   * 功能: 管理重大事项模板，包括创建、编辑、删除和查看模板
   * 权限: 需要用户登录且选择项目
   * 操作: 提供模板列表展示、搜索筛选、批量操作等功能
   */
  {
    path: '/events/major-events/templates',
    name: 'MajorEventTemplateManager',
    component: MajorEventTemplateManager
  },
  
  /**
   * 创建重大事项模板页面路由
   * 
   * 路径: /events/major-events/templates/create
   * 组件: CreateMajorEventTemplate.vue
   * 功能: 新建重大事项模板的表单页面
   * 权限: 需要用户登录且选择项目
   * 交互: 表单提交后跳转到模板详情或模板管理页面
   */
  {
    path: '/events/major-events/templates/create',
    name: 'CreateMajorEventTemplate',
    component: CreateMajorEventTemplate
  },
  
  /**
   * 重大事项模板详情页面路由（动态路由）
   * 
   * 路径: /events/major-events/templates/:id
   * 组件: MajorEventTemplateDetail.vue
   * 功能: 查看特定模板的详细信息
   * 参数: id - 模板的唯一标识符
   * 权限: 需要用户登录且选择项目
   * 
   * 路由参数获取方式：
   * - 在组件中通过 $route.params.id 获取
   * - 或使用 useRoute() 组合式API获取
   */
  {
    path: '/events/major-events/templates/:id',
    name: 'MajorEventTemplateDetail',
    component: MajorEventTemplateDetail
  },
  
  // ==================== 重大事项记录管理路由 ====================
  
  /**
   * 重大事项记录列表页面路由
   * 
   * 路径: /events/major-events/list
   * 组件: MajorEventsList.vue
   * 功能: 显示所有重大事项记录的列表，支持筛选、搜索等功能
   * 权限: 需要用户登录且选择项目
   * 操作: 提供事项列表展示、搜索筛选、分页、批量操作等功能
   */
  {
    path: '/events/major-events/list',
    name: 'MajorEventsList',
    component: MajorEventsList
  },
  
  /**
   * 重大事项详情页面路由（动态路由）
   * 
   * 路径: /events/major-events/:id
   * 组件: MajorEventDetail.vue
   * 功能: 查看特定重大事项的详细信息
   * 参数: id - 事项的唯一标识符
   * 权限: 需要用户登录且选择项目
   * 
   * 页面功能：
   * - 只读模式展示事项的完整信息
   * - 显示基本信息、复核依据、子事项、关联文件等
   * - 提供状态跟踪和进度展示
   * 
   * 导航操作：
   * - 编辑按钮：跳转到编辑页面 (/events/major-events/:id/edit)
   * - 历史按钮：跳转到历史页面 (/events/major-events/:id/history)
   * - 返回按钮：返回到事项列表页面 (/events/major-events/list)
   * 
   * 参数获取：
   * - 组件中通过 this.$route.params.id 或 useRoute().params.id 获取事项ID
   * - 根据ID调用API获取事项详细数据
   */
  {
    path: '/events/major-events/:id',
    name: 'MajorEventDetail',
    component: MajorEventDetail
  },
  
  /**
   * 编辑重大事项页面路由（动态路由）
   * 
   * 路径: /events/major-events/:id/edit
   * 组件: EditMajorEvent.vue
   * 功能: 编辑特定重大事项的表单页面
   * 参数: id - 事项的唯一标识符
   * 权限: 需要用户登录且选择项目
   * 
   * 编辑流程：
   * 1. 根据ID加载现有事项数据
   * 2. 将数据填充到表单中
   * 3. 用户修改表单内容
   * 4. 表单验证和合规性检查
   * 5. 提交更新并保存变更记录
   * 6. 跳转到事项详情页面
   * 
   * 交互逻辑：
   * - 支持草稿保存功能，避免数据丢失
   * - 提供取消编辑功能，返回详情页面
   * - 记录编辑历史，支持变更追踪
   * - 权限检查：只有有权限的用户才能编辑
   */
  {
    path: '/events/major-events/:id/edit',
    name: 'EditMajorEvent',
    component: EditMajorEvent
  },
  
  /**
   * 重大事项历史页面路由（动态路由）
   * 
   * 路径: /events/major-events/:id/history
   * 组件: MajorEventHistory.vue
   * 功能: 查看特定重大事项的历史记录和变更日志
   * 参数: id - 事项的唯一标识符
   * 权限: 需要用户登录且选择项目
   * 
   * 历史记录类型：
   * - 创建记录：事项的初始创建信息
   * - 修改记录：字段变更的详细对比
   * - 状态变更：审核状态、完成状态等的变化
   * - 文件操作：关联文件的添加、删除、更新
   * 
   * 显示内容：
   * - 操作时间和操作人员信息
   * - 变更前后的数据对比（支持高亮显示差异）
   * - 操作类型和操作原因说明
   * - 支持按时间、操作人、操作类型筛选
   * 
   * 审计追踪：
   * - 完整的操作链路记录
   * - 支持合规性审查和问题追溯
   * - 提供数据导出功能用于审计报告
   */
  {
    path: '/events/major-events/:id/history',
    name: 'MajorEventHistory',
    component: MajorEventHistory
  },

  /**
   * 文档管理模块路由配置
   * 
   * 路由设计说明：
   * - 采用RESTful风格的URL设计
   * - 所有文档管理相关路由以 /document 为前缀
   * - 支持直接访问和书签收藏
   * 
   * 功能模块：
   * - 审计底稿：/document/audit-papers
   * - 审计报告：/document/audit-report  
   * - 财务报表：/document/financial-statements
   */
  {
    path: '/document/audit-papers',
    name: 'AuditPapers',
    component: AuditPapers
  },

  /**
   * 审计报告页面路由
   * 
   * 功能说明：
   * - 审计报告的生成和管理
   * - 支持报告模板和自定义内容
   * - 提供报告导出和分发功能
   */
  {
    path: '/document/audit-report',
    name: 'AuditReport', 
    component: AuditReport
  },

  /**
   * 财务报表页面路由
   * 
   * 功能说明：
   * - 财务报表数据的查看和分析
   * - 支持多种报表格式和可视化展示
   * - 提供财务指标计算和趋势分析
   */
  {
    path: '/document/financial-statements',
    name: 'FinancialStatements',
    component: FinancialStatements
  }
]

export default routes