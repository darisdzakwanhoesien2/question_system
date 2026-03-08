import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from services.analytics_service import analytics_service
from services.exam_service import exam_service
from components.progress_bar import render_performance_trend

st.title("📊 Exam Analytics")

st.markdown("View detailed analytics and insights about your exam performance.")

# Get user's exam results
exam_results = exam_service.get_exam_results()

if not exam_results:
    st.info("No exam results available yet. Complete some exams to see analytics!")
    if st.button("Take an Exam"):
        st.switch_page("pages/01_select_exam.py")
    st.stop()

# Generate analytics summary
analytics_summary = analytics_service.generate_analytics_summary()

# Display summary metrics
st.markdown("### 📈 Performance Summary")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Exams Taken", analytics_summary.total_exams_taken)

with col2:
    st.metric("Average Score", f"{analytics_summary.average_score:.1f}%")

with col3:
    st.metric("Highest Score", f"{max(analytics_summary.improvement_trend) if analytics_summary.improvement_trend else 0:.1f}%")

with col4:
    st.metric("Consistency", f"{analytics_summary.consistency_score:.1f}%")

# Performance trend
if analytics_summary.improvement_trend and len(analytics_summary.improvement_trend) > 1:
    st.markdown("### 📈 Performance Trend")
    render_performance_trend(analytics_summary.improvement_trend)

# Topic analysis
st.markdown("### 🎯 Topic Performance")

if analytics_summary.favorite_topics:
    st.markdown("**Strongest Topics:**")
    for topic in analytics_summary.favorite_topics:
        st.markdown(f"- {topic}")

if analytics_summary.struggling_topics:
    st.markdown("**Areas Needing Improvement:**")
    for topic in analytics_summary.struggling_topics:
        st.markdown(f"- {topic}")

# Detailed results table
st.markdown("### 📋 Detailed Results")

# Convert results to DataFrame
results_data = []
for result in exam_results:
    results_data.append({
        'Exam': result.exam_name,
        'Date': result.completed_at.strftime('%Y-%m-%d'),
        'Score': f"{result.metrics.accuracy_percentage:.1f}%",
        'Questions': result.metrics.total_questions,
        'Correct': result.metrics.correct_answers,
        'Time (min)': result.metrics.total_time_taken,
        'Avg Time/Q': f"{result.metrics.average_time_per_question:.1f}s"
    })

df = pd.DataFrame(results_data)
st.dataframe(df, use_container_width=True)

# Performance analysis
st.markdown("### 🔍 Detailed Analysis")

selected_exam = st.selectbox(
    "Select exam for detailed analysis:",
    [f"{r.exam_name} ({r.completed_at.strftime('%Y-%m-%d')})" for r in exam_results]
)

if selected_exam:
    # Find the selected result
    selected_result = None
    for result in exam_results:
        if f"{result.exam_name} ({result.completed_at.strftime('%Y-%m-%d')})" == selected_exam:
            selected_result = result
            break

    if selected_result:
        # Generate detailed analysis
        analysis = analytics_service.generate_performance_analysis(selected_result)

        st.markdown("#### Analysis")
        st.write(analysis.get('llm_analysis', 'Analysis not available'))

        # Show metrics
        if 'metrics' in analysis:
            metrics = analysis['metrics']
            st.markdown("#### Key Metrics")

            mcol1, mcol2, mcol3 = st.columns(3)
            with mcol1:
                st.metric("Time Efficiency", f"{metrics.get('time_efficiency', 0):.1f}%")
            with mcol2:
                st.metric("Consistency", f"{metrics.get('consistency_score', 0):.1f}%")
            with mcol3:
                st.metric("Topic Mastery", "See breakdown")

        # Topic breakdown
        if selected_result.topic_performance:
            st.markdown("#### Topic Breakdown")

            topic_data = []
            for tp in selected_result.topic_performance:
                topic_data.append({
                    'Topic': tp.topic,
                    'Questions': tp.questions_count,
                    'Correct': tp.correct_count,
                    'Accuracy': f"{tp.accuracy:.1f}%",
                    'Avg Time': f"{tp.average_time:.1f}s"
                })

            topic_df = pd.DataFrame(topic_data)
            st.dataframe(topic_df, use_container_width=True)

# Study recommendations
st.markdown("### 💡 Study Recommendations")

if st.button("Generate Recommendations"):
    with st.spinner("Generating personalized recommendations..."):
        # Get the most recent result for recommendations
        if exam_results:
            latest_result = exam_results[0]  # Assuming sorted by date
            recommendations = analytics_service.generate_study_recommendations(latest_result)

            for rec in recommendations:
                with st.expander(f"{rec.title} ({rec.priority.title()} Priority)"):
                    st.write(rec.description)
                    st.write(f"**Estimated time:** {rec.estimated_time_minutes} minutes")
                    st.write("**Suggested actions:**")
                    for action in rec.suggested_actions:
                        st.markdown(f"- {action}")

# Export data
st.markdown("---")
st.markdown("### 📥 Export Data")

if st.button("Export Analytics Data"):
    analytics_df = analytics_service.export_analytics_data()

    # Convert to CSV
    csv = analytics_df.to_csv(index=False)

    st.download_button(
        label="Download CSV",
        data=csv,
        file_name="exam_analytics.csv",
        mime="text/csv",
        key="download-analytics"
    )