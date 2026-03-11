"""
FastAPI 应用创建和配置
"""

import time
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from loguru import logger

from business.system_config_service import settings
from app.api.v1.api import api_router


def setup_middlewares(app: FastAPI):
    """设置中间件"""
    
    @app.middleware("http")
    async def log_requests(request, call_next):
        """请求日志中间件"""
        start_time = time.time()
        
        response = await call_next(request)
        
        process_time = time.time() - start_time
        logger.info(
            f"{request.method} {request.url.path} - "
            f"{response.status_code} - {process_time:.4f}s"
        )
        
        return response


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动
    logger.info("应用启动中...")
    yield
    # 关闭
    logger.info("应用关闭中...")


def create_app() -> FastAPI:
    """创建 FastAPI 应用"""
    
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="审计复核辅助软件",
        debug=settings.DEBUG,
        lifespan=lifespan
    )
    
    # 配置 CORS
    if settings.DEBUG:
        # 开发环境允许所有来源
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    else:
        # 生产环境设置具体的允许来源
        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.ALLOWED_ORIGINS if hasattr(settings, 'ALLOWED_ORIGINS') else ["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    
    # 注册路由
    app.include_router(api_router, prefix="/api/v1")
    
    # 静态文件服务
    # 确保静态文件目录存在
    settings.DATA_DIR.mkdir(parents=True, exist_ok=True)
    app.mount("/static", StaticFiles(directory=str(settings.DATA_DIR)), name="static")
    
    # 添加中间件
    setup_middlewares(app)
    
    return app

