import streamlit as st
from core.session_state_manager import session_state_manager
from core.question_router import question_router
from core.exam_loader import exam_loader
from core.scoring_engine import scoring_engine
from services.exam_service import exam_service
from components.question_navigation import render_question_navigation
from components.mc_component import render_mcq_question, show_mcq_explanation
from components.short_answer_component import render_short_answer_question, show_short_answer_feedback
from components.essay_component import render_essay_question, show_essay_feedback

st.title("🔍 Review Answers")

# Check if there's a completed session or results to review
if session_state_manager.is_session_active():
    st.info("You have an active exam session. Please complete it first.")
    if st.button("Continue Exam"):
        st.switch_page("pages/02_take_exam.py")
    st.stop()

# Try to get the most recent completed session or results
# For now, assume we need to load from results
# This would need to be enhanced to track the last completed session

st.warning("Review functionality requires a completed exam session.")
st.markdown("Please complete an exam first, then return here to review your answers.")

# Placeholder for review functionality
st.markdown("### Review Features (Coming Soon)")
st.markdown("""
- View all your answers
- See correct answers and explanations
- Review scoring and feedback
- Identify areas for improvement
""")

if st.button("Start New Exam"):
    st.switch_page("pages/01_select_exam.py")

# If we had a completed session, the code would be:
"""
# Get completed session results
session_id = st.session_state.get('last_completed_session')
if not session_id:
    st.error("No completed exam to review.")
    st.stop()

# Load exam and results
exam_data = st.session_state.get('last_exam_data')
if not exam_data:
    st.error("Exam data not found.")
    st.stop()

exam = exam_loader.load_exam(exam_data['type'], exam_data['set'])
if not exam:
    st.error("Exam not found.")
    st.stop()

# Get user answers
answers = st.session_state.get('final_answers', {})

# Calculate results
results = []
for i, question in enumerate(question_router.get_all_questions(exam)):
    user_answer = answers.get(i)
    if user_answer:
        result = scoring_engine.score_answer(question, user_answer)
        results.append(result)

st.markdown("### Exam Results Summary")
# Display summary...

# Question by question review
st.markdown("### Question Review")

current_index = st.session_state.get('review_index', 0)
question = question_router.get_question_by_index(exam, current_index)

if question:
    # Navigation
    render_question_navigation(
        current_index,
        question_router.get_total_questions(exam),
        lambda idx: st.session_state.update(review_index=idx)
    )

    # Show question and answers
    user_answer = answers.get(current_index)
    result = results[current_index] if current_index < len(results) else None

    # Display based on type
    if question.type.value == "mcq":
        render_mcq_question(question, user_answer)
        show_mcq_explanation(question, show_correct=True)
    elif question.type.value == "short_answer":
        render_short_answer_question(question, user_answer)
        if result:
            show_short_answer_feedback(question, user_answer.answer if user_answer else "", result.score)
    elif question.type.value == "essay":
        render_essay_question(question, user_answer)
        if result:
            show_essay_feedback(question, user_answer.answer if user_answer else "", result.score, result.feedback)

    # Show score
    if result:
        st.metric("Score", f"{result.score:.2f}/1.00")
"""