"""
Modern SaaS Design System, Role-Aware Theming, Safe HTML Rendering & Plotly Helpers.
"""

import streamlit as st
import plotly.graph_objects as go

COLOR_SAFE = "#10B981"
COLOR_WARNING = "#F59E0B"
COLOR_CRITICAL = "#EF4444"
COLOR_PRIMARY = "#2563EB"

ROLE_THEMES = {
    "executive": {
        "primary": "#1E3A8A",
        "primary_hover": "#1D4ED8",
        "secondary": "#3B82F6",
        "gradient": "linear-gradient(135deg, #0F172A 0%, #1E3A8A 60%, #2563EB 100%)",
        "soft_bg": "#EFF6FF",
        "soft_border": "#BFDBFE",
        "soft_text": "#1E40AF",
        "icon": "🏛️",
        "short_code": "EG",
        "portal_name": "Leadership",
        "avatar": "🏛️",
    },
    "faculty": {
        "primary": "#0F766E",
        "primary_hover": "#0D9488",
        "secondary": "#14B8A6",
        "gradient": "linear-gradient(135deg, #042F2E 0%, #0F766E 60%, #0D9488 100%)",
        "soft_bg": "#F0FDFA",
        "soft_border": "#99F6E4",
        "soft_text": "#115E59",
        "icon": "👨‍🏫",
        "short_code": "EG",
        "portal_name": "Teacher",
        "avatar": "👨‍🏫",
    },
    "student": {
        "primary": "#4F46E5",
        "primary_hover": "#4338CA",
        "secondary": "#818CF8",
        "gradient": "linear-gradient(135deg, #1E1B4B 0%, #4338CA 60%, #6366F1 100%)",
        "soft_bg": "#EEF2FF",
        "soft_border": "#C7D2FE",
        "soft_text": "#3730A3",
        "icon": "🎓",
        "short_code": "EG",
        "portal_name": "Student",
        "avatar": "🎓",
    },
    "parent": {
        "primary": "#0284C7",
        "primary_hover": "#0369A1",
        "secondary": "#38BDF8",
        "gradient": "linear-gradient(135deg, #082F49 0%, #0369A1 60%, #0EA5E9 100%)",
        "soft_bg": "#F0F9FF",
        "soft_border": "#BAE6FD",
        "soft_text": "#075985",
        "icon": "👨‍👩‍👧",
        "short_code": "EG",
        "portal_name": "Parent",
        "avatar": "🏡",
    },
    "default": {
        "primary": "#1E3A8A",
        "primary_hover": "#2563EB",
        "secondary": "#3B82F6",
        "gradient": "linear-gradient(135deg, #0F172A 0%, #1E3A8A 60%, #2563EB 100%)",
        "soft_bg": "#EFF6FF",
        "soft_border": "#DBEAFE",
        "soft_text": "#1E40AF",
        "icon": "🎓",
        "short_code": "EG",
        "portal_name": "EduGrowth AI",
        "avatar": "🎓",
    },
}


def get_role_theme(role: str) -> dict:
    return ROLE_THEMES.get(role, ROLE_THEMES["default"])


def render_html(html: str):
    """Renders HTML safely in Streamlit without CommonMark 4-space code-block glitches."""
    cleaned = "\n".join(line.strip() for line in html.splitlines() if line.strip())
    st.markdown(cleaned, unsafe_allow_html=True)


def inject_global_css(role: str = "default", hide_sidebar: bool = False):
    theme = get_role_theme(role)
    primary = theme["primary"]
    primary_hover = theme["primary_hover"]
    soft_bg = theme["soft_bg"]
    soft_border = theme["soft_border"]
    soft_text = theme["soft_text"]

    sidebar_hide_css = (
        "div[data-testid='stSidebar'], button[data-testid='collapsedControl'] { display: none !important; }"
        if hide_sidebar
        else ""
    )

    css = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Plus+Jakarta+Sans:wght@600;700;800&display=swap');

