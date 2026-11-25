"""
Reusable, Plain-English UI Widgets for EduGrowth AI Portals.
Features a refined architectural sidebar, native bordered panels, and zero raw HTML leaks.
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from goal_optimizer import optimize_gpa_target
from interventions_manager import create_intervention
from ui.theme import (
    COLOR_CRITICAL,
    COLOR_PRIMARY,
    COLOR_SAFE,
    COLOR_WARNING,
    apply_clean_chart_theme,
    get_role_theme,
    render_html,
    render_kpi_card,
)


def render_sidebar_shell(current_user: dict, nav_options: list[str], nav_state_key: str) -> str:
    """Renders a sleek, executive-grade sidebar with initials avatar and left-accented nav items."""
    role = current_user.get("role", "default")
    theme = get_role_theme(role)

    if nav_state_key not in st.session_state or st.session_state[nav_state_key] not in nav_options:
        st.session_state[nav_state_key] = nav_options[0]

    active_view = st.session_state[nav_state_key]
    clean_parts = [
        p for p in current_user["name"].split()
        if p.lower().rstrip(".") not in {"dr", "prof", "mr", "mrs", "ms", "&"}
    ]
    if len(clean_parts) >= 2:
        initials = (clean_parts[0][0] + clean_parts[1][0]).upper()
    elif len(clean_parts) == 1:
        initials = clean_parts[0][:2].upper()
    else:
        initials = "EG"

    with st.sidebar:
        render_html(
            f"""
            <div style="display:flex; align-items:center; justify-content:space-between; padding-bottom:0.85rem; margin-bottom:0.85rem; border-bottom:1px solid #F1F5F9;">
            <div style="display:flex; align-items:center; gap:9px;">
            <div style="width:32px; height:32px; border-radius:8px; background:{theme['gradient']}; color:#FFF; display:flex; align-items:center; justify-content:center; font-size:0.78rem; font-weight:800; letter-spacing:-0.02em;">EG</div>
            <span style="font-size:0.98rem; font-weight:800; color:#0F172A; letter-spacing:-0.02em;">EduGrowth</span>
            </div>
            <span style="background:{theme['soft_bg']}; color:{theme['soft_text']}; border:1px solid {theme['soft_border']}; border-radius:999px; padding:0.15rem 0.55rem; font-size:0.68rem; font-weight:700; text-transform:uppercase; letter-spacing:0.04em;">{theme['portal_name']}</span>
            </div>

            <div style="display:flex; align-items:center; gap:10px; padding:0.45rem 0.2rem 0.95rem 0.2rem; margin-bottom:0.35rem;">
            <div style="width:34px; height:34px; border-radius:50%; background:#0F172A; color:#FFFFFF; display:flex; align-items:center; justify-content:center; font-size:0.76rem; font-weight:700; flex-shrink:0;">{initials}</div>
            <div style="min-width:0;">
            <div style="font-size:0.86rem; font-weight:700; color:#0F172A; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">{current_user['name']}</div>
            <div style="font-size:0.73rem; color:#64748B; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">{current_user['role_title']}</div>
            </div>
            </div>

            <div style="font-size:0.68rem; font-weight:700; text-transform:uppercase; letter-spacing:0.08em; color:#94A3B8; margin:0 0 0.35rem 0.2rem;">Workspace</div>
            """
        )

        for idx, opt in enumerate(nav_options):
            is_active = opt == active_view
            if st.button(
                opt,
                type="primary" if is_active else "secondary",
                key=f"nav_{nav_state_key}_{idx}",
                width="stretch",
            ):
                st.session_state[nav_state_key] = opt
                st.rerun()

        st.divider()
        return active_view


def render_sidebar_footer(current_user: dict):
    """Renders quiet isolation status and clean sign-out button in the sidebar."""
    role = current_user.get("role", "guest")
    theme = get_role_theme(role)
    with st.sidebar:
        render_html(
            f"""
            <div style="font-size:0.74rem; color:#64748B; margin-bottom:0.55rem; padding:0 0.15rem;">
            🔒 Private {theme['portal_name']} chat active
            </div>
            """
        )
        if st.button("Sign Out / Switch Role", type="secondary", width="stretch", key=f"logout_{role}"):
            st.session_state["authenticated"] = False
            st.session_state["user"] = None
            st.rerun()


def render_goal_simulator(
    student_row: pd.Series,
    predictor,
    key_prefix: str,
    accent_color: str = COLOR_PRIMARY,
    parent_friendly: bool = False,
):
    """Plain-English Goal Planner & Interactive Study Scenario Simulator."""
    s_dict = student_row.to_dict()
    cur_diag = predictor.predict_single(s_dict)

    mode_labels = [
        "🎯 Reach a Goal GPA (What effort is needed?)",
        "🎛️ Test 'What-If' Changes (Adjust sliders)",
    ]

    sim_mode = st.radio(
        "Choose what you want to check:",
        mode_labels,
        horizontal=True,
        key=f"{key_prefix}_sim_mode",
    )
    st.write("")

    if sim_mode == mode_labels[0]:
        g_c1, g_c2 = st.columns([1, 1.5], gap="large")
        with g_c1:
            render_html(
                f"""
                <div class="surface-panel">
                <div class="panel-title">🎯 Pick Your Target GPA</div>
                <div style="font-size:0.88rem; color:#475569; margin-bottom:0.4rem;">
                Student: <strong>{student_row['student_name']}</strong>
                </div>
                <div style="font-size:0.88rem; color:#475569;">
                Current Expected GPA: <strong style="color:{accent_color}; font-size:1.05rem;">{cur_diag['predicted_end_term_gpa']:.2f} / 10</strong>
                </div>
                </div>
                """
            )
            default_target = float(min(9.6, max(5.5, round(cur_diag["predicted_end_term_gpa"] + 0.6, 1))))
            target_val = st.slider(
                "Slide to choose your target GPA:",
                5.0,
                9.8,
                default_target,
                0.1,
                key=f"{key_prefix}_target_gpa",
            )

        with g_c2:
            opt = optimize_gpa_target(s_dict, target_val, predictor)
            f_color = (
                COLOR_SAFE
                if opt["feasibility_score"] >= 80
                else (COLOR_WARNING if opt["feasibility_score"] >= 50 else COLOR_CRITICAL)
            )
            friendly_status = (
                "Very Easy to Reach"
                if opt["feasibility_score"] >= 80
                else ("Possible with Steady Effort" if opt["feasibility_score"] >= 50 else "Big Jump — Needs Long-Term Plan")
            )
            render_html(
                f"""
                <div class="surface-panel" style="border-left: 4px solid {f_color};">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.35rem; flex-wrap:wrap; gap:6px;">
                <span style="font-weight:700; font-size:1.05rem; color:#0F172A;">{friendly_status}</span>
                <span class="status-pill" style="border:1px solid {f_color}; color:{f_color};">{opt['feasibility_score']}% Chance</span>
                </div>
                <div style="font-size:0.88rem; color:#475569;">{opt['message']}</div>
                </div>
                """
            )

            o1, o2, o3 = st.columns(3)
            with o1:
                render_kpi_card(
                    "Needed Attendance",
                    f"{opt['required_attendance']:.0f}%",
                    f"+{opt['attendance_delta']:.1f}% more" if opt["attendance_delta"] > 0 else "Already on track",
                    accent_color=accent_color,
                    icon="📅",
                    progress_pct=opt["required_attendance"],
                )
            with o2:
                render_kpi_card(
                    "Needed Exam Score",
                    f"{opt['required_internal']:.0f}/100",
                    f"+{opt['internal_delta']:.1f} marks more" if opt["internal_delta"] > 0 else "Already on track",
                    accent_color=accent_color,
                    icon="📝",
                    progress_pct=opt["required_internal"],
                )
            with o3:
                render_kpi_card(
                    "Weekly Study Time",
                    f"{opt['required_study_hours']:.1f}h",
                    f"+{opt['study_delta']:.1f} hrs/week" if opt["study_delta"] > 0 else "Keep current pace",
                    accent_color=accent_color,
                    icon="⏱️",
                    progress_pct=min(100.0, opt["required_study_hours"] / 25.0 * 100.0),
                )

            comp_df = pd.DataFrame(
                {
                    "Area": ["Attendance (%)", "Exam Score (/100)", "Study Pace"],
                    "Right Now": [
                        float(student_row["attendance_rate_pct"]),
                        float(student_row["internal_assessment_score"]),
                        min(100.0, float(student_row["lms_weekly_hours"]) * 3.0),
                    ],
                    "To Reach Goal": [
                        float(opt["required_attendance"]),
                        float(opt["required_internal"]),
                        min(100.0, float(opt["required_study_hours"]) * 3.0),
                    ],
                }
            )
            fig_comp = px.bar(
                comp_df.melt(id_vars="Area", var_name="Status", value_name="Score"),
                x="Area",
                y="Score",
                color="Status",
                barmode="group",
                color_discrete_map={"Right Now": "#CBD5E1", "To Reach Goal": accent_color},
                height=220,
            )
            fig_comp = apply_clean_chart_theme(fig_comp, height=220)
            fig_comp.update_layout(xaxis_title=None, yaxis_title="Level", legend=dict(orientation="h", y=1.14))
            st.plotly_chart(fig_comp, width="stretch")

            st.markdown("**Simple Step-by-Step Plan:**")
            for step in opt["action_steps"]:
                render_html(f'<div class="callout-card">✅ {step}</div>')
    else:
        c_in, c_out = st.columns([1.05, 1.35], gap="large")
        with c_in:
            with st.container(border=True):
                st.markdown("**🎛️ Change Weekly Habits**")
                calc_att = st.slider("Class Attendance (%)", 30.0, 100.0, float(student_row["attendance_rate_pct"]), 1.0, key=f"{key_prefix}_att")
                calc_int = st.slider("Test / Internal Marks (/100)", 10.0, 100.0, float(student_row["internal_assessment_score"]), 1.0, key=f"{key_prefix}_int")
                calc_hrs = st.slider("Weekly Study Hours (hrs/week)", 1.0, 35.0, float(student_row["lms_weekly_hours"]), 0.5, key=f"{key_prefix}_hrs")
                calc_asn = st.slider("Homework Submitted On Time (%)", 20.0, 100.0, float(student_row["assignment_completion_pct"]), 1.0, key=f"{key_prefix}_asn")

        with c_out:
            calc_dict = s_dict.copy()
            calc_dict["attendance_rate_pct"] = calc_att
            calc_dict["internal_assessment_score"] = calc_int
            calc_dict["lms_weekly_hours"] = calc_hrs
            calc_dict["assignment_completion_pct"] = calc_asn
            calc_dict["lms_logins_per_week"] = int(calc_hrs * 1.6)

            calc_res = predictor.predict_single(calc_dict)
            fail_prob = float(calc_res["risk_probabilities"]["High Risk"])
            pass_prob = round(100.0 - fail_prob, 1)
            gpa_diff = round(calc_res["predicted_end_term_gpa"] - cur_diag["predicted_end_term_gpa"], 2)

            r1, r2, r3 = st.columns(3)
            with r1:
                render_kpi_card("Chance of Passing", f"{pass_prob}%", "Expected course clearance", accent_color=COLOR_SAFE, icon="✅")
            with r2:
                render_kpi_card("Risk of Falling Behind", f"{fail_prob}%", "Needs extra support", accent_color=COLOR_CRITICAL, icon="⚠️")
            with r3:
                delta_str = f"{gpa_diff:+.2f} vs right now" if gpa_diff != 0 else "Same as right now"
                render_kpi_card(
                    "New Expected GPA",
                    f"{calc_res['predicted_end_term_gpa']:.2f}",
                    delta_str,
                    accent_color=accent_color,
                    icon="🎯",
                )

            gauge = go.Figure(
                go.Indicator(
                    mode="gauge+number+delta",
                    value=calc_res["predicted_end_term_gpa"],
                    delta={"reference": cur_diag["predicted_end_term_gpa"], "valueformat": ".2f"},
                    title={"text": "Expected Final GPA (out of 10)", "font": {"size": 14, "color": "#334155"}},
                    gauge={
                        "axis": {"range": [0, 10]},
                        "bar": {"color": accent_color},
                        "steps": [
                            {"range": [0, 5.5], "color": "#FEE2E2"},
                            {"range": [5.5, 7.5], "color": "#FEF3C7"},
                            {"range": [7.5, 10], "color": "#DCFCE7"},
                        ],
                    },
                )
            )
            gauge.update_layout(height=255, margin=dict(l=20, r=20, t=45, b=10), paper_bgcolor="#FFFFFF")
            st.plotly_chart(gauge, width="stretch")


def render_intervention_tracker(
    df: pd.DataFrame,
    current_user: dict,
    scope_df: pd.DataFrame = None,
    key_prefix: str = "int",
):
    """Plain-English Student Support & Follow-Up Tracker."""
    pool_df = scope_df if scope_df is not None else df

    with st.expander("➕ **Add a New Student Support Plan**", expanded=False):
        ic1, ic2 = st.columns(2)
        with ic1:
            s_pick = st.selectbox(
                "Pick a Student:",
                pool_df["student_id"] + " - " + pool_df["student_name"],
                key=f"{key_prefix}_pick",
            )
            i_act = st.selectbox(
                "Type of Support:",
                ["Extra Tutoring", "1-on-1 Teacher Meeting", "Attendance Reminder", "Parent Call / Meeting", "Exam Backlog Help"],
                key=f"{key_prefix}_type",
            )
            i_prio = st.selectbox("How Urgent:", ["Urgent", "High", "Medium", "Low"], key=f"{key_prefix}_prio")
        with ic2:
            assignee = st.text_input("Person Responsible:", value=current_user["name"], key=f"{key_prefix}_assignee")
            i_note = st.text_area("Notes / Next Steps:", placeholder="Write simple notes on how to help this student...", key=f"{key_prefix}_note")

        if st.button("Save Support Plan", key=f"{key_prefix}_save"):
            sid, sname = s_pick.split(" - ", 1)
            s_r = df[df["student_id"] == sid].iloc[0]
            new_item = create_intervention(
                student_id=sid,
                student_name=sname,
                department=s_r["department"],
                risk_tier="Critical Risk" if s_r["academic_risk_level"] == 2 else "Moderate Risk",
                intervention_type=i_act,
                priority=i_prio,
                assigned_to=assignee,
                notes=i_note or "Added from Student Support Plan.",
            )
            st.session_state["interventions"].insert(0, new_item)
            st.success(f"Support plan saved for {sname}.")
            st.rerun()

    fc1, fc2 = st.columns(2)
    with fc1:
        status_filter = st.multiselect(
            "Show Status:",
            ["Pending", "In Progress", "Resolved"],
            default=["Pending", "In Progress", "Resolved"],
            key=f"{key_prefix}_st_filter",
        )
    with fc2:
        prio_filter = st.multiselect(
            "Show Urgency:",
            ["Urgent", "High", "Medium", "Low"],
            default=["Urgent", "High", "Medium", "Low"],
            key=f"{key_prefix}_pr_filter",
        )

    valid_ids = set(pool_df["student_id"].tolist())
    items = [
        item
        for item in st.session_state["interventions"]
        if item["status"] in status_filter
        and item["priority"] in prio_filter
        and (scope_df is None or item["student_id"] in valid_ids)
    ]

    if not items:
        st.info("No support plans match your selected filters.")
        return

    for idx, item in enumerate(items):
        p_c = COLOR_CRITICAL if item["priority"] == "Urgent" else (COLOR_WARNING if item["priority"] == "High" else COLOR_PRIMARY)
        col_card, col_status = st.columns([4, 1.2])
        with col_card:
            render_html(
                f"""
                <div class="surface-panel" style="margin-bottom:0.55rem; padding:0.95rem 1.15rem; border-left: 4px solid {p_c};">
                <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:6px;">
                <span><strong>{item['student_name']}</strong> <span style="color:#64748B; font-size:0.84rem;">({item['student_id']} • {item['department']})</span></span>
                <span class="status-pill" style="border:1px solid {p_c}; color:{p_c};">{item['priority']} • {item['status']}</span>
                </div>
                <div style="font-size:0.85rem; color:#334155; margin-top:0.3rem;">
                <strong>{item['intervention_type']}</strong> • Handled by <em>{item['assigned_to']}</em> ({item['created_date']})
                </div>
                <div style="font-size:0.81rem; color:#64748B; margin-top:0.2rem;">{item['notes']}</div>
                </div>
                """
            )
        with col_status:
            statuses = ["Pending", "In Progress", "Resolved"]
            new_status = st.selectbox(
                "Update Status",
                statuses,
                index=statuses.index(item["status"]) if item["status"] in statuses else 0,
                key=f"{key_prefix}_upd_{item['id']}_{idx}",
                label_visibility="collapsed",
            )
            if new_status != item["status"]:
                item["status"] = new_status
                st.rerun()
