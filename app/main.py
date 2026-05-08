from __future__ import annotations

import os
from contextlib import asynccontextmanager

from typing import Optional

from fastapi import FastAPI, HTTPException, Query

from app.config import settings
from app.phase1 import (
    catalog_summary,
    filter_catalog,
    get_source_column_names,
    load_catalog,
)
from app.phase2 import PreferencesValidationError, validate_and_normalize_preferences
from app.phase3 import build_llm_context, filter_catalog_phase3
from app.phase4 import recommend
from app.schemas import (
    BudgetBand,
    CatalogSummary,
    RecommendResponse,
    RestaurantRecord,
    UserPreferences,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Apply optional HF cache paths so Phase 1 `datasets` / `huggingface_hub` see them."""
    if settings.hf_home:
        os.environ["HF_HOME"] = settings.hf_home
    if settings.hf_datasets_cache:
        os.environ["HF_DATASETS_CACHE"] = settings.hf_datasets_cache
    yield


app = FastAPI(
    title=settings.app_name,
    description="AI-powered restaurant recommendations through Phase 4 (catalog, validation, integration, Groq ranking).",
    version="0.1.0",
    lifespan=lifespan,
)


@app.get("/health")
def health():
    """Liveness check; does not require Hugging Face or LLM."""
    return {"status": "ok"}


@app.post("/preferences", response_model=UserPreferences, tags=["preferences"])
def post_preferences(body: UserPreferences) -> UserPreferences:
    """
    Validate preferences against the loaded catalog (location, cuisines, rating).
    Returns normalized preferences; 400 if no restaurant can match.
    """
    try:
        return validate_and_normalize_preferences(body)
    except PreferencesValidationError as e:
        raise HTTPException(
            status_code=400,
            detail={
                "code": e.code,
                "message": e.message,
                "suggestions": e.suggestions,
            },
        )


@app.post("/phase3/candidates", tags=["phase3"])
def phase3_candidates(
    body: UserPreferences,
    candidate_cap: int = Query(default=50, ge=1, le=200),
) -> dict:
    """
    Phase 3 integration: returns deterministic candidates + counts.

    This endpoint assumes Phase 2 can be called separately; it does not auto-normalize.
    """
    selection = filter_catalog_phase3(body, candidate_cap=candidate_cap)
    return {
        "pre_filter_count": selection.pre_filter_count,
        "post_filter_count": selection.post_filter_count,
        "capped_to": selection.capped_to,
        "candidates": [c.model_dump() for c in selection.candidates],
    }


@app.post("/phase3/llm-context", tags=["phase3"])
def phase3_llm_context(
    body: UserPreferences,
    candidate_cap: int = Query(default=50, ge=1, le=200),
) -> dict[str, str]:
    """Phase 3 context builder for Phase 4; returns a single JSON string prompt payload."""
    selection = filter_catalog_phase3(body, candidate_cap=candidate_cap)
    return {"context": build_llm_context(selection.candidates, body)}


@app.get("/catalog/summary", response_model=CatalogSummary, tags=["catalog"])
def get_catalog_summary() -> CatalogSummary:
    """Load the catalog (first call may download from Hugging Face) and return counts / city sample."""
    return catalog_summary()


@app.get("/catalog/columns", tags=["catalog"])
def catalog_raw_columns() -> dict[str, list[str]]:
    """Raw CSV / dataset column names for schema discovery."""
    return {"columns": get_source_column_names()}


@app.get("/catalog/restaurants", response_model=list[RestaurantRecord], tags=["catalog"])
def list_catalog_restaurants(
    location: Optional[str] = None,
    cuisine_contains: Optional[str] = None,
    minimum_rating: Optional[float] = Query(default=None, ge=0.0, le=5.0),
    budget: Optional[BudgetBand] = None,
    limit: int = Query(default=20, ge=1, le=200),
) -> list[RestaurantRecord]:
    """Filter the in-memory catalog without an LLM (deterministic; Phase 3 will align with full prefs)."""
    all_rows = load_catalog()
    return filter_catalog(
        all_rows,
        location=location,
        cuisine_contains=cuisine_contains,
        minimum_rating=minimum_rating,
        budget=budget,
        limit=limit,
    )


@app.post("/recommendations", response_model=RecommendResponse, tags=["recommendations"])
def recommendations(
    body: UserPreferences,
    candidate_cap: int = Query(default=50, ge=1, le=200),
    top_k: Optional[int] = Query(default=None, ge=1, le=20),
) -> RecommendResponse:
    """
    Phase 4 end-to-end path:
    Phase 2 validation -> Phase 3 candidate selection -> Groq ranking/explanations -> grounding checks.
    """
    try:
        return recommend(body, candidate_cap=candidate_cap, top_k=top_k)
    except PreferencesValidationError as e:
        raise HTTPException(
            status_code=400,
            detail={
                "code": e.code,
                "message": e.message,
                "suggestions": e.suggestions,
            },
        )
