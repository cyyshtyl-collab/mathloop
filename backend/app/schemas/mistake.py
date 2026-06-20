from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel


class UploadOut(BaseModel):
    image_url: str
    image_storage_key: str


class AnalyzeRequest(BaseModel):
    image_url: str
    image_storage_key: str


class GeneratedQuestionCreate(BaseModel):
    question_type: str
    question_text: str
    answer: str | None = None
    solution: str | None = None
    knowledge_point: str | None = None
    difficulty: str | None = None


class AnalyzeOut(BaseModel):
    recognition_status: str = "success"
    question_text: str
    student_answer: str | None = None
    correct_answer: str | None = None
    solution: str | None = None
    mistake_step: str | None = None
    mistake_reason: str | None = None
    mistake_type: str | None = None
    main_knowledge_point: str | None = None
    prerequisite_points: list[str] = []
    related_points: list[str] = []
    grade: str | None = None
    semester: str | None = None
    difficulty: str | None = None
    is_complete: bool = True
    generated_questions: list[GeneratedQuestionCreate] = []


class MistakeCreate(AnalyzeOut):
    image_url: str
    image_storage_key: str
    student_id: UUID | None = None


class MistakeUpdate(BaseModel):
    question_text: str | None = None
    student_answer: str | None = None
    correct_answer: str | None = None
    solution: str | None = None
    mistake_step: str | None = None
    mistake_reason: str | None = None
    mistake_type: str | None = None
    main_knowledge_point: str | None = None
    prerequisite_points: list[str] | None = None
    related_points: list[str] | None = None
    grade: str | None = None
    semester: str | None = None
    difficulty: str | None = None
    mastery_status: str | None = None


class GeneratedQuestionOut(BaseModel):
    id: UUID
    question_type: str
    question_text: str
    answer: str | None
    solution: str | None
    knowledge_point: str | None
    difficulty: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class ReviewOut(BaseModel):
    id: UUID
    review_date: date
    review_type: str
    result: str | None
    next_review_date: date | None
    created_at: datetime

    model_config = {"from_attributes": True}


class MistakeOut(BaseModel):
    id: UUID
    student_id: UUID | None
    image_url: str
    image_storage_key: str
    question_text: str
    student_answer: str | None
    correct_answer: str | None
    solution: str | None
    mistake_step: str | None
    mistake_reason: str | None
    mistake_type: str | None
    main_knowledge_point: str | None
    prerequisite_points: list[str]
    related_points: list[str]
    grade: str | None
    semester: str | None
    difficulty: str | None
    mastery_status: str
    review_count: int
    correct_streak: int
    wrong_count: int
    next_review_date: date | None
    created_at: datetime
    updated_at: datetime
    generated_questions: list[GeneratedQuestionOut] = []
    reviews: list[ReviewOut] = []

    model_config = {"from_attributes": True}


class ReviewSubmit(BaseModel):
    result: str


class DashboardOut(BaseModel):
    total: int
    weekly_new: int
    due_today: int
    frequent: int
    weak_knowledge: list[dict]
    mistake_reasons: list[dict]
