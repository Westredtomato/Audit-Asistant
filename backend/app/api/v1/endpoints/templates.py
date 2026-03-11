"""
模板管理API端点
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database_manager.database import get_db
from app.modules.auth_service import AuthService

router = APIRouter()


@router.get("/", summary="获取模板列表")
async def get_templates(
    current_user: dict = Depends(AuthService().get_current_user),
    db: Session = Depends(get_db)
):
    """获取模板列表"""
    # TODO: 实现模板列表查询逻辑
    return {"templates": []}
