"""认证接口测试"""
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app import store


@pytest.fixture(autouse=True)
def reset_store():
    """每个测试前重置内存存储"""
    store._users_db.clear()
    store._user_id_counter = 0
    yield


client = TestClient(app)

TEST_USER = {
    "username": "张三",
    "email": "zhang@example.com",
    "password": "123456",
}


# ── 注册测试 ──────────────────────────────────

class TestRegister:
    def test_register_success(self):
        resp = client.post("/api/auth/register", json=TEST_USER)
        assert resp.status_code == 201
        data = resp.json()
        assert data["id"] == 1
        assert data["username"] == "张三"
        assert data["email"] == "zhang@example.com"
        assert data["message"] == "注册成功"

    def test_register_duplicate_email(self):
        client.post("/api/auth/register", json=TEST_USER)
        resp = client.post("/api/auth/register", json=TEST_USER)
        assert resp.status_code == 400
        assert resp.json()["detail"] == "该邮箱已被注册"

    def test_register_invalid_email(self):
        resp = client.post("/api/auth/register", json={
            "username": "test",
            "email": "not-an-email",
            "password": "123456",
        })
        assert resp.status_code == 422

    def test_register_short_password(self):
        resp = client.post("/api/auth/register", json={
            "username": "test",
            "email": "test@example.com",
            "password": "123",
        })
        assert resp.status_code == 422

    def test_register_missing_fields(self):
        resp = client.post("/api/auth/register", json={})
        assert resp.status_code == 422


# ── 登录测试 ──────────────────────────────────

class TestLogin:
    def _register(self):
        client.post("/api/auth/register", json=TEST_USER)

    def test_login_success(self):
        self._register()
        resp = client.post("/api/auth/login", json={
            "email": TEST_USER["email"],
            "password": TEST_USER["password"],
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_wrong_password(self):
        self._register()
        resp = client.post("/api/auth/login", json={
            "email": TEST_USER["email"],
            "password": "wrong-password",
        })
        assert resp.status_code == 401
        assert resp.json()["detail"] == "邮箱或密码错误"

    def test_login_nonexistent_user(self):
        resp = client.post("/api/auth/login", json={
            "email": "nobody@example.com",
            "password": "123456",
        })
        assert resp.status_code == 401
        assert resp.json()["detail"] == "邮箱或密码错误"


# ── 获取当前用户测试 ──────────────────────────

class TestGetMe:
    def _get_token(self) -> str:
        client.post("/api/auth/register", json=TEST_USER)
        resp = client.post("/api/auth/login", json={
            "email": TEST_USER["email"],
            "password": TEST_USER["password"],
        })
        return resp.json()["access_token"]

    def test_get_me_success(self):
        token = self._get_token()
        resp = client.get("/api/auth/me", headers={
            "Authorization": f"Bearer {token}",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["username"] == "张三"
        assert data["email"] == "zhang@example.com"
        assert "hashed_password" not in data

    def test_get_me_no_token(self):
        resp = client.get("/api/auth/me")
        assert resp.status_code == 401

    def test_get_me_invalid_token(self):
        resp = client.get("/api/auth/me", headers={
            "Authorization": "Bearer invalid-token",
        })
        assert resp.status_code == 401


# ── 原有端点不受影响 ──────────────────────────

class TestExistingEndpoints:
    def test_root(self):
        resp = client.get("/")
        assert resp.status_code == 200
        assert resp.json()["message"] == "Hello, test-dev-pilot!"

    def test_health(self):
        resp = client.get("/health")
        assert resp.status_code == 200
        assert resp.json()["status"] == "ok"
