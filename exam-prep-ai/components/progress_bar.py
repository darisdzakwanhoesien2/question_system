import streamlit as st
from typing import Dict, Any, List
from datetime import datetime, timedelta

def render_progress_bar(current: int, total: int, label: str = "Progress", show_percentage: bool = True):
    """
    Render a simple progress bar.

    Args:
        current: Current progress value
        total: Total value
        label: Label for the progress bar
        show_percentage: Whether to show percentage
    """
    if total == 0:
        percentage = 0
    else:
        percentage = min(100, (current / total) * 100)

    st.progress(percentage / 100, text=f"{label}: {current}/{total}")

    if show_percentage:
        st.caption(f"{percentage:.1f}% Complete")

def render_exam_progress(session_progress: Dict[str, Any]):
    """
    Render exam progress with detailed information.

    Args:
        session_progress: Progress information from session manager
    """
    st.markdown("### 📊 Exam Progress")

    current = session_progress.get('answered_questions', 0)
    total = session_progress.get('total_questions', 0)
    percentage = session_progress.get('progress_percentage', 0)

    # Main progress bar
    st.progress(percentage / 100, text=f"Questions Completed: {current}/{total}")

    # Detailed metrics
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Completed", f"{current}/{total}", f"{percentage:.1f}%")

    with col2:
        remaining = session_progress.get('remaining_questions', 0)
        st.metric("Remaining", remaining)

    with col3:
        current_q = session_progress.get('current_index', 0) + 1
        st.metric("Current Question", current_q)

def render_time_progress(remaining_seconds: int, total_seconds: int):
    """
    Render time remaining progress.

    Args:
        remaining_seconds: Seconds remaining
        total_seconds: Total seconds for exam
    """
    st.markdown("### ⏱️ Time Remaining")

    if total_seconds == 0:
        percentage = 100
    else:
        percentage = max(0, (remaining_seconds / total_seconds) * 100)

    # Time formatting
    remaining_td = timedelta(seconds=remaining_seconds)
    hours, remainder = divmod(remaining_td.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    if hours > 0:
        time_str = f"{hours}:{minutes:02d}:{seconds:02d}"
    else:
        time_str = f"{minutes:02d}:{seconds:02d}"

    # Color coding based on time remaining
    if percentage > 50:
        color = "🟢"
    elif percentage > 25:
        color = "🟡"
    else:
        color = "🔴"

    st.progress(percentage / 100, text=f"{color} {time_str} remaining")

    # Warning for low time
    if percentage <= 25:
        st.warning("⚠️ Less than 25% time remaining!")
    elif percentage <= 10:
        st.error("🚨 Less than 10% time remaining!")

def render_section_progress(exam_sections: List[Dict[str, Any]], current_section: str):
    """
    Render progress for each section.

    Args:
        exam_sections: List of section information
        current_section: Current section name
    """
    st.markdown("### 📑 Section Progress")

    for section in exam_sections:
        section_name = section.get('name', 'Unknown')
        total_q = len(section.get('questions', []))
        completed_q = len(section.get('completed_questions', []))

        if total_q == 0:
            continue

        percentage = (completed_q / total_q) * 100

        # Highlight current section
        if section_name == current_section:
            st.markdown(f"**{section_name}** (Current)")
        else:
            st.markdown(f"**{section_name}**")

        st.progress(percentage / 100, text=f"{completed_q}/{total_q} questions")

def render_overall_stats(stats: Dict[str, Any]):
    """
    Render overall exam statistics.

    Args:
        stats: Statistics dictionary
    """
    st.markdown("### 📈 Overall Statistics")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Exams", stats.get('total_exams', 0))

    with col2:
        avg_score = stats.get('average_score', 0)
        st.metric("Average Score", f"{avg_score:.1f}%")

    with col3:
        highest = stats.get('highest_score', 0)
        st.metric("Highest Score", f"{highest:.1f}%")

    with col4:
        consistency = stats.get('consistency_score', 0)
        st.metric("Consistency", f"{consistency:.1f}%")

def render_performance_trend(scores: List[float], labels: List[str] = None):
    """
    Render performance trend chart.

    Args:
        scores: List of scores over time
        labels: Labels for x-axis (optional)
    """
    if not scores:
        st.info("No performance data available yet.")
        return

    st.markdown("### 📈 Performance Trend")

    # Simple line chart
    chart_data = {"Score": scores}
    if labels:
        chart_data["Exam"] = labels

    st.line_chart(chart_data)

    # Trend analysis
    if len(scores) > 1:
        trend = "improving" if scores[-1] > scores[0] else "declining" if scores[-1] < scores[0] else "stable"
        st.caption(f"Trend: Your performance is {trend}")