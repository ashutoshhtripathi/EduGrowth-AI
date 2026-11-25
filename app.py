"""
EduGrowth AI - Intelligent Student Success & Retention Monitoring System
Modular Role-Separated Institutional Portal:
- Executive / Dean: src/ui/executive_portal.py
- Faculty / Teacher: src/ui/faculty_portal.py
- Student: src/ui/student_portal.py
- Parent: src/ui/parent_portal.py
- Role-Isolated AI Data Assistant: src/ui/chatbot_panel.py
"""

import hashlib
import os
import sys
import pandas as pd
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "src"))

from inference import EduGrowthPredictor
from interventions_manager import get_initial_interventions
from ui.executive_portal import render_executive_portal
from ui.faculty_portal import render_faculty_portal
from ui.login_portal import render_login_portal
from ui.parent_portal import render_parent_portal
from ui.student_portal import render_student_portal
from ui.theme import inject_global_css

st.set_page_config(
    page_title="EduGrowth AI | Institutional Access Portal",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

FIRST_NAMES = [
    "Aarav", "Ananya", "Rohan", "Priya", "Aditya", "Sneha", "Vikram", "Neha",
    "Kavya", "Rahul", "Ishaan", "Tanvi", "Arjun", "Meera", "Varun", "Rhea",
    "Siddharth", "Pooja", "Dhruv", "Anushka", "Karan", "Divya", "Nikhil", "Simran",
]
LAST_NAMES = [
    "Sharma", "Verma", "Patel", "Nair", "Gupta", "Rao", "Iyer", "Reddy",
    "Chatterjee", "Mehta", "Joshi", "Singh", "Deshmukh", "Chopra", "Bose",
]


def get_student_identity(student_id_str: str):
    num_part = int(hashlib.md5(student_id_str.encode()).hexdigest(), 16)
    first_name = FIRST_NAMES[num_part % len(FIRST_NAMES)]
    last_name = LAST_NAMES[(num_part // 10) % len(LAST_NAMES)]
    return f"{first_name} {last_name}", f"Mr. & Mrs. {last_name}"


@st.cache_resource
def load_system():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(base_dir, "data", "processed", "processed_cohort.csv")
    df = pd.read_csv(data_path)
    df["student_name"] = [get_student_identity(sid)[0] for sid in df["student_id"]]
    predictor = EduGrowthPredictor()
    return df, predictor


df, predictor = load_system()

_DEMO_STU_NAME, _DEMO_PAR_NAME = get_student_identity("EDG-2026-1042")

ACCOUNTS_DB = {
    "dean.vance": {
        "password": "admin",
        "name": "Dr. Eleanor Vance",
        "role": "executive",
        "role_title": "University Dean / Provost",
        "scope": "All University Departments & Cohorts",
    },
    "prof.sharma": {
        "password": "class",
        "name": "Prof. Arvind Sharma",
        "role": "faculty",
        "role_title": "Class Teacher & Associate Professor",
        "department": "Computer Science",
        "semester": 5,
    },
    "student.edg1042": {
        "password": "study",
        "name": _DEMO_STU_NAME,
        "role": "student",
        "role_title": "Undergraduate Student",
        "student_id": "EDG-2026-1042",
    },
    "parent.edg1042": {
        "password": "family",
        "name": _DEMO_PAR_NAME,
        "role": "parent",
        "role_title": "Parent / Guardian",
        "student_id": "EDG-2026-1042",
    },
}

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
    st.session_state["user"] = None

if "interventions" not in st.session_state:
    st.session_state["interventions"] = get_initial_interventions()

if "chat_histories" not in st.session_state:
    st.session_state["chat_histories"] = {}


def main():
    if not st.session_state.get("authenticated", False) or not st.session_state.get("user"):
        inject_global_css("default", hide_sidebar=True)
        render_login_portal(ACCOUNTS_DB, df, get_student_identity)
        return

    current_user = st.session_state["user"]
    role = current_user.get("role", "default")
    inject_global_css(role, hide_sidebar=False)

    if role == "executive":
        render_executive_portal(current_user, df, predictor)
    elif role == "faculty":
        render_faculty_portal(current_user, df, predictor)
    elif role == "student":
        render_student_portal(current_user, df, predictor)
    elif role == "parent":
        render_parent_portal(current_user, df, predictor)
    else:
        st.error(f"Unknown user role: {role}")


if __name__ == "__main__":
    main()
