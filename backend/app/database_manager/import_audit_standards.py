"""
导入审计证据标准库数据
将审计证据标准库目录下的JSON文件导入到数据库
"""
import asyncio
import json
import sys
from pathlib import Path
from typing import List, Dict, Any
from sqlalchemy.orm import Session

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from app.database_manager.database import SessionLocal
from app.models.review_standard import ReviewStandard
from business.retrieval_service import RetrievalService
from loguru import logger


# 审计证据标准库文件路径
AUDIT_STANDARDS_DIR = project_root / "infrastructure" / "database" / "audit_database"

# 文件映射（文件名到分类和标签的映射）
FILE_MAPPINGS = {
    "审计证据标准_货币资金.json": {
        "category": "货币资金",
        "tags": "银行存款,货币资金,完整性,存在"
    },
    "审计证据标准_营业收入.json": {
        "category": "营业收入",
        "tags": "营业收入,收入确认,合同管理"
    },
    "审计证据标准_应收账款（含收入）函证程序.json": {
        "category": "应收账款",
        "tags": "应收账款,函证程序,收入确认"
    },
    "审计证据标准_持续经营.json": {
        "category": "持续经营",
        "tags": "持续经营,预算预测,假设评估"
    },
    "审计证据标准_舞弊风险评估与应对.json": {
        "category": "舞弊风险",
        "tags": "舞弊风险,风险评估,分析程序"
    }
}


def load_json_file(file_path: Path) -> List[Dict[str, Any]]:
    """
    加载JSON文件
    
    Args:
        file_path: 文件路径
        
    Returns:
        JSON数据列表
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            logger.info(f"成功加载文件: {file_path.name}")
            return data
    except Exception as e:
        logger.error(f"加载文件 {file_path.name} 失败: {str(e)}")
        raise


def extract_title_from_filename(filename: str) -> str:
    """
    从文件名提取标题
    
    Args:
        filename: 文件名
        
    Returns:
        标题
    """
    # 移除"审计证据标准_"前缀和".json"后缀
    title = filename.replace("审计证据标准_", "").replace(".json", "")
    return f"{title}复核标准"


def convert_to_review_standard(
    json_data: Dict[str, Any],
    filename: str,
    file_mapping: Dict[str, str]
) -> Dict[str, Any]:
    """
    将JSON数据转换为ReviewStandard格式
    
    Args:
        json_data: JSON数据
        filename: 文件名
        file_mapping: 文件映射信息
        
    Returns:
        ReviewStandard格式的字典
    """
    return {
        "title": extract_title_from_filename(filename),
        "audit_conclusion": json_data.get("审计结论", ""),
        "evidence_classification": json_data.get("审计证据分类与要求", []),
        "category": file_mapping.get("category", "其他"),
        "tags": file_mapping.get("tags", ""),
        "source": "imported",
        "usage_count": 0
    }


async def import_audit_standards(db: Session):
    """
    导入所有审计证据标准
    
    Args:
        db: 数据库会话
    """
    try:
        logger.info("=" * 60)
        logger.info("开始导入审计证据标准库...")
        logger.info("=" * 60)
        
        # 检查标准库目录是否存在
        if not AUDIT_STANDARDS_DIR.exists():
            logger.error(f"审计证据标准库目录不存在: {AUDIT_STANDARDS_DIR}")
            return
        
        # 创建检索服务
        retrieval_service = RetrievalService(db)
        
        # 统计信息
        total_files = 0
        total_standards = 0
        success_count = 0
        failed_count = 0
        skipped_count = 0
        
        # 遍历所有JSON文件
        for filename, file_mapping in FILE_MAPPINGS.items():
            file_path = AUDIT_STANDARDS_DIR / filename
            
            if not file_path.exists():
                logger.warning(f"文件不存在，跳过: {filename}")
                continue
            
            total_files += 1
            logger.info(f"\n处理文件: {filename}")
            
            try:
                # 加载JSON文件
                json_data_list = load_json_file(file_path)
                
                # 处理每条标准数据
                for json_data in json_data_list:
                    total_standards += 1
                    
                    try:
                        # 转换为ReviewStandard格式
                        standard_data = convert_to_review_standard(
                            json_data,
                            filename,
                            file_mapping
                        )
                        
                        # 检查是否已存在相同标题的标准
                        existing = db.query(ReviewStandard).filter(
                            ReviewStandard.title == standard_data["title"]
                        ).first()
                        
                        if existing:
                            logger.info(f"  - 标准已存在，跳过: {standard_data['title']}")
                            skipped_count += 1
                            continue
                        
                        # 创建ReviewStandard对象
                        standard = ReviewStandard(**standard_data)
                        db.add(standard)
                        db.commit()
                        db.refresh(standard)
                        
                        logger.info(f"  - 创建复核标准: {standard.title} (ID: {standard.id})")
                        
                        # 生成向量索引
                        try:
                            await retrieval_service.add_standard_with_embedding(standard)
                            logger.info(f"  - 成功生成向量索引")
                            success_count += 1
                        except Exception as e:
                            logger.error(f"  - 生成向量索引失败: {str(e)}")
                            # 即使向量生成失败，也保留标准记录
                            success_count += 1
                        
                    except Exception as e:
                        db.rollback()
                        logger.error(f"  - 创建复核标准失败: {str(e)}")
                        failed_count += 1
                
            except Exception as e:
                logger.error(f"处理文件 {filename} 失败: {str(e)}")
        
        # 输出统计信息
        logger.info("\n" + "=" * 60)
        logger.info("导入完成！统计信息：")
        logger.info("=" * 60)
        logger.info(f"处理文件数: {total_files}")
        logger.info(f"总标准数: {total_standards}")
        logger.info(f"成功导入: {success_count}")
        logger.info(f"跳过（已存在）: {skipped_count}")
        logger.info(f"失败: {failed_count}")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"导入审计证据标准失败: {str(e)}")
        raise


async def main():
    """主函数"""
    db = SessionLocal()
    try:
        await import_audit_standards(db)
    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(main())
