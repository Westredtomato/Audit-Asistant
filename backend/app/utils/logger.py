import logging
import os
from pathlib import Path
from loguru import logger as loguru_logger
from business.system_config_service import settings

# 配置loguru日志格式
loguru_logger.remove()  # 移除默认的日志配置

# 添加控制台日志输出
loguru_logger.add(
    "logs/app_{time:YYYY-MM-DD}.log",
    rotation="500 MB",
    retention="10 days",
    level="INFO",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} - {message}"
)

# 添加控制台输出
loguru_logger.add(
    "logs/error_{time:YYYY-MM-DD}.log",
    rotation="500 MB",
    retention="10 days",
    level="ERROR",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} - {message}"
)

def get_logger(name: str = None):
    """
    获取logger实例
    
    Args:
        name (str): logger名称
        
    Returns:
        loguru.logger: loguru logger实例
    """
    return loguru_logger




def setup_logging():
    """设置日志配置"""
    # 确保日志目录存在
    log_dir = settings.LOG_DIR
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # 配置loguru日志
    loguru_logger.add(
        log_dir / "app_{time:YYYY-MM-DD}.log",
        rotation="500 MB",
        retention="10 days",
        level="INFO",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} - {message}"
    )
    
    loguru_logger.add(
        log_dir / "error_{time:YYYY-MM-DD}.log",
        rotation="500 MB",
        retention="10 days",
        level="ERROR",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} - {message}"
    )
    
    loguru_logger.info("日志系统初始化完成")