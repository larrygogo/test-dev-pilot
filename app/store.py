"""内存用户存储"""
from typing import Dict, Optional

# 内存存储：{email: {id, username, email, hashed_password}}
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
    }
    _users_db[email] = user
    return user
