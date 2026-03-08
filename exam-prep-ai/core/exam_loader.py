from pathlib import Path
from typing import List, Dict, Optional
import json
from schemas.exam_schema import Exam
from schemas.question_schema import Question, QuestionType
from utils.file_utils import load_json_file, list_files_in_directory
from config.settings import SETTINGS

class ExamLoader:
    def __init__(self, datasets_dir: Optional[Path] = None):
        self.datasets_dir = datasets_dir or SETTINGS['datasets_dir']

    def load_exam(self, exam_type: str, set_name: str) -> Optional[Exam]:
        """Load a complete exam from dataset."""
        exam_file = self.datasets_dir / exam_type / f"{set_name}.json"

        if not exam_file.exists():
            return None

        data = load_json_file(exam_file)

        # Convert questions to Question objects
        questions = []
        for q_data in data.get('questions', []):
            question = self._parse_question(q_data)
            questions.append(question)

        # Create exam sections (simplified - all questions in one section)
        from schemas.exam_schema import ExamSection
        section = ExamSection(
            name="Main Section",
            questions=questions,
            time_limit_minutes=SETTINGS['exam'].get(exam_type, {}).get('time_limit_minutes', 60)
        )

        exam = Exam(
            id=data['exam_id'],
            name=data['exam_name'],
            type=exam_type,
            sections=[section],
            total_questions=len(questions),
            total_time_minutes=SETTINGS['exam'].get(exam_type, {}).get('time_limit_minutes', 60)
        )

        return exam

    def _parse_question(self, data: Dict) -> Question:
        """Parse question data into Question object."""
        question_type = QuestionType(data['type'])

        # Handle options for MCQ
        options = None
        if question_type == QuestionType.MCQ and 'options' in data:
            from schemas.question_schema import MCQOption
            options = [MCQOption(**opt) for opt in data['options']]

        question = Question(
            id=data['id'],
            type=question_type,
            question_text=data['question_text'],
            options=options,
            explanation=data.get('explanation'),
            difficulty=data.get('difficulty', 'medium'),
            topic=data.get('topic', ''),
            subtopic=data.get('subtopic'),
            sample_answer=data.get('sample_answer'),
            rubric=data.get('rubric'),
            max_length=data.get('max_length'),
            points=data.get('points', 1)
        )

        return question

    def get_available_exams(self) -> Dict[str, List[str]]:
        """Get list of available exam types and sets."""
        available = {}

        for exam_type_dir in self.datasets_dir.iterdir():
            if exam_type_dir.is_dir():
                sets = []
                for set_file in exam_type_dir.glob('*.json'):
                    sets.append(set_file.stem)
                if sets:
                    available[exam_type_dir.name] = sorted(sets)

        return available

    def get_exam_info(self, exam_type: str, set_name: str) -> Optional[Dict]:
        """Get basic info about an exam without loading full data."""
        exam_file = self.datasets_dir / exam_type / f"{set_name}.json"

        if not exam_file.exists():
            return None

        data = load_json_file(exam_file)

        return {
            'id': data['exam_id'],
            'name': data['exam_name'],
            'type': data['exam_type'],
            'questions_count': len(data.get('questions', [])),
            'estimated_time': SETTINGS['exam'].get(exam_type, {}).get('time_limit_minutes', 60)
        }

# Global instance
exam_loader = ExamLoader()