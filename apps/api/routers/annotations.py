from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from core.dependencies import get_db
from core.security import get_current_user
from models.annotation import Annotation
from models.artifact import Artifact
from models.user import User
import uuid
import datetime

router = APIRouter(
    prefix="/annotations",
    tags=["Annotations"]
)

class AnnotationCreate(BaseModel):
    artifact_id: str
    type: str = Field(..., description="Type of annotation: note, highlight, experiment, task, link")
    content: str = Field(..., description="The content text of the annotation")
    meta_data: dict = Field(default_factory=dict, description="Metadata dictionary for storing section, page, offsets, etc.")

class AnnotationUpdate(BaseModel):
    content: str | None = None
    meta_data: dict | None = None

class AnnotationResponse(BaseModel):
    id: str
    artifact_id: str
    user_id: str
    type: str
    content: str
    meta_data: dict
    created_at: str

@router.post("", response_model=AnnotationResponse, status_code=status.HTTP_201_CREATED)
async def create_annotation(
    payload: AnnotationCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Create a new annotation (note, highlight, link, task, experiment) for an artifact.
    """
    if payload.type not in ["note", "highlight", "experiment", "task", "link"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid annotation type")

    try:
        artifact_uuid = uuid.UUID(payload.artifact_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid artifact_id format")

    # Verify artifact exists
    artifact_res = await db.execute(select(Artifact).where(Artifact.id == artifact_uuid))
    artifact = artifact_res.scalar_one_or_none()
    if not artifact:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Artifact not found")

    annotation = Annotation(
        artifact_id=artifact_uuid,
        user_id=user.id,
        type=payload.type,
        content=payload.content,
        meta_data=payload.meta_data
    )
    db.add(annotation)
    await db.commit()
    await db.refresh(annotation)

    return AnnotationResponse(
        id=str(annotation.id),
        artifact_id=str(annotation.artifact_id),
        user_id=str(annotation.user_id),
        type=annotation.type,
        content=annotation.content,
        meta_data=annotation.meta_data,
        created_at=annotation.created_at.isoformat()
    )

@router.get("", response_model=list[AnnotationResponse])
async def list_annotations(
    artifact_id: str | None = Query(None, description="Optional filter by artifact ID"),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    List all annotations owned by the user, optionally filtered by artifact ID.
    """
    query = select(Annotation).where(Annotation.user_id == user.id)
    
    if artifact_id:
        try:
            artifact_uuid = uuid.UUID(artifact_id)
            query = query.where(Annotation.artifact_id == artifact_uuid)
        except ValueError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid artifact_id format")

    result = await db.execute(query.order_by(Annotation.created_at.desc()))
    annotations = result.scalars().all()

    return [
        AnnotationResponse(
            id=str(a.id),
            artifact_id=str(a.artifact_id),
            user_id=str(a.user_id),
            type=a.type,
            content=a.content,
            meta_data=a.meta_data,
            created_at=a.created_at.isoformat()
        )
        for a in annotations
    ]

@router.get("/{id}", response_model=AnnotationResponse)
async def get_annotation(
    id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Get details of a specific annotation.
    """
    try:
        annotation_uuid = uuid.UUID(id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid annotation ID format")

    result = await db.execute(select(Annotation).where(Annotation.id == annotation_uuid, Annotation.user_id == user.id))
    annotation = result.scalar_one_or_none()
    if not annotation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Annotation not found")

    return AnnotationResponse(
        id=str(annotation.id),
        artifact_id=str(annotation.artifact_id),
        user_id=str(annotation.user_id),
        type=annotation.type,
        content=annotation.content,
        meta_data=annotation.meta_data,
        created_at=annotation.created_at.isoformat()
    )

@router.put("/{id}", response_model=AnnotationResponse)
async def update_annotation(
    id: str,
    payload: AnnotationUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Update an annotation content or metadata.
    """
    try:
        annotation_uuid = uuid.UUID(id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid annotation ID format")

    result = await db.execute(select(Annotation).where(Annotation.id == annotation_uuid, Annotation.user_id == user.id))
    annotation = result.scalar_one_or_none()
    if not annotation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Annotation not found")

    if payload.content is not None:
        annotation.content = payload.content
    if payload.meta_data is not None:
        # Update existing metadata dict
        current_meta = dict(annotation.meta_data or {})
        current_meta.update(payload.meta_data)
        annotation.meta_data = current_meta

    await db.commit()
    await db.refresh(annotation)

    return AnnotationResponse(
        id=str(annotation.id),
        artifact_id=str(annotation.artifact_id),
        user_id=str(annotation.user_id),
        type=annotation.type,
        content=annotation.content,
        meta_data=annotation.meta_data,
        created_at=annotation.created_at.isoformat()
    )

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_annotation(
    id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Delete an annotation.
    """
    try:
        annotation_uuid = uuid.UUID(id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid annotation ID format")

    result = await db.execute(select(Annotation).where(Annotation.id == annotation_uuid, Annotation.user_id == user.id))
    annotation = result.scalar_one_or_none()
    if not annotation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Annotation not found")

    await db.delete(annotation)
    await db.commit()
