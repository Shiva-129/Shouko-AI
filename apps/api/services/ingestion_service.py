import httpx
import os
import tempfile
import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.paper import Paper
from models.chunk import PaperChunk
from services.pdf_service import PDFService
from services.embedding_service import EmbeddingService

class IngestionService:
    def __init__(self):
        self.pdf_service = PDFService()
        self.embedding_service = EmbeddingService()

    async def ingest_paper(self, db: AsyncSession, paper_id: str, pdf_url: str) -> dict:
        """
        Ingests a paper's PDF: downloads it, extracts text pages, chunks it,
        generates vector embeddings, and stores them in the database.
        """
        # 1. Fetch paper record
        result = await db.execute(select(Paper).where(Paper.id == paper_id))
        paper = result.scalar_one_or_none()
        if not paper:
            raise ValueError(f"Paper with ID {paper_id} not found in database.")

        # Create a workspace temp directory to keep downloads isolated
        temp_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scratch")
        os.makedirs(temp_dir, exist_ok=True)
        
        fd, temp_file_path = tempfile.mkstemp(suffix=".pdf", dir=temp_dir)
        os.close(fd)

        try:
            # 2. Download the PDF
            print(f"[IngestionService] Downloading PDF from {pdf_url}...")
            async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
                response = await client.get(pdf_url)
                response.raise_for_status()
                with open(temp_file_path, "wb") as f:
                    f.write(response.content)

            # 3. Extract text pages
            print(f"[IngestionService] Extracting text pages from PDF...")
            pages = self.pdf_service.extract_text_by_page(temp_file_path)
            
            # 4. Generate sliding chunks
            print(f"[IngestionService] Segmenting text into overlap-based chunks...")
            chunks_data = self.pdf_service.chunk_text(pages, chunk_size=512, overlap=50)
            
            if not chunks_data:
                raise ValueError("No text could be extracted or chunked from the PDF.")

            # 5. Batch embed chunks
            print(f"[IngestionService] Generating semantic embeddings for {len(chunks_data)} chunks...")
            chunk_contents = [c["content"] for c in chunks_data]
            embeddings = await self.embedding_service.get_embeddings(chunk_contents)

            # 6. Save chunks in the database
            print(f"[IngestionService] Registering chunks in database...")
            # Clean up old chunks if they existed
            await db.execute(
                db.delete(PaperChunk).where(PaperChunk.paper_id == paper.id)
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
            paper.pdf_processed_at = datetime.datetime.utcnow()
            
            # Commit the session transaction
            await db.commit()
            print(f"[IngestionService] Successfully completed ingestion for paper {paper.title}!")
            
            return {
                "status": "success",
                "chunks_count": len(db_chunks),
                "paper_title": paper.title
            }

        except Exception as e:
            await db.rollback()
            print(f"[IngestionService] Ingestion failed: {e}")
            raise e
            
        finally:
            # Clean up downloaded PDF file
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
