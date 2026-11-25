"""
Modern SaaS Design System, Full Dark/Light Mode, Role-Aware Theming, Minimal SVG Logo & Plotly Helpers.
"""

import os
import streamlit as st
import plotly.graph_objects as go

COLOR_SAFE = "#10B981"
COLOR_WARNING = "#F59E0B"
COLOR_CRITICAL = "#EF4444"
COLOR_PRIMARY = "#3B82F6"
COLOR_GOLD = "#F5C451"

ROLE_THEMES = {
    "executive": {
        "primary": "#2563EB",
        "primary_light": "#60A5FA",
        "primary_hover": "#1D4ED8",
        "secondary": "#3B82F6",
        "gradient": "linear-gradient(135deg, #091128 0%, #1E3A8A 60%, #2563EB 100%)",
        "soft_bg": "#EFF6FF",
        "soft_border": "#BFDBFE",
        "soft_text": "#1E40AF",
        "dark_soft_bg": "rgba(37, 99, 235, 0.16)",
        "dark_soft_border": "rgba(96, 165, 250, 0.34)",
        "dark_soft_text": "#93C5FD",
        "icon": "🏛️",
        "portal_name": "Leadership",
        "avatar": "🏛️",
    },
    "faculty": {
        "primary": "#0F766E",
        "primary_light": "#2DD4BF",
        "primary_hover": "#0D9488",
        "secondary": "#14B8A6",
        "gradient": "linear-gradient(135deg, #042F2E 0%, #0F766E 60%, #0D9488 100%)",
        "soft_bg": "#F0FDFA",
        "soft_border": "#99F6E4",
        "soft_text": "#115E59",
        "dark_soft_bg": "rgba(20, 184, 166, 0.16)",
        "dark_soft_border": "rgba(45, 212, 191, 0.34)",
        "dark_soft_text": "#5EEAD4",
        "icon": "👨‍🏫",
        "portal_name": "Teacher",
        "avatar": "👨‍🏫",
    },
    "student": {
        "primary": "#4F46E5",
        "primary_light": "#818CF8",
        "primary_hover": "#4338CA",
        "secondary": "#818CF8",
        "gradient": "linear-gradient(135deg, #1E1B4B 0%, #4338CA 60%, #6366F1 100%)",
        "soft_bg": "#EEF2FF",
        "soft_border": "#C7D2FE",
        "soft_text": "#3730A3",
        "dark_soft_bg": "rgba(99, 102, 241, 0.18)",
        "dark_soft_border": "rgba(129, 140, 248, 0.36)",
        "dark_soft_text": "#A5B4FC",
        "icon": "🎓",
        "portal_name": "Student",
        "avatar": "🎓",
    },
    "parent": {
        "primary": "#0284C7",
        "primary_light": "#38BDF8",
        "primary_hover": "#0369A1",
        "secondary": "#38BDF8",
        "gradient": "linear-gradient(135deg, #082F49 0%, #0369A1 60%, #0EA5E9 100%)",
        "soft_bg": "#F0F9FF",
        "soft_border": "#BAE6FD",
        "soft_text": "#075985",
        "dark_soft_bg": "rgba(14, 165, 233, 0.16)",
        "dark_soft_border": "rgba(56, 189, 248, 0.34)",
        "dark_soft_text": "#7DD3FC",
        "icon": "👨‍👩‍👧",
        "portal_name": "Parent",
        "avatar": "🏡",
    },
    "default": {
        "primary": "#2563EB",
        "primary_light": "#60A5FA",
        "primary_hover": "#1D4ED8",
        "secondary": "#3B82F6",
        "gradient": "linear-gradient(135deg, #091128 0%, #1E3A8A 60%, #2563EB 100%)",
        "soft_bg": "#EFF6FF",
        "soft_border": "#DBEAFE",
        "soft_text": "#1E40AF",
        "dark_soft_bg": "rgba(37, 99, 235, 0.16)",
        "dark_soft_border": "rgba(96, 165, 250, 0.34)",
        "dark_soft_text": "#93C5FD",
        "icon": "🎓",
        "portal_name": "EduGrowth AI",
        "avatar": "🎓",
    },
}


