import httpx
import os
import tempfile
import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from models.paper import Paper
from models.chunk import PaperChunk
from services.pdf_service import PDFService
from services.embedding_service import EmbeddingService
from services.storage_service import storage_service
import logging
logger = logging.getLogger("services.ingestion_service")

class IngestionService:
    def __init__(self):
        self.pdf_service = PDFService()
        self.embedding_service = EmbeddingService()

    async def ingest_paper(self, db: AsyncSession, paper_id: str, pdf_url: str, user_id: str | None = None) -> dict:
        """
        Ingests a paper's PDF: downloads it, extracts text pages, chunks it,
        generates vector embeddings, and stores them in the database.
        """
        # 1. Fetch paper record
        result = await db.execute(select(Paper).where(Paper.id == paper_id))
        paper = result.scalar_one_or_none()
        if not paper:
            raise ValueError(f"Paper with ID {paper_id} not found in database.")

        # Use storage service for temp download (local dev uses scratch dir, production uses R2)
        fd, temp_file_path = tempfile.mkstemp(suffix=".pdf")
        os.close(fd)

        try:
            # 2. Download the PDF
            logger.info(f"[IngestionService] Downloading PDF from {pdf_url}...")
            async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
                response = await client.get(pdf_url)
                response.raise_for_status()
                pdf_bytes = response.content

            # 2b. Store PDF in persistent storage (Supabase Storage or local)
            storage_key = f"papers/{user_id or 'anonymous'}/{paper_id}.pdf"
            pdf_storage_url = await storage_service.upload(
                key=storage_key,
                data=pdf_bytes,
                content_type="application/pdf",
            )
            paper.pdf_storage_path = pdf_storage_url

            # Save PDF to temp file for processing
            with open(temp_file_path, "wb") as f:
                f.write(pdf_bytes)

            # 3. Extract text pages
            logger.info(f"[IngestionService] Extracting text pages from PDF...")
            pages = self.pdf_service.extract_text_by_page(temp_file_path)
            
            # 4. Generate sliding chunks
            logger.info(f"[IngestionService] Segmenting text into overlap-based chunks...")
            chunks_data = self.pdf_service.chunk_text(pages, chunk_size=512, overlap=50)
            
            if not chunks_data:
                raise ValueError("No text could be extracted or chunked from the PDF.")

            # 5. Batch embed chunks
            logger.info(f"[IngestionService] Generating semantic embeddings for {len(chunks_data)} chunks...")
            chunk_contents = [c["content"] for c in chunks_data]
            embeddings = await self.embedding_service.get_embeddings(chunk_contents)

            # 6. Save chunks in the database
            logger.info(f"[IngestionService] Registering chunks in database...")
            # Clean up old chunks if they existed
            await db.execute(
                delete(PaperChunk).where(PaperChunk.paper_id == paper.id)
            )

            db_chunks = []
            for i, c in enumerate(chunks_data):
                db_chunk = PaperChunk(
                    paper_id=paper.id,
                    content=c["content"],
                    chunk_index=c["chunk_index"],
                    section=c["section"],
                    page_number=c["page_number"],
                    token_count=c["token_count"],
                    embedding=embeddings[i]
                )
                db.add(db_chunk)
                db_chunks.append(db_chunk)

            # 7. Update paper processing state
            paper.pdf_processed = True
            paper.pdf_processed_at = datetime.datetime.now(datetime.timezone.utc)
            
            # Commit the session transaction
            await db.commit()
            logger.info(f"[IngestionService] Successfully completed ingestion for paper {paper.title}!")
            
            return {
                "status": "success",
                "chunks_count": len(db_chunks),
                "paper_title": paper.title
            }

        except Exception as e:
            await db.rollback()
            logger.info(f"[IngestionService] Ingestion failed: {e}")
            raise e
            
        finally:
            # Clean up downloaded PDF file
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
