"""
系统管理API端点
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database_manager.database import get_db
from app.modules.auth_service import AuthService
from business.system_config_service import settings

router = APIRouter()


@router.get("/health", summary="系统健康检查")
async def health_check():
    """系统健康检查"""
    return {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION
    }


@router.get("/info", summary="系统信息")
async def system_info(
    current_user: dict = Depends(AuthService().get_current_user)
):
    """获取系统信息"""
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足"
        )
    
    return {
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "debug": settings.DEBUG,
        "database_url": settings.DATABASE_URL.split("@")[-1] if "@" in settings.DATABASE_URL else settings.DATABASE_URL
    }
