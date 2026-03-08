from typing import Dict, Any, Optional
import streamlit as st
from datetime import datetime
from schemas.exam_schema import ExamSession
from core.exam_session import session_manager

class SessionStateManager:
    def __init__(self):
        self._init_session_state()

    def _init_session_state(self):
        """Initialize session state variables."""
        if 'current_session' not in st.session_state:
            st.session_state.current_session = None

        if 'exam_data' not in st.session_state:
            st.session_state.exam_data = None

        if 'current_question_index' not in st.session_state:
            st.session_state.current_question_index = 0

        if 'answers' not in st.session_state:
            st.session_state.answers = {}

        if 'start_time' not in st.session_state:
            st.session_state.start_time = None

        if 'user_id' not in st.session_state:
            st.session_state.user_id = None

    def start_exam_session(self, exam_data: Dict[str, Any], user_id: Optional[str] = None) -> str:
        """Start a new exam session."""
        from core.exam_loader import exam_loader
        from schemas.exam_schema import Exam

        # Load exam object
        exam = exam_loader.load_exam(exam_data['type'], exam_data['set'])
        if not exam:
            raise ValueError("Exam not found")

        # Create session
        session = session_manager.create_session(exam, user_id)

        # Update session state
        st.session_state.current_session = session.session_id
        st.session_state.exam_data = exam_data
        st.session_state.current_question_index = 0
        st.session_state.answers = {}
        st.session_state.start_time = datetime.now()

        return session.session_id

    def get_current_session_id(self) -> Optional[str]:
        """Get current session ID."""
        return st.session_state.get('current_session')

    def get_current_session(self) -> Optional[ExamSession]:
        """Get current exam session."""
        session_id = self.get_current_session_id()
        if session_id:
            return session_manager.get_session(session_id)
        return None

    def submit_answer(self, question_index: int, answer: Any) -> bool:
        """Submit answer for current question."""
        session_id = self.get_current_session_id()
        if not session_id:
            return False

        session = self.get_current_session()
        if not session:
            return False

        # Get question ID
        from core.question_router import question_router
        from core.exam_loader import exam_loader

        exam = exam_loader.load_exam(
            st.session_state.exam_data['type'],
            st.session_state.exam_data['set']
        )

        if not exam:
            return False

        question = question_router.get_question_by_index(exam, question_index)
        if not question:
            return False

        # Submit to session manager
        success = session_manager.submit_answer(session_id, question.id, answer)

        if success:
            # Update local state
            st.session_state.answers[question_index] = answer

        return success

    def get_answer(self, question_index: int) -> Optional[Any]:
        """Get answer for a question."""
        return st.session_state.answers.get(question_index)

    def get_current_question_index(self) -> int:
        """Get current question index."""
        return st.session_state.get('current_question_index', 0)

    def set_current_question_index(self, index: int):
        """Set current question index."""
        st.session_state.current_question_index = index
        session_manager.set_current_question_index(
            self.get_current_session_id(),
            index
        )

    def get_remaining_time(self) -> int:
        """Get remaining time in seconds."""
        session_id = self.get_current_session_id()
        if session_id:
            return session_manager.get_remaining_time(session_id)
        return 0

    def pause_session(self) -> bool:
        """Pause the current session."""
        session_id = self.get_current_session_id()
        if session_id:
            return session_manager.pause_session(session_id)
        return False

    def resume_session(self) -> bool:
        """Resume the current session."""
        session_id = self.get_current_session_id()
        if session_id:
            return session_manager.resume_session(session_id)
        return False

    def end_session(self) -> Optional[ExamSession]:
        """End the current session."""
        session_id = self.get_current_session_id()
        if session_id:
            session = session_manager.end_session(session_id)

            # Clear session state
            self.clear_session()

            return session
        return None

    def clear_session(self):
        """Clear all session state."""
        st.session_state.current_session = None
        st.session_state.exam_data = None
        st.session_state.current_question_index = 0
        st.session_state.answers = {}
        st.session_state.start_time = None

    def is_session_active(self) -> bool:
        """Check if there's an active session."""
        session_id = self.get_current_session_id()
        if not session_id:
            return False

        session = session_manager.get_session(session_id)
        return session is not None and not session.is_completed

    def get_session_progress(self) -> Dict[str, Any]:
        """Get session progress information."""
        total_questions = 0
        answered_questions = len(st.session_state.answers)

        if st.session_state.exam_data:
            from core.exam_loader import exam_loader
            exam = exam_loader.load_exam(
                st.session_state.exam_data['type'],
                st.session_state.exam_data['set']
            )
            if exam:
                from core.question_router import question_router
                total_questions = question_router.get_total_questions(exam)

        return {
            'current_index': self.get_current_question_index(),
            'total_questions': total_questions,
            'answered_questions': answered_questions,
            'remaining_questions': total_questions - answered_questions,
            'progress_percentage': (answered_questions / total_questions * 100) if total_questions > 0 else 0
        }

# Global instance
session_state_manager = SessionStateManager()