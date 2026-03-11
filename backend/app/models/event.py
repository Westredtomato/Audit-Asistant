"""
重大事项数据模型
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, JSON, Float
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database_manager.database import Base


class SignificantEvent(Base):
    """重大事项"""
    
    __tablename__ = "significant_events"
    
    # 基本信息
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    event_id = Column(String(36), unique=True, index=True, nullable=False)  # UUID
    
    # 所属项目
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    project = relationship("Project", back_populates="events")
    
    # 事项基本信息
    title = Column(String(200), nullable=False)  # 事项标题
    summary = Column(Text)  # 事项概述
    event_type = Column(String(20), default="significant_matter")  # significant_matter/significant_judgment
    
    # 审计目标和复核设置（JSON格式存储复杂结构）
    audit_objective = Column(Text)  # 审计目标
    evidence_standards = Column(JSON)  # 审计证据标准
    review_settings = Column(JSON)  # 复核设置
    
    # 关联底稿
    related_drafts = Column(JSON)  # 关联的底稿ID列表
    
    # 状态信息
    status = Column(String(20), default="未复核")  # 未复核/复核中/已复核
    
    # 版本信息
    content_version = Column(String(10), default="1.0")  # 内容版本 (a)
    current_review_version = Column(String(10), default="0")  # 当前复核版本 (b)
    
    # 重要性评分（复核后生成）
    importance_score = Column(Float)  # 重要性评分 0-100
    
    # 创建和修改信息
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(String(50))  # 创建者
    last_modified_by = Column(String(50))  # 最后修改者
    
    # 关联关系
    versions = relationship("EventVersion", back_populates="event", lazy="dynamic")
    review_results = relationship("ReviewResult", back_populates="event", lazy="dynamic")
    
    def __repr__(self):
        return f"<SignificantEvent(event_id={self.event_id}, title={self.title})>"
    
    @property
    def full_version(self):
        """完整版本号 a.b 格式"""
        return f"{self.content_version}.{self.current_review_version}"
    
    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "event_id": self.event_id,
            "project_id": self.project_id,
            "title": self.title,
            "summary": self.summary,
            "event_type": self.event_type,
            "audit_objective": self.audit_objective,
            "evidence_standards": self.evidence_standards or {},
            "review_settings": self.review_settings or {},
            "related_drafts": self.related_drafts or [],
            "status": self.status,
            "content_version": self.content_version,
            "current_review_version": self.current_review_version,
            "full_version": self.full_version,
            "importance_score": self.importance_score,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "created_by": self.created_by,
            "last_modified_by": self.last_modified_by
        }


class EventVersion(Base):
    """重大事项版本历史"""
    
    __tablename__ = "event_versions"
    
    # 基本信息
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    version_id = Column(String(36), unique=True, index=True, nullable=False)  # UUID
    
    # 所属事项
    event_id = Column(Integer, ForeignKey("significant_events.id"), nullable=False)
    event = relationship("SignificantEvent", back_populates="versions")
    
    # 版本信息
    version_number = Column(String(10), nullable=False)  # 版本号 a.b
    version_type = Column(String(20), nullable=False)  # content/review 内容版本或复核版本
    change_description = Column(Text)  # 变更描述
    
    # 快照内容（JSON格式存储当时的完整数据）
    content_snapshot = Column(JSON)
    
    # 创建信息
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by = Column(String(50))  # 创建者
    
    def __repr__(self):
        return f"<EventVersion(version_id={self.version_id}, version={self.version_number})>"
    
    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "version_id": self.version_id,
            "event_id": self.event_id,
            "version_number": self.version_number,
            "version_type": self.version_type,
            "change_description": self.change_description,
            "created_at": self.created_at,
            "created_by": self.created_by
        }


class ReviewResult(Base):
    """复核结果"""
    
    __tablename__ = "review_results"
    
    # 基本信息
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    result_id = Column(String(36), unique=True, index=True, nullable=False)  # UUID
    
    # 所属事项
    event_id = Column(Integer, ForeignKey("significant_events.id"), nullable=False)
    event = relationship("SignificantEvent", back_populates="review_results")
    
    # 版本信息
    version = Column(String(10), nullable=False)  # a.b 格式版本号
    
    # 复核结果内容（JSON格式存储复杂结构）
    audit_conclusion = Column(Text)  # 审计结论
    review_details = Column(JSON)  # 复核明细
    evidence_analysis = Column(JSON)  # 证据分析
    statistical_summary = Column(JSON)  # 统计整理
    
    # 结论和评价
    final_conclusion = Column(Text)  # 最终结论
    business_reasons = Column(Text)  # 业务原因分析
    
    # 重要性评分
    importance_score = Column(Float)  # 重要性评分 0-100
    
    # 质量指标
    sufficiency_score = Column(Float)  # 充分性得分
    appropriateness_score = Column(Float)  # 适当性得分
    
    # 复核过程追踪
    review_process_log = Column(JSON)  # 复核过程日志
    involved_drafts = Column(JSON)  # 涉及的底稿清单
    applied_standards = Column(JSON)  # 应用的标准和依据
    
    # 创建信息
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    reviewed_by = Column(String(50))  # 复核人
    review_duration = Column(Integer)  # 复核耗时（秒）
    
    def __repr__(self):
        return f"<ReviewResult(result_id={self.result_id}, version={self.version})>"
    
    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "result_id": self.result_id,
            "event_id": self.event_id,
            "version": self.version,
            "audit_conclusion": self.audit_conclusion,
            "review_details": self.review_details or {},
            "evidence_analysis": self.evidence_analysis or {},
            "statistical_summary": self.statistical_summary or {},
            "final_conclusion": self.final_conclusion,
            "business_reasons": self.business_reasons,
            "importance_score": self.importance_score,
            "sufficiency_score": self.sufficiency_score,
            "appropriateness_score": self.appropriateness_score,
            "review_process_log": self.review_process_log or {},
            "involved_drafts": self.involved_drafts or [],
            "applied_standards": self.applied_standards or [],
            "created_at": self.created_at,
            "reviewed_by": self.reviewed_by,
            "review_duration": self.review_duration
        }
