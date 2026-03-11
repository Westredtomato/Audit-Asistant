"""
文件管理工具
"""

import hashlib
import mimetypes
import os
import uuid
from pathlib import Path
from typing import Optional, List, Dict, Any
import shutil
from datetime import datetime

from business.system_config_service import settings


class FileManager:
    """文件管理器"""
    
    # 支持的文件类型
    SUPPORTED_EXTENSIONS = {
        '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        '.xls': 'application/vnd.ms-excel',
        '.pdf': 'application/pdf',
        '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        '.doc': 'application/msword',
        '.txt': 'text/plain',
        '.csv': 'text/csv'
    }
    
    def __init__(self, project_id: str = None):
        self.project_id = project_id
    
    def get_upload_path(self, filename: str) -> Path:
        """获取文件上传路径"""
        if self.project_id:
            base_dir = settings.DATA_DIR / "projects" / self.project_id / "uploads"
        else:
            base_dir = settings.UPLOAD_DIR
        
        base_dir.mkdir(parents=True, exist_ok=True)
        
        # 按日期组织文件
        date_dir = base_dir / datetime.now().strftime("%Y%m%d")
        date_dir.mkdir(exist_ok=True)
        
        return date_dir / filename
    
    def generate_unique_filename(self, original_filename: str) -> str:
        """生成唯一文件名"""
        name, ext = os.path.splitext(original_filename)
        unique_id = str(uuid.uuid4())[:8]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{name}_{timestamp}_{unique_id}{ext}"
    
    def validate_file(self, filename: str, file_size: int) -> Dict[str, Any]:
        """验证文件"""
        result = {
            "valid": False,
            "error": None,
            "file_type": None,
            "mime_type": None
        }
        
        # 检查文件扩展名
        ext = Path(filename).suffix.lower()
        if ext not in self.SUPPORTED_EXTENSIONS:
            result["error"] = f"不支持的文件类型: {ext}"
            return result
        
        # 检查文件大小
        if file_size > settings.MAX_UPLOAD_SIZE:
            max_size_mb = settings.MAX_UPLOAD_SIZE / (1024 * 1024)
            result["error"] = f"文件大小超过限制 ({max_size_mb}MB)"
            return result
        
        result.update({
            "valid": True,
            "file_type": ext,
            "mime_type": self.SUPPORTED_EXTENSIONS[ext]
        })
        
        return result
    
    def calculate_file_hash(self, file_path: Path) -> str:
        """计算文件哈希值"""
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    
    def save_uploaded_file(self, file_content: bytes, filename: str) -> Dict[str, Any]:
        """保存上传的文件"""
        # 验证文件
        validation = self.validate_file(filename, len(file_content))
        if not validation["valid"]:
            return {
                "success": False,
                "error": validation["error"]
            }
        
        try:
            # 生成唯一文件名
            unique_filename = self.generate_unique_filename(filename)
            file_path = self.get_upload_path(unique_filename)
            
            # 保存文件
            with open(file_path, "wb") as f:
                f.write(file_content)
            
            # 计算文件哈希
            file_hash = self.calculate_file_hash(file_path)
            
            return {
                "success": True,
                "file_path": str(file_path),
                "original_filename": filename,
                "saved_filename": unique_filename,
                "file_size": len(file_content),
                "file_hash": file_hash,
                "mime_type": validation["mime_type"]
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"文件保存失败: {str(e)}"
            }
    
    def delete_file(self, file_path: str) -> bool:
        """删除文件"""
        try:
            path = Path(file_path)
            if path.exists():
                path.unlink()
            return True
        except Exception as e:
            print(f"删除文件失败 {file_path}: {str(e)}")
            return False
    
    def move_file(self, src_path: str, dst_path: str) -> bool:
        """移动文件"""
        try:
            src = Path(src_path)
            dst = Path(dst_path)
            
            # 确保目标目录存在
            dst.parent.mkdir(parents=True, exist_ok=True)
            
            shutil.move(str(src), str(dst))
            return True
            
        except Exception as e:
            print(f"移动文件失败 {src_path} -> {dst_path}: {str(e)}")
            return False
    
    def copy_file(self, src_path: str, dst_path: str) -> bool:
        """复制文件"""
        try:
            src = Path(src_path)
            dst = Path(dst_path)
            
            # 确保目标目录存在
            dst.parent.mkdir(parents=True, exist_ok=True)
            
            shutil.copy2(str(src), str(dst))
            return True
            
        except Exception as e:
            print(f"复制文件失败 {src_path} -> {dst_path}: {str(e)}")
            return False
    
    def create_backup(self, file_path: str) -> Optional[str]:
        """创建文件备份"""
        try:
            src = Path(file_path)
            if not src.exists():
                return None
            
            # 生成备份文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"{src.stem}_backup_{timestamp}{src.suffix}"
            backup_path = src.parent / "backups" / backup_name
            
            # 创建备份目录
            backup_path.parent.mkdir(exist_ok=True)
            
            # 复制文件
            shutil.copy2(str(src), str(backup_path))
            return str(backup_path)
            
        except Exception as e:
            print(f"创建备份失败 {file_path}: {str(e)}")
            return None
    
    def cleanup_old_files(self, directory: str, days: int = 30):
        """清理旧文件"""
        try:
            dir_path = Path(directory)
            if not dir_path.exists():
                return
            
            cutoff_date = datetime.now().timestamp() - (days * 24 * 60 * 60)
            
            for file_path in dir_path.rglob("*"):
                if file_path.is_file() and file_path.stat().st_mtime < cutoff_date:
                    try:
                        file_path.unlink()
                    except Exception as e:
                        print(f"删除旧文件失败 {file_path}: {str(e)}")
                        
        except Exception as e:
            print(f"清理旧文件失败 {directory}: {str(e)}")
    
    def get_file_info(self, file_path: str) -> Dict[str, Any]:
        """获取文件信息"""
        try:
            path = Path(file_path)
            if not path.exists():
                return {"exists": False}
            
            stat = path.stat()
            
            return {
                "exists": True,
                "size": stat.st_size,
                "created_time": datetime.fromtimestamp(stat.st_ctime),
                "modified_time": datetime.fromtimestamp(stat.st_mtime),
                "mime_type": mimetypes.guess_type(str(path))[0],
                "extension": path.suffix.lower()
            }
            
        except Exception as e:
            return {
                "exists": False,
                "error": str(e)
            }
    
    def scan_directory(self, directory: str, pattern: str = "*") -> List[Dict[str, Any]]:
        """扫描目录中的文件"""
        try:
            dir_path = Path(directory)
            if not dir_path.exists():
                return []
            
            files = []
            for file_path in dir_path.glob(pattern):
                if file_path.is_file():
                    file_info = self.get_file_info(str(file_path))
                    file_info["name"] = file_path.name
                    file_info["path"] = str(file_path)
                    files.append(file_info)
            
            return files
            
        except Exception as e:
            print(f"扫描目录失败 {directory}: {str(e)}")
            return []
    
    @staticmethod
    def format_file_size(size_bytes: int) -> str:
        """格式化文件大小"""
        if size_bytes == 0:
            return "0B"
        
        size_names = ["B", "KB", "MB", "GB", "TB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
        
        return f"{size_bytes:.2f}{size_names[i]}"
