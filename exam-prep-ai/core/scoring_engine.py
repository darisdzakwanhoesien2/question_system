from typing import Dict, Any, Optional, List
from schemas.question_schema import Question, QuestionType, UserAnswer, QuestionResult
from schemas.exam_schema import Exam
from services.llm_service import LLMService
from utils.text_processing import calculate_similarity_score, normalize_answer
from config.settings import SETTINGS

class ScoringEngine:
    def __init__(self, llm_service: Optional[LLMService] = None):
        self.llm_service = llm_service

    def score_answer(self, question: Question, user_answer: UserAnswer) -> QuestionResult:
        """Score a user's answer for a question."""
        if question.type == QuestionType.MCQ:
            score = self._score_mcq(question, user_answer)
            feedback = self._get_mcq_feedback(question, user_answer, score)
        elif question.type == QuestionType.SHORT_ANSWER:
            score = self._score_short_answer(question, user_answer)
            feedback = self._get_short_answer_feedback(question, user_answer, score)
        elif question.type == QuestionType.ESSAY:
            score = self._score_essay(question, user_answer)
            feedback = self._get_essay_feedback(question, user_answer, score)
        else:
            score = 0.0
            feedback = "Unknown question type"

        result = QuestionResult(
            question_id=question.id,
            user_answer=user_answer,
            score=score,
            feedback=feedback,
            grading_details=self._get_grading_details(question, user_answer, score)
        )

        return result

    def _score_mcq(self, question: Question, user_answer: UserAnswer) -> float:
        """Score multiple choice question."""
        if not question.options:
            return 0.0

        # Find correct option
        correct_option = None
        for option in question.options:
            if option.is_correct:
                correct_option = option
                break

        if not correct_option:
            return 0.0

        # Check if user's answer matches correct option
        user_text = user_answer.answer
        if isinstance(user_text, str) and user_text.strip() == correct_option.text.strip():
            return 1.0
        elif isinstance(user_text, list) and len(user_text) == 1 and user_text[0] == correct_option.text:
            return 1.0

        return 0.0

    def _score_short_answer(self, question: Question, user_answer: UserAnswer) -> float:
        """Score short answer question using semantic similarity."""
        if not question.sample_answer:
            return 0.0

        user_text = user_answer.answer
        if not isinstance(user_text, str):
            return 0.0

        # Normalize answers
        correct_norm = normalize_answer(question.sample_answer)
        user_norm = normalize_answer(user_text)

        # Calculate similarity
        similarity = calculate_similarity_score(correct_norm, user_norm)

        # Use LLM for more accurate scoring if available
        if self.llm_service:
            try:
                llm_score = self._llm_score_short_answer(question, user_answer)
                # Combine similarity and LLM score
                return (similarity + llm_score) / 2
            except Exception:
                pass

        return similarity

    def _score_essay(self, question: Question, user_answer: UserAnswer) -> float:
        """Score essay question using LLM."""
        if not self.llm_service:
            # Fallback to basic length-based scoring
            user_text = user_answer.answer
            if not isinstance(user_text, str):
                return 0.0

            word_count = len(user_text.split())
            min_words = 100  # Assume minimum essay length

            if word_count < min_words:
                return max(0.1, word_count / min_words)
            else:
                return min(1.0, word_count / 500)  # Cap at 500 words

        try:
            return self._llm_score_essay(question, user_answer)
        except Exception:
            return 0.5  # Default score on error

    def _llm_score_short_answer(self, question: Question, user_answer: UserAnswer) -> float:
        """Use LLM to score short answer."""
        from utils.prompt_loader import prompt_loader

        prompt = prompt_loader.format_prompt(
            'short_answer',
            'semantic_equivalence',
            correct_answer=question.sample_answer,
            student_answer=user_answer.answer
        )

        response = self.llm_service.generate(prompt, max_tokens=50)
        try:
            score = float(response.strip())
            return max(0.0, min(1.0, score))
        except ValueError:
            return 0.5

    def _llm_score_essay(self, question: Question, user_answer: UserAnswer) -> float:
        """Use LLM to score essay."""
        from utils.prompt_loader import prompt_loader

        rubric_text = ""
        if question.rubric:
            rubric_text = "\n".join([f"- {k}: {v}" for k, v in question.rubric.items()])

        prompt = prompt_loader.format_prompt(
            'essay_grading',
            'rubric_grading',
            question_text=question.question_text,
            essay_text=user_answer.answer,
            rubric_criteria=rubric_text
        )

        response = self.llm_service.generate(prompt, max_tokens=500)

        # Parse score from response
        lines = response.split('\n')
        for line in lines:
            if line.startswith('SCORE:'):
                try:
                    score_text = line.split(':', 1)[1].strip()
                    score = float(score_text) / 6.0  # Convert 0-6 scale to 0-1
                    return max(0.0, min(1.0, score))
                except (ValueError, IndexError):
                    break

        return 0.5  # Default if parsing fails

    def _get_mcq_feedback(self, question: Question, user_answer: UserAnswer, score: float) -> str:
        """Get feedback for MCQ."""
        if score == 1.0:
            return "Correct! " + (question.explanation or "")
        else:
            correct_option = None
            for option in question.options or []:
                if option.is_correct:
                    correct_option = option
                    break

            feedback = f"Incorrect. The correct answer is: {correct_option.text if correct_option else 'N/A'}"
            if question.explanation:
                feedback += f"\n\nExplanation: {question.explanation}"
            return feedback

    def _get_short_answer_feedback(self, question: Question, user_answer: UserAnswer, score: float) -> str:
        """Get feedback for short answer."""
        if score >= 0.8:
            return "Excellent answer! Well done."
        elif score >= 0.6:
            return f"Good answer, but could be more precise. Sample answer: {question.sample_answer}"
        else:
            return f"Your answer needs improvement. Sample answer: {question.sample_answer}"

    def _get_essay_feedback(self, question: Question, user_answer: UserAnswer, score: float) -> str:
        """Get feedback for essay."""
        if self.llm_service:
            try:
                from utils.prompt_loader import prompt_loader

                prompt = prompt_loader.format_prompt(
                    'essay_grading',
                    'feedback_generation',
                    question_text=question.question_text,
                    essay_text=user_answer.answer,
                    score_percentage=score * 100
                )

                return self.llm_service.generate(prompt, max_tokens=300)
            except Exception:
                pass

        # Fallback feedback
        if score >= 0.8:
            return "Excellent essay with strong analysis and clear organization."
        elif score >= 0.6:
            return "Good essay, but could benefit from more detailed analysis and examples."
        else:
            return "Your essay needs more development. Focus on providing specific examples and clear organization."

    def _get_grading_details(self, question: Question, user_answer: UserAnswer, score: float) -> Dict[str, Any]:
        """Get detailed grading information."""
        return {
            'question_type': question.type.value,
            'scoring_method': 'llm' if self.llm_service else 'automated',
            'raw_score': score,
            'max_score': 1.0,
            'graded_at': user_answer.timestamp
        }

# Global instance
scoring_engine = ScoringEngine()