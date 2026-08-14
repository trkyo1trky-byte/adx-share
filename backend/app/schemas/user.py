from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from datetime import datetime
import uuid

class UserBase(BaseModel):
    email: EmailStr
    full_name: str = Field(..., min_length=2, max_length=255)
    phone: Optional[str] = Field(None, min_length=10, max_length=20)
    country: Optional[str] = None
    language: Optional[str] = "ar"

class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=100)

    @validator('password')
    def validate_password(cls, v):
        if not any(c.isupper() for c in v):
            raise ValueError('يجب أن تحتوي كلمة المرور على حرف كبير واحد على الأقل')
        if not any(c.islower() for c in v):
            raise ValueError('يجب أن تحتوي كلمة المرور على حرف صغير واحد على الأقل')
        if not any(c.isdigit() for c in v):
            raise ValueError('يجب أن تحتوي كلمة المرور على رقم واحد على الأقل')
        if not any(c in '!@#$%^&*()_+-=[]{};:,.<>?/' for c in v):
            raise ValueError('يجب أن تحتوي كلمة المرور على رمز خاص واحد على الأقل')
        return v

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: uuid.UUID
    email: str
    full_name: str
    phone: Optional[str]
    country: Optional[str]
    language: str
    status: str
    email_verified: bool
    created_at: datetime
    last_login_at: Optional[datetime]

    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class PasswordResetRequest(BaseModel):
    email: EmailStr

class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8, max_length=100)

class ChangePassword(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=100)