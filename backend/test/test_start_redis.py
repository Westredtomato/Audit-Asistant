"""
Redis服务启动功能测试
"""
import unittest
from unittest.mock import patch, MagicMock, mock_open
import sys
import os
import subprocess

from pathlib import Path
# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))



from business.start_redis import (
    is_redis_running, 
    is_wsl,
    start_redis_windows,
    start_redis_wsl_internal,
    start_redis_wsl_external,
    start_redis_unix,
    start_redis_wsl,
    start_redis_service,
    init_redis_service
)


class TestStartRedis(unittest.TestCase):
    
    @patch('business.start_redis.redis.Redis')
    def test_is_redis_running_true(self, mock_redis):
        """测试Redis正在运行的情况"""
        # 设置模拟对象
        mock_client = MagicMock()
        mock_redis.return_value = mock_client
        mock_client.ping.return_value = True
        
        # 执行测试
        result = is_redis_running("redis://localhost:6379")
        
        # 验证结果
        self.assertTrue(result)
        mock_redis.assert_called_once_with(
            host='localhost',
            port=6379,
            db=0,
            decode_responses=True
        )
        mock_client.ping.assert_called_once()
    
    @patch('business.start_redis.redis.Redis')
    def test_is_redis_running_false_connection_error(self, mock_redis):
        """测试Redis连接失败的情况"""
        # 设置模拟对象
        mock_client = MagicMock()
        mock_redis.return_value = mock_client
        mock_client.ping.side_effect = Exception("Connection error")
        
        # 执行测试
        result = is_redis_running("redis://localhost:6379")
        
        # 验证结果
        self.assertFalse(result)
    
    @patch('os.path.exists')
    @patch('builtins.open', new_callable=mock_open, read_data='Linux version Microsoft')
    def test_is_wsl_true(self, mock_file, mock_exists):
        """测试在WSL环境中运行的情况"""
        # 设置模拟对象
        mock_exists.return_value = True
        
        # 执行测试
        result = is_wsl()
        
        # 验证结果
        self.assertTrue(result)
        mock_exists.assert_called_once_with('/proc/version')
    
    @patch('os.path.exists')
    def test_is_wsl_false_no_proc_version(self, mock_exists):
        """测试没有/proc/version文件的情况"""
        # 设置模拟对象
        mock_exists.return_value = False
        
        # 执行测试
        result = is_wsl()
        
        # 验证结果
        self.assertFalse(result)
        mock_exists.assert_called_once_with('/proc/version')
    
    @patch('business.start_redis.start_redis_wsl')
    @patch('shutil.which')
    @patch('subprocess.run')
    def test_start_redis_windows_with_service(self, mock_run, mock_which, mock_wsl):
        """测试Windows环境下通过服务启动Redis"""
        # 设置模拟对象
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_run.return_value = mock_result
        mock_which.return_value = None  # redis-server不可用
        mock_wsl.return_value = False   # WSL启动失败
        
        # 执行测试
        result = start_redis_windows("redis://localhost:6379")
        
        # 验证结果
        self.assertTrue(result)
        mock_run.assert_called_once_with(['net', 'start', 'redis'], capture_output=True, text=True)
    
    @patch('business.start_redis.start_redis_wsl')
    @patch('shutil.which')
    @patch('subprocess.Popen')
    @patch('subprocess.run')
    def test_start_redis_windows_with_redis_server(self, mock_run, mock_popen, mock_which, mock_wsl):
        """测试Windows环境下通过redis-server启动Redis"""
        # 设置模拟对象
        mock_result = MagicMock()
        mock_result.returncode = 1  # net start redis 失败
        mock_run.return_value = mock_result
        mock_which.return_value = "/path/to/redis-server.exe"
        mock_wsl.return_value = False  # WSL启动失败
        
        # 执行测试
        result = start_redis_windows("redis://localhost:6379")
        
        # 验证结果
        self.assertTrue(result)
        mock_popen.assert_called_once()
    
    @patch('business.start_redis.start_redis_wsl_internal')
    @patch('business.start_redis.is_wsl')
    def test_start_redis_wsl_internal_mode(self, mock_is_wsl, mock_internal):
        """测试在WSL内部启动Redis服务"""
        # 设置模拟对象
        mock_is_wsl.return_value = True  # 在WSL环境中
        mock_internal.return_value = True
        
        # 执行测试
        result = start_redis_wsl("redis://localhost:6379")
        
        # 验证结果
        self.assertTrue(result)
        mock_internal.assert_called_once_with("redis://localhost:6379")
    
    @patch('business.start_redis.start_redis_wsl_external')
    @patch('business.start_redis.is_wsl')
    def test_start_redis_wsl_external_mode(self, mock_is_wsl, mock_external):
        """测试在Windows上通过wsl命令启动WSL中的Redis服务"""
        # 设置模拟对象
        mock_is_wsl.return_value = False  # 不在WSL环境中
        mock_external.return_value = True
        
        # 执行测试
        result = start_redis_wsl("redis://localhost:6379")
        
        # 验证结果
        self.assertTrue(result)
        mock_external.assert_called_once_with("redis://localhost:6379")
    
    @patch('subprocess.run')
    def test_start_redis_wsl_internal_with_service(self, mock_run):
        """测试在WSL内部通过service命令启动Redis"""
        # 设置模拟对象
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_run.return_value = mock_result
        
        # 执行测试
        result = start_redis_wsl_internal("redis://localhost:6379")
        
        # 验证结果
        self.assertTrue(result)
        mock_run.assert_called_once_with(
            ['sudo', 'service', 'redis-server', 'start'], 
            capture_output=True, 
            text=True
        )
    
    @patch('subprocess.run')
    def test_start_redis_wsl_external_with_wsl_command(self, mock_run):
        """测试在Windows上通过wsl命令启动WSL中的Redis"""
        # 设置模拟对象
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_run.return_value = mock_result
        
        # 执行测试
        result = start_redis_wsl_external("redis://localhost:6379")
        
        # 验证结果
        self.assertTrue(result)
        mock_run.assert_called_once_with(
            ['wsl', 'sudo', 'service', 'redis-server', 'start'], 
            capture_output=True, 
            text=True
        )
    
    @patch('subprocess.run')
    @patch('shutil.which')
    def test_start_redis_unix_with_systemctl(self, mock_which, mock_run):
        """测试在Unix系统上通过systemctl启动Redis"""
        # 设置模拟对象
        mock_which.return_value = None  # redis-server不可用
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_run.return_value = mock_result
        
        # 执行测试
        result = start_redis_unix("redis://localhost:6379")
        
        # 验证结果
        self.assertTrue(result)
        mock_run.assert_called_once_with(
            ['systemctl', 'is-active', 'redis'], 
            capture_output=True, 
            text=True
        )
    
    @patch('platform.system')
    @patch('business.start_redis.start_redis_wsl')
    def test_start_redis_service_linux_with_wsl(self, mock_wsl, mock_system):
        """测试在Linux系统上优先尝试WSL启动方式"""
        # 设置模拟对象
        mock_system.return_value = 'linux'
        mock_wsl.return_value = True
        
        # 执行测试
        result = start_redis_service("redis://localhost:6379")
        
        # 验证结果
        self.assertTrue(result)
        mock_wsl.assert_called_once_with("redis://localhost:6379")
    
    @patch('platform.system')
    @patch('business.start_redis.start_redis_windows')
    def test_start_redis_service_windows(self, mock_windows, mock_system):
        """测试在Windows系统上启动Redis服务"""
        # 设置模拟对象
        mock_system.return_value = 'windows'
        mock_windows.return_value = True
        
        # 执行测试
        result = start_redis_service("redis://localhost:6379")
        
        # 验证结果
        self.assertTrue(result)
        mock_windows.assert_called_once_with("redis://localhost:6379")


if __name__ == '__main__':
    unittest.main()