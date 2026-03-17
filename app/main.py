"""test-dev-pilot: FastAPI 示例应用"""
from fastapi import FastAPI

from app.routes.auth import router as auth_router
from app.routes.profile import router as profile_router

app = FastAPI(title="test-dev-pilot", version="0.1.0")

app.include_router(auth_router, prefix="/api/auth", tags=["认证"])
app.include_router(profile_router, prefix="/api/profile", tags=["用户资料"])


@app.get("/")
async def root():
    return {"message": "Hello, test-dev-pilot!"}


@app.get("/health")
async def health():
    return {"status": "ok"}
