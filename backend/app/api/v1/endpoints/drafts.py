"""
底稿管理API端点
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database_manager.database import get_db
from app.modules.auth_service import AuthService

router = APIRouter()


@router.get("/", summary="获取底稿列表")
async def get_drafts(
    current_user: dict = Depends(AuthService().get_current_user),
    db: Session = Depends(get_db)
):
    """获取底稿列表"""
    # TODO: 实现底稿列表查询逻辑
    return {"drafts": []}


@router.post("/upload", summary="上传底稿")
async def upload_draft(
    current_user: dict = Depends(AuthService().get_current_user),
    db: Session = Depends(get_db)
):
    """上传底稿文件"""
    # TODO: 实现底稿上传逻辑
    return {"message": "底稿上传成功"}
