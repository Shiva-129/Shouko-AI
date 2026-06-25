from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from core.dependencies import get_db
from core.security import get_current_user
from models.collection import Collection
from models.artifact import Artifact
from models.user import User
from models.paper import Paper
import uuid

router = APIRouter(
    prefix="/collections",
    tags=["Collections"]
)

class CollectionCreate(BaseModel):
    name: str = Field(..., max_length=100)
    description: str | None = Field(None, max_length=500)
    color: str = Field("#3B82F6", max_length=7)

class CollectionUpdate(BaseModel):
    name: str | None = Field(None, max_length=100)
    description: str | None = Field(None, max_length=500)
    color: str | None = Field(None, max_length=7)

class AddArtifactRequest(BaseModel):
    artifact_id: str

class CollectionResponse(BaseModel):
    id: str
    name: str
    description: str | None
    color: str
    artifact_ids: list[str]
    is_default: bool
    created_at: str
    updated_at: str

class CollectionDetailResponse(BaseModel):
    id: str
    name: str
    description: str | None
    color: str
    is_default: bool
    artifacts: list[dict]
    created_at: str
    updated_at: str


@router.get("", response_model=list[CollectionResponse])
async def list_collections(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Collection).where(Collection.user_id == user.id)
        .order_by(Collection.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    collections = result.scalars().all()
    return [
        CollectionResponse(
            id=str(c.id),
            name=c.name,
            description=c.description,
            color=c.color,
            artifact_ids=[str(aid) for aid in c.artifact_ids] if c.artifact_ids else [],
            is_default=c.is_default,
            created_at=c.created_at.isoformat(),
            updated_at=c.updated_at.isoformat(),
        )
        for c in collections
    ]


@router.post("", response_model=CollectionResponse, status_code=status.HTTP_201_CREATED)
async def create_collection(
    payload: CollectionCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Create a new custom collection.
    """
    collection = Collection(
        user_id=user.id,
        name=payload.name,
        description=payload.description,
        color=payload.color,
        artifact_ids=[],
        is_default=False
    )
    db.add(collection)
    await db.commit()
    await db.refresh(collection)
    return CollectionResponse(
        id=str(collection.id),
        name=collection.name,
        description=collection.description,
        color=collection.color,
        artifact_ids=[],
        is_default=collection.is_default,
        created_at=collection.created_at.isoformat(),
        updated_at=collection.updated_at.isoformat(),
    )


@router.get("/{collection_id}", response_model=CollectionDetailResponse)
async def get_collection(
    collection_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Retrieve a single collection along with details of all its grouped artifacts.
    """
    result = await db.execute(
        select(Collection).where(Collection.id == collection_id, Collection.user_id == user.id)
    )
    collection = result.scalar_one_or_none()
    if not collection:
        raise HTTPException(status_code=404, detail="Collection not found")

    artifacts_list = []
    if collection.artifact_ids:
        # Load the details of the artifacts and corresponding papers
        art_result = await db.execute(
            select(Artifact).where(Artifact.id.in_(collection.artifact_ids))
        )
        artifacts = art_result.scalars().all()
        
        paper_ids = [a.paper_id for a in artifacts]
        paper_map = {}
        if paper_ids:
            paper_res = await db.execute(select(Paper).where(Paper.id.in_(paper_ids)))
            for p in paper_res.scalars().all():
                paper_map[str(p.id)] = p

        for a in artifacts:
            paper = paper_map.get(str(a.paper_id))
            artifacts_list.append({
                "id": str(a.id),
                "paper_id": str(a.paper_id),
                "paper_title": paper.title if paper else None,
                "one_line_summary": a.one_line_summary,
                "status": a.status,
                "created_at": a.created_at.isoformat() if a.created_at else None,
            })

    return CollectionDetailResponse(
        id=str(collection.id),
        name=collection.name,
        description=collection.description,
        color=collection.color,
        is_default=collection.is_default,
        artifacts=artifacts_list,
        created_at=collection.created_at.isoformat(),
        updated_at=collection.updated_at.isoformat(),
    )


@router.put("/{collection_id}", response_model=CollectionResponse)
async def update_collection(
    collection_id: uuid.UUID,
    payload: CollectionUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Update a collection's name, description, or color.
    """
    result = await db.execute(
        select(Collection).where(Collection.id == collection_id, Collection.user_id == user.id)
    )
    collection = result.scalar_one_or_none()
    if not collection:
        raise HTTPException(status_code=404, detail="Collection not found")

    if payload.name is not None:
        collection.name = payload.name
    if payload.description is not None:
        collection.description = payload.description
    if payload.color is not None:
        collection.color = payload.color

    db.add(collection)
    await db.commit()
    await db.refresh(collection)

    return CollectionResponse(
        id=str(collection.id),
        name=collection.name,
        description=collection.description,
        color=collection.color,
        artifact_ids=[str(aid) for aid in collection.artifact_ids] if collection.artifact_ids else [],
        is_default=collection.is_default,
        created_at=collection.created_at.isoformat(),
        updated_at=collection.updated_at.isoformat(),
    )


@router.delete("/{collection_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_collection(
    collection_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Delete a collection.
    """
    result = await db.execute(
        select(Collection).where(Collection.id == collection_id, Collection.user_id == user.id)
    )
    collection = result.scalar_one_or_none()
    if not collection:
        raise HTTPException(status_code=404, detail="Collection not found")

    await db.delete(collection)
    await db.commit()


@router.post("/{collection_id}/artifacts", response_model=CollectionResponse)
async def add_artifact_to_collection(
    collection_id: uuid.UUID,
    payload: AddArtifactRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Add an artifact to a collection.
    """
    result = await db.execute(
        select(Collection).where(Collection.id == collection_id, Collection.user_id == user.id)
    )
    collection = result.scalar_one_or_none()
    if not collection:
        raise HTTPException(status_code=404, detail="Collection not found")

    try:
        art_uuid = uuid.UUID(payload.artifact_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid artifact ID format")

    art_check = await db.execute(
        select(Artifact).where(Artifact.id == art_uuid, Artifact.user_id == user.id)
    )
    artifact = art_check.scalar_one_or_none()
    if not artifact:
        raise HTTPException(status_code=404, detail="Artifact not found or unauthorized")

    # Add to list if not already present
    current_ids = list(collection.artifact_ids) if collection.artifact_ids else []
    if art_uuid not in current_ids:
        current_ids.append(art_uuid)
        collection.artifact_ids = current_ids
        db.add(collection)
        await db.commit()
        await db.refresh(collection)

    return CollectionResponse(
        id=str(collection.id),
        name=collection.name,
        description=collection.description,
        color=collection.color,
        artifact_ids=[str(aid) for aid in collection.artifact_ids],
        is_default=collection.is_default,
        created_at=collection.created_at.isoformat(),
        updated_at=collection.updated_at.isoformat(),
    )


@router.delete("/{collection_id}/artifacts/{artifact_id}", response_model=CollectionResponse)
async def remove_artifact_from_collection(
    collection_id: uuid.UUID,
    artifact_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Remove an artifact from a collection.
    """
    result = await db.execute(
        select(Collection).where(Collection.id == collection_id, Collection.user_id == user.id)
    )
    collection = result.scalar_one_or_none()
    if not collection:
        raise HTTPException(status_code=404, detail="Collection not found")

    current_ids = list(collection.artifact_ids) if collection.artifact_ids else []
    if artifact_id in current_ids:
        current_ids.remove(artifact_id)
        collection.artifact_ids = current_ids
        db.add(collection)
        await db.commit()
        await db.refresh(collection)

    return CollectionResponse(
        id=str(collection.id),
        name=collection.name,
        description=collection.description,
        color=collection.color,
        artifact_ids=[str(aid) for aid in collection.artifact_ids],
        is_default=collection.is_default,
        created_at=collection.created_at.isoformat(),
        updated_at=collection.updated_at.isoformat(),
    )
