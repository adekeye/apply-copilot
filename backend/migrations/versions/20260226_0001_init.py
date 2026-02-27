"""init

Revision ID: 20260226_0001
Revises:
Create Date: 2026-02-26 20:00:00
"""

from alembic import op
import sqlalchemy as sa

revision = "20260226_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("username", sa.String(length=100), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_users_username", "users", ["username"], unique=True)

    op.create_table(
        "resume_profiles",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("raw_text", sa.Text(), nullable=False),
        sa.Column("contact", sa.JSON(), nullable=False),
        sa.Column("skills", sa.JSON(), nullable=False),
        sa.Column("years_experience", sa.Integer(), nullable=False),
        sa.Column("projects", sa.JSON(), nullable=False),
        sa.Column("employers", sa.JSON(), nullable=False),
        sa.Column("education", sa.JSON(), nullable=False),
        sa.Column("keywords", sa.JSON(), nullable=False),
        sa.Column("location_preferences", sa.JSON(), nullable=False),
        sa.Column("work_auth", sa.String(length=255), nullable=False),
        sa.Column("links", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )

    job_status = sa.Enum("discovered", "saved", "drafted", "applied", "interview", "rejected", name="jobstatus")
    job_status.create(op.get_bind())

    op.create_table(
        "jobs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("source", sa.String(length=100), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("company", sa.String(length=255), nullable=False),
        sa.Column("url", sa.String(length=1024), nullable=True),
        sa.Column("jd_text", sa.Text(), nullable=False),
        sa.Column("extracted", sa.JSON(), nullable=False),
        sa.Column("score", sa.Float(), nullable=True),
        sa.Column("score_explanation", sa.JSON(), nullable=True),
        sa.Column("status", job_status, nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )

    op.create_table(
        "artifacts",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("job_id", sa.Integer(), sa.ForeignKey("jobs.id"), nullable=False),
        sa.Column("kind", sa.String(length=100), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("content", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("artifacts")
    op.drop_table("jobs")
    op.execute("DROP TYPE IF EXISTS jobstatus")
    op.drop_table("resume_profiles")
    op.drop_index("ix_users_username", table_name="users")
    op.drop_table("users")