html, body, [class*="css"], .stApp {{
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    background: linear-gradient(180deg, #F8FAFC 0%, #F1F5F9 100%) !important;
    color: #0F172A !important;
}}

h1, h2, h3, h4, .hero-title {{
    font-family: 'Plus Jakarta Sans', 'Inter', sans-serif;
}}

.main .block-container {{
    padding-top: 1.35rem;
    padding-bottom: 3rem;
    max-width: 1380px;
}}

{sidebar_hide_css}

/* Architectural Clean Sidebar */
div[data-testid="stSidebar"] {{
    background-color: #FFFFFF !important;
    border-right: 1px solid #E2E8F0 !important;
}}
div[data-testid="stSidebar"] > div:first-child {{
    padding-top: 1.15rem !important;
}}

/* Native Bordered Containers (Login Card & Surface Panels) */
div[data-testid="stVerticalBlockBorderWrapper"] {{
    background-color: #FFFFFF !important;
    border: 1px solid #E2E8F0 !important;
    border-radius: 16px !important;
    box-shadow: 0 10px 30px -12px rgba(15, 23, 42, 0.08) !important;
    padding: 0.35rem 0.45rem !important;
}}

/* Hero Banner */
.hero-banner {{
    background: {theme["gradient"]};
    border-radius: 16px;
    padding: 1.5rem 1.8rem;
    color: #FFFFFF;
    margin-bottom: 1.25rem;
    box-shadow: 0 14px 28px -10px rgba(15, 23, 42, 0.2);
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 1rem;
    position: relative;
    overflow: hidden;
}}
.hero-banner::after {{
    content: "";
    position: absolute;
    right: -35px;
    top: -35px;
    width: 160px;
    height: 160px;
    border-radius: 50%;
    background: rgba(255, 255, 255, 0.07);
    pointer-events: none;
}}
.hero-title {{
    font-size: 1.48rem;
    font-weight: 800;
    color: #FFFFFF;
    margin: 0;
    letter-spacing: -0.02em;
}}
.hero-subtitle {{
    font-size: 0.89rem;
    color: rgba(255, 255, 255, 0.86);
    margin-top: 0.3rem;
}}
.hero-pills {{
    display: flex;
    gap: 0.5rem;
    flex-wrap: wrap;
    align-items: center;
    z-index: 1;
}}
.hero-badge {{
    background: rgba(255, 255, 255, 0.16);
    border: 1px solid rgba(255, 255, 255, 0.28);
    backdrop-filter: blur(8px);
    color: #FFFFFF;
    padding: 0.38rem 0.85rem;
    border-radius: 999px;
    font-size: 0.78rem;
    font-weight: 600;
}}

/* Rich KPI Cards */
.kpi-card {{
    background-color: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 14px;
    padding: 1.1rem 1.2rem;
    box-shadow: 0 4px 14px -6px rgba(15, 23, 42, 0.06);
    margin-bottom: 0.75rem;
    transition: transform 0.16s ease, box-shadow 0.16s ease;
    height: 100%;
}}
.kpi-card:hover {{
    transform: translateY(-2px);
    box-shadow: 0 12px 22px -8px rgba(15, 23, 42, 0.11);
}}
.kpi-head {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.5rem;
}}
.kpi-label {{
    font-size: 0.73rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: #64748B;
}}
.kpi-icon-badge {{
    width: 28px;
    height: 28px;
    border-radius: 8px;
    background: {soft_bg};
    border: 1px solid {soft_border};
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.9rem;
}}
.kpi-value {{
    font-size: 1.72rem;
    font-weight: 800;
    color: #0F172A;
    line-height: 1.1;
    letter-spacing: -0.025em;
}}
.kpi-detail {{
    font-size: 0.79rem;
    color: #64748B;
    margin-top: 0.4rem;
}}
.progress-track {{
    width: 100%;
    height: 5px;
    background-color: #E2E8F0;
    border-radius: 999px;
    margin-top: 0.55rem;
    overflow: hidden;
}}
.progress-fill {{
    height: 100%;
    border-radius: 999px;
}}
.kpi-delta-pos {{
    display: inline-block;
    background-color: #DCFCE7;
    color: #166534;
    font-size: 0.71rem;
    font-weight: 700;
    padding: 0.12rem 0.45rem;
    border-radius: 999px;
    margin-left: 0.35rem;
    vertical-align: middle;
}}
.kpi-delta-neg {{
    display: inline-block;
    background-color: #FEE2E2;
    color: #991B1B;
    font-size: 0.71rem;
    font-weight: 700;
    padding: 0.12rem 0.45rem;
    border-radius: 999px;
    margin-left: 0.35rem;
    vertical-align: middle;
}}

/* Surface Panels */
.surface-panel {{
    background-color: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 14px;
    padding: 1.2rem 1.35rem;
    box-shadow: 0 4px 12px -6px rgba(15, 23, 42, 0.05);
    margin-bottom: 1rem;
}}
.panel-title {{
    font-size: 0.95rem;
    font-weight: 700;
    color: #0F172A;
    margin-bottom: 0.75rem;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid #F1F5F9;
}}

