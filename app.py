"""
EduGrowth AI - Intelligent Student Success & Retention Monitoring System
Institutional Access Portal with Secure Role-Based Authentication:
- Executive / Dean: Institutional cohort analytics, department benchmarks, intervention council
- Faculty / Teacher: Class-level monitoring, student audits & pedagogical action tracking
- Student: Individual academic trajectory, reverse GPA goal optimizer & career pathways
- Parent: Transparent attendance monitoring, achievement highlights & advisor scheduling
- AI Data Assistant: Powered by Groq (openai/gpt-oss-120b) with dynamic Pandas execution
"""

import os
import sys
import json
import hashlib
from datetime import datetime
import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src to sys.path
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))
from inference import EduGrowthPredictor
from chatbot import EduGrowthChatbot
from goal_optimizer import optimize_gpa_target
from interventions_manager import get_initial_interventions, create_intervention
from letter_generator import generate_academic_letter
from career_recommender import evaluate_career_readiness

# Page Configuration - Clean Professional Enterprise Light Theme
st.set_page_config(
    page_title="EduGrowth AI | Institutional Access Portal",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Deterministic Student Name Generator
FIRST_NAMES = ['Aarav', 'Ananya', 'Rohan', 'Priya', 'Aditya', 'Sneha', 'Vikram', 'Neha', 
               'Kavya', 'Rahul', 'Ishaan', 'Tanvi', 'Arjun', 'Meera', 'Varun', 'Rhea',
               'Siddharth', 'Pooja', 'Dhruv', 'Anushka', 'Karan', 'Divya', 'Nikhil', 'Simran']
LAST_NAMES = ['Sharma', 'Verma', 'Patel', 'Nair', 'Gupta', 'Rao', 'Iyer', 'Reddy', 
              'Chatterjee', 'Mehta', 'Joshi', 'Singh', 'Deshmukh', 'Chopra', 'Bose']

def get_student_identity(student_id_str):
    num_part = int(hashlib.md5(student_id_str.encode()).hexdigest(), 16)
    first_name = FIRST_NAMES[num_part % len(FIRST_NAMES)]
    last_name = LAST_NAMES[(num_part // 10) % len(LAST_NAMES)]
    full_name = f"{first_name} {last_name}"
    parent_name = f"Mr. & Mrs. {last_name}"
    return full_name, parent_name

# Enterprise Light Theme Styling - Simple, Crisp & Professional
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"], .stApp {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        background-color: #F8FAFC !important;
        color: #0F172A !important;
    }
    
    .main .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2.5rem;
        max-width: 1380px;
    }
    
    /* Login Portal Card */
    .login-wrapper {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 2.2rem 2.5rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
    }
    
    .login-brand {
        text-align: center;
        margin-bottom: 1.5rem;
    }
    
    .login-brand h2 {
        font-size: 1.45rem;
        font-weight: 700;
        color: #0F172A;
        margin: 0;
        letter-spacing: -0.02em;
    }
    
    .login-brand p {
        font-size: 0.85rem;
        color: #64748B;
        margin-top: 0.35rem;
    }
    
    /* Top Navbar */
    .top-navbar {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 1rem 1.5rem;
        margin-bottom: 1.25rem;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.03);
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .inst-title {
        font-size: 1.2rem;
        font-weight: 700;
        color: #0F172A;
        margin: 0;
    }
    
    .inst-subtitle {
        font-size: 0.82rem;
        color: #64748B;
        margin-top: 0.15rem;
    }
    
    .role-badge {
        background-color: #EFF6FF;
        color: #1E40AF;
        border: 1px solid #DBEAFE;
        padding: 0.35rem 0.75rem;
        border-radius: 6px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    
    /* Clean Metric Cards */
    .clean-card {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 1.1rem 1.25rem;
        box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.03);
        margin-bottom: 0.8rem;
        transition: transform 0.15s ease, box-shadow 0.15s ease;
    }
    
    .clean-card:hover {
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.06);
    }
    
    .card-label {
        font-size: 0.76rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #64748B;
        margin-bottom: 0.35rem;
    }
    
    .card-number {
        font-size: 1.7rem;
        font-weight: 700;
        color: #0F172A;
        line-height: 1.1;
    }
    
    .card-detail {
        font-size: 0.8rem;
        color: #64748B;
        margin-top: 0.3rem;
    }
    
    /* Badges */
    .status-pill {
        padding: 0.25rem 0.65rem;
        border-radius: 4px;
        font-size: 0.78rem;
        font-weight: 600;
        display: inline-block;
    }
    .pill-safe { background-color: #F0FDF4; color: #166534; border: 1px solid #BBF7D0; }
    .pill-warning { background-color: #FFFBEB; color: #92400E; border: 1px solid #FDE68A; }
    .pill-critical { background-color: #FEF2F2; color: #991B1B; border: 1px solid #FECACA; }
    
    .info-panel {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 1.25rem;
        margin-bottom: 1rem;
    }
    
    .panel-heading {
        font-size: 0.92rem;
        font-weight: 600;
        color: #0F172A;
        margin-bottom: 0.75rem;
        border-bottom: 1px solid #F1F5F9;
        padding-bottom: 0.4rem;
    }
    
    div[data-testid="stSidebar"] {
        background-color: #FFFFFF !important;
        border-right: 1px solid #E2E8F0 !important;
    }

    /* Crisp Inputs */
    div[data-baseweb="input"],
    div[data-baseweb="base-input"],
    .stTextInput input,
    .stTextInput > div,
    .stTextInput > div > div,
    input[type="text"],
    input[type="password"] {
        background-color: #FFFFFF !important;
        color: #0F172A !important;
        -webkit-text-fill-color: #0F172A !important;
        border: 1px solid #CBD5E1 !important;
        border-radius: 6px !important;
        box-shadow: none !important;
    }
    
    div[data-baseweb="input"] input,
    .stTextInput input {
        color: #0F172A !important;
        -webkit-text-fill-color: #0F172A !important;
        background-color: transparent !important;
        font-size: 0.95rem !important;
    }
    
    input::placeholder {
        color: #64748B !important;
        -webkit-text-fill-color: #64748B !important;
        opacity: 0.9 !important;
    }
    
    .stTextInput label, 
    div[data-testid="stWidgetLabel"] label, 
    label {
        color: #1E293B !important;
        font-weight: 600 !important;
        font-size: 0.9rem !important;
    }
    
    /* Buttons */
    .stButton > button,
    div.stButton > button,
    button[data-testid^="baseButton"],
    button[kind="secondaryFormSubmit"],
    button[kind="primary"] {
        background-color: #1E3A8A !important;
        color: #FFFFFF !important;
        -webkit-text-fill-color: #FFFFFF !important;
        border: 1px solid #1E3A8A !important;
        border-radius: 6px !important;
        font-weight: 600 !important;
        font-size: 0.92rem !important;
        padding: 0.55rem 1.25rem !important;
        box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05) !important;
        transition: all 0.15s ease !important;
    }
    
    .stButton > button p, 
    .stButton > button span,
    button[data-testid^="baseButton"] p {
        color: #FFFFFF !important;
        -webkit-text-fill-color: #FFFFFF !important;
        font-weight: 600 !important;
    }
    
    .stButton > button:hover,
    button[kind="secondaryFormSubmit"]:hover,
    button[data-testid^="baseButton"]:hover {
        background-color: #2563EB !important;
        border-color: #2563EB !important;
        color: #FFFFFF !important;
        -webkit-text-fill-color: #FFFFFF !important;
    }

    /* Reset Plotly ModeBar Icons */
    .js-plotly-plot .plotly .modebar-container,
    .modebar-container {
        top: 4px !important;
        right: 8px !important;
        background: transparent !important;
    }
    
    .js-plotly-plot .plotly .modebar-btn,
    .modebar-btn,
    button.modebar-btn,
    .modebar-group button {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
    }
    
    .js-plotly-plot .plotly .modebar-btn svg,
    .modebar-btn svg {
        fill: #475569 !important;
        width: 16px !important;
        height: 16px !important;
        opacity: 0.85 !important;
    }

    /* Tab Switcher Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #F1F5F9;
        padding: 6px 8px;
        border-radius: 8px;
        border: 1px solid #E2E8F0;
        margin-bottom: 1.25rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 6px;
        padding: 8px 18px;
        font-weight: 600;
        font-size: 0.92rem;
        color: #475569 !important;
        background-color: transparent !important;
        border: none !important;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #FFFFFF !important;
        color: #1E3A8A !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08) !important;
    }
</style>
""", unsafe_allow_html=True)

# Data & Model Loader
@st.cache_resource
def load_system():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(base_dir, 'data', 'processed', 'processed_cohort.csv')
    df = pd.read_csv(data_path)
    
    # Attach names
    names = [get_student_identity(sid)[0] for sid in df['student_id']]
    df['student_name'] = names
    
    predictor = EduGrowthPredictor()
    return df, predictor

df, predictor = load_system()

# User Credentials Database
ACCOUNTS_DB = {
    "dean.vance": {
        "password": "admin",
        "name": "Dr. Eleanor Vance",
        "role": "executive",
        "role_title": "University Dean / Provost",
        "scope": "All University Departments & Cohorts"
    },
    "prof.sharma": {
        "password": "class",
        "name": "Prof. Arvind Sharma",
        "role": "faculty",
        "role_title": "Class Teacher & Associate Professor",
        "department": "Computer Science",
        "semester": 5
    },
    "student.edg1042": {
        "password": "study",
        "name": "Aarav Patel",
        "role": "student",
        "role_title": "Undergraduate Student",
        "student_id": "EDG-2026-1042"
    },
    "parent.edg1042": {
        "password": "family",
        "name": "Mr. & Mrs. Patel",
        "role": "parent",
        "role_title": "Parent / Guardian",
        "student_id": "EDG-2026-1042"
    }
}

# Session State Initialization
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
    st.session_state["user"] = None

if "interventions" not in st.session_state:
    st.session_state["interventions"] = get_initial_interventions()

if "chat_messages" not in st.session_state:
    st.session_state["chat_messages"] = [
        {
            "role": "assistant",
            "content": "👋 **Hello! I am your EduGrowth AI Data Assistant**, powered by Groq's `openai/gpt-oss-120b`.\n\nI have live query access to our institutional cohort of **3,000 students** across all engineering departments. You can ask me anything about:\n- Department-wide risk distributions & pass rates\n- Attendance correlations, course backlogs, and GPA projections\n- Specific student profiles (by name or ID like `EDG-2026-1042`)\n- Tailored intervention strategies and skill development\n\nHow can I help you analyze the data today?",
            "queries": []
        }
    ]

def apply_clean_chart_theme(fig, height=300):
    fig.update_layout(
        font=dict(family="Inter", size=12, color="#334155"),
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF",
        margin=dict(l=20, r=20, t=30, b=25),
        height=height
    )
    fig.update_xaxes(showgrid=True, gridcolor="#F1F5F9", zeroline=False)
    fig.update_yaxes(showgrid=True, gridcolor="#F1F5F9", zeroline=False)
    return fig

COLOR_SAFE = "#16A34A"
COLOR_WARNING = "#D97706"
COLOR_CRITICAL = "#DC2626"
COLOR_PRIMARY = "#1E3A8A"

# ------------------------------------------------------------------------------
# 1. LOGIN PORTAL
# ------------------------------------------------------------------------------
def render_login_portal():
    """Renders the clean, professional institutional login card with 1-click demo buttons."""
    _, login_col, _ = st.columns([1, 1.4, 1])
    
    with login_col:
        st.markdown("""
        <div class="login-wrapper">
            <div class="login-brand">
                <h2>🏛️ EduGrowth AI</h2>
                <p>Institutional Student Success & Retention Intelligence Portal</p>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("##### **Sign In to Access Institutional Data**")
        
        with st.form("login_form"):
            user_id_input = st.text_input("User ID / Username", placeholder="e.g. dean.vance, prof.sharma, student.edg1042")
            password_input = st.text_input("Password", type="password", placeholder="Enter your security credentials")
            submit_login = st.form_submit_button("Sign In →", use_container_width=True)
            
            if submit_login:
                user_key = user_id_input.strip().lower()
                
                # Check predefined accounts
                if user_key in ACCOUNTS_DB and ACCOUNTS_DB[user_key]["password"] == password_input:
                    st.session_state["authenticated"] = True
                    st.session_state["user"] = ACCOUNTS_DB[user_key]
                    st.rerun()
                # Check dynamic Student ID
                elif user_key.upper() in df['student_id'].values and password_input == "study":
                    sid = user_key.upper()
                    s_name, _ = get_student_identity(sid)
                    st.session_state["authenticated"] = True
                    st.session_state["user"] = {
                        "name": s_name,
                        "role": "student",
                        "role_title": "Undergraduate Student",
                        "student_id": sid
                    }
                    st.rerun()
                else:
                    st.error("Invalid credentials. Please verify your User ID and Password.")
                    
        st.markdown("""
        <div style="margin-top: 1.1rem; padding-top: 0.85rem; border-top: 1px dashed #CBD5E1; text-align: center;">
            <p style="font-size: 0.78rem; font-weight: 600; color: #64748B; margin-bottom: 0.5rem; text-transform: uppercase; letter-spacing: 0.05em;">
                ⚡ 1-Click Demo Login
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        demo_c1, demo_c2 = st.columns(2)
        with demo_c1:
            if st.button("🏛️ Dean Vance (Executive)", use_container_width=True):
                st.session_state["authenticated"] = True
                st.session_state["user"] = ACCOUNTS_DB["dean.vance"]
                st.rerun()
            if st.button("🎓 Aarav Patel (Student)", use_container_width=True):
                st.session_state["authenticated"] = True
                st.session_state["user"] = ACCOUNTS_DB["student.edg1042"]
                st.rerun()
        with demo_c2:
            if st.button("👨‍🏫 Prof. Sharma (Faculty)", use_container_width=True):
                st.session_state["authenticated"] = True
                st.session_state["user"] = ACCOUNTS_DB["prof.sharma"]
                st.rerun()
            if st.button("👨‍👩‍👧 Mr. Patel (Parent)", use_container_width=True):
                st.session_state["authenticated"] = True
                st.session_state["user"] = ACCOUNTS_DB["parent.edg1042"]
                st.rerun()
                
        st.markdown("</div>", unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# 2. ROLE DASHBOARDS
# ------------------------------------------------------------------------------
def render_role_dashboard(current_user, filter_dept="All Departments", filter_sem="All Semesters"):
    user_role = current_user["role"]

    # 1. EXECUTIVE / DEAN
    if user_role == "executive":
        exec_df = df.copy()
        if filter_dept != "All Departments":
            exec_df = exec_df[exec_df['department'] == filter_dept]
        if filter_sem != "All Semesters":
            exec_df = exec_df[exec_df['semester'] == filter_sem]
            
        st.markdown(f"""
        <div class="top-navbar">
            <div>
                <div class="inst-title">Executive Institutional Dashboard</div>
                <div class="inst-subtitle">Logged in as {current_user['name']} • Full University Portfolio Access</div>
            </div>
            <div class="role-badge">Scope: {len(exec_df):,} Enrolled Students</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Macro KPIs
        total = len(exec_df)
        critical_cnt = len(exec_df[exec_df['academic_risk_level'] == 2])
        moderate_cnt = len(exec_df[exec_df['academic_risk_level'] == 1])
        safe_cnt = len(exec_df[exec_df['academic_risk_level'] == 0])
        avg_gpa = exec_df['target_end_term_gpa'].mean()
        retention_rate = ((safe_cnt + moderate_cnt) / total * 100) if total else 0
        
        k1, k2, k3, k4, k5 = st.columns(5)
        with k1:
            st.markdown(f"""
            <div class="clean-card">
                <div class="card-label">Monitored Cohort</div>
                <div class="card-number">{total:,}</div>
                <div class="card-detail">Active Students</div>
            </div>
            """, unsafe_allow_html=True)
        with k2:
            st.markdown(f"""
            <div class="clean-card" style="border-top: 3px solid {COLOR_CRITICAL};">
                <div class="card-label">Critical Risk</div>
                <div class="card-number" style="color: {COLOR_CRITICAL};">{critical_cnt} <span style="font-size:0.95rem; font-weight:500;">({critical_cnt/total*100:.1f}%)</span></div>
                <div class="card-detail">Urgent Intervention</div>
            </div>
            """, unsafe_allow_html=True)
        with k3:
            st.markdown(f"""
            <div class="clean-card" style="border-top: 3px solid {COLOR_WARNING};">
                <div class="card-label">Academic Watchlist</div>
                <div class="card-number" style="color: {COLOR_WARNING};">{moderate_cnt} <span style="font-size:0.95rem; font-weight:500;">({moderate_cnt/total*100:.1f}%)</span></div>
                <div class="card-detail">Moderate Counseling</div>
            </div>
            """, unsafe_allow_html=True)
        with k4:
            st.markdown(f"""
            <div class="clean-card" style="border-top: 3px solid {COLOR_SAFE};">
                <div class="card-label">Retention Index</div>
                <div class="card-number">{retention_rate:.1f}%</div>
                <div class="card-detail">Projected Passing Cohort</div>
            </div>
            """, unsafe_allow_html=True)
        with k5:
            st.markdown(f"""
            <div class="clean-card" style="border-top: 3px solid {COLOR_PRIMARY};">
                <div class="card-label">Forecasted Mean GPA</div>
                <div class="card-number">{avg_gpa:.2f}</div>
                <div class="card-detail">10-Point Institutional Benchmark</div>
            </div>
            """, unsafe_allow_html=True)
            
        st.write("")
        
        c1, c2 = st.columns([1, 1])
        with c1:
            st.markdown("##### **Department-Wise Risk Stratification**")
            dept_risk = exec_df.groupby(['department', 'academic_risk_level']).size().reset_index(name='count')
            dept_risk['Status'] = dept_risk['academic_risk_level'].map({0: 'On Track', 1: 'Moderate Risk', 2: 'Critical Risk'})
            
            fig1 = px.bar(
                dept_risk,
                x='department',
                y='count',
                color='Status',
                color_discrete_map={'On Track': '#94A3B8', 'Moderate Risk': '#F59E0B', 'Critical Risk': '#DC2626'},
                barmode='stack',
                height=320
            )
            fig1 = apply_clean_chart_theme(fig1, height=320)
            fig1.update_layout(xaxis_title=None, yaxis_title="Students", legend=dict(orientation="h", yanchor="bottom", y=1.04, xanchor="left", x=0))
            st.plotly_chart(fig1, use_container_width=True)
            
        with c2:
            st.markdown("##### **Attendance Deficit vs Internal Assessment Correlation**")
            sample_scat = exec_df.sample(min(600, len(exec_df)), random_state=42).copy()
            sample_scat['Status'] = sample_scat['academic_risk_level'].map({0: 'On Track', 1: 'Moderate Risk', 2: 'Critical Risk'})
            
            fig2 = px.scatter(
                sample_scat,
                x='attendance_rate_pct',
                y='internal_assessment_score',
                color='Status',
                color_discrete_map={'On Track': '#CBD5E1', 'Moderate Risk': '#F59E0B', 'Critical Risk': '#DC2626'},
                labels={'attendance_rate_pct': 'Attendance (%)', 'internal_assessment_score': 'Internal Marks (/100)'},
                height=320
            )
            fig2.add_vline(x=75, line_width=1.5, line_dash="dot", line_color="#94A3B8")
            fig2 = apply_clean_chart_theme(fig2, height=320)
            fig2.update_layout(legend=dict(orientation="h", yanchor="bottom", y=1.04, xanchor="left", x=0))
            st.plotly_chart(fig2, use_container_width=True)

        # Quick Student Lookup Bar
        st.markdown("##### **🔍 Instant Student Deep-Dive Search**")
        search_kw = st.text_input("Quick Search Student by Name or ID:", placeholder="e.g. EDG-2026-1042 or Patel")
        if search_kw:
            matched = df[df['student_id'].str.contains(search_kw, case=False) | df['student_name'].str.contains(search_kw, case=False)]
            if len(matched) > 0:
                sel_opt = st.selectbox("Select Record to Inspect:", matched['student_id'] + " - " + matched['student_name'])
                target_sid = sel_opt.split(" - ")[0]
                s_row = df[df['student_id'] == target_sid].iloc[0]
                diag = predictor.predict_single(s_row.to_dict())
                
                sc1, sc2, sc3, sc4 = st.columns(4)
                with sc1:
                    st.metric("Projected GPA", f"{diag['predicted_end_term_gpa']:.2f}", diag['gpa_trajectory'])
                with sc2:
                    st.metric("Attendance", f"{s_row['attendance_rate_pct']:.1f}%", "- Deficit" if s_row['attendance_rate_pct'] < 75 else "Good")
                with sc3:
                    st.metric("Internal Marks", f"{s_row['internal_assessment_score']:.1f}/100")
                with sc4:
                    st.metric("Backlogs", f"{s_row['backlog_count']}")
                st.caption(f"**Identified Drivers:** {', '.join(diag['key_risk_drivers']) if diag['key_risk_drivers'] else 'None (Consistent standing)'}")
            else:
                st.warning("No student matching that query found.")

        st.markdown("##### **High-Priority Student Watchlist (For Academic Council Interventions)**")
        at_risk_df = exec_df[exec_df['academic_risk_level'] == 2][
            ['student_id', 'student_name', 'department', 'semester', 'attendance_rate_pct', 'internal_assessment_score', 'backlog_count', 'target_end_term_gpa']
        ].copy()
        at_risk_df.columns = ['ID', 'Student Name', 'Department', 'Sem', 'Attendance %', 'Internal Score', 'Backlogs', 'Forecasted GPA']
        
        st.dataframe(at_risk_df.head(25), hide_index=True, use_container_width=True, height=280)
        
        csv_bytes = at_risk_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Full Institutional At-Risk Report (.CSV)",
            data=csv_bytes,
            file_name='institutional_at_risk_students.csv',
            mime='text/csv'
        )

    # 2. FACULTY / PROFESSOR
    elif user_role == "faculty":
        f_dept = current_user["department"]
        f_sem = current_user["semester"]
        class_df = df[(df['department'] == f_dept) & (df['semester'] == f_sem)].copy()
        
        st.markdown(f"""
        <div class="top-navbar">
            <div>
                <div class="inst-title">Faculty Portal: {current_user['name']}</div>
                <div class="inst-subtitle">Department: {f_dept} • Semester {f_sem} • Enrolled Section</div>
            </div>
            <div class="role-badge">Class Size: {len(class_df)} Students</div>
        </div>
        """, unsafe_allow_html=True)
        
        c_att = class_df['attendance_rate_pct'].mean()
        c_assign = class_df['assignment_completion_pct'].mean()
        c_internal = class_df['internal_assessment_score'].mean()
        c_at_risk = len(class_df[class_df['academic_risk_level'] > 0])
        
        fc1, fc2, fc3, fc4 = st.columns(4)
        with fc1:
            st.markdown(f"""
            <div class="clean-card">
                <div class="card-label">Class Attendance Average</div>
                <div class="card-number">{c_att:.1f}%</div>
                <div class="card-detail">{"Compliant (>75%)" if c_att >= 75 else "Requires Attendance Drive"}</div>
            </div>
            """, unsafe_allow_html=True)
        with fc2:
            st.markdown(f"""
            <div class="clean-card">
                <div class="card-label">Assignment Submission Rate</div>
                <div class="card-number">{c_assign:.1f}%</div>
                <div class="card-detail">Homework Punctuality</div>
            </div>
            """, unsafe_allow_html=True)
        with fc3:
            st.markdown(f"""
            <div class="clean-card">
                <div class="card-label">Internal Exam Average</div>
                <div class="card-number">{c_internal:.1f}<span style="font-size:1rem; font-weight:500;">/100</span></div>
                <div class="card-detail">Class Mean Score</div>
            </div>
            """, unsafe_allow_html=True)
        with fc4:
            st.markdown(f"""
            <div class="clean-card" style="border-top: 3px solid {COLOR_WARNING};">
                <div class="card-label">Students Needing Support</div>
                <div class="card-number" style="color:{COLOR_WARNING};">{c_at_risk}</div>
                <div class="card-detail">Watchlist / Critical Risk</div>
            </div>
            """, unsafe_allow_html=True)
            
        st.write("")
        
        t_col1, t_col2 = st.columns([2, 1])
        with t_col1:
            st.markdown("##### **Class Roster & Academic Standing**")
            class_table = class_df[['student_id', 'student_name', 'attendance_rate_pct', 'assignment_completion_pct', 'internal_assessment_score', 'backlog_count', 'academic_risk_level']].copy()
            class_table.columns = ['Student ID', 'Full Name', 'Attendance %', 'Assignments %', 'Internal (/100)', 'Backlogs', 'Standing']
            class_table['Standing'] = class_table['Standing'].map({0: '🟢 Good Standing', 1: '🟡 Watchlist', 2: '🔴 Critical Risk'})
            st.dataframe(class_table, hide_index=True, use_container_width=True, height=350)
            
        with t_col2:
            st.markdown("##### **Direct Student Intervention**")
            selected_student = st.selectbox("Select Student to Audit", class_df['student_name'].tolist())
            sel_row = class_df[class_df['student_name'] == selected_student].iloc[0]
            diag = predictor.predict_single(sel_row.to_dict())
            
            st.markdown(f"""
            <div class="info-panel">
                <div class="panel-heading">Identified Challenges for {selected_student}</div>
            """, unsafe_allow_html=True)
            for d in diag['key_risk_drivers']:
                st.markdown(f"<span style='font-size:0.85rem;'>• {d}</span>", unsafe_allow_html=True)
                
            st.markdown("<div style='margin-top:0.8rem; font-weight:600; font-size:0.85rem;'>Suggested Action:</div>", unsafe_allow_html=True)
            st.info(diag['prescribed_interventions'][0] if diag['prescribed_interventions'] else "Maintain consistent coursework.")
            
            if st.button("📧 Schedule Remedial Peer Tutorial Session"):
                new_item = create_intervention(
                    student_id=sel_row['student_id'],
                    student_name=selected_student,
                    department=f_dept,
                    risk_tier="Critical Risk" if diag['risk_level'] == 2 else "Moderate Risk",
                    intervention_type="Peer Tutoring & Lab Review",
                    priority="Urgent" if diag['risk_level'] == 2 else "Medium",
                    assigned_to=current_user['name'],
                    notes="Assigned following class diagnostic audit."
                )
                st.session_state["interventions"].insert(0, new_item)
                st.success(f"Tutorial alert sent to {selected_student}.")
            st.markdown("</div>", unsafe_allow_html=True)

    # 3. STUDENT PORTAL
    elif user_role == "student":
        target_sid = current_user["student_id"]
        s_row = df[df['student_id'] == target_sid].iloc[0]
        diag = predictor.predict_single(s_row.to_dict())
        
        st.markdown(f"""
        <div class="top-navbar">
            <div>
                <div class="inst-title">Student Growth Portal • {current_user['name']}</div>
                <div class="inst-subtitle">{s_row['department']} • Semester {s_row['semester']} • ID: {s_row['student_id']}</div>
            </div>
            <div class="role-badge">Status: Enrolled Student</div>
        </div>
        """, unsafe_allow_html=True)
        
        r_lvl = diag['risk_level']
        if r_lvl == 0:
            st.markdown('<div class="status-pill pill-safe">ACADEMIC STANDING: EXCELLENT • ON TRACK</div>', unsafe_allow_html=True)
        elif r_lvl == 1:
            st.markdown('<div class="status-pill pill-warning">ACADEMIC STANDING: ATTENTION REQUIRED • ADVISORY WATCHLIST</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="status-pill pill-critical">ACADEMIC STANDING: CRITICAL RISK • CONSULT ADVISOR IMMEDIATELY</div>', unsafe_allow_html=True)
            
        st.write("")
        
        sc1, sc2, sc3, sc4 = st.columns(4)
        with sc1:
            st.markdown(f"""
            <div class="clean-card">
                <div class="card-label">Cumulative CGPA</div>
                <div class="card-number">{s_row['prev_cgpa']:.2f}</div>
                <div class="card-detail">Historical Benchmark</div>
            </div>
            """, unsafe_allow_html=True)
        with sc2:
            st.markdown(f"""
            <div class="clean-card" style="border-top: 3px solid #2563EB;">
                <div class="card-label">Forecasted End-Term GPA</div>
                <div class="card-number" style="color:#2563EB;">{diag['predicted_end_term_gpa']:.2f}</div>
                <div class="card-detail">Trajectory: {diag['gpa_trajectory']}</div>
            </div>
            """, unsafe_allow_html=True)
        with sc3:
            att_c = COLOR_SAFE if s_row['attendance_rate_pct'] >= 75 else COLOR_CRITICAL
            st.markdown(f"""
            <div class="clean-card">
                <div class="card-label">Class Attendance</div>
                <div class="card-number" style="color:{att_c};">{s_row['attendance_rate_pct']:.1f}%</div>
                <div class="card-detail">Requirement: 75.0%</div>
            </div>
            """, unsafe_allow_html=True)
        with sc4:
            st.markdown(f"""
            <div class="clean-card">
                <div class="card-label">Employability Index</div>
                <div class="card-number">{s_row['employability_index']:.1f}<span style="font-size:1rem; font-weight:500;">/100</span></div>
                <div class="card-detail">Portfolio & Skill Score</div>
            </div>
            """, unsafe_allow_html=True)
            
        st.write("")
        
        p1, p2 = st.columns([1, 1])
        with p1:
            st.markdown("##### **My Academic Progress Trajectory**")
            prog_df = pd.DataFrame({
                'Milestone': ['High School Score', 'Historical CGPA', 'Current Internal Marks', 'Model Forecasted Term GPA'],
                'Score Normalized (/10)': [
                    s_row['prior_hs_percentage'] / 10.0,
                    s_row['prev_cgpa'],
                    s_row['internal_assessment_score'] / 10.0,
                    diag['predicted_end_term_gpa']
                ]
            })
            fig_s = px.line(prog_df, x='Milestone', y='Score Normalized (/10)', markers=True, line_shape='spline', height=270)
            fig_s = apply_clean_chart_theme(fig_s, height=270)
            fig_s.update_yaxes(range=[0, 10])
            st.plotly_chart(fig_s, use_container_width=True)
            
        with p2:
            st.markdown("##### **Verified Skills & Portfolio Achievements**")
            st.markdown(f"""
            <div class="info-panel">
                <div class="panel-heading">My Professional Accomplishments</div>
                <div style="display:flex; justify-content:space-between; margin-bottom:0.5rem;">
                    <span>📜 Certified Courses:</span>
                    <strong>{s_row['certifications_count']} Completed</strong>
                </div>
                <div style="display:flex; justify-content:space-between; margin-bottom:0.5rem;">
                    <span>💻 Technical Skills:</span>
                    <strong>{s_row['technical_skills_count']} Verified</strong>
                </div>
                <div style="display:flex; justify-content:space-between; margin-bottom:0.5rem;">
                    <span>🛠️ Capstone Projects:</span>
                    <strong>{s_row['projects_count']} Completed</strong>
                </div>
                <div style="display:flex; justify-content:space-between;">
                    <span>💼 Industry Internship:</span>
                    <strong>{"Completed" if s_row['internship_completed'] == 1 else "In Progress"}</strong>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
        st.markdown("##### **Personalized AI Action Plan to Improve Grades**")
        for r in diag['prescribed_interventions']:
            st.info(f"💡 {r}")

    # 4. PARENT PORTAL
    elif user_role == "parent":
        target_sid = current_user["student_id"]
        p_student = df[df['student_id'] == target_sid].iloc[0]
        p_diag = predictor.predict_single(p_student.to_dict())
        
        st.markdown(f"""
        <div class="top-navbar">
            <div>
                <div class="inst-title">Parent Academic Transparency Portal</div>
                <div class="inst-subtitle">Child: {p_student['student_name']} • {p_student['department']} • Semester {p_student['semester']}</div>
            </div>
            <div class="role-badge">Guardian View: {current_user['name']}</div>
        </div>
        """, unsafe_allow_html=True)
        
        if p_student['attendance_rate_pct'] < 75.0:
            st.warning(f"⚠️ **Attendance Advisory:** {p_student['student_name']}'s attendance is currently at **{p_student['attendance_rate_pct']:.1f}%**, which is below the university minimum requirement of 75%. Please ensure regular attendance.")
        else:
            st.success(f"✅ **Attendance Good Standing:** {p_student['student_name']} maintains healthy classroom attendance at **{p_student['attendance_rate_pct']:.1f}%**.")
            
        st.write("")
        
        pc1, pc2, pc3 = st.columns(3)
        with pc1:
            st.markdown(f"""
            <div class="clean-card">
                <div class="card-label">Class Attendance</div>
                <div class="card-number">{p_student['attendance_rate_pct']:.1f}%</div>
                <div class="card-detail">Minimum Requirement: 75.0%</div>
            </div>
            """, unsafe_allow_html=True)
        with pc2:
            st.markdown(f"""
            <div class="clean-card">
                <div class="card-label">Internal Exam Average</div>
                <div class="card-number">{p_student['internal_assessment_score']:.1f}<span style="font-size:1rem; font-weight:500;">/100</span></div>
                <div class="card-detail">Mid-Term Assessment Score</div>
            </div>
            """, unsafe_allow_html=True)
        with pc3:
            st.markdown(f"""
            <div class="clean-card">
                <div class="card-label">Active Course Backlogs</div>
                <div class="card-number" style="color: {'#DC2626' if p_student['backlog_count'] > 0 else '#16A34A'};">{p_student['backlog_count']}</div>
                <div class="card-detail">{"Requires re-examination clearance" if p_student['backlog_count'] > 0 else "All historical subjects cleared"}</div>
            </div>
            """, unsafe_allow_html=True)
            
        st.write("")
        
        par_col1, par_col2 = st.columns([1, 1])
        with par_col1:
            st.markdown("##### **Accomplishments & Growth Highlights**")
            st.markdown(f"""
            <div class="info-panel">
                <div class="panel-heading">Key Successes this Semester</div>
                <p style="margin-bottom:0.5rem; font-size:0.88rem;">⭐ <strong>Projects Completed:</strong> Developed and submitted {p_student['projects_count']} practical project(s).</p>
                <p style="margin-bottom:0.5rem; font-size:0.88rem;">⭐ <strong>Technical Upskilling:</strong> Completed {p_student['certifications_count']} certified online specialization course(s).</p>
                <p style="margin-bottom:0.5rem; font-size:0.88rem;">⭐ <strong>Self-Study Velocity:</strong> Spends an average of {p_student['lms_weekly_hours']:.1f} hours/week on digital study materials.</p>
                <p style="font-size:0.88rem;">⭐ <strong>Assignment Delivery:</strong> {p_student['assignment_completion_pct']:.1f}% of continuous coursework submitted on schedule.</p>
            </div>
            """, unsafe_allow_html=True)
            
        with par_col2:
            st.markdown("##### **Teacher & Advisor Observations**")
            st.markdown(f"""
            <div class="info-panel">
                <div class="panel-heading">Teacher & Advisor Observations</div>
            """, unsafe_allow_html=True)
            for driver in p_diag['key_risk_drivers']:
                st.markdown(f"<p style='font-size:0.88rem; margin-bottom:0.4rem;'>• {driver}</p>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
            
            st.markdown("##### **Communicate with Class Teacher**")
            if st.button("📞 Request Virtual Consultation with Prof. Arvind Sharma"):
                st.success("Consultation request logged. Prof. Arvind Sharma will contact you via email within 24 hours.")

# ------------------------------------------------------------------------------
# 3. FEATURE: WHAT-IF & GOAL-SEEK SIMULATOR TAB
# ------------------------------------------------------------------------------
def render_simulator_tab(current_user):
    st.markdown("##### **🎯 Academic Performance & Goal Simulator**")
    st.caption("Perform forward risk simulation or calculate the exact effort required to achieve your target GPA.")
    
    # Select Student Profile
    if current_user["role"] in ["student", "parent"]:
        active_student = df[df['student_id'] == current_user['student_id']].iloc[0]
    else:
        s_cand = st.selectbox("Select Student to Simulate:", df['student_id'] + " - " + df['student_name'])
        active_student = df[df['student_id'] == s_cand.split(" - ")[0]].iloc[0]
        
    s_dict = active_student.to_dict()
    cur_diag = predictor.predict_single(s_dict)
    
    sim_mode = st.radio("Choose Simulation Mode:", ["🎯 Reverse Goal-Seek (Find required effort for target GPA)", "⚙️ Forward What-If Sliders (Simulate outcomes)"], horizontal=True)
    
    if sim_mode.startswith("🎯"):
        st.write("")
        g_c1, g_c2 = st.columns([1, 1.4], gap="large")
        with g_c1:
            st.markdown(f"**Target GPA for {active_student['student_name']}:**")
            st.caption(f"Current Baseline: **{cur_diag['predicted_end_term_gpa']:.2f} GPA**")
            target_val = st.slider("Select Desired End-Term GPA:", 5.0, 9.8, float(min(9.5, round(cur_diag['predicted_end_term_gpa'] + 0.6, 1))), 0.1)
            
        with g_c2:
            opt = optimize_gpa_target(s_dict, target_val, predictor)
            
            f_color = COLOR_SAFE if opt['feasibility_score'] >= 80 else (COLOR_WARNING if opt['feasibility_score'] >= 50 else COLOR_CRITICAL)
            st.markdown(f"""
            <div class="info-panel" style="border-left: 4px solid {f_color};">
                <div style="font-weight: 700; font-size: 1.05rem; color: #0F172A; margin-bottom: 0.3rem;">
                    Feasibility: {opt['status']} ({opt['feasibility_score']}% confidence)
                </div>
                <div style="font-size: 0.88rem; color: #475569;">{opt['message']}</div>
            </div>
            """, unsafe_allow_html=True)
            
            o1, o2, o3 = st.columns(3)
            with o1:
                st.metric("Target Attendance", f"{opt['required_attendance']:.1f}%", f"+{opt['attendance_delta']:.1f}%" if opt['attendance_delta'] > 0 else "Steady")
            with o2:
                st.metric("Target Internal Score", f"{opt['required_internal']:.1f}/100", f"+{opt['internal_delta']:.1f} pts" if opt['internal_delta'] > 0 else "Steady")
            with o3:
                st.metric("LMS Study Time", f"{opt['required_study_hours']:.1f} hrs/wk", f"+{opt['study_delta']:.1f} hrs" if opt['study_delta'] > 0 else "Steady")
                
            st.markdown("**Roadmap Steps:**")
            for step in opt['action_steps']:
                st.markdown(f"• {step}")
                
    else:
        st.write("")
        c_input_col, c_result_col = st.columns([1.1, 1.3], gap="large")
        with c_input_col:
            calc_attendance = st.slider("Class Attendance Rate (%)", 30.0, 100.0, float(active_student['attendance_rate_pct']), 1.0)
            calc_internal = st.slider("Internal Exam Marks (/100)", 10.0, 100.0, float(active_student['internal_assessment_score']), 1.0)
            calc_study_hours = st.slider("Weekly Study / LMS Hours (hrs/wk)", 1.0, 35.0, float(active_student['lms_weekly_hours']), 0.5)
            calc_assignment = st.slider("Assignment Submission Rate (%)", 20.0, 100.0, float(active_student['assignment_completion_pct']), 1.0)
            
        with c_result_col:
            calc_dict = s_dict.copy()
            calc_dict['attendance_rate_pct'] = calc_attendance
            calc_dict['internal_assessment_score'] = calc_internal
            calc_dict['lms_weekly_hours'] = calc_study_hours
            calc_dict['assignment_completion_pct'] = calc_assignment
            calc_dict['lms_logins_per_week'] = int(calc_study_hours * 1.6)
            
            calc_res = predictor.predict_single(calc_dict)
            fail_prob = float(calc_res['risk_probabilities']['High Risk'])
            pass_prob = round(100.0 - fail_prob, 1)
            
            res_c1, res_c2, res_c3 = st.columns(3)
            with res_c1:
                st.markdown(f"""
                <div class="clean-card" style="border-top: 3px solid #16A34A; padding:0.85rem 1rem;">
                    <div class="card-label">Passing Chance</div>
                    <div class="card-number" style="color:#16A34A; font-size:1.55rem;">{pass_prob}%</div>
                    <div class="card-detail">Course Clearance</div>
                </div>
                """, unsafe_allow_html=True)
            with res_c2:
                st.markdown(f"""
                <div class="clean-card" style="border-top: 3px solid #DC2626; padding:0.85rem 1rem;">
                    <div class="card-label">Failing Risk</div>
                    <div class="card-number" style="color:#DC2626; font-size:1.55rem;">{fail_prob}%</div>
                    <div class="card-detail">Arrear Risk</div>
                </div>
                """, unsafe_allow_html=True)
            with res_c3:
                st.markdown(f"""
                <div class="clean-card" style="border-top: 3px solid #2563EB; padding:0.85rem 1rem;">
                    <div class="card-label">Forecasted GPA</div>
                    <div class="card-number" style="color:#2563EB; font-size:1.55rem;">{calc_res['predicted_end_term_gpa']:.2f}</div>
                    <div class="card-detail">Target 10-Pt Benchmark</div>
                </div>
                """, unsafe_allow_html=True)
                
            prob_chart_df = pd.DataFrame({
                'Outcome': ['Passing Probability', 'Failing Risk'],
                'Probability (%)': [pass_prob, fail_prob]
            })
            fig_calc = px.bar(
                prob_chart_df, x='Probability (%)', y='Outcome', orientation='h', color='Outcome',
                color_discrete_map={'Passing Probability': '#16A34A', 'Failing Risk': '#DC2626'}, text_auto='.1f', height=160
            )
            fig_calc = apply_clean_chart_theme(fig_calc, height=160)
            fig_calc.update_layout(showlegend=False, xaxis=dict(range=[0, 100]))
            st.plotly_chart(fig_calc, use_container_width=True)

# ------------------------------------------------------------------------------
# 4. FEATURE: CAREER PATHWAYS & INTERVENTIONS TAB
# ------------------------------------------------------------------------------
def render_career_and_interventions_tab(current_user):
    user_role = current_user["role"]
    
    # If Student or Parent: Focus on Career Pathways & Industry Readiness
    if user_role in ["student", "parent"]:
        st.markdown("##### **🧭 Career Pathways & Industry Skill Readiness**")
        st.caption("AI mapping of student skill count, projects, and GPA against high-demand engineering careers.")
        
        active_student = df[df['student_id'] == current_user['student_id']].iloc[0]
        readiness = evaluate_career_readiness(active_student.to_dict())
        
        cp1, cp2, cp3 = st.columns(3)
        cols = [cp1, cp2, cp3]
        for i, item in enumerate(readiness['top_tracks']):
            track = item['track']
            score = item['match_score']
            with cols[i]:
                st.markdown(f"""
                <div class="clean-card" style="border-top: 3px solid #1E3A8A; min-height: 240px;">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom: 0.35rem;">
                        <span class="card-label">Rank #{i+1} Match</span>
                        <span style="font-weight: 700; color: #16A34A; font-size: 1.1rem;">{score}%</span>
                    </div>
                    <div style="font-weight: 700; font-size: 1.05rem; color: #0F172A; margin-bottom: 0.3rem;">{track['title']}</div>
                    <div style="font-size: 0.8rem; color: #64748B; margin-bottom: 0.6rem;">{track['description']}</div>
                    <div style="font-size: 0.78rem; font-weight: 600; color: #334155;">Key Competencies:</div>
                    <div style="font-size: 0.76rem; color: #64748B;">{', '.join(track['key_skills'][:3])}</div>
                </div>
                """, unsafe_allow_html=True)
                
        st.write("")
        g1, g2 = st.columns(2)
        with g1:
            st.markdown("##### **Identified Skill Gaps & Action Items:**")
            for g in readiness['gaps']:
                st.info(f"💡 {g}")
        with g2:
            st.markdown("##### **Recommended Industry Certifications:**")
            for cert in readiness['recommended_certifications']:
                st.success(f"🎓 **{cert}**")

    # If Executive or Faculty: Focus on Interventions, Letter Generator & Department Benchmarks
    else:
        sub_tab1, sub_tab2, sub_tab3 = st.tabs([
            "📋 Pedagogical Action Tracker",
            "📜 Official Letter & Notice Generator",
            "⚖️ Department Benchmarks"
        ])
        
        with sub_tab1:
            st.markdown("##### **Pedagogical Action & Intervention Log**")
            with st.expander("➕ **Log New Student Intervention**", expanded=False):
                ic1, ic2 = st.columns(2)
                with ic1:
                    s_pick = st.selectbox("Select Student:", df['student_id'] + " - " + df['student_name'])
                    i_act = st.selectbox("Intervention Type:", ["Peer Tutoring", "Faculty Counseling", "Attendance Warning Notice", "Parent Conference"])
                    i_prio = st.selectbox("Priority Tier:", ["Urgent", "High", "Medium", "Low"])
                with ic2:
                    assignee = st.text_input("Assigned Mentor / Counselor:", value=current_user['name'])
                    i_note = st.text_area("Observations:", placeholder="Enter action plan notes...")
                if st.button("Save Intervention Log"):
                    sid = s_pick.split(" - ")[0]
                    sname = s_pick.split(" - ")[1]
                    s_r = df[df['student_id'] == sid].iloc[0]
                    new_item = create_intervention(
                        student_id=sid, student_name=sname, department=s_r['department'],
                        risk_tier="Critical Risk" if s_r['academic_risk_level'] == 2 else "Moderate Risk",
                        intervention_type=i_act, priority=i_prio, assigned_to=assignee, notes=i_note
                    )
                    st.session_state["interventions"].insert(0, new_item)
                    st.success(f"Intervention recorded for {sname}!")
                    st.rerun()
                    
            # Display interventions
            for item in st.session_state["interventions"]:
                p_c = COLOR_CRITICAL if item['priority'] == "Urgent" else (COLOR_WARNING if item['priority'] == "High" else COLOR_PRIMARY)
                st.markdown(f"""
                <div class="info-panel" style="margin-bottom: 0.6rem; padding: 0.85rem 1.1rem;">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <strong>{item['student_name']}</strong> ({item['student_id']} • {item['department']})
                        <span class="status-pill" style="border: 1px solid {p_c}; color: {p_c};">{item['priority']}</span>
                    </div>
                    <div style="font-size:0.83rem; color:#475569; margin-top:0.25rem;">
                        <strong>Action:</strong> {item['intervention_type']} • <em>Assigned to {item['assigned_to']}</em> ({item['status']})
                    </div>
                    <div style="font-size:0.8rem; color:#64748B; margin-top:0.2rem;">{item['notes']}</div>
                </div>
                """, unsafe_allow_html=True)
                
        with sub_tab2:
            st.markdown("##### **Official Document & Letter Generator**")
            lc1, lc2 = st.columns([1, 1.6], gap="large")
            with lc1:
                s_sel = st.selectbox("Select Recipient Student:", df['student_id'] + " - " + df['student_name'], key="let_s_sel")
                l_type = st.radio("Notice Type:", [
                    "Dean's Commendation of Academic Excellence",
                    "Formal Academic Early-Warning & Attendance Notice",
                    "Parent Consultation Invitation"
                ])
                l_key = "commendation" if "Commendation" in l_type else ("warning" if "Warning" in l_type else "parent")
                s_name = st.text_input("Signatory Name:", "Dr. Eleanor Vance")
                s_title = st.text_input("Signatory Title:", "Dean of Academic Affairs")
            with lc2:
                s_row = df[df['student_id'] == s_sel.split(" - ")[0]].iloc[0]
                s_diag = predictor.predict_single(s_row.to_dict())
                doc_text = generate_academic_letter(l_key, s_row.to_dict(), s_diag, s_name, s_title)
                st.markdown(f"""<div class="info-panel" style="max-height: 440px; overflow-y: auto;">""", unsafe_allow_html=True)
                st.markdown(doc_text)
                st.markdown("</div>", unsafe_allow_html=True)
                st.download_button("📥 Download Official Letter (.md)", data=doc_text.encode('utf-8'), file_name=f"official_letter_{s_row['student_id']}.md", mime="text/markdown", use_container_width=True)

        with sub_tab3:
            st.markdown("##### **Departmental Comparative Benchmarks**")
            dept_df = df.groupby('department').agg(
                Students=('student_id', 'count'),
                Attendance=('attendance_rate_pct', 'mean'),
                Internal_Marks=('internal_assessment_score', 'mean'),
                Forecasted_GPA=('target_end_term_gpa', 'mean'),
                Employability=('employability_index', 'mean')
            ).reset_index()
            st.dataframe(dept_df.style.format({'Attendance': '{:.1f}%', 'Internal_Marks': '{:.1f}', 'Forecasted_GPA': '{:.2f}', 'Employability': '{:.1f}'}), hide_index=True, use_container_width=True)

# ------------------------------------------------------------------------------
# 5. AI DATA CHATBOT INTERFACE (GROQ OPENAI/GPT-OSS-120B)
# ------------------------------------------------------------------------------
def render_chatbot_interface(current_user, df):
    user_role = current_user.get("role", "guest")
    
    if "custom_df" not in st.session_state:
        st.session_state["custom_df"] = None
    if "custom_dataset_name" not in st.session_state:
        st.session_state["custom_dataset_name"] = None
    if "dataset_source" not in st.session_state:
        st.session_state["dataset_source"] = "institutional"
    if "selected_model" not in st.session_state:
        st.session_state["selected_model"] = "openai/gpt-oss-120b"
        
    is_custom = (st.session_state["dataset_source"] == "custom" and st.session_state["custom_df"] is not None)
    active_df = st.session_state["custom_df"] if is_custom else df
    active_name = st.session_state["custom_dataset_name"] if is_custom else "Institutional Student Cohort"
    
    chatbot = EduGrowthChatbot(
        active_df,
        dataset_name=active_name,
        model=st.session_state["selected_model"]
    )
    
    # Top Banner
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #1E3A8A 0%, #1E40AF 50%, #2563EB 100%); border-radius: 8px; padding: 1.1rem 1.4rem; color: #FFFFFF; margin-bottom: 1rem;">
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px;">
            <div>
                <h4 style="margin: 0; color: #FFFFFF; font-weight: 700;">💬 EduGrowth AI Data Assistant</h4>
                <p style="margin: 0.2rem 0 0 0; color: #DBEAFE; font-size: 0.85rem;">Natural language queries with verified Pandas execution.</p>
            </div>
            <div>
                <span style="background-color: rgba(255,255,255,0.18); border-radius: 4px; padding: 0.25rem 0.55rem; font-size: 0.78rem; font-weight: 600;">
                    ⚡ Groq: {st.session_state['selected_model']}
                </span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Dataset Upload Expander
    with st.expander("📁 **Dataset Source & File Upload (Use Default or Upload Your Own CSV/Excel)**", expanded=False):
        src_c1, src_c2 = st.columns([1.3, 2.2])
        with src_c1:
            src_mode = st.radio("Source:", ["Institutional Cohort (3,000 Students)", "Upload Custom Dataset (CSV/Excel)"], index=0 if not is_custom else 1)
            if src_mode.startswith("Inst") and is_custom:
                st.session_state["dataset_source"] = "institutional"
                st.session_state["custom_df"] = None
                st.session_state["custom_dataset_name"] = None
                st.rerun()
            elif src_mode.startswith("Upload") and not is_custom:
                st.session_state["dataset_source"] = "custom"
        with src_c2:
            if is_custom or src_mode.startswith("Upload"):
                up_file = st.file_uploader("Upload tabular data", type=["csv", "xlsx", "xls"], label_visibility="collapsed")
                if up_file is not None and st.session_state.get("custom_dataset_name") != up_file.name:
                    try:
                        loaded = pd.read_csv(up_file) if up_file.name.endswith(".csv") else pd.read_excel(up_file)
                        st.session_state["custom_df"] = loaded
                        st.session_state["custom_dataset_name"] = up_file.name
                        st.session_state["dataset_source"] = "custom"
                        st.success(f"Loaded {up_file.name} ({len(loaded):,} rows)!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error loading file: {e}")

    # Quick Suggestion Chips
    if user_role == "executive":
        sample_questions = [
            "Which department has the highest number of critical risk students?",
            "What is the average attendance and forecasted GPA across all 5 departments?",
            "How many students have more than 2 course backlogs?",
            "List the top 5 students needing immediate intervention."
        ]
    elif user_role == "faculty":
        dept = current_user.get("department", "Computer Science")
        sample_questions = [
            f"How many students in {dept} have attendance below 75%?",
            f"What is the average internal assessment score in {dept}?",
            f"Show the distribution of risk levels in {dept}.",
            f"Who are the top performers in {dept}?"
        ]
    elif user_role == "student":
        sid = current_user.get("student_id", "EDG-2026-1042")
        sample_questions = [
            f"Give me a detailed evaluation and diagnostic summary for student {sid}.",
            f"What specific actions can student {sid} take to improve their end-term GPA?",
            f"How does student {sid}'s attendance compare to class average?",
            f"What skills and projects should student {sid} add to boost employability?"
        ]
    else:
        sid = current_user.get("student_id", "EDG-2026-1042")
        sample_questions = [
            f"How is my child ({sid}) performing academically?",
            f"Are there any backlogs or critical risk warnings for student {sid}?",
            f"What recommendations should we discuss with the class teacher?",
            f"What are my child's strongest accomplishments this semester?"
        ]
        
    cols = st.columns(len(sample_questions))
    selected_quick_prompt = None
    for idx, q_text in enumerate(sample_questions):
        with cols[idx]:
            if st.button(f"💡 {q_text}", key=f"quick_q_{idx}", use_container_width=True):
                selected_quick_prompt = q_text

    # Clear chat & export buttons
    act_col1, act_col2 = st.columns([6, 1.2])
    with act_col2:
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state["chat_messages"] = [
                {"role": "assistant", "content": f"👋 Conversation cleared! What would you like to analyze about **{active_name}**?", "queries": []}
            ]
            st.rerun()

    # Chat History
    for msg in st.session_state.get("chat_messages", []):
        if msg["role"] == "user":
            with st.chat_message("user"):
                st.markdown(msg["content"])
        else:
            with st.chat_message("assistant", avatar="🎓"):
                st.markdown(msg["content"])
                if msg.get("queries"):
                    with st.expander("🔍 View Verified Pandas Query & Output", expanded=False):
                        for q in msg["queries"]:
                            st.caption("**Executed Query:**")
                            st.code(q["code"], language="python")
                            st.caption("**Result:**")
                            st.code(q["output"], language="text")

    # Chat Input
    user_input = st.chat_input(f"Ask any question about {active_name}...")
    prompt_to_send = selected_quick_prompt or user_input
    
    if prompt_to_send:
        st.session_state["chat_messages"].append({"role": "user", "content": prompt_to_send})
        with st.chat_message("user"):
            st.markdown(prompt_to_send)
            
        with st.chat_message("assistant", avatar="🎓"):
            with st.spinner(f"Analyzing {active_name} with Groq {st.session_state['selected_model']}..."):
                role_ctx = f"Logged in as {current_user['name']} ({current_user.get('role_title', 'User')})."
                res_dict = chatbot.chat(st.session_state["chat_messages"], role_context=role_ctx)
                content = res_dict.get("content", "No response generated.")
                queries = res_dict.get("executed_queries", [])
                st.markdown(content)
                if queries:
                    with st.expander("🔍 View Verified Pandas Query & Output", expanded=False):
                        for q in queries:
                            st.code(q["code"], language="python")
                            st.code(q["output"], language="text")
                            
        st.session_state["chat_messages"].append({"role": "assistant", "content": content, "queries": queries})
        st.rerun()

# ------------------------------------------------------------------------------
# 6. MAIN AUTHENTICATED WINDOW
# ------------------------------------------------------------------------------
def render_authenticated_window(current_user):
    user_role = current_user["role"]
    filter_dept = "All Departments"
    filter_sem = "All Semesters"

    # Sidebar - Clean Session Management
    with st.sidebar:
        st.markdown("### **EduGrowth AI**")
        st.caption("Institutional Active Session")
        
        st.markdown(f"""
        <div style="background-color:#F1F5F9; border-radius:6px; padding:0.75rem 0.9rem; margin-bottom:1rem; border:1px solid #E2E8F0;">
            <div style="font-size:0.88rem; font-weight:700; color:#0F172A;">{current_user['name']}</div>
            <div style="font-size:0.76rem; color:#475569;">{current_user['role_title']}</div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🚪 Log Out", use_container_width=True):
            st.session_state["authenticated"] = False
            st.session_state["user"] = None
            st.rerun()
            
        st.divider()
        
        if user_role == "executive":
            st.markdown("##### **Executive Filters**")
            filter_dept = st.selectbox("Department", ["All Departments"] + sorted(list(df['department'].unique())))
            filter_sem = st.selectbox("Semester", ["All Semesters"] + sorted(list(df['semester'].unique())))
            
        elif user_role == "faculty":
            st.markdown("##### **Assigned Class Scope**")
            st.write(f"**Department:** {current_user['department']}")
            st.write(f"**Semester:** {current_user['semester']}")
            
        elif user_role == "student":
            st.markdown("##### **My Account**")
            st.write(f"**Student ID:** {current_user['student_id']}")
            
        elif user_role == "parent":
            st.markdown("##### **Child Profile**")
            st.write(f"**Student ID:** {current_user['student_id']}")

        st.divider()
        st.markdown("##### **🤖 AI Data Assistant**")
        st.caption(f"Engine: `{st.session_state.get('selected_model', 'openai/gpt-oss-120b')}` (Groq)")
        st.caption("Dynamic Query Execution & Visual Exploration")
        st.divider()
        st.caption("🔒 Verified Institutional Session | Model v1.0")

    # Main Tab Navigation - Clean, Simple & Focused
    tab_dash, tab_sim, tab_adv, tab_chat = st.tabs([
        "📊 Institutional Dashboard",
        "🎯 Performance & Goal Simulator",
        "🧭 Career & Interventions",
        "🤖 AI Data Chatbot (Groq GPT OSS 120B)"
    ])
    
    with tab_dash:
        render_role_dashboard(current_user, filter_dept, filter_sem)
        
    with tab_sim:
        render_simulator_tab(current_user)
        
    with tab_adv:
        render_career_and_interventions_tab(current_user)
        
    with tab_chat:
        render_chatbot_interface(current_user, df)

# ------------------------------------------------------------------------------
# MAIN ROUTER
# ------------------------------------------------------------------------------
if not st.session_state.get("authenticated", False) or not st.session_state.get("user"):
    render_login_portal()
else:
    render_authenticated_window(st.session_state["user"])
