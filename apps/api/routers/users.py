from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from core.dependencies import get_db
from core.security import get_current_user
from core.usage import get_monthly_count, get_daily_count, MONTHLY_LIMITS, DAILY_LIMITS
from models.user import User
import datetime
from services.email_service import EmailService

email_service = EmailService()

router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


class InterestProfile(BaseModel):
    topics: list[str] = Field(default_factory=list)
    keywords: list[str] = Field(default_factory=list)
    authors: list[str] = Field(default_factory=list)
    categories: list[str] = Field(default_factory=list)


class UpdateUserRequest(BaseModel):
    name: str | None = None
    interest_profile: InterestProfile | None = None


class UserResponse(BaseModel):
    id: str
    email: str
    name: str | None
    avatar_url: str | None
    plan: str
    interest_profile: dict
    onboarded_at: str | None
    created_at: str
    usage: dict | None = None


class UsageSummary(BaseModel):
    artifact_created_monthly: int
    artifact_created_limit: int | None
    question_asked_daily: int
    question_asked_limit: int | None
    paper_ingested_monthly: int
    paper_ingested_limit: int | None


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    if user.onboarded_at is None:
        if isinstance(user, User):
            user.onboarded_at = datetime.datetime.utcnow()
            await db.commit()
            await db.refresh(user)
        else:
            user.onboarded_at = datetime.datetime.utcnow()
        await email_service.send_welcome_email(user.email, user.name or "Researcher")

    plan = user.plan or "free"
    usage = {
        "artifact_created_monthly": await get_monthly_count(db, user.id, "artifact_created"),
        "artifact_created_limit": MONTHLY_LIMITS.get(plan, {}).get("artifact_created"),
        "question_asked_daily": await get_daily_count(db, user.id, "question_asked"),
        "question_asked_limit": DAILY_LIMITS.get(plan, {}).get("question_asked"),
        "paper_ingested_monthly": await get_monthly_count(db, user.id, "paper_ingested"),
        "paper_ingested_limit": MONTHLY_LIMITS.get(plan, {}).get("paper_ingested"),
    }

    return UserResponse(
        id=str(user.id),
        email=user.email,
        name=user.name,
        avatar_url=user.avatar_url,
        plan=user.plan,
        interest_profile=user.interest_profile or {},
        onboarded_at=user.onboarded_at.isoformat() if hasattr(user.onboarded_at, "isoformat") else user.onboarded_at,
        created_at=user.created_at.isoformat() if hasattr(user.created_at, "isoformat") else user.created_at,
        usage=usage,
    )


@router.patch("/me", response_model=UserResponse)
async def update_current_user_profile(
    payload: UpdateUserRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    if payload.name is not None:
        user.name = payload.name
    if payload.interest_profile is not None:
        current_profile = user.interest_profile or {}
        current_profile.update(payload.interest_profile.model_dump())
        user.interest_profile = current_profile

    if isinstance(user, User):
        await db.commit()
        await db.refresh(user)

    plan = user.plan or "free"
    usage = {
        "artifact_created_monthly": await get_monthly_count(db, user.id, "artifact_created"),
        "artifact_created_limit": MONTHLY_LIMITS.get(plan, {}).get("artifact_created"),
        "question_asked_daily": await get_daily_count(db, user.id, "question_asked"),
        "question_asked_limit": DAILY_LIMITS.get(plan, {}).get("question_asked"),
        "paper_ingested_monthly": await get_monthly_count(db, user.id, "paper_ingested"),
        "paper_ingested_limit": MONTHLY_LIMITS.get(plan, {}).get("paper_ingested"),
    }

    return UserResponse(
        id=str(user.id),
        email=user.email,
        name=user.name,
        avatar_url=user.avatar_url,
        plan=user.plan,
        interest_profile=user.interest_profile or {},
        onboarded_at=user.onboarded_at.isoformat() if hasattr(user.onboarded_at, "isoformat") else user.onboarded_at,
        created_at=user.created_at.isoformat() if hasattr(user.created_at, "isoformat") else user.created_at,
        usage=usage,
    )
