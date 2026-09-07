"""add deterministic assessment results

Revision ID: 578e915f32d3
Revises: a16e5e337717
Create Date: 2026-09-05 14:43:33.962701

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "578e915f32d3"
down_revision: Union[str, Sequence[str], None] = "a16e5e337717"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "loan_applications",
        sa.Column(
            "interest_rate",
            sa.Numeric(precision=5, scale=4),
            nullable=True,
        ),
    )

    op.add_column(
        "loan_applications",
        sa.Column(
            "emi",
            sa.Numeric(precision=12, scale=2),
            nullable=True,
        ),
    )

    op.add_column(
        "loan_applications",
        sa.Column(
            "foir",
            sa.Numeric(precision=6, scale=2),
            nullable=True,
        ),
    )

    op.add_column(
        "loan_applications",
        sa.Column(
            "lti",
            sa.Numeric(precision=6, scale=2),
            nullable=True,
        ),
    )

    op.add_column(
        "loan_applications",
        sa.Column(
            "assessment_reasons",
            sa.Text(),
            nullable=True,
        ),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("loan_applications", "assessment_reasons")
    op.drop_column("loan_applications", "lti")
    op.drop_column("loan_applications", "foir")
    op.drop_column("loan_applications", "emi")
    op.drop_column("loan_applications", "interest_rate")