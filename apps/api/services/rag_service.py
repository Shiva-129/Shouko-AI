from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.chunk import PaperChunk
from services.embedding_service import EmbeddingService

class RAGService:
    def __init__(self):
        self.embedding_service = EmbeddingService()

    async def retrieve_context_chunks(self, db: AsyncSession, paper_id: str, query_text: str, limit: int = 5) -> list[dict]:
        """
        Retrieves the top N most semantically relevant text chunks for a query
        inside a specific paper using pgvector's cosine distance operator.
        """
        # 1. Embed the query text
        embeddings = await self.embedding_service.get_embeddings([query_text])
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
        system_prompt = (
            "You are PaperBrain-AI, a world-class academic research intelligence assistant.\n"
            "Your objective is to provide highly precise, technical, and scientifically accurate answers "
            "based strictly on the extracted context chunks of the academic paper provided.\n\n"
            "Rules:\n"
            "1. Ground your answers thoroughly in the provided text snippets.\n"
            "2. If the context does not contain enough information to answer a question, state this clearly while providing "
            "related context about the scientific domain if available.\n"
            "3. Use LaTeX formatting for mathematical expressions where appropriate (e.g. $E = mc^2$ or $$E=mc^2$$)."
        )

        # Build context string
        context_str = ""
        for i, c in enumerate(context_chunks):
            context_str += f"--- CONTEXT CHUNK #{i+1} (Page {c['page_number']}, Section: {c['section']}) ---\n"
            context_str += f"{c['content']}\n\n"

        # Build history log
        history_str = ""
        for msg in history[-6:]:  # Keep last 6 interactions
            role_label = "User" if msg["role"] == "user" else "Assistant"
            history_str += f"{role_label}: {msg['content']}\n"

        user_prompt = (
            f"Here is the context extracted from the academic paper:\n\n"
            f"{context_str}"
            f"Here is our recent conversation history:\n"
            f"{history_str}\n"
            f"Current Question: {query}\n\n"
            f"Provide a structured, deep academic answer:"
        )

        return system_prompt, user_prompt
