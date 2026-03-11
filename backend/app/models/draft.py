"""
底稿数据模型
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, JSON, LargeBinary
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database_manager.database import Base

class Draft(Base):
    """审计工作底稿"""
    
    __tablename__ = "drafts"
    
    # 基本信息
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    draft_id = Column(String(36), unique=True, index=True, nullable=False)  # UUID
    
    # 所属项目
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    project = relationship("Project", back_populates="drafts")
    
    # 底稿信息
    title = Column(String(200), nullable=False)
    category = Column(String(50))  # 底稿类别
    subcategory = Column(String(50))  # 底稿子类别
    
    # 文件信息
    file_name = Column(String(255))  # 原始文件名
    file_path = Column(String(500))  # 文件存储路径
    file_size = Column(Integer)  # 文件大小(字节)
    file_type = Column(String(20))  # 文件类型
    file_hash = Column(String(64))  # 文件哈希值
    
    # 内容信息
    parsed_content = Column(JSON)  # 解析后的结构化内容
    content_summary = Column(Text)  # 内容摘要
    
    # 状态信息
    status = Column(String(20), default="active")  # active/archived/deleted
    parse_status = Column(String(20), default="pending")  # pending/parsing/completed/failed
    
    # 版本信息
    current_version = Column(String(10), default="1.0")
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 关联关系
    versions = relationship("DraftVersion", back_populates="draft", lazy="dynamic")
    
    def __repr__(self):
        return f"<Draft(draft_id={self.draft_id}, title={self.title})>"
    
    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "draft_id": self.draft_id,
            "project_id": self.project_id,
            "title": self.title,
            "category": self.category,
            "subcategory": self.subcategory,
            "file_name": self.file_name,
            "file_size": self.file_size,
            "file_type": self.file_type,
            "content_summary": self.content_summary,
            "status": self.status,
            "parse_status": self.parse_status,
            "current_version": self.current_version,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }


class DraftVersion(Base):
    """底稿版本历史"""
    
    __tablename__ = "draft_versions"
    
    # 基本信息
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    version_id = Column(String(36), unique=True, index=True, nullable=False)  # UUID
    
    # 所属底稿
    draft_id = Column(Integer, ForeignKey("drafts.id"), nullable=False)
    draft = relationship("Draft", back_populates="versions")
    
    # 版本信息
    version_number = Column(String(10), nullable=False)  # 版本号
    change_description = Column(Text)  # 变更描述
    
    # 文件信息
    file_path = Column(String(500))  # 文件存储路径
    file_size = Column(Integer)  # 文件大小
    file_hash = Column(String(64))  # 文件哈希值
    
    # 内容信息
    parsed_content = Column(JSON)  # 解析后的内容
    
    # 创建信息
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by = Column(String(50))  # 创建者
    
    def __repr__(self):
        return f"<DraftVersion(version_id={self.version_id}, version={self.version_number})>"
    
    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "version_id": self.version_id,
            "draft_id": self.draft_id,
            "version_number": self.version_number,
            "change_description": self.change_description,
            "file_size": self.file_size,
            "file_hash": self.file_hash,
            "created_at": self.created_at,
            "created_by": self.created_by
        }
