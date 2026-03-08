import streamlit as st
from typing import Optional, Any
from schemas.question_schema import Question

def render_essay_question(question: Question, current_answer: Optional[str] = None, key_prefix: str = "") -> Optional[str]:
    """
    Render an essay question component.

    Args:
        question: The question object
        current_answer: Current essay text
        key_prefix: Prefix for streamlit keys

    Returns:
        Essay text
    """
    st.markdown(f"**{question.question_text}**")

    # Show max length hint if specified
    max_length = question.max_length or 2000
    st.caption(f"Maximum {max_length} characters recommended")

    # Text area for essay
    essay = st.text_area(
        "Write your essay:",
        value=current_answer or "",
        max_chars=max_length,
        height=300,
        key=f"{key_prefix}essay_{question.id}",
        label_visibility="collapsed",
        placeholder="Write your essay here..."
    )

    # Character and word count
    char_count = len(essay) if essay else 0
    word_count = len(essay.split()) if essay else 0

    col1, col2 = st.columns(2)
    with col1:
        st.caption(f"Characters: {char_count}/{max_length}")
    with col2:
        st.caption(f"Words: {word_count}")

    return essay.strip() if essay else None

def render_essay_with_formatting(question: Question, current_answer: Optional[str] = None, key_prefix: str = "") -> Optional[str]:
    """
    Render essay with formatting toolbar hint.
    """
    st.markdown("**Formatting Tips:** You can use basic formatting in your essay.")

    essay = render_essay_question(question, current_answer, key_prefix)

    # Show formatting help
    with st.expander("📝 Formatting Help"):
        st.markdown("""
        - Use paragraphs for organization
        - Start each paragraph with a topic sentence
        - Use transitions between paragraphs
        - Provide specific examples and evidence
        - End with a strong conclusion
        """)

    return essay

def show_essay_rubric(question: Question):
    """
    Show essay rubric if available.
    """
    if question.rubric:
        with st.expander("📋 Grading Rubric"):
            for criterion, description in question.rubric.items():
                st.markdown(f"**{criterion.title()}:** {description}")
    else:
        # Default rubric
        with st.expander("📋 Grading Rubric"):
            st.markdown("""
            **Thesis:** Clear, arguable thesis statement
            **Evidence:** Relevant examples and evidence
            **Analysis:** Effective analysis and commentary
            **Organization:** Logical structure and transitions
            **Language:** Clear, varied, and appropriate language
            """)

def show_essay_feedback(question: Question, user_answer: str, score: float, detailed_feedback: Optional[str] = None):
    """
    Show feedback for essay.
    """
    # Score indicator
    score_percentage = int(score * 100)
    if score >= 0.9:
        st.success(f"Excellent Essay! Score: {score_percentage}%")
    elif score >= 0.8:
        st.success(f"Very Good Essay! Score: {score_percentage}%")
    elif score >= 0.7:
        st.warning(f"Good Essay. Score: {score_percentage}%")
    elif score >= 0.6:
        st.warning(f"Satisfactory Essay. Score: {score_percentage}%")
    else:
        st.error(f"Essay Needs Improvement. Score: {score_percentage}%")

    # Detailed feedback
    if detailed_feedback:
        st.info(f"**Feedback:** {detailed_feedback}")
    else:
        # Generic feedback based on score
        if score >= 0.8:
            st.info("Your essay demonstrates strong analytical skills and clear organization.")
        elif score >= 0.6:
            st.info("Your essay has good content but could benefit from stronger analysis and organization.")
        else:
            st.info("Focus on developing a clear thesis, providing specific evidence, and improving organization.")

def validate_essay(question: Question, answer: Optional[str]) -> tuple[bool, str]:
    """
    Validate essay answer.

    Returns (is_valid, error_message)
    """
    if not answer:
        return False, "Essay cannot be empty"

    if not answer.strip():
        return False, "Essay cannot be only whitespace"

    max_length = question.max_length or 2000
    if len(answer) > max_length:
        return False, f"Essay exceeds maximum length of {max_length} characters"

    min_words = 100  # Minimum reasonable essay
    word_count = len(answer.split())
    if word_count < min_words:
        return False, f"Essay is too short (minimum {min_words} words, you have {word_count})"

    return True, ""