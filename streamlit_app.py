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
    /* ForkFinder Theme - Orange/Red Gradient */
    .forkfinder-gradient {
        background: linear-gradient(135deg, #f97316 0%, #ef4444 100%);
    }
    
    .rank-badge {
        background: linear-gradient(135deg, #f97316 0%, #ef4444 100%);
        color: white;
        padding: 6px 16px;
        border-radius: 25px;
        font-weight: bold;
        font-size: 14px;
        display: inline-block;
        margin-bottom: 12px;
        box-shadow: 0 2px 8px rgba(249, 115, 22, 0.3);
    }
    
    .restaurant-card {
        background: white;
        border: 1px solid #e5e7eb;
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        transition: all 0.3s ease;
    }
    
    .restaurant-card:hover {
        box-shadow: 0 8px 24px rgba(249, 115, 22, 0.15);
        transform: translateY(-2px);
    }
    
    .cuisine-tag {
        background: linear-gradient(135deg, #fed7aa 0%, #fdba74 100%);
        color: #9a3412;
        border: 1px solid #fb923c;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 500;
        margin-right: 8px;
        margin-bottom: 6px;
        display: inline-block;
    }
    
    .ai-explanation {
        background: linear-gradient(135deg, #fff7ed 0%, #fed7aa 100%);
        border-left: 4px solid #f97316;
        padding: 12px 16px;
        border-radius: 8px;
        margin: 12px 0;
        font-style: italic;
        color: #374151;
        font-size: 14px;
    }
    
    .stat-box {
        background: white;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        border: 1px solid #e5e7eb;
        transition: all 0.3s ease;
    }
    
    .stat-box:hover {
        box-shadow: 0 8px 24px rgba(249, 115, 22, 0.15);
        transform: translateY(-2px);
    }
    
    .stat-number {
        font-size: 2.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, #f97316 0%, #ef4444 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 4px;
    }
    
    .tag-pill {
        background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%);
        color: #dc2626;
        padding: 3px 10px;
        border-radius: 6px;
        font-size: 11px;
        font-weight: 500;
        margin-right: 4px;
        margin-bottom: 4px;
        display: inline-block;
        border: 1px solid #f87171;
    }
    
    /* Header styling */
    .main-header {
        background: linear-gradient(135deg, #f97316 0%, #ef4444 100%);
        padding: 2rem;
        border-radius: 16px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 8px 24px rgba(249, 115, 22, 0.2);
    }
    
    .main-header h1 {
        font-size: 2.5rem;
        font-weight: 800;
        margin-bottom: 0.5rem;
    }
    
    .main-header p {
        font-size: 1.1rem;
        opacity: 0.9;
        margin: 0;
    }
    
    /* Sidebar enhancements */
    .sidebar-content {
        background: linear-gradient(135deg, #fff7ed 0%, #ffffff 100%);
        padding: 1rem;
        border-radius: 12px;
        margin-bottom: 1rem;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #f97316 0%, #ef4444 100%);
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #ea580c 0%, #dc2626 100%);
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(249, 115, 22, 0.3);
    }
    
    /* Input styling */
    .stTextInput > div > div > input,
    .stSelectbox > div > div > select,
    .stNumberInput > div > div > input,
    .stTextArea > div > div > textarea {
        border: 2px solid #e5e7eb;
        border-radius: 8px;
        transition: all 0.3s ease;
        cursor: pointer;
    }
    
    .stTextInput > div > div > input:focus,
    .stSelectbox > div > div > select:focus,
    .stNumberInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #f97316;
        box-shadow: 0 0 0 3px rgba(249, 115, 22, 0.1);
        cursor: text;
    }
    
    /* Dropdown and select cursor styling */
    .stSelectbox > div > div > select,
    .stMultiSelect > div > div > select,
    .stSelectbox > div[data-testid="stSelectbox"] > div > div,
    .stMultiSelect > div[data-testid="stMultiSelect"] > div > div {
        cursor: pointer !important;
    }
    
    /* Radio button and checkbox cursor styling */
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

# Enhanced ForkFinder Header
st.markdown("""
<div style="text-align: center; padding: 1.5rem 0 1rem 0; margin-bottom: 0.5rem; background: linear-gradient(135deg, #fff7ed 0%, #ffffff 50%, #fee2e2 100%); border-radius: 20px; box-shadow: 0 8px 32px rgba(249, 115, 22, 0.15); position: relative; overflow: hidden;">
    <div style="position: absolute; top: 0; left: 0; right: 0; height: 3px; background: linear-gradient(90deg, #f97316 0%, #ef4444 50%, #f97316 100%); animation: shimmer 2s ease-in-out infinite;"></div>
    <div style="display: inline-block; animation: float 3s ease-in-out infinite;">
        <div style="font-size: 3rem; margin-bottom: 0.5rem; filter: drop-shadow(0 4px 8px rgba(249, 115, 22, 0.3)); animation: pulse 2s ease-in-out infinite;">🍽️</div>
    </div>
    <h1 style="background: linear-gradient(135deg, #f97316 0%, #ef4444 50%, #f97316 100%); background-clip: text; -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 2.5rem; font-weight: 900; margin: 0; text-shadow: 0 2px 4px rgba(249, 115, 22, 0.1); animation: glow 3s ease-in-out infinite;">
        ForkFinder
    </h1>
    <p style="color: #6b7280; font-size: 1rem; margin: 0.5rem 0; font-weight: 500; letter-spacing: 0.5px;">
        🤖 <span style="color: #f97316; font-weight: 600;">AI-Powered</span> Restaurant Discovery
    </p>
    <div style="margin-top: 0.75rem; display: flex; justify-content: center; gap: 1rem; flex-wrap: wrap;">
        <span style="background: linear-gradient(135deg, #f97316 0%, #ef4444 100%); color: white; padding: 0.25rem 0.75rem; border-radius: 20px; font-size: 0.8rem; font-weight: 600; box-shadow: 0 2px 8px rgba(249, 115, 22, 0.3);">
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
                        <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 1rem;">
                            <div>
                                <span class="rank-badge">#{item.rank}</span>
                                <h3 style="margin: 0.5rem 0; font-size: 1.4rem; font-weight: 700; color: #1f2937;">{r.name}</h3>
                                <p style="margin: 0; color: #6b7280; font-size: 0.95rem;">📍 {r.city}</p>
                            </div>
                            <div style="text-align: right;">
                                <div style="font-size: 1.2rem; font-weight: 700; color: #f97316; margin-bottom: 0.25rem;">{star_rating(r.rating)}</div>
                                <div style="font-size: 0.9rem; color: #6b7280; font-weight: 500;">{budget_display(r.cost_band)}</div>
                            </div>
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
                <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 1rem;">
                    <div>
                        <span class="rank-badge">#{item.rank}</span>
                        <h3 style="margin: 0.5rem 0; font-size: 1.4rem; font-weight: 700; color: #1f2937;">{r.name}</h3>
                        <p style="margin: 0; color: #6b7280; font-size: 0.95rem;">📍 {r.city}</p>
                    </div>
                    <div style="text-align: right;">
                        <div style="font-size: 1.2rem; font-weight: 700; color: #f97316; margin-bottom: 0.25rem;">{star_rating(r.rating)}</div>
                        <div style="font-size: 0.9rem; color: #6b7280; font-weight: 500;">{budget_display(r.cost_band)}</div>
                    </div>
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
