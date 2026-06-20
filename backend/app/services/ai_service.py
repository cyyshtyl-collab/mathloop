from app.core.config import get_settings
from app.schemas.mistake import AnalyzeOut, GeneratedQuestionCreate


def mock_analyze_question(image_url: str) -> AnalyzeOut:
    return AnalyzeOut(
        recognition_status="success",
        question_text="计算：-3 + 5 - 8",
        student_answer="-5",
        correct_answer="-6",
        solution="先计算 -3 + 5 = 2，再计算 2 - 8 = -6，所以答案是 -6。",
        mistake_step="最后一步 2 - 8 计算错误。",
        mistake_reason="有理数减法运算不熟练。",
        mistake_type="计算错误",
        main_knowledge_point="有理数加减法",
        prerequisite_points=["正负数概念", "绝对值"],
        related_points=["有理数混合运算"],
        grade="七年级",
        semester="上学期",
        difficulty="L1 基础题",
        is_complete=True,
        generated_questions=[
            GeneratedQuestionCreate(
                question_type="基础题",
                question_text="计算：-4 + 7 - 2",
                answer="1",
                solution="-4 + 7 = 3，3 - 2 = 1。",
                knowledge_point="有理数加减法",
                difficulty="L1 基础题",
            ),
            GeneratedQuestionCreate(
                question_type="变式题",
                question_text="计算：6 - 9 + 4 - 10",
                answer="-9",
                solution="6 - 9 = -3，-3 + 4 = 1，1 - 10 = -9。",
                knowledge_point="有理数加减法",
                difficulty="L2 常规题",
            ),
            GeneratedQuestionCreate(
                question_type="提高题",
                question_text="若 a = -3，b = 5，c = -8，求 a + b + c 的值。",
                answer="-6",
                solution="代入得 -3 + 5 - 8 = -6。",
                knowledge_point="有理数加减法",
                difficulty="L2 常规题",
            ),
        ],
    )


def analyze_question(image_url: str) -> AnalyzeOut:
    settings = get_settings()
    if settings.ai_mode == "mock":
        return mock_analyze_question(image_url)
    if settings.ai_mode == "openai":
        # TODO: 调用 OpenAI 多模态模型，保持返回 AnalyzeOut 结构。
        return mock_analyze_question(image_url)
    if settings.ai_mode == "gemini":
        # TODO: 调用 Gemini 多模态模型，保持返回 AnalyzeOut 结构。
        return mock_analyze_question(image_url)
    return mock_analyze_question(image_url)
