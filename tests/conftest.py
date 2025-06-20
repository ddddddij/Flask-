import pytest
import requests
import json
import os
from dotenv import load_dotenv

# 加载测试环境变量
load_dotenv(".env.test")


@pytest.fixture(scope="session")
def base_url():
    return os.getenv("TEST_BASE_URL", "http://localhost:5001")


@pytest.fixture(scope="session")
def auth_token(base_url):
    """获取有效的 JWT Token"""
    with open("tests/test_data/test_users.json") as f:
        user_data = json.load(f)["valid_user"]

    response = requests.post(
        f"{base_url}/login",
        json={"username": user_data["username"], "password": user_data["password"]}
    )
    assert response.status_code == 200
    return response.json()["token"]