"""
خدمة المصادقة – Auth Service
مسؤولة عن جميع عمليات المصادقة: التسجيل، تسجيل الدخول، التوكنات، إعادة تعيين كلمة المرور...
"""

from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
import uuid
from typing import Optional, Tuple

from ..models.user import User, UserStatus, UserSession, RefreshToken
from ..models.role import Role, UserRole  # ✅ مطلوب لإضافة دور USER
from ..schemas.user import UserCreate, UserLogin
from ..core.security import hash_password, verify_password, create_access_token, create_refresh_token, verify_token
from ..core.config import settings


# ============= استثناءات مخصصة =============
class AuthError(Exception):
    """الخطأ الأساسي في المصادقة"""
    pass

class UserNotFoundError(AuthError):
    """المستخدم غير موجود"""
    pass

class InvalidCredentialsError(AuthError):
    """بيانات الدخول غير صحيحة"""
    pass

class AccountBlockedError(AuthError):
    """الحساب محظور أو معلق"""
    pass

class EmailNotVerifiedError(AuthError):
    """البريد الإلكتروني غير مؤكد"""
    pass

class InvalidTokenError(AuthError):
    """التوكن غير صالح أو منتهي الصلاحية"""
    pass


# ============= خدمة المصادقة =============
class AuthService:
    """
    خدمة المصادقة – تدير جميع عمليات المستخدمين والتوكنات والجلسات.
    """

    def __init__(self, db: Session):
        self.db = db

    # ---------- التسجيل ----------
    def register_user(self, user_data: UserCreate) -> User:
        """
        تسجيل مستخدم جديد.
        يتحقق من عدم وجود البريد الإلكتروني مسبقاً، ثم ينشئ المستخدم.
        ✅ إضافة دور USER تلقائياً
        """
        # التحقق من وجود البريد الإلكتروني
        existing = self.db.query(User).filter(User.email == user_data.email).first()
        if existing:
            raise AuthError("البريد الإلكتروني مستخدم بالفعل")

        # إنشاء المستخدم الجديد
        user = User(
            email=user_data.email,
            password_hash=hash_password(user_data.password),
            full_name=user_data.full_name,
            phone=user_data.phone,
            country=user_data.country,
            language=user_data.language,
            status=UserStatus.PENDING
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)

        # ✅ إضافة دور USER الأساسي (مدمج من النسخة الثانية)
        user_role_obj = self.db.query(Role).filter(Role.name == "USER").first()
        if user_role_obj:
            user_role = UserRole(user_id=user.id, role_id=user_role_obj.id)
            self.db.add(user_role)
            self.db.commit()

        return user

    # ---------- تسجيل الدخول ----------
    def login(self, login_data: UserLogin, ip_address: str, user_agent: str) -> Tuple[User, str, str]:
        """
        تسجيل الدخول.
        يتحقق من صحة البريد وكلمة المرور، وحالة الحساب، وتأكيد البريد.
        يعيد المستخدم مع توكن الوصول وتوكن التحديث.
        """
        # البحث عن المستخدم
        user = self.db.query(User).filter(User.email == login_data.email).first()
        if not user:
            raise InvalidCredentialsError("البريد الإلكتروني أو كلمة المرور غير صحيحة")

        # التحقق من حالة المستخدم
        if user.status == UserStatus.BLOCKED:
            raise AccountBlockedError("الحساب محظور. يرجى التواصل مع الدعم")
        if user.status == UserStatus.SUSPENDED:
            raise AccountBlockedError("الحساب معلق. يرجى التواصل مع الدعم")
        if user.status == UserStatus.DELETED:
            raise UserNotFoundError("الحساب غير موجود")

        # التحقق من تأكيد البريد الإلكتروني
        if not user.email_verified:
            raise EmailNotVerifiedError("يرجى تأكيد البريد الإلكتروني أولاً")

        # التحقق من كلمة المرور
        if not verify_password(login_data.password, user.password_hash):
            raise InvalidCredentialsError("البريد الإلكتروني أو كلمة المرور غير صحيحة")

        # تحديث معلومات آخر دخول
        user.last_login_at = datetime.now(timezone.utc)
        user.last_login_ip = ip_address
        self.db.commit()

        # إنشاء الجلسة
        session = UserSession(
            user_id=user.id,
            ip_address=ip_address,
            user_agent=user_agent,
            expires_at=datetime.now(timezone.utc) + timedelta(days=30)
        )
        self.db.add(session)
        self.db.commit()

        # إنشاء التوكنات
        access_token = create_access_token(user.id, {"email": user.email})
        refresh_token = create_refresh_token(user.id)

        # تخزين Refresh Token في قاعدة البيانات
        refresh_token_obj = RefreshToken(
            user_id=user.id,
            token=refresh_token,
            expires_at=datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        )
        self.db.add(refresh_token_obj)
        self.db.commit()

        return user, access_token, refresh_token

    # ---------- تحديث التوكن ----------
    def refresh_access_token(self, refresh_token: str) -> Tuple[str, str]:
        """
        تحديث توكن الوصول باستخدام توكن التحديث.
        يعيد توكن وصول جديد وتوكن تحديث جديد (Rotation).
        """
        # التحقق من صحة التوكن
        payload = verify_token(refresh_token, is_refresh=True)
        if not payload:
            raise InvalidTokenError("توكن التحديث غير صالح")

        user_id = payload.get("sub")
        if not user_id:
            raise InvalidTokenError("توكن التحديث غير صالح")

        # البحث عن التوكن في قاعدة البيانات
        token_record = self.db.query(RefreshToken).filter(
            RefreshToken.token == refresh_token,
            RefreshToken.revoked == False
        ).first()

        if not token_record:
            raise InvalidTokenError("توكن التحديث غير موجود")
        if token_record.expires_at < datetime.now(timezone.utc):
            raise InvalidTokenError("توكن التحديث منتهي الصلاحية")

        # إنشاء توكنات جديدة
        new_access_token = create_access_token(uuid.UUID(user_id))
        new_refresh_token = create_refresh_token(uuid.UUID(user_id))

        # إلغاء التوكن القديم وإنشاء جديد
        token_record.revoked = True
        token_record.revoked_at = datetime.now(timezone.utc)

        new_token_record = RefreshToken(
            user_id=uuid.UUID(user_id),
            token=new_refresh_token,
            expires_at=datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        )
        self.db.add(new_token_record)
        self.db.commit()

        return new_access_token, new_refresh_token

    # ---------- تسجيل الخروج ----------
    def logout(self, user_id: uuid.UUID, refresh_token: Optional[str] = None) -> None:
        """
        تسجيل الخروج.
        يلغي جميع جلسات المستخدم، ويلغي توكن التحديث إذا تم إرساله.
        """
        # إلغاء جميع جلسات المستخدم
        sessions = self.db.query(UserSession).filter(
            UserSession.user_id == user_id,
            UserSession.revoked == False
        ).all()
        for session in sessions:
            session.revoked = True
        self.db.commit()

        # إلغاء توكن التحديث إذا تم إرساله
        if refresh_token:
            token_record = self.db.query(RefreshToken).filter(
                RefreshToken.token == refresh_token,
                RefreshToken.revoked == False
            ).first()
            if token_record:
                token_record.revoked = True
                token_record.revoked_at = datetime.now(timezone.utc)
                self.db.commit()

    # ---------- استرجاع المستخدم ----------
    def get_user_by_id(self, user_id: uuid.UUID) -> Optional[User]:
        """الحصول على المستخدم بواسطة المعرف"""
        return self.db.query(User).filter(
            User.id == user_id,
            User.deleted_at.is_(None)
        ).first()

    def get_user_by_email(self, email: str) -> Optional[User]:
        """الحصول على المستخدم بواسطة البريد الإلكتروني"""
        return self.db.query(User).filter(
            User.email == email,
            User.deleted_at.is_(None)
        ).first()

    # ---------- تأكيد البريد ----------
    def verify_email(self, user_id: uuid.UUID) -> bool:
        """تأكيد البريد الإلكتروني وتفعيل الحساب"""
        user = self.get_user_by_id(user_id)
        if not user:
            return False
        user.email_verified = True
        if user.status == UserStatus.PENDING:
            user.status = UserStatus.ACTIVE
        self.db.commit()
        return True

    # ---------- إعادة تعيين كلمة المرور ----------
    def reset_password(self, email: str) -> str:
        """
        طلب إعادة تعيين كلمة المرور.
        يعيد توكن لإعادة التعيين (يُرسل عبر البريد الإلكتروني في الإنتاج).
        """
        user = self.get_user_by_email(email)
        if not user:
            raise UserNotFoundError("المستخدم غير موجود")

        # إنشاء توكن لإعادة التعيين (صلاحية 1 ساعة)
        token = create_access_token(
            user.id,
            {"purpose": "password_reset", "email": user.email}
        )
        return token

    def confirm_password_reset(self, token: str, new_password: str) -> bool:
        """تأكيد إعادة تعيين كلمة المرور وتحديثها"""
        payload = verify_token(token)
        if not payload:
            raise InvalidTokenError("التوكن غير صالح")
        if payload.get("purpose") != "password_reset":
            raise InvalidTokenError("التوكن غير صالح لهذه العملية")

        user_id = payload.get("sub")
        if not user_id:
            raise InvalidTokenError("التوكن غير صالح")

        user = self.get_user_by_id(uuid.UUID(user_id))
        if not user:
            raise UserNotFoundError("المستخدم غير موجود")

        user.password_hash = hash_password(new_password)
        self.db.commit()
        return True