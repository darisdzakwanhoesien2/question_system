from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
import uuid
from schemas.exam_schema import ExamSession, Exam, UserAnswer
from schemas.question_schema import Question
from core.timer import Timer
from utils.randomizer import generate_session_id
from config.settings import SETTINGS

class ExamSessionManager:
    def __init__(self):
        self.active_sessions: Dict[str, ExamSession] = {}
        self.timers: Dict[str, Timer] = {}

    def create_session(self, exam: Exam, user_id: Optional[str] = None) -> ExamSession:
        """Create a new exam session."""
        session_id = generate_session_id(12)

        # Calculate total time in seconds
        total_seconds = exam.total_time_minutes * 60

        session = ExamSession(
            session_id=session_id,
            exam_id=exam.id,
            user_id=user_id,
            start_time=datetime.now(),
            time_remaining_seconds=total_seconds
        )

        self.active_sessions[session_id] = session

        # Start timer
        timer = Timer(total_seconds)
        timer.start()
        self.timers[session_id] = timer

        return session

    def get_session(self, session_id: str) -> Optional[ExamSession]:
        """Get active session by ID."""
        return self.active_sessions.get(session_id)

    def submit_answer(self, session_id: str, question_id: str, answer: any) -> bool:
        """Submit answer for a question."""
        session = self.get_session(session_id)
        if not session or session.is_completed:
            return False

        user_answer = UserAnswer(
            question_id=question_id,
            answer=answer,
            timestamp=datetime.now().timestamp()
        )

        session.answers.append(user_answer)
        return True

    def get_remaining_time(self, session_id: str) -> int:
        """Get remaining time in seconds."""
        timer = self.timers.get(session_id)
        if timer:
            return timer.get_remaining_time()
        return 0

    def pause_session(self, session_id: str) -> bool:
        """Pause the exam session."""
        session = self.get_session(session_id)
        if not session or session.is_completed:
            return False

        session.is_paused = True
        timer = self.timers.get(session_id)
        if timer:
            timer.pause()

        return True

    def resume_session(self, session_id: str) -> bool:
        """Resume the exam session."""
        session = self.get_session(session_id)
        if not session or not session.is_paused:
            return False

        session.is_paused = False
        timer = self.timers.get(session_id)
        if timer:
            timer.resume()

        return True

    def end_session(self, session_id: str) -> Optional[ExamSession]:
        """End the exam session."""
        session = self.get_session(session_id)
        if not session or session.is_completed:
            return None

        session.end_time = datetime.now()
        session.is_completed = True

        timer = self.timers.get(session_id)
        if timer:
            timer.stop()

        # Remove from active sessions after some time
        # For now, keep for retrieval

        return session

    def get_current_question_index(self, session_id: str) -> int:
        """Get current question index."""
        session = self.get_session(session_id)
        return session.current_question_index if session else 0

    def set_current_question_index(self, session_id: str, index: int) -> bool:
        """Set current question index."""
        session = self.get_session(session_id)
        if not session or session.is_completed:
            return False

        session.current_question_index = index
        return True

    def get_answers_for_session(self, session_id: str) -> List[UserAnswer]:
        """Get all answers for a session."""
        session = self.get_session(session_id)
        return session.answers if session else []

    def cleanup_expired_sessions(self):
        """Clean up expired sessions (placeholder for future implementation)."""
        # In a real implementation, this would check for sessions that have timed out
        pass

# Global instance
session_manager = ExamSessionManager()