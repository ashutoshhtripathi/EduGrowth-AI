"""
Leadership / Dean Interface for EduGrowth AI.
Simple, clear university-wide overview, student search, support plans, official letters, and Leadership AI.
"""

import pandas as pd
import plotly.express as px
import streamlit as st

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
    COLOR_PRIMARY,
    COLOR_SAFE,
    COLOR_WARNING,
    apply_clean_chart_theme,
    build_student_radar_chart,
    render_hero_header,
    render_html,
    render_kpi_card,
    render_person_card,
)

EXEC_VIEWS = [
    "🏛️ University Overview",
    "🔍 Find & Check Students",
    "📋 Support Plans & Letters",
    "🎯 GPA Goal Planner",
    "🤖 Leadership AI Assistant",
]


def render_executive_portal(current_user: dict, df: pd.DataFrame, predictor):
    active_view = render_sidebar_shell(current_user, EXEC_VIEWS, "exec_active_view")

    with st.sidebar:
        st.markdown("##### **Filter Students**")
        filter_dept = st.selectbox(
            "Branch / Department",
            ["All Departments"] + sorted(df["department"].unique().tolist()),
            key="exec_filter_dept",
        )
        filter_sem = st.selectbox(
            "Semester",
            ["All Semesters"] + sorted(df["semester"].unique().tolist()),
            key="exec_filter_sem",
        )
        st.divider()

    render_sidebar_footer(current_user)

    exec_df = df.copy()
    if filter_dept != "All Departments":
        exec_df = exec_df[exec_df["department"] == filter_dept]
    if filter_sem != "All Semesters":
        exec_df = exec_df[exec_df["semester"] == filter_sem]

    scope_label = f"{filter_dept} • {filter_sem if filter_sem == 'All Semesters' else f'Semester {filter_sem}'}"

    if active_view == EXEC_VIEWS[0]:
        _render_overview(current_user, exec_df, scope_label)
    elif active_view == EXEC_VIEWS[1]:
        _render_student_finder(df, exec_df, predictor)
    elif active_view == EXEC_VIEWS[2]:
        _render_support_and_letters(df, exec_df, current_user, predictor)
    elif active_view == EXEC_VIEWS[3]:
        render_hero_header(
            "University GPA Goal Planner",
            "Pick any student to see what changes are needed to reach a higher GPA.",
            f"Viewing: {len(exec_df):,} Students",
            "executive",
        )
        s_cand = st.selectbox(
            "Pick a Student:",
            exec_df["student_id"] + " - " + exec_df["student_name"] + " (" + exec_df["department"] + ")",
            key="exec_sim_student",
        )
        target_sid = s_cand.split(" - ")[0]
        active_student = df[df["student_id"] == target_sid].iloc[0]
        render_goal_simulator(active_student, predictor, key_prefix="exec_sim", accent_color=COLOR_PRIMARY)
    else:
        render_chatbot_interface(current_user, df)


