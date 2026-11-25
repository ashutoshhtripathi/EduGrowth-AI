"""
Teacher / Faculty Workspace for EduGrowth AI.
Clear classroom overview, student checkups, 1-click tutoring plans, letters, and Teacher AI.
"""

import pandas as pd
import plotly.express as px
import streamlit as st

from interventions_manager import create_intervention
from letter_generator import generate_academic_letter
from ui.chatbot_panel import render_chatbot_interface
from ui.shared_widgets import (
    render_goal_simulator,
    render_intervention_tracker,
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

FACULTY_VIEWS = [
    "🏫 My Classroom",
    "🩺 Check & Help a Student",
    "📝 Support Plans & Letters",
    "🤖 Teacher AI Assistant",
]


def render_faculty_portal(current_user: dict, df: pd.DataFrame, predictor):
    active_view = render_sidebar_shell(current_user, FACULTY_VIEWS, "faculty_active_view")
    theme = get_role_theme("faculty")
    accent = theme["primary"]

    all_depts = sorted(df["department"].unique().tolist())
    default_dept = current_user.get("department", all_depts[0])
    all_sems = sorted(df["semester"].unique().tolist())
    default_sem = current_user.get("semester", all_sems[0])

    with st.sidebar:
        st.markdown("##### **Switch Class Section**")
        sel_dept = st.selectbox(
            "Department",
            all_depts,
            index=all_depts.index(default_dept) if default_dept in all_depts else 0,
            key="fac_dept_sel",
        )
        sel_sem = st.selectbox(
            "Semester",
            all_sems,
            index=all_sems.index(default_sem) if default_sem in all_sems else 0,
            key="fac_sem_sel",
        )
        st.divider()

    render_sidebar_footer(current_user)

    class_df = df[(df["department"] == sel_dept) & (df["semester"] == sel_sem)].copy()
    scoped_user = {**current_user, "department": sel_dept, "semester": sel_sem}

    if active_view == FACULTY_VIEWS[0]:
        _render_classroom(scoped_user, class_df, accent)
    elif active_view == FACULTY_VIEWS[1]:
        _render_student_checkup(scoped_user, class_df, predictor, accent)
    elif active_view == FACULTY_VIEWS[2]:
        _render_faculty_actions(scoped_user, df, class_df, predictor)
    else:
        render_chatbot_interface(scoped_user, df)


def _render_classroom(current_user: dict, class_df: pd.DataFrame, accent: str):
    f_dept = current_user["department"]
    f_sem = current_user["semester"]

    render_hero_header(
        f"Welcome, {current_user['name']}",
        f"Class: {f_dept} • Semester {f_sem} • Easy overview of attendance, tests, and who needs help",
        f"{len(class_df)} Students in Class",
        "faculty",
    )

    c_att = class_df["attendance_rate_pct"].mean() if len(class_df) else 0.0
    c_assign = class_df["assignment_completion_pct"].mean() if len(class_df) else 0.0
    c_internal = class_df["internal_assessment_score"].mean() if len(class_df) else 0.0
    c_gpa = class_df["target_end_term_gpa"].mean() if len(class_df) else 0.0
    c_at_risk = int((class_df["academic_risk_level"] > 0).sum())

    fc1, fc2, fc3, fc4, fc5 = st.columns(5)
    with fc1:
        render_kpi_card(
            "Class Attendance",
            f"{c_att:.1f}%",
            "Meets 75% rule" if c_att >= 75 else "Needs attendance push",
            accent_color=COLOR_SAFE if c_att >= 75 else COLOR_CRITICAL,
            icon="📅",
            progress_pct=c_att,
        )
    with fc2:
        render_kpi_card("Homework On Time", f"{c_assign:.1f}%", "Class average", accent_color=accent, icon="📚", progress_pct=c_assign)
    with fc3:
        render_kpi_card("Test Score Average", f"{c_internal:.1f}/100", "Mid-term marks", accent_color=accent, icon="📝", progress_pct=c_internal)
    with fc4:
        render_kpi_card("Expected Class GPA", f"{c_gpa:.2f}", "Out of 10.0", accent_color=accent, icon="🎓", progress_pct=c_gpa * 10)
    with fc5:
        render_kpi_card("Students Needing Help", f"{c_at_risk}", "Watchlist or urgent", accent_color=COLOR_WARNING, icon="🤝")

    st.write("")
    ch1, ch2 = st.columns([1.15, 0.85])
    with ch1:
        st.markdown("##### **Attendance vs Test Scores in Your Class**")
        st.caption("Students in the bottom-left (low attendance + low marks) need support first.")
        plot_df = class_df.copy()
        plot_df["Status"] = plot_df["academic_risk_level"].map({0: "Doing Well", 1: "Needs Attention", 2: "Needs Urgent Help"})
        fig = px.scatter(
            plot_df,
            x="attendance_rate_pct",
            y="internal_assessment_score",
            color="Status",
            size="lms_weekly_hours",
            hover_data=["student_id", "student_name", "backlog_count"],
            color_discrete_map={"Doing Well": "#10B981", "Needs Attention": "#F59E0B", "Needs Urgent Help": "#EF4444"},
            labels={"attendance_rate_pct": "Attendance (%)", "internal_assessment_score": "Test Score (/100)"},
            height=315,
        )
        fig.add_vline(x=75, line_dash="dot", line_color="#64748B")
        fig = apply_clean_chart_theme(fig, height=315)
        fig.update_layout(legend=dict(orientation="h", y=1.12))
        st.plotly_chart(fig, width="stretch")

    with ch2:
        st.markdown("##### **Class Status Breakdown**")
        st.caption("How many students are on track vs needing extra help.")
        tier_counts = (
            class_df["academic_risk_level"]
            .map({0: "Doing Well", 1: "Needs Attention", 2: "Needs Urgent Help"})
            .value_counts()
            .reset_index()
        )
        tier_counts.columns = ["Status", "Students"]
        fig_pie = px.pie(
            tier_counts,
            names="Status",
            values="Students",
            hole=0.6,
            color="Status",
            color_discrete_map={"Doing Well": "#10B981", "Needs Attention": "#F59E0B", "Needs Urgent Help": "#EF4444"},
            height=315,
        )
        fig_pie.update_layout(margin=dict(l=10, r=10, t=20, b=10), paper_bgcolor="#FFFFFF")
        st.plotly_chart(fig_pie, width="stretch")

    st.markdown("##### **Full Class List**")
    roster = class_df[
        [
            "student_id",
            "student_name",
            "attendance_rate_pct",
            "assignment_completion_pct",
            "internal_assessment_score",
            "backlog_count",
            "target_end_term_gpa",
            "academic_risk_level",
        ]
    ].copy()
    roster["Status"] = roster["academic_risk_level"].map({0: "🟢 Doing Well", 1: "🟡 Needs Attention", 2: "🔴 Needs Urgent Help"})
    roster = roster.drop(columns=["academic_risk_level"]).sort_values("target_end_term_gpa")
    st.dataframe(
        roster,
        hide_index=True,
        width="stretch",
        height=310,
        column_config={
            "student_id": "ID",
            "student_name": "Student Name",
            "attendance_rate_pct": st.column_config.ProgressColumn("Attendance", min_value=0, max_value=100, format="%.1f%%"),
            "assignment_completion_pct": st.column_config.ProgressColumn("Homework", min_value=0, max_value=100, format="%.1f%%"),
            "internal_assessment_score": st.column_config.NumberColumn("Test Score", format="%.1f"),
            "backlog_count": "Pending Subjects",
            "target_end_term_gpa": st.column_config.NumberColumn("Expected GPA", format="%.2f"),
        },
    )


def _render_student_checkup(current_user: dict, class_df: pd.DataFrame, predictor, accent: str):
    render_hero_header(
        "Check & Help a Student",
        "Pick any student in your class to see why they may be struggling and schedule help in one click.",
        f"{current_user['department']} • Semester {current_user['semester']}",
        "faculty",
    )

    if len(class_df) == 0:
        st.warning("No students found in this section.")
        return

    sort_mode = st.radio(
        "Order student list by:",
        ["Students Needing Help First", "A to Z by Name"],
        horizontal=True,
        key="fac_sort_mode",
    )
    ordered = class_df.sort_values(["academic_risk_level", "attendance_rate_pct"], ascending=[False, True]) if sort_mode.startswith("Students") else class_df.sort_values("student_name")
    options = (ordered["student_id"] + " - " + ordered["student_name"]).tolist()
    picked = st.selectbox("Pick a Student:", options, key="fac_audit_pick")
    sid = picked.split(" - ")[0]
    sel_row = class_df[class_df["student_id"] == sid].iloc[0]
    diag = predictor.predict_single(sel_row.to_dict())
    class_avg = class_df.mean(numeric_only=True)

    badge_kind = "safe" if diag["risk_level"] == 0 else ("warning" if diag["risk_level"] == 1 else "critical")
    badge_txt = "Doing Well" if diag["risk_level"] == 0 else ("Needs Attention" if diag["risk_level"] == 1 else "Needs Urgent Help")
    render_person_card(
        sel_row["student_name"],
        f"ID: {sel_row['student_id']} • Prior CGPA: {sel_row['prev_cgpa']:.2f}",
        badge_txt,
        badge_kind=badge_kind,
        right_note=f"Pending Subjects: {int(sel_row['backlog_count'])}",
    )

    c_left, c_right = st.columns([1.05, 1], gap="large")
    with c_left:
        r1, r2, r3 = st.columns(3)
        with r1:
            render_kpi_card("Expected GPA", f"{diag['predicted_end_term_gpa']:.2f}", diag["gpa_trajectory"], accent_color=accent, icon="🎯")
        with r2:
            att_ok = sel_row["attendance_rate_pct"] >= 75
            render_kpi_card("Attendance", f"{sel_row['attendance_rate_pct']:.1f}%", f"Class avg {class_avg['attendance_rate_pct']:.1f}%", accent_color=COLOR_SAFE if att_ok else COLOR_CRITICAL, icon="📅")
        with r3:
            render_kpi_card("Test Marks", f"{sel_row['internal_assessment_score']:.1f}/100", f"Class avg {class_avg['internal_assessment_score']:.1f}", accent_color=COLOR_WARNING, icon="📝")

        with st.container(border=True):
            st.markdown("**What We Noticed & Suggested Next Steps**")
            for d in diag["key_risk_drivers"]:
                st.markdown(f"• {d}")
            st.markdown("---")
            st.markdown("**Best Way to Help:**")
            for p in diag["prescribed_interventions"]:
                render_html(f'<div class="callout-card">💡 {p}</div>')

            b1, b2 = st.columns(2)
            with b1:
                if st.button("📧 Book Extra Tutoring Session", width="stretch", key="fac_btn_rem"):
                    new_item = create_intervention(
                        student_id=sel_row["student_id"],
                        student_name=sel_row["student_name"],
                        department=current_user["department"],
                        risk_tier="Critical Risk" if diag["risk_level"] == 2 else "Moderate Risk",
                        intervention_type="Extra Tutoring",
                        priority="Urgent" if diag["risk_level"] == 2 else "Medium",
                        assigned_to=current_user["name"],
                        notes="Booked from Teacher Student Checkup.",
                    )
                    st.session_state["interventions"].insert(0, new_item)
                    st.success(f"Tutoring session scheduled for {sel_row['student_name']}.")
            with b2:
                if st.button("⚠️ Send Attendance Reminder", type="secondary", width="stretch", key="fac_btn_att"):
                    new_item = create_intervention(
                        student_id=sel_row["student_id"],
                        student_name=sel_row["student_name"],
                        department=current_user["department"],
                        risk_tier="Critical Risk" if diag["risk_level"] == 2 else "Moderate Risk",
                        intervention_type="Attendance Reminder",
                        priority="High",
                        assigned_to=current_user["name"],
                        notes=f"Attendance is {sel_row['attendance_rate_pct']:.1f}% (below 75% rule).",
                    )
                    st.session_state["interventions"].insert(0, new_item)
                    st.success(f"Attendance reminder saved for {sel_row['student_name']}.")

    with c_right:
        st.markdown("##### **How This Student Compares to Class Average**")
        fig_rad = build_student_radar_chart(
            sel_row,
            class_avg,
            student_label=sel_row["student_name"],
            benchmark_label="Class Average",
            accent_color=accent,
            height=360,
        )
        st.plotly_chart(fig_rad, width="stretch")

    st.divider()
    st.markdown("##### **Test How Extra Support Improves This Student's GPA**")
    render_goal_simulator(sel_row, predictor, key_prefix=f"fac_sim_{sid}", accent_color=accent)


def _render_faculty_actions(current_user: dict, full_df: pd.DataFrame, class_df: pd.DataFrame, predictor):
    render_hero_header(
        "Support Plans & Student Letters",
        f"Manage follow-ups and write quick letters for {current_user['department']} • Semester {current_user['semester']}.",
        f"{len(class_df)} Class Students",
        "faculty",
    )

    t1, t2 = st.tabs(["📋 Student Support Log", "📜 Write a Letter / Notice"])
    with t1:
        render_intervention_tracker(full_df, current_user, scope_df=class_df, key_prefix="fac_int")

    with t2:
        lc1, lc2 = st.columns([1, 1.55], gap="large")
        with lc1:
            s_sel = st.selectbox(
                "Pick Student:",
                class_df["student_id"] + " - " + class_df["student_name"],
                key="fac_let_sel",
            )
            l_type = st.radio(
                "Choose Letter Type:",
                [
                    "Attendance & Study Warning Letter",
                    "Parent Meeting Invitation",
                    "Appreciation Letter (Great Performance)",
                ],
                key="fac_let_type",
            )
            l_key = "commendation" if "Appreciation" in l_type else ("warning" if "Warning" in l_type else "parent")
            issuer = st.text_input("Your Name:", current_user["name"], key="fac_let_name")
            role_txt = st.text_input("Your Role:", current_user["role_title"], key="fac_let_role")
        with lc2:
            s_row = class_df[class_df["student_id"] == s_sel.split(" - ")[0]].iloc[0]
            s_diag = predictor.predict_single(s_row.to_dict())
            doc_text = generate_academic_letter(l_key, s_row.to_dict(), s_diag, issuer, role_txt)
            with st.container(border=True, height=460):
                st.markdown(doc_text)
            st.download_button(
                "📥 Download Letter (.md)",
                data=doc_text.encode("utf-8"),
                file_name=f"faculty_notice_{s_row['student_id']}.md",
                mime="text/markdown",
                width="stretch",
                key="fac_let_dl",
            )
