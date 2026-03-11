"""
用户相关Pydantic模式
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional, Dict, Any
from datetime import datetime

from .base import TimestampMixin


class UserBase(BaseModel):
    """用户基础模式"""
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    display_name: str = Field(..., min_length=2, max_length=100, description="显示名称")
    email: Optional[EmailStr] = Field(None, description="邮箱地址")
    phone: Optional[str] = Field(None, max_length=20, description="手机号码")
    role: str = Field("cpa", description="用户角色")


class UserCreate(UserBase):
    """创建用户"""
    password: str = Field(..., min_length=6, description="密码")


class UserUpdate(BaseModel):
    """更新用户"""
    display_name: Optional[str] = Field(None, min_length=2, max_length=100, description="显示名称")
    email: Optional[EmailStr] = Field(None, description="邮箱地址")
    phone: Optional[str] = Field(None, max_length=20, description="手机号码")
    is_active: Optional[bool] = Field(None, description="是否激活")
    is_locked: Optional[bool] = Field(None, description="是否锁定")
    preferences: Optional[Dict[str, Any]] = Field(None, description="用户偏好设置")


class User(UserBase, TimestampMixin):
    """用户响应模式"""
    id: int
    user_id: str
    is_active: bool
    is_locked: bool
    last_login_at: Optional[datetime]
    preferences: Optional[Dict[str, Any]] = None
    
    class Config:
        from_attributes = True
        schema_extra = {
            "example": {
                "id": 1,
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
                "username": "admin",
                "display_name": "管理员",
                "email": "admin@example.com",
                "phone": "13800138000",
                "role": "admin",
                "is_active": True,
                "is_locked": False,
                "created_at": "2024-01-01T12:00:00",
                "updated_at": "2024-01-01T12:00:00",
                "last_login_at": "2024-01-01T12:00:00"
            }
        }


class UserProfile(BaseModel):
    """用户个人资料"""
    display_name: str = Field(..., min_length=2, max_length=100, description="显示名称")
    email: Optional[EmailStr] = Field(None, description="邮箱地址")
    phone: Optional[str] = Field(None, max_length=20, description="手机号码")
    preferences: Optional[Dict[str, Any]] = Field(None, description="用户偏好设置")
    
    class Config:
        schema_extra = {
            "example": {
                "display_name": "张三",
                "email": "zhangsan@example.com",
                "phone": "13800138000",
                "preferences": {
                    "theme": "light",
                    "language": "zh-CN",
                    "default_timeout": 30
                }
            }
        }


class UserStats(BaseModel):
    """用户统计信息"""
    total_projects: int = Field(0, description="项目总数")
    active_projects: int = Field(0, description="活跃项目数")
    total_events: int = Field(0, description="重大事项总数")
    completed_reviews: int = Field(0, description="完成复核数")
    
    class Config:
        schema_extra = {
            "example": {
                "total_projects": 10,
                "active_projects": 3,
                "total_events": 25,
                "completed_reviews": 18
            }
        }