def _render_overview(current_user: dict, exec_df: pd.DataFrame, scope_label: str):
    render_hero_header(
        "University Leadership Overview",
        f"Welcome, {current_user['name']} • Showing: {scope_label}",
        f"{len(exec_df):,} Total Students",
        "executive",
        extra_pill=f"Open Support Plans: {len(st.session_state.get('interventions', []))}",
    )

    total = len(exec_df)
    critical_cnt = int((exec_df["academic_risk_level"] == 2).sum())
    moderate_cnt = int((exec_df["academic_risk_level"] == 1).sum())
    safe_cnt = int((exec_df["academic_risk_level"] == 0).sum())
    avg_gpa = exec_df["target_end_term_gpa"].mean() if total else 0.0
    avg_att = exec_df["attendance_rate_pct"].mean() if total else 0.0
    on_track_rate = ((safe_cnt + moderate_cnt) / total * 100) if total else 0.0

    k1, k2, k3, k4, k5 = st.columns(5)
    with k1:
        render_kpi_card("Total Students", f"{total:,}", "Currently enrolled", accent_color=COLOR_PRIMARY, icon="👥")
    with k2:
        pct_c = (critical_cnt / total * 100) if total else 0.0
        render_kpi_card("Needs Urgent Help", f"{critical_cnt:,}", f"{pct_c:.1f}% falling behind", accent_color=COLOR_CRITICAL, icon="🚨", progress_pct=pct_c)
    with k3:
        pct_m = (moderate_cnt / total * 100) if total else 0.0
        render_kpi_card("Needs Attention", f"{moderate_cnt:,}", f"{pct_m:.1f}% borderline", accent_color=COLOR_WARNING, icon="⚠️", progress_pct=pct_m)
    with k4:
        render_kpi_card("Likely to Pass", f"{on_track_rate:.1f}%", f"Avg attendance {avg_att:.1f}%", accent_color=COLOR_SAFE, icon="✅", progress_pct=on_track_rate)
    with k5:
        render_kpi_card("Expected Avg GPA", f"{avg_gpa:.2f}", "Out of 10.0 overall", accent_color=COLOR_PRIMARY, icon="🎓", progress_pct=avg_gpa * 10)

    st.write("")
    c1, c2 = st.columns([1.05, 1])
    with c1:
        st.markdown("##### **How Each Department Is Doing**")
        st.caption("Number of students who are doing well, need attention, or need urgent help.")
        dept_risk = exec_df.groupby(["department", "academic_risk_level"]).size().reset_index(name="count")
        dept_risk["Status"] = dept_risk["academic_risk_level"].map({0: "Doing Well", 1: "Needs Attention", 2: "Needs Urgent Help"})
        fig1 = px.bar(
            dept_risk,
            x="department",
            y="count",
            color="Status",
            color_discrete_map={"Doing Well": "#10B981", "Needs Attention": "#F59E0B", "Needs Urgent Help": "#EF4444"},
            barmode="stack",
            height=315,
        )
        fig1 = apply_clean_chart_theme(fig1, height=315)
        fig1.update_layout(xaxis_title=None, yaxis_title="Students", legend=dict(orientation="h", y=1.12))
        st.plotly_chart(fig1, width="stretch")

    with c2:
        st.markdown("##### **Where Urgent Cases Are Highest (Branch × Semester)**")
        st.caption("Darker red means a higher share of students in that semester need urgent help.")
        heat_df = (
            exec_df.assign(is_critical=(exec_df["academic_risk_level"] == 2).astype(int) * 100)
            .pivot_table(index="department", columns="semester", values="is_critical", aggfunc="mean")
            .round(1)
        )
        fig_heat = px.imshow(
            heat_df,
            text_auto=".1f",
            color_continuous_scale=["#EFF6FF", "#FDE68A", "#EF4444"],
            labels=dict(x="Semester", y="Department", color="Urgent %"),
            height=315,
        )
        fig_heat = apply_clean_chart_theme(fig_heat, height=315)
        st.plotly_chart(fig_heat, width="stretch")

    c3, c4 = st.columns([1, 1])
    with c3:
        st.markdown("##### **How Attendance Affects Exam Marks**")
        st.caption("Students below the dotted 75% line are much more likely to struggle in exams.")
        sample_scat = exec_df.sample(min(600, len(exec_df)), random_state=42).copy()
        sample_scat["Status"] = sample_scat["academic_risk_level"].map({0: "Doing Well", 1: "Needs Attention", 2: "Needs Urgent Help"})
        fig2 = px.scatter(
            sample_scat,
            x="attendance_rate_pct",
            y="internal_assessment_score",
            color="Status",
            hover_data=["student_id", "student_name", "department"],
            color_discrete_map={"Doing Well": "#94A3B8", "Needs Attention": "#F59E0B", "Needs Urgent Help": "#EF4444"},
            labels={"attendance_rate_pct": "Class Attendance (%)", "internal_assessment_score": "Test Score (/100)"},
            height=300,
        )
        fig2.add_vline(x=75, line_width=1.5, line_dash="dot", line_color="#475569")
        fig2 = apply_clean_chart_theme(fig2, height=300)
        fig2.update_layout(legend=dict(orientation="h", y=1.12))
        st.plotly_chart(fig2, width="stretch")

    with c4:
        st.markdown("##### **Department Report Card**")
        st.caption("Quick comparison of attendance, expected GPA, and job readiness across branches.")
        dept_df = (
            exec_df.groupby("department")
            .agg(
                Students=("student_id", "count"),
                Attendance=("attendance_rate_pct", "mean"),
                GPA=("target_end_term_gpa", "mean"),
                Job_Ready=("employability_index", "mean"),
                Urgent_Pct=("academic_risk_level", lambda s: (s == 2).mean() * 100),
            )
            .reset_index()
            .sort_values("GPA", ascending=False)
        )
        st.dataframe(
            dept_df,
            hide_index=True,
            width="stretch",
            height=300,
            column_config={
                "department": "Department",
                "Attendance": st.column_config.ProgressColumn("Attendance", min_value=0, max_value=100, format="%.1f%%"),
                "GPA": st.column_config.NumberColumn("Expected GPA", format="%.2f"),
                "Job_Ready": st.column_config.ProgressColumn("Job Readiness", min_value=0, max_value=100, format="%.1f"),
                "Urgent_Pct": st.column_config.NumberColumn("Urgent %", format="%.1f%%"),
            },
        )


