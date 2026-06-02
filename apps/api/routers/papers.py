from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from core.dependencies import get_db
from core.security import get_current_user
from core.usage import log_usage_event, check_usage_limit
from core.rate_limit import RateLimit
from models.paper import Paper
from models.user import User
from services.ingestion_service import IngestionService
import uuid

router = APIRouter(
    prefix="/papers",
    tags=["Papers & Ingestion"]
)

class PaperIngestRequest(BaseModel):
    title: str = Field(..., description="The title of the academic paper")
    pdf_url: str = Field(..., description="Direct HTTPS link to the paper's PDF file")
    arxiv_id: str | None = Field(None, description="Optional ArXiv identifier")

class PaperIngestResponse(BaseModel):
    paper_id: str
    title: str
    pdf_url: str
    status: str
    chunks_count: int

@router.post("/ingest", response_model=PaperIngestResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(RateLimit(limit=10, window=60, name="paper_ingest"))])
async def ingest_paper_endpoint(
    payload: PaperIngestRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Trigger the PDF ingestion flow. 
    Registers the paper in the database if new, downloads it, segments it 
    into searchable chunks, and generates 1536-dimensional semantic search vectors.
    """
    try:
        allowed, msg = await check_usage_limit(db, user, "paper_ingested")
        if not allowed:
            raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=msg)

        # Check if paper with this PDF URL or ArXiv ID already exists
        query = select(Paper).where(Paper.pdf_url == payload.pdf_url)
        if payload.arxiv_id:
            query = query.or_(Paper.arxiv_id == payload.arxiv_id)
            
        result = await db.execute(query)
        paper = result.scalar_one_or_none()
        
        if not paper:
            # Create a new Paper record
            paper = Paper(
                title=payload.title,
                pdf_url=payload.pdf_url,
                arxiv_id=payload.arxiv_id,
                source="arxiv" if payload.arxiv_id else "manual"
            )
            db.add(paper)
            await db.flush()  # Populates paper.id without committing yet
            
        # Execute Ingestion flow
        ingestion_service = IngestionService()
        ingest_result = await ingestion_service.ingest_paper(db, paper.id, payload.pdf_url)
        
        await log_usage_event(db, user.id, "paper_ingested", {"paper_id": str(paper.id)})
        await db.commit()

        return PaperIngestResponse(
            paper_id=str(paper.id),
            title=paper.title,
            pdf_url=paper.pdf_url,
            status=ingest_result["status"],
            chunks_count=ingest_result["chunks_count"]
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to ingest paper PDF: {str(e)}"
        )
