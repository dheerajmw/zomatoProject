"""
Phase 2 — User preferences input and catalog-aware validation
(see doc/phase-wise-architecture.md).

Pydantic already enforces enums and numeric bounds on ``UserPreferences``; this
module normalizes strings and rejects payloads that cannot match any restaurant
in the loaded catalog (unknown city, impossible cuisine / rating combos).
"""

from __future__ import annotations

import re
from typing import Optional, Sequence

from app.phase1.catalog import load_catalog, normalize_location_query
from app.schemas import RestaurantRecord, UserPreferences

# Tags we accept today; extend in Phase 3 when matching against ``RestaurantRecord.tags``.
ALLOWED_OPTIONAL_TAGS: frozenset[str] = frozenset(
    {
        "family-friendly",
        "quick-service",
        "online-order",
        "book-table",
    }
)

_OPTIONAL_TAG_SYNONYMS: dict[str, str] = {
    "family friendly": "family-friendly",
    "family_friendly": "family-friendly",
    "quick service": "quick-service",
    "quick": "quick-service",
    "online order": "online-order",
    "book table": "book-table",
    "table booking": "book-table",
}
for _t in ALLOWED_OPTIONAL_TAGS:
    _OPTIONAL_TAG_SYNONYMS[_t] = _t
    _OPTIONAL_TAG_SYNONYMS[_t.replace("-", " ")] = _t


class PreferencesValidationError(ValueError):
    """Raised when preferences are structurally fine but impossible against the catalog."""

    def __init__(
        self,
        code: str,
        message: str,
        *,
        suggestions: Optional[list[str]] = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.suggestions = suggestions or []


def _canonicalize_tag(raw: str) -> str:
    s = str(raw).strip().lower().replace("_", " ")
    s = re.sub(r"\s+", " ", s).strip()
    if not s:
        raise PreferencesValidationError(
            "empty_optional_tag",
            "Optional tags must be non-empty strings.",
        )
    if s in _OPTIONAL_TAG_SYNONYMS:
        return _OPTIONAL_TAG_SYNONYMS[s]
    hyphen = s.replace(" ", "-")
    if hyphen in ALLOWED_OPTIONAL_TAGS:
        return hyphen
    raise PreferencesValidationError(
        "unknown_optional_tag",
        f"Unknown optional tag {raw!r}. Allowed: {', '.join(sorted(ALLOWED_OPTIONAL_TAGS))}.",
        suggestions=sorted(ALLOWED_OPTIONAL_TAGS),
    )


def _canonical_optional_tags(raw_tags: Sequence[str]) -> list[str]:
    out: list[str] = []
    for raw in raw_tags:
        if raw is None or not str(raw).strip():
            continue
        c = _canonicalize_tag(str(raw))
        if c not in out:
            out.append(c)
    return out


def _strip_cuisines(cuisines: Sequence[str]) -> list[str]:
    out = [c.strip() for c in cuisines if c and str(c).strip()]
    if not out:
        raise PreferencesValidationError(
            "empty_cuisines",
            "Provide at least one non-empty cuisine.",
        )
    return out


def _location_matches_record(normalized_location: str, record: RestaurantRecord) -> bool:
    loc = normalized_location.lower()
    return loc in record.city.lower()


def _rows_for_location(catalog: Sequence[RestaurantRecord], normalized_location: str) -> list[RestaurantRecord]:
    return [r for r in catalog if _location_matches_record(normalized_location, r)]


def _row_matches_any_requested_cuisine(row: RestaurantRecord, cuisines_lower: list[str]) -> bool:
    if not cuisines_lower:
        return True
    dish_blob = " ".join(c.lower() for c in row.cuisines)
    for u in cuisines_lower:
        if any(u in c.lower() for c in row.cuisines) or u in dish_blob:
            return True
    return False


def _candidate_pool(
    catalog: Sequence[RestaurantRecord],
    normalized_location: str,
    cuisines_lower: list[str],
) -> list[RestaurantRecord]:
    in_city = _rows_for_location(catalog, normalized_location)
    return [r for r in in_city if _row_matches_any_requested_cuisine(r, cuisines_lower)]


def _suggest_cities(catalog: Sequence[RestaurantRecord], *, limit: int = 20) -> list[str]:
    return sorted({r.city for r in catalog})[:limit]


def _suggest_cuisines_for_city(
    catalog: Sequence[RestaurantRecord],
    normalized_location: str,
    *,
    limit: int = 15,
) -> list[str]:
    seen: list[str] = []
    for r in _rows_for_location(catalog, normalized_location):
        for c in r.cuisines:
            t = c.strip()
            if t and t not in seen:
                seen.append(t)
            if len(seen) >= limit:
                return seen
    return seen


def validate_and_normalize_preferences(
    prefs: UserPreferences,
    *,
    catalog: Optional[Sequence[RestaurantRecord]] = None,
) -> UserPreferences:
    """
    Return a normalized ``UserPreferences`` instance that is guaranteed to match
    at least one catalog row on location, cuisine (any-of), and minimum rating.

    Raises ``PreferencesValidationError`` with ``suggestions`` when the catalog
    cannot satisfy the request.
    """
    cat = list(catalog) if catalog is not None else load_catalog()
    if not cat:
        raise PreferencesValidationError(
            "empty_catalog",
            "Restaurant catalog is empty; load data before validating preferences.",
        )

    cuisines = _strip_cuisines(prefs.cuisines)
    optional_tags = _canonical_optional_tags(prefs.optional_tags)
    loc = normalize_location_query(prefs.location.strip())

    in_city = _rows_for_location(cat, loc)
    if not in_city:
        raise PreferencesValidationError(
            "unknown_location",
            f"No restaurants found for location {loc!r}. Try a city that appears in the catalog.",
            suggestions=_suggest_cities(cat),
        )

    cuisines_lower = [c.lower() for c in cuisines]
    pool = _candidate_pool(cat, loc, cuisines_lower)
    if not pool:
        raise PreferencesValidationError(
            "cuisine_not_available",
            f"No restaurants in {loc} match any of the requested cuisines: {', '.join(cuisines)}.",
            suggestions=_suggest_cuisines_for_city(cat, loc),
        )

    if not any(r.rating >= prefs.minimum_rating for r in pool):
        max_r = max(r.rating for r in pool)
        raise PreferencesValidationError(
            "rating_unreachable",
            (
                f"No restaurant in {loc} matching your cuisines has rating "
                f">= {prefs.minimum_rating}. Highest available in this set is {max_r}."
            ),
            suggestions=[str(max_r)],
        )

    return UserPreferences(
        location=loc,
        budget=prefs.budget,
        cuisines=cuisines,
        minimum_rating=prefs.minimum_rating,
        optional_tags=optional_tags,
    )
