"""
Role-Isolated AI Assistant Component for EduGrowth AI.
Maintains strictly separate chat histories per interface with friendly, plain-English prompts.
"""

from datetime import datetime
import pandas as pd
import streamlit as st
from chatbot import EduGrowthChatbot
from ui.theme import get_role_theme, render_hero_header


def get_interface_chat_key(current_user: dict) -> str:
    """Returns a unique, interface-isolated session key for chat history."""
    role = current_user.get("role", "guest")
    if role in ("student", "parent"):
        sid = current_user.get("student_id", "default")
        return f"{role}:{sid}"
    return role


def _build_welcome_message(current_user: dict, dataset_name: str, row_count: int) -> str:
    role = current_user.get("role", "guest")
    name = current_user.get("name", "User")

    if role == "executive":
        return (
            f"👋 **Hello, {name}!** I am your **Leadership AI Assistant**.\n\n"
            f"This chat is private to the **Leadership View** and can answer questions across **{row_count:,} student records** in plain English.\n\n"
            "Try asking things like:\n"
            "- *Which department has the most students needing urgent help?*\n"
            "- *What is the average attendance and GPA across all departments?*\n"
            "- *Show me the top 5 students who need immediate support.*"
        )
    elif role == "faculty":
        dept = current_user.get("department", "Computer Science")
        sem = current_user.get("semester", 5)
        return (
            f"👋 **Hello, {name}!** I am your **Teacher AI Assistant**.\n\n"
            f"Your chat history here stays completely separate in your **Teacher Workspace** ({dept}, Semester {sem}).\n\n"
            "You can ask me:\n"
            "- *Who in my class has attendance below 75%?*\n"
            "- *What is our class average test score?*\n"
            "- *Which students in my section have pending subjects to clear?*"
        )
    elif role == "student":
        sid = current_user.get("student_id", "EDG-2026-1042")
        return (
            f"👋 **Hey {name}!** I am your **Personal AI Study & Career Helper**.\n\n"
            f"This chat is just for you (`{sid}`). Ask me anything in everyday language—no technical terms needed!\n\n"
            "For example:\n"
            "- *How am I doing overall this semester?*\n"
            "- *What are the 3 easiest ways I can raise my GPA?*\n"
            "- *How do my skills and projects compare with other students in my branch?*"
        )
    else:
        sid = current_user.get("student_id", "EDG-2026-1042")
        return (
            f"👋 **Welcome, {name}!** I am your **Parent Support Assistant**.\n\n"
            f"This chat is private to the **Parent Portal** for your child (`{sid}`). Ask anything in simple language.\n\n"
            "You can ask:\n"
            "- *How is my child doing in class and exams right now?*\n"
            "- *Is my child meeting the 75% attendance rule?*\n"
            "- *What good things has my child achieved this semester?*"
        )


def _get_quick_prompts(current_user: dict) -> list[str]:
    role = current_user.get("role", "guest")
    if role == "executive":
        return [
            "Which department has the highest percentage of students needing urgent help?",
            "Show average attendance, test scores, and expected GPA for each department.",
            "How many students have more than 2 pending subjects and under 75% attendance?",
            "List the top 5 students who need immediate support right now.",
        ]
    elif role == "faculty":
        dept = current_user.get("department", "Computer Science")
        sem = current_user.get("semester", 5)
        return [
            f"Which students in {dept} Sem {sem} have attendance below 75%?",
            f"What is the average internal test score in {dept} Sem {sem}?",
            f"Who are the top 5 students in {dept} Sem {sem}?",
            f"Which students in {dept} Sem {sem} still have pending subjects?",
        ]
    elif role == "student":
        sid = current_user.get("student_id", "EDG-2026-1042")
        return [
            f"Give me a simple summary of how {sid} is doing right now.",
            f"How does {sid}'s attendance and GPA compare to the class average?",
            f"What 3 simple steps will help {sid} improve their GPA fastest?",
            f"How strong is {sid}'s job readiness compared to peers?",
        ]
    else:
        sid = current_user.get("student_id", "EDG-2026-1042")
        return [
            f"Give a simple, clear progress update for {sid}.",
            f"Is {sid} meeting the 75% attendance rule and passing marks?",
            f"What are {sid}'s biggest strengths and projects this semester?",
            f"What topics should we talk about with {sid}'s class teacher?",
        ]


