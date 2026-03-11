"""
工作台相关API端点
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta

from app.database_manager.database import get_db
from business.system_config_service import settings
from app.modules.auth_service import AuthService, get_current_active_user
from app.schemas.auth import Token, UserLogin, UserCreate
from app.schemas.user import User as UserSchema
from app.schemas.workspace import (
    ReviewData, 
    EngineResponseData, 
    ResponseData, 
    UserMessage, 
    ReplyInInteraction,
    StandardsRequest,
    StandardsResponse
)
from app.schemas.review_standard import SemanticSearchRequest
from app.models.user import User
from app.models.review_standard import ReviewStandard

from business.review_engine import MainReviewEngine, InterfaceAgent
from business.retrieval_service import RetrievalService
from business.standard_generation_service import StandardGenerationService

auth_service = AuthService()
router = APIRouter()

main_review_engine = MainReviewEngine()
interface_agent = InterfaceAgent()


@router.post("/standards", response_model=StandardsResponse, summary="获取审计证据标准")
async def get_audit_standards(
    form_data: StandardsRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    智能获取审计证据标准
    
    接收参数格式：
    {
        "status": "analysis",
        "type": "ai",
        "content": "审计结论或查询内容"
    }
    
    智能处理策略：
    1. 先尝试语义检索（相似度 >= 0.7）
    2. 如果没有找到合适的标准，自动使用AI生成
    
    返回：
    - 审计证据标准对象（包含审计结论和证据分类要求）
    """
    try:
        retrieval_service = RetrievalService(db)
        generation_service = StandardGenerationService(db)
        
        # 统一的AI智能处理策略
        # 1. 先尝试语义检索
        search_request = SemanticSearchRequest(
            query=form_data.content,
            top_k=1,  # 只返回最匹配的一条
            similarity_threshold=0.5  # 相似度阈值（降低以增加匹配成功率）
        )
        search_result = await retrieval_service.semantic_search(search_request)
        
        # 2. 如果找到合适的标准，直接返回
        if search_result.results and len(search_result.results) > 0:
            best_match = search_result.results[0]
            return StandardsResponse(
                审计证据标准=StandardsResponse.AuditEvidenceStandard(
                    审计结论=best_match.audit_conclusion,
                    审计证据分类与要求=best_match.evidence_classification
                )
            )
        
        # 3. 如果没有找到合适的标准，自动使用AI生成
        from app.schemas.review_standard import GenerateStandardRequest
        gen_req = GenerateStandardRequest(
            audit_conclusion=form_data.content,
            auto_save=False
        )
        generated = await generation_service.generate_standard(gen_req, current_user.id)
        
        return StandardsResponse(
            审计证据标准=StandardsResponse.AuditEvidenceStandard(
                审计结论=generated.审计结论,
                审计证据分类与要求=generated.审计证据分类与要求
            )
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取审计证据标准时发生错误: {str(e)}"
        )


@router.post("/chat", response_model=ReplyInInteraction, summary="对话交互")
async def reply_in_interaction(
    form_data: UserMessage,
    current_user: User = Depends(get_current_active_user)
):
    try:
        history = []
        for message in form_data.content:
            if message.get("type") == "ai":
                message = {"role":"assistant", "content":message.get("content")}
            else:
                message = {"role":"user", "content":message.get("content")}
            history.append(message) 
        result = interface_agent.chat_with_user(history)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"回复用户消息出错: {str(e)}"
        )

@router.post("/execute_review", response_model=EngineResponseData, summary="开始复核")
async def execute_review(
    form_data: ReviewData,
    current_user: User = Depends(get_current_active_user)
):
    try:
        result = main_review_engine.execute_review(form_data)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"执行复核时发生错误: {str(e)}"
        )


@router.post("/continue_review", response_model=EngineResponseData, summary="继续复核")
async def continue_review(
    form_data: dict,
    current_user: User = Depends(get_current_active_user)
):
    try:
        # 手动解析 ResponseData，避免 Pydantic Union 类型解析错误
        response_type = form_data.get("response_type")
        data = form_data.get("data")
        
        # 根据 response_type 构造正确的 ResponseData
        if response_type == "upload_file_response":
            # 数据是文件列表
            from app.schemas.workspace import ResponseData, WorkPaperFile
            work_paper_files = [WorkPaperFile(**file_data) for file_data in data]
            response_data = ResponseData(response_type=response_type, data=work_paper_files)
        elif response_type == "help_response":
            # 数据是帮助响应
            from app.schemas.workspace import ResponseData, HelpResponseData
            help_response = HelpResponseData(**data)
            response_data = ResponseData(response_type=response_type, data=help_response)
        else:
            raise ValueError(f"不支持的 response_type: {response_type}")
        
        result = main_review_engine.continue_review(response_data)
        return result
    except Exception as e:
        import traceback
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"继续复核时发生错误: {str(e)}")
        logger.error(f"错误堆栈: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"继续复核时发生错误: {str(e)}"
        )