def _render_student_finder(full_df: pd.DataFrame, exec_df: pd.DataFrame, predictor):
    render_hero_header(
        "Find & Check Any Student",
        "Search by name or ID, filter by attendance or status, and open a complete easy-to-read student profile.",
        f"{len(exec_df):,} Students Found",
        "executive",
    )

    f1, f2, f3 = st.columns([1.4, 1.2, 1.2])
    with f1:
        search_kw = st.text_input("Search by Name or ID:", placeholder="Type a name like Patel or ID like EDG-2026-1042", key="exec_search")
    with f2:
        risk_sel = st.multiselect(
            "Student Status:",
            ["Needs Urgent Help", "Needs Attention", "Doing Well"],
            default=["Needs Urgent Help", "Needs Attention", "Doing Well"],
            key="exec_risk_ms",
        )
    with f3:
        max_att = st.slider("Show Attendance Up To (%):", 30, 100, 100, key="exec_max_att")

    risk_map = {"Doing Well": 0, "Needs Attention": 1, "Needs Urgent Help": 2}
    allowed_levels = [risk_map[r] for r in risk_sel]

    filtered = exec_df[
        exec_df["academic_risk_level"].isin(allowed_levels) & (exec_df["attendance_rate_pct"] <= max_att)
    ].copy()
    if search_kw:
        filtered = filtered[
            filtered["student_id"].str.contains(search_kw, case=False)
            | filtered["student_name"].str.contains(search_kw, case=False)
        ]

    filtered["Status"] = filtered["academic_risk_level"].map({0: "🟢 Doing Well", 1: "🟡 Needs Attention", 2: "🔴 Needs Urgent Help"})

    st.dataframe(
        filtered[
            [
                "student_id",
                "student_name",
                "department",
                "semester",
                "attendance_rate_pct",
                "internal_assessment_score",
                "backlog_count",
                "target_end_term_gpa",
                "Status",
            ]
        ].head(100),
        hide_index=True,
        width="stretch",
        height=280,
        column_config={
            "student_id": "ID",
            "student_name": "Name",
            "department": "Department",
            "semester": "Sem",
            "attendance_rate_pct": st.column_config.ProgressColumn("Attendance", min_value=0, max_value=100, format="%.1f%%"),
            "internal_assessment_score": st.column_config.NumberColumn("Test Score", format="%.1f"),
            "backlog_count": "Pending Subjects",
            "target_end_term_gpa": st.column_config.NumberColumn("Expected GPA", format="%.2f"),
        },
    )

    csv_bytes = filtered.to_csv(index=False).encode("utf-8")
    st.download_button(
        "📥 Download This List (.CSV)",
        data=csv_bytes,
        file_name="edugrowth_student_list.csv",
        mime="text/csv",
    )

    st.divider()
    st.markdown("##### **👤 Detailed Student Checkup**")
    pick_pool = filtered if len(filtered) > 0 else full_df
    sel_opt = st.selectbox(
        "Pick a student to inspect:",
        pick_pool["student_id"] + " - " + pick_pool["student_name"],
        key="exec_360_pick",
    )
    target_sid = sel_opt.split(" - ")[0]
    s_row = full_df[full_df["student_id"] == target_sid].iloc[0]
    diag = predictor.predict_single(s_row.to_dict())
    dept_avg = full_df[full_df["department"] == s_row["department"]].mean(numeric_only=True)

    badge_kind = "safe" if diag["risk_level"] == 0 else ("warning" if diag["risk_level"] == 1 else "critical")
    badge_txt = "Doing Well" if diag["risk_level"] == 0 else ("Needs Attention" if diag["risk_level"] == 1 else "Needs Urgent Help")
    render_person_card(
        s_row["student_name"],
        f"{s_row['department']} • Semester {s_row['semester']} • ID: {s_row['student_id']}",
        badge_txt,
        badge_kind=badge_kind,
        right_note=f"Prior CGPA: {s_row['prev_cgpa']:.2f}",
    )

    d_left, d_right = st.columns([1, 1.15], gap="large")
    with d_left:
        m1, m2 = st.columns(2)
        with m1:
            render_kpi_card("Expected GPA", f"{diag['predicted_end_term_gpa']:.2f}", diag["gpa_trajectory"], accent_color=COLOR_PRIMARY, icon="🎯")
            render_kpi_card("Test Score", f"{s_row['internal_assessment_score']:.1f}/100", f"Pending subjects: {int(s_row['backlog_count'])}", icon="📝")
        with m2:
            att_ok = s_row["attendance_rate_pct"] >= 75
            render_kpi_card("Attendance", f"{s_row['attendance_rate_pct']:.1f}%", "Meets 75% rule" if att_ok else "Below 75% rule", accent_color=COLOR_SAFE if att_ok else COLOR_CRITICAL, icon="📅")
            render_kpi_card("Risk Level", f"{diag['risk_probabilities']['High Risk']}%", "Chance of falling behind", accent_color=COLOR_WARNING, icon="⚠️")

        st.markdown("**Main Reasons & What Helps:**")
        for drv in diag["key_risk_drivers"]:
            render_html(f'<div class="callout-card">• {drv}</div>')

    with d_right:
        fig_rad = build_student_radar_chart(
            s_row,
            dept_avg,
            student_label=s_row["student_name"],
            benchmark_label=f"{s_row['department']} Avg",
            accent_color=COLOR_PRIMARY,
        )
        st.plotly_chart(fig_rad, width="stretch")


