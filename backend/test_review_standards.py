"""
复核标准功能测试脚本
用于快速测试复核标准的各项功能
"""
import asyncio
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from app.database_manager.database import SessionLocal
from app.schemas.review_standard import (
    SemanticSearchRequest,
    GenerateStandardRequest
)
from business.retrieval_service import RetrievalService
from business.standard_generation_service import StandardGenerationService
from loguru import logger


async def test_semantic_search():
    """测试语义检索功能"""
    print("\n" + "="*60)
    print("测试 1: 语义检索功能")
    print("="*60)
    
    db = SessionLocal()
    try:
        retrieval_service = RetrievalService(db)
        
        # 测试查询
        test_query = "被审计单位开立了多个银行账户，其中部分账户长期未使用，存在资金管理风险"
        
        print(f"\n查询文本: {test_query}")
        print("\n正在检索...")
        
        request = SemanticSearchRequest(
            query=test_query,
            top_k=3,
            similarity_threshold=0.6
        )
        
        result = await retrieval_service.semantic_search(request)
        
        print(f"\n找到 {result.total_found} 个相似结果:\n")
        
        for idx, item in enumerate(result.results, 1):
            print(f"{idx}. 标准ID: {item.standard_id}")
            print(f"   标题: {item.title}")
            print(f"   相似度: {item.similarity_score:.4f}")
            print(f"   分类: {item.category}")
            print(f"   审计结论预览: {item.audit_conclusion[:100]}...")
            print()
        
        return result
        
    except Exception as e:
        logger.error(f"语义检索测试失败: {str(e)}")
        raise
    finally:
        db.close()


async def test_generate_standard():
    """测试AI生成复核标准功能"""
    print("\n" + "="*60)
    print("测试 2: AI 生成复核标准")
    print("="*60)
    
    db = SessionLocal()
    try:
        generation_service = StandardGenerationService(db)
        
        # 测试审计结论
        test_conclusion = """经审计，被审计单位2023年度应收账款余额较大，占总资产的35%。
        通过函证程序，发现前五大客户中有2家未能及时回函，占应收账款总额的18%。
        对于未回函客户，实施了替代审计程序，包括检查期后回款、销售合同、发货单据等，
        未发现重大异常。但考虑到应收账款金额重大且部分客户未回函，将应收账款的存在性
        和可收回性认定为重大事项，需要在审计工作底稿中予以特别关注。"""
        
        print(f"\n审计结论:\n{test_conclusion}")
        print("\n正在生成复核标准...")
        print("（这可能需要10-30秒，请耐心等待）\n")
        
        request = GenerateStandardRequest(
            audit_conclusion=test_conclusion,
            auto_save=False,  # 测试时不保存
            title="应收账款函证复核标准（测试生成）"
        )
        
        result = await generation_service.generate_standard(request, user_id=1)
        
        print("✓ 生成成功!")
        print(f"\n生成的标题: {result.generated_title}")
        print(f"参考了 {result.reference_count} 个已有标准")
        print(f"\n审计结论: {result.审计结论[:100]}...")
        print(f"\n证据分类数量: {len(result.审计证据分类与要求)}")
        
        # 显示第一个分类的详情
        if result.审计证据分类与要求:
            first_category = result.审计证据分类与要求[0]
            print(f"\n第一个证据分类示例:")
            for level1, level2_dict in first_category.items():
                print(f"\n  一级分类: {level1}")
                for level2, evidences in level2_dict.items():
                    print(f"    二级分类: {level2}")
                    print(f"    证据数量: {len(evidences)}")
                    if evidences:
                        print(f"    第一个证据: {evidences[0].get('证据内容', '')}")
        
        return result
        
    except Exception as e:
        logger.error(f"生成复核标准测试失败: {str(e)}")
        raise
    finally:
        db.close()


