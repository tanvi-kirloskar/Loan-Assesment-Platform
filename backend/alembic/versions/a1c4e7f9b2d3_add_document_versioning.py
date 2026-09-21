"""add document versioning and duplicate detection

Revision ID: a1c4e7f9b2d3
Revises: 8b2d7c4e91af
Create Date: 2026-09-21 18:00:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "a1c4e7f9b2d3"
down_revision: Union[str, Sequence[str], None] = "8b2d7c4e91af"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add document hashes, active-version tracking, and version numbers."""

    op.add_column(
        "documents",
        sa.Column("file_hash", sa.String(length=64), nullable=True),
    )
    op.add_column(
        "documents",
        sa.Column(
            "is_active",
            sa.Boolean(),
            nullable=False,
            server_default=sa.true(),
        ),
    )
    op.add_column(
        "documents",
        sa.Column(
            "version_number",
            sa.Integer(),
            nullable=False,
            server_default="1",
        ),
    )

    # Existing records become version 1. If legacy data contains multiple
    # documents of one type, keep only the newest record active.
    connection = op.get_bind()

    duplicate_types = connection.execute(
        sa.text(
            """
            SELECT application_id, document_type, MAX(created_at) AS latest_created_at
            FROM documents
            GROUP BY application_id, document_type
            HAVING COUNT(*) > 1
            """
        )
    ).mappings()

    for row in duplicate_types:
        connection.execute(
            sa.text(
                """
                UPDATE documents
                SET is_active = FALSE
                WHERE application_id = :application_id
                  AND document_type = :document_type
                  AND created_at < :latest_created_at
                """
            ),
            {
                "application_id": row["application_id"],
                "document_type": row["document_type"],
                "latest_created_at": row["latest_created_at"],
            },
        )

    # Populate SHA-256 hashes for legacy rows where possible.
    # Existing storage contents are intentionally not loaded in migration;
    # hashes will be populated for all newly uploaded documents.
    op.alter_column(
        "documents",
        "is_active",
        server_default=None,
    )
    op.alter_column(
        "documents",
        "version_number",
        server_default=None,
    )

    op.create_index(
        "ix_documents_application_type_active",
        "documents",
        ["application_id", "document_type", "is_active"],
    )
    op.create_index(
        "ix_documents_application_hash",
        "documents",
        ["application_id", "file_hash"],
    )
    op.create_index(
        "uq_documents_one_active_type",
        "documents",
        ["application_id", "document_type"],
        unique=True,
        postgresql_where=sa.text("is_active = true"),
    )


def downgrade() -> None:
    """Remove document versioning metadata."""

    op.drop_index(
        "uq_documents_one_active_type",
        table_name="documents",
    )
    op.drop_index(
        "ix_documents_application_hash",
        table_name="documents",
    )
    op.drop_index(
        "ix_documents_application_type_active",
        table_name="documents",
    )
    op.drop_column("documents", "version_number")
    op.drop_column("documents", "is_active")
    op.drop_column("documents", "file_hash")
