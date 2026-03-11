"""
用户数据模型
"""


from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database_manager.database import Base


class User(Base):
    """用户实体"""
    
    __tablename__ = "users"
    
    # 基本信息
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(String(36), unique=True, index=True, nullable=False)  # UUID
    username = Column(String(50), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    
    # 用户信息
    display_name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, index=True)
    phone = Column(String(20))
    
    # 角色权限
    role = Column(String(20), default="cpa")  # cpa: 注册会计师, admin: 管理员
    is_active = Column(Boolean, default=True)
    is_locked = Column(Boolean, default=False)
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login_at = Column(DateTime(timezone=True))
    
    # 用户偏好设置
    preferences = Column(Text)  # JSON格式存储用户偏好
    
    # 关联关系
    projects = relationship("Project", back_populates="creator", lazy="dynamic")
    messages = relationship("Message", back_populates="user", lazy="dynamic")
    review_standards = relationship("ReviewStandard", back_populates="creator", lazy="dynamic")
    
    def __repr__(self):
        return f"<User(username={self.username}, display_name={self.display_name})>"
    
    @property
    def is_admin(self):
        """是否是管理员"""
        return self.role == "admin"
    
    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "username": self.username,
            "display_name": self.display_name,
            "email": self.email,
            "phone": self.phone,
            "role": self.role,
            "is_active": self.is_active,
            "created_at": self.created_at,
            "last_login_at": self.last_login_at
        }
