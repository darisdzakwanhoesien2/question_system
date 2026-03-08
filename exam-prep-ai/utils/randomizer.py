import random
from typing import List, TypeVar, Optional

T = TypeVar('T')

def shuffle_list(items: List[T]) -> List[T]:
    """Shuffle a list in place and return it."""
    shuffled = items.copy()
    random.shuffle(shuffled)
    return shuffled

def random_sample(items: List[T], k: int, allow_duplicates: bool = False) -> List[T]:
    """Randomly sample k items from list."""
    if allow_duplicates:
        return [random.choice(items) for _ in range(k)]
    else:
        return random.sample(items, min(k, len(items)))

def weighted_random_choice(items: List[T], weights: List[float]) -> T:
    """Choose random item based on weights."""
    if len(items) != len(weights):
        raise ValueError("Items and weights must have same length")

    total_weight = sum(weights)
    if total_weight == 0:
        return random.choice(items)

    r = random.uniform(0, total_weight)
    cumulative = 0

    for item, weight in zip(items, weights):
        cumulative += weight
        if r <= cumulative:
            return item

    return items[-1]  # fallback

def randomize_question_order(questions: List[dict], seed: Optional[int] = None) -> List[dict]:
    """Randomize question order with optional seed for reproducibility."""
    if seed is not None:
        random.seed(seed)

    return shuffle_list(questions)

def randomize_mcq_options(question: dict, seed: Optional[int] = None) -> dict:
    """Randomize MCQ options order."""
    if seed is not None:
        random.seed(seed)

    if 'options' in question and question['options']:
        question_copy = question.copy()
        question_copy['options'] = shuffle_list(question['options'])

        # Update correct answer index if needed
        if 'correct_index' in question_copy:
            original_correct = question['options'][question['correct_index']]
            for i, option in enumerate(question_copy['options']):
                if option == original_correct:
                    question_copy['correct_index'] = i
                    break

        return question_copy

    return question

def generate_session_id(length: int = 8) -> str:
    """Generate random session ID."""
    chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    return ''.join(random.choice(chars) for _ in range(length))

def seeded_random(seed: int):
    """Create a seeded random number generator."""
    rng = random.Random(seed)
    return rng