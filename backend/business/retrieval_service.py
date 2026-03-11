"""
信息检索服务模块
实现复核标准的语义检索功能
"""
import json
import numpy as np
from typing import List, Dict, Optional, Tuple
from sqlalchemy.orm import Session
from loguru import logger
import httpx

from business.system_config_service import settings
from app.models.review_standard import ReviewStandard, ReviewStandardVector
from app.schemas.review_standard import (
    SemanticSearchRequest, 
    SemanticSearchResponse, 
    SemanticSearchResult
)


class EmbeddingService:
    """文本嵌入服务，用于生成文本向量"""
    
    def __init__(self):
        self.api_key = settings.API_KEY
        self.base_url = settings.BASE_URL
        self.model = "text-embedding-v3"  # 阿里云通义千问嵌入模型
        
    async def get_embedding(self, text: str) -> List[float]:
        """
        获取文本的向量表示
        
        Args:
            text: 要编码的文本
            
        Returns:
            向量列表
        """
        if not self.api_key:
            raise ValueError("API_KEY 未配置，请在系统配置中设置")
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": self.model,
                "input": text,
                "encoding_format": "float"
            }
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/embeddings",
                    headers=headers,
                    json=data
                )
                response.raise_for_status()
                
                result = response.json()
                embedding = result["data"][0]["embedding"]
                
                logger.info(f"成功生成文本嵌入，维度: {len(embedding)}")
                return embedding
                
        except Exception as e:
            logger.error(f"生成文本嵌入失败: {str(e)}")
            raise
    
    async def get_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """
        批量获取文本的向量表示
        
        Args:
            texts: 文本列表
            
        Returns:
            向量列表
        """
        if not self.api_key:
            raise ValueError("API_KEY 未配置")
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": self.model,
                "input": texts,
                "encoding_format": "float"
            }
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.base_url}/embeddings",
                    headers=headers,
                    json=data
                )
                response.raise_for_status()
                
                result = response.json()
                embeddings = [item["embedding"] for item in result["data"]]
                
                logger.info(f"成功批量生成 {len(embeddings)} 个文本嵌入")
                return embeddings
                
        except Exception as e:
            logger.error(f"批量生成文本嵌入失败: {str(e)}")
            raise


class VectorSearchService:
    """向量检索服务"""
    
    @staticmethod
    def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
        """
        计算余弦相似度
        
        Args:
            vec1: 向量1
            vec2: 向量2
            
        Returns:
            相似度分数 (0-1)
        """
        vec1_np = np.array(vec1)
        vec2_np = np.array(vec2)
        
        # 计算余弦相似度
        dot_product = np.dot(vec1_np, vec2_np)
        norm1 = np.linalg.norm(vec1_np)
        norm2 = np.linalg.norm(vec2_np)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        similarity = dot_product / (norm1 * norm2)
        # 将 [-1, 1] 范围映射到 [0, 1]
        return float((similarity + 1) / 2)
    
    @staticmethod
    def euclidean_distance(vec1: List[float], vec2: List[float]) -> float:
        """
        计算欧氏距离（已归一化）
        
        Args:
            vec1: 向量1
            vec2: 向量2
            
        Returns:
            距离分数 (0-1，越小越相似)
        """
        vec1_np = np.array(vec1)
        vec2_np = np.array(vec2)
        
        distance = np.linalg.norm(vec1_np - vec2_np)
        # 归一化到 0-1 范围（假设最大距离约为2）
        return float(1 - min(distance / 2, 1))


