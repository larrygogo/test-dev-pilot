"""Pydantic 请求/响应模型"""
from pydantic import BaseModel, EmailStr, Field


class UserRegisterRequest(BaseModel):
    username: str = Field(..., min_length=1, description="用户名")
    email: EmailStr = Field(..., description="邮箱地址")
    password: str = Field(..., min_length=6, description="密码，最少6位")


class UserRegisterResponse(BaseModel):
    id: int
    username: str
    email: str
    message: str = "注册成功"


class UserLoginRequest(BaseModel):
    email: EmailStr = Field(..., description="邮箱地址")
    password: str = Field(..., description="密码")


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserInfoResponse(BaseModel):
    id: int
    username: str
    email: str
