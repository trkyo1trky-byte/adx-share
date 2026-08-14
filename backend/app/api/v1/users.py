from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Any

from ...core.database import get_db
from ...core.dependencies import get_current_user
from ...models.user import User
from ...schemas.user import UserResponse

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """الحصول على معلومات المستخدم الحالي"""
    return current_user