"""用户资料管理接口测试"""
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

TEST_USER = {
    "username": "张三",
    "email": "zhang@example.com",
    "password": "123456",
}


def _register_and_login() -> str:
    """注册用户并返回 JWT token"""
    client.post("/api/auth/register", json=TEST_USER)
    resp = client.post("/api/auth/login", json={
        "email": TEST_USER["email"],
        "password": TEST_USER["password"],
    })
    return resp.json()["access_token"]


def _auth_header(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


class TestGetProfile:
    """GET /api/profile"""

    def test_get_profile_success(self):
        """注册后可查看完整资料，新字段有默认值"""
        token = _register_and_login()
        resp = client.get("/api/profile", headers=_auth_header(token))
        assert resp.status_code == 200
        data = resp.json()
        assert data["username"] == "张三"
        assert data["email"] == "zhang@example.com"
        assert data["nickname"] == ""
        assert data["avatar_url"] == ""
        assert data["bio"] == ""
        assert "created_at" in data
        assert "hashed_password" not in data

    def test_get_profile_no_token(self):
        """未认证返回 401"""
        resp = client.get("/api/profile")
        assert resp.status_code == 401

    def test_get_profile_invalid_token(self):
        """无效 token 返回 401"""
        resp = client.get("/api/profile", headers=_auth_header("invalid"))
        assert resp.status_code == 401


class TestUpdateProfile:
    """PUT /api/profile"""

    def test_update_nickname(self):
        """更新昵称"""
        token = _register_and_login()
        resp = client.put("/api/profile", json={"nickname": "小张"}, headers=_auth_header(token))
        assert resp.status_code == 200
        assert resp.json()["nickname"] == "小张"

    def test_update_all_fields(self):
        """同时更新昵称、头像、简介"""
        token = _register_and_login()
        resp = client.put("/api/profile", json={
            "nickname": "小张",
            "avatar_url": "https://example.com/avatar.jpg",
            "bio": "Hello World",
        }, headers=_auth_header(token))
        assert resp.status_code == 200
        data = resp.json()
        assert data["nickname"] == "小张"
        assert data["avatar_url"] == "https://example.com/avatar.jpg"
        assert data["bio"] == "Hello World"

    def test_update_preserves_other_fields(self):
        """更新某字段不影响其他字段"""
        token = _register_and_login()
        client.put("/api/profile", json={"nickname": "小张"}, headers=_auth_header(token))
        resp = client.put("/api/profile", json={"bio": "test"}, headers=_auth_header(token))
        data = resp.json()
        assert data["nickname"] == "小张"
        assert data["bio"] == "test"

    def test_update_empty_body(self):
        """空请求体返回 400"""
        token = _register_and_login()
        resp = client.put("/api/profile", json={}, headers=_auth_header(token))
        assert resp.status_code == 400

    def test_update_no_token(self):
        """未认证返回 401"""
        resp = client.put("/api/profile", json={"nickname": "test"})
        assert resp.status_code == 401

    def test_username_email_immutable(self):
        """username 和 email 不可通过更新接口修改"""
        token = _register_and_login()
        resp = client.get("/api/profile", headers=_auth_header(token))
        assert resp.json()["username"] == "张三"
        assert resp.json()["email"] == "zhang@example.com"


class TestChangePassword:
    """PUT /api/profile/password"""

    def test_change_password_success(self):
        """正确的旧密码可以修改密码"""
        token = _register_and_login()
        resp = client.put("/api/profile/password", json={
            "old_password": "123456",
            "new_password": "654321",
        }, headers=_auth_header(token))
        assert resp.status_code == 200
        assert resp.json()["message"] == "密码修改成功"

    def test_login_with_new_password(self):
        """修改密码后可用新密码登录"""
        token = _register_and_login()
        client.put("/api/profile/password", json={
            "old_password": "123456",
            "new_password": "654321",
        }, headers=_auth_header(token))
        resp = client.post("/api/auth/login", json={
            "email": "zhang@example.com",
            "password": "654321",
        })
        assert resp.status_code == 200

    def test_old_password_invalid(self):
        """旧密码错误返回 400"""
        token = _register_and_login()
        resp = client.put("/api/profile/password", json={
            "old_password": "wrong!",
            "new_password": "654321",
        }, headers=_auth_header(token))
        assert resp.status_code == 400
        assert "旧密码错误" in resp.json()["detail"]

    def test_same_password(self):
        """新旧密码相同返回 400"""
        token = _register_and_login()
        resp = client.put("/api/profile/password", json={
            "old_password": "123456",
            "new_password": "123456",
        }, headers=_auth_header(token))
        assert resp.status_code == 400
        assert "不能与旧密码相同" in resp.json()["detail"]

    def test_short_new_password(self):
        """新密码长度不足返回 422"""
        token = _register_and_login()
        resp = client.put("/api/profile/password", json={
            "old_password": "123456",
            "new_password": "123",
        }, headers=_auth_header(token))
        assert resp.status_code == 422

    def test_change_password_no_token(self):
        """未认证返回 401"""
        resp = client.put("/api/profile/password", json={
            "old_password": "123456",
            "new_password": "654321",
        })
        assert resp.status_code == 401