def get_role_theme(role: str) -> dict:
    return ROLE_THEMES.get(role, ROLE_THEMES["default"])


def is_dark_mode() -> bool:
    return bool(st.session_state.get("dark_mode", True))


def get_logo_svg(size: int = 44) -> str:
    """Returns an ultra-minimal, classic transparent geometric growth crest SVG."""
    return (
        f'<svg width="{size}" height="{size}" viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg">'
        '<defs>'
        '<linearGradient id="egM1" x1="8" y1="36" x2="36" y2="10" gradientUnits="userSpaceOnUse">'
        '<stop offset="0%" stop-color="#2563EB"/><stop offset="100%" stop-color="#38BDF8"/>'
        '</linearGradient>'
        '<linearGradient id="egM2" x1="16" y1="40" x2="40" y2="16" gradientUnits="userSpaceOnUse">'
        '<stop offset="0%" stop-color="#D97706"/><stop offset="100%" stop-color="#FDE68A"/>'
        '</linearGradient>'
        '</defs>'
        '<path d="M10 31.5C10 21.8 17.8 14 27.5 14H33" stroke="url(#egM1)" stroke-width="4.2" stroke-linecap="round"/>'
        '<path d="M15 36C21 36 28.5 31.5 33.5 23.5" stroke="url(#egM2)" stroke-width="4.2" stroke-linecap="round"/>'
        '<circle cx="36.5" cy="14" r="3.2" fill="#F5C451"/>'
        '</svg>'
    )


def render_html(html: str):
    """Renders HTML safely in Streamlit without CommonMark 4-space code-block glitches."""
    cleaned = "\n".join(line.strip() for line in html.splitlines() if line.strip())
    st.markdown(cleaned, unsafe_allow_html=True)


