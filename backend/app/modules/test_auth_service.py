import unittest
from unittest.mock import patch, MagicMock
import sys
import os
from datetime import timedelta

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from app.modules.auth_service import AuthService
from app.schemas.auth import UserCreate
from app.models.user import User

class TestAuthService(unittest.TestCase):
    """测试认证服务类"""

    def setUp(self):
        """测试前准备"""
        self.auth_service = AuthService()
        
    def test_verify_password(self):
        """测试密码验证功能"""
        plain_password = "20232027"
        hashed_password = self.auth_service.get_password_hash(plain_password)
        self.assertTrue(self.auth_service.verify_password(plain_password, hashed_password))
        self.assertFalse(self.auth_service.verify_password("wrong_password", hashed_password))
    
    def test_get_password_hash(self):
        """测试密码哈希生成"""
        password = "20232027"
        hashed1 = self.auth_service.get_password_hash(password)
        hashed2 = self.auth_service.get_password_hash(password)
        # 同一个密码的哈希值应该不同（因为有盐值）
        self.assertNotEqual(hashed1, hashed2)
        # 但验证应该通过
        self.assertTrue(self.auth_service.verify_password(password, hashed1))
    
    @patch('app.modules.auth_service.Session')
    def test_get_user_by_username(self, mock_session):
        """测试根据用户名获取用户"""
        mock_db = MagicMock()
        mock_user = User(username="cpa_001")
        mock_db.query().filter().first.return_value = mock_user
        
        result = self.auth_service.get_user_by_username(mock_db, "cpa_001")
        self.assertEqual(result, mock_user)
    
    @patch('app.modules.auth_service.Session')
    def test_get_user_by_email(self, mock_session):
        """测试根据邮箱获取用户"""
        mock_db = MagicMock()
        mock_user = User(email="cpa_001@example.com")
        mock_db.query().filter().first.return_value = mock_user
        
        result = self.auth_service.get_user_by_email(mock_db, "cpa_001@example.com")
        self.assertEqual(result, mock_user)
    
    @patch('app.modules.auth_service.Session')
    def test_authenticate_user_success(self, mock_session):
        """测试用户认证成功"""
        mock_db = MagicMock()
        password = "20232027"
        hashed_password = self.auth_service.get_password_hash(password)
        mock_user = User(username="cpa_001", password_hash=hashed_password)
        
        mock_db.query().filter().first.return_value = mock_user
        
        result = self.auth_service.authenticate_user(mock_db, "cpa_001", password)
        self.assertEqual(result, mock_user)
    
    @patch('app.modules.auth_service.Session')
    def test_authenticate_user_wrong_password(self, mock_session):
        """测试用户认证失败 - 错误密码"""
        mock_db = MagicMock()
        password = "20232027"
        hashed_password = self.auth_service.get_password_hash("different_password")
        mock_user = User(username="cpa_001", password_hash=hashed_password)
        
        mock_db.query().filter().first.return_value = mock_user
        
        result = self.auth_service.authenticate_user(mock_db, "cpa_001", password)
        self.assertIsNone(result)
    
    @patch('app.modules.auth_service.Session')
    def test_authenticate_user_not_found(self, mock_session):
        """测试用户认证失败 - 用户不存在"""
        mock_db = MagicMock()
        mock_db.query().filter().first.return_value = None
        
        result = self.auth_service.authenticate_user(mock_db, "cpa_001", "20232027")
        self.assertIsNone(result)
    
    @patch('app.modules.auth_service.Session')
    def test_create_user(self, mock_session):
        """测试创建用户"""
        mock_db = MagicMock()
        user_data = UserCreate(
            username="cpa_001",
            password="20232027",
            display_name="cpa_001"
        )
        
        mock_db.add = MagicMock()
        mock_db.commit = MagicMock()
        mock_db.refresh = MagicMock()
        
        result = self.auth_service.create_user(mock_db, user_data)
        self.assertIsInstance(result, User)
        self.assertEqual(result.username, "cpa_001")
        self.assertEqual(result.display_name, "cpa_001")
        self.assertTrue(result.password_hash)  # 确保密码已哈希
        
        # 验证调用了数据库操作
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()
    
    def test_create_access_token(self):
        """测试创建访问令牌"""
        from business.system_config_service import settings
        data = {"sub": "cpa_001"}
        token = self.auth_service.create_access_token(data)
        self.assertIsInstance(token, str)
        self.assertTrue(len(token) > 0)
    
    def test_create_access_token_with_expires(self):
        """测试创建带过期时间的访问令牌"""
        data = {"sub": "cpa_001"}
        expires_delta = timedelta(minutes=30)
        token = self.auth_service.create_access_token(data, expires_delta)
        self.assertIsInstance(token, str)
        self.assertTrue(len(token) > 0)

if __name__ == '__main__':
    unittest.main()