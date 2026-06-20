import json
from collections import Counter
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.api.deps import get_current_user
from app.core.config import get_settings
from app.core.database import get_db
from app.models import GeneratedQuestion, Mistake, Review, Student, User
from app.schemas.mistake import (
    AnalyzeOut,
    AnalyzeRequest,
    DashboardOut,
    GeneratedQuestionCreate,
    MistakeCreate,
    MistakeOut,
    MistakeUpdate,
    ReviewSubmit,
    UploadOut,
)
from app.services.ai_service import analyze_question
from app.services.storage_service import save_upload

router = APIRouter(tags=["mistakes"])


def dumps(items: list[str] | None) -> str:
    return json.dumps(items or [], ensure_ascii=False)


def loads(value: str | None) -> list[str]:
    if not value:
        return []
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return []


def make_out(mistake: Mistake) -> MistakeOut:
    return MistakeOut(
        id=mistake.id,
        student_id=mistake.student_id,
        image_url=mistake.image_url,
        image_storage_key=mistake.image_storage_key,
        question_text=mistake.question_text,
        student_answer=mistake.student_answer,
        correct_answer=mistake.correct_answer,
        solution=mistake.solution,
        mistake_step=mistake.mistake_step,
        mistake_reason=mistake.mistake_reason,
        mistake_type=mistake.mistake_type,
        main_knowledge_point=mistake.main_knowledge_point,
        prerequisite_points=loads(mistake.prerequisite_points),
        related_points=loads(mistake.related_points),
        grade=mistake.grade,
        semester=mistake.semester,
        difficulty=mistake.difficulty,
        mastery_status=mistake.mastery_status,
        review_count=mistake.review_count,
        correct_streak=mistake.correct_streak,
        wrong_count=mistake.wrong_count,
        next_review_date=mistake.next_review_date,
        created_at=mistake.created_at,
        updated_at=mistake.updated_at,
        generated_questions=list(mistake.generated_questions),
        reviews=list(mistake.reviews),
    )


def create_generated_questions(db: Session, mistake: Mistake, user_id: UUID, generated_questions: list[GeneratedQuestionCreate] | None = None):
    kp = mistake.main_knowledge_point or "当前知识点"
    questions = generated_questions or [
        GeneratedQuestionCreate(question_type="基础题", question_text=f"围绕「{kp}」完成一道直接计算题。", answer="按基本步骤求解。", solution="先确认条件，再使用基础方法。", knowledge_point=kp, difficulty="L1 基础题"),
        GeneratedQuestionCreate(question_type="变式题", question_text=f"改变条件顺序后，解决一道「{kp}」同类题。", answer="整理条件后求解。", solution="检查是否真正理解题型结构。", knowledge_point=kp, difficulty="L2 常规题"),
        GeneratedQuestionCreate(question_type="提高题", question_text=f"将「{kp}」与相关知识点结合完成综合应用。", answer="分步骤推理后得到答案。", solution="拆解问题，再合并结论。", knowledge_point=kp, difficulty="L3 综合题"),
    ]
    for item in questions[:3]:
        db.add(
            GeneratedQuestion(
                mistake_id=mistake.id,
                user_id=user_id,
                question_type=item.question_type,
                question_text=item.question_text,
                answer=item.answer,
                solution=item.solution,
                knowledge_point=item.knowledge_point or kp,
                difficulty=item.difficulty,
            )
        )


def ensure_user_storage_key(image_storage_key: str, current_user: User):
    if not image_storage_key.startswith(f"users/{current_user.id}/"):
        raise HTTPException(status_code=400, detail="图片不存在或无权使用")
    settings = get_settings()
    if settings.storage_mode == "local":
        upload_root = Path(settings.upload_dir).resolve()
        target = (upload_root / image_storage_key).resolve()
        if upload_root not in target.parents or not target.exists():
            raise HTTPException(status_code=400, detail="图片不存在或无权使用")


