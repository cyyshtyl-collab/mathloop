"""initial schema

Revision ID: 20260620_0001
Revises:
Create Date: 2026-06-20
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "20260620_0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def timestamps():
    return [
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    ]


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("role", sa.String(length=50), nullable=False, server_default="parent"),
        *timestamps(),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    op.create_table(
        "students",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("grade", sa.String(length=50)),
        sa.Column("school", sa.String(length=120)),
        *timestamps(),
    )
    op.create_index("ix_students_user_id", "students", ["user_id"])

    op.create_table(
        "mistakes",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("student_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("students.id")),
        sa.Column("image_url", sa.Text(), nullable=False),
        sa.Column("image_storage_key", sa.Text(), nullable=False),
        sa.Column("question_text", sa.Text(), nullable=False),
        sa.Column("student_answer", sa.Text()),
        sa.Column("correct_answer", sa.Text()),
        sa.Column("solution", sa.Text()),
        sa.Column("mistake_step", sa.Text()),
        sa.Column("mistake_reason", sa.Text()),
        sa.Column("mistake_type", sa.String(length=100)),
        sa.Column("main_knowledge_point", sa.String(length=120)),
        sa.Column("prerequisite_points", sa.Text()),
        sa.Column("related_points", sa.Text()),
        sa.Column("grade", sa.String(length=50)),
        sa.Column("semester", sa.String(length=50)),
        sa.Column("difficulty", sa.String(length=50)),
        sa.Column("mastery_status", sa.String(length=50), nullable=False, server_default="未订正"),
        sa.Column("review_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("correct_streak", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("wrong_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("next_review_date", sa.Date()),
        *timestamps(),
    )
    op.create_index("ix_mistakes_user_id", "mistakes", ["user_id"])
    op.create_index("ix_mistakes_next_review_date", "mistakes", ["next_review_date"])

    op.create_table(
        "generated_questions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("mistake_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("mistakes.id"), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("question_type", sa.String(length=50), nullable=False),
        sa.Column("question_text", sa.Text(), nullable=False),
        sa.Column("answer", sa.Text()),
        sa.Column("solution", sa.Text()),
        sa.Column("knowledge_point", sa.String(length=120)),
        sa.Column("difficulty", sa.String(length=50)),
        *timestamps(),
    )
    op.create_index("ix_generated_questions_mistake_id", "generated_questions", ["mistake_id"])
    op.create_index("ix_generated_questions_user_id", "generated_questions", ["user_id"])

    op.create_table(
        "reviews",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("mistake_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("mistakes.id"), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("review_date", sa.Date(), nullable=False),
        sa.Column("review_type", sa.String(length=50), nullable=False),
        sa.Column("result", sa.String(length=50)),
        sa.Column("next_review_date", sa.Date()),
        *timestamps(),
    )
    op.create_index("ix_reviews_mistake_id", "reviews", ["mistake_id"])
    op.create_index("ix_reviews_user_id", "reviews", ["user_id"])

    op.create_table(
        "knowledge_points",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("stage", sa.String(length=50), nullable=False, server_default="初中"),
        sa.Column("grade", sa.String(length=50)),
        sa.Column("semester", sa.String(length=50)),
        sa.Column("category", sa.String(length=100), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("parent_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("knowledge_points.id")),
    )


def downgrade() -> None:
    op.drop_table("knowledge_points")
    op.drop_table("reviews")
    op.drop_table("generated_questions")
    op.drop_table("mistakes")
    op.drop_table("students")
    op.drop_table("users")
