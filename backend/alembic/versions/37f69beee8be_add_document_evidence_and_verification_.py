"""add document evidence and verification findings

Revision ID: 37f69beee8be
Revises: 0316b8535f32
Create Date: 2026-09-12 11:00:49.089447

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "37f69beee8be"
down_revision: Union[str, Sequence[str], None] = "0316b8535f32"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "verification_findings",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("application_id", sa.Integer(), nullable=False),
        sa.Column("finding_type", sa.String(length=50), nullable=False),
        sa.Column("severity", sa.String(length=20), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("action", sa.String(length=30), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["application_id"],
            ["loan_applications.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "document_evidence",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("document_id", sa.Uuid(), nullable=False),
        sa.Column("field_name", sa.String(length=100), nullable=False),
        sa.Column("extracted_value", sa.Text(), nullable=False),
        sa.Column(
            "confidence",
            sa.Numeric(precision=5, scale=4),
            nullable=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["document_id"],
            ["documents.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("document_evidence")
    op.drop_table("verification_findings")