import streamlit as st
from core.session_state_manager import session_state_manager
from core.question_router import question_router
from core.exam_loader import exam_loader
from components.question_navigation import render_question_navigation, render_question_grid
from components.timer_display import render_timer_display
from components.progress_bar import render_exam_progress
from components.mc_component import render_mcq_question
from components.short_answer_component import render_short_answer_question
from components.essay_component import render_essay_question

st.title("📝 Take Exam")

# Check if there's an active session
if not session_state_manager.is_session_active():
    st.warning("No active exam session. Please select an exam first.")
    if st.button("Go to Exam Selection"):
        st.switch_page("pages/01_select_exam.py")
    st.stop()

# Get current session
session = session_state_manager.get_current_session()
if not session:
    st.error("Session not found.")
    st.stop()

# Load exam
exam_data = st.session_state.exam_data
exam = exam_loader.load_exam(exam_data['type'], exam_data['set'])
if not exam:
    st.error("Exam not found.")
    st.stop()

# Get current question
current_index = session_state_manager.get_current_question_index()
question = question_router.get_question_by_index(exam, current_index)

if not question:
    st.error("Question not found.")
    st.stop()

# Display timer and progress
col1, col2 = st.columns([2, 1])

with col1:
    remaining_time = session_state_manager.get_remaining_time()
    render_timer_display(remaining_time, session.time_remaining_seconds)

with col2:
    progress = session_state_manager.get_session_progress()
    render_exam_progress(progress)

# Question display
st.markdown("---")

# Question counter and navigation
render_question_navigation(
    current_index,
    question_router.get_total_questions(exam),
    lambda idx: session_state_manager.set_current_question_index(idx)
)

# Display question based on type
st.markdown("---")

current_answer = session_state_manager.get_answer(current_index)

if question.type.value == "mcq":
    answer = render_mcq_question(question, current_answer)
elif question.type.value == "short_answer":
    answer = render_short_answer_question(question, current_answer)
elif question.type.value == "essay":
    answer = render_essay_question(question, current_answer)
else:
    st.error(f"Unknown question type: {question.type.value}")
    answer = None

# Submit answer button
col1, col2, col3 = st.columns([1, 1, 1])

with col1:
    if st.button("⬅️ Previous", disabled=(current_index == 0)):
        if current_index > 0:
            session_state_manager.set_current_question_index(current_index - 1)
            st.rerun()

with col2:
    if st.button("💾 Save Answer", type="secondary"):
        if answer is not None:
            session_state_manager.submit_answer(current_index, answer)
            st.success("Answer saved!")
        else:
            st.warning("Please provide an answer before saving.")

with col3:
    next_disabled = current_index >= question_router.get_total_questions(exam) - 1
    if st.button("Next ➡️", disabled=next_disabled):
        # Save current answer first
        if answer is not None:
            session_state_manager.submit_answer(current_index, answer)

        if current_index < question_router.get_total_questions(exam) - 1:
            session_state_manager.set_current_question_index(current_index + 1)
            st.rerun()

# Question grid for navigation
st.markdown("---")
st.markdown("### Question Overview")

# Show question status
questions_status = []
for i in range(question_router.get_total_questions(exam)):
    answered = i in st.session_state.answers and st.session_state.answers[i] is not None
    current = i == current_index
    status = "current" if current else ("answered" if answered else "unanswered")
    questions_status.append((i, status))

# Simple grid display
cols = st.columns(5)
for i, (q_idx, status) in enumerate(questions_status):
    col_idx = i % 5
    with cols[col_idx]:
        if status == "current":
            st.button(f"**{q_idx + 1}**", key=f"q_{q_idx}", disabled=True, use_container_width=True)
        elif status == "answered":
            if st.button(f"✓ {q_idx + 1}", key=f"q_{q_idx}", use_container_width=True):
                session_state_manager.set_current_question_index(q_idx)
                st.rerun()
        else:
            if st.button(str(q_idx + 1), key=f"q_{q_idx}", use_container_width=True):
                session_state_manager.set_current_question_index(q_idx)
                st.rerun()

# Finish exam button
st.markdown("---")
col1, col2, col3 = st.columns([1, 1, 1])

with col2:
    if st.button("🏁 Finish Exam", type="primary", use_container_width=True):
        # Confirm submission
        if st.checkbox("I confirm that I want to submit the exam"):
            with st.spinner("Submitting exam..."):
                try:
                    result = session_state_manager.end_session(session.session_id)
                    if result:
                        st.success("Exam submitted successfully!")
                        st.switch_page("pages/03_review_answers.py")
                    else:
                        st.error("Failed to submit exam.")
                except Exception as e:
                    st.error(f"Error submitting exam: {str(e)}")
        else:
            st.info("Please confirm submission by checking the box above.")

# Pause/Resume functionality
st.markdown("---")
col1, col2 = st.columns(2)

with col1:
    if st.button("⏸️ Pause Exam"):
        if session_state_manager.pause_session():
            st.success("Exam paused. You can resume later.")
        else:
            st.error("Could not pause exam.")

with col2:
    if st.button("▶️ Resume Exam"):
        if session_state_manager.resume_session():
            st.success("Exam resumed.")
            st.rerun()
        else:
            st.error("Could not resume exam.")