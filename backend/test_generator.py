import random
from datetime import datetime
from typing import List
from sqlalchemy.orm import Session
from models import Question, TestQuestion, TestSession


def create_test_session(db: Session, questions: List[Question]) -> TestSession:
    session = TestSession(total_questions=len(questions))
    db.add(session)
    db.flush()

    shuffled = questions[:]
    random.shuffle(shuffled)

    for idx, question in enumerate(shuffled):
        link = TestQuestion(test_id=session.id, question_id=question.id, order_index=idx)
        db.add(link)

    db.commit()
    db.refresh(session)
    return session


def start_test_session(db: Session, session: TestSession, duration_minutes: int) -> TestSession:
    session.duration_minutes = duration_minutes
    session.started_at = datetime.utcnow()
    db.commit()
    db.refresh(session)
    return session
