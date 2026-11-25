"""
iPhone / iOS-Inspired Liquid Glass Login Screen for EduGrowth AI with Custom Brand Logo.
"""

import pandas as pd
import streamlit as st

from ui.theme import get_logo_svg, render_html


def render_login_portal(accounts_db: dict, df: pd.DataFrame, get_student_identity):
    _, center_col, _ = st.columns([1.05, 1.15, 1.05])

    with center_col:
        brand_block = f"""
        <div style="text-align:center; margin-top:1.1rem; margin-bottom:1.15rem;">
        <div style="display:inline-flex; align-items:center; justify-content:center; width:56px; height:56px; border-radius:16px; background:rgba(255,255,255,0.08); backdrop-filter:blur(18px); -webkit-backdrop-filter:blur(18px); border:1px solid rgba(255,255,255,0.18); box-shadow:0 14px 30px -10px rgba(0,0,0,0.6), inset 0 1px 0 rgba(255,255,255,0.22); margin-bottom:0.75rem;">
        {get_logo_svg(size=34)}
        </div>
        <h1 style="margin:0; font-size:1.62rem; font-weight:700; color:#F8FAFC; letter-spacing:-0.025em;">
        EduGrowth <span style="color:#F5C451; font-weight:800;">AI</span>
        </h1>
        <p style="margin:0.25rem 0 0 0; color:rgba(203,213,225,0.78); font-size:0.86rem;">Campus Intelligence Workspace</p>
        </div>
        """
        render_html(brand_block)

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
                <div style="display:flex; align-items:center; gap:10px; margin:0.65rem 0 0.6rem 0;">
                <div style="flex:1; height:1px; background:rgba(255,255,255,0.18);"></div>
                <span style="font-size:0.71rem; font-weight:700; color:rgba(226,232,240,0.8); text-transform:uppercase; letter-spacing:0.08em;">Quick Demo</span>
                <div style="flex:1; height:1px; background:rgba(255,255,255,0.18);"></div>
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
            <p style="text-align:center; margin-top:0.8rem; font-size:0.73rem; color:rgba(148,163,184,0.78);">
            ID login: e.g. EDG-2026-1001 • password <strong style="color:rgba(226,232,240,0.9);">study</strong> or <strong style="color:rgba(226,232,240,0.9);">family</strong>
            </p>
            """
        )

        chat_histories = st.session_state.get("chat_histories", {})
        active_chats = [
            f"{k.split(':')[0].title()} ({sum(1 for m in v if m['role']=='user')})"
            for k, v in chat_histories.items()
            if sum(1 for m in v if m["role"] == "user") > 0
        ]
        if active_chats:
            render_html(
                f'<p style="text-align:center; font-size:0.74rem; color:rgba(255,255,255,0.7);">💬 Saved private chats: {", ".join(active_chats)}</p>'
            )
