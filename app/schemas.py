from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class BudgetBand(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class UserPreferences(BaseModel):
    """Structured preferences from the user (Phase 2 will validate via API)."""

    location: str = Field(min_length=1, description="City or area, e.g. Delhi, Bangalore")
    budget: BudgetBand
    cuisines: list[str] = Field(
        min_length=1,
        description="At least one cuisine, e.g. Italian, Chinese",
    )
    minimum_rating: float = Field(
        ge=0.0,
        le=5.0,
        description="Minimum acceptable rating (0–5 scale; adjust in Phase 1 if dataset differs).",
    )
    optional_tags: list[str] = Field(
        default_factory=list,
        description="e.g. family-friendly, quick service",
    )


class RestaurantRecord(BaseModel):
    """Normalized restaurant row from the catalog (Phase 1 maps dataset columns here)."""

    id: str = Field(description="Stable identifier for grounding and LLM output validation")
    name: str
    city: str
    cuisines: list[str] = Field(default_factory=list)
    cost_band: BudgetBand
    rating: float = Field(ge=0.0, le=5.0)
    tags: list[str] = Field(
        default_factory=list,
        description="Optional normalized tags derived from dataset text fields",
    )


class RecommendationItem(BaseModel):
    """Single ranked recommendation with narrative (Phase 4 produces explanations)."""

    rank: int = Field(ge=1)
    restaurant_id: str
    restaurant: RestaurantRecord
    explanation: str = Field(
        default="",
        description="LLM or templated reason this pick fits the user",
    )


class CatalogSummary(BaseModel):
    """Sanity-check stats after loading the restaurant catalog (Phase 1)."""

    row_count: int = Field(description="Number of normalized rows kept")
    skipped_invalid_rows: int = Field(
        default=0,
        description="Rows dropped (missing name or unrated) in the last full load; 0 when summarizing a custom subset",
    )
    unique_cities: int
    sample_cities: list[str] = Field(description="Up to 30 distinct cities, sorted")


class RecommendResponse(BaseModel):
    """API response shape for top recommendations (Phase 5 display)."""

    recommendations: list[RecommendationItem] = Field(default_factory=list)
    llm_used: bool = Field(
        default=False,
        description="False when LLM was skipped or unavailable",
    )
    message: Optional[str] = Field(
        default=None,
        description="Optional note, e.g. empty candidate set or degraded mode",
    )
