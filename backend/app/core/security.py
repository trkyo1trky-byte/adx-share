from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from typing import Optional, Dict, Any
import uuid
from .config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """تشفير كلمة المرور باستخدام bcrypt"""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """التحقق من صحة كلمة المرور"""
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(user_id: uuid.UUID, extra_data: Optional[Dict[str, Any]] = None) -> str:
    """إنشاء توكن وصول (Access Token)"""
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": str(user_id),
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "type": "access"
    }
    if extra_data:
        payload.update(extra_data)
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)

def create_refresh_token(user_id: uuid.UUID) -> str:
    """إنشاء توكن تحديث (Refresh Token)"""
    expire = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    payload = {
        "sub": str(user_id),
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "type": "refresh"
    }
    return jwt.encode(payload, settings.JWT_REFRESH_SECRET, algorithm=settings.JWT_ALGORITHM)

def verify_token(token: str, is_refresh: bool = False) -> Optional[Dict[str, Any]]:
    """التحقق من صحة التوكن وفك تشفيره"""
    try:
        secret = settings.JWT_REFRESH_SECRET if is_refresh else settings.JWT_SECRET
        payload = jwt.decode(token, secret, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except JWTError:
        return None

def decode_token(token: str, is_refresh: bool = False) -> Optional[Dict[str, Any]]:
    """فك تشفير التوكن (بدون التحقق من الصلاحية)"""
    try:
        secret = settings.JWT_REFRESH_SECRET if is_refresh else settings.JWT_SECRET
        payload = jwt.decode(token, secret, algorithms=[settings.JWT_ALGORITHM], options={"verify_exp": False})
        return payload
    except JWTError:
        return None