from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Integer, DateTime, Date, ForeignKey, UniqueConstraint, CheckConstraint, func, text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from core.database import Base
import datetime
import uuid

class DailyDigest(Base):
    __tablename__ = "daily_digests"

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
    
    date: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    
    paper_scores: Mapped[list] = mapped_column(
        JSONB, 
        nullable=False, 
        default=list,
        server_default=text("'[]'::jsonb")
    )
    
    paper_count: Mapped[int] = mapped_column(
        Integer, 
        nullable=False, 
        default=0,
        server_default="0"
    )
    
    status: Mapped[str] = mapped_column(
        String, 
        nullable=False, 
        default="pending",
        server_default="pending"
    )
    
    email_sent_at: Mapped[datetime.datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), 
        nullable=False, 
        default=datetime.datetime.utcnow,
        server_default=func.now()
    )

    __table_args__ = (
        UniqueConstraint("user_id", "date", name="uq_user_date_digest"),
        CheckConstraint(
            status.in_(["pending", "ready", "sent", "skipped"]), 
            name="check_digest_status"
        ),
    )
