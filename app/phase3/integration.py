"""
Phase 3 — Integration layer (filter + prompt context)
(see doc/phase-wise-architecture.md).

Responsibilities:
- Deterministic filtering from full ``UserPreferences`` (hard constraints).
- Candidate capping with stable ordering to control token/latency.
- Building a model-safe context bundle so the LLM can only rank/explain
  *from the provided candidates* (no hallucinated restaurants or metrics).
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Iterable, Optional, Sequence

from app.phase1.catalog import load_catalog, normalize_location_query
from app.schemas import BudgetBand, RestaurantRecord, UserPreferences


@dataclass(frozen=True)
class CandidateSelection:
    """Phase 3 artifact: deterministic candidate list + metadata."""

    candidates: list[RestaurantRecord]
    pre_filter_count: int
    post_filter_count: int
    capped_to: int


def _matches_location(record: RestaurantRecord, location: str) -> bool:
    loc = normalize_location_query(location).lower()
    record_loc = normalize_location_query(record.city).lower()
    return loc == record_loc


def _matches_budget(record: RestaurantRecord, budget: BudgetBand) -> bool:
    return record.cost_band == budget


def _matches_min_rating(record: RestaurantRecord, minimum_rating: float) -> bool:
    return record.rating >= minimum_rating


def _matches_any_cuisine(record: RestaurantRecord, cuisines: Sequence[str]) -> bool:
    want = [c.strip().lower() for c in cuisines if c and str(c).strip()]
    if not want:
        return True
    have = [c.lower() for c in record.cuisines]
    blob = " ".join(have)
    return any((w in blob) for w in want)


def _matches_optional_tags(record: RestaurantRecord, optional_tags: Sequence[str]) -> bool:
    """
    Tags are best-effort in Phase 3:
    - if user provides tags, require that the record contains *all* those tags.
    - Phase 1 tags currently include: online-order, book-table, and slugged rest_type.
    """
    want = [t.strip().lower() for t in optional_tags if t and str(t).strip()]
    if not want:
        return True
    have = {t.lower() for t in record.tags}
    return all(t in have for t in want)


def _stable_sort_key(r: RestaurantRecord) -> tuple:
    # rating desc, name asc, id asc: deterministic ordering for caps and prompts
    return (-float(r.rating), r.name.lower(), r.id)


def filter_catalog_phase3(
    prefs: UserPreferences,
    *,
    catalog: Optional[Sequence[RestaurantRecord]] = None,
    candidate_cap: int = 50,
) -> CandidateSelection:
    """
    Deterministic Phase 3 filtering from the full preference object.

    - Hard constraints: location, budget, cuisines (any-of substring), minimum rating, optional tags.
    - Candidate cap: stable sort (rating desc, name asc, id asc) then top-N.
    """
    rows = list(catalog) if catalog is not None else load_catalog()
    pre_count = len(rows)

    filtered: list[RestaurantRecord] = []
    for r in rows:
        if not _matches_location(r, prefs.location):
            continue
        if not _matches_budget(r, prefs.budget):
            continue
        if not _matches_min_rating(r, prefs.minimum_rating):
            continue
        if not _matches_any_cuisine(r, prefs.cuisines):
            continue
        if not _matches_optional_tags(r, prefs.optional_tags):
            continue
        filtered.append(r)

    filtered.sort(key=_stable_sort_key)
    post_count = len(filtered)

    cap = max(1, int(candidate_cap))
    capped = filtered[:cap]

    return CandidateSelection(
        candidates=capped,
        pre_filter_count=pre_count,
        post_filter_count=post_count,
        capped_to=len(capped),
    )


def _candidate_prompt_rows(candidates: Iterable[RestaurantRecord]) -> list[dict]:
    rows: list[dict] = []
    for r in candidates:
        rows.append(
            {
                "restaurant_id": r.id,
                "name": r.name,
                "city": r.city,
                "cuisines": r.cuisines,
                "budget_band": r.cost_band.value,
                "rating": r.rating,
                "tags": r.tags,
            }
        )
    return rows


def build_llm_context(candidates: Sequence[RestaurantRecord], prefs: UserPreferences) -> str:
    """
    Build a model-safe prompt context.

    The key constraint from the problem statement: the LLM must rank/explain using
    *only* the candidates provided, and must not invent restaurants or numeric facts.
    """
    payload = {
        "task": "Rank restaurants and explain why they match the user.",
        "rules": [
            "Use ONLY the candidate restaurants provided below.",
            "Do NOT invent restaurants or facts not present in candidates.",
            "Use rating and budget_band ONLY from candidates; do not fabricate numbers.",
            "Return JSON in the required output schema.",
        ],
        "user_preferences": {
            "location": prefs.location,
            "budget_band": prefs.budget.value,
            "cuisines": prefs.cuisines,
            "minimum_rating": prefs.minimum_rating,
            "optional_tags": prefs.optional_tags,
        },
        "candidates": _candidate_prompt_rows(candidates),
        "output_schema": {
            "recommendations": [
                {
                    "rank": 1,
                    "restaurant_id": "zomato-00000000",
                    "explanation": "Short, specific reason grounded in provided fields.",
                }
            ]
        },
    }
    return json.dumps(payload, ensure_ascii=False, indent=2)

