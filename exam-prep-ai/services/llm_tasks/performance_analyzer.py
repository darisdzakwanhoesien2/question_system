from typing import Dict, Any, List
from services.llm_router import llm_router
from utils.prompt_loader import prompt_loader
from schemas.result_schema import ExamResult

class PerformanceAnalyzer:
    """Analyzes exam performance and provides insights."""

    def __init__(self):
        pass

    def analyze_performance(self, exam_result: ExamResult) -> Dict[str, Any]:
        """
        Generate comprehensive performance analysis.

        Returns analysis with insights, trends, and recommendations.
        """
        # Prepare performance data
        performance_data = self._format_performance_data(exam_result)

        # Get LLM analysis
        prompt = prompt_loader.format_prompt(
            'analytics',
            'performance_analysis',
            performance_data=performance_data
        )

        llm_analysis = llm_router.route_request('performance_analysis', prompt, max_tokens=400)

        # Calculate additional metrics
        metrics = self._calculate_detailed_metrics(exam_result)

        return {
            'llm_analysis': llm_analysis,
            'metrics': metrics,
            'insights': self._extract_insights(exam_result),
            'recommendations': self._generate_recommendations(exam_result)
        }

    def _format_performance_data(self, exam_result: ExamResult) -> str:
        """Format performance data for LLM prompt."""
        data = f"""
Exam: {exam_result.exam_name}
Total Questions: {exam_result.metrics.total_questions}
Correct Answers: {exam_result.metrics.correct_answers}
Accuracy: {exam_result.metrics.accuracy_percentage:.1f}%
Average Time per Question: {exam_result.metrics.average_time_per_question:.1f} seconds
Total Time Taken: {exam_result.metrics.total_time_taken:.1f} minutes

Topic Performance:
"""

        for topic_perf in exam_result.topic_performance:
            data += f"- {topic_perf.topic}: {topic_perf.correct_count}/{topic_perf.questions_count} correct ({topic_perf.accuracy:.1f}%)\n"

        data += f"\nWeak Areas: {', '.join(exam_result.weak_areas.topics) if exam_result.weak_areas.topics else 'None identified'}"

        return data

    def _calculate_detailed_metrics(self, exam_result: ExamResult) -> Dict[str, Any]:
        """Calculate additional performance metrics."""
        metrics = {
            'accuracy_percentage': exam_result.metrics.accuracy_percentage,
            'time_efficiency': self._calculate_time_efficiency(exam_result),
            'consistency_score': self._calculate_consistency(exam_result),
            'topic_mastery': self._assess_topic_mastery(exam_result)
        }

        return metrics

    def _calculate_time_efficiency(self, exam_result: ExamResult) -> float:
        """Calculate time efficiency score (0-100)."""
        # Assume 1 minute per question is ideal
        ideal_time = exam_result.metrics.total_questions * 60  # seconds
        actual_time = exam_result.metrics.total_time_taken * 60  # seconds

        if actual_time <= ideal_time:
            return 100.0
        else:
            # Gradual penalty for overtime
            overtime_ratio = actual_time / ideal_time
            return max(10.0, 100.0 / overtime_ratio)

    def _calculate_consistency(self, exam_result: ExamResult) -> float:
        """Calculate consistency score based on topic performance variance."""
        if not exam_result.topic_performance:
            return 100.0

        accuracies = [tp.accuracy for tp in exam_result.topic_performance]
        if len(accuracies) <= 1:
            return 100.0

        # Calculate coefficient of variation
        mean_acc = sum(accuracies) / len(accuracies)
        if mean_acc == 0:
            return 0.0

        variance = sum((acc - mean_acc) ** 2 for acc in accuracies) / len(accuracies)
        std_dev = variance ** 0.5
        cv = std_dev / mean_acc

        # Convert to score (lower CV = higher consistency)
        consistency = max(0.0, min(100.0, 100.0 - (cv * 100.0)))
        return consistency

    def _assess_topic_mastery(self, exam_result: ExamResult) -> Dict[str, str]:
        """Assess mastery level for each topic."""
        mastery_levels = {}

        for topic_perf in exam_result.topic_performance:
            accuracy = topic_perf.accuracy

            if accuracy >= 90:
                level = "Mastered"
            elif accuracy >= 80:
                level = "Proficient"
            elif accuracy >= 70:
                level = "Developing"
            elif accuracy >= 60:
                level = "Needs Improvement"
            else:
                level = "Struggling"

            mastery_levels[topic_perf.topic] = level

        return mastery_levels

    def _extract_insights(self, exam_result: ExamResult) -> List[str]:
        """Extract key insights from performance."""
        insights = []

        accuracy = exam_result.metrics.accuracy_percentage

        if accuracy >= 85:
            insights.append("Strong overall performance across topics")
        elif accuracy >= 70:
            insights.append("Solid foundation with room for improvement")
        else:
            insights.append("Significant improvement needed in core concepts")

        # Time insights
        avg_time = exam_result.metrics.average_time_per_question
        if avg_time > 120:
            insights.append("Consider improving speed while maintaining accuracy")
        elif avg_time < 30:
            insights.append("Fast performance - ensure thorough understanding")

        # Topic insights
        if exam_result.topic_performance:
            best_topic = max(exam_result.topic_performance, key=lambda x: x.accuracy)
            worst_topic = min(exam_result.topic_performance, key=lambda x: x.accuracy)

            if best_topic.accuracy > worst_topic.accuracy + 20:
                insights.append(f"Strong in {best_topic.topic}, needs work in {worst_topic.topic}")

        return insights

    def _generate_recommendations(self, exam_result: ExamResult) -> List[str]:
        """Generate study recommendations."""
        recommendations = []

        # Based on weak areas
        for topic in exam_result.weak_areas.topics[:3]:  # Top 3 weak areas
            recommendations.append(f"Focus additional study time on {topic}")

        # Based on time
        if exam_result.metrics.average_time_per_question > 90:
            recommendations.append("Practice time management techniques")

        # Based on accuracy
        if exam_result.metrics.accuracy_percentage < 70:
            recommendations.append("Review fundamental concepts and practice basic problems")
        elif exam_result.metrics.accuracy_percentage < 85:
            recommendations.append("Work on application problems and complex scenarios")

        if not recommendations:
            recommendations.append("Continue current study approach with regular practice")

        return recommendations

# Global instance
performance_analyzer = PerformanceAnalyzer()