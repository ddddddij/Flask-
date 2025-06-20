import allure
import pytest
import requests
import json


@allure.feature("门禁控制模块")
class TestDoorAPI:
    """门禁控制接口测试套件"""

    @allure.story("门禁基本功能")
    @allure.title("测试开门功能")
    def test_open_door(self, base_url, auth_token):
        with allure.step("准备请求头"):
            headers = {"Authorization": f"Bearer {auth_token}"}
            allure.attach(
                json.dumps(headers, indent=2),
                name="请求头",
                attachment_type=allure.attachment_type.JSON
            )

        with allure.step("发送开门请求"):
            response = requests.get(
                f"{base_url}/door?open=1",
                headers=headers
            )

        with allure.step("验证响应"):
            assert response.status_code == 200
            resp_json = response.json()
            assert "开门成功" in resp_json["message"]
            allure.attach(
                json.dumps(resp_json, indent=2),
                name="响应数据",
                attachment_type=allure.attachment_type.JSON
            )

    @allure.story("门禁基本功能")
    @allure.title("测试关门功能")
    def test_close_door(self, base_url, auth_token):
        with allure.step("发送关门请求"):
            headers = {"Authorization": f"Bearer {auth_token}"}
            response = requests.get(
                f"{base_url}/door?open=2",
                headers=headers
            )

        with allure.step("验证响应"):
            assert response.status_code == 200
            resp_json = response.json()
            assert "关门成功" in resp_json["message"]

    @allure.story("认证测试")
    @allure.title("测试未授权访问")
    def test_unauthorized_access(self, base_url):
        with allure.step("发送无Token的请求"):
            response = requests.get(f"{base_url}/door?open=1")

        with allure.step("验证返回401未授权"):
            assert response.status_code == 401
            resp_json = response.json()
            assert "用户未认证" in resp_json["message"]
            allure.attach(
                json.dumps(resp_json, indent=2),
                name="响应数据",
                attachment_type=allure.attachment_type.JSON
            )

    @allure.story("认证测试")
    @allure.title("测试无效Token访问")
    def test_invalid_token(self, base_url):
        with allure.step("发送无效Token的请求"):
            headers = {"Authorization": "Bearer invalid_token"}
            response = requests.get(
                f"{base_url}/door?open=1",
                headers=headers
            )

        with allure.step("验证返回401未授权"):
            assert response.status_code == 401
            resp_json = response.json()
            assert "无效或过期的令牌" in resp_json["message"]

    @allure.story("参数验证测试")
    @allure.title("测试错误参数")
    @pytest.mark.parametrize("param,expected_msg", [
        ("", "参数错误"),
        ("open=3", "参数错误"),
        ("open=abc", "参数错误"),
        ("open=0", "参数错误"),
        ("open=1.5", "参数错误"),
        ("action=open", "参数错误")  # 错误参数名
    ], ids=[
        "空参数",
        "无效值3",
        "非数字值",
        "零值",
        "浮点值",
        "错误参数名"
    ])
    def test_invalid_parameters(self, base_url, auth_token, param, expected_msg):
        with allure.step(f"发送错误参数: {param}"):
            headers = {"Authorization": f"Bearer {auth_token}"}
            response = requests.get(
                f"{base_url}/door?{param}",
                headers=headers
            )

        with allure.step("验证返回400错误"):
            assert response.status_code == 400
            resp_json = response.json()
            assert expected_msg in resp_json["message"]
            allure.attach(
                f"请求参数: {param}\n响应: {json.dumps(resp_json)}",
                name="请求-响应详情",
                attachment_type=allure.attachment_type.TEXT
            )

    @allure.story("性能测试")
    @allure.title("测试连续多次开门操作")
    @pytest.mark.parametrize("repeat", range(5))  # 重复5次
    def test_repeated_operations(self, base_url, auth_token, repeat):
        with allure.step(f"第{repeat+1}次发送开门请求"):
            headers = {"Authorization": f"Bearer {auth_token}"}
            response = requests.get(
                f"{base_url}/door?open=1",
                headers=headers
            )

        with allure.step("验证响应"):
            assert response.status_code == 200
            resp_json = response.json()
            assert "开门成功" in resp_json["message"]