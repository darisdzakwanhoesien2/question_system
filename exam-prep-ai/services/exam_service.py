from typing import List, Dict, Optional, Any
from pathlib import Path
from datetime import datetime
from schemas.exam_schema import Exam, ExamAttempt, ExamSession
from schemas.result_schema import ExamResult
from core.exam_loader import exam_loader
from core.scoring_engine import scoring_engine
from utils.file_utils import save_json_file, load_json_file
from config.settings import SETTINGS

class ExamService:
    def __init__(self):
        self.results_dir = SETTINGS['storage_dir'] / 'results'
        self.sessions_dir = SETTINGS['storage_dir'] / 'exam_sessions'
        self.results_dir.mkdir(exist_ok=True)
        self.sessions_dir.mkdir(exist_ok=True)

    def get_available_exams(self) -> Dict[str, List[str]]:
        """Get all available exams."""
        return exam_loader.get_available_exams()

    def get_exam(self, exam_type: str, set_name: str) -> Optional[Exam]:
        """Get exam by type and set."""
        return exam_loader.load_exam(exam_type, set_name)

    def get_exam_info(self, exam_type: str, set_name: str) -> Optional[Dict[str, Any]]:
        """Get basic exam information."""
        return exam_loader.get_exam_info(exam_type, set_name)

    def start_exam_session(self, exam: Exam, user_id: Optional[str] = None) -> ExamSession:
        """Start a new exam session."""
        from core.exam_session import session_manager
        return session_manager.create_session(exam, user_id)

    def submit_exam_attempt(self, session: ExamSession) -> ExamAttempt:
        """Process completed exam attempt and generate results."""
        from core.question_router import question_router
        from schemas.question_schema import QuestionResult

        exam = exam_loader.load_exam(session.exam_id.split('_')[0], session.exam_id.split('_')[1])
        if not exam:
            raise ValueError(f"Exam {session.exam_id} not found")

        # Score all answers
        results = []
        total_score = 0

        for user_answer in session.answers:
            question = question_router.get_question_by_index(exam, 0)  # Simplified
            if question:
                result = scoring_engine.score_answer(question, user_answer)
                results.append(result)
                total_score += result.score

        # Calculate metrics
        total_questions = len(results)
        correct_answers = sum(1 for r in results if r.score >= 0.8)  # 80% threshold
        accuracy = correct_answers / total_questions if total_questions > 0 else 0

        # Create attempt
        attempt = ExamAttempt(
            session_id=session.session_id,
            exam=exam,
            results=results,
            total_score=total_score,
            percentage_score=accuracy * 100,
            time_taken_minutes=(session.end_time - session.start_time).total_seconds() / 60,
            completed_at=session.end_time or datetime.now()
        )

        # Save attempt
        self._save_exam_attempt(attempt)

        return attempt

    def get_exam_results(self, user_id: Optional[str] = None) -> List[ExamResult]:
        """Get exam results, optionally filtered by user."""
        results = []

        for result_file in self.results_dir.glob('*.json'):
            result_data = load_json_file(result_file)

            if user_id and result_data.get('user_id') != user_id:
                continue

            # Convert to ExamResult object
            results.append(self._dict_to_exam_result(result_data))

        return sorted(results, key=lambda x: x.completed_at, reverse=True)

    def get_exam_result(self, attempt_id: str) -> Optional[ExamResult]:
        """Get specific exam result."""
        result_file = self.results_dir / f"{attempt_id}.json"
        if not result_file.exists():
            return None

        result_data = load_json_file(result_file)
        return self._dict_to_exam_result(result_data)

    def _save_exam_attempt(self, attempt: ExamAttempt):
        """Save exam attempt to storage."""
        result_data = {
            'attempt_id': attempt.session_id,
            'exam_id': attempt.exam.id,
            'exam_name': attempt.exam.name,
            'user_id': None,  # Add user management later
            'completed_at': attempt.completed_at.isoformat(),
            'total_score': attempt.total_score,
            'percentage_score': attempt.percentage_score,
            'time_taken_minutes': attempt.time_taken_minutes,
            'results': [
                {
                    'question_id': r.question_id,
                    'score': r.score,
                    'feedback': r.feedback,
                    'graded_by': r.graded_by
                } for r in attempt.results
            ]
        }

        save_json_file(result_data, self.results_dir / f"{attempt.session_id}.json")

    def _dict_to_exam_result(self, data: Dict[str, Any]) -> ExamResult:
        """Convert dictionary to ExamResult object."""
        from schemas.result_schema import PerformanceMetrics, TopicPerformance, WeakAreas

        # Create metrics
        results = data.get('results', [])
        total_questions = len(results)
        correct_answers = sum(1 for r in results if r.get('score', 0) >= 0.8)

        metrics = PerformanceMetrics(
            total_questions=total_questions,
            correct_answers=correct_answers,
            incorrect_answers=total_questions - correct_answers,
            unanswered=0,  # Simplified
            accuracy_percentage=data.get('percentage_score', 0),
            average_time_per_question=data.get('time_taken_minutes', 0) / total_questions if total_questions > 0 else 0,
            total_time_taken=data.get('time_taken_minutes', 0)
        )

        # Placeholder for other fields
        topic_performance = []
        weak_areas = WeakAreas(topics=[], question_types=[], recommendations=[])

        return ExamResult(
            attempt_id=data['attempt_id'],
            exam_id=data['exam_id'],
            exam_name=data['exam_name'],
            user_id=data.get('user_id'),
            completed_at=datetime.fromisoformat(data['completed_at']),
            metrics=metrics,
            topic_performance=topic_performance,
            weak_areas=weak_areas,
            overall_feedback=None,
            score_breakdown={'total': data.get('percentage_score', 0)}
        )

# Global instance
exam_service = ExamService()