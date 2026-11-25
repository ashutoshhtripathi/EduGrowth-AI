"""
Student Hub Interface for EduGrowth AI.
Friendly, motivating, jargon-free academic overview, GPA Goal Planner, Career Matcher, and Personal AI Helper.
"""

import pandas as pd
import plotly.express as px
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
    COLOR_WARNING,
    apply_clean_chart_theme,
    build_student_radar_chart,
    get_role_theme,
    render_hero_header,
    render_html,
    render_kpi_card,
    render_person_card,
)

STUDENT_VIEWS = [
    "🚀 My Dashboard",
    "🎯 GPA Goal Planner",
    "🧭 Career & Skills Guide",
    "🤖 My AI Study Helper",
]


def render_student_portal(current_user: dict, df: pd.DataFrame, predictor):
    active_view = render_sidebar_shell(current_user, STUDENT_VIEWS, "student_active_view")
    theme = get_role_theme("student")
    accent = theme["primary"]

    target_sid = current_user["student_id"]
    s_row = df[df["student_id"] == target_sid].iloc[0]
    diag = predictor.predict_single(s_row.to_dict())

    with st.sidebar:
        st.markdown("##### **My Details**")
        st.write(f"**ID:** `{s_row['student_id']}`")
        st.write(f"**Branch:** {s_row['department']}")
        st.write(f"**Semester:** {s_row['semester']}")
        st.write(f"**Credits:** {int(s_row['credit_load'])}")
        st.divider()

    render_sidebar_footer(current_user)

    if active_view == STUDENT_VIEWS[0]:
        _render_my_dashboard(current_user, df, s_row, diag, accent)
    elif active_view == STUDENT_VIEWS[1]:
        render_hero_header(
            f"GPA Goal Planner • {current_user['name']}",
            "Pick your dream GPA for this semester and see the exact attendance, test scores, and study hours to get there.",
            f"Expected GPA: {diag['predicted_end_term_gpa']:.2f} / 10",
            "student",
        )
        render_goal_simulator(s_row, predictor, key_prefix=f"stu_sim_{target_sid}", accent_color=accent)
    elif active_view == STUDENT_VIEWS[2]:
        _render_career_guide(current_user, s_row, accent)
    else:
        render_chatbot_interface(current_user, df)


