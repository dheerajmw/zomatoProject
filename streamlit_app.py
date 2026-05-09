"""
Streamlit UI for the AI-powered Restaurant Recommendation System.
Calls Phase 2 → Phase 3 → Phase 4 directly (no FastAPI server needed).
Deploy on Streamlit Cloud: set GROQ_API_KEY in app secrets.
"""

from __future__ import annotations

import os
from pathlib import Path

# ── Step 1: inject Streamlit secrets into os.environ ─────────────────────────
# Must happen before ANY app.* import so pydantic-settings reads correct values.
import streamlit as st

try:
    for _k, _v in st.secrets.items():
        if isinstance(_v, str) and _v.strip():
            os.environ[_k] = _v
except Exception:
    pass  # local run — values already in .env / os.environ

# ── Step 2: set CSV path ──────────────────────────────────────────────────────
_SAMPLE_CSV = str(Path(__file__).parent / "tests" / "fixtures" / "zomato_full_sample.csv")
if not os.environ.get("ZOMATO_CSV_PATH"):
    os.environ["ZOMATO_CSV_PATH"] = _SAMPLE_CSV

# ── Step 3: NOW import app modules (env is fully set) ────────────────────────
# No patching needed — pydantic-settings reads os.environ at first instantiation.
from app.schemas import UserPreferences, BudgetBand
from app.phase1 import catalog_summary
from app.phase1.catalog import load_catalog, clear_catalog_cache
from app.phase2 import PreferencesValidationError
from app.phase4 import recommend

