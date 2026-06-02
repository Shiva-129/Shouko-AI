import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from core.database import get_db
from core.security import get_current_user
from models.user import User
from models.paper import Paper
from models.digest import DailyDigest
from pydantic import BaseModel
from services.digest_service import DigestService

router = APIRouter(prefix="/digests", tags=["Digests"])


class ScoredPaperDetail(BaseModel):
    paper_id: str
    score: int
    reason: str
    title: str
    abstract: str | None
    category: str | None
    authors: list[str] | None


class DailyDigestResponse(BaseModel):
    id: str
    date: str
    paper_count: int
    status: str
    papers: list[ScoredPaperDetail]
    created_at: str | None = None
    email_sent_at: str | None = None


class DigestListItem(BaseModel):
    id: str
    date: str
    paper_count: int
    status: str
    created_at: str | None = None


class DigestListResponse(BaseModel):
    digests: list[DigestListItem]
    total: int
    page: int
    page_size: int


@router.get("", response_model=DigestListResponse)
async def list_digests(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    offset = (page - 1) * page_size
    count_res = await db.execute(
        select(func.count(DailyDigest.id)).where(DailyDigest.user_id == user.id)
    )
    total = count_res.scalar() or 0

    res = await db.execute(
        select(DailyDigest)
        .where(DailyDigest.user_id == user.id)
        .order_by(DailyDigest.date.desc())
        .offset(offset)
        .limit(page_size)
    )
    digests = res.scalars().all()

    return DigestListResponse(
        digests=[
            DigestListItem(
                id=str(d.id),
                date=d.date.isoformat(),
                paper_count=d.paper_count,
                status=d.status,
                created_at=d.created_at.isoformat() if d.created_at else None,
            )
            for d in digests
        ],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.post("/trigger", status_code=201)
async def trigger_digest(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    today = datetime.date.today()
    existing_res = await db.execute(
        select(DailyDigest).where(
            DailyDigest.user_id == user.id,
            DailyDigest.date == today,
        )
    )
    if existing_res.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Digest already exists for today.")

    digest_service = DigestService(db)
    digest = await digest_service.compile_user_daily_digest(user.id, today)
    if not digest:
        raise HTTPException(status_code=500, detail="Failed to compile digest.")
    return await _get_digest(db, user.id, today)


@router.get("/today", response_model=DailyDigestResponse | None)
async def get_today_digest(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    today = datetime.date.today()
    return await _get_digest(db, user.id, today)


@router.get("/{date}", response_model=DailyDigestResponse | None)
async def get_digest_by_date(
    date: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    try:
        parsed = datetime.date.fromisoformat(date)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD.")
    return await _get_digest(db, user.id, parsed)


async def _get_digest(
    db: AsyncSession, user_id, date: datetime.date
) -> DailyDigestResponse | None:
    res = await db.execute(
        select(DailyDigest).where(
            DailyDigest.user_id == user_id,
            DailyDigest.date == date,
        )
    )
    digest = res.scalar_one_or_none()
    if not digest:
        raise HTTPException(status_code=404, detail="No digest found for this date.")

    paper_scores = digest.paper_scores or []
    paper_ids = [s.get("paper_id") for s in paper_scores if s.get("paper_id")]
    paper_map: dict[str, Paper] = {}
    if paper_ids:
        papers_res = await db.execute(select(Paper).where(Paper.id.in_(paper_ids)))
        for p in papers_res.scalars().all():
            paper_map[str(p.id)] = p

    papers = []
    for s in paper_scores:
        pid = s.get("paper_id", "")
        p = paper_map.get(pid)
        papers.append(ScoredPaperDetail(
            paper_id=pid,
            score=s.get("score", 0),
            reason=s.get("reason", ""),
            title=p.title if p else "Unknown Paper",
            abstract=p.abstract if p else None,
            category=p.categories[0] if (p and p.categories) else None,
            authors=p.authors if p and p.authors else None,
        ))

    return DailyDigestResponse(
        id=str(digest.id),
        date=digest.date.isoformat(),
        paper_count=digest.paper_count,
        status=digest.status,
        papers=papers,
        created_at=digest.created_at.isoformat() if digest.created_at else None,
        email_sent_at=digest.email_sent_at.isoformat() if digest.email_sent_at else None,
    )