/* Person Card */
.person-card {{
    background: linear-gradient(135deg, #FFFFFF 0%, {soft_bg} 100%);
    border: 1px solid {soft_border};
    border-radius: 14px;
    padding: 1.05rem 1.3rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 1rem;
    margin-bottom: 1rem;
}}
.avatar-circle {{
    width: 44px;
    height: 44px;
    border-radius: 50%;
    background: {theme["gradient"]};
    color: #FFFFFF;
    font-weight: 800;
    font-size: 0.98rem;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 4px 10px rgba(15, 23, 42, 0.14);
    flex-shrink: 0;
}}

/* Callouts & Tags */
.callout-card {{
    background-color: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-left: 3.5px solid {primary};
    border-radius: 10px;
    padding: 0.8rem 0.95rem;
    margin-bottom: 0.55rem;
    font-size: 0.86rem;
    color: #1E293B;
}}
.tag-pill {{
    display: inline-block;
    background: {soft_bg};
    color: {soft_text};
    border: 1px solid {soft_border};
    border-radius: 999px;
    padding: 0.2rem 0.62rem;
    font-size: 0.73rem;
    font-weight: 600;
    margin: 0.15rem 0.22rem 0.15rem 0;
}}

/* Status Pills */
.status-pill {{
    padding: 0.32rem 0.8rem;
    border-radius: 999px;
    font-size: 0.77rem;
    font-weight: 700;
    display: inline-block;
}}
.pill-safe {{ background-color: #ECFDF5; color: #065F46; border: 1px solid #A7F3D0; }}
.pill-warning {{ background-color: #FFFBEB; color: #92400E; border: 1px solid #FDE68A; }}
.pill-critical {{ background-color: #FEF2F2; color: #991B1B; border: 1px solid #FECACA; }}

/* Inputs */
div[data-baseweb="input"],
div[data-baseweb="base-input"],
.stTextInput input,
input[type="text"],
input[type="password"] {{
    background-color: #FFFFFF !important;
    color: #0F172A !important;
    -webkit-text-fill-color: #0F172A !important;
    border-radius: 9px !important;
}}
.stTextInput > div > div {{
    border: 1px solid #CBD5E1 !important;
    border-radius: 9px !important;
    background-color: #FFFFFF !important;
}}
input::placeholder {{
    color: #94A3B8 !important;
    -webkit-text-fill-color: #94A3B8 !important;
}}
.stTextInput label,
div[data-testid="stWidgetLabel"] label {{
    color: #334155 !important;
    font-weight: 600 !important;
    font-size: 0.85rem !important;
}}

/* Primary Buttons */
.stButton > button,
button[kind="primary"],
button[kind="secondaryFormSubmit"] {{
    background: {primary} !important;
    color: #FFFFFF !important;
    -webkit-text-fill-color: #FFFFFF !important;
    border: 1px solid {primary} !important;
    border-radius: 9px !important;
    font-weight: 600 !important;
    font-size: 0.87rem !important;
    padding: 0.5rem 1rem !important;
    box-shadow: 0 2px 6px rgba(15, 23, 42, 0.1) !important;
    transition: all 0.15s ease !important;
}}
.stButton > button p,
.stButton > button span {{
    color: #FFFFFF !important;
    -webkit-text-fill-color: #FFFFFF !important;
}}
.stButton > button:hover,
button[kind="primary"]:hover,
button[kind="secondaryFormSubmit"]:hover {{
    background: {primary_hover} !important;
    border-color: {primary_hover} !important;
}}

/* Secondary Buttons */
button[kind="secondary"] {{
    background: #FFFFFF !important;
    color: #334155 !important;
    -webkit-text-fill-color: #334155 !important;
    border: 1px solid #E2E8F0 !important;
    border-radius: 9px !important;
    font-weight: 600 !important;
    box-shadow: none !important;
}}
button[kind="secondary"] p,
button[kind="secondary"] span {{
    color: #334155 !important;
    -webkit-text-fill-color: #334155 !important;
}}
button[kind="secondary"]:hover {{
    background: #F8FAFC !important;
    border-color: #CBD5E1 !important;
    color: #0F172A !important;
    -webkit-text-fill-color: #0F172A !important;
}}
button[kind="secondary"]:hover p,
button[kind="secondary"]:hover span {{
    color: #0F172A !important;
    -webkit-text-fill-color: #0F172A !important;
}}

/* Refined Executive Sidebar Navigation Items */
div[data-testid="stSidebar"] .stButton > button {{
    justify-content: flex-start !important;
    text-align: left !important;
    padding: 0.48rem 0.78rem !important;
    font-size: 0.85rem !important;
    border-radius: 8px !important;
    box-shadow: none !important;
}}
div[data-testid="stSidebar"] button[kind="primary"] {{
    background: {soft_bg} !important;
    color: {primary} !important;
    -webkit-text-fill-color: {primary} !important;
    border: 1px solid {soft_border} !important;
    border-left: 3.5px solid {primary} !important;
    font-weight: 700 !important;
}}
div[data-testid="stSidebar"] button[kind="primary"] p,
div[data-testid="stSidebar"] button[kind="primary"] span {{
    color: {primary} !important;
    -webkit-text-fill-color: {primary} !important;
}}
div[data-testid="stSidebar"] button[kind="secondary"] {{
    background: transparent !important;
    border: 1px solid transparent !important;
    color: #475569 !important;
    -webkit-text-fill-color: #475569 !important;
    font-weight: 500 !important;
}}
div[data-testid="stSidebar"] button[kind="secondary"] p,
div[data-testid="stSidebar"] button[kind="secondary"] span {{
    color: #475569 !important;
    -webkit-text-fill-color: #475569 !important;
}}
div[data-testid="stSidebar"] button[kind="secondary"]:hover {{
    background: #F1F5F9 !important;
    color: #0F172A !important;
    -webkit-text-fill-color: #0F172A !important;
}}
div[data-testid="stSidebar"] button[kind="secondary"]:hover p,
div[data-testid="stSidebar"] button[kind="secondary"]:hover span {{
    color: #0F172A !important;
    -webkit-text-fill-color: #0F172A !important;
}}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {{
    gap: 6px;
    background-color: #F1F5F9;
    padding: 4px;
    border-radius: 10px;
    border: 1px solid #E2E8F0;
    margin-bottom: 1rem;
}}
.stTabs [data-baseweb="tab"] {{
    border-radius: 8px;
    padding: 6px 15px;
    font-weight: 600;
    font-size: 0.86rem;
    color: #475569 !important;
    background-color: transparent !important;
    border: none !important;
}}
.stTabs [aria-selected="true"] {{
    background-color: #FFFFFF !important;
    color: {primary} !important;
    box-shadow: 0 1px 4px rgba(15, 23, 42, 0.08) !important;
}}

/* Reset Plotly Modebar */
.js-plotly-plot .plotly .modebar-container,
.modebar-container {{
    top: 4px !important;
    right: 8px !important;
    background: transparent !important;
}}
.js-plotly-plot .plotly .modebar-btn,
.modebar-btn,
.modebar-group button {{
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
}}
.js-plotly-plot .plotly .modebar-btn svg,
.modebar-btn svg {{
    fill: #64748B !important;
    width: 15px !important;
    height: 15px !important;
}}

/* Chat Bubbles */
div[data-testid="stChatMessage"] {{
    background-color: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 14px;
    padding: 0.95rem 1.15rem;
    margin-bottom: 0.7rem;
    box-shadow: 0 3px 10px -5px rgba(15, 23, 42, 0.06);
}}
</style>
"""
    st.markdown(css, unsafe_allow_html=True)


def render_hero_header(title: str, subtitle: str, badge_text: str = "", role: str = "default", extra_pill: str = None):
    pills = []
    if extra_pill:
        pills.append(f'<span class="hero-badge">{extra_pill}</span>')
    if badge_text:
        pills.append(f'<span class="hero-badge">{badge_text}</span>')
    pills_html = f'<div class="hero-pills">{"".join(pills)}</div>' if pills else ""

    render_html(
        f"""
        <div class="hero-banner">
        <div>
        <h2 class="hero-title">{title}</h2>
        <div class="hero-subtitle">{subtitle}</div>
        </div>
        {pills_html}
        </div>
        """
    )


def render_kpi_card(
    label: str,
    value: str,
    detail: str = "",
    accent_color: str = None,
    delta_text: str = None,
    delta_positive: bool = True,
    icon: str = None,
    progress_pct: float = None,
):
    border_style = f"border-top: 3px solid {accent_color};" if accent_color else ""
    delta_html = ""
    if delta_text:
        cls = "kpi-delta-pos" if delta_positive else "kpi-delta-neg"
        delta_html = f'<span class="{cls}">{delta_text}</span>'

    icon_html = f'<div class="kpi-icon-badge">{icon}</div>' if icon else ""
    bar_color = accent_color or COLOR_PRIMARY
    progress_html = ""
    if progress_pct is not None:
        clamped = max(0.0, min(100.0, float(progress_pct)))
        progress_html = f'<div class="progress-track"><div class="progress-fill" style="width:{clamped:.1f}%; background:{bar_color};"></div></div>'

    render_html(
        f"""
        <div class="kpi-card" style="{border_style}">
        <div class="kpi-head">
        <div class="kpi-label">{label}</div>
        {icon_html}
        </div>
        <div class="kpi-value">{value}{delta_html}</div>
        {progress_html}
        <div class="kpi-detail">{detail}</div>
        </div>
        """
    )


def render_person_card(name: str, subtitle: str, badge_text: str, badge_kind: str = "safe", right_note: str = ""):
    initials = "".join(part[0].upper() for part in name.split()[:2]) or "ST"
    pill_cls = f"pill-{badge_kind}"
    render_html(
        f"""
        <div class="person-card">
        <div style="display:flex; align-items:center; gap:12px;">
        <div class="avatar-circle">{initials}</div>
        <div>
        <div style="font-size:1.02rem; font-weight:800; color:#0F172A;">{name}</div>
        <div style="font-size:0.82rem; color:#475569;">{subtitle}</div>
        </div>
        </div>
        <div style="display:flex; align-items:center; gap:10px; flex-wrap:wrap;">
        <span style="font-size:0.82rem; color:#475569; font-weight:600;">{right_note}</span>
        <span class="status-pill {pill_cls}">{badge_text}</span>
        </div>
        </div>
        """
    )


def apply_clean_chart_theme(fig, height: int = 320):
    fig.update_layout(
        font=dict(family="Inter, sans-serif", size=12, color="#334155"),
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF",
        margin=dict(l=20, r=20, t=34, b=24),
        height=height,
        hoverlabel=dict(bgcolor="#0F172A", font_color="#FFFFFF", font_size=12),
    )
    fig.update_xaxes(showgrid=True, gridcolor="#F1F5F9", zeroline=False)
    fig.update_yaxes(showgrid=True, gridcolor="#F1F5F9", zeroline=False)
    return fig


def build_student_radar_chart(
    student_row,
    benchmark_series,
    student_label: str = "Student",
    benchmark_label: str = "Class Average",
    accent_color: str = "#4F46E5",
    height: int = 310,
):
    categories = [
        "Attendance",
        "Exam Scores",
        "Homework On Time",
        "Study Hours",
        "Job Readiness",
    ]

    def _norm_study(hrs):
        return min(100.0, float(hrs) / 25.0 * 100.0)

    s_vals = [
        float(student_row["attendance_rate_pct"]),
        float(student_row["internal_assessment_score"]),
        float(student_row["assignment_completion_pct"]),
        _norm_study(student_row["lms_weekly_hours"]),
        float(student_row["employability_index"]),
    ]
    b_vals = [
        float(benchmark_series["attendance_rate_pct"]),
        float(benchmark_series["internal_assessment_score"]),
        float(benchmark_series["assignment_completion_pct"]),
        _norm_study(benchmark_series["lms_weekly_hours"]),
        float(benchmark_series["employability_index"]),
    ]

    def _hex_to_rgba(hex_color: str, alpha: float = 0.2) -> str:
        h = hex_color.lstrip("#")
        if len(h) == 6:
            r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
            return f"rgba({r}, {g}, {b}, {alpha})"
        return f"rgba(37, 99, 235, {alpha})"

    fig = go.Figure()
    fig.add_trace(
        go.Scatterpolar(
            r=b_vals + [b_vals[0]],
            theta=categories + [categories[0]],
            fill="toself",
            name=benchmark_label,
            line=dict(color="#94A3B8", width=2, dash="dot"),
            fillcolor="rgba(148, 163, 184, 0.14)",
        )
    )
    fig.add_trace(
        go.Scatterpolar(
            r=s_vals + [s_vals[0]],
            theta=categories + [categories[0]],
            fill="toself",
            name=student_label,
            line=dict(color=accent_color, width=2.5),
            fillcolor=_hex_to_rgba(accent_color, 0.2),
        )
    )
    fig.update_layout(
        polar=dict(
            bgcolor="#FFFFFF",
            radialaxis=dict(visible=True, range=[0, 100], gridcolor="#E2E8F0", tickfont=dict(size=10)),
            angularaxis=dict(gridcolor="#E2E8F0", tickfont=dict(size=11, color="#334155")),
        ),
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.06, xanchor="center", x=0.5),
        margin=dict(l=42, r=42, t=42, b=24),
        paper_bgcolor="#FFFFFF",
        height=height,
        font=dict(family="Inter, sans-serif", size=12, color="#334155"),
    )
    return fig
