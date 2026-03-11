"""
基础Pydantic模式
"""

from pydantic import BaseModel
from typing import Optional, Any, Dict, List
from datetime import datetime


class BaseResponse(BaseModel):
    """基础响应模型"""
    success: bool = True
    message: str = "操作成功"
    data: Optional[Any] = None


class ErrorResponse(BaseModel):
    """错误响应模型"""
    success: bool = False
    message: str
    error_code: Optional[str] = None
    details: Optional[Dict[str, Any]] = None


class PaginationParams(BaseModel):
    """分页参数"""
    page: int = 1
    page_size: int = 20
    
    class Config:
        schema_extra = {
            "example": {
                "page": 1,
                "page_size": 20
            }
        }


class PaginatedResponse(BaseModel):
    """分页响应模型"""
    items: List[Any]
    total: int
    page: int
    page_size: int
    total_pages: int
    
    @classmethod
    def create(cls, items: List[Any], total: int, page: int, page_size: int):
        """创建分页响应"""
        total_pages = (total + page_size - 1) // page_size
        return cls(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages
        )


class TimestampMixin(BaseModel):
    """时间戳混入"""
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