class RetrievalService:
    """信息检索服务，提供语义检索功能"""
    
    def __init__(self, db: Session):
        self.db = db
        self.embedding_service = EmbeddingService()
        self.vector_search = VectorSearchService()
    
    async def add_standard_with_embedding(
        self, 
        standard: ReviewStandard
    ) -> ReviewStandardVector:
        """
        为复核标准添加向量索引
        
        Args:
            standard: 复核标准对象
            
        Returns:
            向量索引对象
        """
        try:
            # 生成审计结论的向量
            embedding = await self.embedding_service.get_embedding(
                standard.audit_conclusion
            )
            
            # 创建向量索引
            vector_index = ReviewStandardVector(
                standard_id=standard.id,
                vector_data=json.dumps(embedding),
                vector_dimension=len(embedding),
                embedding_model=self.embedding_service.model
            )
            
            self.db.add(vector_index)
            self.db.commit()
            self.db.refresh(vector_index)
            
            logger.info(f"成功为标准 {standard.id} 创建向量索引")
            return vector_index
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"创建向量索引失败: {str(e)}")
            raise
    
    async def update_standard_embedding(self, standard_id: int) -> bool:
        """
        更新复核标准的向量索引
        
        Args:
            standard_id: 复核标准ID
            
        Returns:
            是否成功
        """
        try:
            standard = self.db.query(ReviewStandard).filter(
                ReviewStandard.id == standard_id
            ).first()
            
            if not standard:
                raise ValueError(f"标准 {standard_id} 不存在")
            
            # 删除旧的向量索引
            self.db.query(ReviewStandardVector).filter(
                ReviewStandardVector.standard_id == standard_id
            ).delete()
            
            # 创建新的向量索引
            await self.add_standard_with_embedding(standard)
            
            return True
            
        except Exception as e:
            logger.error(f"更新向量索引失败: {str(e)}")
            return False
    
    async def semantic_search(
        self, 
        request: SemanticSearchRequest
    ) -> SemanticSearchResponse:
        """
        语义检索复核标准
        
        Args:
            request: 检索请求
            
        Returns:
            检索结果
        """
        try:
            # 1. 生成查询向量
            query_embedding = await self.embedding_service.get_embedding(request.query)
            
            # 2. 构建查询条件
            query = self.db.query(ReviewStandard)
            
            if request.category:
                query = query.filter(ReviewStandard.category == request.category)
            
            if request.project_id:
                query = query.filter(ReviewStandard.project_id == request.project_id)
            
            # 获取所有候选标准
            candidates = query.all()
            
            if not candidates:
                return SemanticSearchResponse(
                    query=request.query,
                    results=[],
                    total_found=0
                )
            
            # 3. 获取向量并计算相似度
            results_with_scores: List[Tuple[ReviewStandard, float]] = []
            
            for standard in candidates:
                # 获取标准的向量
                vector_record = self.db.query(ReviewStandardVector).filter(
                    ReviewStandardVector.standard_id == standard.id
                ).first()
                
                if vector_record:
                    standard_embedding = json.loads(vector_record.vector_data)
                    
                    # 计算相似度
                    similarity = self.vector_search.cosine_similarity(
                        query_embedding, 
                        standard_embedding
                    )
                    
                    # 过滤低于阈值的结果
                    if similarity >= request.similarity_threshold:
                        results_with_scores.append((standard, similarity))
            
            # 4. 按相似度排序并取top_k
            results_with_scores.sort(key=lambda x: x[1], reverse=True)
            top_results = results_with_scores[:request.top_k]
            
            # 5. 构建响应
            search_results = [
                SemanticSearchResult(
                    standard_id=standard.id,
                    title=standard.title,
                    audit_conclusion=standard.audit_conclusion,
                    evidence_classification=standard.evidence_classification,
                    similarity_score=round(score, 4),
                    category=standard.category,
                    tags=standard.tags,
                    usage_count=standard.usage_count
                )
                for standard, score in top_results
            ]
            
            logger.info(f"语义检索完成，找到 {len(search_results)} 个相似结果")
            
            return SemanticSearchResponse(
                query=request.query,
                results=search_results,
                total_found=len(search_results)
            )
            
        except Exception as e:
            logger.error(f"语义检索失败: {str(e)}")
            raise
    
    async def batch_update_all_embeddings(self) -> Dict[str, int]:
        """
        批量更新所有标准的向量索引（用于初始化或重建索引）
        
        Returns:
            更新统计信息
        """
        try:
            # 获取所有标准
            standards = self.db.query(ReviewStandard).all()
            
            success_count = 0
            failed_count = 0
            
            for standard in standards:
                try:
                    # 检查是否已有向量
                    existing_vector = self.db.query(ReviewStandardVector).filter(
                        ReviewStandardVector.standard_id == standard.id
                    ).first()
                    
                    if not existing_vector:
                        await self.add_standard_with_embedding(standard)
                        success_count += 1
                    else:
                        logger.info(f"标准 {standard.id} 已有向量索引，跳过")
                        
                except Exception as e:
                    logger.error(f"处理标准 {standard.id} 失败: {str(e)}")
                    failed_count += 1
            
            logger.info(f"批量更新完成: 成功 {success_count}, 失败 {failed_count}")
            
            return {
                "total": len(standards),
                "success": success_count,
                "failed": failed_count,
                "skipped": len(standards) - success_count - failed_count
            }
            
        except Exception as e:
            logger.error(f"批量更新向量索引失败: {str(e)}")
            raise

