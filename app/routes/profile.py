"""用户资料管理接口"""
from fastapi import APIRouter, Depends, HTTPException

from app.auth import get_current_user, hash_password, verify_password
from app.models import ChangePasswordRequest, ProfileResponse, UpdateProfileRequest
from app import store

router = APIRouter()


@router.get("", response_model=ProfileResponse)
def get_profile(current_user: dict = Depends(get_current_user)):
    return ProfileResponse(
        id=current_user["id"],
        username=current_user["username"],
        email=current_user["email"],
        nickname=current_user.get("nickname", ""),
        avatar_url=current_user.get("avatar_url", ""),
        bio=current_user.get("bio", ""),
        created_at=current_user.get("created_at", ""),
    )


@router.put("", response_model=ProfileResponse)
def update_profile(
    request: UpdateProfileRequest,
    current_user: dict = Depends(get_current_user),
):
    updates = request.model_dump(exclude_none=True)
    if not updates:
        raise HTTPException(status_code=400, detail="没有提供需要更新的字段")

    updated_user = store.update_user(current_user["email"], updates)
    return ProfileResponse(
        id=updated_user["id"],
        username=updated_user["username"],
        email=updated_user["email"],
        nickname=updated_user.get("nickname", ""),
        avatar_url=updated_user.get("avatar_url", ""),
        bio=updated_user.get("bio", ""),
        created_at=updated_user.get("created_at", ""),
    )


@router.put("/password")
def change_password(
    request: ChangePasswordRequest,
    current_user: dict = Depends(get_current_user),
):
    if not verify_password(request.old_password, current_user["hashed_password"]):
        raise HTTPException(status_code=400, detail="旧密码错误")

    # 比较用户提交的明文输入，而非哈希值
    if request.old_password == request.new_password:
        raise HTTPException(status_code=400, detail="新密码不能与旧密码相同")

    new_hashed = hash_password(request.new_password)
    store.update_user_password(current_user["email"], new_hashed)
    return {"message": "密码修改成功"}
