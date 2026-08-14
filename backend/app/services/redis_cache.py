import redis
import json
from ..core.config import settings

redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)

def cache_set(key: str, value, ttl: int = 300):
    """تخزين قيمة في Redis مع مدة صلاحية"""
    redis_client.setex(key, ttl, json.dumps(value))

def cache_get(key: str):
    """استرجاع قيمة من Redis"""
    data = redis_client.get(key)
    if data:
        return json.loads(data)
    return None

def cache_delete(key: str):
    """حذف قيمة من Redis"""
    redis_client.delete(key)

def cache_invalidate_pattern(pattern: str):
    """حذف جميع المفاتيح التي تطابق النمط"""
    for key in redis_client.scan_iter(match=pattern):
        redis_client.delete(key)