def inject_global_css(role: str = "default", hide_sidebar: bool = False, login_glass: bool = False):
    dark = is_dark_mode()
    theme = get_role_theme(role)
    primary = theme["primary_light"] if dark else theme["primary"]
    btn_primary = theme["primary"]
    primary_hover = theme["primary_hover"]
    soft_bg = theme["dark_soft_bg"] if dark else theme["soft_bg"]
    soft_border = theme["dark_soft_border"] if dark else theme["soft_border"]
    soft_text = theme["dark_soft_text"] if dark else theme["soft_text"]

    if dark:
        app_bg = (
            "radial-gradient(at 88% 8%, rgba(37, 99, 235, 0.16) 0%, transparent 45%), "
            "radial-gradient(at 10% 90%, rgba(245, 196, 81, 0.08) 0%, transparent 45%), "
            "linear-gradient(180deg, #060A15 0%, #0B1221 100%)"
        )
        text_main = "#F1F5F9"
        text_muted = "#94A3B8"
        sidebar_bg = "#0A0F1E"
        sidebar_border = "#1E293B"
        card_bg = "#111827"
        card_border = "#1F2937"
        card_shadow = "0 10px 26px -10px rgba(0, 0, 0, 0.55)"
        input_bg = "#0F172A"
        input_border = "#334155"
        tab_bar_bg = "#0F172A"
        tab_active_bg = "#1E293B"
        person_bg = f"linear-gradient(135deg, #111827 0%, {soft_bg} 100%)"
        progress_track_bg = "#1F2937"
        divider_color = "#1E293B"
        color_scheme = "dark"
        sec_btn_bg = "#111827"
        sec_btn_border = "#334155"
        sec_btn_text = "#E2E8F0"
        sec_btn_hover_bg = "#1E293B"
        sidebar_sec_hover = "#162033"
        sidebar_sec_text = "#CBD5E1"
        header_bg = "rgba(6, 10, 21, 0.78)"
    else:
        app_bg = (
            "radial-gradient(at 90% 6%, rgba(219, 234, 254, 0.55) 0%, transparent 45%), "
            "radial-gradient(at 12% 92%, rgba(224, 231, 255, 0.45) 0%, transparent 45%), "
            "linear-gradient(180deg, #F8FAFC 0%, #F1F5F9 100%)"
        )
        text_main = "#0F172A"
        text_muted = "#64748B"
        sidebar_bg = "#FFFFFF"
        sidebar_border = "#E2E8F0"
        card_bg = "#FFFFFF"
        card_border = "#E2E8F0"
        card_shadow = "0 6px 18px -6px rgba(15, 23, 42, 0.06)"
        input_bg = "#FFFFFF"
        input_border = "#CBD5E1"
        tab_bar_bg = "#F1F5F9"
        tab_active_bg = "#FFFFFF"
        person_bg = f"linear-gradient(135deg, #FFFFFF 0%, {soft_bg} 100%)"
        progress_track_bg = "#E2E8F0"
        divider_color = "#F1F5F9"
        color_scheme = "light"
        sec_btn_bg = "#FFFFFF"
        sec_btn_border = "#E2E8F0"
        sec_btn_text = "#334155"
        sec_btn_hover_bg = "#F8FAFC"
        sidebar_sec_hover = "#F1F5F9"
        sidebar_sec_text = "#475569"
        header_bg = "rgba(248, 250, 252, 0.8)"

    sidebar_hide_css = (
        "section[data-testid='stSidebar'], div[data-testid='stSidebar'], button[data-testid='collapsedControl'] { display: none !important; }"
        if hide_sidebar
        else ""
    )

    dark_widget_css = (
        f"""
div[data-baseweb="select"] > div,
div[data-baseweb="popover"] > div,
ul[role="listbox"],
.stTextArea textarea,
.stDateInput > div > div {{
    background-color: {input_bg} !important;
    color: {text_main} !important;
    border-color: {input_border} !important;
}}
div[data-baseweb="select"] span,
div[data-baseweb="select"] svg {{
    color: {text_main} !important;
    fill: {text_main} !important;
}}
ul[role="listbox"] li {{
    color: {text_main} !important;
    background-color: {input_bg} !important;
}}
ul[role="listbox"] li:hover {{
    background-color: #1E293B !important;
}}
div[data-testid="stExpander"] {{
    background-color: {card_bg} !important;
    border: 1px solid {card_border} !important;
    border-radius: 12px !important;
}}
div[data-testid="stExpander"] summary,
div[data-testid="stExpander"] summary p,
div[data-testid="stExpander"] summary svg {{
    color: {text_main} !important;
    fill: {text_main} !important;
}}
div[data-testid="stChatInput"] > div {{
    background-color: {card_bg} !important;
    border: 1px solid {input_border} !important;
    border-radius: 14px !important;
}}
div[data-testid="stChatInput"] textarea {{
    color: {text_main} !important;
    -webkit-text-fill-color: {text_main} !important;
}}
.stRadio label, .stCheckbox label, .stSlider label, .stSelectbox label, .stMultiSelect label, .stDateInput label, .stTextArea label,
div[data-testid="stToggle"] label, div[data-testid="stToggle"] p {{
    color: {text_main} !important;
}}
.stMarkdown p, .stMarkdown li, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4, .stMarkdown h5 {{
    color: {text_main} !important;
}}
.stCaption, div[data-testid="stCaptionContainer"] p {{
    color: {text_muted} !important;
}}
hr {{
    border-color: {divider_color} !important;
}}
"""
        if dark and not login_glass
        else ""
    )

    login_glass_css = (
        """
header[data-testid="stHeader"] {
    background: transparent !important;
}
.stApp {
    background-color: #040711 !important;
    background-image:
        radial-gradient(rgba(255, 255, 255, 0.045) 1px, transparent 1px),
        radial-gradient(ellipse 65% 55% at 15% 18%, rgba(56, 189, 248, 0.30) 0%, transparent 62%),
        radial-gradient(ellipse 60% 55% at 85% 22%, rgba(245, 196, 81, 0.20) 0%, transparent 58%),
        radial-gradient(ellipse 55% 50% at 74% 84%, rgba(59, 130, 246, 0.28) 0%, transparent 60%),
        radial-gradient(ellipse 50% 45% at 22% 84%, rgba(139, 92, 246, 0.22) 0%, transparent 60%),
        linear-gradient(160deg, #040711 0%, #091024 48%, #0E172A 100%) !important;
    background-size: 28px 28px, 100% 100%, 100% 100%, 100% 100%, 100% 100%, 100% 100% !important;
    background-attachment: fixed !important;
}
.stApp::before {
    content: "";
    position: fixed;
    width: 340px;
    height: 340px;
    border-radius: 50%;
    top: 10%;
    left: 20%;
    background: radial-gradient(circle at 30% 30%, rgba(125, 211, 252, 0.36), rgba(59, 130, 246, 0.08) 60%, transparent 72%);
    filter: blur(20px);
    pointer-events: none;
    z-index: 0;
}
.stApp::after {
    content: "";
    position: fixed;
    width: 380px;
    height: 380px;
    border-radius: 50%;
    bottom: 6%;
    right: 18%;
    background: radial-gradient(circle at 70% 70%, rgba(245, 196, 81, 0.22), rgba(99, 102, 241, 0.12) 62%, transparent 74%);
    filter: blur(24px);
    pointer-events: none;
    z-index: 0;
}
div[data-testid="stVerticalBlockBorderWrapper"] {
    background: linear-gradient(155deg, rgba(255, 255, 255, 0.13) 0%, rgba(255, 255, 255, 0.05) 100%) !important;
    backdrop-filter: blur(34px) saturate(185%) !important;
    -webkit-backdrop-filter: blur(34px) saturate(185%) !important;
    border: 1px solid rgba(255, 255, 255, 0.24) !important;
    border-top: 1px solid rgba(255, 255, 255, 0.42) !important;
    border-radius: 28px !important;
    box-shadow: 0 32px 70px -15px rgba(0, 0, 0, 0.68), inset 0 1px 0 rgba(255, 255, 255, 0.30) !important;
    padding: 0.95rem 1.05rem !important;
}
.stTextInput label,
div[data-testid="stWidgetLabel"] label {
    color: rgba(241, 245, 249, 0.92) !important;
    font-weight: 600 !important;
    font-size: 0.84rem !important;
}
.stTextInput > div > div {
    background: rgba(15, 23, 42, 0.48) !important;
    backdrop-filter: blur(12px) !important;
    -webkit-backdrop-filter: blur(12px) !important;
    border: 1px solid rgba(255, 255, 255, 0.20) !important;
    border-radius: 14px !important;
    box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.25) !important;
}
.stTextInput input,
input[type="text"],
input[type="password"] {
    color: #FFFFFF !important;
    -webkit-text-fill-color: #FFFFFF !important;
}
input::placeholder {
    color: rgba(203, 213, 225, 0.58) !important;
    -webkit-text-fill-color: rgba(203, 213, 225, 0.58) !important;
}
.stTextInput > div > div button svg {
    fill: rgba(226, 232, 240, 0.85) !important;
    color: rgba(226, 232, 240, 0.85) !important;
}
button[kind="secondaryFormSubmit"],
button[kind="primary"],
button[data-testid="stBaseButton-primary"],
button[data-testid="stBaseButton-secondaryFormSubmit"] {
    background: linear-gradient(135deg, #2563EB 0%, #3B82F6 100%) !important;
    border: 1px solid rgba(255, 255, 255, 0.28) !important;
    border-radius: 13px !important;
    box-shadow: 0 10px 24px -8px rgba(37, 99, 235, 0.65), inset 0 1px 0 rgba(255, 255, 255, 0.35) !important;
    font-weight: 600 !important;
    color: #FFFFFF !important;
    -webkit-text-fill-color: #FFFFFF !important;
}
button[kind="secondary"],
button[data-testid="stBaseButton-secondary"] {
    background: rgba(255, 255, 255, 0.10) !important;
    backdrop-filter: blur(14px) !important;
    -webkit-backdrop-filter: blur(14px) !important;
    border: 1px solid rgba(255, 255, 255, 0.22) !important;
    border-radius: 12px !important;
    color: #F8FAFC !important;
    -webkit-text-fill-color: #F8FAFC !important;
    box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.18) !important;
}
button[kind="secondary"] p,
button[kind="secondary"] span,
button[data-testid="stBaseButton-secondary"] p,
button[data-testid="stBaseButton-secondary"] span {
    color: #F8FAFC !important;
    -webkit-text-fill-color: #F8FAFC !important;
}
button[kind="secondary"]:hover,
button[data-testid="stBaseButton-secondary"]:hover {
    background: rgba(255, 255, 255, 0.22) !important;
    border-color: rgba(255, 255, 255, 0.45) !important;
}
"""
        if login_glass
        else ""
    )

    css = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Plus+Jakarta+Sans:wght@600;700;800&display=swap');

