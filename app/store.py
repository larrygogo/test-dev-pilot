"""内存用户存储"""
from datetime import datetime, timezone
from typing import Dict, Optional

# 内存存储：{email: {id, username, email, hashed_password, ...}}
_users_db: Dict[str, dict] = {}
_user_id_counter: int = 0


def get_user_by_email(email: str) -> Optional[dict]:
    """根据邮箱查找用户"""
    return _users_db.get(email)


def create_user(username: str, email: str, hashed_password: str) -> dict:
    """创建新用户并存入内存"""
    global _user_id_counter
    _user_id_counter += 1
    user = {
        "id": _user_id_counter,
        "username": username,
        "email": email,
        "hashed_password": hashed_password,
        "nickname": "",
        "avatar_url": "",
        "bio": "",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    _users_db[email] = user
    return user


def update_user(email: str, updates: dict) -> dict | None:
    """更新用户资料，返回更新后的用户数据。不可修改字段自动忽略。"""
    if email not in _users_db:
        return None
    protected_fields = ("id", "email", "username", "hashed_password", "created_at")
    for key, value in updates.items():
        if key in _users_db[email] and key not in protected_fields:
            _users_db[email][key] = value
    return _users_db[email]


def update_user_password(email: str, new_hashed_password: str) -> bool:
    """更新用户密码哈希。返回是否成功。"""
    if email not in _users_db:
        return False
    _users_db[email]["hashed_password"] = new_hashed_password
    return True
