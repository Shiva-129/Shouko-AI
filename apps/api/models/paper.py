from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Integer, Boolean, DateTime, Date, func, CheckConstraint, ARRAY
from sqlalchemy.dialects.postgresql import JSONB, UUID
from core.database import Base
import datetime
import uuid

class Paper(Base):
    __tablename__ = "papers"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4,
        server_default=func.uuid_generate_v4()
    )
    
    arxiv_id: Mapped[str | None] = mapped_column(String, unique=True, nullable=True)
    semantic_scholar_id: Mapped[str | None] = mapped_column(String, unique=True, nullable=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    abstract: Mapped[str | None] = mapped_column(String, nullable=True)
    
    authors: Mapped[list] = mapped_column(
        JSONB, 
        nullable=False, 
        default=list,
        server_default="'[]'::jsonb"
    )
    
    categories: Mapped[list[str]] = mapped_column(
        ARRAY(String), 
        nullable=False, 
        default=list,
        server_default="'{}'::text[]"
    )
    
    published_date: Mapped[datetime.date | None] = mapped_column(Date, nullable=True)
    updated_date: Mapped[datetime.date | None] = mapped_column(Date, nullable=True)
    
    pdf_url: Mapped[str] = mapped_column(String, nullable=False)
    pdf_storage_path: Mapped[str | None] = mapped_column(String, nullable=True)
    
    source: Mapped[str] = mapped_column(
        String, 
        nullable=False, 
        default="arxiv",
        server_default="arxiv"
    )
    
    citation_count: Mapped[int] = mapped_column(
        Integer, 
        nullable=False, 
        default=0,
        server_default="0"
    )
    
    meta_data: Mapped[dict] = mapped_column(
        JSONB, 
        nullable=False, 
        default=dict,
        server_default="'{}'::jsonb"
    )
    
    pdf_processed: Mapped[bool] = mapped_column(
        Boolean, 
        nullable=False, 
        default=False,
        server_default="false"
    )
    
    pdf_processed_at: Mapped[datetime.datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), 
        nullable=False, 
        default=datetime.datetime.utcnow,
        server_default=func.now()
    )

    __table_args__ = (
        CheckConstraint(source.in_(["arxiv", "semantic_scholar", "pubmed", "manual"]), name="check_paper_source"),
    )
