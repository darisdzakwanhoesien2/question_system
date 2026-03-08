import streamlit as st
from typing import List, Callable, Optional
from schemas.question_schema import Question, QuestionType

def render_question_navigation(current_index: int, total_questions: int, on_navigate: Callable[[int], None], key_prefix: str = ""):
    """
    Render question navigation component.

    Args:
        current_index: Current question index (0-based)
        total_questions: Total number of questions
        on_navigate: Callback function when navigation occurs
        key_prefix: Prefix for streamlit keys
    """
    st.markdown("### Question Navigation")

    # Previous/Next buttons
    col1, col2, col3 = st.columns([1, 2, 1])

    with col1:
        if current_index > 0:
            if st.button("⬅️ Previous", key=f"{key_prefix}prev_{current_index}"):
                on_navigate(current_index - 1)
        else:
            st.button("⬅️ Previous", disabled=True, key=f"{key_prefix}prev_disabled")

    with col2:
        st.markdown(f"<center><h4>Question {current_index + 1} of {total_questions}</h4></center>",
                   unsafe_allow_html=True)

    with col3:
        if current_index < total_questions - 1:
            if st.button("Next ➡️", key=f"{key_prefix}next_{current_index}"):
                on_navigate(current_index + 1)
        else:
            st.button("Next ➡️", disabled=True, key=f"{key_prefix}next_disabled")

def render_question_grid(current_index: int, questions: List[Question], answers: dict,
                        on_navigate: Callable[[int], None], key_prefix: str = ""):
    """
    Render a grid of question numbers for quick navigation.

    Args:
        current_index: Current question index
        questions: List of questions
        answers: Dictionary of question_index -> answer
        on_navigate: Callback for navigation
        key_prefix: Prefix for keys
    """
    st.markdown("### Question Overview")

    # Calculate grid dimensions
    cols_per_row = 5
    rows = (len(questions) + cols_per_row - 1) // cols_per_row

    for row in range(rows):
        cols = st.columns(cols_per_row)
        for col_idx in range(cols_per_row):
            question_idx = row * cols_per_row + col_idx
            if question_idx >= len(questions):
                break

            with cols[col_idx]:
                question = questions[question_idx]
                is_current = question_idx == current_index
                is_answered = question_idx in answers and answers[question_idx] is not None

                # Determine button style
                if is_current:
                    button_type = "primary"
                    label = f"**{question_idx + 1}**"
                elif is_answered:
                    button_type = "secondary"
                    label = f"✓ {question_idx + 1}"
                else:
                    button_type = "secondary"
                    label = str(question_idx + 1)

                # Create button
                if st.button(label, key=f"{key_prefix}q_{question_idx}",
                           type=button_type, use_container_width=True):
                    on_navigate(question_idx)

def render_section_navigation(exam_sections: List[dict], current_section: str,
                            on_section_change: Callable[[str], None], key_prefix: str = ""):
    """
    Render section navigation for multi-section exams.

    Args:
        exam_sections: List of section dicts with 'name' and 'questions' keys
        current_section: Current section name
        on_section_change: Callback for section change
        key_prefix: Prefix for keys
    """
    st.markdown("### Sections")

    section_options = [section['name'] for section in exam_sections]
    current_idx = section_options.index(current_section) if current_section in section_options else 0

    selected_section = st.selectbox(
        "Select Section:",
        section_options,
        index=current_idx,
        key=f"{key_prefix}section_select",
        label_visibility="collapsed"
    )

    if selected_section != current_section:
        on_section_change(selected_section)

    # Show section progress
    for section in exam_sections:
        if section['name'] == current_section:
            st.progress(len(section.get('completed_questions', [])) / len(section['questions']),
                       text=f"{section['name']}: {len(section.get('completed_questions', []))}/{len(section['questions'])}")

def render_question_palette(questions: List[Question], answers: dict, current_index: int,
                          on_navigate: Callable[[int], None], key_prefix: str = ""):
    """
    Render a compact question palette showing status.

    Args:
        questions: List of questions
        answers: Dictionary of answers
        current_index: Current question index
        on_navigate: Navigation callback
        key_prefix: Key prefix
    """
    st.markdown("**Question Status:**")

    # Create a row of buttons
    cols = st.columns(min(len(questions), 10))  # Max 10 per row

    for i, question in enumerate(questions):
        col_idx = i % 10
        if col_idx == 0 and i > 0:
            cols = st.columns(min(len(questions) - i, 10))

        with cols[col_idx]:
            is_answered = i in answers and answers[i] is not None
            is_current = i == current_index

            if is_current:
                label = f"🔵 {i + 1}"
            elif is_answered:
                label = f"🟢 {i + 1}"
            else:
                label = f"⚪ {i + 1}"

            if st.button(label, key=f"{key_prefix}palette_{i}", use_container_width=True):
                on_navigate(i)

    # Legend
    st.caption("🔵 Current | 🟢 Answered | ⚪ Not Answered")