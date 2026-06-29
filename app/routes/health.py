"""健康检查接口"""
from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
async def health():
    """健康检查，返回服务存活状态"""
    return {"status": "ok"}
