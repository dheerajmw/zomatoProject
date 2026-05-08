"""
Streamlit UI for the AI-powered Restaurant Recommendation System.
Calls Phase 2 → Phase 3 → Phase 4 directly (no FastAPI server needed).
Deploy on Streamlit Cloud: set GROQ_API_KEY in app secrets.
"""

from __future__ import annotations

import os
from pathlib import Path
import streamlit as st

# ── Inject Streamlit secrets into env BEFORE any app imports ─────────────────
# This must happen before importing app modules so pydantic-settings picks them up.
def _inject_secrets() -> None:
    """Copy Streamlit secrets into os.environ so app/config.py sees them."""
    try:
        for key, value in st.secrets.items():
            if isinstance(value, str):
                os.environ.setdefault(key, value)
    except Exception:
        pass  # No secrets file locally — env vars already set

_inject_secrets()

# Point to the bundled sample CSV so we never hit HuggingFace on Streamlit Cloud.
# Users can override by setting ZOMATO_CSV_PATH in secrets to a real dataset path.
_SAMPLE_CSV = str(Path(__file__).parent / "tests" / "fixtures" / "delhi_sample.csv")
if not os.environ.get("ZOMATO_CSV_PATH"):
    os.environ["ZOMATO_CSV_PATH"] = _SAMPLE_CSV

# Bust the lru_cache on settings so it re-reads the env vars we just set
from app.config import get_settings
get_settings.cache_clear()

# ── Page config (must be first Streamlit call) ────────────────────────────────
st.set_page_config(
    page_title="🍽️ Restaurant Recommendations",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .rank-badge {
        background: #E23744;
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: bold;
        font-size: 14px;
        display: inline-block;
        margin-bottom: 8px;
    }
    .restaurant-card {
        background: white;
        border: 1px solid #e0e0e0;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 16px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    }
    .cuisine-tag {
        background: #f8f9fa;
        border: 1px solid #dee2e6;
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 13px;
        margin-right: 6px;
        display: inline-block;
    }
    .ai-explanation {
        background: #f0f7ff;
        border-left: 4px solid #E23744;
        padding: 10px 14px;
        border-radius: 0 8px 8px 0;
        font-style: italic;
        color: #444;
        margin-top: 10px;
    }
    .stat-box {
        background: #fff;
        border-radius: 10px;
        padding: 16px;
        text-align: center;
        box-shadow: 0 1px 4px rgba(0,0,0,0.08);
    }
    .stat-number {
        font-size: 2rem;
        font-weight: 700;
        color: #E23744;
    }
    .tag-pill {
        background: #e3f2fd;
        color: #1565c0;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 12px;
        margin-right: 4px;
        display: inline-block;
    }
</style>
""", unsafe_allow_html=True)


# ── Imports (after page config) ───────────────────────────────────────────────
from app.schemas import UserPreferences, BudgetBand
from app.phase2 import PreferencesValidationError
from app.phase4 import recommend
from app.phase1 import load_catalog, catalog_summary


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
    Avoids pickle incompatibility between Pydantic models and st.cache_resource on Python 3.9.
    """
    if "catalog" not in st.session_state:
        st.session_state["catalog"] = load_catalog()
    return st.session_state["catalog"]


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
    st.image("https://img.icons8.com/color/96/restaurant.png", width=64)
    st.title("🍽️ Restaurant Finder")
    st.caption("AI-powered recommendations using Groq LLM")
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

st.markdown("## 🍽️ AI-Powered Restaurant Recommendations")
st.caption("Powered by Groq · llama-3.3-70b-versatile · Zomato dataset")
st.divider()

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
            st.markdown(
                f'<span class="rank-badge">#{item.rank}</span>',
                unsafe_allow_html=True,
            )

            col_left, col_right = st.columns([3, 1])

            with col_left:
                st.markdown(f"#### {r.name}")
                st.caption(f"📍 {r.city}")

                # Cuisine tags
                tags_html = "".join(
                    f'<span class="cuisine-tag">{c}</span>' for c in r.cuisines
                )
                st.markdown(tags_html, unsafe_allow_html=True)

                # Optional tags
                if r.tags:
                    pills_html = "".join(
                        f'<span class="tag-pill">{t}</span>' for t in r.tags
                    )
                    st.markdown(pills_html, unsafe_allow_html=True)

            with col_right:
                st.markdown(f"**Rating:** {star_rating(r.rating)}")
                st.markdown(f"**Budget:** {budget_display(r.cost_band)}")

            # AI explanation
            if item.explanation:
                st.markdown(
                    f'<div class="ai-explanation">🤖 {item.explanation}</div>',
                    unsafe_allow_html=True,
                )

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
