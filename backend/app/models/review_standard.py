"""
复核标准数据模型
"""
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, Text, Float, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.database_manager.database import Base


class ReviewStandard(Base):
    """复核标准模型"""
    __tablename__ = "review_standards"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False, comment="标准标题")
    audit_conclusion = Column(Text, nullable=False, comment="审计结论")
    audit_conclusion_embedding = Column(Text, nullable=True, comment="审计结论向量（JSON存储）")
    evidence_classification = Column(JSON, nullable=False, comment="审计证据分类与要求（JSON存储）")
    
    # 元数据
    category = Column(String(100), nullable=True, comment="分类标签")
    tags = Column(String(500), nullable=True, comment="标签，逗号分隔")
    source = Column(String(200), nullable=True, comment="来源（用户创建/系统预置/导入）")
    usage_count = Column(Integer, default=0, comment="使用次数")
    
    # 关联信息
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True, comment="创建者ID")
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True, comment="关联项目ID")
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")
    
    # 关系
    creator = relationship("User", back_populates="review_standards", foreign_keys=[created_by])
    project = relationship("Project", back_populates="review_standards", foreign_keys=[project_id])
    
    def __repr__(self):
        return f"<ReviewStandard(id={self.id}, title='{self.title}')>"


class ReviewStandardVector(Base):
    """复核标准向量索引模型（用于高效向量检索）"""
    __tablename__ = "review_standard_vectors"
    
    id = Column(Integer, primary_key=True, index=True)
    standard_id = Column(Integer, ForeignKey("review_standards.id"), nullable=False, comment="关联复核标准ID")
    vector_data = Column(Text, nullable=False, comment="向量数据（JSON格式存储）")
    vector_dimension = Column(Integer, default=1024, comment="向量维度")
    embedding_model = Column(String(100), default="text-embedding-v1", comment="使用的嵌入模型")
    
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    
    # 关系
    standard = relationship("ReviewStandard", backref="vectors")
    
    def __repr__(self):
        return f"<ReviewStandardVector(id={self.id}, standard_id={self.standard_id})>"

