from typing import List, Dict, Any
from services.llm_router import llm_router
from utils.prompt_loader import prompt_loader
from schemas.result_schema import ExamResult, LearningRecommendation

class LearningRecommender:
    """Generates personalized learning recommendations."""

    def __init__(self):
        pass

    def generate_recommendations(self, exam_result: ExamResult, time_available: int = 60) -> List[LearningRecommendation]:
        """
        Generate personalized learning recommendations.

        Args:
            exam_result: The exam result to analyze
            time_available: Available study time in minutes per day

        Returns:
            List of learning recommendations
        """
        # Get LLM-based recommendations
        llm_recommendations = self._get_llm_recommendations(exam_result, time_available)

        # Generate structured recommendations
        recommendations = []

        # Add topic-specific recommendations
        for topic in exam_result.weak_areas.topics[:3]:  # Focus on top 3 weak areas
            rec = LearningRecommendation(
                type="focus_topic",
                title=f"Strengthen {topic} Knowledge",
                description=f"Dedicated practice and review for {topic} concepts",
                priority="high",
                suggested_actions=[
                    f"Review {topic} lecture notes and key concepts",
                    f"Complete {topic} practice problems",
                    f"Watch tutorial videos on {topic}",
                    f"Create summary notes for {topic}"
                ],
                estimated_time_minutes=45
            )
            recommendations.append(rec)

        # Time management recommendations
        avg_time = exam_result.metrics.average_time_per_question
        if avg_time > 120:
            rec = LearningRecommendation(
                type="time_management",
                title="Improve Time Management",
                description="Develop strategies to solve problems more efficiently",
                priority="medium",
                suggested_actions=[
                    "Set time limits for practice questions",
                    "Identify steps that take the most time",
                    "Practice mental math and shortcuts",
                    "Use timers during study sessions"
                ],
                estimated_time_minutes=30
            )
            recommendations.append(rec)

        # General improvement recommendations
        accuracy = exam_result.metrics.accuracy_percentage
        if accuracy < 70:
            rec = LearningRecommendation(
                type="practice_more",
                title="Build Foundational Skills",
                description="Focus on fundamental concepts and basic problem-solving",
                priority="high",
                suggested_actions=[
                    "Review basic concepts and formulas",
                    "Practice with easier problems first",
                    "Use spaced repetition for key facts",
                    "Join study groups for peer learning"
                ],
                estimated_time_minutes=60
            )
            recommendations.append(rec)
        elif accuracy < 85:
            rec = LearningRecommendation(
                type="practice_more",
                title="Advance to Complex Problems",
                description="Work on application and analysis level problems",
                priority="medium",
                suggested_actions=[
                    "Solve multi-step problems",
                    "Practice with mixed topic questions",
                    "Analyze incorrect answers thoroughly",
                    "Simulate exam conditions"
                ],
                estimated_time_minutes=50
            )
            recommendations.append(rec)

        # Add LLM-generated recommendations if available
        if llm_recommendations:
            for llm_rec in llm_recommendations[:2]:  # Add top 2 LLM recommendations
                rec = LearningRecommendation(
                    type="llm_generated",
                    title=llm_rec.get('title', 'AI Recommendation'),
                    description=llm_rec.get('description', ''),
                    priority=llm_rec.get('priority', 'medium'),
                    suggested_actions=llm_rec.get('actions', []),
                    estimated_time_minutes=llm_rec.get('time', 30)
                )
                recommendations.append(rec)

        return recommendations

    def _get_llm_recommendations(self, exam_result: ExamResult, time_available: int) -> List[Dict[str, Any]]:
        """Get recommendations from LLM."""
        # Prepare data for LLM
        weak_areas = ", ".join(exam_result.weak_areas.topics) if exam_result.weak_areas.topics else "None"
        strong_areas = "General performance"  # Could be enhanced

        performance_summary = f"""
Accuracy: {exam_result.metrics.accuracy_percentage:.1f}%
Average time per question: {exam_result.metrics.average_time_per_question:.1f}s
Weak areas: {weak_areas}
"""

        prompt = prompt_loader.format_prompt(
            'analytics',
            'study_recommendations',
            weak_areas=weak_areas,
            strong_areas=strong_areas,
            time_available=time_available,
            exam_date="Next exam",  # Could be parameterized
            performance_summary=performance_summary
        )

        response = llm_router.route_request('learning_recommendations', prompt, max_tokens=300)

        # Parse response into structured recommendations
        return self._parse_llm_recommendations(response)

    def _parse_llm_recommendations(self, response: str) -> List[Dict[str, Any]]:
        """Parse LLM response into structured recommendations."""
        recommendations = []

        # Simple parsing - split by numbered items
        lines = response.split('\n')
        current_rec = None

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Check for numbered recommendations
            if line.startswith(('1.', '2.', '3.', '4.', '5.')):
                if current_rec:
                    recommendations.append(current_rec)

                title = line.split('.', 1)[1].strip()
                current_rec = {
                    'title': title,
                    'description': '',
                    'actions': [],
                    'priority': 'medium',
                    'time': 30
                }
            elif current_rec and line.startswith('-'):
                # Action item
                action = line[1:].strip()
                current_rec['actions'].append(action)
            elif current_rec:
                # Additional description
                if not current_rec['description']:
                    current_rec['description'] = line

        if current_rec:
            recommendations.append(current_rec)

        return recommendations

    def prioritize_recommendations(self, recommendations: List[LearningRecommendation]) -> List[LearningRecommendation]:
        """Prioritize recommendations based on various factors."""
        priority_order = {'high': 3, 'medium': 2, 'low': 1}

        return sorted(recommendations,
                     key=lambda x: priority_order.get(x.priority, 1),
                     reverse=True)

    def filter_by_time(self, recommendations: List[LearningRecommendation], available_time: int) -> List[LearningRecommendation]:
        """Filter recommendations that fit within available time."""
        return [rec for rec in recommendations if rec.estimated_time_minutes <= available_time]

# Global instance
learning_recommender = LearningRecommender()