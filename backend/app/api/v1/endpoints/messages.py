"""
消息中心API端点
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database_manager.database import get_db
from app.modules.auth_service import AuthService

router = APIRouter()


@router.get("/", summary="获取消息列表")
async def get_messages(
    current_user: dict = Depends(AuthService().get_current_user),
    db: Session = Depends(get_db)
):
    """获取用户消息列表"""
    # TODO: 实现消息列表查询逻辑
    return {"messages": []}
