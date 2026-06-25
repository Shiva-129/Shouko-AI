"""fix_artifact_paper_id_cascade

Revision ID: 5a1b2c3d4e5f
Revises: 4e8f2c1a6b3d
Create Date: 2026-06-12

"""

from typing import Sequence, Union
from alembic import op

revision: str = "5a1b2c3d4e5f"
down_revision: Union[str, None] = "4e8f2c1a6b3d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Fix the artifacts.paper_id foreign key to include ondelete=CASCADE,
    # matching the current SQLAlchemy model definition.
    op.drop_constraint("artifacts_paper_id_fkey", "artifacts", type_="foreignkey")
    op.create_foreign_key(
        "artifacts_paper_id_fkey",
        "artifacts",
        "papers",
        ["paper_id"],
        ["id"],
        ondelete="CASCADE",
    )


def downgrade() -> None:
    op.drop_constraint("artifacts_paper_id_fkey", "artifacts", type_="foreignkey")
    op.create_foreign_key(
        "artifacts_paper_id_fkey",
        "artifacts",
        "papers",
        ["paper_id"],
        ["id"],
    )
