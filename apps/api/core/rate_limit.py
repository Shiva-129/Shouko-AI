import time
import uuid
import logging
from fastapi import Request, HTTPException, status, Depends
from core.redis import redis_client
from core.security import get_current_user
from core.dependencies import MockUser
from models.user import User

logger = logging.getLogger(__name__)


class RateLimiter:
    def __init__(self, limit: int, window: int, name: str = "default"):
        self.limit = limit
        self.window = window
        self.name = name

    async def is_rate_limited(self, identifier: str) -> bool:
        key = f"rate_limit:{self.name}:{identifier}"
        now = time.time()
        clear_before = now - self.window
        member = f"{now}:{uuid.uuid4()}"
        
        try:
            pipe = redis_client.pipeline()
            pipe.zremrangebyscore(key, 0, clear_before)
            pipe.zadd(key, {member: now})
            pipe.zcard(key)
            pipe.expire(key, self.window + 10)
            res = await pipe.execute()
            
            current_hits = res[2]
            return current_hits > self.limit
        except Exception as e:
            logger.warning(f"Redis rate limiter exception (falling back to allowed): {e}")
            return False


def RateLimit(limit: int, window: int, name: str = "default"):
    limiter = RateLimiter(limit, window, name)
    
    async def dependency(
        request: Request,
        current_user: User | MockUser = Depends(get_current_user)
    ):
        identifier = str(current_user.id) if current_user else (request.client.host if request.client else "unknown")
        
        if await limiter.is_rate_limited(identifier):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many requests. Please slow down.",
                headers={"Retry-After": str(limiter.window)}
            )
            
    return dependency
