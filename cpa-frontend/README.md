CPA-assistant

## 技术栈

- 前端框架 : Vue 3 (Composition API)
- 状态管理 : Pinia
- 路由管理 : Vue Router
- 构建工具 : Vite
- HTTP 客户端 : Axios
- 后端 : FastAPI (Python)
- 样式设计：Element Plus

## 启动步骤

### 第一步：环境准备

- **Node.js** (版本 16 或更高)
- **npm** (通常随 Node.js 一起安装)

**代码编辑器**

   - 推荐使用 VS Code，并安装以下插件：
     - Volar（Vue 官方推荐插件）
     - Vue Language Features (Volar)
     - ESLint
     - Prettier

### 第二步：安装依赖

#### 1. 安装前端依赖

```
# 在项目根目录下执行
npm install

# 安装 Vue Router
npm install vue-router@4

# 安装 pinia 状态管理
npm install pinia

# 安装 Axios（用于 API 调用）
npm install axios

npm install element-plus @element-plus/icons-vue

npm install @vitejs/plugin-vue

npm install vite @vitejs/plugin-vue vue@^3.2.0 vue-router@^4.0.0 vuex@^4.0.0

npm i xlsx

npm i pinia-plugin-persistedstate
```

#### 2. 后端（Python）依赖安装

```
# 进入 Python 后端目录
cd ../backend
pip install -r requirements.txt
```

### 第三步：启动服务

**重要：需要同时启动前端和后端服务**

```
# 启动后端（FastAPI），服务将在 http://127.0.0.1:8000 启动
cd ../backend
python main.py
```

```
# 启动前端开发服务器，前端服务将在 http://localhost:5173 启动
# 在 cpa-frontend 目录下（新开一个终端窗口）
npm run dev
```

## 结构说明

这个项目包含两个部分：

- **前端**: Vue 3 + Vite 应用（cpa-frontend 目录）
- **后端**: FastAPI (Python) 服务（backend 目录）

**核心文件结构：**

- `main.js` - 应用入口，配置 Pinia 和路由
- `App.vue` - 根组件，包含导航布局
- `router/index.js` - 路由配置和导航守卫
- `router/routes.js` - 路由定义和页面映射
- `api.js` - API 请求封装和数据交互

**页面:**

登录认证模块 (`LoginView.vue`)

项目管理模块 (`ProjectView.vue`)

工作台主界面 (`WorkbenchView.vue`)

文档管理模块 (`DocumentView.vue`)

事件管理模块 (`EventView.vue`)

基础设置模块 (`BaseSettingView.vue`)

消息中心模块 (`MessageView.vue`)

**状态管理架构:**

认证状态管理 (`auth.js`)

项目状态管理 (`project.js`)

文档状态管理 (`document.js`)

事件状态管理 (`event.js`)

工作区状态管理 (`workspace.js`)

消息状态管理 (`message.js`)

复核结果状态管理(`reviewResult.js`)

## 存储与数据持久化逻辑

### 1. 前端数据持久化

- **localStorage**: 用户认证信息、项目选择状态、用户偏好设置
- **sessionStorage**: 临时会话数据、表单草稿
- **IndexedDB**: 大量结构化数据存储（通过 workspace store 实现）

### 2. 后端数据存储

- **文件系统**: 由后端统一管理（FastAPI），按项目隔离
- **数据库**: 使用后端定义的存储方案（见 backend/infrastructure）
- **API 接口**: 完整的 RESTful API 设计（见 backend/app/api/v1）

### 3. 数据同步机制

- 前后端通过 HTTP API 进行数据交互
- 支持文件上传和下载的数据传输
- 实现 CRUD 操作的数据持久化
- WebSocket 实时通信支持

### API 文档位置

当前项目的 API 相关文档主要在以下位置：

1. **前端 API 工具**: `src/utils/api.js` - 包含接口定义和使用说明
2. **后端 API**: `backend/app/api/v1` - FastAPI 路由与端点实现
3. **工作台 API 使用示例**: `backend/docs/workspace_api_usage.md`

### 主要 API 接口

- **工作台**: `/api/v1/workspace/*` - 复核流程相关接口
- 注：前端当前使用的文件/文档列表接口为 `/api/v1/files`、`/api/v1/documents`（由 Python 后端实现）。未实现时请避免触发或进行容错处理。