import redis
from datetime import timedelta
from fastapi import HTTPException, status
from ..core.config import settings

# اتصال Redis
redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)

def check_rate_limit(key: str, limit: int, period_seconds: int) -> bool:
    """
    التحقق من تجاوز الحد المسموح به.
    key: مفتاح فريد (مثل IP:email)
    limit: عدد المحاولات المسموح بها
    period_seconds: الفترة الزمنية بالثواني
    """
    current = redis_client.get(key)
    if current is None:
        redis_client.setex(key, period_seconds, 1)
        return True
    current = int(current)
    if current >= limit:
        return False
    redis_client.incr(key)
    return True

def rate_limit_login(ip: str, email: str) -> bool:
    """تحديد معدل محاولات تسجيل الدخول"""
    key = f"rate_limit:login:{ip}:{email}"
    return check_rate_limit(key, settings.RATE_LIMIT_LOGIN, 60)

def rate_limit_register(ip: str) -> bool:
    """تحديد معدل محاولات التسجيل"""
    key = f"rate_limit:register:{ip}"
    return check_rate_limit(key, settings.RATE_LIMIT_REGISTER, 3600)

def rate_limit_password_reset(ip: str, email: str) -> bool:
    """تحديد معدل طلبات إعادة تعيين كلمة المرور"""
    key = f"rate_limit:reset:{ip}:{email}"
    return check_rate_limit(key, 3, 3600)