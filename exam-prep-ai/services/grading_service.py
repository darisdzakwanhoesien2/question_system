from typing import List, Dict, Any, Optional
from schemas.question_schema import Question, QuestionResult, UserAnswer
from schemas.result_schema import ExamResult
from core.scoring_engine import scoring_engine
from services.llm_service import LLMService
from utils.prompt_loader import prompt_loader

class GradingService:
    def __init__(self, llm_service: Optional[LLMService] = None):
        self.llm_service = llm_service

    def grade_question(self, question: Question, user_answer: UserAnswer) -> QuestionResult:
        """Grade a single question answer."""
        return scoring_engine.score_answer(question, user_answer)

    def grade_exam_answers(self, questions: List[Question], answers: List[UserAnswer]) -> List[QuestionResult]:
        """Grade all answers for an exam."""
        results = []

        for question, answer in zip(questions, answers):
            result = self.grade_question(question, answer)
            results.append(result)

        return results

    def generate_feedback(self, exam_result: ExamResult) -> str:
        """Generate overall feedback for exam performance."""
        if not self.llm_service:
            return self._generate_basic_feedback(exam_result)

        try:
            prompt = prompt_loader.format_prompt(
                'essay_grading',
                'feedback_generation',
                total_questions=exam_result.metrics.total_questions,
                correct_answers=exam_result.metrics.correct_answers,
                score_percentage=exam_result.metrics.accuracy_percentage,
                topic_breakdown="Topics: General performance analysis",
                weak_areas=", ".join(exam_result.weak_areas.topics)
            )

            return self.llm_service.generate(prompt, max_tokens=300)
        except Exception as e:
            print(f"LLM feedback generation failed: {e}")
            return self._generate_basic_feedback(exam_result)

    def explain_wrong_answer(self, question: Question, user_answer: UserAnswer) -> str:
        """Generate explanation for wrong answer."""
        if not self.llm_service:
            return "Incorrect answer. Please review the question and try again."

        try:
            prompt = prompt_loader.format_prompt(
                'tutoring',
                'explain_wrong_answer',
                question_text=question.question_text,
                student_answer=user_answer.answer,
                correct_answer=question.sample_answer or "See explanation",
                explanation=question.explanation or "Review the material"
            )

            return self.llm_service.generate(prompt, max_tokens=200)
        except Exception as e:
            print(f"Answer explanation failed: {e}")
            return question.explanation or "Please review the correct answer."

    def generate_study_recommendations(self, exam_result: ExamResult) -> List[str]:
        """Generate personalized study recommendations."""
        recommendations = []

        # Basic recommendations based on performance
        accuracy = exam_result.metrics.accuracy_percentage

        if accuracy < 60:
            recommendations.append("Focus on fundamental concepts and practice basic problems")
        elif accuracy < 80:
            recommendations.append("Work on understanding complex topics and application problems")
        else:
            recommendations.append("Challenge yourself with advanced problems and time management")

        # Add topic-specific recommendations
        if exam_result.weak_areas.topics:
            recommendations.append(f"Review these topics: {', '.join(exam_result.weak_areas.topics)}")

        # Time management
        avg_time = exam_result.metrics.average_time_per_question
        if avg_time > 120:  # More than 2 minutes per question
            recommendations.append("Practice time management and work on solving problems faster")

        return recommendations

    def _generate_basic_feedback(self, exam_result: ExamResult) -> str:
        """Generate basic feedback without LLM."""
        accuracy = exam_result.metrics.accuracy_percentage

        if accuracy >= 90:
            return "Excellent performance! You have a strong understanding of the material."
        elif accuracy >= 80:
            return "Very good performance! Continue practicing to maintain this level."
        elif accuracy >= 70:
            return "Good performance. Focus on weak areas to improve further."
        elif accuracy >= 60:
            return "Satisfactory performance. More practice is needed in several areas."
        else:
            return "Performance needs improvement. Consider reviewing fundamental concepts."

    def calculate_performance_metrics(self, results: List[QuestionResult]) -> Dict[str, Any]:
        """Calculate detailed performance metrics."""
        if not results:
            return {}

        total_questions = len(results)
        correct_answers = sum(1 for r in results if r.score >= 0.8)
        total_score = sum(r.score for r in results)

        return {
            'total_questions': total_questions,
            'correct_answers': correct_answers,
            'incorrect_answers': total_questions - correct_answers,
            'accuracy_percentage': (correct_answers / total_questions) * 100 if total_questions > 0 else 0,
            'average_score': total_score / total_questions if total_questions > 0 else 0,
            'total_score': total_score
        }

    def identify_weak_areas(self, results: List[QuestionResult], questions: List[Question]) -> Dict[str, Any]:
        """Identify weak areas based on performance."""
        topic_performance = {}
        question_type_performance = {}

        for result, question in zip(results, questions):
            # By topic
            topic = question.topic
            if topic not in topic_performance:
                topic_performance[topic] = {'correct': 0, 'total': 0}
            topic_performance[topic]['total'] += 1
            if result.score >= 0.8:
                topic_performance[topic]['correct'] += 1

            # By question type
            q_type = question.type.value
            if q_type not in question_type_performance:
                question_type_performance[q_type] = {'correct': 0, 'total': 0}
            question_type_performance[q_type]['total'] += 1
            if result.score >= 0.8:
                question_type_performance[q_type]['correct'] += 1

        # Find weak topics (accuracy < 70%)
        weak_topics = []
        for topic, perf in topic_performance.items():
            accuracy = (perf['correct'] / perf['total']) * 100 if perf['total'] > 0 else 0
            if accuracy < 70:
                weak_topics.append(topic)

        weak_types = []
        for q_type, perf in question_type_performance.items():
            accuracy = (perf['correct'] / perf['total']) * 100 if perf['total'] > 0 else 0
            if accuracy < 70:
                weak_types.append(q_type)

        return {
            'weak_topics': weak_topics,
            'weak_question_types': weak_types,
            'topic_performance': topic_performance,
            'question_type_performance': question_type_performance
        }

# Global instance
grading_service = GradingService()