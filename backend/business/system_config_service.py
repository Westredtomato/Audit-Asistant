"""
系统配置文件
"""

import os
from pathlib import Path
from typing import Optional, List
from pydantic_settings import BaseSettings

# 添加项目根目录(backend)到 Python 路径
# 注意：本文件所处项目位置需要为backend/business/system_config_service.py
project_root = Path(__file__).parent.parent



class Settings(BaseSettings):
    """应用配置"""
    
    # 基础配置
    APP_NAME: str = "核瞳君"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # 服务器配置
    HOST: str = "127.0.0.1"
    PORT: int = 8000
     
    # 数据库配置
    DATABASE_URL: str = f"sqlite:///{rf"{project_root}"}/infrastructure/data/cpa_assistant.db"
    
    # 目录配置
    BASE_DIR: Path = project_root

    DATA_DIR: Path = BASE_DIR / "infrastructure/data"
    UPLOAD_DIR: Path = DATA_DIR / "uploads"
    EXCEL_FILE_DIR: Path = DATA_DIR / "uploads" / "excel_files"
    HTML_FILE_DIR: Path = DATA_DIR / "uploads" / "html_files"

    LOG_DIR: Path = DATA_DIR / "logs"
    TEMPLATE_DIR: Path = DATA_DIR / "templates"
    
    # 安全配置
    SECRET_KEY: str = "20232027"  # 生产环境需要修改
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480
    
    # LLM 配置
    API_KEY: Optional[str] = "sk-a36573a3d7c34db492b5cd68d54b5fdd"
    BASE_URL: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    LLM_MODAL: str = "qwen3-max"
    
    # 文件上传配置
    MAX_UPLOAD_SIZE: int = 100 * 1024 * 1024  # 100MB
    ALLOWED_FILE_TYPES: List[str] = [".xlsx", ".xls", ".pdf", ".docx", ".doc"]
    
    # Redis配置（消息队列）
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_URL: str = "redis://localhost:6379"
    
    # 项目相关配置
    MAX_PROJECTS_PER_USER: int = 50
    PROJECT_DATA_RETENTION_DAYS: int = 365
    
    # 复核配置
    DEFAULT_TIMEOUT_MINUTES: int = 30
    MAX_DRAFT_VERSIONS: int = 10
    MAX_EVENT_VERSIONS: int = 10
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# 创建全局配置实例
settings = Settings()



def get_project_data_dir(project_id: str) -> Path:
    """获取项目数据目录"""
    project_dir = settings.DATA_DIR / "projects" / project_id
    project_dir.mkdir(parents=True, exist_ok=True)
    return project_dir


def get_upload_dir(project_id: str) -> Path:
    """获取项目上传目录"""
    upload_dir = get_project_data_dir(project_id) / "uploads"
    upload_dir.mkdir(parents=True, exist_ok=True)
    return upload_dir
