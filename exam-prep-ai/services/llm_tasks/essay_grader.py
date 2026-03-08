from typing import Dict, Any, Optional
from services.llm_router import llm_router
from utils.prompt_loader import prompt_loader
from schemas.question_schema import Question, UserAnswer

class EssayGrader:
    """Handles essay grading using LLM."""

    def __init__(self):
        pass

    def grade_essay(self, question: Question, user_answer: UserAnswer) -> Dict[str, Any]:
        """
        Grade an essay answer.

        Returns dict with score (0-1), feedback, and detailed analysis.
        """
        if not user_answer.answer or not isinstance(user_answer.answer, str):
            return {
                'score': 0.0,
                'feedback': 'No essay submitted',
                'analysis': 'Empty submission'
            }

        essay_text = user_answer.answer.strip()
        if len(essay_text) < 50:  # Very short essay
            return {
                'score': 0.1,
                'feedback': 'Essay is too short to evaluate properly',
                'analysis': 'Insufficient length for meaningful assessment'
            }

        # Prepare rubric text
        rubric_text = ""
        if question.rubric:
            rubric_items = []
            for criterion, description in question.rubric.items():
                rubric_items.append(f"- {criterion}: {description}")
            rubric_text = "\n".join(rubric_items)

        # Generate grading prompt
        prompt = prompt_loader.format_prompt(
            'essay_grading',
            'rubric_grading',
            question_text=question.question_text,
            essay_text=essay_text,
            rubric_criteria=rubric_text
        )

        # Get LLM response
        response = llm_router.route_request('essay_grading', prompt, max_tokens=500)

        # Parse response
        return self._parse_grading_response(response)

    def generate_feedback(self, question: Question, user_answer: UserAnswer, score: float) -> str:
        """Generate detailed feedback for essay."""
        prompt = prompt_loader.format_prompt(
            'essay_grading',
            'feedback_generation',
            question_text=question.question_text,
            essay_text=user_answer.answer,
            score_percentage=score * 100,
            topic_breakdown="Essay analysis",
            weak_areas="General writing areas"
        )

        return llm_router.route_request('essay_grading', prompt, max_tokens=300)

    def _parse_grading_response(self, response: str) -> Dict[str, Any]:
        """Parse LLM grading response."""
        response = response.strip()

        # Extract score
        score = 0.5  # Default
        lines = response.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('SCORE:'):
                try:
                    score_text = line.split(':', 1)[1].strip()
                    # Convert 0-6 scale to 0-1
                    numeric_score = float(score_text)
                    score = min(1.0, max(0.0, numeric_score / 6.0))
                    break
                except (ValueError, IndexError):
                    pass

        # Extract feedback
        feedback = ""
        suggestions = ""

        # Find FEEDBACK section
        feedback_start = response.find('FEEDBACK:')
        suggestions_start = response.find('SUGGESTIONS:')

        if feedback_start != -1:
            if suggestions_start != -1:
                feedback = response[feedback_start + 9:suggestions_start].strip()
            else:
                feedback = response[feedback_start + 9:].strip()

        if suggestions_start != -1:
            suggestions = response[suggestions_start + 12:].strip()

        return {
            'score': score,
            'feedback': feedback or 'No specific feedback provided',
            'suggestions': suggestions or 'No suggestions provided',
            'raw_response': response
        }

# Global instance
essay_grader = EssayGrader()