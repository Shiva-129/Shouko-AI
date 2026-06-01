from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, DateTime, ForeignKey, CheckConstraint, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from core.database import Base
import datetime
import uuid

class Annotation(Base):
    __tablename__ = "annotations"

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
    
    type: Mapped[str] = mapped_column(String, nullable=False)
    content: Mapped[str] = mapped_column(String, nullable=False)
    
    meta_data: Mapped[dict] = mapped_column(
        JSONB, 
        nullable=False, 
        default=dict,
        server_default="'{}'::jsonb"
    )
    
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), 
        nullable=False, 
        default=datetime.datetime.utcnow,
        server_default=func.now()
    )

    __table_args__ = (
        CheckConstraint(
            type.in_(["note", "highlight", "experiment", "task", "link"]), 
            name="check_annotation_type"
        ),
    )