:root {{
    color-scheme: {color_scheme};
}}

html, body, [class*="css"], .stApp {{
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    background: {app_bg} !important;
    color: {text_main} !important;
}}

header[data-testid="stHeader"] {{
    background: {header_bg} !important;
    backdrop-filter: blur(10px);
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

/* Architectural Sidebar (Target both section and div testids in Streamlit 1.58) */
section[data-testid="stSidebar"],
div[data-testid="stSidebar"],
section[data-testid="stSidebar"] > div,
div[data-testid="stSidebarContent"],
div[data-testid="stSidebarUserContent"] {{
    background-color: {sidebar_bg} !important;
    color: {text_main} !important;
}}
section[data-testid="stSidebar"],
div[data-testid="stSidebar"] {{
    border-right: 1px solid {sidebar_border} !important;
}}
section[data-testid="stSidebar"] > div:first-child {{
    padding-top: 1.05rem !important;
}}
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] span {{
    color: {text_main};
}}
section[data-testid="stSidebar"] button[data-testid="stSidebarCollapseButton"] svg {{
    fill: {text_muted} !important;
    color: {text_muted} !important;
}}

/* Native Bordered Containers */
div[data-testid="stVerticalBlockBorderWrapper"] {{
    background-color: {card_bg} !important;
    border: 1px solid {card_border} !important;
    border-radius: 16px !important;
    box-shadow: {card_shadow} !important;
    padding: 0.35rem 0.45rem !important;
}}

/* Hero Banner */
.hero-banner {{
    background: {theme["gradient"]};
    border: 1px solid rgba(255, 255, 255, 0.14);
    border-radius: 16px;
    padding: 1.45rem 1.75rem;
    color: #FFFFFF;
    margin-bottom: 1.25rem;
    box-shadow: 0 14px 30px -10px rgba(0, 0, 0, 0.35);
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
    color: #FFFFFF !important;
    margin: 0;
    letter-spacing: -0.02em;
}}
.hero-subtitle {{
    font-size: 0.89rem;
    color: rgba(255, 255, 255, 0.86) !important;
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
    color: #FFFFFF !important;
    padding: 0.38rem 0.85rem;
    border-radius: 999px;
    font-size: 0.78rem;
    font-weight: 600;
}}

/* Rich KPI Cards */
.kpi-card {{
    background-color: {card_bg};
    border: 1px solid {card_border};
    border-radius: 14px;
    padding: 1.1rem 1.2rem;
    box-shadow: {card_shadow};
    margin-bottom: 0.75rem;
    transition: transform 0.16s ease, box-shadow 0.16s ease;
    height: 100%;
}}
.kpi-card:hover {{
    transform: translateY(-2px);
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
    color: {text_muted};
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
    color: {text_main};
    line-height: 1.1;
    letter-spacing: -0.025em;
}}
.kpi-detail {{
    font-size: 0.79rem;
    color: {text_muted};
    margin-top: 0.4rem;
}}
.progress-track {{
    width: 100%;
    height: 5px;
    background-color: {progress_track_bg};
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
    background-color: rgba(16, 185, 129, 0.18);
    color: #34D399;
    font-size: 0.71rem;
    font-weight: 700;
    padding: 0.12rem 0.45rem;
    border-radius: 999px;
    margin-left: 0.35rem;
    vertical-align: middle;
}}
.kpi-delta-neg {{
    display: inline-block;
    background-color: rgba(239, 68, 68, 0.18);
    color: #F87171;
    font-size: 0.71rem;
    font-weight: 700;
    padding: 0.12rem 0.45rem;
    border-radius: 999px;
    margin-left: 0.35rem;
    vertical-align: middle;
}}

/* Surface Panels */
.surface-panel {{
    background-color: {card_bg};
    border: 1px solid {card_border};
    border-radius: 14px;
    padding: 1.2rem 1.35rem;
    box-shadow: {card_shadow};
    margin-bottom: 1rem;
    color: {text_main};
}}
.panel-title {{
    font-size: 0.95rem;
    font-weight: 700;
    color: {text_main};
    margin-bottom: 0.75rem;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid {divider_color};
}}

/* Person Card */
.person-card {{
    background: {person_bg};
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
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.22);
    flex-shrink: 0;
}}

