from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, DateTime, ForeignKey, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from core.database import Base
import datetime
import uuid

class Conversation(Base):
    __tablename__ = "conversations"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4,
        server_default=func.uuid_generate_v4()
    )
    
    artifact_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        ForeignKey("artifacts.id", ondelete="CASCADE"), 
        nullable=False
    )
    
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        ForeignKey("users.id", ondelete="CASCADE"), 
        nullable=False
    )
    
    messages: Mapped[list] = mapped_column(
        JSONB, 
        nullable=False, 
        default=list,
        server_default="'[]'::jsonb"
    )
    
    message_count: Mapped[int] = mapped_column(
        Integer, 
        nullable=False, 
        default=0,
        server_default="0"
    )
    
    total_tokens_used: Mapped[int] = mapped_column(
        Integer, 
        nullable=False, 
        default=0,
        server_default="0"
    )
    
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), 
        nullable=False, 
        default=datetime.datetime.utcnow,
        server_default=func.now()
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), 
        nullable=False, 
        default=datetime.datetime.utcnow,
        onupdate=datetime.datetime.utcnow,
        server_default=func.now()
    )

    __table_args__ = (
        UniqueConstraint("artifact_id", "user_id", name="uq_artifact_user_conversation"),
    )
