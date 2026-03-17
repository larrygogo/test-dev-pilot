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


class UpdateProfileRequest(BaseModel):
    nickname: str | None = None
    avatar_url: str | None = None
    bio: str | None = None


class ChangePasswordRequest(BaseModel):
    old_password: str = Field(..., min_length=6)
    new_password: str = Field(..., min_length=6)


class ProfileResponse(BaseModel):
    id: int
    username: str
    email: str
    nickname: str
    avatar_url: str
    bio: str
    created_at: str
