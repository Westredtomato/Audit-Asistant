"""
数据库管理工具
"""

import asyncio
import sys
import os
import argparse
from pathlib import Path
import shutil

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from sqlalchemy import text
from loguru import logger

from app.database_manager.database import engine, SessionLocal, Base, init_database
from app.models import *  # 导入所有模型
from business.system_config_service import settings


class DatabaseManager:
    """数据库管理器"""
    
    def __init__(self):
        self.db_path = settings.DATA_DIR / "cpa_assistant.db"
    
    def backup_database(self, backup_path: str = None):
        """备份数据库"""
        if not backup_path:
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = f"backup_cpa_assistant_{timestamp}.db"
        
        if self.db_path.exists():
            shutil.copy2(self.db_path, backup_path)
            logger.info(f"数据库已备份到: {backup_path}")
        else:
            logger.warning("数据库文件不存在，无法备份")
    
    def restore_database(self, backup_path: str):
        """从备份恢复数据库"""
        backup_file = Path(backup_path)
        if not backup_file.exists():
            logger.error(f"备份文件不存在: {backup_path}")
            return False
        
        # 备份当前数据库
        if self.db_path.exists():
            self.backup_database("before_restore.db")
        
        # 恢复备份
        shutil.copy2(backup_file, self.db_path)
        logger.info(f"数据库已从 {backup_path} 恢复")
        return True
    
    def reset_database(self):
        """重置数据库"""
        logger.warning("即将重置数据库，所有数据将被清除！")
        
        # 备份当前数据库
        self.backup_database("before_reset.db")
        
        # 删除所有表
        Base.metadata.drop_all(bind=engine)
        logger.info("所有数据表已删除")
        
        # 重新创建表
        Base.metadata.create_all(bind=engine)
        logger.info("数据表已重新创建")
    
    def show_database_info(self):
        """显示数据库信息"""
        logger.info(f"数据库路径: {self.db_path}")
        logger.info(f"数据库大小: {self.get_database_size()}")
        
        try:
            with engine.connect() as conn:
                # 获取表信息
                if "sqlite" in settings.DATABASE_URL.lower():
                    result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"))
                    tables = [row[0] for row in result]
                    
                    logger.info(f"表数量: {len(tables)}")
                    logger.info(f"表列表: {', '.join(tables)}")
                    
                    # 获取每个表的记录数
                    for table in tables:
                        if not table.startswith('sqlite_'):
                            count_result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                            count = count_result.scalar()
                            logger.info(f"  {table}: {count} 条记录")
                            
        except Exception as e:
            logger.error(f"获取数据库信息失败: {str(e)}")
    
    def get_database_size(self) -> str:
        """获取数据库文件大小"""
        if self.db_path.exists():
            size = self.db_path.stat().st_size
            if size < 1024:
                return f"{size} B"
            elif size < 1024 * 1024:
                return f"{size / 1024:.2f} KB"
            elif size < 1024 * 1024 * 1024:
                return f"{size / (1024 * 1024):.2f} MB"
            else:
                return f"{size / (1024 * 1024 * 1024):.2f} GB"
        return "文件不存在"
    
    def vacuum_database(self):
        """清理数据库（SQLite VACUUM）"""
        try:
            with engine.connect() as conn:
                conn.execute(text("VACUUM"))
                logger.info("数据库清理完成")
        except Exception as e:
            logger.error(f"数据库清理失败: {str(e)}")
    
    def analyze_database(self):
        """分析数据库统计信息"""
        try:
            with engine.connect() as conn:
                conn.execute(text("ANALYZE"))
                logger.info("数据库统计信息更新完成")
        except Exception as e:
            logger.error(f"数据库分析失败: {str(e)}")
    
    def check_database_integrity(self):
        """检查数据库完整性"""
        try:
            with engine.connect() as conn:
                result = conn.execute(text("PRAGMA integrity_check"))
                integrity_result = result.fetchall()
                
                if len(integrity_result) == 1 and integrity_result[0][0] == 'ok':
                    logger.info("✅ 数据库完整性检查通过")
                else:
                    logger.warning("⚠️ 数据库完整性检查发现问题:")
                    for row in integrity_result:
                        logger.warning(f"  {row[0]}")
                        
        except Exception as e:
            logger.error(f"数据库完整性检查失败: {str(e)}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="注会帮数据库管理工具")
    parser.add_argument("command", choices=[
        "info", "backup", "restore", "reset", "vacuum", "analyze", "check"
    ], help="管理命令")
    parser.add_argument("--backup-path", help="备份文件路径")
    parser.add_argument("--restore-path", help="恢复文件路径")
    parser.add_argument("--force", action="store_true", help="强制执行（跳过确认）")
    
    args = parser.parse_args()
    
    db_manager = DatabaseManager()
    
    if args.command == "info":
        db_manager.show_database_info()
    
    elif args.command == "backup":
        db_manager.backup_database(args.backup_path)
    
    elif args.command == "restore":
        if not args.restore_path:
            logger.error("请指定恢复文件路径: --restore-path")
            sys.exit(1)
        
        if not args.force:
            confirm = input("确认要恢复数据库吗？当前数据将被覆盖 (y/N): ")
            if confirm.lower() != 'y':
                logger.info("操作已取消")
                return
        
        db_manager.restore_database(args.restore_path)
    
    elif args.command == "reset":
        if not args.force:
            confirm = input("确认要重置数据库吗？所有数据将被清除 (y/N): ")
            if confirm.lower() != 'y':
                logger.info("操作已取消")
                return
        
        db_manager.reset_database()
    
    elif args.command == "vacuum":
        db_manager.vacuum_database()
    
    elif args.command == "analyze":
        db_manager.analyze_database()
    
    elif args.command == "check":
        db_manager.check_database_integrity()


if __name__ == "__main__":
    main()
