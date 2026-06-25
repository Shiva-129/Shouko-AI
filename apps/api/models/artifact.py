from decimal import Decimal
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Integer, DateTime, Numeric, ForeignKey, UniqueConstraint, CheckConstraint, ARRAY, func, text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from pgvector.sqlalchemy import Vector
from core.database import Base
import datetime
import uuid

class Artifact(Base):
    __tablename__ = "artifacts"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4,
        server_default=func.uuid_generate_v4()
    )
    
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        ForeignKey("users.id", ondelete="CASCADE"), 
        nullable=False
    )
    
    paper_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        ForeignKey("papers.id", ondelete="CASCADE"), 
        nullable=False
    )
    
    one_line_summary: Mapped[str | None] = mapped_column(String, nullable=True)
    summary: Mapped[str | None] = mapped_column(String, nullable=True)
    
    key_insights: Mapped[list] = mapped_column(
        JSONB, 
        nullable=False, 
        default=list,
        server_default=text("'[]'::jsonb")
    )
    
    auto_qa: Mapped[list] = mapped_column(
        JSONB, 
        nullable=False, 
        default=list,
        server_default=text("'[]'::jsonb")
    )
    
    suggested_experiments: Mapped[list] = mapped_column(
        JSONB, 
        nullable=False, 
        default=list,
        server_default=text("'[]'::jsonb")
    )
    
    related_paper_ids: Mapped[list[uuid.UUID]] = mapped_column(
        ARRAY(UUID(as_uuid=True)), 
        nullable=False, 
        default=list,
        server_default=text("'{}'::uuid[]")
    )
    
    # Vector column representing 2048-dimensional embeddings (nvidia/llama-nemotron-embed-vl-1b-v2)
    embedding = mapped_column(Vector(2048), nullable=True)
    
    status: Mapped[str] = mapped_column(
        String, 
        nullable=False, 
        default="queued",
        server_default="queued"
    )
    
    error_message: Mapped[str | None] = mapped_column(String, nullable=True)
    
    version: Mapped[int] = mapped_column(
        Integer, 
        nullable=False, 
        default=1,
        server_default="1"
    )
    
    generation_cost_usd: Mapped[Decimal | None] = mapped_column(
        Numeric(10, 6), 
        nullable=True
    )
    
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), 
        nullable=False, 
        default=lambda: datetime.datetime.now(datetime.timezone.utc),
        server_default=func.now()
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), 
        nullable=False, 
        default=lambda: datetime.datetime.now(datetime.timezone.utc),
        onupdate=lambda: datetime.datetime.now(datetime.timezone.utc),
        server_default=func.now()
    )

    __table_args__ = (
        UniqueConstraint("user_id", "paper_id", name="uq_user_paper_artifact"),
        CheckConstraint(
            status.in_(["queued", "ingesting", "generating", "ready", "partial", "failed"]), 
            name="check_artifact_status"
        ),
    )
