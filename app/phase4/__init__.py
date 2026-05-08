"""Phase 4 — Groq-backed recommendation engine."""

from app.phase4.recommender import Phase4Error, recommend, validate_llm_recommendations

__all__ = [
    "Phase4Error",
    "recommend",
    "validate_llm_recommendations",
]