/* Callouts & Tags */
.callout-card {{
    background-color: {card_bg};
    border: 1px solid {card_border};
    border-left: 3.5px solid {primary};
    border-radius: 10px;
    padding: 0.8rem 0.95rem;
    margin-bottom: 0.55rem;
    font-size: 0.86rem;
    color: {text_main};
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
.pill-safe {{ background-color: rgba(16, 185, 129, 0.16); color: #10B981; border: 1px solid rgba(16, 185, 129, 0.35); }}
.pill-warning {{ background-color: rgba(245, 158, 11, 0.16); color: #F59E0B; border: 1px solid rgba(245, 158, 11, 0.35); }}
.pill-critical {{ background-color: rgba(239, 68, 68, 0.16); color: #EF4444; border: 1px solid rgba(239, 68, 68, 0.35); }}

/* Unified Inputs (Zero double borders) */
div[data-baseweb="input"],
div[data-baseweb="base-input"],
.stTextInput input,
input[type="text"],
input[type="password"] {{
    background-color: transparent !important;
    color: {text_main} !important;
    -webkit-text-fill-color: {text_main} !important;
    border: none !important;
    box-shadow: none !important;
}}
.stTextInput > div > div {{
    border: 1px solid {input_border} !important;
    border-radius: 10px !important;
    background-color: {input_bg} !important;
}}
.stTextInput > div > div button {{
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
}}
input::placeholder {{
    color: {text_muted} !important;
    -webkit-text-fill-color: {text_muted} !important;
}}
.stTextInput label,
div[data-testid="stWidgetLabel"] label {{
    color: {text_main} !important;
    font-weight: 600 !important;
    font-size: 0.85rem !important;
}}

/* Primary Buttons */
.stButton > button,
button[kind="primary"],
button[data-testid="stBaseButton-primary"],
button[kind="secondaryFormSubmit"],
button[data-testid="stBaseButton-secondaryFormSubmit"] {{
    background: {btn_primary} !important;
    color: #FFFFFF !important;
    -webkit-text-fill-color: #FFFFFF !important;
    border: 1px solid {btn_primary} !important;
    border-radius: 9px !important;
    font-weight: 600 !important;
    font-size: 0.87rem !important;
    padding: 0.5rem 1rem !important;
    transition: all 0.15s ease !important;
}}
.stButton > button p,
.stButton > button span {{
    color: #FFFFFF !important;
    -webkit-text-fill-color: #FFFFFF !important;
}}
.stButton > button:hover,
button[kind="primary"]:hover,
button[data-testid="stBaseButton-primary"]:hover,
button[kind="secondaryFormSubmit"]:hover {{
    background: {primary_hover} !important;
    border-color: {primary_hover} !important;
}}

/* Secondary Buttons */
button[kind="secondary"],
button[data-testid="stBaseButton-secondary"] {{
    background: {sec_btn_bg} !important;
    color: {sec_btn_text} !important;
    -webkit-text-fill-color: {sec_btn_text} !important;
    border: 1px solid {sec_btn_border} !important;
    border-radius: 9px !important;
    font-weight: 600 !important;
    box-shadow: none !important;
}}
button[kind="secondary"] p,
button[kind="secondary"] span,
button[data-testid="stBaseButton-secondary"] p,
button[data-testid="stBaseButton-secondary"] span {{
    color: {sec_btn_text} !important;
    -webkit-text-fill-color: {sec_btn_text} !important;
}}
button[kind="secondary"]:hover,
button[data-testid="stBaseButton-secondary"]:hover {{
    background: {sec_btn_hover_bg} !important;
}}

/* Refined Executive Sidebar Navigation Items */
section[data-testid="stSidebar"] .stButton > button,
div[data-testid="stSidebar"] .stButton > button {{
    justify-content: flex-start !important;
    text-align: left !important;
    padding: 0.48rem 0.78rem !important;
    font-size: 0.85rem !important;
    border-radius: 8px !important;
    box-shadow: none !important;
}}
section[data-testid="stSidebar"] button[kind="primary"],
section[data-testid="stSidebar"] button[data-testid="stBaseButton-primary"],
div[data-testid="stSidebar"] button[kind="primary"] {{
    background: {soft_bg} !important;
    color: {primary} !important;
    -webkit-text-fill-color: {primary} !important;
    border: 1px solid {soft_border} !important;
    border-left: 3.5px solid {primary} !important;
    font-weight: 700 !important;
}}
section[data-testid="stSidebar"] button[kind="primary"] p,
section[data-testid="stSidebar"] button[kind="primary"] span,
section[data-testid="stSidebar"] button[data-testid="stBaseButton-primary"] p,
section[data-testid="stSidebar"] button[data-testid="stBaseButton-primary"] span {{
    color: {primary} !important;
    -webkit-text-fill-color: {primary} !important;
}}
section[data-testid="stSidebar"] button[kind="secondary"],
section[data-testid="stSidebar"] button[data-testid="stBaseButton-secondary"],
div[data-testid="stSidebar"] button[kind="secondary"] {{
    background: transparent !important;
    border: 1px solid transparent !important;
    color: {sidebar_sec_text} !important;
    -webkit-text-fill-color: {sidebar_sec_text} !important;
    font-weight: 500 !important;
}}
section[data-testid="stSidebar"] button[kind="secondary"] p,
section[data-testid="stSidebar"] button[kind="secondary"] span,
section[data-testid="stSidebar"] button[data-testid="stBaseButton-secondary"] p,
section[data-testid="stSidebar"] button[data-testid="stBaseButton-secondary"] span {{
    color: {sidebar_sec_text} !important;
    -webkit-text-fill-color: {sidebar_sec_text} !important;
}}
section[data-testid="stSidebar"] button[kind="secondary"]:hover,
section[data-testid="stSidebar"] button[data-testid="stBaseButton-secondary"]:hover {{
    background: {sidebar_sec_hover} !important;
    color: {text_main} !important;
    -webkit-text-fill-color: {text_main} !important;
}}
section[data-testid="stSidebar"] button[kind="secondary"]:hover p,
section[data-testid="stSidebar"] button[kind="secondary"]:hover span,
section[data-testid="stSidebar"] button[data-testid="stBaseButton-secondary"]:hover p,
section[data-testid="stSidebar"] button[data-testid="stBaseButton-secondary"]:hover span {{
    color: {text_main} !important;
    -webkit-text-fill-color: {text_main} !important;
}}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {{
    gap: 6px;
    background-color: {tab_bar_bg};
    padding: 4px;
    border-radius: 10px;
    border: 1px solid {card_border};
    margin-bottom: 1rem;
}}
.stTabs [data-baseweb="tab"] {{
    border-radius: 8px;
    padding: 6px 15px;
    font-weight: 600;
    font-size: 0.86rem;
    color: {text_muted} !important;
    background-color: transparent !important;
    border: none !important;
}}
.stTabs [aria-selected="true"] {{
    background-color: {tab_active_bg} !important;
    color: {primary} !important;
    box-shadow: 0 1px 4px rgba(0, 0, 0, 0.12) !important;
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
    fill: {text_muted} !important;
    width: 15px !important;
    height: 15px !important;
}}

/* Chat Bubbles */
div[data-testid="stChatMessage"] {{
    background-color: {card_bg};
    border: 1px solid {card_border};
    border-radius: 14px;
    padding: 0.95rem 1.15rem;
    margin-bottom: 0.7rem;
    box-shadow: {card_shadow};
}}
{dark_widget_css}
{login_glass_css}
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
    dark = is_dark_mode()
    name_col = "#F1F5F9" if dark else "#0F172A"
    sub_col = "#94A3B8" if dark else "#475569"
    initials = "".join(part[0].upper() for part in name.split()[:2]) or "ST"
    pill_cls = f"pill-{badge_kind}"
    render_html(
        f"""
        <div class="person-card">
        <div style="display:flex; align-items:center; gap:12px;">
        <div class="avatar-circle">{initials}</div>
        <div>
        <div style="font-size:1.02rem; font-weight:800; color:{name_col};">{name}</div>
        <div style="font-size:0.82rem; color:{sub_col};">{subtitle}</div>
        </div>
        </div>
        <div style="display:flex; align-items:center; gap:10px; flex-wrap:wrap;">
        <span style="font-size:0.82rem; color:{sub_col}; font-weight:600;">{right_note}</span>
        <span class="status-pill {pill_cls}">{badge_text}</span>
        </div>
        </div>
        """
    )


def apply_clean_chart_theme(fig, height: int = 320):
    dark = is_dark_mode()
    bg = "#111827" if dark else "#FFFFFF"
    font_col = "#E2E8F0" if dark else "#334155"
    grid_col = "#1F2937" if dark else "#F1F5F9"

    fig.update_layout(
        font=dict(family="Inter, sans-serif", size=12, color=font_col),
        legend=dict(font=dict(color=font_col), title_font=dict(color=font_col)),
        coloraxis_colorbar=dict(tickfont=dict(color=font_col), title_font=dict(color=font_col)),
        plot_bgcolor=bg,
        paper_bgcolor=bg,
        margin=dict(l=20, r=20, t=34, b=24),
        height=height,
        hoverlabel=dict(bgcolor="#0F172A", font_color="#FFFFFF", font_size=12),
    )
    fig.update_xaxes(
        showgrid=True,
        gridcolor=grid_col,
        zeroline=False,
        tickfont=dict(color=font_col),
        title_font=dict(color=font_col),
    )
    fig.update_yaxes(
        showgrid=True,
        gridcolor=grid_col,
        zeroline=False,
        tickfont=dict(color=font_col),
        title_font=dict(color=font_col),
    )
    return fig


def build_student_radar_chart(
    student_row,
    benchmark_series,
    student_label: str = "Student",
    benchmark_label: str = "Class Average",
    accent_color: str = "#4F46E5",
    height: int = 310,
):
    dark = is_dark_mode()
    bg = "#111827" if dark else "#FFFFFF"
    grid_col = "#1F2937" if dark else "#E2E8F0"
    font_col = "#E2E8F0" if dark else "#334155"

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

    def _hex_to_rgba(hex_color: str, alpha: float = 0.22) -> str:
        h = hex_color.lstrip("#")
        if len(h) == 6:
            r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
            return f"rgba({r}, {g}, {b}, {alpha})"
        return f"rgba(59, 130, 246, {alpha})"

    fig = go.Figure()
    fig.add_trace(
        go.Scatterpolar(
            r=b_vals + [b_vals[0]],
            theta=categories + [categories[0]],
            fill="toself",
            name=benchmark_label,
            line=dict(color="#94A3B8", width=2, dash="dot"),
            fillcolor="rgba(148, 163, 184, 0.16)",
        )
    )
    fig.add_trace(
        go.Scatterpolar(
            r=s_vals + [s_vals[0]],
            theta=categories + [categories[0]],
            fill="toself",
            name=student_label,
            line=dict(color=accent_color, width=2.5),
            fillcolor=_hex_to_rgba(accent_color, 0.24),
        )
    )
    fig.update_layout(
        polar=dict(
            bgcolor=bg,
            radialaxis=dict(visible=True, range=[0, 100], gridcolor=grid_col, tickfont=dict(size=10, color=font_col)),
            angularaxis=dict(gridcolor=grid_col, tickfont=dict(size=11, color=font_col)),
        ),
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.06, xanchor="center", x=0.5, font=dict(color=font_col)),
        margin=dict(l=42, r=42, t=42, b=24),
        paper_bgcolor=bg,
        height=height,
        font=dict(family="Inter, sans-serif", size=12, color=font_col),
    )
    return fig
