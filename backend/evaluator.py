from datetime import datetime
from typing import Dict, List
from sqlalchemy.orm import Session
from starlette.concurrency import run_in_threadpool
from gemini_service import evaluate_answer
from models import Answer, Result, TestQuestion, TestSession


async def evaluate_submission(
    db: Session, test_session: TestSession, answers: Dict[int, str]
) -> Result:
    details: List[Dict] = []
    correct_count = 0

    ordered_questions = (
        db.query(TestQuestion)
        .filter(TestQuestion.test_id == test_session.id)
        .order_by(TestQuestion.order_index)
        .all()
    )

    for link in ordered_questions:
        question = link.question
        user_answer = answers.get(question.id)

        try:
            evaluation = await run_in_threadpool(
                evaluate_answer,
                question.text,
                question.options or {},
                user_answer or "",
            )
        except Exception:
            evaluation = {
                "correct_answer": "A",
                "is_correct": False,
                "explanation": "Evaluation failed. Please check Gemini configuration.",
            }

        is_correct = bool(evaluation.get("is_correct"))
        if is_correct:
            correct_count += 1

        detail = {
            "question_id": question.id,
            "user_answer": user_answer,
            "correct_answer": evaluation.get("correct_answer", ""),
            "is_correct": is_correct,
            "explanation": evaluation.get("explanation", ""),
        }
        details.append(detail)

        db.add(
            Answer(
                test_id=test_session.id,
                question_id=question.id,
                selected_option=user_answer,
            )
        )

    total = len(ordered_questions)
    wrong_count = total - correct_count
    accuracy = (correct_count / total) * 100 if total else 0.0

    result = Result(
        test_id=test_session.id,
        score=float(correct_count),
        correct_count=correct_count,
        wrong_count=wrong_count,
        accuracy=accuracy,
        details=details,
        created_at=datetime.utcnow(),
    )

    test_session.submitted_at = datetime.utcnow()

    db.add(result)
    db.commit()
    db.refresh(result)
    return result
