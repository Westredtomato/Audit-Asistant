import subprocess
import sys
import os
import time
import redis
import platform
import shutil
try:
    from system_config_service import settings
except:
    from business.system_config_service import settings
from urllib.parse import urlparse


def is_redis_running(redis_url: str) -> bool:
    """
    检查Redis服务是否正在运行
    
    Args:
        redis_url: Redis连接URL
        
    Returns:
        bool: 如果Redis正在运行返回True，否则返回False
    """
    try:
        parsed_url = urlparse(redis_url)
        client = redis.Redis(
            host=parsed_url.hostname or 'localhost',
            port=parsed_url.port or 6379,
            db=0,
            decode_responses=True
        )
        client.ping()
        return True
    except redis.ConnectionError:
        return False
    except Exception:
        return False


def is_wsl() -> bool:
    """
    检查是否在WSL环境中运行
    
    Returns:
        bool: 如果在WSL环境中返回True，否则返回False
    """
    try:
        if os.path.exists('/proc/version'):
            with open('/proc/version', 'r') as f:
                content = f.read().lower()
                return 'microsoft' in content
    except Exception:
        pass
    return False


def start_redis_windows(redis_url: str) -> bool:
    """
    在Windows系统上启动Redis服务
    
    Args:
        redis_url: Redis连接URL
        
    Returns:
        bool: 启动成功返回True，否则返回False
    """
    parsed_url = urlparse(redis_url)
    port = parsed_url.port or 6379
    
    # 方法1: 尝试作为Windows服务启动
    try:
        result = subprocess.run(['net', 'start', 'redis'], 
                              capture_output=True, text=True)
        if result.returncode == 0 or "already" in result.stdout.lower():
            print("Redis服务已作为Windows服务启动")
            return True
    except FileNotFoundError:
        pass  # net命令不可用
    
    # 方法2: 尝试直接运行redis-server
    redis_server_path = shutil.which('redis-server')
    if redis_server_path:
        try:
            # 尝试使用默认配置启动
            conf_path = 'redis.windows.conf'
            if os.path.exists(conf_path):
                subprocess.Popen([redis_server_path, conf_path], 
                               stdout=subprocess.DEVNULL, 
                               stderr=subprocess.DEVNULL)
            else:
                # 不使用配置文件启动
                subprocess.Popen([redis_server_path, '--port', str(port)], 
                               stdout=subprocess.DEVNULL, 
                               stderr=subprocess.DEVNULL)
            time.sleep(2)  # 等待服务启动
            return True
        except Exception as e:
            print(f"使用redis-server启动失败: {e}")
    
    # 方法3: 尝试启动WSL中的Redis服务
    if start_redis_wsl(redis_url):
        return True
    
    return False


def start_redis_wsl(redis_url: str) -> bool:
    """
    在WSL环境下启动Redis服务
    
    Args:
        redis_url: Redis连接URL
        
    Returns:
        bool: 启动成功返回True，否则返回False
    """
    # 检查是否在WSL环境中
    if is_wsl():
        # 在WSL内部直接启动Redis
        return start_redis_wsl_internal(redis_url)
    else:
        # 在Windows上通过wsl命令启动WSL中的Redis
        return start_redis_wsl_external(redis_url)


