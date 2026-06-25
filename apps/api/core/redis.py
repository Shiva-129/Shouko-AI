import logging
import redis.asyncio as redis
from core.config import settings

logger = logging.getLogger("core.redis")
_redis_client: redis.Redis | None = None


def _get_redis() -> redis.Redis | None:
    global _redis_client
    if _redis_client is not None:
        return _redis_client
    if not settings.REDIS_URL:
        logger.info("[Redis] No REDIS_URL configured — using fakeredis in-memory fallback")
        return _get_fakeredis()
    try:
        client = redis.from_url(settings.REDIS_URL, decode_responses=True, socket_connect_timeout=2)
        _redis_client = client
        return client
    except Exception as e:
        logger.info(f"[Redis] Real Redis unreachable ({e}) — using fakeredis in-memory fallback")
        return _get_fakeredis()


def _get_fakeredis() -> redis.Redis | None:
    try:
        import fakeredis.aioredis as fakeredis_aioredis
        client = fakeredis_aioredis.FakeRedis(decode_responses=True)
        _redis_client = client
        return client
    except ImportError:
        logger.info("[Redis] fakeredis not installed — running without Redis cache; rate limiting degraded")
        return None


redis_client = _get_redis()
