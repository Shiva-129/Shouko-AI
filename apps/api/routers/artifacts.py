from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from core.database import get_db
from core.security import get_current_user
from core.usage import check_usage_limit, log_usage_event
from core.rate_limit import RateLimit
from models.artifact import Artifact
from models.paper import Paper
from models.user import User
from tasks.generate_artifact import generate_artifact
import uuid

router = APIRouter(
    prefix="/artifacts",
    tags=["Artifacts"],
)


class CreateArtifactRequest(BaseModel):
    paper_id: str
    title: str | None = None


class ArtifactResponse(BaseModel):
    id: str
    paper_id: str
    paper_title: str | None = None
    one_line_summary: str | None = None
    summary: str | None = None
    key_insights: list = []
    auto_qa: list = []
    suggested_experiments: list = []
    status: str
    error_message: str | None = None
    generation_cost_usd: float | None = None
    created_at: str | None = None
    updated_at: str | None = None


class ArtifactListItem(BaseModel):
    id: str
    paper_id: str
    paper_title: str | None = None
    one_line_summary: str | None = None
    status: str
    created_at: str | None = None


class ArtifactListResponse(BaseModel):
    artifacts: list[ArtifactListItem]
    total: int


class ArtifactStatusResponse(BaseModel):
    id: str
    status: str
    error_message: str | None = None


@router.get("", response_model=ArtifactListResponse)
async def list_artifacts(
    search: str = Query("", max_length=200),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    query = select(Artifact).where(Artifact.user_id == user.id)

    count_query = select(func.count(Artifact.id)).where(Artifact.user_id == user.id)

    if search:
        paper_ids_subq = select(Paper.id).where(Paper.title.ilike(f"%{search}%"))
        query = query.where(Artifact.paper_id.in_(paper_ids_subq))
        count_query = count_query.where(Artifact.paper_id.in_(paper_ids_subq))

    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    result = await db.execute(
        query.order_by(Artifact.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    artifacts = result.scalars().all()

    paper_ids = [a.paper_id for a in artifacts]
    paper_map: dict[str, Paper] = {}
    if paper_ids:
        paper_res = await db.execute(select(Paper).where(Paper.id.in_(paper_ids)))
        for p in paper_res.scalars().all():
            paper_map[str(p.id)] = p

    return ArtifactListResponse(
        artifacts=[
            ArtifactListItem(
                id=str(a.id),
                paper_id=str(a.paper_id),
                paper_title=paper_map.get(str(a.paper_id), {}).title if isinstance(paper_map.get(str(a.paper_id)), Paper) else getattr(paper_map.get(str(a.paper_id)), 'title', None),
                one_line_summary=a.one_line_summary,
                status=a.status,
                created_at=a.created_at.isoformat() if a.created_at else None,
            )
            for a in artifacts
        ],
        total=total,
    )


@router.get("/{artifact_id}", response_model=ArtifactResponse)
async def get_artifact(
    artifact_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Artifact).where(Artifact.id == artifact_id, Artifact.user_id == user.id)
    )
    artifact = result.scalar_one_or_none()
    if not artifact:
        raise HTTPException(status_code=404, detail="Artifact not found")

    paper_result = await db.execute(select(Paper).where(Paper.id == artifact.paper_id))
    paper = paper_result.scalar_one_or_none()

    return ArtifactResponse(
        id=str(artifact.id),
        paper_id=str(artifact.paper_id),
        paper_title=paper.title if paper else None,
        one_line_summary=artifact.one_line_summary,
        summary=artifact.summary,
        key_insights=artifact.key_insights or [],
        auto_qa=artifact.auto_qa or [],
        suggested_experiments=artifact.suggested_experiments or [],
        status=artifact.status,
        error_message=artifact.error_message,
        generation_cost_usd=float(artifact.generation_cost_usd) if artifact.generation_cost_usd else None,
        created_at=artifact.created_at.isoformat() if artifact.created_at else None,
        updated_at=artifact.updated_at.isoformat() if artifact.updated_at else None,
    )


@router.get("/{artifact_id}/status", response_model=ArtifactStatusResponse)
async def get_artifact_status(
    artifact_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Artifact).where(Artifact.id == artifact_id, Artifact.user_id == user.id)
    )
    artifact = result.scalar_one_or_none()
    if not artifact:
        raise HTTPException(status_code=404, detail="Artifact not found")

    return ArtifactStatusResponse(
        id=str(artifact.id),
        status=artifact.status,
        error_message=artifact.error_message,
    )


@router.post("", response_model=ArtifactResponse, status_code=201, dependencies=[Depends(RateLimit(limit=5, window=60, name="create_artifact"))])
async def create_artifact(
    req: CreateArtifactRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    allowed, msg = await check_usage_limit(db, user, "artifact_created")
    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=msg,
        )

    paper_result = await db.execute(select(Paper).where(Paper.id == req.paper_id))
    paper = paper_result.scalar_one_or_none()
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")

    existing = await db.execute(
        select(Artifact).where(
            Artifact.user_id == user.id,
            Artifact.paper_id == req.paper_id,
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=409,
            detail="Artifact already exists for this paper. Use GET /artifacts to find it.",
        )

    artifact = Artifact(
        user_id=user.id,
        paper_id=req.paper_id,
        status="queued",
    )
    db.add(artifact)
    await db.commit()
    await db.refresh(artifact)

    generate_artifact.delay(
        paper_id=str(req.paper_id),
        artifact_id=str(artifact.id),
        user_id=str(user.id),
    )

    return ArtifactResponse(
        id=str(artifact.id),
        paper_id=str(artifact.paper_id),
        paper_title=paper.title,
        status=artifact.status,
        created_at=artifact.created_at.isoformat() if artifact.created_at else None,
    )


@router.delete("/{artifact_id}", status_code=204)
async def delete_artifact(
    artifact_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Artifact).where(Artifact.id == artifact_id, Artifact.user_id == user.id)
    )
    artifact = result.scalar_one_or_none()
    if not artifact:
        raise HTTPException(status_code=404, detail="Artifact not found")

    await db.delete(artifact)
    await db.commit()
