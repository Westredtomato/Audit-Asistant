# 注会帮 - 审计复核辅助软件

## 项目简介

"注会帮" 是一款审计复核辅助软件，通过严格依照法律法规与行业准则，智能分析与重大事项或重大判断有关的审计工作底稿的充分性、适当性，旨在帮助注册会计师省时高效地把控审计工作质量。

## 项目结构

```
cpa-assistant/
├── frontend/                                # 前端项目根目录
│   ├── public/                             # 静态资源目录
│   │   ├── index.html                      # 主页面模板
│   │   └── favicon.ico                     # 网站图标
│   ├── src/                                # 源代码目录
│   │   ├── main.js                         # Vue应用入口
│   │   ├── App.vue                         # 根组件
│   │   ├── router/                         # 路由配置
│   │   │   ├── index.js                    # 路由配置文件
│   │   │   └── routes.js                   # 路由定义
│   │   ├── stores/                          # pinia状态管理
│   │   │   ├── auth.js                      # 认证状态管理
│   │   │   ├── project.js                   # 项目状态管理
│   │   │   ├── document.js                  # 文档状态管理
│   │   │   ├── event.js                     # 事件状态管理
│   │   │   ├── workspace.js                 # 工作台状态管理
│   │   │   └── message.js                   # 消息状态管理
│   │   ├── views/                          # 页面视图组件
│   │   │   ├── LoginView.vue               # 登录界面组件
│   │   │   ├── ProjectView.vue             # 项目管理界面组件
│   │   │   ├── BaseSettingView.vue         # 基础设置界面组件
│   │   │   ├── DocumentView.vue            # 文档管理界面组件
│   │   │   ├── EventView.vue               # 事件管理界面组件
│   │   │   ├── WorkbenchView.vue           # 工作台界面组件
│   │   │   └── MessageView.vue             # 消息中心界面组件
│   │   ├── components/                     # 可复用组件
│   │   │   ├── common/                     # 通用组件
│   │   │   ├── layout/                     # 布局组件
│   │   │   └── modules/                    # 模块化组件
│   │   │       ├── document/               # 文档相关组件
│   │   │       ├── event/                  # 事件相关组件
│   │   │       ├── workspace/              # 工作台相关组件
│   │   │       └── message/                # 消息相关组件
│   │   ├── assets/                         # 静态资源
│   │   │   ├── styles/                     # 样式文件
│   │   │   └── images/                     # 图片资源
│   │   └── utils/                          # 前端工具类
│   │       ├── api.js                      # API调用封装
│   │       ├── helpers.js                  # 辅助函数
│   │       └── validators.js               # 表单验证器
│   ├── package.json                        # 前端依赖配置
│   └── vue.config.js                       # Vue配置文件
├── backend/                                    # 后端服务根目录
│   ├── __init__.py
│   ├── main.py                                # FastAPI应用入口
│   ├── launcher/                             # 系统启动器
│   │   ├── __init__.py
│   │   ├── startup_manager.py                # 系统启动管理模块
│   │   └── system_launcher.py                # 系统启动器主程序
│   ├── app/                                  # 应用层主目录
│   │   ├── __init__.py
│   │   ├── application.py                    # 应用创建与路由集成
│   │   ├── api/                              # API路由定义
│   │   │   ├── __init__.py
│   │   │   └── v1/                           
|   │   │       ├── api.py                    # 路由集成
|   │   │       └── endpoints/                # API端点
│   │   ├── schemas/                          # 应用层请求、响应的数据模式定义
│   │   ├── modules/                          # 应用层服务模块
│   │   │   ├── __init__.py
│   │   │   ├── auth_service.py              # 登录认证模块
│   │   │   ├── project_service.py           # 项目管理模块
│   │   │   ├── base_setting_service.py      # 基础设置模块
│   │   │   ├── document_service.py          # 文档管理模块
│   │   │   ├── event_service.py             # 重大事项管理模块
│   │   │   ├── message_service.py           # 消息中心模块
│   │   │   ├── workspace_service.py         # 工作台模块
│   │   │   └── config_service.py            # 系统配置模块
│   │   └── utils/                           # 应用层工具类
│   │       ├── __init__.py
│   │       ├── file_manager.py              # 认证上下文管理器
│   │       └── project_isolation.py         # 项目上下文管理器
│   ├── business/                             # 业务逻辑层
│   │   ├── __init__.py
│   │   ├── compliance_checker.py            # 重大事项合规性检查服务
│   │   ├── review_engine/                   # 重大事项复核引擎
│   │   │   ├── __init__.py
|   |   |   ├── interface.py      # 复核引擎模块接口
│   │   │   ├── schemas.py        # 复核引擎请求、响应的数据模式定义
│   │   │   └── agent/            # 复核引擎内核
│   │   ├── document_matcher.py              # 智能匹配服务
│   │   ├── document_parser.py               # 底稿解析服务
│   │   ├── system_config_service.py         # 系统配置服务,统一管理项目环境与配置
│   │   ├── message_manager.py               # 消息管理服务
│   │   ├── version_control.py               # 版本控制服务
│   │   └── log_manager.py                   # 日志管理服务
│   ├── infrastructure/                       # 基础设施层
│   │   ├── __init__.py
│   │   ├── storage/                         # 本地数据存储
│   │   │   ├── file_manager.py        # 文件管理
│   │   │   ├── project_isolation.py   # 项目隔离
│   │   │   └── data_access.py         # 数据访问接口
│   │   ├── database/                        # 复核依据数据库
│   │   │   ├── __init__.py
│   │   │   ├── audit_database.py           # 审计依据数据库
│   │   │   ├── template_manager.py         
│   │   │   └── api_key_storage.py          
│   │   ├── config/                          # 系统配置管理
│   │   │   ├── __init__.py
│   │   │   ├── config_manager.py           # 配置管理器
│   │   │   └── default_settings.py         # 默认配置设置
│   │   └── llm_interface.py                # 大语言模型接口
|   ├── data/                          # 本地数据存储目录
|   |   ├── projects/                      # 各项目数据目录
|   │   |   ├── project_001/               # 具体项目数据
|   │   |   └── project_002/
│   |   └── templates/                     # 系统模板数据          
│   └── tests/                               # 测试目录
│       ├── __init__.py
│       ├── unit/                           # 单元测试
│       ├── integration/                    # 集成测试
│       └── fixtures/                       # 测试数据
├── README.md                               # 项目说明文档
├── docs/                                   # 文档目录
│   ├── architecture/                       # 架构文档
│   ├── user_manual/                        # 用户手册
│   └── api_docs/                           # API文档
├── scripts/                                # 脚本目录
│   ├── setup/                              # 安装脚本
│   ├── deployment/                         # 部署脚本
│   └── maintenance/                        # 维护脚本
└── config/                                 # 配置文件目录
    ├── development/                        # 开发环境配置
    ├── production/                         # 生产环境配置
    └── testing/                            # 测试环境配置
```

