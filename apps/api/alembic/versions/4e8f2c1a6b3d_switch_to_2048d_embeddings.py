"""switch_to_2048d_embeddings

Revision ID: 4e8f2c1a6b3d
Revises: 1327a1c5b9d4
Create Date: 2026-06-05
"""
from typing import Sequence, Union
from alembic import op
from pgvector.sqlalchemy import Vector

revision: str = "4e8f2c1a6b3d"
down_revision: Union[str, None] = "1327a1c5b9d4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column("paper_chunks", "embedding", type_=Vector(2048), existing_nullable=False)
    op.alter_column("artifacts", "embedding", type_=Vector(2048), existing_nullable=True)


def downgrade() -> None:
    op.alter_column("paper_chunks", "embedding", type_=Vector(384), existing_nullable=False)
    op.alter_column("artifacts", "embedding", type_=Vector(384), existing_nullable=True)