def _build_role_context(current_user: dict, scope_label: str) -> str:
    role = current_user.get("role", "guest")
    name = current_user.get("name", "User")
    title = current_user.get("role_title", "User")

    plain_rule = (
        "Always write in simple, clear, everyday English that any non-technical person can understand easily. "
        "Avoid heavy academic/ML jargon (say 'needs urgent help' instead of 'critical risk stratification', "
        "'pending subjects' instead of 'course arrears', 'expected GPA' instead of 'regression forecast')."
    )

    if role == "executive":
        return f"User: {name} ({title}). Workspace: Leadership View. Data scope: {scope_label}. {plain_rule}"
    elif role == "faculty":
        dept = current_user.get("department", "Computer Science")
        sem = current_user.get("semester", 5)
        return f"User: {name} ({title}, {dept}, Sem {sem}). Workspace: Teacher Workspace. Data scope: {scope_label}. {plain_rule}"
    elif role == "student":
        sid = current_user.get("student_id", "")
        return f"User: {name} (ID: {sid}). Workspace: Student Hub. Data scope: {scope_label}. Be warm, motivating, and practical. {plain_rule}"
    else:
        sid = current_user.get("student_id", "")
        return f"User: {name} (Parent of {sid}). Workspace: Parent Portal. Data scope: {scope_label}. Be warm, reassuring, honest, and easy to understand. {plain_rule}"


def _export_chat_markdown(messages: list, title: str) -> str:
    lines = [f"# {title}", f"Saved on: {datetime.now().strftime('%Y-%m-%d %H:%M')}", ""]
    for m in messages:
        speaker = "You" if m["role"] == "user" else "EduGrowth AI"
        ts = f" ({m['timestamp']})" if m.get("timestamp") else ""
        lines.append(f"### {speaker}{ts}")
        lines.append(m["content"])
        lines.append("")
    return "\n".join(lines)


