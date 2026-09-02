"""backfill applicants and decisions

Revision ID: c092554ba480
Revises: 113da068d118
Create Date: 2026-09-02 11:56:23.377136

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "c092554ba480"
down_revision: Union[str, Sequence[str], None] = "113da068d118"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Backfill applicants and preserve existing loan decisions."""

    connection = op.get_bind()

    applications = connection.execute(
        sa.text(
            """
            SELECT id, full_name, monthly_income, status
            FROM loan_applications
            WHERE applicant_id IS NULL
            ORDER BY id
            """
        )
    ).fetchall()

    for application in applications:
        applicant_id = connection.execute(
            sa.text(
                """
                INSERT INTO applicants (
                    user_id,
                    full_name,
                    age,
                    employment_type,
                    employer,
                    years_employed,
                    monthly_income
                )
                VALUES (
                    NULL,
                    :full_name,
                    NULL,
                    NULL,
                    NULL,
                    NULL,
                    :monthly_income
                )
                RETURNING id
                """
            ),
            {
                "full_name": application.full_name,
                "monthly_income": application.monthly_income,
            },
        ).scalar_one()

        connection.execute(
            sa.text(
                """
                UPDATE loan_applications
                SET
                    applicant_id = :applicant_id,
                    decision = :decision,
                    status = 'submitted'
                WHERE id = :application_id
                """
            ),
            {
                "applicant_id": applicant_id,
                "decision": application.status,
                "application_id": application.id,
            },
        )


def downgrade() -> None:
    """Reverse the applicant backfill."""

    connection = op.get_bind()

    applicant_ids = connection.execute(
        sa.text(
            """
            SELECT applicant_id
            FROM loan_applications
            WHERE applicant_id IS NOT NULL
            """
        )
    ).fetchall()

    connection.execute(
        sa.text(
            """
            UPDATE loan_applications
            SET applicant_id = NULL,
                decision = NULL
            """
        )
    )

    for row in applicant_ids:
        connection.execute(
            sa.text(
                """
                DELETE FROM applicants
                WHERE id = :applicant_id
                """
            ),
            {"applicant_id": row.applicant_id},
        )