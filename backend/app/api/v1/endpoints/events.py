"""
重大事项管理API端点
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database_manager.database import get_db
from app.modules.auth_service import AuthService

router = APIRouter()


@router.get("/", summary="获取重大事项列表")
async def get_events(
    current_user: dict = Depends(AuthService().get_current_user),
    db: Session = Depends(get_db)
):
    """获取重大事项列表"""
    # TODO: 实现重大事项列表查询逻辑
    return {"events": []}


@router.post("/", summary="创建重大事项")
async def create_event(
    current_user: dict = Depends(AuthService().get_current_user),
    db: Session = Depends(get_db)
):
    """创建重大事项"""
    # TODO: 实现重大事项创建逻辑
    return {"message": "重大事项创建成功"}


@router.post("/{event_id}/review", summary="执行复核")
async def review_event(
    event_id: str,
    current_user: dict = Depends(AuthService().get_current_user),
    db: Session = Depends(get_db)
):
    """执行重大事项复核"""
    # TODO: 实现复核逻辑
    return {"message": "复核开始执行"}
