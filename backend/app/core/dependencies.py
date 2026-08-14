from fastapi import Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import Optional
import uuid

from .database import get_db
from ..models.user import User
from ..services.auth_service import AuthService
from .security import verify_token

async def get_current_user(
    request: Request,
    db: Session = Depends(get_db)
) -> User:
    """الحصول على المستخدم الحالي من التوكن"""
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="توكن المصادقة مطلوب",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = auth_header.split(" ")[1]
    payload = verify_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="توكن غير صالح أو منتهي الصلاحية",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="توكن غير صالح",
        )

    service = AuthService(db)
    user = service.get_user_by_id(uuid.UUID(user_id))
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="المستخدم غير موجود",
        )

    if user.status in ["SUSPENDED", "BLOCKED", "DELETED"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"الحساب {user.status}. يرجى التواصل مع الدعم",
        )

    return user

async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """الحصول على المستخدم النشط (تم تأكيد البريد)"""
    if not current_user.email_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="يرجى تأكيد البريد الإلكتروني أولاً",
        )
    return current_user

def require_permission(permission: str):
    """مصنع دالة للتحقق من الصلاحيات"""
    async def permission_dependency(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):
        # التحقق من وجود الصلاحية للمستخدم
        # سيتم تنفيذ هذا في المرحلة القادمة بعد إضافة RBAC
        # حالياً نسمح لكل المستخدمين النشطين
        return current_user
    return permission_dependency