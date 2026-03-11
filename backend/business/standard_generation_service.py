"""
复核标准生成服务
使用LLM根据审计结论和参考标准生成复核标准
"""
import json
import re
from typing import List, Dict, Optional, Any
from sqlalchemy.orm import Session
from loguru import logger
from openai import OpenAI

from business.system_config_service import settings
from app.models.review_standard import ReviewStandard
from app.schemas.review_standard import (
    GenerateStandardRequest,
    GenerateStandardResponse,
    SemanticSearchRequest
)
from business.retrieval_service import RetrievalService


class StandardGenerationService:
    """复核标准生成服务"""
    
    def __init__(self, db: Session):
        self.db = db
        self.retrieval_service = RetrievalService(db)
        
        # 初始化 OpenAI 客户端（兼容阿里云通义千问）
        if not settings.API_KEY:
            raise ValueError("API_KEY 未配置，请在系统配置中设置")
        
        self.client = OpenAI(
            api_key=settings.API_KEY,
            base_url=settings.BASE_URL
        )
        self.model = settings.LLM_MODAL
    
    def _extract_json_from_response(self, response_text: str) -> Optional[Dict]:
        """
        从LLM响应中提取JSON内容
        
        Args:
            response_text: LLM原始响应
            
        Returns:
            解析后的JSON对象，如果失败返回None
        """
        try:
            # 尝试直接解析
            return json.loads(response_text)
        except json.JSONDecodeError:
            # 尝试提取 ```json ... ``` 块
            json_match = re.search(r'```json\s*(\{.*?\})\s*```', response_text, re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group(1))
                except json.JSONDecodeError:
                    pass
            
            # 尝试提取 {...} 块
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group(0))
                except json.JSONDecodeError:
                    pass
            
            logger.error("无法从响应中提取有效的JSON")
            return None
    
    def _build_generation_prompt(
        self, 
        audit_conclusion: str, 
        reference_standards: Optional[List[Dict]] = None
    ) -> str:
        """
        构建生成复核标准的提示词
        
        Args:
            audit_conclusion: 审计结论
            reference_standards: 参考的复核标准列表
            
        Returns:
            完整的提示词
        """
        prompt = f"""# 你的角色
你是一名资深的审计专家和质量控制专家，精通审计准则和质量控制标准。你的任务是根据审计结论生成对应的复核标准。

# 任务说明
根据给定的审计结论，生成详细的审计证据分类与质量要求。复核标准用于指导对审计工作底稿的充分性和适当性进行复核。

# 输入的审计结论
```
{audit_conclusion}
```

"""
        
        # 如果有参考标准，添加到提示词中
        if reference_standards and len(reference_standards) > 0:
            prompt += f"""# 参考标准（供参考）
以下是与该审计结论语义相似的已有复核标准，可以参考其结构和内容，但需要根据新的审计结论进行调整和优化：

"""
            for idx, ref in enumerate(reference_standards, 1):
                prompt += f"""## 参考标准 {idx}
**审计结论**: {ref.get('audit_conclusion', '')[:200]}...

**证据分类与要求**:
```json
{json.dumps(ref.get('evidence_classification', []), ensure_ascii=False, indent=2)[:500]}...
```

"""
        
        prompt += """# 输出要求
请严格按照以下JSON格式输出复核标准。你的输出必须是合法的JSON，不要包含任何额外的文字说明。

## 输出格式
```json
{
    "审计结论": "与输入的审计结论保持一致",
    "审计证据分类与要求": [
        {
            "实质性工作底稿": {
                "银行存款": [
                    {
                        "证据内容": "具体的证据内容描述（如：银行存款余额调节表）",
                        "质量要求": "详细的质量要求说明，包括：证据来源、证据形式、证据的相关性、证据对财务报表认定的支持作用等"
                    },
                    {
                        "证据内容": "另一个证据内容",
                        "质量要求": "对应的质量要求"
                    }
                ],
                "营业收入": [
                    {
                        "证据内容": "...",
                        "质量要求": "..."
                    }
                ]
            }
        },
        {
            "特定事项底稿": {
                "持续经营": [
                    {
                        "证据内容": "...",
                        "质量要求": "..."
                    }
                ],
                "舞弊风险评估与应对": [
                    {
                        "证据内容": "...",
                        "质量要求": "..."
                    }
                ]
            }
        }
    ]
}
```

## 关键要求
1. **一级分类**必须是底稿类型（如：实质性工作底稿、特定事项底稿）
2. **二级分类**必须是审计对象的具体项目（如：银行存款、营业收入、应收账款、持续经营、舞弊风险评估与应对等）
3. **证据内容**要具体明确，指出需要的具体文件或程序
4. **质量要求**要详细说明：
   - 证据来源（被审计单位/第三方）
   - 证据形式（原件/复印件/电子文档等）
   - 证据的相关性（与审计结论的关系）
   - 证据对认定的支持（如何支持某项认定）
5. 确保输出的JSON格式正确，可以被直接解析

# 现在开始生成
请直接输出JSON格式的复核标准，不要包含任何其他文字。
"""
        
        return prompt
    
    async def generate_standard(
        self, 
        request: GenerateStandardRequest,
        user_id: Optional[int] = None
    ) -> GenerateStandardResponse:
        """
        生成复核标准
        
        Args:
            request: 生成请求
            user_id: 用户ID（用于保存标准）
            
        Returns:
            生成的复核标准
        """
        try:
            logger.info(f"开始生成复核标准，审计结论长度: {len(request.audit_conclusion)}")
            
            # 1. 如果提供了参考标准ID，获取这些标准
            reference_standards = []
            if request.reference_standards:
                for std_id in request.reference_standards:
                    standard = self.db.query(ReviewStandard).filter(
                        ReviewStandard.id == std_id
                    ).first()
                    if standard:
                        reference_standards.append({
                            "audit_conclusion": standard.audit_conclusion,
                            "evidence_classification": standard.evidence_classification
                        })
            
            # 2. 如果没有提供参考标准，尝试自动检索
            elif not request.reference_standards:
                logger.info("未提供参考标准，执行自动语义检索")
                search_request = SemanticSearchRequest(
                    query=request.audit_conclusion,
                    top_k=3,
                    similarity_threshold=0.7
                )
                search_result = await self.retrieval_service.semantic_search(search_request)
                
                for result in search_result.results:
                    reference_standards.append({
                        "audit_conclusion": result.audit_conclusion,
                        "evidence_classification": result.evidence_classification
                    })
                
                logger.info(f"自动检索到 {len(reference_standards)} 个参考标准")
            
            # 3. 构建提示词
            prompt = self._build_generation_prompt(
                request.audit_conclusion,
                reference_standards if reference_standards else None
            )
            
            # 4. 调用LLM生成
            logger.info("调用LLM生成复核标准...")
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "你是一名资深的审计专家和质量控制专家，精通审计准则和质量控制标准。"
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=4000
            )
            
            response_text = response.choices[0].message.content
            logger.info(f"LLM响应长度: {len(response_text)}")
            
            # 5. 解析响应
            generated_data = self._extract_json_from_response(response_text)
            
            if not generated_data:
                raise ValueError("无法解析LLM响应为有效的JSON格式")
            
            # 6. 验证必需字段
            if "审计结论" not in generated_data or "审计证据分类与要求" not in generated_data:
                raise ValueError("生成的标准缺少必需字段")
            
            # 7. 生成标题
            generated_title = request.title
            if not generated_title:
                # 从审计结论中提取关键信息作为标题
                conclusion_preview = request.audit_conclusion[:50]
                generated_title = f"复核标准 - {conclusion_preview}..."
            
            # 8. 如果需要自动保存
            saved = False
            saved_id = None
            
            if request.auto_save:
                try:
                    new_standard = ReviewStandard(
                        title=generated_title,
                        audit_conclusion=generated_data["审计结论"],
                        evidence_classification=generated_data["审计证据分类与要求"],
                        source="llm_generated",
                        created_by=user_id,
                        project_id=request.project_id
                    )
                    
                    self.db.add(new_standard)
                    self.db.commit()
                    self.db.refresh(new_standard)
                    
                    # 为新标准创建向量索引
                    await self.retrieval_service.add_standard_with_embedding(new_standard)
                    
                    saved = True
                    saved_id = new_standard.id
                    logger.info(f"复核标准已保存，ID: {saved_id}")
                    
                except Exception as e:
                    self.db.rollback()
                    logger.error(f"保存复核标准失败: {str(e)}")
            
            # 9. 构建响应
            return GenerateStandardResponse(
                审计结论=generated_data["审计结论"],
                审计证据分类与要求=generated_data["审计证据分类与要求"],
                generated_title=generated_title,
                reference_count=len(reference_standards),
                saved=saved,
                saved_id=saved_id
            )
            
        except Exception as e:
            logger.error(f"生成复核标准失败: {str(e)}")
            raise
    
    def regenerate_with_feedback(
        self, 
        original_result: Dict[str, Any],
        feedback: str
    ) -> Dict[str, Any]:
        """
        根据反馈重新生成标准
        
        Args:
            original_result: 原始生成结果
            feedback: 用户反馈
            
        Returns:
            新的生成结果
        """
        # 构建包含反馈的提示词
        prompt = f"""之前生成的复核标准如下：
```json
{json.dumps(original_result, ensure_ascii=False, indent=2)}
```

用户反馈：{feedback}

请根据用户反馈，调整和优化复核标准，并以JSON格式输出。
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "你是一名资深的审计专家，请根据反馈优化复核标准。"
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7
            )
            
            response_text = response.choices[0].message.content
            return self._extract_json_from_response(response_text)
            
        except Exception as e:
            logger.error(f"重新生成失败: {str(e)}")
            raise

