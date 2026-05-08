"""
Phase 1 — Data ingestion & catalog (see doc/phase-wise-architecture.md).

Loads `ManikaSaini/zomato-restaurant-recommendation` (Zomato CSV on Hugging Face),
normalizes rows into `RestaurantRecord`, and exposes helpers for stats and
deterministic filtering without an LLM.
"""

from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import Any, Iterator, Mapping, Optional, Sequence

from datasets import load_dataset

from app.config import settings
from app.schemas import BudgetBand, CatalogSummary, RestaurantRecord

logger = logging.getLogger(__name__)

# Matches rupees-for-two → BudgetBand (problem statement: low / medium / high)
_COST_LOW_MAX = 500
_COST_MEDIUM_MAX = 1000

# Canonical city tokens → display name (user may say "Bengaluru", data says "Bangalore")
_CITY_ALIASES: dict[str, str] = {
    "bangalore": "Bangalore",
    "bengaluru": "Bangalore",
    "mumbai": "Mumbai",
    "bombay": "Mumbai",
    "delhi": "Delhi",
    "new delhi": "Delhi",
    "ncr": "Delhi",
    "gurgaon": "Gurgaon",
    "gurugram": "Gurgaon",
    "noida": "Noida",
    "hyderabad": "Hyderabad",
    "chennai": "Chennai",
    "madras": "Chennai",
    "kolkata": "Kolkata",
    "calcutta": "Kolkata",
    "pune": "Pune",
    "ahmedabad": "Ahmedabad",
    "jaipur": "Jaipur",
    "goa": "Goa",
}

_COL_RATE = "rate"
_COL_NAME = "name"
_COL_ADDRESS = "address"
_COL_LOCATION = "location"
_COL_LISTED_CITY = "listed_in(city)"
_COL_CUISINES = "cuisines"
_COL_COST = "approx_cost(for two people)"
_COL_ONLINE = "online_order"
_COL_BOOK_TABLE = "book_table"
_COL_REST_TYPE = "rest_type"

_catalog_store: dict[str, Any] = {"rows": None, "skipped": 0}


def _datasets_cache_dir() -> str:
    """Prefer env/config; otherwise use project ``.cache/hf_datasets`` (avoids requiring ``~/.cache``)."""
    if settings.hf_datasets_cache:
        return settings.hf_datasets_cache
    # app/phase1/catalog.py → repo root is three levels up
    p = Path(__file__).resolve().parent.parent.parent / ".cache" / "hf_datasets"
    p.mkdir(parents=True, exist_ok=True)
    return str(p)


def _parse_rate(raw: Any) -> Optional[float]:
    if raw is None:
        return None
    s = str(raw).strip()
    if not s or s in {"-", "NEW", "nan", "None"}:
        return None
    if "/" in s:
        s = s.split("/", 1)[0].strip()
    try:
        v = float(s)
    except ValueError:
        return None
    if v < 0.0 or v > 5.0:
        return None
    return round(v, 2)


def _parse_cost(raw: Any) -> Optional[int]:
    if raw is None:
        return None
    s = str(raw).strip().lower()
    s = re.sub(r"^rs\.?\s*", "", s, flags=re.I)
    s = s.replace(",", "")
    digits = re.sub(r"[^\d]", "", s)
    if not digits:
        return None
    return int(digits)


def _cost_to_band(cost: int) -> BudgetBand:
    if cost <= _COST_LOW_MAX:
        return BudgetBand.low
    if cost <= _COST_MEDIUM_MAX:
        return BudgetBand.medium
    return BudgetBand.high


def _infer_city(address: str, listed: str, location: str) -> str:
    blob = f"{address} {location} {listed}".lower()
    for key, canonical in sorted(_CITY_ALIASES.items(), key=lambda x: -len(x[0])):
        if key in blob:
            return canonical
    addr = (address or "").strip()
    if "," in addr:
        tail = addr.split(",")[-1].strip()
        if len(tail) > 2:
            return tail.title()
    listed = (listed or "").strip()
    if listed:
        return listed.title()
    loc = (location or "").strip()
    if loc:
        return loc.title()
    return "unknown"


def _split_cuisines(raw: Any) -> list[str]:
    if raw is None:
        return []
    parts = re.split(r",|/", str(raw))
    return [p.strip() for p in parts if p.strip()]


def _tags_from_row(row: Mapping[str, Any]) -> list[str]:
    tags: list[str] = []
    if str(row.get(_COL_ONLINE, "")).strip().lower() == "yes":
        tags.append("online-order")
    if str(row.get(_COL_BOOK_TABLE, "")).strip().lower() == "yes":
        tags.append("book-table")
    rt = str(row.get(_COL_REST_TYPE, "")).strip()
    if rt:
        slug = re.sub(r"\s+", "-", rt.lower())
        slug = re.sub(r"[^a-z0-9-]", "", slug)
        if slug:
            tags.append(slug[:80])
    return tags


def _row_to_record(row: Mapping[str, Any], index: int) -> Optional[RestaurantRecord]:
    name = str(row.get(_COL_NAME, "")).strip()
    if not name:
        return None

    rating = _parse_rate(row.get(_COL_RATE))
    if rating is None:
        return None

    cost = _parse_cost(row.get(_COL_COST))
    if cost is None:
        cost = 600
        cost_band = BudgetBand.medium
    else:
        cost_band = _cost_to_band(cost)

    address = str(row.get(_COL_ADDRESS, "") or "")
    city = _infer_city(
        address,
        str(row.get(_COL_LISTED_CITY, "") or ""),
        str(row.get(_COL_LOCATION, "") or ""),
    )

    cuisines = _split_cuisines(row.get(_COL_CUISINES))
    tags = _tags_from_row(row)

    return RestaurantRecord(
        id=f"zomato-{index:08d}",
        name=name,
        city=city,
        cuisines=cuisines,
        cost_band=cost_band,
        rating=rating,
        tags=tags,
    )


