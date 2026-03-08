from pydantic import BaseModel, Field
from typing import List, Optional, Union, Dict, Any
from enum import Enum

class QuestionType(str, Enum):
    MCQ = "mcq"
    SHORT_ANSWER = "short_answer"
    ESSAY = "essay"

class MCQOption(BaseModel):
    text: str
    is_correct: bool = False

class Question(BaseModel):
    id: str
    type: QuestionType
    question_text: str
    explanation: Optional[str] = None
    difficulty: str = "medium"  # easy, medium, hard
    topic: str = ""
    subtopic: Optional[str] = None

    # MCQ specific
    options: Optional[List[MCQOption]] = None

    # Short answer/Essay specific
    sample_answer: Optional[str] = None
    rubric: Optional[Dict[str, Any]] = None
    max_length: Optional[int] = None

    # Metadata
    points: int = 1
    time_estimate_seconds: Optional[int] = None

class UserAnswer(BaseModel):
    question_id: str
    answer: Union[str, List[str], None]  # str for text, list for multiple choices
    timestamp: Optional[float] = None
    time_spent_seconds: Optional[int] = None

class QuestionResult(BaseModel):
    question_id: str
    user_answer: UserAnswer
    correct_answer: Optional[Union[str, List[str]]] = None
    score: float  # 0.0 to 1.0
    feedback: Optional[str] = None
    graded_by: str = "auto"  # auto, manual, llm
    grading_details: Optional[Dict[str, Any]] = None