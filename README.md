# Restaurant Recommendation Service

Zomato-inspired, AI-assisted restaurant recommendations. This repo follows the phased plan in [`doc/phase-wise-architecture.md`](doc/phase-wise-architecture.md).

**Phase 0–4 (current):** FastAPI app, configuration, **Phase 1** in [`app/phase1/`](app/phase1/) (catalog ingestion), **Phase 2** in [`app/phase2/`](app/phase2/) (preferences validation), **Phase 3** in [`app/phase3/`](app/phase3/) (integration), and **Phase 4** in [`app/phase4/`](app/phase4/) (Groq-backed recommendation engine).

## Prerequisites

- Python 3.9+

## Setup

```bash
cd /path/to/zomatoProject-1
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Edit `.env` when you implement later phases (Hugging Face cache paths, LLM keys).

## Run locally

```bash
source .venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

- Health: [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)
- OpenAPI docs: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

## Project layout

| Path | Purpose |
|------|---------|
| `app/main.py` | FastAPI app and routes |
| `app/config.py` | Settings from environment (HF cache, dataset id / local CSV, LLM, feature flags) |
| `app/schemas.py` | Domain models + `CatalogSummary` |
| `app/phase1/` | **Phase 1:** `catalog.py` — `load_catalog()`, normalization, `filter_catalog()`, etc. |
| `app/phase2/` | **Phase 2:** `preferences.py` — `validate_and_normalize_preferences()`, optional-tag allowlist |
| `app/phase3/` | **Phase 3:** `integration.py` — deterministic candidates + `build_llm_context()` |
| `app/phase4/` | **Phase 4:** `recommender.py` — Groq call, JSON parsing, grounding validation, fallback |
| `doc/` | Problem statement, architecture, edge cases |

## Catalog (Phase 1)

- Default source: Hugging Face [`ManikaSaini/zomato-restaurant-recommendation`](https://huggingface.co/datasets/ManikaSaini/zomato-restaurant-recommendation) (`zomato.csv`). First load downloads ~574 MB; set `HF_HOME` or `HF_DATASETS_CACHE` to control cache location.
- Offline / tests: set `ZOMATO_CSV_PATH` in `.env` to an absolute path of a CSV with the same columns, or use the tiny sample at `tests/fixtures/zomato_sample.csv`.

Query examples (after `uvicorn` is running):

- `GET /catalog/summary`
- `GET /catalog/restaurants?location=Bangalore&cuisine_contains=Chinese&minimum_rating=4&limit=10`
- `POST /preferences` with a `UserPreferences` JSON body (see `/docs`). Returns normalized preferences or **400** with `code`, `message`, and `suggestions` when the catalog cannot satisfy the request.
- `POST /phase3/candidates` with `UserPreferences` to see deterministic candidates (pre/post counts + capped list)
- `POST /phase3/llm-context` with `UserPreferences` to get the Phase 3 prompt payload for Phase 4
- `POST /recommendations` with `UserPreferences` to get Groq-ranked, grounded recommendations

## Contracts

Downstream phases should import from `app.schemas`, `app.config`, and `app.phase1` through `app.phase4` (or their submodules).
