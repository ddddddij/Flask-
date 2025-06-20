import os
import json
import requests
import allure
import pytest


@allure.feature("用户登录模块")
class TestLoginAPI:
    """用户登录接口测试套件"""

    @allure.story("成功登录")
    @allure.title("测试有效用户登录")
    def test_login_success(self, base_url):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        data_path = os.path.join(current_dir, "test_data", "test_users.json")

        with open(data_path, "r", encoding="utf-8") as f:
            users = json.load(f)

        # 使用有效测试用户
        user = users["valid_user"]
        username = user["username"]
        password = user["password"]

        payload = {"username": username, "password": password}

        with allure.step(f"使用有效用户 {username} 登录"):
            response = requests.post(f"{base_url}/login", json=payload)

        with allure.step("验证响应"):
            assert response.status_code == 200
            resp_json = response.json()
            assert "token" in resp_json
            assert "expires_in" in resp_json
            allure.attach(
                json.dumps(resp_json, indent=2, ensure_ascii=False),
                name="登录响应",
                attachment_type=allure.attachment_type.JSON
            )

    @allure.story("失败登录")
    @allure.title("测试无效密码登录")
    def test_login_wrong_password(self, base_url):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        data_path = os.path.join(current_dir, "test_data", "test_users.json")

        with open(data_path, "r", encoding="utf-8") as f:
            users = json.load(f)

        # 使用有效用户但错误密码
        user = users["valid_user"]
        username = user["username"]
        password = "wrong_password"

        payload = {"username": username, "password": password}

        with allure.step(f"使用错误密码尝试登录用户 {username}"):
            response = requests.post(f"{base_url}/login", json=payload)

        with allure.step("验证响应"):
            assert response.status_code == 401
            resp_json = response.json()
            assert "message" in resp_json
            assert "用户名或密码错误" in resp_json["message"]
            allure.attach(
                json.dumps(resp_json, indent=2, ensure_ascii=False),
                name="登录失败响应",
                attachment_type=allure.attachment_type.JSON
            )

    @allure.story("失败登录")
    @allure.title("测试不存在的用户登录")
    def test_login_nonexistent_user(self, base_url):
        payload = {
            "username": "nonexistent_user_123",
            "password": "any_password"
        }

        with allure.step("尝试登录不存在的用户"):
            response = requests.post(f"{base_url}/login", json=payload)

        with allure.step("验证响应"):
            assert response.status_code == 401
            resp_json = response.json()
            assert "message" in resp_json
            assert "用户名或密码错误" in resp_json["message"]
            allure.attach(
                json.dumps(resp_json, indent=2, ensure_ascii=False),
                name="登录失败响应",
                attachment_type=allure.attachment_type.JSON
            )

    @allure.story("参数验证")
    @allure.title("测试空用户名登录")
    def test_login_empty_username(self, base_url):
        payload = {"username": "", "password": "Test1234"}

        with allure.step("发送空用户名的登录请求"):
            response = requests.post(f"{base_url}/login", json=payload)

        with allure.step("验证响应"):
            assert response.status_code == 400
            resp_json = response.json()
            assert "message" in resp_json
            assert "用户名和密码不能为空" in resp_json["message"]
            allure.attach(
                json.dumps(resp_json, indent=2, ensure_ascii=False),
                name="参数验证响应",
                attachment_type=allure.attachment_type.JSON
            )

    @allure.story("参数验证")
    @allure.title("测试空密码登录")
    def test_login_empty_password(self, base_url):
        payload = {"username": "test_user", "password": ""}

        with allure.step("发送空密码的登录请求"):
            response = requests.post(f"{base_url}/login", json=payload)

        with allure.step("验证响应"):
            assert response.status_code == 400
            resp_json = response.json()
            assert "message" in resp_json
            assert "用户名和密码不能为空" in resp_json["message"]
            allure.attach(
                json.dumps(resp_json, indent=2, ensure_ascii=False),
                name="参数验证响应",
                attachment_type=allure.attachment_type.JSON
            )

    @allure.story("异常情况测试")
    @allure.title("测试非JSON请求体登录")
    def test_login_non_json_request(self, base_url):
        with allure.step("发送非JSON格式的登录请求"):
            response = requests.post(
                f"{base_url}/login",
                data="not a json",
                headers={"Content-Type": "text/plain"}
            )

        with allure.step("验证响应"):
            assert response.status_code in [400, 500]
            resp_json = response.json()
            assert "message" in resp_json
            if response.status_code == 400:
                assert "请求体必须为JSON格式" in resp_json["message"]
            else:
                assert "服务器内部错误" in resp_json["message"]
            allure.attach(
                json.dumps(resp_json, indent=2, ensure_ascii=False),
                name="异常响应",
                attachment_type=allure.attachment_type.JSON
            )

    @allure.story("性能测试")
    @allure.title("测试连续多次登录")
    @pytest.mark.parametrize("attempt", range(3))  # 重复3次
    def test_repeated_login_attempts(self, base_url, attempt):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        data_path = os.path.join(current_dir, "test_data", "test_users.json")

        with open(data_path, "r", encoding="utf-8") as f:
            users = json.load(f)

        user = users["valid_user"]
        payload = {
            "username": user["username"],
            "password": user["password"]
        }

        with allure.step(f"第{attempt+1}次登录尝试"):
            response = requests.post(f"{base_url}/login", json=payload)

        with allure.step("验证响应"):
            assert response.status_code == 200
            resp_json = response.json()
            assert "token" in resp_json
            allure.attach(
                json.dumps(resp_json, indent=2, ensure_ascii=False),
                name="登录响应",
                attachment_type=allure.attachment_type.JSON
            )
