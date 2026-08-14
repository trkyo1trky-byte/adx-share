from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import Any
import uuid

from ...core.database import get_db
from ...core.security import create_access_token, verify_token
from ...core.config import settings
from ...schemas.user import (
    UserCreate, UserLogin, UserResponse, TokenResponse,
    RefreshTokenRequest, PasswordResetRequest, PasswordResetConfirm,
    ChangePassword
)
from ...services.auth_service import AuthService
from ...services.rate_limiter import rate_limit_login, rate_limit_register, rate_limit_password_reset
from ...services.email_service import send_verification_email, send_reset_email

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    request: Request,
    db: Session = Depends(get_db)
):
    """تسجيل مستخدم جديد"""
    # ===== Rate Limiting =====
    ip = request.client.host if request.client else "unknown"
    if not rate_limit_register(ip):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="محاولات تسجيل كثيرة، يرجى المحاولة لاحقاً"
        )

    try:
        service = AuthService(db)
        user = service.register_user(user_data)
        
        # ===== إرسال بريد تأكيد =====
        if settings.EMAIL_VERIFICATION_REQUIRED:
            token = create_access_token(user.id, {"purpose": "email_verification"})
            send_verification_email(user.email, token)
            
        return user
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.post("/login", response_model=TokenResponse)
async def login(
    login_data: UserLogin,
    request: Request,
    db: Session = Depends(get_db)
):
    """تسجيل الدخول والحصول على توكنات"""
    # ===== Rate Limiting =====
    ip = request.client.host if request.client else "unknown"
    if not rate_limit_login(ip, login_data.email):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="محاولات تسجيل دخول كثيرة، يرجى المحاولة لاحقاً"
        )

    try:
        service = AuthService(db)
        ip_address = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "unknown")
        user, access_token, refresh_token = service.login(login_data, ip_address, user_agent)

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=900
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(refresh_data: RefreshTokenRequest, db: Session = Depends(get_db)):
    """تحديث توكن الوصول"""
    try:
        service = AuthService(db)
        access_token, refresh_token = service.refresh_access_token(refresh_data.refresh_token)
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=900
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(request: Request, db: Session = Depends(get_db)):
    """تسجيل الخروج"""
    try:
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="توكن غير صالح")

        access_token = auth_header.split(" ")[1]
        payload = verify_token(access_token)
        if not payload:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="توكن غير صالح")

        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="توكن غير صالح")

        refresh_token = request.headers.get("X-Refresh-Token")
        service = AuthService(db)
        service.logout(uuid.UUID(user_id), refresh_token)
        return
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.post("/forgot-password")
async def forgot_password(
    reset_data: PasswordResetRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """طلب إعادة تعيين كلمة المرور"""
    # ===== Rate Limiting =====
    ip = request.client.host if request.client else "unknown"
    if not rate_limit_password_reset(ip, reset_data.email):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="طلبات كثيرة، يرجى المحاولة لاحقاً"
        )

    try:
        service = AuthService(db)
        token = service.reset_password(reset_data.email)
        
        # ===== إرسال البريد الإلكتروني بدلاً من إرجاع التوكن =====
        send_reset_email(reset_data.email, token)
        return {"message": "تم إرسال رابط إعادة تعيين كلمة المرور إلى بريدك الإلكتروني"}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.post("/reset-password")
async def confirm_reset_password(reset_data: PasswordResetConfirm, db: Session = Depends(get_db)):
    """تأكيد إعادة تعيين كلمة المرور"""
    try:
        service = AuthService(db)
        service.confirm_password_reset(reset_data.token, reset_data.new_password)
        return {"message": "تم إعادة تعيين كلمة المرور بنجاح"}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.post("/verify-email/{user_id}")
async def verify_email(user_id: str, db: Session = Depends(get_db)):
    """تأكيد البريد الإلكتروني"""
    try:
        service = AuthService(db)
        success = service.verify_email(uuid.UUID(user_id))
        if not success:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="المستخدم غير موجود")
        return {"message": "تم تأكيد البريد الإلكتروني بنجاح"}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))