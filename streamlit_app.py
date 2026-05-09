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
        padding: 24px;
        margin-bottom: 20px;
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
        margin-right: 6px;
        margin-bottom: 4px;
        display: inline-block;
    }
    
    .ai-explanation {
        background: linear-gradient(135deg, #fff7ed 0%, #fed7aa 100%);
        border-left: 4px solid #f97316;
        padding: 12px 16px;
        border-radius: 0 12px 12px 0;
        font-style: italic;
        color: #9a3412;
        margin-top: 12px;
        box-shadow: 0 2px 8px rgba(249, 115, 22, 0.1);
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
    .stSelectbox > div > div > select {
        border: 2px solid #e5e7eb;
        border-radius: 8px;
        transition: all 0.3s ease;
    }
    
    .stTextInput > div > div > input:focus,
    .stSelectbox > div > div > select:focus {
        border-color: #f97316;
        box-shadow: 0 0 0 3px rgba(249, 115, 22, 0.1);
    }
    
    /* Slider styling */
    .stSlider > div > div > div {
        background: linear-gradient(90deg, #f97316 0%, #ef4444 100%);
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

def star_rating(rating: float) -> str:
    full = int(rating)
    return "⭐" * full + f"  **{rating}**"


def budget_display(band: BudgetBand) -> str:
    return {
        BudgetBand.low: "₹0 – ₹500",
        BudgetBand.medium: "₹500 – ₹1,000",
        BudgetBand.high: "₹1,000+",
    }[band]


# ── Sidebar ───────────────────────────────────────────────────────────────────

with st.sidebar:
    # ForkFinder Logo and Title
    st.markdown("""
    <div style="text-align: center; padding: 1rem;">
        <div style="font-size: 3rem; margin-bottom: 0.5rem;">🍽️</div>
        <h1 style="color: #f97316; font-size: 1.8rem; font-weight: 800; margin: 0;">ForkFinder</h1>
        <p style="color: #6b7280; font-size: 0.9rem; margin: 0.5rem 0;">AI-Powered Restaurant Discovery</p>
    </div>
    """, unsafe_allow_html=True)
    st.divider()

    # Quick search
    st.subheader("⚡ Quick Search")
    quick = st.selectbox(
        "Pick a preset",
        ["— choose —"] + list(QUICK_SEARCHES.keys()),
        label_visibility="collapsed",
    )

    st.divider()

    # Manual preferences
    st.subheader("🎯 Your Preferences")

    location = st.text_input(
        "📍 Location",
        placeholder="e.g. Delhi, Bangalore, Mumbai",
        help="Enter any Indian city",
    )

    budget_label = st.radio(
        "💰 Budget",
        list(BUDGET_LABELS.values()),
        index=1,
    )
    budget = BUDGET_FROM_LABEL[budget_label]

    cuisines = st.multiselect(
        "🍴 Cuisines  (pick at least one)",
        CUISINE_OPTIONS,
        help="Select one or more cuisines you prefer",
    )

    minimum_rating = st.slider(
        "⭐ Minimum Rating",
        min_value=0.0, max_value=5.0,
        value=3.5, step=0.5,
        help="Restaurants below this rating are excluded",
    )

    optional_tags = st.multiselect(
        "🏷️ Optional Tags",
        OPTIONAL_TAG_OPTIONS,
    )

    top_k = st.slider("🏆 Top results", min_value=1, max_value=10, value=5)

    st.divider()
    search_btn = st.button("🔍 Get Recommendations", use_container_width=True, type="primary")


# ── Apply quick search preset ─────────────────────────────────────────────────
if quick != "— choose —":
    preset = QUICK_SEARCHES[quick]
    location = preset["location"]
    budget = preset["budget"]
    cuisines = preset["cuisines"]
    minimum_rating = preset["minimum_rating"]


# ── Main area ─────────────────────────────────────────────────────────────────

# ForkFinder Header
st.markdown("""
<div class="main-header">
    <h1>🍽️ ForkFinder</h1>
    <p>Find Your Perfect Dining Experience with AI-Powered Recommendations</p>
    <p style="font-size: 0.9rem; opacity: 0.8; margin-top: 0.5rem;">Powered by Groq · llama-3.3-70b-versatile · Zomato dataset</p>
</div>
""", unsafe_allow_html=True)

# Stats row — load catalog once, show spinner on first load
with st.spinner("Loading restaurant catalog…"):
    try:
        cat = get_catalog()
        summary = catalog_summary(cat)
    except Exception as e:
        st.error(f"Failed to load catalog: {e}")
        st.info("Make sure `GROQ_API_KEY` is set and the dataset is accessible.")
        st.stop()

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(f'<div class="stat-box"><div class="stat-number">{summary.row_count:,}</div><div>Restaurants</div></div>', unsafe_allow_html=True)
with c2:
    st.markdown(f'<div class="stat-box"><div class="stat-number">{summary.unique_cities}</div><div>Cities</div></div>', unsafe_allow_html=True)
with c3:
    st.markdown(f'<div class="stat-box"><div class="stat-number">6</div><div>AI Phases</div></div>', unsafe_allow_html=True)
with c4:
    st.markdown(f'<div class="stat-box"><div class="stat-number">100%</div><div>Grounded</div></div>', unsafe_allow_html=True)
st.divider()


# ── Run recommendation ────────────────────────────────────────────────────────

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
            # ForkFinder Restaurant Card
            cuisine_tags = "".join(f'<span class="cuisine-tag">{c}</span>' for c in r.cuisines)
            feature_tags = "".join(f'<span class="tag-pill">{t}</span>' for t in r.tags) if r.tags else ""
            features_section = f'''
                <div style="margin-bottom: 1rem;">
                    <div style="font-weight: 600; color: #374151; margin-bottom: 0.5rem;">🏷️ Features</div>
                    <div>
                        {feature_tags}
                    </div>
                </div>
                ''' if r.tags else ""
            
            ai_explanation = f'<div class="ai-explanation">🤖 {item.explanation}</div>' if item.explanation else ""
            
            card_html = f"""
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
                
                <div style="margin-bottom: 1rem;">
                    <div style="font-weight: 600; color: #374151; margin-bottom: 0.5rem;">🍴 Cuisines</div>
                    <div>
                        {cuisine_tags}
                    </div>
                </div>
                
                {features_section}
                
                {ai_explanation}
            </div>
            """
            st.markdown(card_html, unsafe_allow_html=True)

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
