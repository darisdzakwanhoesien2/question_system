import streamlit as st
from config.settings import load_settings

# Load settings
settings = load_settings()

st.set_page_config(
    page_title="Exam Prep AI",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("📚 Exam Prep AI")
st.markdown("Welcome to your AI-powered exam preparation system!")

st.markdown("""
## Get Started

Navigate through the pages using the sidebar to:

1. **Select Exam** - Choose your exam type and set
2. **Take Exam** - Answer questions with real-time timer
3. **Review Answers** - Check your answers and correct solutions
4. **Exam Analytics** - View detailed performance analytics
5. **LLM Feedback** - Get AI-powered feedback and recommendations

## Features

- Multiple exam types (SAT, GRE, TOEFL)
- Various question types (MCQ, Short Answer, Essay)
- AI-powered grading and feedback
- Performance tracking and analytics
- Personalized learning recommendations
""")

# Display some stats or quick access
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Exam Types", "3")
with col2:
    st.metric("Question Types", "3")
with col3:
    st.metric("AI Providers", "3")

st.markdown("---")
st.markdown("Built with ❤️ using Streamlit and AI")