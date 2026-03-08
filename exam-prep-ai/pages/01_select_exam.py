import streamlit as st
from services.exam_service import exam_service
from core.session_state_manager import session_state_manager

st.title("📚 Select Exam")

st.markdown("Choose an exam type and set to begin your practice session.")

# Get available exams
available_exams = exam_service.get_available_exams()

if not available_exams:
    st.error("No exam sets available. Please check your datasets.")
    st.stop()

# Exam type selection
exam_types = list(available_exams.keys())
selected_exam_type = st.selectbox(
    "Select Exam Type:",
    exam_types,
    help="Choose the type of exam you want to practice"
)

if selected_exam_type:
    # Set selection
    sets = available_exams[selected_exam_type]
    selected_set = st.selectbox(
        "Select Exam Set:",
        sets,
        help="Choose a specific set of questions"
    )

    if selected_set:
        # Show exam info
        exam_info = exam_service.get_exam_info(selected_exam_type, selected_set)

        if exam_info:
            st.markdown("### Exam Information")
            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("Questions", exam_info['questions_count'])

            with col2:
                st.metric("Duration", f"{exam_info['estimated_time']} min")

            with col3:
                st.metric("Type", selected_exam_type.upper())

            # Start exam button
            if st.button("🚀 Start Exam", type="primary", use_container_width=True):
                # Check if there's already an active session
                if session_state_manager.is_session_active():
                    st.warning("You have an active exam session. Please complete it first or navigate to the exam page.")
                else:
                    # Start new session
                    with st.spinner("Loading exam..."):
                        try:
                            session_id = session_state_manager.start_exam_session({
                                'type': selected_exam_type,
                                'set': selected_set
                            })

                            st.success("Exam started! Redirecting...")
                            st.switch_page("pages/02_take_exam.py")

                        except Exception as e:
                            st.error(f"Failed to start exam: {str(e)}")

        # Preview questions (optional)
        with st.expander("👀 Preview Questions"):
            exam = exam_service.get_exam(selected_exam_type, selected_set)
            if exam:
                st.markdown(f"**{exam.name}**")
                st.markdown(f"Total sections: {len(exam.sections)}")

                for i, section in enumerate(exam.sections):
                    st.markdown(f"**Section {i+1}: {section.name}**")
                    st.markdown(f"- Questions: {len(section.questions)}")
                    if section.time_limit_minutes:
                        st.markdown(f"- Time limit: {section.time_limit_minutes} minutes")

                    # Show sample questions
                    if section.questions:
                        st.markdown("Sample questions:")
                        for j, question in enumerate(section.questions[:3]):  # Show first 3
                            st.markdown(f"  {j+1}. {question.question_text[:100]}...")
            else:
                st.error("Could not load exam preview.")

# Instructions
st.markdown("---")
st.markdown("### Instructions")
st.markdown("""
1. **Select Exam Type**: Choose from available exam types (SAT, GRE, TOEFL)
2. **Choose Set**: Pick a question set to practice with
3. **Start Exam**: Click to begin your timed practice session
4. **Take Exam**: Answer questions and manage your time
5. **Review**: Check your answers and get feedback
6. **Analytics**: View detailed performance analytics
""")

# Quick stats
st.markdown("### Available Exams")
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Exam Types", len(exam_types))

with col2:
    total_sets = sum(len(sets) for sets in available_exams.values())
    st.metric("Total Sets", total_sets)

with col3:
    # Estimate total questions
    total_questions = 0
    for exam_type, sets in available_exams.items():
        for set_name in sets:
            exam_info = exam_service.get_exam_info(exam_type, set_name)
            if exam_info:
                total_questions += exam_info['questions_count']
    st.metric("Total Questions", total_questions)