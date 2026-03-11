"""
认证服务
"""

import uuid
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
import redis
import json

from business.system_config_service import settings
from app.database_manager.database import get_db
from app.models.user import User
from app.schemas.auth import UserCreate

# 密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 方案
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")



class AuthService:
    """认证服务类"""
    
    def __init__(self):
        self.pwd_context = pwd_context
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """验证密码"""
        return self.pwd_context.verify(plain_password, hashed_password)
    
    def get_password_hash(self, password: str) -> str:
        """获取密码哈希"""
        return self.pwd_context.hash(password)
    
    def get_user_by_username(self, db: Session, username: str) -> Optional[User]:
        """根据用户名获取用户"""
        return db.query(User).filter(User.username == username).first()
    
    def get_user_by_email(self, db: Session, email: str) -> Optional[User]:
        """根据邮箱获取用户"""
        return db.query(User).filter(User.email == email).first()
    
    def get_user_by_user_id(self, db: Session, user_id: str) -> Optional[User]:
        """根据用户ID获取用户"""
        return db.query(User).filter(User.user_id == user_id).first()
    
    def authenticate_user(self, db: Session, username: str, password: str) -> Optional[User]:
        """验证用户凭据"""
        user = self.get_user_by_username(db, username)
        if not user:
            return None
        if not self.verify_password(password, user.password_hash):
            return None
        return user
    
    def create_user(self, db: Session, user_data: UserCreate) -> User:
        """创建用户"""
        hashed_password = self.get_password_hash(user_data.password)
        
        db_user = User(
            user_id=str(uuid.uuid4()),
            username=user_data.username,
            password_hash=hashed_password,
            display_name=user_data.display_name,
            email=user_data.email,
            phone=user_data.phone,
            role=user_data.role
        )
        
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    
    def create_default_admin(self, db: Session):
        """创建默认管理员用户"""
        admin_data = UserCreate(
            username="admin",
            password="admin123",
            display_name="系统管理员",
            email="admin@cpa-assistant.com",
            role="admin"
        )
        
        return self.create_user(db, admin_data)
    
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None):
        """创建访问令牌"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")
        return encoded_jwt
    
    def update_last_login(self, db: Session, user: User):
        """更新最后登录时间"""
        user.last_login_at = func.now()
        db.commit()
    
    async def get_current_user(self, 
                              token: str = Depends(oauth2_scheme),
                              db: Session = Depends(get_db)):
        """获取当前用户"""
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无法验证凭据",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            username: str = payload.get("sub")
            if username is None:
                raise credentials_exception
        except JWTError:
            raise credentials_exception
        
        user = self.get_user_by_username(db, username)
        if user is None:
            raise credentials_exception
        return user

auth_service = AuthService()    
async def get_current_active_user(current_user: User = Depends(auth_service.get_current_user)):
    """获取当前活跃用户"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="账号已经登出，请重新登录"
        )
    return current_user