def render_chatbot_interface(current_user: dict, base_df: pd.DataFrame):
    """Renders an interface-isolated AI Assistant with independent chat history."""
    role = current_user.get("role", "guest")
    theme = get_role_theme(role)
    chat_key = get_interface_chat_key(current_user)

    if "chat_histories" not in st.session_state:
        st.session_state["chat_histories"] = {}
    if "chat_datasets" not in st.session_state:
        st.session_state["chat_datasets"] = {}
    if "selected_model" not in st.session_state:
        st.session_state["selected_model"] = "openai/gpt-oss-120b"

    ds_state = st.session_state["chat_datasets"].setdefault(
        chat_key,
        {
            "source": "default",
            "custom_df": None,
            "custom_name": None,
            "faculty_scope": "My Class Section" if role == "faculty" else "All Students",
        },
    )

    if ds_state["source"] == "custom" and ds_state["custom_df"] is not None:
        active_df = ds_state["custom_df"]
        active_name = ds_state["custom_name"]
    elif role == "faculty" and ds_state.get("faculty_scope") == "My Class Section":
        f_dept = current_user.get("department")
        f_sem = current_user.get("semester")
        active_df = base_df[(base_df["department"] == f_dept) & (base_df["semester"] == f_sem)].copy()
        active_name = f"{f_dept} (Semester {f_sem})"
    else:
        active_df = base_df
        active_name = "All Student Records"

    if chat_key not in st.session_state["chat_histories"]:
        st.session_state["chat_histories"][chat_key] = [
            {
                "role": "assistant",
                "content": _build_welcome_message(current_user, active_name, len(active_df)),
                "queries": [],
                "timestamp": datetime.now().strftime("%H:%M"),
            }
        ]

    history = st.session_state["chat_histories"][chat_key]
    user_turns = sum(1 for m in history if m["role"] == "user")

    render_hero_header(
        f"{theme['icon']} {theme['portal_name']} AI Assistant",
        f"Looking at: {active_name} ({len(active_df):,} students) • Ask anything in simple language",
        badge_text=f"🔒 Private {role.title()} Chat ({user_turns} question{'s' if user_turns != 1 else ''})",
        role=role,
    )

    ctrl_col1, ctrl_col2, ctrl_col3 = st.columns([2.6, 1.1, 1.0])
    with ctrl_col1:
        if role in ("executive", "faculty"):
            with st.expander("📁 **Change Data or Upload Your Own File (CSV / Excel)**", expanded=False):
                if role == "faculty":
                    scope_choice = st.radio(
                        "Which students should the AI look at?",
                        ["My Class Section", "All Students in University", "Upload My Own File"],
                        index=(
                            2
                            if ds_state["source"] == "custom"
                            else (0 if ds_state.get("faculty_scope") == "My Class Section" else 1)
                        ),
                        horizontal=True,
                        key=f"scope_radio_{chat_key}",
                    )
                    if scope_choice == "Upload My Own File":
                        ds_state["source"] = "custom"
                    else:
                        if ds_state["source"] == "custom" or ds_state.get("faculty_scope") != scope_choice:
                            ds_state["source"] = "default"
                            ds_state["faculty_scope"] = scope_choice
                            st.rerun()
                else:
                    src_mode = st.radio(
                        "Choose data:",
                        ["All University Students (3,000)", "Upload My Own CSV / Excel File"],
                        index=0 if ds_state["source"] == "default" else 1,
                        horizontal=True,
                        key=f"exec_src_{chat_key}",
                    )
                    if src_mode.startswith("All") and ds_state["source"] == "custom":
                        ds_state["source"] = "default"
                        ds_state["custom_df"] = None
                        ds_state["custom_name"] = None
                        st.rerun()
                    elif src_mode.startswith("Upload") and ds_state["source"] != "custom":
                        ds_state["source"] = "custom"

                if ds_state["source"] == "custom":
                    up_file = st.file_uploader(
                        "Drop a CSV or Excel file here",
                        type=["csv", "xlsx", "xls"],
                        key=f"uploader_{chat_key}",
                        label_visibility="collapsed",
                    )
                    if up_file is not None and ds_state.get("custom_name") != up_file.name:
                        try:
                            loaded = pd.read_csv(up_file) if up_file.name.endswith(".csv") else pd.read_excel(up_file)
                            ds_state["custom_df"] = loaded
                            ds_state["custom_name"] = up_file.name
                            st.success(f"Loaded {up_file.name} ({len(loaded):,} rows).")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Could not read file: {e}")
        else:
            st.caption(
                f"🔐 Your chat stays private inside the **{theme['portal_name']}** and never mixes with other accounts."
            )

    with ctrl_col2:
        transcript_md = _export_chat_markdown(history, f"EduGrowth AI - {theme['portal_name']} Chat")
        st.download_button(
            "📥 Save Chat",
            data=transcript_md.encode("utf-8"),
            file_name=f"edugrowth_chat_{role}.md",
            mime="text/markdown",
            width="stretch",
            key=f"export_chat_{chat_key}",
        )

    with ctrl_col3:
        if st.button("🗑️ New Chat", type="secondary", width="stretch", key=f"clear_chat_{chat_key}"):
            st.session_state["chat_histories"][chat_key] = [
                {
                    "role": "assistant",
                    "content": f"✨ Started a fresh **{theme['portal_name']}** conversation! What would you like to check about **{active_name}**?",
                    "queries": [],
                    "timestamp": datetime.now().strftime("%H:%M"),
                }
            ]
            st.rerun()

    st.markdown("**Tap a quick question to try:**")
    sample_questions = _get_quick_prompts(current_user)
    q_cols = st.columns(2)
    selected_quick_prompt = None
    for idx, q_text in enumerate(sample_questions):
        with q_cols[idx % 2]:
            if st.button(f"💬 {q_text}", type="secondary", key=f"quick_q_{chat_key}_{idx}", width="stretch"):
                selected_quick_prompt = q_text

    st.write("")

    for msg in history:
        if msg["role"] == "user":
            with st.chat_message("user", avatar="👤"):
                st.markdown(msg["content"])
                if msg.get("timestamp"):
                    st.caption(f"Sent at {msg['timestamp']}")
        else:
            with st.chat_message("assistant", avatar=theme["avatar"]):
                st.markdown(msg["content"])
                if msg.get("queries"):
                    with st.expander(f"🔎 See how this answer was calculated ({len(msg['queries'])} check{'s' if len(msg['queries']) != 1 else ''})", expanded=False):
                        for q_idx, q in enumerate(msg["queries"], 1):
                            st.caption(f"**Data check #{q_idx}:**")
                            st.code(q["code"], language="python")
                            st.caption("**Result:**")
                            st.code(q["output"], language="text")
                if msg.get("timestamp"):
                    st.caption(f"{theme['portal_name']} AI • {msg['timestamp']}")

    user_input = st.chat_input(f"Type a question about {active_name}...", key=f"chat_input_{chat_key}")
    prompt_to_send = selected_quick_prompt or user_input

    if prompt_to_send:
        now_ts = datetime.now().strftime("%H:%M")
        history.append({"role": "user", "content": prompt_to_send, "timestamp": now_ts})
        with st.chat_message("user", avatar="👤"):
            st.markdown(prompt_to_send)

        chatbot = EduGrowthChatbot(
            active_df,
            dataset_name=active_name,
            model=st.session_state["selected_model"],
        )

        with st.chat_message("assistant", avatar=theme["avatar"]):
            with st.spinner("Checking the student records and preparing a clear answer..."):
                role_ctx = _build_role_context(current_user, active_name)
                res_dict = chatbot.chat(history, role_context=role_ctx)
                content = res_dict.get("content", "Sorry, I couldn't generate an answer right now.")
                queries = res_dict.get("executed_queries", [])
                st.markdown(content)
                if queries:
                    with st.expander(f"🔎 See how this answer was calculated ({len(queries)})", expanded=False):
                        for q in queries:
                            st.code(q["code"], language="python")
                            st.code(q["output"], language="text")

        history.append(
            {
                "role": "assistant",
                "content": content,
                "queries": queries,
                "timestamp": datetime.now().strftime("%H:%M"),
            }
        )
        st.rerun()
