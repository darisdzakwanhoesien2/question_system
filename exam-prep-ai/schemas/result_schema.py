from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
from .exam_schema import ExamAttempt

class PerformanceMetrics(BaseModel):
    total_questions: int
    correct_answers: int
    incorrect_answers: int
    unanswered: int
    accuracy_percentage: float
    average_time_per_question: float
    total_time_taken: int

class TopicPerformance(BaseModel):
    topic: str
    questions_count: int
    correct_count: int
    accuracy: float
    average_time: float

class WeakAreas(BaseModel):
    topics: List[str]
    question_types: List[str]
    recommendations: List[str]

class ExamResult(BaseModel):
    attempt_id: str
    exam_id: str
    exam_name: str
    user_id: Optional[str] = None
    completed_at: datetime
    metrics: PerformanceMetrics
    topic_performance: List[TopicPerformance]
    weak_areas: WeakAreas
    overall_feedback: Optional[str] = None
    score_breakdown: Dict[str, float]

class AnalyticsSummary(BaseModel):
    total_exams_taken: int
    average_score: float
    improvement_trend: List[float]  # scores over time
    favorite_topics: List[str]
    struggling_topics: List[str]
    time_management_score: float
    consistency_score: float

class LearningRecommendation(BaseModel):
    type: str  # focus_topic, practice_more, time_management, etc.
    title: str
    description: str
    priority: str  # high, medium, low
    suggested_actions: List[str]
    estimated_time_minutes: int