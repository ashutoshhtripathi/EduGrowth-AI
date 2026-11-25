"""
Minimal, Centered SaaS Login Screen for EduGrowth AI.
Uses native bordered containers so there are zero stray empty boxes or messy cards.
"""

import pandas as pd
import streamlit as st

from ui.theme import render_html


def render_login_portal(accounts_db: dict, df: pd.DataFrame, get_student_identity):
    _, center_col, _ = st.columns([1.05, 1.15, 1.05])

    with center_col:
        render_html(
            """
            <div style="text-align:center; margin-top:1.4rem; margin-bottom:1.15rem;">
            <div style="width:46px; height:46px; border-radius:12px; background:linear-gradient(135deg,#0F172A 0%,#1E3A8A 60%,#2563EB 100%); color:#FFF; display:inline-flex; align-items:center; justify-content:center; font-size:1.25rem; font-weight:800; box-shadow:0 8px 20px -6px rgba(30,58,138,0.45); margin-bottom:0.65rem;">EG</div>
            <h1 style="margin:0; font-size:1.65rem; font-weight:800; color:#0F172A; letter-spacing:-0.025em;">EduGrowth AI</h1>
            <p style="margin:0.25rem 0 0 0; color:#64748B; font-size:0.9rem;">Sign in to open your campus workspace</p>
            </div>
            """
        )

        with st.container(border=True):
            with st.form("login_form", border=False):
                user_id_input = st.text_input(
                    "Username or Student ID",
                    placeholder="e.g. dean.vance, prof.sharma, or EDG-2026-1042",
                )
                password_input = st.text_input(
                    "Password",
                    type="password",
                    placeholder="Enter password",
                )
                submit_login = st.form_submit_button("Sign In →", width="stretch")

                if submit_login:
                    user_key = user_id_input.strip().lower()
                    upper_key = user_id_input.strip().upper()

                    if user_key in accounts_db and accounts_db[user_key]["password"] == password_input:
                        st.session_state["authenticated"] = True
                        st.session_state["user"] = accounts_db[user_key]
                        st.rerun()
                    elif upper_key in df["student_id"].values and password_input == "study":
                        s_name, _ = get_student_identity(upper_key)
                        st.session_state["authenticated"] = True
                        st.session_state["user"] = {
                            "name": s_name,
                            "role": "student",
                            "role_title": "Student",
                            "student_id": upper_key,
                        }
                        st.rerun()
                    elif upper_key in df["student_id"].values and password_input == "family":
                        _, parent_name = get_student_identity(upper_key)
                        st.session_state["authenticated"] = True
                        st.session_state["user"] = {
                            "name": parent_name,
                            "role": "parent",
                            "role_title": "Parent / Guardian",
                            "student_id": upper_key,
                        }
                        st.rerun()
                    else:
                        st.error("Incorrect username or password.")

            render_html(
                """
                <div style="display:flex; align-items:center; gap:10px; margin:0.6rem 0 0.55rem 0;">
                <div style="flex:1; height:1px; background:#E2E8F0;"></div>
                <span style="font-size:0.72rem; font-weight:600; color:#94A3B8; text-transform:uppercase; letter-spacing:0.06em;">Quick Demo</span>
                <div style="flex:1; height:1px; background:#E2E8F0;"></div>
                </div>
                """
            )

            d1, d2, d3, d4 = st.columns(4)
            with d1:
                if st.button("Dean", type="secondary", key="demo_btn_executive", width="stretch"):
                    st.session_state["authenticated"] = True
                    st.session_state["user"] = accounts_db["dean.vance"]
                    st.rerun()
            with d2:
                if st.button("Teacher", type="secondary", key="demo_btn_faculty", width="stretch"):
                    st.session_state["authenticated"] = True
                    st.session_state["user"] = accounts_db["prof.sharma"]
                    st.rerun()
            with d3:
                if st.button("Student", type="secondary", key="demo_btn_student", width="stretch"):
                    st.session_state["authenticated"] = True
                    st.session_state["user"] = accounts_db["student.edg1042"]
                    st.rerun()
            with d4:
                if st.button("Parent", type="secondary", key="demo_btn_parent", width="stretch"):
                    st.session_state["authenticated"] = True
                    st.session_state["user"] = accounts_db["parent.edg1042"]
                    st.rerun()

        render_html(
            """
            <p style="text-align:center; margin-top:0.75rem; font-size:0.77rem; color:#94A3B8;">
            Student/Parent ID login: use any ID like EDG-2026-1001 with password <strong>study</strong> or <strong>family</strong>
            </p>
            """
        )

        chat_histories = st.session_state.get("chat_histories", {})
        if chat_histories:
            saved_roles = ", ".join(
                f"{k.split(':')[0].title()} ({sum(1 for m in v if m['role']=='user')})"
                for k, v in chat_histories.items()
            )
            st.caption(f"Saved private chats: {saved_roles}")
