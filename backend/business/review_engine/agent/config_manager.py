"""
控制器模块
"""
import sys
import os
from pathlib import Path
from loguru import logger

# 添加项目根目录(backend/)到 Python 路径
project_root = Path(__file__).parent.parent.parent.parent
sys.path.append(str(project_root))

from business.system_config_service import settings

class Controller:

    def init_config():
        """初始化配置"""
        if settings.API_KEY:
            API_KEY = settings.API_KEY
        else:
            API_KEY = "sk-a36573a3d7c34db492b5cd68d54b5fdd"
        review_config = {
            "LLM_CONFIG": {"API_KEY": API_KEY,
                            "BASE_URL": settings.BASE_URL,
                            "LLM_MODAL": settings.LLM_MODAL},
            "MAX_TRIES": 2,
            "WAIT_TIMES": {
                "file_loading": 10,
                "replying": 20
            },
            "HTML_FILE_DIR": settings.HTML_FILE_DIR,
            "EXCEL_FILE_DIR": settings.EXCEL_FILE_DIR
        }    
        return review_config        

    review_config = init_config() 


