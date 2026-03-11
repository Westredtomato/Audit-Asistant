"""
数据库初始化脚本
"""

import asyncio
import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from sqlalchemy import text
from loguru import logger

from app.database_manager.database import engine, SessionLocal, Base, init_database
from app.models import *  # 导入所有模型
from business.system_config_service import settings

def create_database_if_not_exists():
    """创建数据库文件（如果不存在）"""
    # 确保数据目录存在
    settings.DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    # 对于SQLite，文件会在第一次连接时自动创建
    logger.info(f"数据库文件路径: {settings.DATABASE_URL}")


def create_tables():
    """创建所有数据表"""
    logger.info("正在创建数据库表...")
    
    try:
        # 创建所有表
        Base.metadata.create_all(bind=engine)
        logger.info("数据库表创建成功")
        
        # 显示创建的表
        with engine.connect() as conn:
            if "sqlite" in settings.DATABASE_URL.lower():
                result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
                tables = [row[0] for row in result]
                logger.info(f"已创建的表: {', '.join(tables)}")
            
    except Exception as e:
        logger.error(f"创建数据库表失败: {str(e)}")
        raise


def create_default_data():
    """创建默认数据"""
    logger.info("正在创建默认数据...")
    
    try:
        db = SessionLocal()
        
        # 创建默认审计依据方案
        create_default_audit_standards(db)
        
        # 创建默认系统模板
        create_default_templates(db)
        
        # 创建默认管理员用户（如果不存在）
        create_default_admin_user(db)
        
        db.close()
        logger.info("默认数据创建成功")
        
    except Exception as e:
        logger.error(f"创建默认数据失败: {str(e)}")
        raise


def create_default_audit_standards(db):
    """创建默认审计依据方案"""
    from app.models.project import AuditStandard
    import uuid
    
    # 检查是否已存在默认方案
    existing = db.query(AuditStandard).filter(AuditStandard.is_system_default == True).first()
    if existing:
        logger.info("默认审计依据方案已存在")
        return
    
    # 创建境内大型企业默认方案
    default_standard = AuditStandard(
        standard_id=str(uuid.uuid4()),
        name="境内大型企业标准方案",
        description="适用于境内大型企业的标准审计依据方案",
        accounting_standards=[
            {"name": "企业会计准则", "code": "CAS", "version": "2021"},
            {"name": "企业会计准则解释", "code": "CAS-INT", "version": "最新"}
        ],
        audit_standards=[
            {"name": "中国注册会计师审计准则", "code": "CSA", "version": "2021"},
            {"name": "中国注册会计师职业道德守则", "code": "CODE", "version": "2021"}
        ],
        basic_laws=[
            {"name": "公司法", "version": "2018修正"},
            {"name": "证券法", "version": "2019修订"},
            {"name": "会计法", "version": "2017修正"}
        ],
        special_regulations=[
            {"name": "上市公司信息披露管理办法", "authority": "证监会"},
            {"name": "企业内部控制基本规范", "authority": "财政部"}
        ],
        basic_regulations=[
            {"name": "会计基础工作规范", "authority": "财政部"},
            {"name": "企业财务会计报告条例", "authority": "国务院"}
        ],
        special_supervisions=[
            {"name": "上市公司治理准则", "authority": "证监会"},
            {"name": "企业国有资产监督管理暂行条例", "authority": "国资委"}
        ],
        applicable_conditions={
            "domestic": True,
            "listed": True,
            "company_scale": ["large"],
            "state_owned": None
        },
        is_system_default=True
    )
    
    db.add(default_standard)
    db.commit()
    logger.info("创建默认审计依据方案成功")


def create_default_templates(db):
    """创建默认系统模板"""
    from app.models.template import EventTemplate
    import uuid
    
    # 检查是否已存在系统模板
    existing = db.query(EventTemplate).filter(EventTemplate.is_system_template == True).first()
    if existing:
        logger.info("系统默认模板已存在")
        return
    
    # 持续经营重大事项模板
    going_concern_template = EventTemplate(
        template_id=str(uuid.uuid4()),
        name="持续经营重大疑虑事项模板",
        description="用于评估被审计单位持续经营能力的重大事项复核模板",
        category="持续经营",
        template_content={
            "summary": "被审计单位所属行业发生重大变化，导致对持续经营能力产生重大不确定性，可能导致收入舞弊风险等。",
            "audit_objective": "根据获取的审计证据，就\"被审计单位所属行业发生重大变化\"是否作为\"可能导致对被审计单位持续经营能力产生重大疑虑的事项或情况\"得出结论。",
            "evidence_standards": {
                "situation_one": {
                    "conclusion": "根据获取的审计证据，认为\"被审计单位所属行业发生重大变化\"应作为\"可能导致对被审计单位持续经营能力产生重大疑虑的事项或情况\"。",
                    "evidence_requirements": [
                        {
                            "category": "风险评估及计划工作底稿",
                            "subcategories": [
                                {
                                    "name": "了解被审计单位及其环境",
                                    "evidences": [
                                        {
                                            "content": "影响被审计单位的行业/市场因素",
                                            "quality_requirements": "证据来源必须为国家统计局、工信部、证监会、行业协会、交易所、央行等具有法定披露义务或公信力的机构..."
                                        }
                                    ]
                                }
                            ]
                        }
                    ]
                }
            }
        },
        applicable_conditions={
            "event_type": "significant_matter",
            "industry": ["manufacturing", "energy", "technology"],
            "categories": ["持续经营", "重大风险"]
        },
        is_system_template=True,
        is_public=True
    )
    
    db.add(going_concern_template)
    db.commit()
    logger.info("创建系统默认模板成功")


def create_default_admin_user(db):
    """创建默认管理员用户"""
    from app.models.user import User
    from app.modules.auth_service import AuthService
    import uuid
    
    # 检查是否已存在管理员用户
    admin_user = db.query(User).filter(User.username == "admin").first()
    if admin_user:
        logger.info("管理员用户已存在")
        return
    
    # 创建默认管理员
    auth_service = AuthService()
    password_hash = auth_service.get_password_hash("admin123")
    
    admin = User(
        user_id=str(uuid.uuid4()),
        username="admin",
        password_hash=password_hash,
        display_name="系统管理员",
        email="admin@cpa-assistant.com",
        role="admin",
        is_active=True,
        preferences={}
    )
    
    db.add(admin)
    db.commit()
    logger.info("创建默认管理员用户成功 (admin/admin123)")


async def main():
    """主函数"""
    logger.info("开始初始化数据库...")
    
    try:
        # 1. 创建数据库文件
        create_database_if_not_exists()
        
        # 2. 创建数据表
        create_tables()
        
        # 3. 创建默认数据
        create_default_data()
        
        logger.info("✅ 数据库初始化完成!")
        logger.info(f"📍 数据库文件位置: {settings.DATA_DIR / 'cpa_assistant.db'}")
        logger.info("🔐 默认管理员账号: admin / admin123")
        
    except Exception as e:
        logger.error(f"❌ 数据库初始化失败: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
