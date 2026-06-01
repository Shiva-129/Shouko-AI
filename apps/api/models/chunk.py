from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Integer, ForeignKey, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from pgvector.sqlalchemy import Vector
from core.database import Base
import uuid

class PaperChunk(Base):
    __tablename__ = "paper_chunks"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4,
        server_default=func.uuid_generate_v4()
    )
    
    paper_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        ForeignKey("papers.id", ondelete="CASCADE"), 
        nullable=False
    )
    
    artifact_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), 
        ForeignKey("artifacts.id", ondelete="CASCADE"), 
        nullable=True
    )
    
    content: Mapped[str] = mapped_column(String, nullable=False)
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    section: Mapped[str | None] = mapped_column(String, nullable=True)
    page_number: Mapped[int | None] = mapped_column(Integer, nullable=True)
    token_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    
    # Embedding is required and is 1536-dimensional Vector
    embedding = mapped_column(Vector(1536), nullable=False)
    
    meta_data: Mapped[dict] = mapped_column(
        JSONB, 
        nullable=False, 
        default=dict,
        server_default="'{}'::jsonb"
    )
