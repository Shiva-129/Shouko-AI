"""switch_to_384d_embeddings

Revision ID: 1327a1c5b9d4
Revises: 960bef3e8fab
Create Date: 2026-06-02
"""
from typing import Sequence, Union
from alembic import op
from pgvector.sqlalchemy import Vector

revision: str = "1327a1c5b9d4"
down_revision: Union[str, None] = "960bef3e8fab"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column("paper_chunks", "embedding", type_=Vector(384), existing_nullable=False)
    op.alter_column("artifacts", "embedding", type_=Vector(384), existing_nullable=True)


def downgrade() -> None:
    op.alter_column("paper_chunks", "embedding", type_=Vector(1536), existing_nullable=False)
    op.alter_column("artifacts", "embedding", type_=Vector(1536), existing_nullable=True)
