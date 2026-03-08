from typing import List, Optional
from schemas.question_schema import Question, QuestionType
from schemas.exam_schema import Exam

class QuestionRouter:
    def __init__(self):
        pass

    def get_question_by_index(self, exam: Exam, index: int) -> Optional[Question]:
        """Get question by index from exam."""
        all_questions = self.get_all_questions(exam)

        if 0 <= index < len(all_questions):
            return all_questions[index]

        return None

    def get_all_questions(self, exam: Exam) -> List[Question]:
        """Get all questions from exam in order."""
        questions = []
        for section in exam.sections:
            questions.extend(section.questions)
        return questions

    def get_questions_by_type(self, exam: Exam, question_type: QuestionType) -> List[Question]:
        """Get questions of specific type."""
        all_questions = self.get_all_questions(exam)
        return [q for q in all_questions if q.type == question_type]

    def get_questions_by_topic(self, exam: Exam, topic: str) -> List[Question]:
        """Get questions by topic."""
        all_questions = self.get_all_questions(exam)
        return [q for q in all_questions if q.topic.lower() == topic.lower()]

    def get_next_question(self, exam: Exam, current_index: int) -> Optional[Question]:
        """Get next question in sequence."""
        return self.get_question_by_index(exam, current_index + 1)

    def get_previous_question(self, exam: Exam, current_index: int) -> Optional[Question]:
        """Get previous question in sequence."""
        if current_index > 0:
            return self.get_question_by_index(exam, current_index - 1)
        return None

    def get_total_questions(self, exam: Exam) -> int:
        """Get total number of questions in exam."""
        return len(self.get_all_questions(exam))

    def get_section_for_question(self, exam: Exam, question_index: int) -> Optional[str]:
        """Get section name for a question index."""
        current_count = 0

        for section in exam.sections:
            section_start = current_count
            section_end = current_count + len(section.questions)

            if section_start <= question_index < section_end:
                return section.name

            current_count = section_end

        return None

    def get_question_index_in_section(self, exam: Exam, global_index: int) -> tuple[Optional[str], int]:
        """Get section name and local index for global question index."""
        current_count = 0

        for section in exam.sections:
            section_start = current_count
            section_end = current_count + len(section.questions)

            if section_start <= global_index < section_end:
                local_index = global_index - section_start
                return section.name, local_index

            current_count = section_end

        return None, -1

    def validate_question_index(self, exam: Exam, index: int) -> bool:
        """Validate if question index is valid for exam."""
        return 0 <= index < self.get_total_questions(exam)

# Global instance
question_router = QuestionRouter()