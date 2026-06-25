from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.chunk import PaperChunk
from services.embedding_service import EmbeddingService
from prompts.rag_qa import SYSTEM_PROMPT, build_user_prompt

class RAGService:
    def __init__(self):
        self.embedding_service = EmbeddingService()

    async def retrieve_context_chunks(self, db: AsyncSession, paper_id: str, query_text: str, limit: int = 5) -> list[dict]:
        """
        Retrieves the top N most semantically relevant text chunks for a query
        inside a specific paper using pgvector's cosine distance operator.
        """
        # 1. Embed the query text
        embeddings = await self.embedding_service.get_embeddings([query_text], input_type="query")
        query_embedding = embeddings[0]

        # 2. Perform pgvector similarity search
        # order_by chunk.embedding.cosine_distance
        stmt = (
            select(PaperChunk)
            .where(PaperChunk.paper_id == paper_id)
            .order_by(PaperChunk.embedding.cosine_distance(query_embedding))
            .limit(limit)
        )
        
        result = await db.execute(stmt)
        chunks = result.scalars().all()

        return [
            {
                "chunk_id": str(c.id),
                "content": c.content,
                "section": c.section or "body",
                "page_number": c.page_number or 1,
                "chunk_index": c.chunk_index
            }
            for c in chunks
        ]

    def compile_rag_prompt(self, query: str, context_chunks: list[dict], history: list[dict]) -> tuple[str, str]:
        """
        Assembles the system instruction and context-rich prompt for the LLM.
        """
        return SYSTEM_PROMPT, build_user_prompt(query, context_chunks, history)
