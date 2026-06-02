from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from core.dependencies import get_db
from core.security import get_current_user
from core.usage import log_usage_event, check_usage_limit
from core.rate_limit import RateLimit
from models.artifact import Artifact
from models.conversation import Conversation
from models.user import User
from services.rag_service import RAGService
from services.llm_service import LLMService
import json
import uuid

router = APIRouter(
    prefix="/conversations",
    tags=["Conversational Chat"]
)

class ChatRequest(BaseModel):
    message: str = Field(..., description="The user's query or question about the paper")

@router.post("/{artifact_id}/chat", dependencies=[Depends(RateLimit(limit=20, window=60, name="chat"))])
async def chat_sse_endpoint(
    artifact_id: str,
    payload: ChatRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Submit a technical question about a paper artifact. 
    Queries pgvector, builds system instructions, and streams the answer 
    token-by-token using Server-Sent Events (SSE).
    """
    try:
        artifact_uuid = uuid.UUID(artifact_id)
        result = await db.execute(
            select(Artifact).where(Artifact.id == artifact_uuid, Artifact.user_id == user.id)
        )
        artifact = result.scalar_one_or_none()
        
        if not artifact:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Artifact with ID {artifact_id} not found."
            )

        allowed, msg = await check_usage_limit(db, user, "question_asked")
        if not allowed:
            raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=msg)

        # 2. Retrieve or create conversation record
        conv_result = await db.execute(
            select(Conversation).where(
                Conversation.artifact_id == artifact.id,
                Conversation.user_id == user.id
            )
        )
        conversation = conv_result.scalar_one_or_none()

        if not conversation:
            conversation = Conversation(
                artifact_id=artifact.id,
                user_id=user.id,
                messages=[]
            )
            db.add(conversation)
            await db.flush()

        # Load history
        history = list(conversation.messages) if conversation.messages else []

        # 3. Instantiate services
        rag_service = RAGService()
        llm_service = LLMService()

        # 4. Define SSE stream generator
        async def event_generator():
            try:
                # A. Retrieve relevant paper chunks
                context_chunks = await rag_service.retrieve_context_chunks(
                    db=db,
                    paper_id=artifact.paper_id,
                    query_text=payload.message
                )

                # B. Compile history and prompts
                system_prompt, user_prompt = rag_service.compile_rag_prompt(
                    query=payload.message,
                    context_chunks=context_chunks,
                    history=history
                )

                # C. Stream LLM tokens
                full_response = ""
                async for token in llm_service.stream_chat_response(
                    system_prompt=system_prompt,
                    prompt=user_prompt,
                    context_chunks=context_chunks
                ):
                    full_response += token
                    # SSE standard format: "data: <content>\n\n"
                    yield f"data: {json.dumps({'token': token})}\n\n"

                # D. Update database conversation logs
                updated_history = list(history)
                updated_history.append({"role": "user", "content": payload.message})
                updated_history.append({"role": "assistant", "content": full_response})
                
                await log_usage_event(db, user.id, "question_asked", {"artifact_id": artifact_id})

                conversation.messages = updated_history
                conversation.message_count = len(updated_history)
                await db.commit()

                yield "data: [DONE]\n\n"

            except Exception as inner_e:
                print(f"[SSE Stream Error] {inner_e}")
                yield f"data: {json.dumps({'error': str(inner_e)})}\n\n"

        return StreamingResponse(
            event_generator(),
            media_type="text/event-stream"
        )

    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid UUID format for artifact_id."
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Chat execution failed: {str(e)}"
        )
