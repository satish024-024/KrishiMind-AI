"""
Agri Advisor — Smart Agriculture Assistant
"""

import streamlit as st
import sys
from pathlib import Path
import time
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

from services.faiss_store import FAISSSearcher
from services.watsonx_service import WatsonxService
from services.query_handler import QueryHandler
from config import (
    FAISS_INDEX_FILE, 
    METADATA_FILE,
    GEMINI_API_KEY
)


# Page configuration
st.set_page_config(
    page_title="Agri Advisor — Smart Agriculture Assistant",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Initialize session state
_session_defaults = {
    'query_history': [],
    'total_queries': 0,
    'successful_queries': 0,
    'show_welcome': True,
    'selected_language': 'en',
    'selected_question': None,
    'active_category': None,
    'chat_messages': [],
    'response_times': [],
    'last_processed_query': None,
}
for _key, _val in _session_defaults.items():
    if _key not in st.session_state:
        st.session_state[_key] = _val


def sanitize_input(text: str) -> str:
    """Sanitize user input: strip, limit length, remove HTML tags."""
    import re
    text = re.sub(r'[<>]', '', text)
    return text.strip()[:500]

# ─────────────────────────────────────────────────────────
# CSS — Modern KissanAI-inspired design
# ─────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    * { font-family: 'Inter', sans-serif; }

    /* ── FORCE WHITE / LIGHT THEME ───────────────────── */
    :root {
        color-scheme: light !important;
    }
    html, body, [data-testid="stAppViewContainer"],
    [data-testid="stApp"],
    .main, .stApp,
    [data-testid="stAppViewBlockContainer"],
    [data-testid="stVerticalBlock"],
    [data-testid="stMainBlockContainer"],
    .block-container {
        background-color: #f9fafb !important;
        color: #1f2937 !important;
    }
    [data-testid="stSidebar"],
    [data-testid="stSidebar"] > div {
        background-color: #f9fafb !important;
        color: #1f2937 !important;
    }
    [data-testid="stHeader"] {
        background-color: #ffffff !important;
    }
    /* Override all dark-theme text */
    p, span, label, h1, h2, h3, h4, h5, h6, li, div {
        color: inherit;
    }
    .stMarkdown, .stText { color: #1f2937 !important; }

    /* ── Page background ─────────────────────────────── */
    .main { background: #f9fafb !important; }
    .block-container { padding-top: 0 !important; max-width: 960px; padding-bottom: 2rem !important; }

    /* ── Hide streamlit chrome ────────────────────────── */
    #MainMenu, footer, header { visibility: hidden; }
    .stDeployButton { display: none; }
    [data-testid="stHeader"] { height: 0 !important; min-height: 0 !important; }

    /* ── Fixed Header ─────────────────────────────────── */
    .km-header {
        position: fixed;
        top: 0; left: 0; right: 0;
        z-index: 9999;
        background: #ffffff;
        border-bottom: 1px solid #e5e7eb;
        box-shadow: 0 1px 3px rgba(0,0,0,0.06);
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0.75rem 2rem;
        height: 56px;
        box-sizing: border-box;
    }
    .km-header-logo {
        display: flex; align-items: center; gap: 0.5rem;
    }
    .km-header-logo-icon { font-size: 1.5rem; }
    .km-header-logo-text {
        font-size: 1.2rem; font-weight: 800;
        background: linear-gradient(135deg,#1a6b3c,#43a047);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    }
    .km-header-right { display: flex; align-items: center; gap: 0.6rem; }
    .km-pill {
        display: flex; align-items: center; gap: 0.35rem;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.78rem; font-weight: 600;
    }
    .km-pill-lang { background: #eef7f0; color: #1a6b3c; }
    .km-pill-status { background: #ecfdf5; color: #059669; }
    .km-dot {
        width: 6px; height: 6px; border-radius: 50%; background: #10b981;
        animation: blink 1.6s ease-in-out infinite;
    }
    @keyframes blink {
        0%,100% { opacity: 1; } 50% { opacity: .35; }
    }

    /* ── Spacer for fixed header ──────────────────────── */
    .km-header-spacer { height: 64px; }

    /* ── Hero / Centered content area ─────────────────── */
    .km-hero {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        min-height: 50vh;
        padding: 2rem 1rem;
        text-align: center;
    }
    .km-hero-title {
        font-size: 2rem; font-weight: 700; color: #374151;
        margin-bottom: 1.5rem;
        animation: fadeUp 0.45s ease;
    }
    @keyframes fadeUp {
        from { opacity: 0; transform: translateY(14px); }
        to   { opacity: 1; transform: translateY(0); }
    }

    /* ── Feature card grid (KissanAI style) ───────────── */
    .km-grid {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 1rem;
        max-width: 540px;
        width: 100%;
        margin: 0 auto;
    }
    @media (min-width: 640px) {
        .km-grid { grid-template-columns: repeat(4, 1fr); max-width: 700px; gap: 1.25rem; }
    }
    .km-fcard {
        background: white;
        border-radius: 16px;
        padding: 1.5rem 1rem;
        text-align: center;
        border: 2px solid #e5e7eb;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        cursor: pointer;
        transition: all 0.3s ease;
        animation: cardPop 0.5s ease both;
    }
    .km-fcard:nth-child(1) { animation-delay: .05s; }
    .km-fcard:nth-child(2) { animation-delay: .12s; }
    .km-fcard:nth-child(3) { animation-delay: .19s; }
    .km-fcard:nth-child(4) { animation-delay: .26s; }
    @keyframes cardPop {
        from { opacity: 0; transform: translateY(18px) scale(.96); }
        to   { opacity: 1; transform: translateY(0) scale(1); }
    }
    .km-fcard:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 28px rgba(76,175,80,0.12);
        border-color: #43a047;
    }
    .km-fcard.active {
        border-color: #2e7d32;
        background: linear-gradient(135deg,#e8f5e9,#f1f8e9);
        box-shadow: 0 8px 24px rgba(76,175,80,0.18);
    }
    .km-fcard-icon {
        font-size: 2.5rem; margin-bottom: 0.5rem;
        display: inline-block;
    }
    .km-fcard-title {
        font-size: 0.88rem; font-weight: 700; color: #1f2937;
    }
    .km-fcard-sub {
        font-size: 0.75rem; color: #6b7280; font-weight: 500; margin-top: 2px;
    }

    /* ── Bottom search bar (in-flow) ────────────────── */
    .km-searchbar {
        background: #ffffff;
        border-top: 1px solid #e5e7eb;
        border-bottom: 1px solid #e5e7eb;
        padding: 0.75rem 1.5rem;
        margin: 1.5rem -1rem 0 -1rem;
    }

    /* ── Popular Questions card ───────────────────────── */
    .km-pq-card {
        background: #ffffff;
        border-radius: 16px;
        box-shadow: 0 1px 6px rgba(0,0,0,0.06);
        overflow: hidden;
        margin: 0 auto;
        max-width: 700px;
        animation: fadeUp 0.5s ease;
    }
    .km-pq-header {
        padding: 1.1rem 1.5rem 0.8rem;
        font-size: 1.05rem;
        font-weight: 700;
        color: #1f2937;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    .km-pq-item {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        padding: 0.9rem 1.5rem;
        border-top: 1px solid #f3f4f6;
        cursor: pointer;
        transition: background 0.18s ease, padding-left 0.18s ease;
        font-size: 0.92rem;
        color: #374151;
        font-weight: 500;
    }
    .km-pq-item:hover {
        background: #f0fdf4;
        padding-left: 2rem;
    }
    .km-pq-chevron {
        color: #43a047;
        font-size: 0.8rem;
        font-weight: 700;
    }

    /* ── Footer ───────────────────────────────────────── */
    .km-footer {
        background: #f9fafb;
        border-top: 1px solid #e5e7eb;
        padding: 0.75rem 0;
        text-align: center;
        font-size: 0.8rem;
        color: #9ca3af;
        margin-top: 1rem;
    }
    .km-footer a {
        color: #43a047;
        text-decoration: none;
        font-weight: 600;
    }

    /* ── Default buttons (question list items) ────────── */
    .stButton > button {
        background: #ffffff !important;
        color: #374151 !important;
        border: none !important;
        border-bottom: 1px solid #f3f4f6 !important;
        border-radius: 0 !important;
        font-weight: 500 !important;
        font-size: 0.92rem !important;
        padding: 0.9rem 1.2rem !important;
        text-align: left !important;
        box-shadow: none !important;
        transition: background 0.18s ease, padding-left 0.18s ease !important;
    }
    .stButton > button:hover {
        background: #f0fdf4 !important;
        padding-left: 1.6rem !important;
        transform: none !important;
        box-shadow: none !important;
    }

    /* ── Secondary buttons (category cards) ───────────── */
    .stButton > button[kind="secondary"] {
        background: white !important;
        color: #1f2937 !important;
        border: 2px solid #e5e7eb !important;
        border-radius: 16px !important;
        padding: 1.4rem 0.8rem !important;
        font-size: 1rem !important;
        font-weight: 700 !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04) !important;
        transition: all 0.3s ease !important;
        white-space: pre-line !important;
        line-height: 1.5 !important;
        min-height: 100px !important;
        text-align: center !important;
    }
    .stButton > button[kind="secondary"]:hover {
        border-color: #43a047 !important;
        box-shadow: 0 8px 20px rgba(76,175,80,0.15) !important;
        transform: translateY(-4px) !important;
        background: #f0fdf4 !important;
        padding-left: 0.8rem !important;
    }

    /* ── Primary buttons (selected category card) ──────── */
    .stButton > button[kind="primary"] {
        background: white !important;
        color: #2e7d32 !important;
        border: 2px solid #2e7d32 !important;
        border-radius: 16px !important;
        padding: 1.4rem 0.8rem !important;
        font-size: 1rem !important;
        font-weight: 700 !important;
        box-shadow: 0 4px 16px rgba(76,175,80,0.18) !important;
        white-space: pre-line !important;
        line-height: 1.5 !important;
        min-height: 100px !important;
        text-align: center !important;
    }
    .stButton > button[kind="primary"]:hover {
        transform: translateY(-4px) !important;
        padding-left: 0.8rem !important;
    }

    /* ── Send button ──────────────────────────────────── */
    [data-testid="stButton"][class*="send"] button,
    button[key="send_btn"] {
        background: linear-gradient(135deg,#2e7d32,#43a047) !important;
        color: white !important;
        border: none !important;
        border-radius: 50px !important;
        min-height: auto !important;
        padding: 0.65rem 1.2rem !important;
    }

    /* ── Text input ───────────────────────────────────── */
    .stTextInput > div > div > input {
        border-radius: 28px !important;
        border: 2px solid #e5e7eb !important;
        padding: 0.85rem 1.3rem !important;
        font-size: 0.92rem !important;
        background: #ffffff !important;
        transition: border-color .25s ease, box-shadow .25s ease !important;
    }
    .stTextInput > div > div > input:focus {
        border-color: #43a047 !important;
        box-shadow: 0 0 0 3px rgba(76,175,80,0.12) !important;
    }

    /* ── Tabs styling for white bg ────────────────────── */
    .stTabs [data-baseweb="tab-list"] {
        background: #f9fafb !important;
        border-radius: 12px;
        padding: 0.4rem;
        gap: 6px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        font-weight: 600;
        color: #6b7280 !important;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg,#2e7d32,#43a047) !important;
        color: white !important;
    }

    /* ── Answer card ──────────────────────────────────── */
    .ans-card {
        background: white; border-radius: 16px;
        padding: 1.75rem 1.5rem; margin: 1.25rem 0;
        border-left: 4px solid #43a047;
        box-shadow: 0 4px 16px rgba(0,0,0,0.05);
        animation: slideUp 0.4s ease;
    }
    @keyframes slideUp {
        from { opacity: 0; transform: translateY(16px); }
        to   { opacity: 1; transform: translateY(0); }
    }
    .ans-card-head {
        display: flex; align-items: center; gap: 0.75rem;
        margin-bottom: 1rem; padding-bottom: 0.75rem;
        border-bottom: 1px solid #f3f4f6;
    }
    .ans-card-icon {
        width: 42px; height: 42px; border-radius: 12px;
        display: flex; align-items: center; justify-content: center;
        font-size: 1.3rem;
        background: linear-gradient(135deg,#2e7d32,#43a047);
    }
    .ans-card-title { font-size: 1.1rem; font-weight: 700; color: #1f2937; }
    .ans-card-sub { font-size: 0.8rem; color: #6b7280; margin-top: 2px; }
    .ans-card-body {
        font-size: 0.98rem; line-height: 1.85; color: #374151;
    }
    .ans-card.ai { border-left-color: #7c3aed; }
    .ans-card.ai .ans-card-icon {
        background: linear-gradient(135deg,#7c3aed,#a855f7);
    }

    /* ── Additional Card Variants ─────────────────────── */
    .ans-card.offline { border-left-color: #3b82f6; }
    .ans-card.online { border-left-color: #8b5cf6; }
    .card-icon.offline { background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%); }
    .card-icon.online { background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%); }

    .metric-delta {
        font-size: 0.8rem;
        color: #10b981;
        margin-top: 0.5rem;
        font-weight: 600;
    }

    /* ── Confidence bar ───────────────────────────────── */
    .conf-bar-bg {
        height: 7px; background: #e5e7eb; border-radius: 10px;
        overflow: hidden; margin: 4px 0;
    }
    .conf-bar-fill {
        height: 100%; border-radius: 10px;
        background: linear-gradient(90deg,#2e7d32,#66bb6a);
        transition: width 0.6s ease;
    }

    /* ── Badges ────────────────────────────────────────── */
    .badge {
        display: inline-block; padding: 0.3rem 0.85rem;
        border-radius: 20px; font-size: 0.8rem; font-weight: 600;
        margin: 0.15rem;
    }
    .badge-ok  { background: #d1fae5; color: #065f46; }
    .badge-warn { background: #fef3c7; color: #92400e; }
    .badge-info { background: #dbeafe; color: #1e40af; }

    /* ── Metric mini-cards ─────────────────────────────── */
    .mcard {
        background: white; border-radius: 14px; padding: 1.15rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        border: 1px solid #f3f4f6;
        transition: transform .25s ease, box-shadow .25s ease;
    }
    .mcard:hover {
        transform: translateY(-3px);
        box-shadow: 0 6px 18px rgba(0,0,0,0.08);
    }
    .mcard-val {
        font-size: 2rem; font-weight: 800;
        background: linear-gradient(135deg,#1a6b3c,#43a047);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    }
    .mcard-label {
        font-size: 0.78rem; color: #6b7280; text-transform: uppercase;
        letter-spacing: 0.5px; margin-top: 0.3rem; font-weight: 600;
    }

    /* ── Welcome screen ───────────────────────────────── */
    .ws-header {
        background: linear-gradient(135deg,#1a6b3c,#43a047);
        padding: 4rem 2rem 3rem; text-align: center;
        margin: -1rem -1rem 0 -1rem; position: relative; overflow: hidden;
    }
    .ws-header::before {
        content: ''; position: absolute; inset: 0;
        background: repeating-linear-gradient(
            45deg, transparent, transparent 35px,
            rgba(255,255,255,.04) 35px, rgba(255,255,255,.04) 70px);
    }
    .ws-float {
        position: absolute; opacity: 0.15;
        animation: wFloat 6s ease-in-out infinite;
    }
    @keyframes wFloat {
        0%,100% { transform: translateY(0) rotate(0); }
        50%     { transform: translateY(-22px) rotate(5deg); }
    }
    .ws-title {
        font-size: 2.8rem; font-weight: 800; color: white;
        text-shadow: 2px 4px 10px rgba(0,0,0,0.18);
        position: relative; z-index: 2; letter-spacing: -0.5px;
    }
    .ws-sub {
        font-size: 1.15rem; color: rgba(255,255,255,0.92);
        font-weight: 500; position: relative; z-index: 2; margin-top: 0.75rem;
    }

    /* ── Scrollbar ─────────────────────────────────────── */
    ::-webkit-scrollbar { width: 7px; }
    ::-webkit-scrollbar-track { background: #f3f4f6; }
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(180deg,#43a047,#2e7d32);
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────
# Service loaders (cached)
# ─────────────────────────────────────────────────────────
@st.cache_resource(show_spinner=False)
def load_faiss_searcher() -> FAISSSearcher:
    """Load FAISS searcher (cached for performance)"""
    try:
        searcher = FAISSSearcher().load()
        return searcher
    except Exception as e:
        st.error(f"FAISS Error: {e}")
        return None


@st.cache_resource(show_spinner=False)
def load_watsonx_service() -> WatsonxService:
    """Load Watsonx service (cached for performance)"""
    try:
        service = WatsonxService().initialize()
        return service
    except Exception as e:
        st.warning(f"Watsonx unavailable: {e}")
        return None


# ─────────────────────────────────────────────────────────
# Welcome / Language-selection screen
# ─────────────────────────────────────────────────────────
def render_welcome_screen() -> None:
    """Render welcome screen with language selection"""
    languages = [
        {"code": "en", "native": "English",   "english": "English"},
        {"code": "hi", "native": "हिंदी",      "english": "Hindi"},
        {"code": "te", "native": "తెలుగు",     "english": "Telugu"},
    ]

    # Header
    st.markdown("""
    <div class="ws-header">
        <div class="ws-float" style="top:18%;left:8%;font-size:3rem;">🌾</div>
        <div class="ws-float" style="top:55%;right:12%;font-size:2.5rem;animation-delay:.8s;">🌱</div>
        <div class="ws-float" style="bottom:18%;left:22%;font-size:2rem;animation-delay:1.6s;">🍃</div>
        <div style="position:relative;z-index:2;">
            <div style="font-size:4.5rem;margin-bottom:1rem;
                        animation:bounceIn 0.8s ease;
                        filter:drop-shadow(0 4px 10px rgba(0,0,0,0.2));">🌾</div>
            <h1 class="ws-title">Welcome to Agri Advisor</h1>
            <p class="ws-sub">Empowering Indian Farmers with AI-Powered Agricultural Insights</p>
        </div>
    </div>
    <style>
        @keyframes bounceIn {
            0%  { transform:scale(0);opacity:0; }
            50% { transform:scale(1.12); }
            100%{ transform:scale(1);opacity:1; }
        }
    </style>
    """, unsafe_allow_html=True)

    # Description
    st.markdown("""
    <div style="max-width:860px;margin:2.5rem auto 1rem;text-align:center;padding:0 1rem;background:#ffffff;">
        <h2 style="font-size:1.8rem;font-weight:700;color:#1f2937;margin-bottom:.75rem;">
            Your Personal Agriculture AI Agent</h2>
        <p style="font-size:1.05rem;color:#6b7280;line-height:1.8;">
            Get real-time weather updates, market prices, crop recommendations, and expert farming
            advice in your preferred language.</p>
    </div>
    """, unsafe_allow_html=True)

    # Feature cards
    col1, col2, col3, col4 = st.columns(4)
    feats = [
        ("🌤️", "Weather Forecast", "Real-time updates"),
        ("💰", "Market Prices", "Latest rates"),
        ("🌱", "Crop Advice", "Expert guidance"),
        ("🐛", "Pest Control", "Smart solutions"),
    ]
    for col, (icon, title, sub) in zip([col1, col2, col3, col4], feats):
        with col:
            st.markdown(f"""
            <div style="background:white;border-radius:18px;padding:1.8rem 1rem;
                        text-align:center;box-shadow:0 3px 14px rgba(0,0,0,0.05);
                        border:2px solid #f3f4f6;margin-bottom:1.5rem;
                        transition:all .3s ease;"
                 onmouseover="this.style.transform='translateY(-6px)';this.style.borderColor='#43a047';this.style.boxShadow='0 10px 26px rgba(76,175,80,0.14)';"
                 onmouseout ="this.style.transform='';this.style.borderColor='#f3f4f6';this.style.boxShadow='0 3px 14px rgba(0,0,0,0.05)';">
                <div style="font-size:3rem;margin-bottom:.7rem;">{icon}</div>
                <div style="font-size:1rem;font-weight:700;color:#1f2937;">{title}</div>
                <div style="font-size:.82rem;color:#6b7280;margin-top:3px;">{sub}</div>
            </div>
            """, unsafe_allow_html=True)

    # Language selection heading
    st.markdown("""
    <h3 style="font-size:1.6rem;font-weight:700;color:#1f2937;text-align:center;
               margin:2.5rem 0 1.5rem;">Choose Your Preferred Language</h3>
    """, unsafe_allow_html=True)

    # Set default language if none selected
    if st.session_state.selected_language is None:
        st.session_state.selected_language = "en"

    selected = st.session_state.selected_language

    cols = st.columns(4)
    for idx, lang in enumerate(languages):
        with cols[idx % 4]:
            is_sel = lang['code'] == selected
            if st.button(
                f"{lang['native']}\n{lang['english']}",
                key=f"lang_{lang['code']}",
                use_container_width=True,
                type="primary" if is_sel else "secondary"
            ):
                st.session_state.selected_language = lang['code']
                st.rerun()

    # Default language validation
    if st.session_state.selected_language and st.session_state.selected_language not in [l['code'] for l in languages]:
        st.session_state.selected_language = "en"

    # Continue button
    st.markdown("<div style='height:1.5rem;'></div>", unsafe_allow_html=True)
    
    lang_names = {
        "en": "English", "hi": "हिंदी", "te": "తెలుగు",
    }
    current_name = lang_names.get(st.session_state.selected_language, "English")
    
    col_left, col_center, col_right = st.columns([1, 2, 1])
    with col_center:
        if st.button(
            f"Continue with {current_name}",
            key="continue_btn",
            use_container_width=True,
            type="primary"
        ):
            st.session_state.show_welcome = False
            st.rerun()
    
    # Footer quote
    st.markdown("""
    <div style="text-align:center;padding:2.5rem 1rem 1rem;color:#9ca3af;
                font-style:italic;font-size:.9rem;">
        <div style="max-width:560px;margin:0 auto;line-height:1.6;">
            "Agriculture is our wisest pursuit, because it will in the end contribute
            most to real wealth, good morals, and happiness."
            <div style="margin-top:.4rem;font-weight:700;color:#43a047;font-style:normal;">
                — Supporting Indian Farmers 🇮🇳</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────
# Sidebar
# ─────────────────────────────────────────────────────────
def render_sidebar():
    with st.sidebar:
        st.markdown("### ⚙️ Configuration")

        online_mode = st.toggle("Enable AI Enhancement", value=True,
                                help="Use IBM Watsonx Granite LLM for enhanced responses")
        top_k = st.slider("Similar Results", 1, 10, 5,
                          help="Number of similar Q&A pairs to retrieve")

        st.markdown("---")
        st.markdown("### 🌐 Language")
        if st.session_state.selected_language:
            names = {
                "en": "English", "hi": "हिंदी", "te": "తెలుగు",
            }
            st.markdown(
                f'<span class="badge badge-info">{names.get(st.session_state.selected_language, "English")}</span>',
                unsafe_allow_html=True)
        if st.button("🌐 Change Language", use_container_width=True):
            st.session_state.show_welcome = True
            st.rerun()

        st.markdown("---")
        st.markdown("### 📡 System Status")
        if Path(FAISS_INDEX_FILE).exists():
            st.markdown('<span class="badge badge-ok">FAISS Ready</span>', unsafe_allow_html=True)
        else:
            st.markdown('<span class="badge badge-warn">FAISS Missing</span>', unsafe_allow_html=True)

        if online_mode:
            if GEMINI_API_KEY:
                st.markdown('<span class="badge badge-ok">AI Connected</span>', unsafe_allow_html=True)
            else:
                st.markdown('<span class="badge badge-warn">AI Not Configured</span>', unsafe_allow_html=True)

        return online_mode, top_k


# ─────────────────────────────────────────────────────────
# Answer card helper
# ─────────────────────────────────────────────────────────
def render_answer_card(
    title: str, 
    subtitle: str, 
    content: str, 
    card_type: str = "db"
) -> None:
    icon = "📊" if card_type == "db" else "🤖"
    css_class = "ai" if card_type == "ai" else ""
    st.markdown(f"""
    <div class="ans-card {css_class}">
        <div class="ans-card-head">
            <div class="ans-card-icon">{icon}</div>
            <div>
                <div class="ans-card-title">{title}</div>
                <div class="ans-card-sub">{subtitle}</div>
            </div>
        </div>
        <div class="ans-card-body">{content}</div>
    </div>
    """, unsafe_allow_html=True)


def render_confidence_bars(results: list) -> None:
    """Render confidence bars for retrieved results"""
    if not results:
        st.warning("No similar results found to show confidence.")
        return
        
    st.markdown("#### Confidence Scores")
    for i, r in enumerate(results[:5], 1):
        conf = max(0, 1 - (r['distance'] / 100))
        st.markdown(f"""
        <div style="margin:.75rem 0;">
            <div style="display:flex;justify-content:space-between;margin-bottom:4px;">
                <span style="font-weight:600;color:#1f2937;font-size:.88rem;">Result {i}</span>
                <span style="font-weight:700;color:#2e7d32;font-size:.88rem;">{conf*100:.1f}%</span>
            </div>
            <div class="conf-bar-bg"><div class="conf-bar-fill" style="width:{conf*100}%"></div></div>
        </div>
        """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────
# Process a query
# ─────────────────────────────────────────────────────────
def process_query(query: str, online_mode: bool, top_k: int) -> None:
    """Process user query and display results"""
    start = time.time()

    with st.spinner("🔍 Searching knowledge base..."):
        try:
            searcher = load_faiss_searcher()
            if not searcher:
                st.error("📚 Knowledge base not ready. Run `python rebuild_index.py` to initialize."); return

            watsonx = None
            if online_mode:
                watsonx = load_watsonx_service()
                if not watsonx:
                    st.warning("AI service unavailable, falling back to offline mode.")

            handler = QueryHandler(searcher, watsonx)
            result = handler.process_query(
                query, top_k=top_k,
                online_mode=online_mode and watsonx is not None)

            st.session_state.total_queries += 1
            st.session_state.successful_queries += 1
            st.session_state.query_history.append({
                'query': query,
                'timestamp': datetime.now(),
                'mode': 'online' if online_mode else 'offline'
            })

            elapsed = time.time() - start
            st.session_state.response_times.append(elapsed)

            # Show results
            st.markdown("---")
            num_results = len(result['retrieved_results'])

            if num_results == 0:
                # No FAISS matches — still try Gemini for a direct answer
                if online_mode and watsonx:
                    try:
                        direct_prompt = f"A farmer asked: '{query}'. Provide a helpful response. If it's a greeting, greet them warmly and ask how you can help with their farming needs. If it's an agricultural question, provide your best advice."
                        direct_answer = watsonx.generate_response(direct_prompt)
                        render_answer_card(
                            "AI Answer",
                            f"Watsonx Granite • {elapsed:.2f}s",
                            direct_answer.replace('\n', '<br>'),
                            "ai"
                        )
                    except Exception:
                        st.info("🔍 No closely matching results found for your query. Try rephrasing or asking about a specific crop, pest, or farming practice.")
                else:
                    st.info("🔍 No closely matching results found in the knowledge base. Enable Online Mode in the sidebar for AI-powered answers.")
            else:
                render_answer_card(
                    "Knowledge Base Answer",
                    f"Retrieved from KCC database • {elapsed:.2f}s • {num_results} matches",
                    result["offline_answer"].replace('\n', '<br>'),
                    "db"
                )

                if online_mode and result.get('online_answer'):
                    render_answer_card(
                        "AI-Enhanced Answer",
                        f"IBM Watsonx Granite • {elapsed:.2f}s",
                        result["online_answer"].replace('\n', '<br>'),
                        "ai"
                    )

                with st.expander("Detailed Insights"):
                    meta = handler.get_query_metadata(result['retrieved_results'])
                    c1, c2, c3 = st.columns(3)
                    c1.metric("Results", num_results)
                    c2.metric("Crops", len(meta.get('crops', [])))
                    c3.metric("States", len(meta.get('states', [])))
                    st.markdown("---")
                    st.markdown("#### Source Data")
                    for i, res in enumerate(result['retrieved_results'][:3], 1):
                        conf_pct = res.get('confidence', 0) * 100
                        st.markdown(f"**Source {i}** • Relevance: {conf_pct:.0f}%")
                        st.markdown(f"**Q:** {res['metadata']['question']}")
                        st.markdown(f"**A:** {res['metadata']['answer']}")
                        if i < 3:
                            st.markdown("---")

        except Exception as e:
            error_msg = str(e)
            if 'api_key' in error_msg.lower() or 'unauthorized' in error_msg.lower():
                st.error("🔑 API key issue. Please check your GEMINI_API_KEY in the .env file.")
            elif 'timeout' in error_msg.lower() or 'connection' in error_msg.lower():
                st.error("🌐 Network issue. Please check your internet connection and try again.")
            elif 'quota' in error_msg.lower() or 'rate' in error_msg.lower():
                st.error("⏳ Rate limit reached. Please wait a moment and try again.")
            else:
                st.error(f"❌ Error processing query: {error_msg}")
            import traceback
            with st.expander("Technical Details"):
                st.code(traceback.format_exc())


# ─────────────────────────────────────────────────────────
# Main application
# ─────────────────────────────────────────────────────────
def main() -> None:
    # Critical dependency check
    if not Path(FAISS_INDEX_FILE).exists():
        st.error(" FAISS index not found. Please run data preprocessing first.")
        st.code("python setup.py") # Using setup.py as found in root
        st.stop()

    if st.session_state.show_welcome:
        render_welcome_screen()
        return

    # Sidebar
    online_mode, top_k = render_sidebar()

    # ── Fixed Header ──────────────────────────────────────
    lang_names = {
        "en": "English", "hi": "हिंदी", "te": "తెలుగు",
    }
    curr_lang = lang_names.get(st.session_state.selected_language, "English")

    st.markdown(f"""
    <div class="km-header">
        <div class="km-header-logo">
            <span class="km-header-logo-icon">🌾</span>
            <span class="km-header-logo-text">Agri Advisor</span>
        </div>
        <div class="km-header-right">
            <div class="km-pill km-pill-lang">🌐 {curr_lang}</div>
            <div class="km-pill km-pill-status"><div class="km-dot"></div> Online</div>
        </div>
    </div>
    <div class="km-header-spacer"></div>
    """, unsafe_allow_html=True)

    # ── Hero area with title + feature grid ──────────────
    categories = [
        ("🌤️", "Weather", "Forecast"),
        ("💰", "Market", "Prices"),
        ("🌱", "Crop", "Advice"),
        ("🐛", "Pest", "Control"),
    ]

    category_questions = {
        "Weather": [
            "What is the weather forecast for the next 7 days in my area?",
            "Will it rain in the next 48 hours? Should I postpone spraying?",
            "What is the expected temperature range this week?",
            "Is there any extreme weather warning for my region?",
            "What is the humidity level and how will it affect my crops?",
        ],
        "Market": [
            "What are the current mandi prices for wheat in my district?",
            "Which crop is fetching the best price this season?",
            "How have onion prices changed in the last month?",
            "Where can I sell my produce for the best price?",
            "What is the MSP for paddy this year?",
        ],
        "Crop": [
            "What crops should I plant this season?",
            "What fertilizer is best during flowering stage?",
            "How to improve soil health for better yield?",
            "What is the recommended irrigation schedule for wheat?",
            "How to increase cotton yield per acre?",
        ],
        "Pest": [
            "How to control aphids in mustard crop?",
            "What is the treatment for leaf spot in tomato?",
            "How to prevent fruit borer in brinjal?",
            "What is the dosage of neem oil for pest control?",
            "How to protect paddy from blast disease?",
        ],
    }

    # ── Hero title ────────────────────────────────────────
    st.markdown("""
    <div style="text-align:center;padding:2.5rem 1rem 1rem;">
        <h2 style="font-size:2rem;font-weight:700;color:#374151;
                   margin-bottom:0.5rem;">🌾 Agri Advisor AI Agent</h2>
    </div>
    """, unsafe_allow_html=True)

    # ── Feature category buttons (4 columns) ─────────────
    active_cat_name = st.session_state.active_category or "Weather"
    cols = st.columns(4)
    for i, (icon, title, sub) in enumerate(categories):
        with cols[i]:
            btn_type = "primary" if st.session_state.active_category == title else "secondary"
            if st.button(f"{icon}\n{title}\n{sub}", key=f"cat_{title}", use_container_width=True, type=btn_type):
                st.session_state.active_category = title
                st.session_state.selected_question = None
                st.rerun()

    # ── Popular Questions header ─────────────────────────
    questions = category_questions.get(active_cat_name, category_questions["Weather"])

    st.markdown("""
    <div style="max-width:700px;margin:1.5rem auto 0.5rem;padding:0 0.5rem;">
        <span style="font-size:1.05rem;font-weight:700;color:#1f2937;">🔥 Popular Questions</span>
    </div>
    """, unsafe_allow_html=True)

    # ── Question buttons ─────────────────────────────────
    for i, q in enumerate(questions):
        if st.button(f"›  {q}", key=f"pq_{i}", use_container_width=True):
            st.session_state.selected_question = q
            st.rerun()

    # ── Search Bar (in page flow) ────────────────────────
    st.markdown('<div style="height:1.5rem;"></div>', unsafe_allow_html=True)
    input_col, send_col = st.columns([9, 1])
    with input_col:
        user_query = st.text_input(
            "Ask anything",
            value=st.session_state.selected_question or "",
            placeholder="Ask about weather, market prices, or farming advice...",
            label_visibility="collapsed",
            key="main_input"
        )
    with send_col:
        send_pressed = st.button("➤", key="send_btn")

    # ── Process query ────────────────────────────────────
    query_to_run = None
    if send_pressed and user_query:
        query_to_run = sanitize_input(user_query)
    elif st.session_state.selected_question:
        query_to_run = sanitize_input(st.session_state.selected_question)

    if query_to_run and len(query_to_run) > 0:
        # Prevent duplicate processing of the same query
        if query_to_run != st.session_state.last_processed_query:
            st.session_state.selected_question = None
            st.session_state.last_processed_query = query_to_run
            process_query(query_to_run, online_mode, top_k)
        else:
            st.session_state.selected_question = None
            process_query(query_to_run, online_mode, top_k)
    elif send_pressed and (not user_query or not user_query.strip()):
        st.warning("⚠️ Please enter a question before searching.")

    # ── Footer (like KissanAI) ───────────────────────────
    st.markdown("""
    <div class="km-footer">
        <a href="#">Home</a>
        <span style="color:#d1d5db;margin:0 0.5rem;">|</span>
        <span>© 2025 Agri Advisor</span>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
