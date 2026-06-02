import redis.asyncio as redis
from core.config import settings

# Shared async Redis client
redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
