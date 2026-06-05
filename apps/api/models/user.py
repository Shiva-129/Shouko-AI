from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, DateTime, func, CheckConstraint, text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from core.database import Base
import datetime
from uuid import UUID as PyUUID

class User(Base):
    __tablename__ = "users"

    id: Mapped[PyUUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    name: Mapped[str | None] = mapped_column(String, nullable=True)
    avatar_url: Mapped[str | None] = mapped_column(String, nullable=True)
    
    plan: Mapped[str] = mapped_column(
        String, 
        nullable=False, 
        default="free",
        server_default="free"
    )
    
    stripe_customer_id: Mapped[str | None] = mapped_column(String, unique=True, nullable=True)
    stripe_subscription_id: Mapped[str | None] = mapped_column(String, nullable=True)
    
    interest_profile: Mapped[dict] = mapped_column(
        JSONB, 
        nullable=False, 
        default=lambda: {"topics": [], "keywords": [], "authors": [], "categories": []},
        server_default=text("'{\"topics\": [], \"keywords\": [], \"authors\": [], \"categories\": []}'::jsonb")
    )
    
    onboarded_at: Mapped[datetime.datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
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
        CheckConstraint(plan.in_(["free", "pro", "team", "enterprise"]), name="check_plan_type"),
    )
