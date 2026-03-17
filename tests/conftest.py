import pytest
from app import store


@pytest.fixture(autouse=True)
def reset_store():
    """每个测试前重置内存存储"""
    store._users_db.clear()
    store._user_id_counter = 0
    yield
