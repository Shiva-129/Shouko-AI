from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from models.usage import UsageEvent
from models.user import User
import datetime

MONTHLY_LIMITS: dict[str, dict[str, int]] = {
    "free": {"artifact_created": 5, "paper_ingested": 10, "question_asked": None},
    "pro": {"artifact_created": None, "paper_ingested": None, "question_asked": None},
    "team": {"artifact_created": None, "paper_ingested": None, "question_asked": None},
    "enterprise": {"artifact_created": None, "paper_ingested": None, "question_asked": None},
}

DAILY_LIMITS: dict[str, dict[str, int]] = {
    "free": {"question_asked": 20},
    "pro": {"question_asked": None},
    "team": {"question_asked": None},
    "enterprise": {"question_asked": None},
}


async def log_usage_event(db: AsyncSession, user_id: str, event_type: str, meta_data: dict | None = None) -> UsageEvent:
    event = UsageEvent(
        user_id=user_id,
        event_type=event_type,
        meta_data=meta_data or {},
    )
    db.add(event)
    await db.flush()
    return event


async def get_monthly_count(db: AsyncSession, user_id: str, event_type: str) -> int:
    start_of_month = datetime.datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    result = await db.execute(
        select(func.count(UsageEvent.id)).where(
            and_(
                UsageEvent.user_id == user_id,
                UsageEvent.event_type == event_type,
                UsageEvent.created_at >= start_of_month,
            )
        )
    )
    return result.scalar() or 0


async def get_daily_count(db: AsyncSession, user_id: str, event_type: str) -> int:
    start_of_day = datetime.datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    result = await db.execute(
        select(func.count(UsageEvent.id)).where(
            and_(
                UsageEvent.user_id == user_id,
                UsageEvent.event_type == event_type,
                UsageEvent.created_at >= start_of_day,
            )
        )
    )
    return result.scalar() or 0


async def check_usage_limit(
    db: AsyncSession, user: User, event_type: str
) -> tuple[bool, str | None]:
    plan = user.plan or "free"

    monthly_limit = MONTHLY_LIMITS.get(plan, {}).get(event_type)
    if monthly_limit is not None:
        monthly_count = await get_monthly_count(db, user.id, event_type)
        if monthly_count >= monthly_limit:
            return False, f"Monthly limit reached ({monthly_count}/{monthly_limit}). Upgrade to Pro for unlimited access."

    daily_limit = DAILY_LIMITS.get(plan, {}).get(event_type)
    if daily_limit is not None:
        daily_count = await get_daily_count(db, user.id, event_type)
        if daily_count >= daily_limit:
            return False, f"Daily limit reached ({daily_count}/{daily_limit}). Upgrade to Pro for unlimited access."

    return True, None
