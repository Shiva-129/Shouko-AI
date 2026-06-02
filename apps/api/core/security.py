from jose import JWTError, jwt
from jose import jwk
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from core.config import settings
from core.dependencies import MockUser
from sqlalchemy.ext.asyncio import AsyncSession
from core.database import get_db
from sqlalchemy import select
from models.user import User
import httpx
import json
import uuid

SECURITY_SCHEME = HTTPBearer(auto_error=False)

SUPABASE_JWKS_URL = f"{settings.SUPABASE_URL}/.well-known/jwks.json" if settings.SUPABASE_URL else None

_jwks_cache: list[dict] | None = None


async def _fetch_jwks() -> list[dict]:
    global _jwks_cache
    if _jwks_cache is not None:
        return _jwks_cache
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(SUPABASE_JWKS_URL)
            resp.raise_for_status()
            data = resp.json()
            _jwks_cache = data.get("keys", [])
            return _jwks_cache
    except Exception as e:
        print(f"[Security] Failed to fetch JWKS: {e}")
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
        payload = jwt.decode(
            token,
            public_key,
            algorithms=["RS256"],
            options={"verify_aud": False}
        )
        return payload
    except JWTError as e:
        print(f"[Security] JWT validation failed: {e}")
        return None


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(SECURITY_SCHEME),
    db: AsyncSession = Depends(get_db),
) -> User | MockUser:
    if credentials is None:
        if settings.ENVIRONMENT == "development":
            return MockUser()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials

    if settings.ENVIRONMENT == "development" and token == "mock-token":
        return MockUser()

    payload = await verify_supabase_jwt(token)
    if payload is None:
        if settings.ENVIRONMENT == "development":
            return MockUser()
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

    user_id = uuid.UUID(sub) if isinstance(sub, str) else sub
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        email = payload.get("email", f"{sub}@supabase.auth")
        user = User(
            id=user_id,
            email=email,
            interest_profile={"topics": [], "keywords": [], "authors": [], "categories": []},
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)

    return user