def _render_my_dashboard(current_user: dict, df: pd.DataFrame, s_row: pd.Series, diag: dict, accent: str):
    friendly_status = (
        "Doing Great — Keep It Up!"
        if diag["risk_level"] == 0
        else ("Needs a Little Extra Focus" if diag["risk_level"] == 1 else "Needs Urgent Attention — Talk to Your Advisor")
    )
    badge_kind = "safe" if diag["risk_level"] == 0 else ("warning" if diag["risk_level"] == 1 else "critical")

    render_hero_header(
        f"Hi, {current_user['name']} 👋",
        f"{s_row['department']} • Semester {s_row['semester']} • Here is how your semester is going right now.",
        friendly_status,
        "student",
    )

    render_person_card(
        current_user["name"],
        f"Student ID: {s_row['student_id']} • {s_row['department']} (Sem {s_row['semester']})",
        friendly_status,
        badge_kind=badge_kind,
        right_note=f"Pending Subjects: {int(s_row['backlog_count'])}",
    )

    sc1, sc2, sc3, sc4 = st.columns(4)
    with sc1:
        render_kpi_card("Past CGPA", f"{s_row['prev_cgpa']:.2f}", "Before this semester", accent_color=accent, icon="📘", progress_pct=s_row["prev_cgpa"] * 10)
    with sc2:
        gpa_delta = diag["gpa_delta"]
        render_kpi_card(
            "Expected Term GPA",
            f"{diag['predicted_end_term_gpa']:.2f}",
            "Going up!" if gpa_delta > 0.2 else ("Steady" if abs(gpa_delta) <= 0.2 else "Slightly dipping"),
            accent_color=accent,
            delta_text=f"{gpa_delta:+.2f}",
            delta_positive=gpa_delta >= 0,
            icon="🎯",
            progress_pct=diag["predicted_end_term_gpa"] * 10,
        )
    with sc3:
        att_ok = s_row["attendance_rate_pct"] >= 75.0
        render_kpi_card(
            "My Attendance",
            f"{s_row['attendance_rate_pct']:.1f}%",
            "Above the 75% rule" if att_ok else "Below 75% — attend more classes",
            accent_color=COLOR_SAFE if att_ok else COLOR_CRITICAL,
            icon="📅",
            progress_pct=s_row["attendance_rate_pct"],
        )
    with sc4:
        render_kpi_card(
            "Job Readiness",
            f"{s_row['employability_index']:.0f}/100",
            f"{int(s_row['projects_count'])} projects • {int(s_row['certifications_count'])} certs",
            accent_color=COLOR_SAFE if s_row["employability_index"] >= 70 else COLOR_WARNING,
            icon="💼",
            progress_pct=s_row["employability_index"],
        )

    st.write("")
    p1, p2 = st.columns([1.05, 0.95], gap="large")
    with p1:
        st.markdown("##### **Your Grade Journey So Far**")
        st.caption("How your scores have moved from school to your expected semester GPA.")
        prog_df = pd.DataFrame(
            {
                "Stage": ["School Marks (/10)", "Past CGPA", "Current Tests (/10)", "Expected GPA"],
                "Score": [
                    s_row["prior_hs_percentage"] / 10.0,
                    s_row["prev_cgpa"],
                    s_row["internal_assessment_score"] / 10.0,
                    diag["predicted_end_term_gpa"],
                ],
            }
        )
        fig_s = px.area(
            prog_df,
            x="Stage",
            y="Score",
            markers=True,
            line_shape="spline",
            height=300,
            color_discrete_sequence=[accent],
        )
        fig_s = apply_clean_chart_theme(fig_s, height=300)
        fig_s.update_yaxes(range=[0, 10], title="Score (out of 10)")
        fig_s.update_xaxes(title=None)
        st.plotly_chart(fig_s, width="stretch")

    with p2:
        st.markdown("##### **You vs Top 25% Students in Your Branch**")
        st.caption("See where you already shine and which habits to boost.")
        dept_df = df[df["department"] == s_row["department"]]
        top_quartile = dept_df[dept_df["target_end_term_gpa"] >= dept_df["target_end_term_gpa"].quantile(0.75)].mean(numeric_only=True)
        fig_rad = build_student_radar_chart(
            s_row,
            top_quartile,
            student_label="You",
            benchmark_label="Top 25% Peers",
            accent_color=accent,
            height=300,
        )
        st.plotly_chart(fig_rad, width="stretch")

    a1, a2 = st.columns([1.2, 0.8], gap="large")
    with a1:
        st.markdown("##### **Your Simple Action Checklist**")
        st.caption("Check off these steps as you work through your week:")
        for idx, rec in enumerate(diag["prescribed_interventions"]):
            st.checkbox(rec, key=f"stu_chk_{s_row['student_id']}_{idx}")

        student_interventions = [
            it for it in st.session_state.get("interventions", []) if it["student_id"] == s_row["student_id"]
        ]
        if student_interventions:
            st.markdown("##### **Messages & Sessions from Your Teachers**")
            for it in student_interventions:
                render_html(
                    f'<div class="callout-card">📌 <strong>{it["intervention_type"]}</strong> ({it["status"]}) — With {it["assigned_to"]}<br><span style="color:#64748B; font-size:0.82rem;">{it["notes"]}</span></div>'
                )

    with a2:
        st.markdown("##### **My Portfolio & Skills**")
        render_html(
            f"""
            <div class="surface-panel">
            <div class="panel-title">What You Have Built</div>
            <div style="display:flex; justify-content:space-between; margin-bottom:0.6rem;">
            <span>📜 Certificates</span><strong>{int(s_row['certifications_count'])} Earned</strong>
            </div>
            <div style="display:flex; justify-content:space-between; margin-bottom:0.6rem;">
            <span>💻 Tech Skills</span><strong>{int(s_row['technical_skills_count'])} Skills</strong>
            </div>
            <div style="display:flex; justify-content:space-between; margin-bottom:0.6rem;">
            <span>🛠️ Projects</span><strong>{int(s_row['projects_count'])} Completed</strong>
            </div>
            <div style="display:flex; justify-content:space-between; margin-bottom:0.6rem;">
            <span>🐙 Coding Activity</span><strong>{s_row['github_activity_score']:.0f}/100</strong>
            </div>
            <div style="display:flex; justify-content:space-between;">
            <span>💼 Internship</span><strong>{"Done ✅" if s_row['internship_completed'] == 1 else "Not yet — keep applying"}</strong>
            </div>
            </div>
            """
        )


def _render_career_guide(current_user: dict, s_row: pd.Series, accent: str):
    render_hero_header(
        f"Career & Skills Guide • {current_user['name']}",
        "Jobs that match your branch, projects, and skills—plus what to learn next.",
        f"Job Readiness: {s_row['employability_index']:.0f}/100",
        "student",
    )

    readiness = evaluate_career_readiness(s_row.to_dict())

    cp1, cp2, cp3 = st.columns(3)
    for col, (i, item) in zip([cp1, cp2, cp3], enumerate(readiness["top_tracks"])):
        track = item["track"]
        score = item["match_score"]
        skill_tags = "".join(f'<span class="tag-pill">{sk}</span>' for sk in track["key_skills"][:4])
        with col:
            render_html(
                f"""
                <div class="kpi-card" style="border-top: 4px solid {accent}; min-height: 275px;">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.45rem;">
                <span class="kpi-label">Top Match #{i+1}</span>
                <span style="font-weight:800; color:{COLOR_SAFE}; font-size:1.05rem;">{score}% Fit</span>
                </div>
                <div style="font-weight:700; font-size:1.05rem; color:#0F172A; margin-bottom:0.35rem;">{track['title']}</div>
                <div class="progress-track" style="margin-bottom:0.65rem;">
                <div class="progress-fill" style="width:{score}%; background:{COLOR_SAFE};"></div>
                </div>
                <div style="font-size:0.82rem; color:#64748B; margin-bottom:0.65rem;">{track['description']}</div>
                <div>{skill_tags}</div>
                </div>
                """
            )

    st.write("")
    g1, g2 = st.columns(2, gap="large")
    with g1:
        st.markdown("##### **What to Work On Next**")
        for g in readiness["gaps"]:
            render_html(f'<div class="callout-card">💡 {g}</div>')
    with g2:
        st.markdown("##### **Helpful Certificates to Try**")
        for cert in readiness["recommended_certifications"]:
            render_html(f'<div class="callout-card" style="border-left-color:{COLOR_SAFE};">🎓 <strong>{cert}</strong></div>')
