"""
项目数据模型
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database_manager.database import Base

class Project(Base):
    """项目实体"""
    
    __tablename__ = "projects"
    
    # 基本信息
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    project_id = Column(String(36), unique=True, index=True, nullable=False)  # UUID
    
    # 企业信息
    official_name = Column(String(200), nullable=False)  # 企业名称
    short_names = Column(JSON)  # 企业简称列表
    report_year = Column(Integer, nullable=False)  # 财务报表年份
    
    # 企业属性
    is_domestic = Column(Boolean, default=True)  # 是否境内企业
    company_scale = Column(String(20))  # 企业规模: large/medium/small
    industry = Column(String(100))  # 所属行业
    listing_type = Column(String(20))  # 上市类型: listed/unlisted/preparing
    is_state_owned = Column(Boolean, default=False)  # 是否国有企业
    
    # 审计依据
    audit_standard_id = Column(Integer, ForeignKey("audit_standards.id"))
    audit_standard = relationship("AuditStandard", back_populates="projects")
    
    # 状态管理
    status = Column(String(20), default="active")  # active/archived/deleted
    
    # 关联用户
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    creator = relationship("User", back_populates="projects")
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 关联关系
    drafts = relationship("Draft", back_populates="project", lazy="dynamic")
    events = relationship("SignificantEvent", back_populates="project", lazy="dynamic")
    review_standards = relationship("ReviewStandard", back_populates="project", lazy="dynamic")
    
    def __repr__(self):
        return f"<Project(project_id={self.project_id}, name={self.official_name})>"
    
    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "project_id": self.project_id,
            "official_name": self.official_name,
            "short_names": self.short_names or [],
            "report_year": self.report_year,
            "is_domestic": self.is_domestic,
            "company_scale": self.company_scale,
            "industry": self.industry,
            "listing_type": self.listing_type,
            "is_state_owned": self.is_state_owned,
            "status": self.status,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }


class AuditStandard(Base):
    """审计依据方案"""
    
    __tablename__ = "audit_standards"
    
    # 基本信息
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    standard_id = Column(String(36), unique=True, index=True, nullable=False)
    
    # 方案信息
    name = Column(String(200), nullable=False)
    description = Column(Text)
    
    # 依据内容（JSON格式存储复杂结构）
    accounting_standards = Column(JSON)  # 会计准则
    audit_standards = Column(JSON)  # 审计准则
    basic_laws = Column(JSON)  # 基础法律
    special_regulations = Column(JSON)  # 专项法规
    basic_regulations = Column(JSON)  # 基础监管规范
    special_supervisions = Column(JSON)  # 专项监管规范
    
    # 适用条件
    applicable_conditions = Column(JSON)  # 适用条件JSON
    
    # 系统信息
    is_system_default = Column(Boolean, default=False)  # 是否系统默认
    is_active = Column(Boolean, default=True)
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 关联关系
    projects = relationship("Project", back_populates="audit_standard", lazy="dynamic")
    
    def __repr__(self):
        return f"<AuditStandard(name={self.name})>"
    
    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "standard_id": self.standard_id,
            "name": self.name,
            "description": self.description,
            "accounting_standards": self.accounting_standards or [],
            "audit_standards": self.audit_standards or [],
            "basic_laws": self.basic_laws or [],
            "special_regulations": self.special_regulations or [],
            "basic_regulations": self.basic_regulations or [],
            "special_supervisions": self.special_supervisions or [],
            "applicable_conditions": self.applicable_conditions or {},
            "is_system_default": self.is_system_default,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
