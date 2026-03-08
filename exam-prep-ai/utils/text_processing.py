import re
from typing import List, Set, Dict
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords

# Download required NLTK data (run once)
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

def clean_text(text: str) -> str:
    """Clean text by removing extra whitespace and normalizing."""
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text.strip())
    return text

def tokenize_words(text: str) -> List[str]:
    """Tokenize text into words."""
    return word_tokenize(text.lower())

def tokenize_sentences(text: str) -> List[str]:
    """Tokenize text into sentences."""
    return sent_tokenize(text)

def remove_stopwords(words: List[str]) -> List[str]:
    """Remove common stopwords from word list."""
    stop_words = set(stopwords.words('english'))
    return [word for word in words if word not in stop_words]

def get_word_frequency(text: str) -> Dict[str, int]:
    """Get word frequency dictionary."""
    words = tokenize_words(text)
    words = remove_stopwords(words)

    frequency = {}
    for word in words:
        frequency[word] = frequency.get(word, 0) + 1

    return frequency

def calculate_similarity_score(text1: str, text2: str) -> float:
    """Calculate simple similarity score between two texts."""
    words1 = set(tokenize_words(text1))
    words2 = set(tokenize_words(text2))

    intersection = words1.intersection(words2)
    union = words1.union(words2)

    if not union:
        return 0.0

    return len(intersection) / len(union)

def extract_keywords(text: str, max_keywords: int = 10) -> List[str]:
    """Extract top keywords from text based on frequency."""
    freq = get_word_frequency(text)
    sorted_words = sorted(freq.items(), key=lambda x: x[1], reverse=True)
    return [word for word, count in sorted_words[:max_keywords]]

def count_words(text: str) -> int:
    """Count words in text."""
    return len(tokenize_words(text))

def count_sentences(text: str) -> int:
    """Count sentences in text."""
    return len(tokenize_sentences(text))

def calculate_readability_score(text: str) -> float:
    """Calculate simple readability score (words per sentence)."""
    sentences = tokenize_sentences(text)
    if not sentences:
        return 0.0

    total_words = sum(len(tokenize_words(sent)) for sent in sentences)
    return total_words / len(sentences)

def normalize_answer(text: str) -> str:
    """Normalize answer text for comparison."""
    # Convert to lowercase
    text = text.lower()
    # Remove punctuation
    text = re.sub(r'[^\w\s]', '', text)
    # Clean whitespace
    text = clean_text(text)
    return text