def _iter_csv_direct(csv_path: str) -> Iterator[Mapping[str, Any]]:
    """Read a local CSV with stdlib csv — no HuggingFace, no pickle, no Arrow."""
    import csv as _csv
    with open(csv_path, newline="", encoding="utf-8") as fh:
        reader = _csv.DictReader(fh)
        for row in reader:
            yield row


def _iter_hf_dataset(csv_path_override: Optional[str] = None) -> Iterator[Mapping[str, Any]]:
    """Load dataset rows.
    - Local CSV path → plain csv.DictReader (no HuggingFace, avoids pickle issues on Python 3.9).
    - No path → HuggingFace hub with streaming=True.
    """
    csv_path = csv_path_override if csv_path_override is not None else settings.zomato_csv_path
    if csv_path:
        yield from _iter_csv_direct(csv_path)
        return

    # HuggingFace hub path — streaming avoids full download and pickle caching
    cache_dir = _datasets_cache_dir()
    ds = load_dataset(
        settings.zomato_dataset_id,
        split="train",
        streaming=True,
        cache_dir=cache_dir,
    )
    for row in ds:
        yield row


def load_catalog(
    *,
    force_reload: bool = False,
    csv_path_override: Optional[str] = None,
) -> list[RestaurantRecord]:
    """
    Load and normalize the full catalog into memory (MVP persistence strategy).

    Results are cached in-process unless ``force_reload`` is True. If
    ``csv_path_override`` is set (e.g. tests), caching is bypassed.
    """
    use_cache = csv_path_override is None
    if use_cache and not force_reload:
        cached = _get_cached_catalog()
        if cached is not None:
            return cached

    records: list[RestaurantRecord] = []
    skipped = 0
    for i, row in enumerate(_iter_hf_dataset(csv_path_override)):
        rec = _row_to_record(row, i)
        if rec is None:
            skipped += 1
            continue
        records.append(rec)

    logger.info(
        "catalog loaded: %s rows, %s skipped (invalid name/rating)",
        len(records),
        skipped,
    )
    if use_cache:
        _set_cached_catalog(records, skipped)
    return records


def _get_cached_catalog() -> Optional[list[RestaurantRecord]]:
    return _catalog_store["rows"]


def _set_cached_catalog(rows: list[RestaurantRecord], skipped: int) -> None:
    _catalog_store["rows"] = rows
    _catalog_store["skipped"] = skipped


def clear_catalog_cache() -> None:
    """Test helper: drop in-memory catalog."""
    _catalog_store["rows"] = None
    _catalog_store["skipped"] = 0


def catalog_summary(catalog: Optional[Sequence[RestaurantRecord]] = None) -> CatalogSummary:
    """Row counts, skip count from last load, and city distribution snapshot."""
    if catalog is None:
        cat = load_catalog()
        skipped = int(_catalog_store.get("skipped", 0))
    else:
        cat = list(catalog)
        skipped = 0
    cities = {r.city for r in cat}
    sample = sorted(cities)[:30]
    return CatalogSummary(
        row_count=len(cat),
        skipped_invalid_rows=skipped,
        unique_cities=len(cities),
        sample_cities=sample,
    )


def normalize_location_query(location: str) -> str:
    """Map user location string toward canonical city name used in ``RestaurantRecord.city``."""
    key = location.strip().lower()
    if key in _CITY_ALIASES:
        return _CITY_ALIASES[key]
    return location.strip().title()


def filter_catalog(
    records: Sequence[RestaurantRecord],
    *,
    location: Optional[str] = None,
    cuisine_contains: Optional[str] = None,
    minimum_rating: Optional[float] = None,
    budget: Optional[BudgetBand] = None,
    limit: int = 50,
) -> list[RestaurantRecord]:
    """
    Deterministic filter (Phase 3 will extend). Case-insensitive cuisine substring match.
    """
    out: list[RestaurantRecord] = []
    loc_norm = normalize_location_query(location).lower() if location else None
    cuisine_q = cuisine_contains.strip().lower() if cuisine_contains else None
    for r in records:
        if loc_norm and loc_norm not in r.city.lower():
            continue
        if cuisine_q and not any(cuisine_q in c.lower() for c in r.cuisines):
            continue
        if minimum_rating is not None and r.rating < minimum_rating:
            continue
        if budget is not None and r.cost_band != budget:
            continue
        out.append(r)
        if len(out) >= limit:
            break
    return out


def get_source_column_names(csv_path_override: Optional[str] = None) -> list[str]:
    """Columns present in the raw CSV / dataset (streaming read of first row)."""
    cache_dir = _datasets_cache_dir()
    csv_path = (
        csv_path_override
        if csv_path_override is not None
        else settings.zomato_csv_path
    )
    if csv_path:
        # Use stdlib csv to avoid HuggingFace pickle issues on Python 3.9
        import csv as _csv
        with open(csv_path, newline="", encoding="utf-8") as fh:
            reader = _csv.DictReader(fh)
            return list(reader.fieldnames or [])
    else:
        cache_dir = _datasets_cache_dir()
        ds = load_dataset(
            settings.zomato_dataset_id,
            split="train",
            streaming=True,
            cache_dir=cache_dir,
        )
        cols = getattr(ds, "column_names", None)
        if cols:
            return list(cols)
        row = next(iter(ds))
        return list(row.keys())