# ── Page config (must be first Streamlit call) ────────────────────────────────
st.set_page_config(
    page_title="🍽️ ForkFinder - AI Restaurant Recommendations",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* Import Enhanced Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Poppins:wght@300;400;500;600;700;800&display=swap');
    
    /* Enhanced ForkFinder Theme with Improved Color Palette */
    body, .stApp {
        font-family: 'Inter', 'Poppins', system-ui, -apple-system, sans-serif !important;
        -webkit-font-smoothing: antialiased !important;
        -moz-osx-font-smoothing: grayscale !important;
        background: #ffffff !important;
    }
    
    .forkfinder-gradient {
        background: linear-gradient(135deg, #ea580c 0%, #dc2626 100%);
    }
    
    .brand-gradient {
        background: linear-gradient(135deg, #fde68a 0%, #f97316 50%, #d946ef 100%) !important;
    }
    
    .accent-gradient {
        background: linear-gradient(135deg, #14b8a6 0%, #22c55e 50%, #84cc16 100%) !important;
    }
    
    .rank-badge {
        background: linear-gradient(135deg, #ea580c 0%, #dc2626 100%);
        color: white;
        padding: 6px 16px;
        border-radius: 25px;
        font-weight: bold;
        font-size: 14px;
        display: inline-block;
        margin-bottom: 12px;
        box-shadow: 0 2px 8px rgba(234, 88, 12, 0.4);
    }
    
    /* Restaurant Cards - Theme Support */
    .restaurant-card {
        background: white;
        border: 1px solid #e5e7eb;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        transition: all 0.3s ease;
        overflow: hidden;
    }
    
    /* Enhanced Restaurant Cards - Theme Support */
    .restaurant-card {
        background: white;
        border: 1px solid #e5e7eb;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        transition: all 0.3s ease;
        overflow: hidden;
    }
    
    /* Light theme specific restaurant card styling */
    [data-theme="light"] .restaurant-card {
        background: linear-gradient(135deg, #fed7aa 0%, #fbbf24 50%, #fb923c 100%);
        border: 1px solid #f59e0b;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        box-shadow: 0 2px 8px rgba(251, 146, 60, 0.2), 0 1px 2px rgba(251, 146, 60, 0.3);
        transition: all 0.3s ease;
        overflow: hidden;
        position: relative;
    }
    
    [data-theme="light"] .restaurant-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, #ea580c 0%, #dc2626 50%, #ea580c 100%);
        background-size: 200% 100%;
        animation: shimmer 3s ease-in-out infinite;
    }
    
    /* Dark theme specific restaurant card styling */
    [data-theme="dark"] .restaurant-card {
        background: linear-gradient(135deg, #0a0a0a 0%, #1a1a1a 100%);
        border: 1px solid #2a2a2a;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.4), 0 1px 2px rgba(0,0,0,0.6);
        transition: all 0.3s ease;
        overflow: hidden;
        position: relative;
    }
    
    [data-theme="dark"] .restaurant-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, #ea580c 0%, #dc2626 50%, #ea580c 100%);
        background-size: 200% 100%;
        animation: shimmer 3s ease-in-out infinite;
    }
    
    /* Enhanced Restaurant Name Cards - Theme Support */
    .restaurant-name {
        font-family: 'Poppins', 'Inter', system-ui, -apple-system, sans-serif;
        font-weight: 800;
        font-size: 1.5rem;
        line-height: 1.2;
        margin-bottom: 0.75rem;
        letter-spacing: -0.025em;
        transition: all 0.3s ease;
    }
    
    /* Light theme restaurant name styling */
    [data-theme="light"] .restaurant-name {
        color: #1f2937;
        font-family: 'Poppins', 'Inter', system-ui, -apple-system, sans-serif;
        font-weight: 800;
        font-size: 1.5rem;
        line-height: 1.2;
        margin-bottom: 0.75rem;
        letter-spacing: -0.025em;
        text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
        transition: all 0.3s ease;
        position: relative;
    }
    
    [data-theme="light"] .restaurant-name::after {
        content: '';
        position: absolute;
        bottom: -2px;
        left: 0;
        width: 0;
        height: 2px;
        background: linear-gradient(90deg, #ea580c 0%, #dc2626 100%);
        transition: width 0.3s ease;
    }
    
    [data-theme="light"] .restaurant-card:hover .restaurant-name::after {
        width: 100%;
    }
    
    /* Dark theme restaurant name styling */
    [data-theme="dark"] .restaurant-name {
        color: #ffffff;
        font-family: 'Poppins', 'Inter', system-ui, -apple-system, sans-serif;
        font-weight: 800;
        font-size: 1.5rem;
        line-height: 1.2;
        margin-bottom: 0.75rem;
        letter-spacing: -0.025em;
        text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
        transition: all 0.3s ease;
        position: relative;
    }
    
    [data-theme="dark"] .restaurant-name::after {
        content: '';
        position: absolute;
        bottom: -2px;
        left: 0;
        width: 0;
        height: 2px;
        background: linear-gradient(90deg, #ea580c 0%, #dc2626 100%);
        transition: width 0.3s ease;
    }
    
    [data-theme="dark"] .restaurant-card:hover .restaurant-name::after {
        width: 100%;
    }
    
    /* Restaurant name hover effects */
    .restaurant-card:hover .restaurant-name {
        transform: translateY(-1px);
        filter: brightness(1.1);
    }
    
    [data-theme="light"] .restaurant-card:hover .restaurant-name {
        color: #374151;
    }
    
    [data-theme="dark"] .restaurant-card:hover .restaurant-name {
        color: #f9fafb;
    }
    
    /* Restaurant name gradient effect for special restaurants */
    .restaurant-name.featured {
        background: linear-gradient(135deg, #ea580c 0%, #dc2626 50%, #ea580c 100%);
        background-size: 200% 200%;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        animation: gradient-shift 3s ease infinite;
    }
    
    @keyframes gradient-shift {
        0% {
            background-position: 0% 50%;
        }
        50% {
            background-position: 100% 50%;
        }
        100% {
            background-position: 0% 50%;
        }
    }
    
    /* Light theme restaurant rating color */
    [data-theme="light"] .restaurant-rating {
        color: #ea580c;
        font-weight: 600;
        font-size: 0.875rem;
    }
    
    /* Dark theme restaurant rating color */
    [data-theme="dark"] .restaurant-rating {
        color: #ea580c;
        font-weight: 600;
        font-size: 0.875rem;
    }
    
    /* Light theme restaurant cost color */
    [data-theme="light"] .restaurant-cost {
        color: #6b7280;
        font-weight: 500;
        font-size: 0.875rem;
    }
    
    /* Dark theme restaurant cost color */
    [data-theme="dark"] .restaurant-cost {
        color: #9ca3af;
        font-weight: 500;
        font-size: 0.875rem;
    }
    
    /* Light theme restaurant address color */
    [data-theme="light"] .restaurant-address {
        color: #6b7280;
        font-size: 0.875rem;
        margin-top: 0.5rem;
    }
    
    /* Dark theme restaurant address color */
    [data-theme="dark"] .restaurant-address {
        color: #9ca3af;
        font-size: 0.875rem;
        margin-top: 0.5rem;
    }
    
    /* Light theme cuisine tags */
    [data-theme="light"] .cuisine-tag {
        background: linear-gradient(135deg, #fef3c7 0%, #fed7aa 100%);
        color: #92400e;
        border: 1px solid #fbbf24;
        padding: 0.25rem 0.5rem;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        margin: 0.125rem;
        display: inline-block;
    }
    
    /* Dark theme cuisine tags */
    [data-theme="dark"] .cuisine-tag {
        background: linear-gradient(135deg, #451a03 0%, #78350f 100%);
        color: #fed7aa;
        border: 1px solid #92400e;
        padding: 0.25rem 0.5rem;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        margin: 0.125rem;
        display: inline-block;
    }
    
    /* Light theme feature tags */
    [data-theme="light"] .feature-tag {
        background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%);
        color: #1e40af;
        border: 1px solid #3b82f6;
        padding: 0.25rem 0.5rem;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 500;
        margin: 0.125rem;
        display: inline-block;
    }
    
    /* Dark theme feature tags */
    [data-theme="dark"] .feature-tag {
        background: linear-gradient(135deg, #1e3a8a 0%, #1e40af 100%);
        color: #bfdbfe;
        border: 1px solid #3b82f6;
        padding: 0.25rem 0.5rem;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 500;
        margin: 0.125rem;
        display: inline-block;
    }
    
    .restaurant-card:hover {
        box-shadow: 0 4px 16px rgba(249, 115, 22, 0.12);
        transform: translateY(-1px);
    }
    
    .restaurant-header {
        background: linear-gradient(135deg, #ea580c 0%, #c2410c 50%, #dc2626 100%);
        padding: 1rem 1.5rem;
        position: relative;
    }
    
    .restaurant-header::after {
        content: '';
        position: absolute;
        bottom: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, #ea580c 0%, #c2410c 50%, #dc2626 100%);
        animation: shimmer 2s ease-in-out infinite;
    }
    
    .restaurant-content {
        padding: 1.5rem;
    }
    
    .cuisine-tag {
        background: linear-gradient(135deg, #fef7ed 0%, #fed7aa 100%);
        color: #7c2d12;
        border: 1px solid #fb923c;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
        margin-right: 8px;
        margin-bottom: 6px;
        display: inline-block;
        font-family: 'Inter', 'Poppins', system-ui, -apple-system, sans-serif;
        transition: all 0.3s ease;
    }
    
    .cuisine-tag:hover {
        background: linear-gradient(135deg, #fed7aa 0%, #fdba74 100%);
        transform: translateY(-1px);
        box-shadow: 0 2px 8px rgba(249, 115, 22, 0.3);
    }
    
    .tag-pill {
        background: linear-gradient(135deg, #f0fdfa 0%, #ccfbf1 100%);
        color: #134e4a;
        border: 1px solid #14b8a6;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
        margin-right: 8px;
        margin-bottom: 4px;
        display: inline-block;
        font-family: 'Inter', 'Poppins', system-ui, -apple-system, sans-serif;
        transition: all 0.3s ease;
    }
    
    .tag-pill:hover {
        background: linear-gradient(135deg, #99f6e4 0%, #5eead4 100%);
        transform: translateY(-1px);
        box-shadow: 0 2px 8px rgba(20, 184, 166, 0.3);
    }
    
    .ai-explanation {
        background: linear-gradient(135deg, #fffdf7 0%, #fefbf0 100%);
        border-left: 4px solid #f97316;
        padding: 16px 20px;
        border-radius: 12px;
        margin: 16px 0;
        font-style: italic;
        color: #404040;
        font-size: 14px;
        font-family: 'Inter', 'Poppins', system-ui, -apple-system, sans-serif;
        box-shadow: 0 2px 8px rgba(249, 115, 22, 0.1);
    }
    
    .stat-box {
        background: linear-gradient(135deg, #ea580c 0%, #c2410c 50%, #dc2626 100%);
        color: white;
        padding: 1rem;
        border-radius: 12px;
        text-align: center;
        box-shadow: 0 4px 12px rgba(234, 88, 12, 0.4);
    }
    
    .stat-number {
        font-size: 1.5rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
        font-family: 'Poppins', 'Inter', system-ui, -apple-system, sans-serif;
        animation: gradient-shift 3s ease infinite;
        background-size: 200% 200%;
        background: linear-gradient(135deg, #ffffff 0%, #fed7aa 50%, #fbbf24 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        animation: gradient-shift 3s ease infinite;
        background-size: 200% 200%;
    }
    
    /* Header styling */
    .main-header {
        background: linear-gradient(135deg, #ea580c 0%, #dc2626 100%);
        padding: 2rem;
        border-radius: 16px;
    }
    
    /* Enhanced Animations */
    @keyframes shimmer {
        0% {
            transform: translateX(-100%);
        }
        100% {
            transform: translateX(100%);
        }
    }

    @keyframes gradient-shift {
        0% {
            background-position: 0% 50%;
        }
        50% {
            background-position: 100% 50%;
        }
        100% {
            background-position: 0% 50%;
        }
    }

    /* Enhanced Interactive Elements */
    [data-testid="stButton"] > button[kind="primary"] {
        background: linear-gradient(135deg, #ea580c 0%, #c2410c 50%, #dc2626 100%) !important;
        border: none !important;
        color: white !important;
        font-weight: 600 !important;
        border-radius: 8px !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 12px rgba(234, 88, 12, 0.4) !important;
    }
    
    [data-testid="stButton"] > button[kind="primary"]:hover {
        background: linear-gradient(135deg, #c2410c 0%, #b91c1c 50%, #991b1b 100%) !important;
        box-shadow: 0 6px 20px rgba(234, 88, 12, 0.5) !important;
        transform: translateY(-2px) !important;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #ea580c 0%, #dc2626 100%);
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s ease;
        cursor: pointer;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #c2410c 0%, #b91c1c 100%) !important;
        box-shadow: 0 6px 20px rgba(234, 88, 12, 0.5) !important;
        transform: translateY(-2px) !important;
    }

    .stTextInput > div > div > input,
    .stSelectbox > div > div > select,
    .stSlider > div > div > div {
        border: 2px solid #e5e5e5 !important;
        border-radius: 16px !important;
        padding: 0.875rem !important;
        transition: all 0.3s ease !important;
        background: linear-gradient(135deg, #ffffff 0%, #fafafa 100%) !important;
        font-family: 'Inter', 'Poppins', system-ui, -apple-system, sans-serif !important;
        font-size: 0.95rem !important;
    }

    .stTextInput > div > div > input:focus,
    .stSelectbox > div > div > select:focus,
    .stSlider > div > div > div:focus {
        border-color: #ea580c !important;
        box-shadow: 0 0 0 4px rgba(234, 88, 12, 0.15) !important;
        background: linear-gradient(135deg, #ffffff 0%, #fef2f2 100%) !important;
    }

    /* Enhanced Sidebar */
    .stSidebar {
        background: linear-gradient(135deg, #fffdf7 0%, #fefbf0 100%) !important;
        border-right: 1px solid #e5e5e5 !important;
        box-shadow: 4px 0 20px rgba(0, 0, 0, 0.05) !important;
    }

    .stSidebar .stMarkdown {
        color: #171717 !important;
        font-family: 'Inter', 'Poppins', system-ui, -apple-system, sans-serif !important;
    }

    .stSidebar h1, .stSidebar h2, .stSidebar h3 {
        font-family: 'Poppins', 'Inter', system-ui, -apple-system, sans-serif !important;
        font-weight: 600 !important;
        letter-spacing: -0.025em !important;
    }
    
    /* Dark Theme Support - Most aggressive approach */
    html, body {
        background: #000000 !important;
        background-color: #000000 !important;
    }
    
    .stApp, .stApp * {
        background: #000000 !important;
        background-color: #000000 !important;
    }
    
    [data-testid="stAppViewContainer"],
    [data-testid="stAppViewContainer"] * {
        background: #000000 !important;
        background-color: #000000 !important;
    }
    
        
    /* Override any background in dark theme only */
    [data-theme="dark"] [style*="background"],
    [data-theme="dark"] [style*="background-color"] {
        background: #000000 !important;
        background-color: #000000 !important;
    }
    
    /* Light theme - white background - maximum specificity */
    body[data-theme="light"],
    html[data-theme="light"],
    .stApp[data-theme="light"] {
        background: #ffffff !important;
        background-color: #ffffff !important;
    }
    
    /* Force white background for all elements in light theme */
    body:not([data-theme="dark"]):not(.stApp),
    html:not([data-theme="dark"]):not(.stApp),
    .stApp:not([data-theme="dark"]) {
        background: #ffffff !important;
        background-color: #ffffff !important;
    }
    
    /* Override any non-white backgrounds in light theme */
    body:not([data-theme="dark"]):not(.stApp) *,
    html:not([data-theme="dark"]):not(.stApp) *,
    .stApp:not([data-theme="dark"]) * {
        background: #ffffff !important;
        background-color: #ffffff !important;
    }
    
    /* Force white for specific containers in light theme */
    body:not([data-theme="dark"]) .element-container,
    body:not([data-theme="dark"]) .block-container,
    body:not([data-theme="dark"]) .stVerticalBlock,
    body:not([data-theme="dark"]) .stHorizontalBlock {
        background: #ffffff !important;
        background-color: #ffffff !important;
    }
    
    /* Restaurant Cards - Enhanced Dark Theme */
    .restaurant-card {
        background: #0a0a0a !important;
        border: 1px solid #1a1a1a !important;
        color: #ffffff !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.4) !important;
        padding: 0 !important;
        margin: 0.5rem 0 !important;
    }
    
    .restaurant-card:hover {
        box-shadow: 0 4px 16px rgba(234, 88, 12, 0.15) !important;
        transform: translateY(-1px) !important;
        border-color: #ea580c !important;
        background: #0f0f0f !important;
    }
    
    .restaurant-header {
        background: #0f0f0f !important;
        border-bottom: 1px solid #1a1a1a !important;
        padding: 0.75rem !important;
    }
    
    .restaurant-content {
        background: #0a0a0a !important;
        color: #ffffff !important;
        padding: 0.75rem !important;
    }
    
    .restaurant-name {
        color: #ffffff !important;
        font-weight: 700 !important;
        margin: 0 !important;
    }
    
    .restaurant-rating {
        color: #ea580c !important;
        font-weight: 600 !important;
        margin: 0.25rem 0 !important;
    }
    
    .restaurant-cost {
        color: #d4d4d8 !important;
        font-weight: 500 !important;
        margin: 0.25rem 0 !important;
    }
    
    .restaurant-address {
        color: #888888 !important;
        font-size: 0.85rem !important;
        margin: 0.5rem 0 0 !important;
    }
    
    .cuisine-tag {
        background: #ea580c !important;
        color: #ffffff !important;
        border: none !important;
        padding: 0.25rem 0.5rem !important;
        margin: 0.125rem !important;
        font-size: 0.75rem !important;
        font-weight: 600 !important;
    }
    
    .cuisine-tag:hover {
        background: #dc2626 !important;
        transform: scale(1.05) !important;
    }
    
    .tag-pill {
        background: #1a1a1a !important;
        color: #ffffff !important;
        border: 1px solid #333333 !important;
        padding: 0.25rem 0.5rem !important;
        margin: 0.125rem !important;
        font-size: 0.75rem !important;
        font-weight: 500 !important;
    }
    
    .tag-pill:hover {
        background: #2a2a2a !important;
        border-color: #ea580c !important;
    }
    
    .ai-explanation {
        background: #0f0f0f !important;
        border-left: 3px solid #ea580c !important;
        color: #e5e5e5 !important;
        border: 1px solid #1a1a1a !important;
        padding: 1rem !important;
        margin: 0.5rem 0 !important;
    }
    
        
    /* Force dark background on all container elements */
    [data-theme="dark"] div,
    [data-theme="dark"] main,
    [data-theme="dark"] section,
    [data-theme="dark"] [data-testid="stAppViewContainer"],
    [data-theme="dark"] [data-testid="stAppViewContainer"] > div,
    [data-theme="dark"] [data-testid="stAppViewContainer"] > div > div,
    [data-theme="dark"] [data-testid="stAppViewContainer"] > div > div > div,
    [data-theme="dark"] .main,
    [data-theme="dark"] .element-container,
    [data-theme="dark"] .block-container,
    [data-theme="dark"] .stVerticalBlock,
    .stApp.darkTheme [data-testid="stAppViewContainer"],
    .stApp.darkTheme [data-testid="stAppViewContainer"] > div,
    .stApp.darkTheme [data-testid="stAppViewContainer"] > div > div {
        background: #000000 !important;
        background-color: #000000 !important;
    }
    
    /* Force transparent for containers in dark theme */
    .stApp.darkTheme div,
    .stApp.darkTheme main,
    .stApp.darkTheme section,
    .stApp.darkTheme .element-container,
    .stApp.darkTheme .block-container,
    .stApp.darkTheme .stVerticalBlock,
    .stApp.darkTheme .stHorizontalBlock {
        background: transparent !important;
        background-color: transparent !important;
    }
    
    .stApp.darkTheme .restaurant-card {
        background: #2a2a2a !important;
        border: 1px solid #404040 !important;
        color: #ffffff !important;
    }
    
    .stApp.darkTheme .restaurant-content {
        color: #ffffff !important;
    }
    
    .stApp.darkTheme .restaurant-header {
        background: linear-gradient(135deg, #ea580c 0%, #c2410c 50%, #dc2626 100%) !important;
    }
    
    .stApp.darkTheme .cuisine-tag {
        background: linear-gradient(135deg, #7c2d12 0%, #ea580c 100%) !important;
        color: white !important;
        border: 1px solid #c2410c !important;
    }
    
    .stApp.darkTheme .cuisine-tag:hover {
        background: linear-gradient(135deg, #c2410c 0%, #b91c1c 100%) !important;
    }
    
    .stApp.darkTheme .tag-pill {
        background: linear-gradient(135deg, #ea580c 0%, #dc2626 100%) !important;
        color: white !important;
        border: 1px solid #c2410c !important;
    }
    
    .stApp.darkTheme .tag-pill:hover {
        background: linear-gradient(135deg, #c2410c 0%, #b91c1c 100%) !important;
    }
    
    .stApp.darkTheme .ai-explanation {
        background: linear-gradient(135deg, #2a2a2a 0%, #1f1f1f 100%) !important;
        border-left: 4px solid #ea580c !important;
        color: #e5e5e5 !important;
    }
    
    .stApp.darkTheme .stat-box {
        background: linear-gradient(135deg, #ea580c 0%, #c2410c 50%, #dc2626 100%) !important;
        color: white !important;
    }
    
    .stApp.darkTheme .main-header {
        background: linear-gradient(135deg, #ea580c 0%, #dc2626 100%) !important;
    }
    
    .stApp.darkTheme .stTextInput > div > div > input,
    .stApp.darkTheme .stSelectbox > div > div > select,
    .stApp.darkTheme .stSlider > div > div > div {
        background: #2a2a2a !important;
        color: #ffffff !important;
        border: 2px solid #404040 !important;
    }
    
    .stApp.darkTheme .stTextInput > div > div > input:focus,
    .stApp.darkTheme .stSelectbox > div > div > select:focus,
    .stApp.darkTheme .stSlider > div > div > div:focus {
        border-color: #ea580c !important;
        background: linear-gradient(135deg, #2a2a2a 0%, #1f1f1f 100%) !important;
    }
    
    .stApp.darkTheme .stSidebar {
        background: linear-gradient(135deg, #2a2a2a 0%, #1f1f1f 100%) !important;
        border-right: 1px solid #404040 !important;
    }
    
    .stApp.darkTheme .stSidebar .stMarkdown {
        color: #ffffff !important;
    }
    
    .stApp.darkTheme .stSidebar h1, 
    .stApp.darkTheme .stSidebar h2, 
    .stApp.darkTheme .stSidebar h3 {
        color: #ffffff !important;
    }
    
    .stApp.darkTheme .stMarkdown {
        color: #e5e5e5 !important;
    }
    
    .stApp.darkTheme h1, 
    .stApp.darkTheme h2, 
    .stApp.darkTheme h3,
    .stApp.darkTheme h4,
    .stApp.darkTheme h5,
    .stApp.darkTheme h6 {
        color: #ffffff !important;
    }
    
    .stApp.darkTheme p, 
    .stApp.darkTheme span, 
    .stApp.darkTheme div {
        color: #e5e5e5 !important;
    }
    
    .stApp.darkTheme .stButton > button {
        background: linear-gradient(135deg, #ea580c 0%, #dc2626 100%) !important;
        color: white !important;
    }
    
    .stApp.darkTheme .stButton > button:hover {
        background: linear-gradient(135deg, #c2410c 0%, #b91c1c 100%) !important;
    }
    
    /* Alternative dark theme detection */
    [data-testid="stAppViewContainer"][data-theme="dark"] .restaurant-card {
        background: #2a2a2a !important;
        border: 1px solid #404040 !important;
        color: #ffffff !important;
    }
    
    [data-testid="stAppViewContainer"][data-theme="dark"] .restaurant-content {
        color: #ffffff !important;
    }
    
    [data-testid="stAppViewContainer"][data-theme="dark"] .cuisine-tag {
        background: linear-gradient(135deg, #7c2d12 0%, #ea580c 100%) !important;
        color: white !important;
        border: 1px solid #c2410c !important;
    }
    
    [data-testid="stAppViewContainer"][data-theme="dark"] .tag-pill {
        background: linear-gradient(135deg, #ea580c 0%, #dc2626 100%) !important;
        color: white !important;
        border: 1px solid #c2410c !important;
    }
    
    [data-testid="stAppViewContainer"][data-theme="dark"] .stSidebar {
        background: linear-gradient(135deg, #2a2a2a 0%, #1f1f1f 100%) !important;
        border-right: 1px solid #404040 !important;
    }
    
    [data-testid="stAppViewContainer"][data-theme="dark"] .stMarkdown {
        color: #e5e5e5 !important;
    }
    
    .stRadio > div,
    .stCheckbox > div {
        cursor: pointer;
    }
    
    .stRadio > div > label,
    .stCheckbox > div > label {
        cursor: pointer;
    }
    
    /* Slider cursor styling */
    .stSlider > div > div > div {
        cursor: pointer;
    }
    
    /* Button cursor styling */
    .stButton > button {
        background: linear-gradient(135deg, #f97316 0%, #ef4444 100%);
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s ease;
        cursor: pointer;
    }
    
    /* Slider styling */
    .stSlider > div > div > div {
        background: linear-gradient(90deg, #f97316 0%, #ef4444 100%);
        cursor: pointer;
    }
    
    /* Quick search dropdown cursor styling */
    .stSelectbox[data-testid="stSelectbox"] > div > div {
        cursor: pointer !important;
    }
    
    /* All interactive elements cursor styling */
    [data-testid="stSelectbox"],
    [data-testid="stMultiSelect"],
    [data-testid="stTextInput"],
    [data-testid="stNumberInput"],
    [data-testid="stTextArea"],
    [data-testid="stRadio"],
    [data-testid="stCheckbox"],
    [data-testid="stSlider"],
    [data-testid="stButton"] {
        cursor: pointer !important;
    }
    
    /* Preferences section styling */
    .preferences-section {
        background: linear-gradient(135deg, #fff7ed 0%, #ffffff 100%);
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 4px 12px rgba(249, 115, 22, 0.1);
        border: 1px solid rgba(249, 115, 22, 0.2);
    }
    
    /* Two-column preferences layout */
    .preferences-columns > div {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
        border: 1px solid #e5e7eb;
        margin-bottom: 1rem;
        transition: all 0.3s ease;
    }
    
    .preferences-columns > div:hover {
        box-shadow: 0 4px 16px rgba(249, 115, 22, 0.15);
        transform: translateY(-2px);
    }
    
    /* Metric styling */
    .stMetric {
        background: white;
        border: 1px solid #e5e7eb;
        border-radius: 12px;
        padding: 1rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    }
    
    /* Success/Error styling */
    .stSuccess {
        background: linear-gradient(135deg, #bbf7d0 0%, #86efac 100%);
        border-left: 4px solid #22c55e;
        color: #14532d;
    }
    
    .stError {
        background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%);
        border-left: 4px solid #ef4444;
        color: #7f1d1d;
    }
    
    .stWarning {
        background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
        border-left: 4px solid #f59e0b;
        color: #78350f;
    }
    
    .stInfo {
        background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%);
        border-left: 4px solid #3b82f6;
        color: #1e40af;
    }
</style>
""", unsafe_allow_html=True)

# JavaScript to force light theme white background
st.markdown("""
<script>
// Comprehensive light theme background enforcement
function forceLightThemeBackground() {
    const isLightTheme = !document.body.getAttribute('data-theme') || 
                         document.body.getAttribute('data-theme') !== 'dark';
    
    if (isLightTheme) {
        // Force white background with maximum specificity
        const style = document.createElement('style');
        style.textContent = `
            body, html, .stApp {
                background: #ffffff !important;
                background-color: #ffffff !important;
            }
            
            body:not([data-theme="dark"]):not(.stApp),
            html:not([data-theme="dark"]):not(.stApp),
            .stApp:not([data-theme="dark"]) {
                background: #ffffff !important;
                background-color: #ffffff !important;
            }
            
            body:not([data-theme="dark"]):not(.stApp) *,
            html:not([data-theme="dark"]):not(.stApp) *,
            .stApp:not([data-theme="dark"]) * {
                background: #ffffff !important;
                background-color: #ffffff !important;
            }
        `;
        document.head.appendChild(style);
        
        // Direct DOM manipulation
        document.body.style.background = '#ffffff';
        document.body.style.backgroundColor = '#ffffff';
        document.documentElement.style.background = '#ffffff';
        document.documentElement.style.backgroundColor = '#ffffff';
        
        // Apply to all elements
        const allElements = document.querySelectorAll('*');
        allElements.forEach(el => {
            if (!el.closest('[data-theme="dark"]')) {
                el.style.background = '#ffffff';
                el.style.backgroundColor = '#ffffff';
            }
        });
    }
}

// Run immediately and continuously check
forceLightThemeBackground();
setInterval(forceLightThemeBackground, 500);

// Also check for theme changes
const observer = new MutationObserver(forceLightThemeBackground);
observer.observe(document.body, { 
    attributes: true, 
    attributeFilter: ['data-theme'] 
});
</script>
""", unsafe_allow_html=True)



# ── Helpers ───────────────────────────────────────────────────────────────────

BUDGET_LABELS = {
    BudgetBand.low:    "💰 Low  (under ₹500)",
    BudgetBand.medium: "💰💰 Medium  (₹500 – ₹1000)",
    BudgetBand.high:   "💰💰💰 High  (above ₹1000)",
}

BUDGET_FROM_LABEL = {v: k for k, v in BUDGET_LABELS.items()}

CUISINE_OPTIONS = [
    "North Indian", "South Indian", "Chinese", "Mughlai", "Continental",
    "Italian", "Mexican", "Thai", "Japanese", "Biryani", "Kerala",
    "Bengali", "Gujarati", "Rajasthani", "Fast Food", "Cafe", "Bakery",
    "Street Food", "Seafood", "Pizza", "Burger", "Desserts",
]

OPTIONAL_TAG_OPTIONS = [
    "online-order", "book-table", "family-friendly", "quick-service",
]

QUICK_SEARCHES = {
    "🍛 Delhi • High • North Indian + Mughlai": {
        "location": "Delhi", "budget": BudgetBand.high,
        "cuisines": ["North Indian", "Mughlai"], "minimum_rating": 3.5,
    },
    "🍜 Bangalore • Medium • Chinese + Continental": {
        "location": "Bangalore", "budget": BudgetBand.medium,
        "cuisines": ["Chinese", "Continental"], "minimum_rating": 3.5,
    },
    "🍕 Mumbai • High • Italian + Continental": {
        "location": "Mumbai", "budget": BudgetBand.high,
        "cuisines": ["Italian", "Continental"], "minimum_rating": 4.0,
    },
    "🥘 Hyderabad • Low • Biryani + South Indian": {
        "location": "Hyderabad", "budget": BudgetBand.low,
        "cuisines": ["Biryani", "South Indian"], "minimum_rating": 3.5,
    },
}


def get_catalog():
    """Load catalog once per session via session_state.
    Cache key includes the CSV path so it invalidates when the source changes.
    Avoids pickle incompatibility between Pydantic models and st.cache_resource on Python 3.9.
    """
    csv_path = os.environ.get("ZOMATO_CSV_PATH", "")
    cache_key = f"catalog__{csv_path}"
    if cache_key not in st.session_state:
        # Clear any stale catalog from a previous CSV path
        for k in list(st.session_state.keys()):
            if k.startswith("catalog__"):
                del st.session_state[k]
        from app.phase1.catalog import clear_catalog_cache
        clear_catalog_cache()
        from app.phase1.catalog import load_catalog
        st.session_state[cache_key] = load_catalog()
    return st.session_state[cache_key]

def get_top_cities(catalog, limit=8):
    """Get top cities by restaurant count."""
    from collections import Counter
    city_counts = Counter(restaurant.city for restaurant in catalog)
    top_cities = city_counts.most_common(limit)
    return [city for city, count in top_cities]

def star_rating(rating: float) -> str:
    full = int(rating)
    return "⭐" * full + f"  **{rating}**"


def budget_display(band: BudgetBand) -> str:
    return {
        BudgetBand.low: "₹0 – ₹500",
        BudgetBand.medium: "₹500 – ₹1,000",
        BudgetBand.high: "₹1,000+",
    }[band]

# ── Main area ─────────────────────────────────────────────────────────────────

# Enhanced ForkFinder Header - Dark Theme Friendly
st.markdown("""
<div style="text-align: center; padding: 1.5rem 0 1rem 0; margin-bottom: 0.5rem; background: #000000; border-radius: 20px; position: relative; overflow: hidden;">
    <div style="display: flex; align-items: center; justify-content: center; gap: 1rem;">
        <div style="font-size: 3rem; margin-bottom: 0.5rem; animation: pulse 2s ease-in-out infinite;">🍽️</div>
    </div>
    <h1 style="color: #ea580c; font-size: 2.5rem; font-weight: 900; margin: 0;">
        ForkFinder
    </h1>
    <p style="color: #e5e5e5; font-size: 1rem; margin: 0.5rem 0; font-weight: 500; letter-spacing: 0.5px;">
        🤖 <span style="color: #ea580c; font-weight: 600;">AI-Powered</span> Restaurant Discovery
    </p>
    <div style="margin-top: 0.75rem; display: flex; justify-content: center; gap: 1rem; flex-wrap: wrap;">
        <span style="background: linear-gradient(135deg, #ea580c 0%, #dc2626 100%); color: white; padding: 0.25rem 0.75rem; border-radius: 20px; font-size: 0.8rem; font-weight: 600; box-shadow: 0 2px 8px rgba(234, 88, 12, 0.3);">
            🚀 Groq LLM
        </span>
        <span style="background: linear-gradient(135deg, #10b981 0%, #059669 100%); color: white; padding: 0.25rem 0.75rem; border-radius: 20px; font-size: 0.8rem; font-weight: 600; box-shadow: 0 2px 8px rgba(16, 185, 129, 0.3);">
            📊 Real-time Data
        </span>
        <span style="background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%); color: white; padding: 0.25rem 0.75rem; border-radius: 20px; font-size: 0.8rem; font-weight: 600; box-shadow: 0 2px 8px rgba(59, 130, 246, 0.3);">
            🎯 Smart Filters
        </span>
    </div>
    <style>
        @keyframes float {
            0%, 100% { transform: translateY(0px); }
            50% { transform: translateY(-10px); }
        }
        @keyframes pulse {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.05); }
        }
        @keyframes shimmer {
            0% { transform: translateX(-100%); }
            100% { transform: translateX(100%); }
        }
        @keyframes glow {
            0%, 100% { filter: brightness(1); }
            50% { filter: brightness(1.2); }
        }
    </style>
</div>
""", unsafe_allow_html=True)

# Load catalog data quietly
with st.spinner("Loading restaurant catalog…"):
    try:
        cat = get_catalog()
        summary = catalog_summary(cat)
        top_cities = get_top_cities(cat, 8)
    except Exception as e:
        st.error(f"Failed to load catalog: {e}")
        st.info("Make sure `GROQ_API_KEY` is set and the dataset is accessible.")
        st.stop()

# Compact stats row
col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
with col1:
    st.markdown(f'<div style="text-align: center; padding: 0.5rem; background: #f9fafb; border-radius: 8px; margin: 0.25rem;"><div style="font-size: 1.2rem; font-weight: 700; color: #f97316;">{summary.row_count:,}</div><div style="font-size: 0.8rem; color: #6b7280;">Restaurants</div></div>', unsafe_allow_html=True)
with col2:
    st.markdown(f'<div style="text-align: center; padding: 0.5rem; background: #f9fafb; border-radius: 8px; margin: 0.25rem;"><div style="font-size: 1.2rem; font-weight: 700; color: #f97316;">{summary.unique_cities}</div><div style="font-size: 0.8rem; color: #6b7280;">Cities</div></div>', unsafe_allow_html=True)
with col3:
    st.markdown(f'<div style="text-align: center; padding: 0.5rem; background: #f9fafb; border-radius: 8px; margin: 0.25rem;"><div style="font-size: 1.2rem; font-weight: 700; color: #f97316;">6</div><div style="font-size: 0.8rem; color: #6b7280;">AI Phases</div></div>', unsafe_allow_html=True)
with col4:
    st.markdown(f'<div style="text-align: center; padding: 0.5rem; background: #f9fafb; border-radius: 8px; margin: 0.25rem;"><div style="font-size: 1.2rem; font-weight: 700; color: #f97316;">100%</div><div style="font-size: 0.8rem; color: #6b7280;">Grounded</div></div>', unsafe_allow_html=True)

# ── Preferences Section (moved from sidebar) ───────────────────────────────────


# Quick Search Section
st.markdown("### ⚡ Quick Search")
quick = st.selectbox(
    "Pick a preset",
    ["— choose —"] + list(QUICK_SEARCHES.keys()),
    label_visibility="collapsed",
    help="Choose a pre-configured preference set"
)

# Manual Preferences in Columns
st.markdown("### 🎯 Your Preferences")

# Create two-column layout for better organization
pref_col1, pref_col2 = st.columns(2)

with pref_col1:
    # Location Dropdown
    location = st.selectbox(
        "📍 Location",
        top_cities,
        help="Select from top cities by restaurant count",
        index=0  # Default to first city
    )
    
    # Budget Selection
    budget_label = st.radio(
        "💰 Budget",
        list(BUDGET_LABELS.values()),
        index=1,
        help="Select your preferred price range"
    )
    budget = BUDGET_FROM_LABEL[budget_label]
    
    # Minimum Rating
    minimum_rating = st.slider(
        "⭐ Minimum Rating",
        min_value=1.0, max_value=5.0,
        value=3.5, step=0.1,
        help="Restaurants below this rating are excluded",
        format="%.1f ⭐"
    )
    
    # Rating indicator
    st.markdown(f"""
    <div style="text-align: center; padding: 0.5rem; background: linear-gradient(90deg, #fee2e2 0%, #fef3c7 50%, #dcfce7 100%); border-radius: 8px; margin-top: 0.5rem;">
        <span style="font-weight: 600; color: #374151;">Filtering for restaurants rated ⭐ {minimum_rating} and above</span>
    </div>
    """, unsafe_allow_html=True)

with pref_col2:
    # Cuisine Selection
    cuisines = st.multiselect(
        "🍴 Cuisines (pick at least one)",
        CUISINE_OPTIONS,
        help="Select one or more cuisines you prefer",
    )
    
    # Optional Tags
    optional_tags = st.multiselect(
        "🏷️ Optional Tags",
        OPTIONAL_TAG_OPTIONS,
        help="Filter by restaurant features"
    )
    
    # Top Results
    top_k = st.slider("🏆 Top results", min_value=1, max_value=10, value=5)

# Search Button
search_btn = st.button("🔍 Get Recommendations", use_container_width=True, type="primary")


# ── Apply quick search preset ─────────────────────────────────────────────────
if quick != "— choose —":
    preset = QUICK_SEARCHES[quick]
    # Use preset location if it's in top cities, otherwise use first top city
    location = preset["location"] if preset["location"] in top_cities else (top_cities[0] if top_cities else "Bangalore")
    budget = preset["budget"]
    cuisines = preset["cuisines"]
    minimum_rating = preset["minimum_rating"]


# ── Run recommendation ────────────────────────────────────────────────────────

# Show default recommendations on first load
if not search_btn and quick == "— choose —" and 'initial_load' not in st.session_state:
    st.session_state.initial_load = True
    # Set default preferences for initial recommendations
    default_location = top_cities[0] if top_cities else "Bangalore"
    default_budget = BudgetBand.medium
    default_cuisines = ["North Indian", "Chinese", "Continental", "South Indian"]
    default_minimum_rating = 3.5
    default_optional_tags = []
    default_top_k = 8
    
    # Create default preferences
    default_prefs = UserPreferences(
        location=default_location,
        budget=default_budget,
        cuisines=default_cuisines,
        minimum_rating=default_minimum_rating,
        optional_tags=default_optional_tags,
    )
    
    # Show loading message
    with st.spinner(f"Loading top restaurants in {default_location}…"):
        try:
            default_result = recommend(
                default_prefs,
                candidate_cap=100,
                top_k=default_top_k,
                catalog=cat,
            )
            
            # Display default recommendations
            st.markdown(f"### 🌟 Top {len(default_result.recommendations)} Restaurants in {default_location}")
            st.info("👋 Welcome! Here are some popular restaurants to get you started. Use the sidebar to customize your preferences.")
            
            # Display metrics
            col_meta1, col_meta2, col_meta3 = st.columns(3)
            col_meta1.metric("Results", len(default_result.recommendations))
            col_meta2.metric("AI Ranked", "Yes" if default_result.llm_used else "No (fallback)")
            col_meta3.metric("Budget Filter", budget_display(default_budget))
            
            if default_result.message:
                st.info(f"ℹ️ {default_result.message}")
            
            st.divider()
            
            # Display restaurant cards
            for item in default_result.recommendations:
                r = item.restaurant
                with st.container():
                    # ForkFinder Restaurant Card using Streamlit components
                    st.markdown(f"""
                    <div class="restaurant-card">
                        <div class="restaurant-header">
                            <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                                <div style="flex: 1;">
                                    <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 0.5rem;">
                                        <span class="rank-badge">#{item.rank}</span>
                                        <div style="width: 3px; height: 24px; background: linear-gradient(180deg, #fff 0%, rgba(255,255,255,0.6) 100%); border-radius: 2px;"></div>
                                        <span style="background: linear-gradient(135deg, rgba(255,255,255,0.2) 0%, rgba(255,255,255,0.1) 100%); padding: 0.25rem 0.75rem; border-radius: 20px; font-size: 0.75rem; color: rgba(255,255,255,0.9); font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px;">
                                            TOP PICK
                                        </span>
                                    </div>
                                    <h3 class="restaurant-name">{r.name}</h3>
                                    <div style="display: flex; align-items: center; gap: 0.5rem; margin-top: 0.25rem;">
                                        <div style="width: 8px; height: 8px; background: #10b981; border-radius: 50%; box-shadow: 0 0 8px rgba(16,185,129,0.5);"></div>
                                        <span style="color: rgba(255,255,255,0.8); font-size: 0.8rem; font-weight: 500;">VERIFIED RESTAURANT</span>
                                    </div>
                                </div>
                                <div style="text-align: right; margin-left: 1rem;">
                                    <div style="font-size: 1.2rem; font-weight: 800; color: white; margin-bottom: 0.15rem; text-shadow: 0 2px 4px rgba(0,0,0,0.1);">{star_rating(r.rating)}</div>
                                    <div style="font-size: 0.85rem; color: rgba(255,255,255,0.9); font-weight: 600; background: rgba(255,255,255,0.1); padding: 0.25rem 0.5rem; border-radius: 12px; display: inline-block;">
                                        {budget_display(r.cost_band)}
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div class="restaurant-content">
                            <p style="margin: 0 0 1rem 0; color: #6b7280; font-size: 0.9rem; font-weight: 500;">📍 {r.city}</p>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Cuisines section
                    st.markdown("**🍴 Cuisines**")
                    cuisine_cols = st.columns(len(r.cuisines) if len(r.cuisines) <= 3 else 3)
                    for i, cuisine in enumerate(r.cuisines[:3]):
                        with cuisine_cols[i % 3]:
                            st.markdown(f'<span class="cuisine-tag">{cuisine}</span>', unsafe_allow_html=True)
                    
                    # Features section
                    if r.tags:
                        st.markdown("**🏷️ Features**")
                        feature_cols = st.columns(len(r.tags) if len(r.tags) <= 3 else 3)
                        for i, tag in enumerate(r.tags[:3]):
                            with feature_cols[i % 3]:
                                st.markdown(f'<span class="tag-pill">{tag}</span>', unsafe_allow_html=True)
                    
                    # AI explanation
                    if item.explanation:
                        st.markdown(f"""
                        <div class="ai-explanation">
                            🤖 {item.explanation}
                        </div>
                        """, unsafe_allow_html=True)

                    st.divider()
                    
        except Exception as e:
            st.error(f"Failed to load default recommendations: {e}")

if search_btn or quick != "— choose —":

    # Validate inputs
    if not location:
        st.error("Please enter a location.")
        st.stop()
    if not cuisines:
        st.error("Please select at least one cuisine.")
        st.stop()

    prefs = UserPreferences(
        location=location,
        budget=budget,
        cuisines=cuisines,
        minimum_rating=minimum_rating,
        optional_tags=optional_tags,
    )

    with st.spinner(f"Finding top {top_k} restaurants in {location}…"):
        try:
            result = recommend(
                prefs,
                candidate_cap=50,
                top_k=top_k,
                catalog=cat,
            )
        except PreferencesValidationError as e:
            st.error(f"**{e.code}**: {e.message}")
            if e.suggestions:
                st.info("💡 Suggestions: " + ", ".join(e.suggestions[:10]))
            st.stop()
        except Exception as e:
            st.error(f"Unexpected error: {e}")
            st.stop()

    # ── Results header ────────────────────────────────────────────────────────
    st.markdown(f"### 🏆 Top {len(result.recommendations)} Restaurants in {location}")

    col_meta1, col_meta2, col_meta3 = st.columns(3)
    col_meta1.metric("Results", len(result.recommendations))
    col_meta2.metric("AI Ranked", "Yes" if result.llm_used else "No (fallback)")
    col_meta3.metric("Budget Filter", budget_display(budget))

    if result.message:
        st.info(f"ℹ️ {result.message}")

    st.divider()

    if not result.recommendations:
        st.warning("No restaurants matched your criteria. Try lowering the minimum rating or changing the cuisine.")
        st.stop()

    # ── Restaurant cards ──────────────────────────────────────────────────────
    for item in result.recommendations:
        r = item.restaurant

        with st.container():
            # ForkFinder Restaurant Card using Streamlit components
            st.markdown(f"""
            <div class="restaurant-card">
                <div class="restaurant-header">
                    <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                        <div style="flex: 1;">
                            <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 0.5rem;">
                                <span class="rank-badge">#{item.rank}</span>
                                <div style="width: 3px; height: 24px; background: linear-gradient(180deg, #fff 0%, rgba(255,255,255,0.6) 100%); border-radius: 2px;"></div>
                                <span style="background: linear-gradient(135deg, rgba(255,255,255,0.2) 0%, rgba(255,255,255,0.1) 100%); padding: 0.25rem 0.75rem; border-radius: 20px; font-size: 0.75rem; color: rgba(255,255,255,0.9); font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px;">
                                    TOP PICK
                                </span>
                            </div>
                            <h3 class="restaurant-name">{r.name}</h3>
                            <div style="display: flex; align-items: center; gap: 0.5rem; margin-top: 0.25rem;">
                                <div style="width: 8px; height: 8px; background: #10b981; border-radius: 50%; box-shadow: 0 0 8px rgba(16,185,129,0.5);"></div>
                                <span style="color: rgba(255,255,255,0.8); font-size: 0.8rem; font-weight: 500;">VERIFIED RESTAURANT</span>
                            </div>
                        </div>
                        <div style="text-align: right; margin-left: 1rem;">
                            <div style="font-size: 1.2rem; font-weight: 800; color: white; margin-bottom: 0.15rem; text-shadow: 0 2px 4px rgba(0,0,0,0.1);">{star_rating(r.rating)}</div>
                            <div style="font-size: 0.85rem; color: rgba(255,255,255,0.9); font-weight: 600; background: rgba(255,255,255,0.1); padding: 0.25rem 0.5rem; border-radius: 12px; display: inline-block;">
                                {budget_display(r.cost_band)}
                            </div>
                        </div>
                    </div>
                </div>
                <div class="restaurant-content">
                    <p style="margin: 0 0 1rem 0; color: #6b7280; font-size: 0.9rem; font-weight: 500;">📍 {r.city}</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Cuisines section
            st.markdown("**🍴 Cuisines**")
            cuisine_cols = st.columns(len(r.cuisines) if len(r.cuisines) <= 3 else 3)
            for i, cuisine in enumerate(r.cuisines[:3]):
                with cuisine_cols[i % 3]:
                    st.markdown(f'<span class="cuisine-tag">{cuisine}</span>', unsafe_allow_html=True)
            
            # Features section
            if r.tags:
                st.markdown("**🏷️ Features**")
                feature_cols = st.columns(len(r.tags) if len(r.tags) <= 3 else 3)
                for i, tag in enumerate(r.tags[:3]):
                    with feature_cols[i % 3]:
                        st.markdown(f'<span class="tag-pill">{tag}</span>', unsafe_allow_html=True)
            
            # AI explanation
            if item.explanation:
                st.markdown(f"""
                <div class="ai-explanation">
                    🤖 {item.explanation}
                </div>
                """, unsafe_allow_html=True)

            st.divider()

# ── Empty state ───────────────────────────────────────────────────────────────
else:
    st.info("👈 Set your preferences in the sidebar and click **Get Recommendations**")

    st.markdown("### 🗺️ How it works")
    cols = st.columns(4)
    steps = [
        ("1️⃣", "Set Preferences", "Location, budget, cuisine, rating"),
        ("2️⃣", "Validate", "Phase 2 checks against real catalog"),
        ("3️⃣", "Filter", "Phase 3 deterministic candidate selection"),
        ("4️⃣", "AI Rank", "Groq LLM ranks & explains top picks"),
    ]
    for col, (icon, title, desc) in zip(cols, steps):
        with col:
            st.markdown(f"**{icon} {title}**")
            st.caption(desc)
