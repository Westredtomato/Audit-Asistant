"""
复核标准相关的数据模式
"""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class EvidenceRequirement(BaseModel):
    """证据要求"""
    证据内容: str = Field(..., description="证据内容描述")
    质量要求: str = Field(..., description="证据质量要求说明")


class EvidenceClassification(BaseModel):
    """审计证据分类（支持动态键名）"""
    # 使用 Dict 支持动态的一级分类和二级分类
    pass


class ReviewStandardBase(BaseModel):
    """复核标准基础模型"""
    title: str = Field(..., description="标准标题", max_length=500)
    audit_conclusion: str = Field(..., description="审计结论")
    evidence_classification: List[Dict[str, Dict[str, List[Dict[str, str]]]]] = Field(
        ..., 
        description="审计证据分类与要求",
        example=[{
            "银行存款": {
                "完整性": [
                    {
                        "证据内容": "银行存款余额调节表",
                        "质量要求": "证据来源于被审计单位..."
                    }
                ]
            }
        }]
    )
    category: Optional[str] = Field(None, description="分类标签", max_length=100)
    tags: Optional[str] = Field(None, description="标签，逗号分隔", max_length=500)


class ReviewStandardCreate(ReviewStandardBase):
    """创建复核标准的请求模型"""
    source: Optional[str] = Field("user_created", description="来源")
    project_id: Optional[int] = Field(None, description="关联项目ID")


class ReviewStandardUpdate(BaseModel):
    """更新复核标准的请求模型"""
    title: Optional[str] = Field(None, max_length=500)
    audit_conclusion: Optional[str] = None
    evidence_classification: Optional[List[Dict[str, Dict[str, List[Dict[str, str]]]]]] = None
    category: Optional[str] = Field(None, max_length=100)
    tags: Optional[str] = Field(None, max_length=500)


class ReviewStandardResponse(ReviewStandardBase):
    """复核标准响应模型"""
    id: int
    source: str
    usage_count: int
    created_by: Optional[int] = None
    project_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ReviewStandardListResponse(BaseModel):
    """复核标准列表响应"""
    total: int
    items: List[ReviewStandardResponse]
    page: int
    page_size: int


class SemanticSearchRequest(BaseModel):
    """语义检索请求模型"""
    query: str = Field(..., description="查询文本（审计结论）", min_length=10)
    top_k: int = Field(5, description="返回结果数量", ge=1, le=50)
    similarity_threshold: Optional[float] = Field(0.7, description="相似度阈值", ge=0.0, le=1.0)
    category: Optional[str] = Field(None, description="筛选分类")
    project_id: Optional[int] = Field(None, description="筛选项目")


class SemanticSearchResult(BaseModel):
    """语义检索结果项"""
    standard_id: int
    title: str
    audit_conclusion: str
    evidence_classification: List[Dict[str, Dict[str, List[Dict[str, str]]]]]
    similarity_score: float = Field(..., description="相似度分数 0-1")
    category: Optional[str] = None
    tags: Optional[str] = None
    usage_count: int


class SemanticSearchResponse(BaseModel):
    """语义检索响应模型"""
    query: str
    results: List[SemanticSearchResult]
    total_found: int


class GenerateStandardRequest(BaseModel):
    """生成复核标准请求模型"""
    audit_conclusion: str = Field(..., description="审计结论", min_length=20)
    reference_standards: Optional[List[int]] = Field(
        None, 
        description="参考的标准ID列表（来自语义检索）"
    )
    auto_save: bool = Field(True, description="是否自动保存生成的标准")
    project_id: Optional[int] = Field(None, description="关联项目ID")
    title: Optional[str] = Field(None, description="自定义标题")


class GenerateStandardResponse(BaseModel):
    """生成复核标准响应模型"""
    审计结论: str
    审计证据分类与要求: List[Dict[str, Dict[str, List[Dict[str, str]]]]]
    generated_title: Optional[str] = Field(None, description="自动生成的标题")
    reference_count: int = Field(0, description="参考了多少个标准")
    saved: bool = Field(False, description="是否已保存")
    saved_id: Optional[int] = Field(None, description="保存后的ID")


class ReviewStandardStats(BaseModel):
    """复核标准统计信息"""
    total_standards: int
    by_category: Dict[str, int]
    by_source: Dict[str, int]
    most_used: List[ReviewStandardResponse]
    recent_created: List[ReviewStandardResponse]

