import pytest
from unittest.mock import AsyncMock, patch
from sqlalchemy import delete, select
from services.pdf_service import PDFService
from tests.conftest import test_sessionmaker
from models.paper import Paper
from models.artifact import Artifact

def test_pdf_chunking_logic():
    pdf_service = PDFService()
    pages = [
        {"page_number": 1, "text": "This is page one content. " * 50, "section": "Introduction"},
        {"page_number": 2, "text": "This is page two content. " * 50, "section": "Background"}
    ]
    chunks = pdf_service.chunk_text(pages, chunk_size=30, overlap=5)
    assert len(chunks) > 0
    assert "content" in chunks[0]
    assert "page_number" in chunks[0]
    assert "chunk_index" in chunks[0]

@pytest.mark.asyncio
async def test_paper_ingestion_endpoint(client, auth_headers):
    payload = {
        "title": "Attention Is All You Need",
        "pdf_url": "https://arxiv.org/pdf/1706.03762.pdf",
        "arxiv_id": "1706.03762"
    }
    
    mock_result = {"status": "success", "chunks_count": 12}
    try:
        with patch("routers.papers.IngestionService.ingest_paper", new_callable=AsyncMock) as mock_ingest, \
             patch("routers.papers.check_usage_limit", return_value=(True, None)):
            mock_ingest.return_value = mock_result
            
            response = await client.post("/papers/ingest", json=payload, headers=auth_headers)
            assert response.status_code == 201
            data = response.json()
            assert data["title"] == "Attention Is All You Need"
            assert data["chunks_count"] == 12
            assert data["status"] == "success"
    finally:
        async with test_sessionmaker() as session:
            res = await session.execute(select(Paper.id).where(Paper.pdf_url == payload["pdf_url"]))
            paper_ids = res.scalars().all()
            if paper_ids:
                await session.execute(delete(Artifact).where(Artifact.paper_id.in_(paper_ids)))
                await session.execute(delete(Paper).where(Paper.id.in_(paper_ids)))
                await session.commit()

def test_arxiv_id_sanitization_helper():
    from routers.papers import sanitize_arxiv_id
    assert sanitize_arxiv_id("  1706.03762  ") == "1706.03762"
    assert sanitize_arxiv_id("1706.03762v7") == "1706.03762v7"
    assert sanitize_arxiv_id("arxiv:1706.03762") == "1706.03762"
    assert sanitize_arxiv_id("arXiv:1706.03762") == "1706.03762"
    assert sanitize_arxiv_id("https://arxiv.org/abs/1706.03762") == "1706.03762"
    assert sanitize_arxiv_id("https://arxiv.org/pdf/1706.03762.pdf") == "1706.03762"
    assert sanitize_arxiv_id("http://arxiv.org/abs/math/0111084") == "math/0111084"

@pytest.mark.asyncio
async def test_paper_ingestion_endpoint_with_url(client, auth_headers):
    payload = {
        "title": "Attention Is All You Need",
        "pdf_url": "https://arxiv.org/pdf/1706.03762.pdf",
        "arxiv_id": "https://arxiv.org/abs/1706.03762"
    }
    
    mock_result = {"status": "success", "chunks_count": 12}
    try:
        with patch("routers.papers.IngestionService.ingest_paper", new_callable=AsyncMock) as mock_ingest, \
             patch("routers.papers.check_usage_limit", return_value=(True, None)):
            mock_ingest.return_value = mock_result
            
            response = await client.post("/papers/ingest", json=payload, headers=auth_headers)
            assert response.status_code == 201
            data = response.json()
            assert data["title"] == "Attention Is All You Need"
            assert data["chunks_count"] == 12
            assert data["status"] == "success"
    finally:
        async with test_sessionmaker() as session:
            res = await session.execute(select(Paper.id).where(Paper.pdf_url == payload["pdf_url"]))
            paper_ids = res.scalars().all()
            if paper_ids:
                await session.execute(delete(Artifact).where(Artifact.paper_id.in_(paper_ids)))
                await session.execute(delete(Paper).where(Paper.id.in_(paper_ids)))
                await session.commit()

