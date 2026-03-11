"""
认证相关Pydantic模式
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional, Dict, Any
from datetime import datetime


class Token(BaseModel):
    """访问令牌响应"""
    access_token: str
    token_type: str
    user: Dict[str, Any]
    
    class Config:
        schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "user": {
                    "username": "admin",
                    "display_name": "管理员",
                    "role": "admin"
                }
            }
        }


class TokenData(BaseModel):
    """令牌数据"""
    username: Optional[str] = None


class UserLogin(BaseModel):
    """用户登录请求"""
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    password: str = Field(..., min_length=6, description="密码")
    
    class Config:
        schema_extra = {
            "example": {
                "username": "admin",
                "password": "admin123"
            }
        }


class UserCreate(BaseModel):
    """创建用户请求"""
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    password: str = Field(..., min_length=6, description="密码")
    display_name: str = Field(..., min_length=2, max_length=100, description="显示名称")
    email: Optional[EmailStr] = Field(None, description="邮箱地址")
    phone: Optional[str] = Field(None, max_length=20, description="手机号码")
    role: Optional[str] = Field("cpa", description="用户角色")
    
    class Config:
        schema_extra = {
            "example": {
                "username": "testuser",
                "password": "password123",
                "display_name": "测试用户",
                "email": "test@example.com",
                "phone": "13800138000",
                "role": "cpa"
            }
        }


class PasswordChange(BaseModel):
    """修改密码请求"""
    old_password: str = Field(..., description="原密码")
    new_password: str = Field(..., min_length=6, description="新密码")
    
    class Config:
        schema_extra = {
            "example": {
                "old_password": "oldpassword",
                "new_password": "newpassword123"
            }
        }


class PasswordReset(BaseModel):
    """重置密码请求"""
    email: EmailStr = Field(..., description="邮箱地址")
    
    class Config:
        schema_extra = {
            "example": {
                "email": "user@example.com"
            }
        }
