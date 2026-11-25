"""
Parent / Family Portal for EduGrowth AI.
Warm, simple, everyday English so any parent can understand attendance, exams,
achievements, teacher meetings, and their child's career direction at a glance.
"""

from datetime import date, timedelta
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from career_recommender import evaluate_career_readiness
from ui.chatbot_panel import render_chatbot_interface
from ui.shared_widgets import (
    render_goal_simulator,
    render_sidebar_footer,
    render_sidebar_shell,
)
from ui.theme import (
    COLOR_CRITICAL,
    COLOR_SAFE,
    apply_clean_chart_theme,
    get_role_theme,
    is_dark_mode,
    render_hero_header,
    render_html,
    render_kpi_card,
    render_person_card,
)

PARENT_VIEWS = [
    "🏡 Child's Progress Summary",
    "🌟 Achievements & Book Teacher Call",
    "🎯 Grade Planner & Career Outlook",
    "🤖 Parent Helper AI",
]


def render_parent_portal(current_user: dict, df: pd.DataFrame, predictor):
    active_view = render_sidebar_shell(current_user, PARENT_VIEWS, "parent_active_view")
    theme = get_role_theme("parent")
    accent = theme["primary"]

    target_sid = current_user["student_id"]
    p_student = df[df["student_id"] == target_sid].iloc[0]
    p_diag = predictor.predict_single(p_student.to_dict())

    with st.sidebar:
        st.markdown("##### **Your Child's Info**")
        st.write(f"**Name:** {p_student['student_name']}")
        st.write(f"**ID:** `{p_student['student_id']}`")
        st.write(f"**Branch:** {p_student['department']}")
        st.write(f"**Semester:** {p_student['semester']}")
        st.divider()

    render_sidebar_footer(current_user)

    if active_view == PARENT_VIEWS[0]:
        _render_progress_summary(current_user, df, p_student, p_diag, accent)
    elif active_view == PARENT_VIEWS[1]:
        _render_achievements_and_call(current_user, p_student, p_diag, accent)
    elif active_view == PARENT_VIEWS[2]:
        _render_planner_and_careers(current_user, p_student, predictor, accent)
    else:
        render_chatbot_interface(current_user, df)


