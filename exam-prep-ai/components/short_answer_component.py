import streamlit as st
from typing import Optional, Any
from schemas.question_schema import Question

def render_short_answer_question(question: Question, current_answer: Optional[str] = None, key_prefix: str = "") -> Optional[str]:
    """
    Render a short answer question component.

    Args:
        question: The question object
        current_answer: Current answer text
        key_prefix: Prefix for streamlit keys

    Returns:
        Answer text
    """
    st.markdown(f"**{question.question_text}**")

    # Show max length hint if specified
    max_length = question.max_length or 500
    st.caption(f"Maximum {max_length} characters")

    # Text area for answer
    answer = st.text_area(
        "Your answer:",
        value=current_answer or "",
        max_chars=max_length,
        height=100,
        key=f"{key_prefix}short_answer_{question.id}",
        label_visibility="collapsed",
        placeholder="Type your answer here..."
    )

    # Character count
    char_count = len(answer) if answer else 0
    st.caption(f"Characters: {char_count}/{max_length}")

    return answer.strip() if answer else None

def render_short_answer_with_validation(question: Question, current_answer: Optional[str] = None, key_prefix: str = "") -> Optional[str]:
    """
    Render short answer with real-time validation.
    """
    answer = render_short_answer_question(question, current_answer, key_prefix)

    # Basic validation
    if answer:
        word_count = len(answer.split())
        if word_count < 2:
            st.warning("Please provide a more complete answer.")
        elif len(answer) < 10:
            st.warning("Your answer seems too short. Please elaborate.")

    return answer

def show_short_answer_sample(question: Question):
    """
    Show sample answer for short answer question.
    """
    if question.sample_answer:
        with st.expander("💡 View Sample Answer"):
            st.markdown(question.sample_answer)

def show_short_answer_feedback(question: Question, user_answer: str, score: float):
    """
    Show feedback for short answer.
    """
    if score >= 0.8:
        st.success("Excellent answer!")
    elif score >= 0.6:
        st.warning("Good answer, but could be more precise.")
    else:
        st.error("Your answer needs improvement.")

        if question.sample_answer:
            st.info(f"**Sample Answer:** {question.sample_answer}")

def validate_short_answer(question: Question, answer: Optional[str]) -> tuple[bool, str]:
    """
    Validate short answer.

    Returns (is_valid, error_message)
    """
    if not answer:
        return False, "Answer cannot be empty"

    if not answer.strip():
        return False, "Answer cannot be only whitespace"

    max_length = question.max_length or 500
    if len(answer) > max_length:
        return False, f"Answer exceeds maximum length of {max_length} characters"

    min_length = 10  # Minimum reasonable answer
    if len(answer) < min_length:
        return False, f"Answer is too short (minimum {min_length} characters)"

    return True, ""