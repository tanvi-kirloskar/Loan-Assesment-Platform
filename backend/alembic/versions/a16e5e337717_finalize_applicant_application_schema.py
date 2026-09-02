"""finalize applicant application schema

Revision ID: a16e5e337717
Revises: c092554ba480
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "a16e5e337717"
down_revision: Union[str, Sequence[str], None] = "c092554ba480"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    connection = op.get_bind()

    missing = connection.execute(
        sa.text(
            """
            SELECT COUNT(*)
            FROM loan_applications
            WHERE applicant_id IS NULL
            """
        )
    ).scalar_one()

    if missing != 0:
        raise RuntimeError(
            f"Cannot finalize schema: {missing} applications have no applicant."
        )

    op.alter_column(
        "loan_applications",
        "applicant_id",
        existing_type=sa.Integer(),
        nullable=False,
    )

    op.drop_column("loan_applications", "full_name")
    op.drop_column("loan_applications", "monthly_income")

    op.create_unique_constraint(
        "uq_users_email",
        "users",
        ["email"],
    )

    op.create_unique_constraint(
        "uq_applicants_user_id",
        "applicants",
        ["user_id"],
    )


def downgrade() -> None:
    connection = op.get_bind()

    op.drop_constraint(
        "uq_applicants_user_id",
        "applicants",
        type_="unique",
    )

    op.drop_constraint(
        "uq_users_email",
        "users",
        type_="unique",
    )

    op.add_column(
        "loan_applications",
        sa.Column(
            "full_name",
            sa.String(length=100),
            nullable=True,
        ),
    )

    op.add_column(
        "loan_applications",
        sa.Column(
            "monthly_income",
            sa.Integer(),
            nullable=True,
        ),
    )

    connection.execute(
        sa.text(
            """
            UPDATE loan_applications AS la
            SET
                full_name = a.full_name,
                monthly_income = a.monthly_income
            FROM applicants AS a
            WHERE la.applicant_id = a.id
            """
        )
    )

    op.alter_column(
        "loan_applications",
        "applicant_id",
        existing_type=sa.Integer(),
        nullable=True,
    )