"""
注会帮 - 审计复核辅助软件
主启动文件
"""

import sys
import os
from pathlib import Path
import asyncio
import uvicorn
from loguru import logger

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent
sys.path.append(str(project_root))

# 添加 review_engine 目录到 Python 路径
review_engine_path = project_root / "business"
sys.path.append(str(review_engine_path))

# 添加 review_engine 目录到 Python 路径
review_engine_path = project_root / "business" / "review_engine"
sys.path.append(str(review_engine_path))

# 添加 review_engine 目录到 Python 路径
review_engine_path = project_root / "business" / "review_engine" / "agent"
sys.path.append(str(review_engine_path))

from business.system_config_service import settings
from business.start_redis import init_redis_service
from app.application import create_app
from app.database_manager.database import init_database


async def init_system():
    """系统初始化"""
    logger.info("正在初始化注会帮系统...")
    
    # 初始化数据库
    await init_database()
    logger.info("数据库初始化完成")
    
    # 初始化复核标准示例数据
    try:
        from app.database_manager.init_review_standards import init_sample_standards
        from app.database_manager.database import SessionLocal
        db = SessionLocal()
        try:
            await init_sample_standards(db)
        finally:
            db.close()
    except Exception as e:
        logger.warning(f"初始化复核标准示例数据失败（可能已存在）: {str(e)}")
    
    # 创建必要的目录
    os.makedirs(settings.DATA_DIR, exist_ok=True)
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    os.makedirs(settings.LOG_DIR, exist_ok=True)
    os.makedirs(settings.EXCEL_FILE_DIR, exist_ok=True)
    os.makedirs(settings.HTML_FILE_DIR, exist_ok=True)
    
    logger.info("必要的目录初始化完成")

    # 启动Redis服务
    #if init_redis_service():
        #logger.info("启动Redis服务完成")
    #else:
        #logger.error("启动Redis服务失败")





def main():
    """主启动函数"""
    try:
        # 配置日志
        logger.add(
            settings.LOG_DIR / "app.log",
            rotation="500 MB",
            retention="10 days",
            level="INFO"
        )
        
        logger.info("启动注会帮系统...")
        
        # 初始化系统
        asyncio.run(init_system())
        
        # 创建 FastAPI 应用
        app = create_app()
        
        # 启动服务器
        uvicorn.run(
            app,
            host=settings.HOST,
            port=settings.PORT,
            log_level="info",
            access_log=True
        )
        
    except Exception as e:
        logger.error(f"系统启动失败: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
