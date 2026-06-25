import pytest
import uuid
from sqlalchemy import delete, select
from unittest.mock import AsyncMock, patch
from tests.conftest import test_sessionmaker
from models.paper import Paper
from models.artifact import Artifact
from models.conversation import Conversation

@pytest.mark.asyncio
async def test_chat_sse_stream(client, auth_headers):
    
    paper_id = uuid.uuid4()
    artifact_id = uuid.uuid4()
    
    paper = Paper(
        id=paper_id,
        title="Attention Is All You Need",
        pdf_url="https://arxiv.org/pdf/1706.03762.pdf",
        authors=["Ashish Vaswani"]
    )
    
    artifact = Artifact(
        id=artifact_id,
        user_id=uuid.UUID("00000000-0000-0000-0000-000000000000"),
        paper_id=paper_id,
        status="ready"
    )

    # Commit paper first
    async with test_sessionmaker() as session:
        session.add(paper)
        await session.commit()

    # Commit artifact second
    async with test_sessionmaker() as session:
        session.add(artifact)
        await session.commit()

    payload = {"message": "How does self-attention scale?"}
    mock_chunks = [{"content": "self-attention scales quadratically with sequence length", "page_number": 4}]
    mock_prompts = ("system prompt", "user prompt")
    
    async def mock_stream(*args, **kwargs):
        yield "self-attention "
        yield "scales "
        yield "quadratically."

    try:
        with patch("routers.chat.RAGService.retrieve_context_chunks", new_callable=AsyncMock) as mock_retrieval, \
             patch("routers.chat.RAGService.compile_rag_prompt") as mock_compile, \
             patch("routers.chat.LLMService.stream_chat_response", side_effect=mock_stream) as mock_llm, \
             patch("routers.chat.check_usage_limit", return_value=(True, None)):
             
            mock_retrieval.return_value = mock_chunks
            mock_compile.return_value = mock_prompts
            
            response = await client.post(
                f"/conversations/{artifact_id}/chat",
                json=payload,
                headers=auth_headers
            )
            
            assert response.status_code == 200
            chunks = []
            async for line in response.aiter_lines():
                if line.strip():
                    chunks.append(line)
            
            assert len(chunks) > 0
            assert "data:" in chunks[0]
            assert "[DONE]" in chunks[-1]
    finally:
        async with test_sessionmaker() as session:
            await session.execute(delete(Conversation).where(Conversation.artifact_id == artifact_id))
            await session.execute(delete(Artifact).where(Artifact.id == artifact_id))
            await session.execute(delete(Paper).where(Paper.id == paper_id))
            await session.commit()
