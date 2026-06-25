from jose import JWTError, jwt
from jose import jwk
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from core.config import settings
from core.supabase_utils import normalize_supabase_url
from sqlalchemy.ext.asyncio import AsyncSession
from core.database import get_db
from sqlalchemy import select
from models.user import User
import httpx
import time
import uuid
import logging

logger = logging.getLogger("core.security")

SECURITY_SCHEME = HTTPBearer(auto_error=False)

_supabase_base = normalize_supabase_url(settings.SUPABASE_URL) if settings.SUPABASE_URL else None
SUPABASE_JWKS_URL = f"{_supabase_base}/auth/v1/.well-known/jwks.json" if _supabase_base else None

_jwks_cache: list[dict] | None = None
_jwks_cache_ts: float = 0.0
JWKS_CACHE_TTL: float = 3600.0  # 1 hour


async def _fetch_jwks() -> list[dict]:
    global _jwks_cache, _jwks_cache_ts
    now = time.time()
    if _jwks_cache is not None and (now - _jwks_cache_ts) < JWKS_CACHE_TTL:
        return _jwks_cache
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(SUPABASE_JWKS_URL)
            resp.raise_for_status()
            data = resp.json()
            _jwks_cache = data.get("keys", [])
            _jwks_cache_ts = now
            return _jwks_cache
    except Exception as e:
        logger.info(f"[Security] Failed to fetch JWKS: {e}")
        return []


async def verify_supabase_jwt(token: str) -> dict | None:
    try:
        unverified_header = jwt.get_unverified_header(token)
        jwks = await _fetch_jwks()
        if not jwks:
            return None

        matching_key = None
        for key in jwks:
            if key.get("kid") == unverified_header.get("kid"):
                matching_key = key
                break

        if not matching_key:
            return None

        public_key = jwk.construct(matching_key)
        # SECURITY-TODO: Enable audience verification once the correct `aud` value is determined.
        # Supabase JWTs typically use `"authenticated"` or the project URL.
        # Set `audience=settings.SUPABASE_URL` and remove `options={"verify_aud": False}`.
        payload = jwt.decode(
            token,
            public_key,
            algorithms=["RS256", "ES256"],
            options={"verify_aud": False}
        )
        return payload
    except JWTError as e:
        logger.info(f"[Security] JWT validation failed: {e}")
        return None


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(SECURITY_SCHEME),
    db: AsyncSession = Depends(get_db),
) -> User:
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials

    payload = await verify_supabase_jwt(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    sub = payload.get("sub")
    if not sub:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token missing subject claim",
        )

    try:
        user_id = uuid.UUID(sub) if isinstance(sub, str) else sub
    except (ValueError, AttributeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user identifier in authentication token."
        )
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        email = payload.get("email", f"{sub}@supabase.auth")
        user = User(
            id=user_id,
            email=email,
            name=payload.get("user_metadata", {}).get("full_name"),
            onboarded_at=datetime.datetime.now(datetime.timezone.utc),
            interest_profile={"topics": [], "keywords": [], "authors": [], "categories": []},
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        # Send welcome email asynchronously — fire-and-forget
        try:
            from services.email_service import EmailService
            email_svc = EmailService()
            await email_svc.send_welcome_email(user.email, user.name or "Researcher")
        except Exception:
            pass

    return user
