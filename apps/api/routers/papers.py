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
import asyncio
from services.ingestion_service import IngestionService

router = APIRouter(
    prefix="/papers",
    tags=["Papers & Ingestion"]
)

def sanitize_arxiv_id(val: str) -> str:
    val = val.strip()
    if "arxiv.org" in val:
        for marker in ("/abs/", "/pdf/"):
            if marker in val:
                val = val.split(marker)[-1]
                break
        if val.endswith(".pdf"):
            val = val[:-4]
    if val.lower().startswith("arxiv:"):
        val = val[6:]
    return val.strip()

class PaperIngestRequest(BaseModel):
    title: str | None = Field(None, description="The title of the academic paper")
    pdf_url: str | None = Field(None, description="Direct HTTPS link to the paper's PDF file")
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
    into searchable chunks, and generates 2048-dimensional semantic search vectors.
    """
    try:
        allowed, msg = await check_usage_limit(db, user, "paper_ingested")
        if not allowed:
            raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=msg)

        arxiv_id = payload.arxiv_id
        if arxiv_id:
            arxiv_id = sanitize_arxiv_id(arxiv_id)
        title = payload.title
        pdf_url = payload.pdf_url

        if arxiv_id and (not title or not pdf_url):
            import arxiv
            client = arxiv.Client()
            search = arxiv.Search(id_list=[arxiv_id])
            try:
                results = list(client.results(search))
                if not results:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"ArXiv paper {arxiv_id} not found")
                result = results[0]
                if not title:
                    title = result.title
                if not pdf_url:
                    pdf_url = result.pdf_url
            except Exception as e:
                if isinstance(e, HTTPException):
                    raise
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Failed to fetch metadata from ArXiv: {str(e)}")
        # Validate PDF URL scheme
        if pdf_url:
            if not pdf_url.startswith(("http://", "https://")):
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="PDF URL must use http or https scheme.")
            if len(pdf_url) > 2048:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="PDF URL exceeds maximum length.")

        if not title or not pdf_url:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Title and PDF URL are required (or a valid ArXiv ID)")

        # Check if paper with this PDF URL or ArXiv ID already exists
        from sqlalchemy import or_
        if arxiv_id:
            query = select(Paper).where(or_(Paper.pdf_url == pdf_url, Paper.arxiv_id == arxiv_id))
        else:
            query = select(Paper).where(Paper.pdf_url == pdf_url)
            
        result = await db.execute(query)
        paper = result.scalar_one_or_none()
        
        if not paper:
            # Create a new Paper record
            paper = Paper(
                title=title,
                pdf_url=pdf_url,
                arxiv_id=arxiv_id,
                source="arxiv" if arxiv_id else "manual"
            )
            db.add(paper)
            await db.flush()  # Populates paper.id without committing yet
            
        # Execute Ingestion flow
        ingestion_service = IngestionService()
        ingest_result = await ingestion_service.ingest_paper(db, paper.id, pdf_url, user_id=str(user.id))
        
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
    except (asyncio.CancelledError, KeyboardInterrupt):
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to ingest paper PDF: {str(e)}"
        )