async def test_create_and_search():
    """测试创建标准后立即检索"""
    print("\n" + "="*60)
    print("测试 3: 创建标准并检索")
    print("="*60)
    
    db = SessionLocal()
    try:
        from app.models.review_standard import ReviewStandard
        from business.retrieval_service import RetrievalService
        
        # 创建一个测试标准
        test_standard = ReviewStandard(
            title="固定资产盘点复核标准（测试）",
            audit_conclusion="经审计，被审计单位固定资产账实不符，部分资产已报废但未及时处理，存在资产管理不规范的问题。",
            evidence_classification=[
                {
                    "固定资产": {
                        "存在": [
                            {
                                "证据内容": "固定资产盘点表",
                                "质量要求": "证据来源于被审计单位，需由盘点人员和监盘人员签字确认。"
                            }
                        ]
                    }
                }
            ],
            category="固定资产",
            tags="盘点,存在性",
            source="test_created"
        )
        
        db.add(test_standard)
        db.commit()
        db.refresh(test_standard)
        
        print(f"\n✓ 创建测试标准，ID: {test_standard.id}")
        
        # 为新标准创建向量索引
        retrieval_service = RetrievalService(db)
        await retrieval_service.add_standard_with_embedding(test_standard)
        
        print("✓ 向量索引创建成功")
        
        # 立即检索这个标准
        print("\n正在检索刚创建的标准...")
        
        search_request = SemanticSearchRequest(
            query="固定资产盘点存在差异，账实不符",
            top_k=5,
            similarity_threshold=0.5
        )
        
        search_result = await retrieval_service.semantic_search(search_request)
        
        # 检查是否能找到刚创建的标准
        found = False
        for item in search_result.results:
            if item.standard_id == test_standard.id:
                found = True
                print(f"\n✓ 成功检索到刚创建的标准!")
                print(f"  相似度: {item.similarity_score:.4f}")
                break
        
        if not found:
            print(f"\n✗ 未能检索到刚创建的标准（可能相似度过低）")
        
        # 清理测试数据
        from app.models.review_standard import ReviewStandardVector
        db.query(ReviewStandardVector).filter(
            ReviewStandardVector.standard_id == test_standard.id
        ).delete()
        db.delete(test_standard)
        db.commit()
        
        print("\n✓ 测试数据已清理")
        
    except Exception as e:
        db.rollback()
        logger.error(f"创建和检索测试失败: {str(e)}")
        raise
    finally:
        db.close()


async def test_statistics():
    """测试统计功能"""
    print("\n" + "="*60)
    print("测试 4: 统计信息")
    print("="*60)
    
    db = SessionLocal()
    try:
        from app.models.review_standard import ReviewStandard
        
        # 总数统计
        total = db.query(ReviewStandard).count()
        print(f"\n复核标准总数: {total}")
        
        # 按分类统计
        from sqlalchemy import func
        by_category = db.query(
            ReviewStandard.category,
            func.count(ReviewStandard.id)
        ).group_by(ReviewStandard.category).all()
        
        print("\n按分类统计:")
        for category, count in by_category:
            print(f"  {category or '未分类'}: {count}")
        
        # 按来源统计
        by_source = db.query(
            ReviewStandard.source,
            func.count(ReviewStandard.id)
        ).group_by(ReviewStandard.source).all()
        
        print("\n按来源统计:")
        for source, count in by_source:
            print(f"  {source or '未知'}: {count}")
        
        # 最常用的标准
        most_used = db.query(ReviewStandard).order_by(
            ReviewStandard.usage_count.desc()
        ).limit(3).all()
        
        print("\n最常用的标准:")
        for std in most_used:
            print(f"  {std.title} (使用次数: {std.usage_count})")
        
    except Exception as e:
        logger.error(f"统计信息测试失败: {str(e)}")
        raise
    finally:
        db.close()


async def main():
    """主测试函数"""
    print("\n" + "="*60)
    print("复核标准功能测试")
    print("="*60)
    print("\n注意: 请确保已配置 API_KEY 环境变量")
    print("      否则语义检索和AI生成功能将无法使用\n")
    
    try:
        # 测试 1: 语义检索
        await test_semantic_search()
        
        # 测试 2: AI 生成（需要API Key）
        try:
            await test_generate_standard()
        except ValueError as e:
            if "API_KEY" in str(e):
                print("\n⚠ 跳过AI生成测试（未配置API_KEY）")
            else:
                raise
        
        # 测试 3: 创建和检索
        try:
            await test_create_and_search()
        except ValueError as e:
            if "API_KEY" in str(e):
                print("\n⚠ 跳过创建和检索测试（未配置API_KEY）")
            else:
                raise
        
        # 测试 4: 统计信息
        await test_statistics()
        
        print("\n" + "="*60)
        print("所有测试完成!")
        print("="*60)
        
    except Exception as e:
        print(f"\n✗ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())