def _render_progress_summary(current_user: dict, df: pd.DataFrame, p_student: pd.Series, p_diag: dict, accent: str):
    render_hero_header(
        "Parent Progress Portal",
        f"Hello, {current_user['name']} • Easy-to-read update on {p_student['student_name']}'s college progress.",
        f"Student ID: {p_student['student_id']}",
        "parent",
    )

    att_ok = p_student["attendance_rate_pct"] >= 75.0
    status_lbl = "Attendance & Progress On Track" if (att_ok and p_diag["risk_level"] == 0) else "Needs Some Support"
    badge_kind = "safe" if (att_ok and p_diag["risk_level"] == 0) else "warning"

    render_person_card(
        p_student["student_name"],
        f"{p_student['department']} • Semester {p_student['semester']}",
        status_lbl,
        badge_kind=badge_kind,
        right_note=f"Expected GPA: {p_diag['predicted_end_term_gpa']:.2f} / 10",
    )

    if not att_ok:
        st.warning(
            f"⚠️ **Attendance Note:** {p_student['student_name']}'s class attendance is **{p_student['attendance_rate_pct']:.1f}%**, "
            "which is below the college's 75% rule. Attending classes regularly will help them stay eligible for final exams."
        )
    else:
        st.success(
            f"✅ **Good Attendance:** {p_student['student_name']} has **{p_student['attendance_rate_pct']:.1f}%** attendance, which comfortably meets the 75% rule."
        )

    st.write("")
    pc1, pc2, pc3, pc4 = st.columns(4)
    with pc1:
        render_kpi_card(
            "Class Attendance",
            f"{p_student['attendance_rate_pct']:.1f}%",
            "Must be 75% or higher",
            accent_color=COLOR_SAFE if att_ok else COLOR_CRITICAL,
            icon="📅",
            progress_pct=p_student["attendance_rate_pct"],
        )
    with pc2:
        render_kpi_card(
            "Test & Quiz Average",
            f"{p_student['internal_assessment_score']:.1f}/100",
            "Mid-term exam marks",
            accent_color=accent,
            icon="📝",
            progress_pct=p_student["internal_assessment_score"],
        )
    with pc3:
        render_kpi_card(
            "Homework On Time",
            f"{p_student['assignment_completion_pct']:.1f}%",
            "Assignments submitted",
            accent_color=accent,
            icon="📚",
            progress_pct=p_student["assignment_completion_pct"],
        )
    with pc4:
        bl = int(p_student["backlog_count"])
        render_kpi_card(
            "Subjects to Clear",
            f"{bl}",
            "All past subjects passed!" if bl == 0 else "Old subjects still pending",
            accent_color=COLOR_SAFE if bl == 0 else COLOR_CRITICAL,
            icon="📌",
        )

    st.write("")
    dark = is_dark_mode()
    c_bg = "#111827" if dark else "#FFFFFF"
    c_font = "#E2E8F0" if dark else "#334155"

    g1, g2 = st.columns([1, 1.15], gap="large")
    with g1:
        st.markdown("##### **Attendance Meter**")
        st.caption("Green area (75%+) means your child is safe to take final exams.")
        gauge = go.Figure(
            go.Indicator(
                mode="gauge+number",
                value=float(p_student["attendance_rate_pct"]),
                number={"suffix": "%", "font": {"color": c_font}},
                title={"text": "Class Attendance (Goal: 75%+)", "font": {"size": 14, "color": c_font}},
                gauge={
                    "axis": {"range": [0, 100], "tickcolor": c_font, "tickfont": {"color": c_font}},
                    "bar": {"color": accent},
                    "threshold": {"line": {"color": COLOR_CRITICAL, "width": 3}, "thickness": 0.75, "value": 75},
                    "steps": [
                        {"range": [0, 65], "color": "rgba(239, 68, 68, 0.25)" if dark else "#FEE2E2"},
                        {"range": [65, 75], "color": "rgba(245, 158, 11, 0.25)" if dark else "#FEF3C7"},
                        {"range": [75, 100], "color": "rgba(16, 185, 129, 0.25)" if dark else "#DCFCE7"},
                    ],
                },
            )
        )
        gauge.update_layout(height=275, margin=dict(l=20, r=20, t=45, b=10), paper_bgcolor=c_bg)
        st.plotly_chart(gauge, width="stretch")

    with g2:
        st.markdown("##### **How Your Child Compares to Classmates**")
        st.caption("Side-by-side comparison with the average student in the same branch.")
        dept_avg = df[df["department"] == p_student["department"]].mean(numeric_only=True)
        metrics = ["Attendance", "Test Marks", "Homework", "Job Readiness"]
        ward_vals = [
            float(p_student["attendance_rate_pct"]),
            float(p_student["internal_assessment_score"]),
            float(p_student["assignment_completion_pct"]),
            float(p_student["employability_index"]),
        ]
        peer_vals = [
            float(dept_avg["attendance_rate_pct"]),
            float(dept_avg["internal_assessment_score"]),
            float(dept_avg["assignment_completion_pct"]),
            float(dept_avg["employability_index"]),
        ]
        fig_bar = go.Figure(
            data=[
                go.Bar(name=p_student["student_name"], x=metrics, y=ward_vals, marker_color=accent),
                go.Bar(name="Branch Average", x=metrics, y=peer_vals, marker_color="#64748B" if dark else "#CBD5E1"),
            ]
        )
        fig_bar = apply_clean_chart_theme(fig_bar, height=275)
        fig_bar.update_layout(
            barmode="group",
            margin=dict(l=20, r=20, t=35, b=20),
            legend=dict(orientation="h", y=1.12, font=dict(color=c_font)),
            yaxis=dict(range=[0, 105]),
        )
        st.plotly_chart(fig_bar, width="stretch")


