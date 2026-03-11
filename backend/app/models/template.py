"""
模板数据模型
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database_manager.database import Base

class EventTemplate(Base):
    """重大事项模板"""
    
    __tablename__ = "event_templates"
    
    # 基本信息
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    template_id = Column(String(36), unique=True, index=True, nullable=False)  # UUID
    
    # 模板信息
    name = Column(String(200), nullable=False)  # 模板名称
    description = Column(Text)  # 模板描述
    category = Column(String(50))  # 模板分类
    
    # 模板内容（JSON格式存储重大事项的结构）
    template_content = Column(JSON, nullable=False)
    
    # 适用条件
    applicable_conditions = Column(JSON)  # 适用条件
    
    # 模板属性
    is_system_template = Column(Boolean, default=False)  # 是否系统模板
    is_public = Column(Boolean, default=False)  # 是否公开模板
    is_active = Column(Boolean, default=True)
    
    # 使用统计
    usage_count = Column(Integer, default=0)  # 使用次数
    
    # 创建信息
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(String(50))  # 创建者
    last_modified_by = Column(String(50))  # 最后修改者
    
    # 如果是用户创建的模板，关联到用户
    creator_id = Column(Integer, ForeignKey("users.id"))
    creator = relationship("User", lazy="select")
    
    def __repr__(self):
        return f"<EventTemplate(template_id={self.template_id}, name={self.name})>"
    
    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "template_id": self.template_id,
            "name": self.name,
            "description": self.description,
            "category": self.category,
            "template_content": self.template_content or {},
            "applicable_conditions": self.applicable_conditions or {},
            "is_system_template": self.is_system_template,
            "is_public": self.is_public,
            "is_active": self.is_active,
            "usage_count": self.usage_count,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "created_by": self.created_by,
            "last_modified_by": self.last_modified_by
        }
    
    def increment_usage(self):
        """增加使用次数"""
        self.usage_count += 1
