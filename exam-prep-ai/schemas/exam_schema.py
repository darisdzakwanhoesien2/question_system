from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from .question_schema import Question, QuestionResult, UserAnswer

class ExamSection(BaseModel):
    name: str
    questions: List[Question]
    time_limit_minutes: Optional[int] = None
    instructions: Optional[str] = None

class Exam(BaseModel):
    id: str
    name: str
    type: str  # sat, gre, toefl
    version: str = "1.0"
    total_questions: int
    total_time_minutes: int
    sections: List[ExamSection]
    instructions: Optional[str] = None
    passing_score: Optional[float] = None  # percentage

class ExamSession(BaseModel):
    session_id: str
    exam_id: str
    user_id: Optional[str] = None
    start_time: datetime
    end_time: Optional[datetime] = None
    current_question_index: int = 0
    answers: List[UserAnswer] = []
    time_remaining_seconds: int
    is_completed: bool = False
    is_paused: bool = False

class ExamAttempt(BaseModel):
    session_id: str
    exam: Exam
    results: List[QuestionResult]
    total_score: float
    percentage_score: float
    time_taken_minutes: int
    completed_at: datetime
    analytics: Optional[Dict[str, Any]] = None