def _render_achievements_and_call(current_user: dict, p_student: pd.Series, p_diag: dict, accent: str):
    render_hero_header(
        "Achievements & Teacher Connect",
        f"See what {p_student['student_name']} has accomplished and book a quick call with their class teacher.",
        "Family Support",
        "parent",
    )

    if "parent_meetings" not in st.session_state:
        st.session_state["parent_meetings"] = []

    c1, c2 = st.columns([1, 1], gap="large")
    with c1:
        st.markdown("##### **Highlights This Semester**")
        render_html(
            f"""
            <div class="surface-panel">
            <div class="panel-title">Good Things to Celebrate</div>
            <p style="margin-bottom:0.6rem; font-size:0.9rem;">⭐ <strong>Hands-on Projects:</strong> Built {int(p_student['projects_count'])} practical project(s).</p>
            <p style="margin-bottom:0.6rem; font-size:0.9rem;">⭐ <strong>Extra Courses:</strong> Completed {int(p_student['certifications_count'])} skill certificate(s).</p>
            <p style="margin-bottom:0.6rem; font-size:0.9rem;">⭐ <strong>Weekly Study Time:</strong> Studies about {p_student['lms_weekly_hours']:.1f} hours/week online.</p>
            <p style="font-size:0.9rem;">⭐ <strong>Expected Final Grade:</strong> {p_diag['predicted_end_term_gpa']:.2f} out of 10.0.</p>
            </div>
            """
        )

        st.markdown("##### **Notes from College Advisors**")
        for drv in p_diag["key_risk_drivers"]:
            render_html(f'<div class="callout-card">📝 {drv}</div>')

    with c2:
        st.markdown("##### **Book a Call with Class Teacher (Prof. Arvind Sharma)**")
        with st.form("parent_meeting_form"):
            m_date = st.date_input("Pick a Date:", value=date.today() + timedelta(days=2), min_value=date.today())
            m_slot = st.selectbox("Pick a Time:", ["10:30 AM - 11:00 AM", "02:00 PM - 02:30 PM", "04:30 PM - 05:00 PM"])
            m_mode = st.radio("How would you like to meet?", ["Video Call", "Visit Campus"], horizontal=True)
            m_topic = st.text_input("What would you like to talk about? (Optional)", placeholder="e.g. Attendance or exam preparation")
            submitted = st.form_submit_button("📅 Request Meeting", width="stretch")
            if submitted:
                st.session_state["parent_meetings"].insert(
                    0,
                    {
                        "date": str(m_date),
                        "slot": m_slot,
                        "mode": m_mode,
                        "topic": m_topic or "General progress check-in",
                    },
                )
                st.success(f"Meeting requested for {m_date} ({m_slot}) via {m_mode}.")

        if st.session_state["parent_meetings"]:
            st.markdown("**Your Requested Meetings:**")
            for mt in st.session_state["parent_meetings"]:
                render_html(
                    f'<div class="callout-card" style="border-left-color:{COLOR_SAFE};">📅 <strong>{mt["date"]}</strong> • {mt["slot"]} ({mt["mode"]})<br><span style="color:#64748B; font-size:0.82rem;">Topic: {mt["topic"]}</span></div>'
                )


def _render_planner_and_careers(current_user: dict, p_student: pd.Series, predictor, accent: str):
    render_hero_header(
        "Grade Planner & Future Career Outlook",
        f"See how small improvements in attendance or study time can raise {p_student['student_name']}'s final GPA.",
        f"Expected GPA: {predictor.predict_single(p_student.to_dict())['predicted_end_term_gpa']:.2f}",
        "parent",
    )

    render_goal_simulator(
        p_student,
        predictor,
        key_prefix=f"par_sim_{p_student['student_id']}",
        accent_color=accent,
        parent_friendly=True,
    )

    dark = is_dark_mode()
    title_col = "#F1F5F9" if dark else "#0F172A"
    sub_col = "#94A3B8" if dark else "#64748B"

    st.divider()
    st.markdown(f"##### **Best Future Job Matches for {p_student['student_name']}**")
    readiness = evaluate_career_readiness(p_student.to_dict())
    cols = st.columns(3)
    for col, (i, item) in zip(cols, enumerate(readiness["top_tracks"])):
        track = item["track"]
        with col:
            render_html(
                f"""
                <div class="kpi-card" style="border-top:3px solid {accent};">
                <div class="kpi-label">Match #{i+1}</div>
                <div style="font-weight:700; font-size:1rem; color:{title_col};">{track['title']}</div>
                <div style="font-size:0.84rem; color:{COLOR_SAFE}; font-weight:700; margin:0.35rem 0;">{item['match_score']}% Ready</div>
                <div class="progress-track" style="margin-bottom:0.55rem;">
                <div class="progress-fill" style="width:{item['match_score']}%; background:{COLOR_SAFE};"></div>
                </div>
                <div style="font-size:0.8rem; color:{sub_col};">{track['description']}</div>
                </div>
                """
            )
