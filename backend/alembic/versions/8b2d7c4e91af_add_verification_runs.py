"""add verification run history

Revision ID: 8b2d7c4e91af
Revises: 37f69beee8be
Create Date: 2026-09-21 17:30:00.000000

"""

from typing import Sequence, Union
from uuid import uuid4

from alembic import op
import sqlalchemy as sa


revision: str = "8b2d7c4e91af"
down_revision: Union[str, Sequence[str], None] = "37f69beee8be"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create immutable verification runs and link existing findings to run 1."""

    op.create_table(
        "verification_runs",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("application_id", sa.Integer(), nullable=False),
        sa.Column("run_number", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("is_latest", sa.Boolean(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.Column(
            "completed_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(
            ["application_id"],
            ["loan_applications.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "application_id",
            "run_number",
            name="uq_verification_run_application_number",
        ),
    )

    op.add_column(
        "verification_findings",
        sa.Column("run_id", sa.Uuid(), nullable=True),
    )
    op.create_foreign_key(
        "fk_verification_findings_run_id",
        "verification_findings",
        "verification_runs",
        ["run_id"],
        ["id"],
    )

    connection = op.get_bind()
    existing = connection.execute(
        sa.text(
            """
            SELECT application_id, MIN(created_at) AS created_at,
                   MAX(created_at) AS completed_at
            FROM verification_findings
            GROUP BY application_id
            """
        )
    ).mappings()

    for row in existing:
        run_id = uuid4()
        connection.execute(
            sa.text(
                """
                INSERT INTO verification_runs
                    (id, application_id, run_number, status, is_latest,
                     created_at, completed_at)
                VALUES
                    (:id, :application_id, 1, 'COMPLETED', TRUE,
                     :created_at, :completed_at)
                """
            ),
            {
                "id": run_id,
                "application_id": row["application_id"],
                "created_at": row["created_at"],
                "completed_at": row["completed_at"],
            },
        )
        connection.execute(
            sa.text(
                """
                UPDATE verification_findings
                SET run_id = :run_id
                WHERE application_id = :application_id
                  AND run_id IS NULL
                """
            ),
            {
                "run_id": run_id,
                "application_id": row["application_id"],
            },
        )

    op.alter_column(
        "verification_findings",
        "run_id",
        existing_type=sa.Uuid(),
        nullable=False,
    )

    op.create_index(
        "ix_verification_runs_application",
        "verification_runs",
        ["application_id"],
    )
    op.create_index(
        "uq_verification_runs_one_latest",
        "verification_runs",
        ["application_id"],
        unique=True,
        postgresql_where=sa.text("is_latest = true"),
    )


def downgrade() -> None:
    """Remove verification run history."""

    op.drop_index(
        "uq_verification_runs_one_latest",
        table_name="verification_runs",
    )
    op.drop_index(
        "ix_verification_runs_application",
        table_name="verification_runs",
    )
    op.drop_constraint(
        "fk_verification_findings_run_id",
        "verification_findings",
        type_="foreignkey",
    )
    op.drop_column("verification_findings", "run_id")
    op.drop_table("verification_runs")