# 项目环境与配置说明
## 环境准备
### 数据库
- 暂时不用配置Redis内存数据库。
- 持久化数据库文件在infrastructure/data中

~~#### Redis~~
~~项目需要在部署Redis服务，推荐采用WLS2方法部署（保障项目可以自动驱动Redis服务，而不用手动配置）~~

~~**部署方法（WLS2）：**~~
~~1. 安装wls2与Ubuntu~~
~~- 注意：实例化Ubuntu（设置账户与密码时），密码输入的时候显示上没有反应，但实际有在输入，按回车即可确定~~
~~2. 安装Redis~~

### python环境
**注意：** python第三方库统一用pip管理

**解释器：** python = 3.12.3

**第三方库:**
``` bash
cd backend
pip install -r requirements.txt
```


## 环境配置与管理
business.system_config_service.py统一管理项目环境与配置。涉及内容如下：
- 服务器配置
- 文件目录配置
- LLM 参数与API配置
- 数据库配置

# 快速开始
**终端命令**
``` bash
cd backend
python main.py
```
**注意**
main.py会直接完成系统环境的初始化（包括外部资源的启动）。但对于Redis服务，项目没有提供终止后自动关闭机制，所以需要运行结束后手动关闭。

# API文档
暂时把API文档放在这里

## 应用层

### 路由
1. 基础API端点定义在app.api.v1.endpoint目录下
2. 路由初步集成在app.api.v1.api.py中，再由application.py进行集成为最终路由集合

### 数据模式
- app.schemas定义了应用层请求、响应数据模式

## 业务逻辑层

### review_engine
1. 数据模式
- review_engine.schemas定义了 review_engine 与应用层的请求、响应数据模式
- 接口接收：ReviewData，ResponseData类数据
- 接口返回响应：UploadFileRequirement，HelpRequirement，ReviewResult类数据

2. 环境配置
- requirements 记录了python第三方库
- python version: 3.12.3
- config_manager.py 暂时静态配置了LLM接口参数与文件目录，迁移需修改

3. how tos

接口封装了execute_review()，continue_review()两种方法，复核后人工输入数据均通过continue_review()方法处理。

``` python
from review_engine import MainReviewEngine

# 实例化
main_review_engine = MainReviewEngine()

# 执行复核 
main_review_engine.execute_review(review_data : ReviewData)

# 继续复核，
main_review_engine.continue_review(response_data: ResponseData | None)

```



