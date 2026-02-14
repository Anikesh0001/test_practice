from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class QuestionOut(BaseModel):
    id: int
    number: int
    text: str
    options: Optional[Dict[str, str]] = None

    class Config:
        from_attributes = True


class UploadResponse(BaseModel):
    test_id: int
    questions: List[QuestionOut]


class StartTestRequest(BaseModel):
    duration_minutes: int = Field(..., ge=1, le=240)


class StartTestResponse(BaseModel):
    test_id: int
    duration_minutes: int
    questions: List[QuestionOut]


class SubmitRequest(BaseModel):
    answers: Dict[int, Optional[str]]


class ResultDetail(BaseModel):
    question_id: int
    user_answer: Optional[str]
    correct_answer: str
    is_correct: bool
    explanation: str


class SubmitResponse(BaseModel):
    result_id: int
    test_id: int
    score: float
    accuracy: float
    correct_count: int
    wrong_count: int
    details: List[ResultDetail]


class ExplanationRequest(BaseModel):
    question_id: int
    correct_answer: str


class ExplanationResponse(BaseModel):
    question_id: int
    explanation: str


class RetryResponse(BaseModel):
    test_id: int
    questions: List[QuestionOut]
