import uuid
from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, Integer, String, Text, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    role: Mapped[str] = mapped_column(String(50), default="parent", nullable=False)

    students: Mapped[list["Student"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    mistakes: Mapped[list["Mistake"]] = relationship(back_populates="user", cascade="all, delete-orphan")


class Student(Base, TimestampMixin):
    __tablename__ = "students"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("users.id"), index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    grade: Mapped[str | None] = mapped_column(String(50))
    school: Mapped[str | None] = mapped_column(String(120))

    user: Mapped[User] = relationship(back_populates="students")


class Mistake(Base, TimestampMixin):
    __tablename__ = "mistakes"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("users.id"), index=True, nullable=False)
    student_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("students.id"), nullable=True)
    image_url: Mapped[str] = mapped_column(Text, nullable=False)
    image_storage_key: Mapped[str] = mapped_column(Text, nullable=False)
    question_text: Mapped[str] = mapped_column(Text, nullable=False)
    student_answer: Mapped[str | None] = mapped_column(Text)
    correct_answer: Mapped[str | None] = mapped_column(Text)
    solution: Mapped[str | None] = mapped_column(Text)
    mistake_step: Mapped[str | None] = mapped_column(Text)
    mistake_reason: Mapped[str | None] = mapped_column(Text)
    mistake_type: Mapped[str | None] = mapped_column(String(100))
    main_knowledge_point: Mapped[str | None] = mapped_column(String(120), index=True)
    prerequisite_points: Mapped[str | None] = mapped_column(Text)
    related_points: Mapped[str | None] = mapped_column(Text)
    grade: Mapped[str | None] = mapped_column(String(50), index=True)
    semester: Mapped[str | None] = mapped_column(String(50))
    difficulty: Mapped[str | None] = mapped_column(String(50), index=True)
    mastery_status: Mapped[str] = mapped_column(String(50), default="未订正", index=True)
    review_count: Mapped[int] = mapped_column(Integer, default=0)
    correct_streak: Mapped[int] = mapped_column(Integer, default=0)
    wrong_count: Mapped[int] = mapped_column(Integer, default=0)
    next_review_date: Mapped[date | None] = mapped_column(Date, index=True)

    user: Mapped[User] = relationship(back_populates="mistakes")
    generated_questions: Mapped[list["GeneratedQuestion"]] = relationship(back_populates="mistake", cascade="all, delete-orphan")
    reviews: Mapped[list["Review"]] = relationship(back_populates="mistake", cascade="all, delete-orphan")


class GeneratedQuestion(Base, TimestampMixin):
    __tablename__ = "generated_questions"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    mistake_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("mistakes.id"), index=True, nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("users.id"), index=True, nullable=False)
    question_type: Mapped[str] = mapped_column(String(50), nullable=False)
    question_text: Mapped[str] = mapped_column(Text, nullable=False)
    answer: Mapped[str | None] = mapped_column(Text)
    solution: Mapped[str | None] = mapped_column(Text)
    knowledge_point: Mapped[str | None] = mapped_column(String(120))
    difficulty: Mapped[str | None] = mapped_column(String(50))

    mistake: Mapped[Mistake] = relationship(back_populates="generated_questions")


class Review(Base, TimestampMixin):
    __tablename__ = "reviews"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    mistake_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("mistakes.id"), index=True, nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("users.id"), index=True, nullable=False)
    review_date: Mapped[date] = mapped_column(Date, nullable=False)
    review_type: Mapped[str] = mapped_column(String(50), nullable=False)
    result: Mapped[str | None] = mapped_column(String(50))
    next_review_date: Mapped[date | None] = mapped_column(Date)

    mistake: Mapped[Mistake] = relationship(back_populates="reviews")


class KnowledgePoint(Base):
    __tablename__ = "knowledge_points"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    stage: Mapped[str] = mapped_column(String(50), default="初中", nullable=False)
    grade: Mapped[str | None] = mapped_column(String(50), index=True)
    semester: Mapped[str | None] = mapped_column(String(50))
    category: Mapped[str] = mapped_column(String(100), index=True)
    name: Mapped[str] = mapped_column(String(120), index=True, nullable=False)
    parent_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("knowledge_points.id"), nullable=True)
