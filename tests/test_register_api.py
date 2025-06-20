import requests
import allure
import random
import string
import pytest
import json


@allure.feature("用户注册模块")
class TestRegisterAPI:
    """用户注册接口测试套件"""

    @allure.story("成功注册新用户")
    @allure.title("测试正常注册流程")
    def test_register_success(self, base_url):
        """测试注册接口能成功注册新用户"""
        # 生成随机用户名，避免重复
        username = "user_" + ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
        password = "Test1234"

        payload = {"username": username, "password": password}

        with allure.step(f"使用用户名 {username} 注册新用户"):
            response = requests.post(f"{base_url}/register", json=payload)

        with allure.step("验证响应"):
            assert response.status_code == 200
            resp_json = response.json()
            assert "message" in resp_json
            assert "成功" in resp_json["message"]
            allure.attach(
                json.dumps(resp_json, indent=2),
                name="响应数据",
                attachment_type=allure.attachment_type.JSON
            )

    @allure.story("注册已存在的用户")
    @allure.title("测试重复注册")
    def test_register_existing_user(self, base_url):
        """测试注册已存在的用户"""
        # 使用已知存在的测试用户
        username = "test_user"
        password = "Test1234"

        payload = {"username": username, "password": password}

        with allure.step(f"尝试注册已存在的用户 {username}"):
            response = requests.post(f"{base_url}/register", json=payload)

        with allure.step("验证响应"):
            assert response.status_code == 409
            resp_json = response.json()
            assert "message" in resp_json
            assert "已存在" in resp_json["message"]

    @allure.story("注册参数验证")
    @allure.title("测试无效用户名注册")
    @pytest.mark.parametrize("username,password,expected_msg", [
        ("", "Test1234", "用户名和密码不能为空"),
        ("usr", "Test1234", "用户名长度必须在4-20个字符之间"),
        ("a" * 21, "Test1234", "用户名长度必须在4-20个字符之间"),
        ("test@user", "Test1234", None)  # 假设允许特殊字符
    ])
    def test_invalid_username(self, base_url, username, password, expected_msg):
        """测试无效用户名的注册"""
        payload = {"username": username, "password": password}

        with allure.step(f"尝试使用无效用户名注册: {username}"):
            response = requests.post(f"{base_url}/register", json=payload)

        with allure.step("验证响应"):
            if expected_msg:
                assert response.status_code == 400
                resp_json = response.json()
                assert expected_msg in resp_json["message"]
            else:
                assert response.status_code in [200, 409]

    @allure.story("注册参数验证")
    @allure.title("测试无效密码注册")
    @pytest.mark.parametrize("username,password,expected_msg", [
        ("valid_user", "", "用户名和密码不能为空"),
        ("valid_user", "short", "密码长度不能少于6个字符"),
        ("valid_user", "123456", None),  # 纯数字密码
        ("valid_user", "password", None)  # 纯字母密码
    ])
    def test_invalid_password(self, base_url, username, password, expected_msg):
        """测试无效密码的注册"""
        # 生成随机用户名避免冲突
        if username == "valid_user":
            username = "user_" + ''.join(random.choices(string.ascii_lowercase, k=8))

        payload = {"username": username, "password": password}

        with allure.step(f"尝试使用无效密码注册: {password}"):
            response = requests.post(f"{base_url}/register", json=payload)

        with allure.step("验证响应"):
            if expected_msg:
                assert response.status_code == 400
                resp_json = response.json()
                assert expected_msg in resp_json["message"]
            else:
                assert response.status_code in [200, 409]

    @allure.story("异常情况测试")
    @allure.title("测试空请求体注册")
    def test_empty_request(self, base_url):
        """测试发送空请求体"""
        with allure.step("发送空请求体"):
            response = requests.post(f"{base_url}/register", json={})

        with allure.step("验证响应"):
            assert response.status_code == 400
            resp_json = response.json()
            assert "请求体必须为JSON格式" in resp_json["message"]

    @allure.story("异常情况测试")
    @allure.title("测试非JSON请求体注册")
    def test_non_json_request(self, base_url):
        """测试发送非JSON请求体"""
        with allure.step("发送非JSON请求体"):
            response = requests.post(
                f"{base_url}/register",
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