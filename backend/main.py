import os
from dotenv import load_dotenv
from typing import List
from fastapi import Depends, FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database import Base, engine, get_db
from evaluator import evaluate_submission
from gemini_service import explain_answer, extract_questions_llm
from models import Question, TestQuestion, TestSession
from pdf_parser import extract_text_from_pdf, parse_questions_from_text
from schemas import (
    ExplanationRequest,
    ExplanationResponse,
    RetryResponse,
    StartTestRequest,
    StartTestResponse,
    SubmitRequest,
    SubmitResponse,
    UploadResponse,
)
from test_generator import create_test_session, start_test_session
# Import company-based assessment routes
from company_routes import router as company_router

load_dotenv()
Base.metadata.create_all(bind=engine)

app = FastAPI(title="PDF Test Generator & Evaluator")

# Include company assessment routes
app.include_router(company_router)

cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in cors_origins],
    allow_credentials=True,
    allow_methods=["*"] ,
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    return {"status": "ok"}


@app.post("/api/upload", response_model=UploadResponse)
async def upload_pdf(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    content = await file.read()
    text = extract_text_from_pdf(content)
    questions_data = parse_questions_from_text(text)

    if not questions_data:
        questions_data = extract_questions_llm(text)

    if not questions_data:
        raise HTTPException(status_code=422, detail="No questions found in PDF.")

    questions: List[Question] = []
    for item in questions_data:
        question = Question(
            number=int(item.get("number", len(questions) + 1)),
            text=str(item.get("text", "")).strip(),
            options=item.get("options", {}),
            source_name=file.filename,
        )
        questions.append(question)
        db.add(question)

    db.commit()

    for question in questions:
        db.refresh(question)

    session = create_test_session(db, questions)

    ordered_links = (
        db.query(TestQuestion)
        .filter(TestQuestion.test_id == session.id)
        .order_by(TestQuestion.order_index)
        .all()
    )

    ordered_questions = [link.question for link in ordered_links]

    return UploadResponse(test_id=session.id, questions=ordered_questions)


@app.post("/api/tests/{test_id}/start", response_model=StartTestResponse)
async def start_test(
    test_id: int, payload: StartTestRequest, db: Session = Depends(get_db)
):
    session = db.query(TestSession).filter(TestSession.id == test_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Test session not found.")

    session = start_test_session(db, session, payload.duration_minutes)

    ordered_links = (
        db.query(TestQuestion)
        .filter(TestQuestion.test_id == session.id)
        .order_by(TestQuestion.order_index)
        .all()
    )
    ordered_questions = [link.question for link in ordered_links]

    return StartTestResponse(
        test_id=session.id, duration_minutes=session.duration_minutes, questions=ordered_questions
    )


@app.post("/api/tests/{test_id}/retry", response_model=RetryResponse)
async def retry_test(test_id: int, db: Session = Depends(get_db)):
    session = db.query(TestSession).filter(TestSession.id == test_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Test session not found.")

    links = db.query(TestQuestion).filter(TestQuestion.test_id == session.id).all()
    questions = [link.question for link in links]

    new_session = create_test_session(db, questions)

    ordered_links = (
        db.query(TestQuestion)
        .filter(TestQuestion.test_id == new_session.id)
        .order_by(TestQuestion.order_index)
        .all()
    )
    ordered_questions = [link.question for link in ordered_links]

    return RetryResponse(test_id=new_session.id, questions=ordered_questions)


@app.post("/api/tests/{test_id}/submit", response_model=SubmitResponse)
async def submit_test(
    test_id: int, payload: SubmitRequest, db: Session = Depends(get_db)
):
    session = db.query(TestSession).filter(TestSession.id == test_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Test session not found.")

    result = await evaluate_submission(db, session, payload.answers)

    return SubmitResponse(
        result_id=result.id,
        test_id=session.id,
        score=result.score,
        accuracy=result.accuracy,
        correct_count=result.correct_count,
        wrong_count=result.wrong_count,
        details=result.details or [],
    )


@app.post("/api/explanations", response_model=ExplanationResponse)
async def generate_explanation(
    payload: ExplanationRequest, db: Session = Depends(get_db)
):
    question = db.query(Question).filter(Question.id == payload.question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found.")

    explanation = explain_answer(
        question.text, question.options or {}, payload.correct_answer
    )

    return ExplanationResponse(question_id=question.id, explanation=explanation)
