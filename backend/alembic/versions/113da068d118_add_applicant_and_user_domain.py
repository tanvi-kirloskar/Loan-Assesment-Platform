"""add applicant and user domain

Revision ID: 113da068d118
Revises: 9004ed9a003a
Create Date: 2026-09-02 11:49:15.320376

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "113da068d118"
down_revision: Union[str, Sequence[str], None] = "9004ed9a003a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add users, applicants, and new loan application fields."""

    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("role", sa.String(length=20), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )

    op.create_table(
        "applicants",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("full_name", sa.String(length=100), nullable=False),
        sa.Column("age", sa.Integer(), nullable=True),
        sa.Column("employment_type", sa.String(length=50), nullable=True),
        sa.Column("employer", sa.String(length=100), nullable=True),
        sa.Column("years_employed", sa.Integer(), nullable=True),
        sa.Column("monthly_income", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id"),
    )

    op.add_column(
        "loan_applications",
        sa.Column("applicant_id", sa.Integer(), nullable=True),
    )

    op.add_column(
        "loan_applications",
        sa.Column("loan_purpose", sa.String(length=100), nullable=True),
    )

    op.add_column(
        "loan_applications",
        sa.Column("existing_monthly_emi", sa.Integer(), nullable=True),
    )

    op.add_column(
        "loan_applications",
        sa.Column("decision", sa.String(length=20), nullable=True),
    )

    op.add_column(
        "loan_applications",
        sa.Column("credit_score", sa.Integer(), nullable=True),
    )

    op.add_column(
        "loan_applications",
        sa.Column("credit_score_source", sa.String(length=50), nullable=True),
    )

    op.create_foreign_key(
        "fk_loan_applications_applicant_id",
        "loan_applications",
        "applicants",
        ["applicant_id"],
        ["id"],
    )


def downgrade() -> None:
    """Remove users, applicants, and new loan application fields."""

    op.drop_constraint(
        "fk_loan_applications_applicant_id",
        "loan_applications",
        type_="foreignkey",
    )

    op.drop_column("loan_applications", "credit_score_source")
    op.drop_column("loan_applications", "credit_score")
    op.drop_column("loan_applications", "decision")
    op.drop_column("loan_applications", "existing_monthly_emi")
    op.drop_column("loan_applications", "loan_purpose")
    op.drop_column("loan_applications", "applicant_id")

    op.drop_table("applicants")
    op.drop_table("users")