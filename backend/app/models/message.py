"""
消息数据模型
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy.orm import declarative_base

from app.database_manager.database import Base

class Message(Base):
    """系统消息"""
    
    __tablename__ = "messages"
    
    # 基本信息
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    message_id = Column(String(36), unique=True, index=True, nullable=False)  # UUID
    
    # 消息内容
    title = Column(String(200), nullable=False)  # 消息标题
    content = Column(Text)  # 消息内容
    message_type = Column(String(20), nullable=False)  # 消息类型
    
    # 消息分类
    category = Column(String(50))  # 消息分类
    priority = Column(String(10), default="normal")  # 优先级: high/normal/low
    
    # 关联信息
    project_id = Column(String(36))  # 关联项目ID
    related_entity_type = Column(String(20))  # 关联实体类型: draft/event/review
    related_entity_id = Column(String(36))  # 关联实体ID
    
    # 消息数据（JSON格式存储扩展信息）
    message_data = Column(JSON)
    
    # 状态信息
    is_read = Column(Boolean, default=False)  # 是否已读
    is_handled = Column(Boolean, default=False)  # 是否已处理
    is_system = Column(Boolean, default=False)  # 是否系统消息
    
    # 用户关联
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="messages")
    
    # 时间信息
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    read_at = Column(DateTime(timezone=True))  # 阅读时间
    handled_at = Column(DateTime(timezone=True))  # 处理时间
    expires_at = Column(DateTime(timezone=True))  # 过期时间
    
    def __repr__(self):
        return f"<Message(message_id={self.message_id}, title={self.title})>"
    
    def mark_as_read(self):
        """标记为已读"""
        self.is_read = True
        self.read_at = func.now()
    
    def mark_as_handled(self):
        """标记为已处理"""
        self.is_handled = True
        self.handled_at = func.now()
    
    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "message_id": self.message_id,
            "title": self.title,
            "content": self.content,
            "message_type": self.message_type,
            "category": self.category,
            "priority": self.priority,
            "project_id": self.project_id,
            "related_entity_type": self.related_entity_type,
            "related_entity_id": self.related_entity_id,
            "message_data": self.message_data or {},
            "is_read": self.is_read,
            "is_handled": self.is_handled,
            "is_system": self.is_system,
            "created_at": self.created_at,
            "read_at": self.read_at,
            "handled_at": self.handled_at,
            "expires_at": self.expires_at
        }


# 消息类型常量
class MessageType:
    """消息类型枚举"""
    
    # 系统消息
    SYSTEM_NOTIFICATION = "system_notification"
    
    # 上传相关
    UPLOAD_SUCCESS = "upload_success"
    UPLOAD_FAILED = "upload_failed"
    UPLOAD_PROCESSING = "upload_processing"
    
    # 复核相关
    REVIEW_STARTED = "review_started"
    REVIEW_COMPLETED = "review_completed"
    REVIEW_FAILED = "review_failed"
    REVIEW_TIMEOUT = "review_timeout"
    REVIEW_INTERACTION_REQUIRED = "review_interaction_required"
    
    # 业务消息
    DRAFT_UPDATED = "draft_updated"
    EVENT_UPDATED = "event_updated"
    
    # 错误和警告
    ERROR = "error"
    WARNING = "warning"
    
    # 提醒消息
    REMINDER = "reminder"


class MessageCategory:
    """消息分类枚举"""
    
    SYSTEM = "system"  # 系统消息
    UPLOAD = "upload"  # 上传消息
    REVIEW = "review"  # 复核消息
    INTERACTION = "interaction"  # 交互消息
    NOTIFICATION = "notification"  # 通知消息
