"""initial_schema

Revision ID: 0001
Revises:
Create Date: 2026-06-02
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    op.create_table(
        "users",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("email", sa.String(), unique=True, nullable=False),
        sa.Column("name", sa.String(), nullable=True),
        sa.Column("avatar_url", sa.String(), nullable=True),
        sa.Column("plan", sa.String(), nullable=False, server_default=sa.text("'free'")),
        sa.Column("stripe_customer_id", sa.String(), unique=True, nullable=True),
        sa.Column("stripe_subscription_id", sa.String(), nullable=True),
        sa.Column("interest_profile", JSONB, nullable=False, server_default=sa.text("'{\"topics\": [], \"keywords\": [], \"authors\": [], \"categories\": []}'::jsonb")),
        sa.Column("onboarded_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("plan IN ('free', 'pro', 'team', 'enterprise')", name="check_plan_type"),
    )

    op.create_table(
        "papers",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.func.uuid_generate_v4()),
        sa.Column("arxiv_id", sa.String(), unique=True, nullable=True),
        sa.Column("semantic_scholar_id", sa.String(), unique=True, nullable=True),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("abstract", sa.String(), nullable=True),
        sa.Column("authors", JSONB, nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("categories", ARRAY(sa.String()), nullable=False, server_default=sa.text("'{}'::text[]")),
        sa.Column("published_date", sa.Date(), nullable=True),
        sa.Column("updated_date", sa.Date(), nullable=True),
        sa.Column("pdf_url", sa.String(), nullable=False),
        sa.Column("pdf_storage_path", sa.String(), nullable=True),
        sa.Column("source", sa.String(), nullable=False, server_default=sa.text("'arxiv'")),
        sa.Column("citation_count", sa.Integer(), nullable=False, server_default=sa.text("'0'")),
        sa.Column("pdf_processed", sa.Boolean(), nullable=False, server_default=sa.text("'false'")),
        sa.Column("pdf_processed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        "artifacts",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.func.uuid_generate_v4()),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("paper_id", UUID(as_uuid=True), sa.ForeignKey("papers.id"), nullable=False),
        sa.Column("one_line_summary", sa.String(), nullable=True),
        sa.Column("summary", sa.String(), nullable=True),
        sa.Column("key_insights", JSONB, nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("auto_qa", JSONB, nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("suggested_experiments", JSONB, nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("related_paper_ids", ARRAY(UUID(as_uuid=True)), nullable=False, server_default=sa.text("'{}'::uuid[]")),
        sa.Column("embedding", Vector(1536), nullable=True),
        sa.Column("status", sa.String(), nullable=False, server_default=sa.text("'queued'")),
        sa.Column("error_message", sa.String(), nullable=True),
        sa.Column("version", sa.Integer(), nullable=False, server_default=sa.text("'1'")),
        sa.Column("generation_cost_usd", sa.Numeric(10, 6), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("user_id", "paper_id", name="uq_user_paper_artifact"),
        sa.CheckConstraint("status IN ('queued', 'ingesting', 'generating', 'ready', 'partial', 'failed')", name="check_artifact_status"),
    )

    op.create_table(
        "paper_chunks",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.func.uuid_generate_v4()),
        sa.Column("paper_id", UUID(as_uuid=True), sa.ForeignKey("papers.id", ondelete="CASCADE"), nullable=False),
        sa.Column("artifact_id", UUID(as_uuid=True), sa.ForeignKey("artifacts.id", ondelete="CASCADE"), nullable=True),
        sa.Column("content", sa.String(), nullable=False),
        sa.Column("chunk_index", sa.Integer(), nullable=False),
        sa.Column("section", sa.String(), nullable=True),
        sa.Column("page_number", sa.Integer(), nullable=True),
        sa.Column("token_count", sa.Integer(), nullable=True),
        sa.Column("embedding", Vector(1536), nullable=False),
        sa.Column("meta_data", JSONB, nullable=False, server_default=sa.text("'{}'::jsonb")),
    )

    op.create_table(
        "conversations",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.func.uuid_generate_v4()),
        sa.Column("artifact_id", UUID(as_uuid=True), sa.ForeignKey("artifacts.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("messages", JSONB, nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("message_count", sa.Integer(), nullable=False, server_default=sa.text("'0'")),
        sa.Column("total_tokens_used", sa.Integer(), nullable=False, server_default=sa.text("'0'")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("artifact_id", "user_id", name="uq_artifact_user_conversation"),
    )

    op.create_table(
        "annotations",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.func.uuid_generate_v4()),
        sa.Column("artifact_id", UUID(as_uuid=True), sa.ForeignKey("artifacts.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("type", sa.String(), nullable=False),
        sa.Column("content", sa.String(), nullable=False),
        sa.Column("meta_data", JSONB, nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("type IN ('note', 'highlight', 'experiment', 'task', 'link')", name="check_annotation_type"),
    )

    op.create_table(
        "collections",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.func.uuid_generate_v4()),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("description", sa.String(), nullable=True),
        sa.Column("color", sa.String(), nullable=False, server_default=sa.text("'#3B82F6'")),
        sa.Column("artifact_ids", ARRAY(UUID(as_uuid=True)), nullable=False, server_default=sa.text("'{}'::uuid[]")),
        sa.Column("is_default", sa.Boolean(), nullable=False, server_default=sa.text("'false'")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        "daily_digests",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.func.uuid_generate_v4()),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("paper_scores", JSONB, nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("paper_count", sa.Integer(), nullable=False, server_default=sa.text("'0'")),
        sa.Column("status", sa.String(), nullable=False, server_default=sa.text("'pending'")),
        sa.Column("email_sent_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("user_id", "date", name="uq_user_date_digest"),
        sa.CheckConstraint("status IN ('pending', 'ready', 'sent', 'skipped')", name="check_digest_status"),
    )

    op.create_table(
        "usage_events",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.func.uuid_generate_v4()),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("event_type", sa.String(), nullable=False),
        sa.Column("meta_data", JSONB, nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("event_type IN ('artifact_created', 'question_asked', 'paper_ingested', 'report_generated')", name="check_usage_event_type"),
    )


def downgrade() -> None:
    op.drop_table("usage_events")
    op.drop_table("daily_digests")
    op.drop_table("collections")
    op.drop_table("annotations")
    op.drop_table("conversations")
    op.drop_table("paper_chunks")
    op.drop_table("artifacts")
    op.drop_table("papers")
    op.drop_table("users")
