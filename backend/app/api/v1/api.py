"""
API v1 主路由
"""

from fastapi import APIRouter

from app.api.v1.endpoints import (
    auth,
    users,
    projects,
    drafts,
    events,
    templates,
    messages,
    system,
    workspace
)

api_router = APIRouter()

# 认证相关路由
api_router.include_router(auth.router, prefix="/auth", tags=["认证"])

# 工作台路由
api_router.include_router(workspace.router, prefix="/workspace", tags=["工作台"])

# 用户管理路由
api_router.include_router(users.router, prefix="/users", tags=["用户管理"])

# 项目管理路由
api_router.include_router(projects.router, prefix="/projects", tags=["项目管理"])

# 底稿管理路由
api_router.include_router(drafts.router, prefix="/drafts", tags=["底稿管理"])

# 重大事项管理路由
api_router.include_router(events.router, prefix="/events", tags=["重大事项管理"])

# 模板管理路由
api_router.include_router(templates.router, prefix="/templates", tags=["模板管理"])

# 消息中心路由
api_router.include_router(messages.router, prefix="/messages", tags=["消息中心"])

# 系统管理路由
api_router.include_router(system.router, prefix="/system", tags=["系统管理"])



@api_router.get("/", tags=["根路径"])
async def root():
    """根路径"""
    return {
        "message": "注会帮 API v1.0",
        "status": "运行中",
        "version": "1.0.0"
    }
