"""认证相关 API 端点"""
from fastapi import APIRouter, Depends, HTTPException, status

from app.auth import create_access_token, get_current_user, hash_password, verify_password
from app.models import (
    TokenResponse,
    UserInfoResponse,
    UserLoginRequest,
    UserRegisterRequest,
    UserRegisterResponse,
)
from app.store import create_user, get_user_by_email

router = APIRouter()


@router.post("/register", response_model=UserRegisterResponse, status_code=status.HTTP_201_CREATED)
async def register(request: UserRegisterRequest):
    """用户注册"""
    if get_user_by_email(request.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该邮箱已被注册",
        )
    hashed = hash_password(request.password)
    user = create_user(
        username=request.username,
        email=request.email,
        hashed_password=hashed,
    )
    return UserRegisterResponse(
        id=user["id"],
        username=user["username"],
        email=user["email"],
    )


@router.post("/login", response_model=TokenResponse)
async def login(request: UserLoginRequest):
    """用户登录，返回 JWT token"""
    user = get_user_by_email(request.email)
    if not user or not verify_password(request.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="邮箱或密码错误",
        )
    access_token = create_access_token(data={"sub": user["email"]})
    return TokenResponse(access_token=access_token)


@router.get("/me", response_model=UserInfoResponse)
async def get_me(current_user: dict = Depends(get_current_user)):
    """获取当前登录用户信息"""
    return UserInfoResponse(
        id=current_user["id"],
        username=current_user["username"],
        email=current_user["email"],
    )
