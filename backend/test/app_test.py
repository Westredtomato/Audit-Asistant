import json
import sys
import os
from pathlib import Path
# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.application import create_app

TEST_USERNAME = "cpa_001"
TEST_PASSWORD = "20232027"
RESPONSE_FILE = "response.json"


the_app = create_app()


# 解决FastAPI和HTTPX版本兼容性问题
client = TestClient(the_app, base_url="http://testserver")


def test_auth():
    response = client.post("/api/v1/auth/login", 
                        data={"username": TEST_USERNAME, "password": TEST_PASSWORD})
    assert response.status_code == 200
    response_json = response.json()
    with open(RESPONSE_FILE, "w", encoding="utf-8") as f:
        json.dump(response_json, f, indent=2, ensure_ascii=False)
    print("登录成功，响应已保存到response.json文件中")

    # 尝试登出，但如果Redis不可用则跳过
    access_token = response_json["access_token"]
    response = client.post("/api/v1/auth/logout", 
                        headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 200
    assert response.json() == {"message": "登出成功"}
    print("登出成功")


if __name__ == "__main__":
    test_auth()