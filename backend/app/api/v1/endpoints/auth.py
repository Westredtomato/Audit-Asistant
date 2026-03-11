"""
认证相关API端点
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta

from app.database_manager.database import get_db
from business.system_config_service import settings
from app.modules.auth_service import AuthService, get_current_active_user
from app.schemas.auth import Token, UserLogin, UserCreate
from app.schemas.user import User as UserSchema
from app.models.user import User

auth_service = AuthService()
router = APIRouter()


@router.post("/login", response_model=Token, summary="用户登录")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(OAuth2PasswordRequestForm),
    db: Session = Depends(get_db)
):
    """
    用户登录
    
    请求数据模式：
    - application/x-www-form-urlencoded格式
    - javascript请求示例:
        ```
            // 或者使用URLSearchParams
        const params = new URLSearchParams();
        params.append('username', 'johndoe');
        params.append('password', 'secret123');

        fetch('/api/v1/auth/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: params
        });
        ```
        - **username**: 用户名
        - **password**: 密码
    """
    
    # 验证用户凭据
    user = auth_service.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if user.is_locked:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户账号已被锁定"
        )

    # 将用户状态设置为活跃
    user.is_active = True
    db.commit()    

    
    # 生成访问令牌
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth_service.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    # 更新最后登录时间
    auth_service.update_last_login(db, user)
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user.to_dict()
    }


@router.post("/register", response_model=UserSchema, summary="用户注册")
async def register(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """
    用户注册（如果系统允许）
    
    - **username**: 用户名
    - **password**: 密码
    - **display_name**: 显示名称
    - **email**: 邮箱（可选）
    """
    
    # 检查用户名是否已存在
    if auth_service.get_user_by_username(db, user_data.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在"
        )
    
    # 检查邮箱是否已存在
    if user_data.email and auth_service.get_user_by_email(db, user_data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="邮箱已被使用"
        )
    
    # 创建用户
    user = auth_service.create_user(db, user_data)
    return user.to_dict()


@router.post("/refresh", response_model=Token, summary="刷新令牌")
async def refresh_token(
    current_user: UserSchema = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db)
):
    """
    刷新访问令牌
    """
    
    # 生成新的访问令牌
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth_service.create_access_token(
        data={"sub": current_user["username"]}, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": current_user
    }

    
@router.post("/logout", summary="用户登出")
async def logout(
    current_user: User = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db)
):
    """
    用户登出：
        将当前用户设为非活跃态
    
    请求数据模式：
      无请求体，代码直接读取HTTP 请求头部数据

    """
    # 将用户状态设置为非活跃
    user = db.query(User).filter(User.username == current_user.username).first()
    if user:
        user.is_active = False
        db.commit()
        return {"message": "登出成功"}
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )


@router.get("/me", response_model=UserSchema, summary="获取当前用户信息")
async def get_current_user_info(
    current_user: UserSchema = Depends(auth_service.get_current_user)
):
    """
    获取当前登录用户信息
    """
    return current_user
