import streamlit as st
from typing import List, Optional, Any
from schemas.question_schema import Question, MCQOption

def render_mcq_question(question: Question, current_answer: Optional[Any] = None, key_prefix: str = "") -> Optional[str]:
    """
    Render a multiple choice question component.

    Args:
        question: The question object
        current_answer: Current selected answer
        key_prefix: Prefix for streamlit keys to avoid conflicts

    Returns:
        Selected answer text or None
    """
    st.markdown(f"**{question.question_text}**")

    if not question.options:
        st.error("No options available for this question.")
        return None

    # Prepare options
    options = [opt.text for opt in question.options]

    # Determine current selection
    current_index = None
    if current_answer:
        if isinstance(current_answer, str):
            # Find index of matching option
            for i, opt in enumerate(question.options):
                if opt.text == current_answer:
                    current_index = i
                    break
        elif isinstance(current_answer, int) and 0 <= current_answer < len(options):
            current_index = current_answer

    # Render radio buttons
    selected_index = st.radio(
        "Select your answer:",
        options=options,
        index=current_index,
        key=f"{key_prefix}mcq_{question.id}",
        label_visibility="collapsed"
    )

    # Find selected option text
    selected_answer = None
    if selected_index:
        for opt in question.options:
            if opt.text == selected_index:
                selected_answer = opt.text
                break

    return selected_answer

def render_mcq_options(question: Question, current_answer: Optional[Any] = None, key_prefix: str = "") -> Optional[str]:
    """
    Alternative rendering with individual radio buttons for each option.
    """
    st.markdown(f"**{question.question_text}**")

    if not question.options:
        st.error("No options available for this question.")
        return None

    # Create radio button for each option
    selected_option = st.radio(
        "Choose your answer:",
        question.options,
        index=None,  # No default selection
        format_func=lambda opt: opt.text,
        key=f"{key_prefix}mcq_options_{question.id}",
        label_visibility="collapsed"
    )

    return selected_option.text if selected_option else None

def show_mcq_explanation(question: Question, show_correct: bool = True):
    """
    Show explanation for MCQ question.

    Args:
        question: The question object
        show_correct: Whether to show the correct answer
    """
    if show_correct and question.options:
        correct_option = None
        for opt in question.options:
            if opt.is_correct:
                correct_option = opt
                break

        if correct_option:
            st.success(f"**Correct Answer:** {correct_option.text}")

    if question.explanation:
        st.info(f"**Explanation:** {question.explanation}")

def validate_mcq_answer(question: Question, answer: Optional[str]) -> bool:
    """
    Validate MCQ answer.

    Returns True if answer is valid (exists in options).
    """
    if not answer or not question.options:
        return False

    return any(opt.text == answer for opt in question.options)