def _render_support_and_letters(full_df: pd.DataFrame, exec_df: pd.DataFrame, current_user: dict, predictor):
    render_hero_header(
        "Student Support Plans & Official Letters",
        "Assign follow-up help for struggling students and create ready-to-send university letters.",
        f"{len(st.session_state.get('interventions', []))} Support Plans",
        "executive",
    )

    tab_cases, tab_letters = st.tabs(["📋 Support Plans", "📜 Create Official Letter"])
    with tab_cases:
        render_intervention_tracker(full_df, current_user, key_prefix="exec_int")

    with tab_letters:
        lc1, lc2 = st.columns([1, 1.55], gap="large")
        with lc1:
            s_sel = st.selectbox(
                "Pick Student:",
                exec_df["student_id"] + " - " + exec_df["student_name"],
                key="exec_let_sel",
            )
            l_type = st.radio(
                "Choose Letter Type:",
                [
                    "Appreciation Letter (Great Performance)",
                    "Attendance & Study Warning Letter",
                    "Parent Meeting Invitation",
                ],
                key="exec_let_type",
            )
            l_key = "commendation" if "Appreciation" in l_type else ("warning" if "Warning" in l_type else "parent")
            s_name = st.text_input("Signed By:", current_user["name"], key="exec_sig_name")
            s_title = st.text_input("Title:", "Dean of Academic Affairs", key="exec_sig_title")
        with lc2:
            s_row = full_df[full_df["student_id"] == s_sel.split(" - ")[0]].iloc[0]
            s_diag = predictor.predict_single(s_row.to_dict())
            doc_text = generate_academic_letter(l_key, s_row.to_dict(), s_diag, s_name, s_title)
            with st.container(border=True, height=460):
                st.markdown(doc_text)
            st.download_button(
                "📥 Download Letter (.md)",
                data=doc_text.encode("utf-8"),
                file_name=f"official_letter_{s_row['student_id']}.md",
                mime="text/markdown",
                width="stretch",
                key="exec_let_dl",
            )
