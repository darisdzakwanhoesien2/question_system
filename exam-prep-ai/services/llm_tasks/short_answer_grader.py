from typing import Dict, Any, Optional
from services.llm_router import llm_router
from utils.prompt_loader import prompt_loader
from utils.text_processing import calculate_similarity_score, normalize_answer
from schemas.question_schema import Question, UserAnswer

class ShortAnswerGrader:
    """Handles short answer grading using LLM and similarity."""

    def __init__(self):
        pass

    def grade_answer(self, question: Question, user_answer: UserAnswer) -> Dict[str, Any]:
        """
        Grade a short answer.

        Returns dict with score (0-1), feedback, and analysis.
        """
        if not user_answer.answer or not isinstance(user_answer.answer, str):
            return {
                'score': 0.0,
                'feedback': 'No answer provided',
                'method': 'empty'
            }

        user_text = user_answer.answer.strip()
        if not user_text:
            return {
                'score': 0.0,
                'feedback': 'No answer provided',
                'method': 'empty'
            }

        # If no sample answer, use basic validation
        if not question.sample_answer:
            return self._basic_grading(user_text)

        # Use LLM for semantic equivalence
        llm_score = self._llm_semantic_grading(question, user_answer)

        # Also calculate text similarity as backup
        similarity = calculate_similarity_score(
            normalize_answer(question.sample_answer),
            normalize_answer(user_text)
        )

        # Combine scores (weighted average)
        final_score = (llm_score * 0.7) + (similarity * 0.3)

        return {
            'score': final_score,
            'feedback': self._generate_feedback(final_score, question.sample_answer),
            'method': 'llm_semantic',
            'llm_score': llm_score,
            'similarity_score': similarity
        }

    def _llm_semantic_grading(self, question: Question, user_answer: UserAnswer) -> float:
        """Use LLM to check semantic equivalence."""
        prompt = prompt_loader.format_prompt(
            'short_answer',
            'semantic_equivalence',
            correct_answer=question.sample_answer,
            student_answer=user_answer.answer
        )

        response = llm_router.route_request('short_answer_grading', prompt, max_tokens=50)

        # Parse score from response
        response = response.strip()
        try:
            # Look for a number at the end
            lines = response.split('\n')
            last_line = lines[-1]
            # Extract number
            import re
            numbers = re.findall(r'(\d+\.?\d*)', last_line)
            if numbers:
                score = float(numbers[-1])
                return min(1.0, max(0.0, score))
        except (ValueError, IndexError):
            pass

        return 0.5  # Default if parsing fails

    def _basic_grading(self, user_text: str) -> Dict[str, Any]:
        """Basic grading when no sample answer available."""
        word_count = len(user_text.split())

        if word_count < 3:
            return {
                'score': 0.2,
                'feedback': 'Answer is too brief',
                'method': 'basic'
            }
        elif word_count > 50:
            return {
                'score': 0.8,
                'feedback': 'Detailed answer provided',
                'method': 'basic'
            }
        else:
            return {
                'score': 0.6,
                'feedback': 'Reasonable answer length',
                'method': 'basic'
            }

    def _generate_feedback(self, score: float, sample_answer: str) -> str:
        """Generate feedback based on score."""
        if score >= 0.9:
            return "Excellent answer! Very accurate and well-expressed."
        elif score >= 0.8:
            return "Very good answer with minor differences from the ideal response."
        elif score >= 0.7:
            return "Good answer that captures most of the key points."
        elif score >= 0.6:
            return "Fair answer with some correct elements but missing key points."
        elif score >= 0.4:
            return f"Partial credit. Compare with sample: {sample_answer}"
        else:
            return f"Incorrect or incomplete. Sample answer: {sample_answer}"

# Global instance
short_answer_grader = ShortAnswerGrader()