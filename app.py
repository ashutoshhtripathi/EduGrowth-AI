"""
EduGrowth AI - Intelligent Student Success & Retention Monitoring System
Institutional Portal with Secure Role-Based Authentication:
- Executive / Dean: Complete institutional student body analytics
- Faculty / Teacher: Class-level monitoring & academic interventions
- Student: Individual academic trajectory & skills portfolio
- Parent: Child attendance tracking & success monitoring
"""

import os
import sys
import json
import hashlib
import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

# Add src to sys.path
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))
from inference import EduGrowthPredictor
from chatbot import EduGrowthChatbot

# Page Configuration - Clean Light Theme
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

# Enterprise Light Theme Styling
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
    
    /* Metrics */
    .clean-card {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 1.1rem 1.25rem;
        box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.03);
        margin-bottom: 0.8rem;
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

    /* Fix Dark Blocks: Force Inputs to Crisp White Background & Dark Legible Text */
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
    
    /* Input Labels */
    .stTextInput label, 
    div[data-testid="stWidgetLabel"] label, 
    label {
        color: #1E293B !important;
        font-weight: 600 !important;
        font-size: 0.9rem !important;
    }
    
    /* Buttons: Target Streamlit Buttons Only - NEVER Plotly ModeBar Icons */
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
        font-size: 0.95rem !important;
        padding: 0.6rem 1.25rem !important;
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

    /* Reset Plotly ModeBar Icons: Fully Transparent Background & Clear Visible Icons */
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
        background-color: transparent !important;
        border: none !important;
        box-shadow: none !important;
        padding: 4px !important;
        margin: 0 2px !important;
        width: 26px !important;
        height: 26px !important;
        line-height: normal !important;
        border-radius: 4px !important;
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
        cursor: pointer !important;
    }
    
    .js-plotly-plot .plotly .modebar-btn svg,
    .modebar-btn svg {
        fill: #475569 !important;
        width: 16px !important;
        height: 16px !important;
        display: block !important;
        opacity: 0.85 !important;
    }
    
    .js-plotly-plot .plotly .modebar-btn:hover,
    .modebar-btn:hover,
    button.modebar-btn:hover {
        background-color: #F1F5F9 !important;
        border: none !important;
    }
    
    .js-plotly-plot .plotly .modebar-btn:hover svg,
    .modebar-btn:hover svg {
        fill: #1E3A8A !important;
        opacity: 1 !important;
    }
    
    /* Password Eye Icon Visibility */
    div[data-baseweb="input"] svg {
        fill: #64748B !important;
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
    
    /* Chat Input Styling */
    .stChatInputContainer {
        border-radius: 8px !important;
    }
    
    .stChatInput textarea {
        color: #0F172A !important;
        -webkit-text-fill-color: #0F172A !important;
        background-color: #FFFFFF !important;
        font-size: 0.95rem !important;
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
    chatbot = EduGrowthChatbot(df)
    return df, predictor, chatbot

df, predictor, chatbot = load_system()

# User Credentials Database
ACCOUNTS_DB = {
    # 1. Executive
    "dean.vance": {
        "password": "admin",
        "name": "Dr. Eleanor Vance",
        "role": "executive",
        "role_title": "University Dean / Provost",
        "scope": "All University Departments & Cohorts"
    },
    # 2. Faculty
    "prof.sharma": {
        "password": "class",
        "name": "Prof. Arvind Sharma",
        "role": "faculty",
        "role_title": "Class Teacher & Associate Professor",
        "department": "Computer Science",
        "semester": 5
    },
    # 3. Student (Default)
    "student.edg1042": {
        "password": "study",
        "name": "Aarav Patel",
        "role": "student",
        "role_title": "Undergraduate Student",
        "student_id": "EDG-2026-1042"
    },
    # 4. Parent (Default)
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

def render_login_portal():
    """Renders the secure access portal with username & password."""
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
                # Check dynamic Student ID (e.g. EDG-2026-1005 with password 'study')
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
        <div style="margin-top: 1rem; padding-top: 0.75rem; border-top: 1px dashed #CBD5E1; text-align: center;">
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

def render_role_dashboard(current_user, filter_dept="All Departments", filter_sem="All Semesters"):
    """Renders the visual institutional dashboard scoped to the authenticated user's role."""
    user_role = current_user["role"]

    # --------------------------------------------------------------------------
    # 1. EXECUTIVE / DEAN DATA WINDOW
    # --------------------------------------------------------------------------
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
            st.markdown("##### **Attendance Deficit vs Internal Evaluation Correlation**")
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

        st.markdown("##### **High-Priority Student Watchlist (For Academic Council Interventions)**")
        at_risk_df = exec_df[exec_df['academic_risk_level'] == 2][
            ['student_id', 'student_name', 'department', 'semester', 'attendance_rate_pct', 'internal_assessment_score', 'backlog_count', 'target_end_term_gpa']
        ].copy()
        at_risk_df.columns = ['ID', 'Student Name', 'Department', 'Sem', 'Attendance %', 'Internal Score', 'Backlogs', 'Forecasted GPA']
        
        st.dataframe(at_risk_df.head(20), hide_index=True, use_container_width=True, height=280)
        
        csv_bytes = at_risk_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Full Institutional At-Risk Report (.CSV)",
            data=csv_bytes,
            file_name='institutional_at_risk_students.csv',
            mime='text/csv'
        )

    # --------------------------------------------------------------------------
    # 2. FACULTY / PROFESSOR DATA WINDOW
    # --------------------------------------------------------------------------
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
                st.success(f"Tutorial alert sent to {selected_student}.")
            st.markdown("</div>", unsafe_allow_html=True)

    # --------------------------------------------------------------------------
    # 3. STUDENT DATA WINDOW (Self-Service)
    # --------------------------------------------------------------------------
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

        # ----------------------------------------------------------------------
        # Student Passing & Failure Risk Calculator
        # ----------------------------------------------------------------------
        st.write("")
        st.markdown("##### **🎯 Passing & Failure Risk Calculator**")
        st.caption("Adjust your attendance, internal assessment marks, and weekly study hours below to simulate your real-time passing and failure probabilities.")

        st.markdown('<div class="info-panel" style="padding: 1.5rem 1.8rem; margin-top: 0.5rem; margin-bottom: 1.5rem;">', unsafe_allow_html=True)
        
        c_input_col, c_result_col = st.columns([1.1, 1.3], gap="large")
        
        with c_input_col:
            st.markdown("<p style='font-size:0.92rem; font-weight:700; color:#0F172A; margin-bottom:0.75rem;'>⚙️ Adjust Your Performance Parameters:</p>", unsafe_allow_html=True)
            
            calc_attendance = st.slider(
                "Class Attendance Rate (%)",
                min_value=30.0,
                max_value=100.0,
                value=float(s_row['attendance_rate_pct']),
                step=1.0,
                help="Institutional minimum compliance threshold is 75%."
            )
            
            calc_internal = st.slider(
                "Internal Exam Marks (/100)",
                min_value=10.0,
                max_value=100.0,
                value=float(s_row['internal_assessment_score']),
                step=1.0,
                help="Continuous assessment, mid-term, and quiz scores."
            )
            
            calc_study_hours = st.slider(
                "Weekly Study / LMS Hours (hrs/wk)",
                min_value=1.0,
                max_value=35.0,
                value=float(s_row['lms_weekly_hours']),
                step=0.5,
                help="Hours dedicated weekly to studying uploaded course materials."
            )
            
            calc_assignment = st.slider(
                "Assignment Submission Rate (%)",
                min_value=20.0,
                max_value=100.0,
                value=float(s_row['assignment_completion_pct']),
                step=1.0,
                help="Percentage of homework and assignments submitted on schedule."
            )
            
        with c_result_col:
            # Construct feature dictionary reflecting adjusted parameters
            calc_dict = s_row.to_dict()
            calc_dict['attendance_rate_pct'] = calc_attendance
            calc_dict['internal_assessment_score'] = calc_internal
            calc_dict['lms_weekly_hours'] = calc_study_hours
            calc_dict['assignment_completion_pct'] = calc_assignment
            calc_dict['lms_logins_per_week'] = int(calc_study_hours * 1.6)
            
            # Real-time ML inference
            calc_res = predictor.predict_single(calc_dict)
            
            fail_prob = float(calc_res['risk_probabilities']['High Risk'])
            pass_prob = round(100.0 - fail_prob, 1)
            calc_pred_gpa = calc_res['predicted_end_term_gpa']
            
            st.markdown("<p style='font-size:0.92rem; font-weight:700; color:#0F172A; margin-bottom:0.75rem;'>📊 Predicted Academic Outcome:</p>", unsafe_allow_html=True)
            
            # Status Indicator
            if pass_prob >= 80.0:
                status_html = f'<div class="status-pill pill-safe" style="font-size:0.85rem; padding:0.4rem 0.85rem;">🟢 High Passing Probability ({pass_prob}%) • Safe Standing</div>'
            elif pass_prob >= 50.0:
                status_html = f'<div class="status-pill pill-warning" style="font-size:0.85rem; padding:0.4rem 0.85rem;">🟡 Moderate Passing Probability ({pass_prob}%) • Advisory Needed</div>'
            else:
                status_html = f'<div class="status-pill pill-critical" style="font-size:0.85rem; padding:0.4rem 0.85rem;">🔴 High Failure Risk ({fail_prob}%) • Critical Action Required</div>'
            
            st.markdown(status_html, unsafe_allow_html=True)
            st.write("")
            
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
                    <div class="card-detail">Arrear / Probation Risk</div>
                </div>
                """, unsafe_allow_html=True)
            with res_c3:
                st.markdown(f"""
                <div class="clean-card" style="border-top: 3px solid #2563EB; padding:0.85rem 1rem;">
                    <div class="card-label">Forecasted GPA</div>
                    <div class="card-number" style="color:#2563EB; font-size:1.55rem;">{calc_pred_gpa:.2f}</div>
                    <div class="card-detail">Target 10-Pt Benchmark</div>
                </div>
                """, unsafe_allow_html=True)
                
            # Clean Comparison Chart
            prob_chart_df = pd.DataFrame({
                'Outcome': ['Passing Probability', 'Failing Risk'],
                'Probability (%)': [pass_prob, fail_prob]
            })
            fig_calc = px.bar(
                prob_chart_df,
                x='Probability (%)',
                y='Outcome',
                orientation='h',
                color='Outcome',
                color_discrete_map={'Passing Probability': '#16A34A', 'Failing Risk': '#DC2626'},
                text_auto='.1f',
                height=160
            )
            fig_calc = apply_clean_chart_theme(fig_calc, height=160)
            fig_calc.update_layout(
                showlegend=False,
                xaxis=dict(range=[0, 100], showgrid=True, gridcolor="#F1F5F9"),
                yaxis=dict(title=None),
                margin=dict(l=10, r=10, t=10, b=10)
            )
            st.plotly_chart(fig_calc, use_container_width=True)
            
            # Actionable Feedback
            if calc_attendance < 75.0:
                st.warning(f"⚠️ **Attendance Alert:** Your simulated attendance ({calc_attendance:.0f}%) is below the university threshold (75%). Raising it above 75% will dramatically lower your failure probability.")
            elif calc_internal < 50.0:
                st.warning(f"⚠️ **Internal Marks Advisory:** Internal score ({calc_internal:.0f}/100) is low. Scoring 60+ on subsequent quizzes/tests creates a comfortable buffer.")
            elif calc_study_hours < 5.0:
                st.info(f"💡 **Study Habit:** Increasing study time from {calc_study_hours:.1f} to 8+ hrs/week significantly boosts predicted GPA.")
            else:
                st.success("✅ **Optimal Trajectory:** With this combination of attendance, internals, and study hours, you have a strong buffer and high probability of passing with distinction!")
                
        st.markdown('</div>', unsafe_allow_html=True)

    # --------------------------------------------------------------------------
    # 4. PARENT / GUARDIAN DATA WINDOW
    # --------------------------------------------------------------------------
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
            st.markdown("##### **Academic Challenges & Areas Needing Support**")
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

# ==============================================================================
# AI DATA CHATBOT INTERFACE (GROQ OPENAI/GPT-OSS-120B)
# ==============================================================================
def render_chatbot_interface(current_user, chatbot, df):
    """Interactive conversational analytics engine powered by Groq openai/gpt-oss-120b."""
    user_role = current_user.get("role", "guest")
    
    # Header Banner
    st.markdown("""
    <div style="background: linear-gradient(135deg, #1E3A8A 0%, #1E40AF 50%, #2563EB 100%); border-radius: 10px; padding: 1.25rem 1.5rem; color: #FFFFFF; margin-bottom: 1.2rem; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.08);">
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">
            <div>
                <h3 style="margin: 0; color: #FFFFFF; font-weight: 700; font-size: 1.35rem;">💬 EduGrowth AI Data Assistant</h3>
                <p style="margin: 0.35rem 0 0 0; color: #DBEAFE; font-size: 0.88rem;">
                    Ask questions about academic cohorts, risk indicators, attendance, test scores, or individual student trajectories.
                </p>
            </div>
            <div style="display: flex; gap: 8px;">
                <span style="background-color: rgba(255,255,255,0.18); border: 1px solid rgba(255,255,255,0.3); border-radius: 6px; padding: 0.35rem 0.65rem; font-size: 0.78rem; font-weight: 600;">
                    ⚡ Groq: openai/gpt-oss-120b
                </span>
                <span style="background-color: rgba(255,255,255,0.18); border: 1px solid rgba(255,255,255,0.3); border-radius: 6px; padding: 0.35rem 0.65rem; font-size: 0.78rem; font-weight: 600;">
                    📊 3,000 Verified Students
                </span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Suggestion Chips by Role
    st.markdown("##### **⚡ Quick Analytics Questions**")
    if user_role == "executive":
        sample_questions = [
            "Which department has the highest number of critical risk students?",
            "What is the average attendance and forecasted GPA across all 5 departments?",
            "How many students have more than 2 course backlogs?",
            "List the top 5 students needing immediate intervention with their IDs and departments."
        ]
    elif user_role == "faculty":
        dept = current_user.get("department", "Computer Science")
        sem = current_user.get("semester", 5)
        sample_questions = [
            f"How many students in {dept} Semester {sem} have attendance below 75%?",
            f"What is the average internal assessment score and backlog count in {dept}?",
            f"Show the distribution of risk levels in {dept} Semester {sem}.",
            f"Who are the top performers in {dept} with highest practical portfolio scores?"
        ]
    elif user_role == "student":
        sid = current_user.get("student_id", "EDG-2026-1042")
        sample_questions = [
            f"Give me a detailed evaluation and diagnostic summary for student {sid}.",
            f"What specific actions can student {sid} take to improve their end-term GPA?",
            f"How does student {sid}'s attendance and internal score compare to class average?",
            f"What skills and projects should student {sid} add to boost employability?"
        ]
    else: # Parent
        sid = current_user.get("student_id", "EDG-2026-1042")
        sample_questions = [
            f"How is my child ({sid}) performing academically and what is their attendance?",
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

    # Action row (Clear chat)
    act_col1, act_col2 = st.columns([6, 1])
    with act_col2:
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state["chat_messages"] = [
                {
                    "role": "assistant",
                    "content": "👋 Conversation cleared! What would you like to analyze about the student cohort data?",
                    "queries": []
                }
            ]
            st.rerun()

    st.markdown("---")
    
    # Render Chat History
    for msg in st.session_state.get("chat_messages", []):
        if msg["role"] == "user":
            with st.chat_message("user"):
                st.markdown(msg["content"])
        else:
            with st.chat_message("assistant", avatar="🎓"):
                st.markdown(msg["content"])
                if msg.get("queries"):
                    with st.expander("🔍 View Verified Pandas Query & Dataset Output", expanded=False):
                        for q in msg["queries"]:
                            st.caption("**Executed Query (Python):**")
                            st.code(q["code"], language="python")
                            st.caption("**Computed Dataset Result:**")
                            st.code(q["output"], language="text")

    # Chat Input Handling
    user_input = st.chat_input("Ask any question about students, grades, attendance, risk factors, or departments...")
    prompt_to_send = selected_quick_prompt or user_input
    
    if prompt_to_send:
        # Add user message
        st.session_state["chat_messages"].append({
            "role": "user",
            "content": prompt_to_send
        })
        
        # Display immediately
        with st.chat_message("user"):
            st.markdown(prompt_to_send)
            
        with st.chat_message("assistant", avatar="🎓"):
            with st.spinner("Analyzing institutional dataset with Groq openai/gpt-oss-120b..."):
                # Prepare role context
                if user_role == "executive":
                    role_ctx = f"Logged in as {current_user['name']} ({current_user['role_title']}). Access level: Complete institutional portfolio (all 3,000 students)."
                elif user_role == "faculty":
                    role_ctx = f"Logged in as {current_user['name']} ({current_user['role_title']}). Assigned Department: {current_user['department']}, Semester: {current_user['semester']}."
                elif user_role == "student":
                    role_ctx = f"Logged in as {current_user['name']} (Student ID: {current_user['student_id']})."
                elif user_role == "parent":
                    role_ctx = f"Logged in as {current_user['name']} (Guardian of Student ID: {current_user['student_id']})."
                else:
                    role_ctx = f"Logged in as {current_user.get('name', 'User')}."
                    
                response_dict = chatbot.chat(
                    messages=st.session_state["chat_messages"],
                    role_context=role_ctx
                )
                
                content = response_dict.get("content", "No response generated.")
                queries = response_dict.get("executed_queries", [])
                
                st.markdown(content)
                if queries:
                    with st.expander("🔍 View Verified Pandas Query & Dataset Output", expanded=False):
                        for q in queries:
                            st.caption("**Executed Query (Python):**")
                            st.code(q["code"], language="python")
                            st.caption("**Computed Dataset Result:**")
                            st.code(q["output"], language="text")
                            
        st.session_state["chat_messages"].append({
            "role": "assistant",
            "content": content,
            "queries": queries
        })
        st.rerun()

# ==============================================================================
# AUTHENTICATED PORTAL WINDOW
# ==============================================================================
def render_authenticated_window(current_user):
    """Renders top navigation tabs: Institutional Dashboard & AI Data Chatbot."""
    user_role = current_user["role"]
    filter_dept = "All Departments"
    filter_sem = "All Semesters"

    # Sidebar - Session Management
    with st.sidebar:
        st.markdown("### **EduGrowth AI**")
        st.caption("Active Session")
        
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
        st.caption("Engine: `openai/gpt-oss-120b` (Groq)")
        st.caption("Live Pandas Execution on 3,000 Students")
        st.divider()
        st.caption("🔒 Verified Institutional Session | Model v1.0")

    # Main Tab Router
    tab_dash, tab_chat = st.tabs(["📊 Institutional Dashboard", "🤖 AI Data Chatbot (Groq GPT OSS 120B)"])
    
    with tab_dash:
        render_role_dashboard(current_user, filter_dept, filter_sem)
        
    with tab_chat:
        render_chatbot_interface(current_user, chatbot, df)

# ==============================================================================
# MAIN ROUTER
# ==============================================================================
if not st.session_state.get("authenticated", False) or not st.session_state.get("user"):
    render_login_portal()
else:
    render_authenticated_window(st.session_state["user"])
