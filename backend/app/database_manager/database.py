"""
数据库配置和连接管理
"""
import os
import sys
from pathlib import Path

from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
import asyncio
from loguru import logger

project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))
from business.system_config_service import settings

# 同步数据库引擎
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {},
    echo=settings.DEBUG
)

# 异步数据库引擎（SQLite 不支持异步，这里为扩展性预留）
if "sqlite" not in settings.DATABASE_URL:
    async_engine = create_async_engine(settings.DATABASE_URL)
else:
    async_engine = None

# 数据库会话
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
if async_engine:
    AsyncSessionLocal = sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)
else:
    AsyncSessionLocal = None

# 数据库基类
Base = declarative_base()

# 元数据
#metadata = MetaData()


def get_db():
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_async_db():
    """获取异步数据库会话"""
    if AsyncSessionLocal is None:
        raise RuntimeError("异步数据库会话未配置")
    
    async with AsyncSessionLocal() as session:
        yield session


async def init_database():
    """初始化数据库"""
    try:
        logger.info("正在创建数据库表...")
        
        from app.models import user, project, draft, event, template, message
        
        # 创建所有表
        # 注意：需要导入sys.modules的Base类，否则将引用本模块一开始未被更新的Base类.
        # 导入任意模块的Base类均指向同一sys.modules的Base类
        user.Base.metadata.create_all(bind=engine)
        
        logger.info("数据库表创建完成")
        
        # 创建默认数据
        await create_default_data()
        
    except Exception as e:
        logger.error(f"数据库初始化失败: {str(e)}")
        raise


async def create_default_data():
    """创建默认数据"""
    try:
        from app.models.user import User
        from app.modules.auth_service import AuthService
        
        db = SessionLocal()
        
        # 检查是否已有管理员用户
        admin_user = db.query(User).filter(User.username == "admin").first()
        if not admin_user:
            # 创建默认管理员用户
            auth_service = AuthService()
            # 使用同步方法而不是异步方法
            auth_service.create_default_admin(db)
            logger.info("创建默认管理员用户: admin/admin123")
        
        db.close()
        
    except Exception as e:
        logger.error(f"创建默认数据失败: {str(e)}")


def reset_database():
    """重置数据库（开发环境使用）"""
    if not settings.DEBUG:
        raise RuntimeError("只能在调试模式下重置数据库")
    
    logger.warning("正在重置数据库...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    logger.info("数据库重置完成")


if __name__ == "__main__":
    asyncio.run(init_database())