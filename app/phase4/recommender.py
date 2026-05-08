"""
Phase 4 — Recommendation engine (Groq-backed LLM)
(see doc/phase-wise-architecture.md).

This module wires:
- Phase 2 preference validation
- Phase 3 deterministic candidates + prompt context
- Groq chat completion
- Post-parse grounding checks so only candidate restaurants survive
"""

from __future__ import annotations

import json
import re
from typing import Any, Optional, Sequence

import httpx

from app.config import settings
from app.phase2 import validate_and_normalize_preferences
from app.phase3 import build_llm_context, filter_catalog_phase3
from app.schemas import RecommendationItem, RecommendResponse, RestaurantRecord, UserPreferences


class Phase4Error(RuntimeError):
    """Raised when the Groq recommendation engine cannot produce a valid response."""


def _strip_code_fences(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```[a-zA-Z0-9_-]*\n?", "", text)
        text = re.sub(r"\n?```$", "", text)
    return text.strip()


def _extract_json_payload(text: str) -> dict[str, Any]:
    cleaned = _strip_code_fences(text)
    try:
        parsed = json.loads(cleaned)
        if isinstance(parsed, dict):
            return parsed
    except json.JSONDecodeError:
        pass

    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start != -1 and end != -1 and start < end:
        snippet = cleaned[start : end + 1]
        parsed = json.loads(snippet)
        if isinstance(parsed, dict):
            return parsed

    raise Phase4Error("LLM response was not valid JSON.")


def _candidate_lookup(candidates: Sequence[RestaurantRecord]) -> dict[str, RestaurantRecord]:
    return {r.id: r for r in candidates}


def _normalize_llm_rows(payload: dict[str, Any]) -> list[dict[str, Any]]:
    rows = payload.get("recommendations", [])
    if not isinstance(rows, list):
        raise Phase4Error("LLM JSON did not contain a recommendations list.")
    return [row for row in rows if isinstance(row, dict)]


def validate_llm_recommendations(
    payload: dict[str, Any],
    candidates: Sequence[RestaurantRecord],
    *,
    top_k: int,
) -> list[RecommendationItem]:
    """
    Grounding guardrail:
    - keep only known candidate ids
    - deduplicate restaurants
    - normalize rank order to 1..k
    """
    lookup = _candidate_lookup(candidates)
    seen_ids: set[str] = set()
    validated: list[RecommendationItem] = []

    for row in _normalize_llm_rows(payload):
        restaurant_id = str(row.get("restaurant_id", "")).strip()
        explanation = str(row.get("explanation", "")).strip()
        if not restaurant_id or restaurant_id not in lookup:
            continue
        if restaurant_id in seen_ids:
            continue
        seen_ids.add(restaurant_id)
        validated.append(
            RecommendationItem(
                rank=len(validated) + 1,
                restaurant_id=restaurant_id,
                restaurant=lookup[restaurant_id],
                explanation=explanation or "Matches the user's preferences based on the provided candidate data.",
            )
        )
        if len(validated) >= top_k:
            break

    return validated


def _fallback_recommendations(
    candidates: Sequence[RestaurantRecord],
    *,
    top_k: int,
    message: str,
) -> RecommendResponse:
    items: list[RecommendationItem] = []
    for idx, restaurant in enumerate(candidates[:top_k], start=1):
        items.append(
            RecommendationItem(
                rank=idx,
                restaurant_id=restaurant.id,
                restaurant=restaurant,
                explanation=(
                    f"Selected from the deterministic candidate list: {restaurant.name} "
                    f"matches the requested city, budget, cuisine, and minimum rating filters."
                ),
            )
        )
    return RecommendResponse(
        recommendations=items,
        llm_used=False,
        message=message,
    )


def _groq_chat_completion(context: str, *, top_k: int) -> dict[str, Any]:
    if not settings.groq_api_key:
        raise Phase4Error("GROQ_API_KEY is not configured.")

    system_prompt = (
        "You are a restaurant recommendation ranker. "
        "Respond with JSON only. "
        "Use only the candidate restaurants given in the user message. "
        "Do not invent restaurants, ratings, budgets, or tags."
    )

    user_prompt = (
        f"{context}\n\n"
        "Return exactly this JSON shape:\n"
        "{\n"
        '  "recommendations": [\n'
        '    {"rank": 1, "restaurant_id": "candidate-id", "explanation": "why this matches"}\n'
        "  ]\n"
        "}\n"
        f"Return at most {top_k} recommendations."
    )

    payload = {
        "model": settings.groq_model,
        "temperature": 0.2,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "response_format": {"type": "json_object"},
    }

    headers = {
        "Authorization": f"Bearer {settings.groq_api_key}",
        "Content-Type": "application/json",
    }

    with httpx.Client(timeout=settings.llm_timeout_seconds) as client:
        response = client.post(
            f"{settings.groq_base_url.rstrip('/')}/chat/completions",
            headers=headers,
            json=payload,
        )
        response.raise_for_status()
        data = response.json()

    try:
        content = data["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as exc:
        raise Phase4Error("Groq response did not contain a chat message.") from exc

    return _extract_json_payload(str(content))


def recommend(
    prefs: UserPreferences,
    *,
    candidate_cap: int = 50,
    top_k: Optional[int] = None,
    catalog: Optional[Sequence[RestaurantRecord]] = None,
) -> RecommendResponse:
    """
    End-to-end Phase 4 pipeline:
    validate prefs -> deterministic candidates -> Groq rank/explain -> grounding validation.
    """
    normalized_prefs = validate_and_normalize_preferences(prefs, catalog=catalog)
    selection = filter_catalog_phase3(
        normalized_prefs,
        catalog=catalog,
        candidate_cap=candidate_cap,
    )
    desired_top_k = top_k or settings.llm_top_k
    desired_top_k = max(1, min(int(desired_top_k), max(1, candidate_cap)))

    if not selection.candidates:
        return RecommendResponse(
            recommendations=[],
            llm_used=False,
            message="No restaurants matched the deterministic Phase 3 filters.",
        )

    if not settings.llm_enabled:
        return _fallback_recommendations(
            selection.candidates,
            top_k=desired_top_k,
            message="LLM disabled; returning deterministic candidates with templated explanations.",
        )

    context = build_llm_context(selection.candidates, normalized_prefs)

    try:
        payload = _groq_chat_completion(context, top_k=desired_top_k)
        validated = validate_llm_recommendations(
            payload,
            selection.candidates,
            top_k=desired_top_k,
        )
    except (httpx.HTTPError, Phase4Error, RuntimeError, ValueError, KeyError) as exc:
        return _fallback_recommendations(
            selection.candidates,
            top_k=desired_top_k,
            message=f"Groq unavailable or invalid response; using deterministic fallback. Detail: {exc}",
        )

    if not validated:
        return _fallback_recommendations(
            selection.candidates,
            top_k=desired_top_k,
            message="Groq response could not be grounded to candidate ids; using deterministic fallback.",
        )

    return RecommendResponse(
        recommendations=validated,
        llm_used=True,
        message=None,
    )

