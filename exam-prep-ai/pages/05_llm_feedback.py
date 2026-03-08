import streamlit as st
from services.llm_service import llm_service
from services.exam_service import exam_service
from services.grading_service import grading_service
from core.session_state_manager import session_state_manager

st.title("🤖 AI Feedback & Tutoring")

st.markdown("Get personalized AI-powered feedback and tutoring support.")

# Check if LLM service is available
if not llm_service.get_available_providers():
    st.warning("No LLM providers configured. Please check your configuration.")
    st.stop()

# Get user's exam results
exam_results = exam_service.get_exam_results()

if not exam_results:
    st.info("Complete an exam first to get AI feedback!")
    if st.button("Take an Exam"):
        st.switch_page("pages/01_select_exam.py")
    st.stop()

# Select exam for feedback
st.markdown("### Select Exam for Feedback")

exam_options = [f"{r.exam_name} ({r.completed_at.strftime('%Y-%m-%d')}) - {r.metrics.accuracy_percentage:.1f}%" for r in exam_results]
selected_exam_option = st.selectbox("Choose an exam:", exam_options)

if selected_exam_option:
    # Find selected result
    selected_result = None
    for result in exam_results:
        if f"{result.exam_name} ({result.completed_at.strftime('%Y-%m-%d')}) - {result.metrics.accuracy_percentage:.1f}%" == selected_exam_option:
            selected_result = result
            break

    if selected_result:
        st.markdown("---")

        # Overall feedback
        st.markdown("### 📝 Overall Performance Feedback")

        if st.button("Generate Overall Feedback"):
            with st.spinner("Generating AI feedback..."):
                try:
                    feedback = grading_service.generate_feedback(selected_result)
                    st.write(feedback)
                except Exception as e:
                    st.error(f"Failed to generate feedback: {str(e)}")

        # Question-specific feedback
        st.markdown("### ❓ Question-by-Question Feedback")

        # This would require storing individual question results
        # For now, show a placeholder
        st.info("Detailed question feedback requires enhanced result storage. Coming soon!")

        # Study recommendations
        st.markdown("### 🎯 Personalized Study Plan")

        if st.button("Generate Study Recommendations"):
            with st.spinner("Creating personalized study plan..."):
                try:
                    from services.analytics_service import analytics_service
                    recommendations = analytics_service.generate_study_recommendations(selected_result)

                    for rec in recommendations:
                        priority_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(rec.priority, "🟢")

                        with st.expander(f"{priority_emoji} {rec.title}"):
                            st.write(rec.description)
                            st.write(f"**Time required:** {rec.estimated_time_minutes} minutes")

                            st.write("**Recommended actions:**")
                            for action in rec.suggested_actions:
                                st.checkbox(action, key=f"action_{hash(action)}")

                except Exception as e:
                    st.error(f"Failed to generate recommendations: {str(e)}")

        # Interactive tutoring
        st.markdown("### 🧑‍🏫 Interactive Tutoring")

        st.markdown("Get help with specific topics or questions:")

        topic_help = st.text_input("What topic do you need help with?")
        specific_question = st.text_area("Describe a specific question or concept you're struggling with:")

        if st.button("Get AI Tutoring"):
            if not topic_help and not specific_question:
                st.warning("Please enter a topic or question to get tutoring help.")
            else:
                with st.spinner("Getting AI tutoring assistance..."):
                    try:
                        # Create a tutoring prompt
                        prompt = f"""
You are an expert tutor helping a student with exam preparation.

Topic: {topic_help or 'General exam preparation'}
Question/Concept: {specific_question or 'General study help'}

Please provide:
1. Clear explanation of the concept
2. Common mistakes to avoid
3. Practice tips
4. Additional resources or study strategies

Be encouraging and supportive in your response.
"""

                        response = llm_service.generate(prompt, max_tokens=400)
                        st.write(response)

                    except Exception as e:
                        st.error(f"Failed to get tutoring help: {str(e)}")

        # Socratic guidance
        st.markdown("### 🤔 Socratic Guidance")

        st.markdown("Answer these guiding questions to deepen your understanding:")

        if st.button("Generate Guiding Questions"):
            with st.spinner("Creating guiding questions..."):
                try:
                    prompt = f"""
Based on this exam performance:
- Score: {selected_result.metrics.accuracy_percentage:.1f}%
- Weak areas: {', '.join(selected_result.weak_areas.topics) if selected_result.weak_areas.topics else 'None identified'}

Generate 3-5 thoughtful questions that will help the student reflect on their learning and identify areas for improvement. Use the Socratic method - don't give direct answers, but guide thinking.
"""

                    questions = llm_service.generate(prompt, max_tokens=300)
                    st.write(questions)

                except Exception as e:
                    st.error(f"Failed to generate questions: {str(e)}")

# Configuration status
st.markdown("---")
st.markdown("### ⚙️ AI Configuration Status")

providers = llm_service.get_available_providers()
if providers:
    st.success(f"✅ {len(providers)} LLM provider(s) configured: {', '.join(providers)}")

    # Test providers
    if st.button("Test LLM Connection"):
        with st.spinner("Testing providers..."):
            test_results = []
            for provider in providers:
                working = llm_service.test_provider(provider)
                status = "✅ Working" if working else "❌ Failed"
                test_results.append(f"{provider}: {status}")

            for result in test_results:
                st.write(result)
else:
    st.error("❌ No LLM providers configured")
    st.markdown("Please configure LLM providers in `config/llm_config.yaml`")