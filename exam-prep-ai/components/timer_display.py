import streamlit as st
from typing import Optional, Callable
import time
from datetime import datetime, timedelta

def render_timer_display(remaining_seconds: int, total_seconds: int = 0, show_progress: bool = True):
    """
    Render a timer display component.

    Args:
        remaining_seconds: Seconds remaining
        total_seconds: Total seconds (for progress calculation)
        show_progress: Whether to show progress bar
    """
    # Format time
    remaining_td = timedelta(seconds=remaining_seconds)
    hours, remainder = divmod(remaining_td.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    if hours > 0:
        time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    else:
        time_str = f"{minutes:02d}:{seconds:02d}"

    # Color coding
    if remaining_seconds > 1800:  # > 30 min
        color = "🟢"
        status = "Good"
    elif remaining_seconds > 600:  # > 10 min
        color = "🟡"
        status = "Warning"
    elif remaining_seconds > 300:  # > 5 min
        color = "🟠"
        status = "Critical"
    else:
        color = "🔴"
        status = "Hurry!"

    # Display timer
    st.markdown(f"### ⏱️ Time Remaining: {color} **{time_str}**")

    if remaining_seconds <= 300:  # 5 minutes
        st.error(f"⚠️ {status}: {time_str} remaining!")

    # Progress bar
    if show_progress and total_seconds > 0:
        progress = max(0, remaining_seconds / total_seconds)
        st.progress(progress, text=f"Time Progress: {time_str}")

def render_countdown_timer(remaining_seconds: int, on_timeout: Optional[Callable] = None,
                          auto_update: bool = True):
    """
    Render an auto-updating countdown timer.

    Args:
        remaining_seconds: Initial seconds remaining
        on_timeout: Callback when timer reaches zero
        auto_update: Whether to auto-refresh display
    """
    # Store timer state in session state
    if 'timer_start' not in st.session_state:
        st.session_state.timer_start = time.time()
        st.session_state.timer_duration = remaining_seconds

    # Calculate current remaining time
    elapsed = time.time() - st.session_state.timer_start
    current_remaining = max(0, st.session_state.timer_duration - elapsed)

    # Display timer
    render_timer_display(int(current_remaining), st.session_state.timer_duration)

    # Check for timeout
    if current_remaining <= 0 and on_timeout:
        on_timeout()

    # Auto refresh every few seconds
    if auto_update and current_remaining > 0:
        time.sleep(1)  # Small delay to prevent too frequent updates
        st.rerun()

def render_exam_timer(session_id: str, show_warnings: bool = True):
    """
    Render timer for exam session.

    Args:
        session_id: Exam session ID
        show_warnings: Whether to show time warnings
    """
    from core.session_state_manager import session_state_manager

    remaining = session_state_manager.get_remaining_time()

    if remaining <= 0:
        st.error("⏰ Time's up! Please submit your exam.")
        return

    render_timer_display(remaining, show_progress=True)

    # Time warnings
    if show_warnings:
        if remaining <= 300:  # 5 minutes
            st.error("🚨 Less than 5 minutes remaining!")
        elif remaining <= 600:  # 10 minutes
            st.warning("⚠️ Less than 10 minutes remaining!")
        elif remaining <= 1800:  # 30 minutes
            st.info("ℹ️ Less than 30 minutes remaining")

def render_section_timer(section_time_limit: int, elapsed_section_time: int):
    """
    Render timer for current section.

    Args:
        section_time_limit: Time limit for section in seconds
        elapsed_section_time: Time elapsed in section in seconds
    """
    remaining = max(0, section_time_limit - elapsed_section_time)

    st.markdown("#### Section Time")

    render_timer_display(remaining, section_time_limit, show_progress=True)

    if remaining <= 60:  # 1 minute
        st.error("🚨 Section time almost up!")

def format_time_duration(seconds: int) -> str:
    """
    Format seconds into readable time duration.

    Args:
        seconds: Time in seconds

    Returns:
        Formatted time string
    """
    td = timedelta(seconds=seconds)
    hours, remainder = divmod(td.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    if hours > 0:
        return f"{hours}h {minutes}m {seconds}s"
    elif minutes > 0:
        return f"{minutes}m {seconds}s"
    else:
        return f"{seconds}s"

def render_time_summary(total_time: int, time_spent: int, efficiency_score: Optional[float] = None):
    """
    Render time usage summary.

    Args:
        total_time: Total available time in seconds
        time_spent: Time spent in seconds
        efficiency_score: Optional efficiency score (0-1)
    """
    st.markdown("### ⏱️ Time Summary")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Total Time", format_time_duration(total_time))

    with col2:
        st.metric("Time Spent", format_time_duration(time_spent))

    with col3:
        remaining = max(0, total_time - time_spent)
        st.metric("Time Remaining", format_time_duration(remaining))

    if efficiency_score is not None:
        efficiency_pct = int(efficiency_score * 100)
        st.metric("Time Efficiency", f"{efficiency_pct}%")

        if efficiency_score < 0.5:
            st.warning("Consider improving time management.")
        elif efficiency_score > 0.8:
            st.success("Excellent time management!")

def render_pace_indicator(questions_completed: int, total_questions: int, time_remaining: int,
                         average_time_per_question: float = 60):
    """
    Render pace indicator for exam progress.

    Args:
        questions_completed: Number of questions completed
        total_questions: Total number of questions
        time_remaining: Time remaining in seconds
        average_time_per_question: Average time per question in seconds
    """
    remaining_questions = total_questions - questions_completed
    estimated_time_needed = remaining_questions * average_time_per_question

    st.markdown("### 🏃 Pace Check")

    if estimated_time_needed <= time_remaining:
        st.success("✅ You're on pace!")
        extra_time = time_remaining - estimated_time_needed
        st.caption(f"You have {format_time_duration(int(extra_time))} extra time.")
    else:
        shortage = estimated_time_needed - time_remaining
        st.warning("⚠️ You're behind pace!")
        st.caption(f"You need {format_time_duration(int(shortage))} more time.")

        # Suggest actions
        questions_per_minute = 60 / average_time_per_question
        suggested_pace = remaining_questions / (time_remaining / 60)
        st.info(f"Try to complete ~{suggested_pace:.1f} questions per minute.")