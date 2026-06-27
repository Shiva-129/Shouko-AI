from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from core.config import settings
from sqlalchemy.ext.asyncio import AsyncSession
from core.database import get_db
from sqlalchemy import select
from models.user import User
import uuid
import datetime
import logging

logger = logging.getLogger("core.security")

SECURITY_SCHEME = HTTPBearer(auto_error=False)

MOCK_USER_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")


def create_token(user_id: str, email: str) -> str:
    payload = {
        "sub": user_id,
        "email": email,
        "iat": datetime.datetime.now(datetime.timezone.utc),
        "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=30),
    }
    return jwt.encode(payload, settings.APP_SECRET_KEY, algorithm="HS256")


async def verify_token(token: str) -> dict | None:
    try:
        payload = jwt.decode(token, settings.APP_SECRET_KEY, algorithms=["HS256"])
        return payload
    except JWTError as e:
        logger.info(f"[Security] Token validation failed: {e}")
        return None


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(SECURITY_SCHEME),
    db: AsyncSession = Depends(get_db),
) -> User:
    if credentials is None:
        if settings.ENVIRONMENT == "development":
            return await _get_or_create_mock_user(db)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = await verify_token(credentials.credentials)
    if payload is None:
        if settings.ENVIRONMENT == "development":
            return await _get_or_create_mock_user(db)
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
        email = payload.get("email", f"{sub}@shouko-ai.app")
        user = User(
            id=user_id,
            email=email,
            name=payload.get("name"),
            onboarded_at=datetime.datetime.now(datetime.timezone.utc),
            interest_profile={"topics": [], "keywords": [], "authors": [], "categories": []},
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)

    return user


async def _get_or_create_mock_user(db: AsyncSession) -> User:
    result = await db.execute(select(User).where(User.id == MOCK_USER_ID))
    user = result.scalar_one_or_none()
    if user:
        return user
    user = User(
        id=MOCK_USER_ID,
        email="demo@shouko-ai.app",
        name="Demo User",
        onboarded_at=datetime.datetime.now(datetime.timezone.utc),
        interest_profile={"topics": ["machine learning", "artificial intelligence"], "keywords": [], "authors": [], "categories": []},
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user
