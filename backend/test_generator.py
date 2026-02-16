from datetime import datetime
from typing import List
from sqlalchemy.orm import Session
from models import Question, TestQuestion, TestSession


def create_test_session(db: Session, questions: List[Question]) -> TestSession:
    session = TestSession(total_questions=len(questions))
    db.add(session)
    db.flush()

    for idx, question in enumerate(questions):
        link = TestQuestion(test_id=session.id, question_id=question.id, order_index=idx)
        db.add(link)

    db.commit()
    db.refresh(session)
    return session


def start_test_session(db: Session, session: TestSession, duration_minutes: int) -> TestSession:
    if session.started_at is None:  # Only set once
        session.started_at = datetime.utcnow()
    session.duration_minutes = duration_minutes
    db.commit()
    db.refresh(session)
    return session
