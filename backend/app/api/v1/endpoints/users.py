"""
用户管理API端点
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database_manager.database import get_db
from app.modules.auth_service import AuthService
from app.schemas.user import User as UserSchema, UserUpdate, UserProfile
from app.schemas.base import BaseResponse

router = APIRouter()


@router.get("/profile", response_model=UserSchema, summary="获取用户资料")
async def get_user_profile(
    current_user: dict = Depends(AuthService().get_current_user)
):
    """获取当前用户资料"""
    return current_user


@router.put("/profile", response_model=UserSchema, summary="更新用户资料")
async def update_user_profile(
    profile_data: UserProfile,
    current_user: dict = Depends(AuthService().get_current_user),
    db: Session = Depends(get_db)
):
    """更新当前用户资料"""
    # TODO: 实现用户资料更新逻辑
    return {"message": "用户资料更新成功"}


@router.get("/", response_model=List[UserSchema], summary="获取用户列表")
async def get_users(
    skip: int = 0,
    limit: int = 100,
    current_user: dict = Depends(AuthService().get_current_user),
    db: Session = Depends(get_db)
):
    """获取用户列表（管理员权限）"""
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足"
        )
    
    # TODO: 实现用户列表查询逻辑
    return []
