from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import pandas as pd
from schemas.result_schema import ExamResult, AnalyticsSummary, LearningRecommendation
from services.exam_service import exam_service
from services.llm_service import LLMService
from utils.prompt_loader import prompt_loader

class AnalyticsService:
    def __init__(self, llm_service: Optional[LLMService] = None):
        self.llm_service = llm_service

    def generate_analytics_summary(self, user_id: Optional[str] = None) -> AnalyticsSummary:
        """Generate comprehensive analytics summary for user."""
        exam_results = exam_service.get_exam_results(user_id)

        if not exam_results:
            return AnalyticsSummary(
                total_exams_taken=0,
                average_score=0.0,
                improvement_trend=[],
                favorite_topics=[],
                struggling_topics=[],
                time_management_score=0.0,
                consistency_score=0.0
            )

        # Calculate metrics
        scores = [r.metrics.accuracy_percentage for r in exam_results]
        average_score = sum(scores) / len(scores) if scores else 0

        # Improvement trend (last 5 exams)
        improvement_trend = scores[-5:] if len(scores) >= 5 else scores

        # Topic analysis
        topic_performance = self._analyze_topic_performance(exam_results)
        favorite_topics = sorted(topic_performance.keys(),
                               key=lambda x: topic_performance[x]['avg_score'],
                               reverse=True)[:3]
        struggling_topics = sorted(topic_performance.keys(),
                                 key=lambda x: topic_performance[x]['avg_score'])[:3]

        # Time management score
        time_scores = [self._calculate_time_efficiency(r) for r in exam_results]
        time_management_score = sum(time_scores) / len(time_scores) if time_scores else 0

        # Consistency score (inverse of score variance)
        if len(scores) > 1:
            variance = sum((s - average_score) ** 2 for s in scores) / len(scores)
            consistency_score = max(0, 100 - variance)  # Higher consistency = lower variance
        else:
            consistency_score = 100

        return AnalyticsSummary(
            total_exams_taken=len(exam_results),
            average_score=average_score,
            improvement_trend=improvement_trend,
            favorite_topics=favorite_topics,
            struggling_topics=struggling_topics,
            time_management_score=time_management_score,
            consistency_score=consistency_score
        )

    def generate_performance_analysis(self, exam_result: ExamResult) -> str:
        """Generate detailed performance analysis."""
        if not self.llm_service:
            return self._generate_basic_analysis(exam_result)

        try:
            # Prepare performance data
            perf_data = f"""
Total Questions: {exam_result.metrics.total_questions}
Correct Answers: {exam_result.metrics.correct_answers}
Accuracy: {exam_result.metrics.accuracy_percentage:.1f}%
Average Time per Question: {exam_result.metrics.average_time_per_question:.1f}s
Total Time: {exam_result.metrics.total_time_taken:.1f}min
"""

            prompt = prompt_loader.format_prompt(
                'analytics',
                'performance_analysis',
                performance_data=perf_data
            )

            return self.llm_service.generate(prompt, max_tokens=400)
        except Exception as e:
            print(f"LLM analysis failed: {e}")
            return self._generate_basic_analysis(exam_result)

    def generate_study_recommendations(self, exam_result: ExamResult, time_available: int = 60) -> List[LearningRecommendation]:
        """Generate personalized study recommendations."""
        recommendations = []

        # Basic recommendations based on performance
        accuracy = exam_result.metrics.accuracy_percentage

        if accuracy < 60:
            recommendations.append(LearningRecommendation(
                type="focus_topic",
                title="Review Fundamental Concepts",
                description="Focus on basic concepts and principles",
                priority="high",
                suggested_actions=["Review lecture notes", "Practice basic problems", "Use flashcards"],
                estimated_time_minutes=45
            ))
        elif accuracy < 80:
            recommendations.append(LearningRecommendation(
                type="practice_more",
                title="Practice Application Problems",
                description="Work on applying concepts to different scenarios",
                priority="high",
                suggested_actions=["Solve practice problems", "Work through examples", "Explain concepts to others"],
                estimated_time_minutes=60
            ))

        # Time management
        avg_time = exam_result.metrics.average_time_per_question
        if avg_time > 90:  # More than 1.5 minutes per question
            recommendations.append(LearningRecommendation(
                type="time_management",
                title="Improve Time Management",
                description="Practice solving problems more efficiently",
                priority="medium",
                suggested_actions=["Set time limits for practice", "Identify slow steps", "Practice mental math"],
                estimated_time_minutes=30
            ))

        # Topic-specific recommendations
        for topic in exam_result.weak_areas.topics[:2]:  # Top 2 weak topics
            recommendations.append(LearningRecommendation(
                type="focus_topic",
                title=f"Strengthen {topic}",
                description=f"Dedicated practice for {topic} concepts",
                priority="high",
                suggested_actions=[f"Find {topic} practice problems", f"Watch {topic} tutorial videos", f"Create {topic} summary notes"],
                estimated_time_minutes=40
            ))

        return recommendations

    def _analyze_topic_performance(self, exam_results: List[ExamResult]) -> Dict[str, Dict[str, float]]:
        """Analyze performance by topic across multiple exams."""
        topic_stats = {}

        for result in exam_results:
            for topic_perf in result.topic_performance:
                topic = topic_perf.topic
                if topic not in topic_stats:
                    topic_stats[topic] = {'total_score': 0, 'count': 0}

                topic_stats[topic]['total_score'] += topic_perf.accuracy
                topic_stats[topic]['count'] += 1

        # Calculate averages
        for topic, stats in topic_stats.items():
            stats['avg_score'] = stats['total_score'] / stats['count'] if stats['count'] > 0 else 0

        return topic_stats

    def _calculate_time_efficiency(self, exam_result: ExamResult) -> float:
        """Calculate time efficiency score (0-100)."""
        # Ideal time per question (assume 1 minute per question)
        ideal_total_time = exam_result.metrics.total_questions * 60  # 60 seconds per question
        actual_time = exam_result.metrics.total_time_taken * 60  # Convert to seconds

        if actual_time <= ideal_total_time:
            return 100  # On time or faster
        else:
            # Penalty for taking longer, but not below 20
            overtime_ratio = actual_time / ideal_total_time
            efficiency = max(20, 100 / overtime_ratio)
            return efficiency

    def _generate_basic_analysis(self, exam_result: ExamResult) -> str:
        """Generate basic performance analysis without LLM."""
        accuracy = exam_result.metrics.accuracy_percentage
        avg_time = exam_result.metrics.average_time_per_question

        analysis = f"""
Performance Analysis:
- Accuracy: {accuracy:.1f}%
- Average time per question: {avg_time:.1f} seconds
- Total questions: {exam_result.metrics.total_questions}
- Correct answers: {exam_result.metrics.correct_answers}

"""

        if accuracy >= 80:
            analysis += "Excellent performance! You have a strong grasp of the material."
        elif accuracy >= 70:
            analysis += "Good performance. Continue practicing to improve further."
        elif accuracy >= 60:
            analysis += "Satisfactory performance. Focus on weak areas."
        else:
            analysis += "Performance needs improvement. Consider reviewing fundamental concepts."

        if avg_time > 120:
            analysis += "\n\nTime Management: Consider working on solving problems more quickly."
        elif avg_time < 30:
            analysis += "\n\nTime Management: You work quickly - ensure accuracy isn't being sacrificed for speed."

        return analysis

    def export_analytics_data(self, user_id: Optional[str] = None) -> pd.DataFrame:
        """Export analytics data as DataFrame for further analysis."""
        exam_results = exam_service.get_exam_results(user_id)

        data = []
        for result in exam_results:
            data.append({
                'exam_id': result.exam_id,
                'exam_name': result.exam_name,
                'completed_at': result.completed_at,
                'score_percentage': result.metrics.accuracy_percentage,
                'total_questions': result.metrics.total_questions,
                'correct_answers': result.metrics.correct_answers,
                'average_time': result.metrics.average_time_per_question,
                'total_time': result.metrics.total_time_taken
            })

        return pd.DataFrame(data)

# Global instance
analytics_service = AnalyticsService()