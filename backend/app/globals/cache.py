from fastapi_cache.backends.redis import RedisBackend
from redis import asyncio as aioredis

from app.config import get_settings

# Redis缓存实例
redis_be: RedisBackend = RedisBackend(
    aioredis.from_url(get_settings().redis_url, encoding='utf8', decode_responses=True)
)