def start_redis_wsl_internal(redis_url: str) -> bool:
    """
    在WSL内部启动Redis服务
    
    Args:
        redis_url: Redis连接URL
        
    Returns:
        bool: 启动成功返回True，否则返回False
    """
    parsed_url = urlparse(redis_url)
    port = parsed_url.port or 6379
    
    # WSL中尝试使用service命令启动Redis
    try:
        # Ubuntu/Debian系列
        result = subprocess.run(['sudo', 'service', 'redis-server', 'start'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("Redis服务已在WSL中通过service命令启动")
            time.sleep(2)  # 等待服务启动
            return True
    except Exception as e:
        print(f"通过service命令启动Redis失败: {e}")
    
    try:
        # CentOS/RHEL系列
        result = subprocess.run(['sudo', 'service', 'redis', 'start'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("Redis服务已在WSL中通过service命令启动")
            time.sleep(2)  # 等待服务启动
            return True
    except Exception as e:
        print(f"通过service命令启动Redis失败: {e}")
    
    # 尝试直接运行redis-server
    redis_server_path = shutil.which('redis-server')
    if redis_server_path:
        try:
            # 查找配置文件
            conf_paths = [
                '/etc/redis/redis.conf',
                '/etc/redis/redis-server.conf',
                '/usr/local/etc/redis.conf'
            ]
            
            conf_path = None
            for path in conf_paths:
                if os.path.exists(path):
                    conf_path = path
                    break
            
            if conf_path:
                subprocess.Popen(['sudo', redis_server_path, conf_path], 
                               stdout=subprocess.DEVNULL, 
                               stderr=subprocess.DEVNULL)
            else:
                # 不使用配置文件启动
                subprocess.Popen(['sudo', redis_server_path, '--port', str(port)], 
                               stdout=subprocess.DEVNULL, 
                               stderr=subprocess.DEVNULL)
            
            time.sleep(2)  # 等待服务启动
            return True
        except Exception as e:
            print(f"在WSL中使用redis-server启动失败: {e}")
    
    return False


def start_redis_wsl_external(redis_url: str) -> bool:
    """
    在Windows上通过wsl命令启动WSL中的Redis服务
    
    Args:
        redis_url: Redis连接URL
        
    Returns:
        bool: 启动成功返回True，否则返回False
    """
    try:
        # 直接在WSL中运行redis-server
        result = subprocess.run(['wsl', 'redis-server', '--daemonize', 'yes'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("Redis服务已在WSL中通过Windows上的wsl命令启动")
            time.sleep(2)  # 等待服务启动
            return True                   
    except Exception as e:
        print(f"通过wsl命令启动Redis失败: {e}")
    
    try:
        # 尝试另一种服务名称
        result = subprocess.run(['wsl', 'sudo', 'service', 'redis', 'start'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("Redis服务已在WSL中通过Windows上的wsl命令启动")
            time.sleep(2)  # 等待服务启动
            return True
    except Exception as e:
        print(f"通过wsl命令启动Redis失败: {e}")
    
    try:
        # 尝试通过wsl命令在WSL中启动Redis服务
        result = subprocess.run(['wsl', 'sudo', 'service', 'redis-server', 'start'], 
                              shell=True, capture_output=True, text=True,timeout=5)
        if result.returncode == 0:
            print("Redis服务已在WSL中通过Windows上的wsl命令启动")
            time.sleep(2)  # 等待服务启动
            return True       
    except Exception as e:
        print(f"通过wsl命令启动Redis失败: {e}")
    
    return False


def start_redis_unix(redis_url: str) -> bool:
    """
    在Unix-like系统（Linux/macOS）上启动Redis服务
    
    Args:
        redis_url: Redis连接URL
        
    Returns:
        bool: 启动成功返回True，否则返回False
    """
    # 方法1: systemd (Linux)
    try:
        result = subprocess.run(['systemctl', 'is-active', 'redis'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("Redis服务已通过systemctl运行")
            return True
    except FileNotFoundError:
        pass  # systemctl不可用
    
    try:
        result = subprocess.run(['systemctl', 'is-active', 'redis-server'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("Redis服务已通过systemctl运行")
            return True
    except FileNotFoundError:
        pass  # systemctl不可用
    
    # 方法2: service命令 (Linux)
    try:
        subprocess.run(['service', 'redis', 'start'], 
                      capture_output=True)
        print("Redis服务已通过service命令启动")
        return True
    except FileNotFoundError:
        pass  # service命令不可用
    
    try:
        subprocess.run(['service', 'redis-server', 'start'], 
                      capture_output=True)
        print("Redis服务已通过service命令启动")
        return True
    except FileNotFoundError:
        pass  # service命令不可用
    
    # 方法3: 直接运行redis-server (通用)
    redis_server_path = shutil.which('redis-server')
    if redis_server_path:
        try:
            parsed_url = urlparse(redis_url)
            port = parsed_url.port or 6379
            
            # 尝试使用默认配置启动
            conf_paths = [
                '/etc/redis/redis.conf',
                '/usr/local/etc/redis.conf',
                'redis.conf'
            ]
            
            conf_path = None
            for path in conf_paths:
                if os.path.exists(path):
                    conf_path = path
                    break
            
            # 特别处理WSL环境
            if not conf_path and os.path.exists('/etc/redis/redis-server.conf'):
                conf_path = '/etc/redis/redis-server.conf'
            
            if conf_path:
                subprocess.Popen([redis_server_path, conf_path], 
                               stdout=subprocess.DEVNULL, 
                               stderr=subprocess.DEVNULL)
            else:
                # 不使用配置文件启动
                subprocess.Popen([redis_server_path, '--port', str(port)], 
                               stdout=subprocess.DEVNULL, 
                               stderr=subprocess.DEVNULL)
            
            time.sleep(2)  # 等待服务启动
            return True
        except Exception as e:
            print(f"使用redis-server启动失败: {e}")
    
    return False


def start_redis_service(redis_url: str) -> bool:
    """
    根据操作系统类型启动Redis服务
    
    Args:
        redis_url: Redis连接URL
        
    Returns:
        bool: 启动成功返回True，否则返回False
    """
    system = platform.system().lower()
    
    if system == 'windows':
        # 首先尝试WSL特定的启动方法
        if start_redis_wsl(redis_url):
            return True
        return start_redis_windows(redis_url)
    elif system in ['linux', 'darwin']:  # Linux or macOS
        return start_redis_unix(redis_url)
    else:
        print(f"不支持的操作系统: {system}")
        return False


def init_redis_service():
    """主函数"""
    redis_url = settings.REDIS_URL
    print(f"尝试启动Redis服务: {redis_url}")
    
    # 首先检查Redis是否已经在运行
    if is_redis_running(redis_url):
        print("Redis服务已在运行")
        return True
    
    # 尝试启动Redis服务
    if start_redis_service(redis_url):
        # 等待一段时间让服务启动
        time.sleep(3)
        
        # 再次检查Redis是否运行
        if is_redis_running(redis_url):
            print("Redis服务启动成功")
            return True
        else:
            print("Redis服务启动失败或启动时间过长")
            return False
    else:
        print("无法启动Redis服务，请手动启动Redis或检查安装")
        return False


if __name__ == '__main__':
    init_redis_service()