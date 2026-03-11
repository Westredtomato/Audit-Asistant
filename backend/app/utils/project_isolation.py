"""
项目数据隔离工具
"""

from pathlib import Path
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from business.system_config_service import settings, get_project_data_dir, get_upload_dir
from app.models.project import Project
from app.models.user import User


class ProjectIsolationManager:
    """项目数据隔离管理器"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_user_projects(self, user_id: int) -> List[Project]:
        """获取用户可访问的项目列表"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return []
        
        # 管理员可以访问所有项目
        if user.role == "admin":
            return self.db.query(Project).filter(Project.status == "active").all()
        
        # 普通用户只能访问自己创建的项目
        return self.db.query(Project).filter(
            and_(
                Project.creator_id == user_id,
                Project.status == "active"
            )
        ).all()
    
    def can_user_access_project(self, user_id: int, project_id: str) -> bool:
        """检查用户是否可以访问指定项目"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return False
        
        # 管理员可以访问所有项目
        if user.role == "admin":
            project = self.db.query(Project).filter(
                and_(
                    Project.project_id == project_id,
                    Project.status == "active"
                )
            ).first()
            return project is not None
        
        # 普通用户只能访问自己创建的项目
        project = self.db.query(Project).filter(
            and_(
                Project.project_id == project_id,
                Project.creator_id == user_id,
                Project.status == "active"
            )
        ).first()
        return project is not None
    
    def get_project_data_path(self, project_id: str) -> Path:
        """获取项目数据存储路径"""
        return get_project_data_dir(project_id)
    
    def get_project_upload_path(self, project_id: str) -> Path:
        """获取项目上传文件路径"""
        return get_upload_dir(project_id)
    
    def create_project_directories(self, project_id: str):
        """创建项目相关目录"""
        # 创建主数据目录
        data_dir = self.get_project_data_path(project_id)
        data_dir.mkdir(parents=True, exist_ok=True)
        
        # 创建上传目录
        upload_dir = self.get_project_upload_path(project_id)
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        # 创建其他子目录
        subdirs = [
            "drafts",      # 底稿文件
            "events",      # 重大事项文件
            "templates",   # 用户自定义模板
            "exports",     # 导出文件
            "logs",        # 项目日志
            "temp"         # 临时文件
        ]
        
        for subdir in subdirs:
            (data_dir / subdir).mkdir(exist_ok=True)
    
    def archive_project(self, project_id: str) -> bool:
        """归档项目（移动到归档目录）"""
        try:
            project_dir = self.get_project_data_path(project_id)
            if not project_dir.exists():
                return True  # 目录不存在，认为已归档
            
            # 创建归档目录
            archive_dir = settings.DATA_DIR / "archived_projects"
            archive_dir.mkdir(exist_ok=True)
            
            # 移动项目目录到归档目录
            archive_path = archive_dir / project_id
            if archive_path.exists():
                # 如果已存在，添加时间戳
                from datetime import datetime
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                archive_path = archive_dir / f"{project_id}_{timestamp}"
            
            project_dir.rename(archive_path)
            return True
            
        except Exception as e:
            print(f"项目归档失败: {str(e)}")
            return False
    
    def delete_project_data(self, project_id: str) -> bool:
        """删除项目数据（谨慎使用）"""
        try:
            project_dir = self.get_project_data_path(project_id)
            if project_dir.exists():
                import shutil
                shutil.rmtree(project_dir)
            return True
            
        except Exception as e:
            print(f"项目数据删除失败: {str(e)}")
            return False
    
    def get_project_storage_usage(self, project_id: str) -> dict:
        """获取项目存储使用情况"""
        project_dir = self.get_project_data_path(project_id)
        if not project_dir.exists():
            return {
                "total_size": 0,
                "file_count": 0,
                "subdirs": {}
            }
        
        def get_dir_size(path: Path) -> tuple:
            """获取目录大小和文件数量"""
            total_size = 0
            file_count = 0
            
            if path.is_file():
                return path.stat().st_size, 1
            
            for item in path.rglob("*"):
                if item.is_file():
                    total_size += item.stat().st_size
                    file_count += 1
            
            return total_size, file_count
        
        total_size, file_count = get_dir_size(project_dir)
        
        # 获取各子目录的使用情况
        subdirs = {}
        for subdir in project_dir.iterdir():
            if subdir.is_dir():
                size, count = get_dir_size(subdir)
                subdirs[subdir.name] = {
                    "size": size,
                    "file_count": count
                }
        
        return {
            "total_size": total_size,
            "file_count": file_count,
            "subdirs": subdirs
        }
    
    def cleanup_temp_files(self, project_id: str, older_than_hours: int = 24):
        """清理临时文件"""
        from datetime import datetime, timedelta
        
        temp_dir = self.get_project_data_path(project_id) / "temp"
        if not temp_dir.exists():
            return
        
        cutoff_time = datetime.now() - timedelta(hours=older_than_hours)
        
        for temp_file in temp_dir.rglob("*"):
            if temp_file.is_file():
                file_time = datetime.fromtimestamp(temp_file.stat().st_mtime)
                if file_time < cutoff_time:
                    try:
                        temp_file.unlink()
                    except Exception as e:
                        print(f"删除临时文件失败 {temp_file}: {str(e)}")


def create_project_context_filter(model_class, project_field="project_id"):
    """创建项目上下文过滤器装饰器"""
    def decorator(query_func):
        def wrapper(db: Session, current_user_id: int, project_id: str, *args, **kwargs):
            # 检查用户权限
            isolation_manager = ProjectIsolationManager(db)
            if not isolation_manager.can_user_access_project(current_user_id, project_id):
                raise PermissionError("无权限访问此项目")
            
            # 执行查询并添加项目过滤
            query = query_func(db, *args, **kwargs)
            if hasattr(model_class, project_field):
                # 根据project_id过滤
                project = db.query(Project).filter(Project.project_id == project_id).first()
                if project:
                    query = query.filter(getattr(model_class, project_field) == project.id)
                else:
                    # 项目不存在，返回空结果
                    query = query.filter(False)
            
            return query
        return wrapper
    return decorator