@router.post("/api/upload", response_model=UploadOut)
async def upload(file: UploadFile = File(...), current_user: User = Depends(get_current_user)):
    image_url, image_storage_key = await save_upload(file, str(current_user.id))
    return UploadOut(image_url=image_url, image_storage_key=image_storage_key)


@router.get("/api/files/{file_path:path}")
def get_local_file(file_path: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    settings = get_settings()
    if settings.storage_mode != "local":
        raise HTTPException(status_code=404, detail="文件不存在")
    mistake = db.scalar(select(Mistake).where(Mistake.user_id == current_user.id, Mistake.image_storage_key == file_path))
    if not mistake:
        raise HTTPException(status_code=404, detail="文件不存在")
    upload_root = Path(settings.upload_dir).resolve()
    target = (upload_root / file_path).resolve()
    if upload_root not in target.parents or not target.exists():
        raise HTTPException(status_code=404, detail="文件不存在")
    return FileResponse(target)


@router.post("/api/analyze", response_model=AnalyzeOut)
def analyze(payload: AnalyzeRequest, current_user: User = Depends(get_current_user)):
    ensure_user_storage_key(payload.image_storage_key, current_user)
    return analyze_question(payload.image_url)


@router.post("/api/mistakes", response_model=MistakeOut)
def create_mistake(payload: MistakeCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    ensure_user_storage_key(payload.image_storage_key, current_user)
    if payload.student_id:
        student = db.scalar(select(Student).where(Student.id == payload.student_id, Student.user_id == current_user.id))
        if not student:
            raise HTTPException(status_code=400, detail="学生不存在或无权使用")
    mistake = Mistake(
        user_id=current_user.id,
        student_id=payload.student_id,
        image_url=payload.image_url,
        image_storage_key=payload.image_storage_key,
        question_text=payload.question_text,
        student_answer=payload.student_answer,
        correct_answer=payload.correct_answer,
        solution=payload.solution,
        mistake_step=payload.mistake_step,
        mistake_reason=payload.mistake_reason,
        mistake_type=payload.mistake_type,
        main_knowledge_point=payload.main_knowledge_point,
        prerequisite_points=dumps(payload.prerequisite_points),
        related_points=dumps(payload.related_points),
        grade=payload.grade,
        semester=payload.semester,
        difficulty=payload.difficulty,
        mastery_status="未订正",
        next_review_date=date.today(),
    )
    db.add(mistake)
    db.flush()
    create_generated_questions(db, mistake, current_user.id, payload.generated_questions)
    db.add(Review(mistake_id=mistake.id, user_id=current_user.id, review_date=date.today(), review_type="订正", result="待完成", next_review_date=date.today()))
    db.commit()
    db.refresh(mistake)
    return get_mistake(mistake.id, db, current_user)


@router.get("/api/mistakes", response_model=list[MistakeOut])
def list_mistakes(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    mistakes = db.scalars(
        select(Mistake)
        .where(Mistake.user_id == current_user.id)
        .options(selectinload(Mistake.generated_questions), selectinload(Mistake.reviews))
        .order_by(Mistake.created_at.desc())
    ).all()
    return [make_out(item) for item in mistakes]


@router.get("/api/mistakes/{mistake_id}", response_model=MistakeOut)
def get_mistake(mistake_id: UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    mistake = db.scalar(
        select(Mistake)
        .where(Mistake.id == mistake_id, Mistake.user_id == current_user.id)
        .options(selectinload(Mistake.generated_questions), selectinload(Mistake.reviews))
    )
    if not mistake:
        raise HTTPException(status_code=404, detail="错题不存在")
    return make_out(mistake)


@router.patch("/api/mistakes/{mistake_id}", response_model=MistakeOut)
def update_mistake(mistake_id: UUID, payload: MistakeUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    mistake = db.scalar(select(Mistake).where(Mistake.id == mistake_id, Mistake.user_id == current_user.id))
    if not mistake:
        raise HTTPException(status_code=404, detail="错题不存在")
    updates = payload.model_dump(exclude_unset=True)
    for key, value in updates.items():
        if key in {"prerequisite_points", "related_points"}:
            value = dumps(value)
        setattr(mistake, key, value)
    db.commit()
    return get_mistake(mistake_id, db, current_user)


@router.delete("/api/mistakes/{mistake_id}")
def delete_mistake(mistake_id: UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    mistake = db.scalar(select(Mistake).where(Mistake.id == mistake_id, Mistake.user_id == current_user.id))
    if not mistake:
        raise HTTPException(status_code=404, detail="错题不存在")
    db.delete(mistake)
    db.commit()
    return {"ok": True}


@router.get("/api/review/today", response_model=list[MistakeOut])
def review_today(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    mistakes = db.scalars(
        select(Mistake)
        .where(Mistake.user_id == current_user.id, Mistake.next_review_date <= date.today(), Mistake.mastery_status != "已掌握")
        .options(selectinload(Mistake.generated_questions), selectinload(Mistake.reviews))
        .order_by(Mistake.next_review_date.asc())
    ).all()
    return [make_out(item) for item in mistakes]


@router.post("/api/review/{mistake_id}/submit", response_model=MistakeOut)
def submit_review(mistake_id: UUID, payload: ReviewSubmit, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    mistake = db.scalar(select(Mistake).where(Mistake.id == mistake_id, Mistake.user_id == current_user.id))
    if not mistake:
        raise HTTPException(status_code=404, detail="错题不存在")
    if payload.result not in {"correct", "wrong", "later"}:
        raise HTTPException(status_code=400, detail="复习结果只能是 correct / wrong / later")
    if payload.result == "later":
        next_date = date.today() + timedelta(days=1)
        mistake.next_review_date = next_date
        db.add(Review(mistake_id=mistake.id, user_id=current_user.id, review_date=date.today(), review_type="稍后复习", result=payload.result, next_review_date=next_date))
        db.commit()
        return get_mistake(mistake_id, db, current_user)

    mistake.review_count += 1
    if payload.result == "correct":
        mistake.correct_streak += 1
        mistake.mastery_status = "已掌握" if mistake.correct_streak >= 2 else "复习正确"
        schedule = {1: 3, 2: 7, 3: 14}
        next_date = date.today() + timedelta(days=schedule.get(mistake.correct_streak, 30))
    else:
        mistake.correct_streak = 0
        mistake.wrong_count += 1
        mistake.mastery_status = "高频错题" if mistake.wrong_count >= 2 else "复习仍错"
        next_date = date.today() + timedelta(days=3)
    mistake.next_review_date = next_date
    db.add(Review(mistake_id=mistake.id, user_id=current_user.id, review_date=date.today(), review_type="复习", result=payload.result, next_review_date=next_date))
    db.commit()
    return get_mistake(mistake_id, db, current_user)


@router.get("/api/dashboard", response_model=DashboardOut)
def dashboard(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    mistakes = db.scalars(select(Mistake).where(Mistake.user_id == current_user.id)).all()
    week_start_naive = datetime.utcnow() - timedelta(days=7)
    week_start_aware = datetime.now(timezone.utc) - timedelta(days=7)
    knowledge = Counter([m.main_knowledge_point or "未标记" for m in mistakes])
    reasons = Counter([m.mistake_reason or "未标记" for m in mistakes])

    def is_weekly_new(created_at: datetime | None) -> bool:
        if not created_at:
            return False
        if created_at.tzinfo and created_at.utcoffset():
            return created_at >= week_start_aware
        return created_at >= week_start_naive

    return DashboardOut(
        total=len(mistakes),
        weekly_new=len([m for m in mistakes if is_weekly_new(m.created_at)]),
        due_today=len([m for m in mistakes if m.next_review_date and m.next_review_date <= date.today() and m.mastery_status != "已掌握"]),
        frequent=len([m for m in mistakes if m.mastery_status == "高频错题"]),
        weak_knowledge=[{"name": name, "count": count} for name, count in knowledge.most_common(5)],
        mistake_reasons=[{"name": name, "count": count} for name, count in reasons.most_common(5)],
    )
