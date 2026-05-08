# Phase-Wise Architecture

This document decomposes the [problem statement](./problemStatement.md) into build phases. Each phase has a clear scope, outputs, and dependencies so you can implement incrementally while keeping an end-to-end path: **ingest → preferences → filter → LLM → display**.

---

## Alignment With System Workflow

| Problem statement step | Primary phase |
|------------------------|---------------|
| 1. Data ingestion | Phase 1 |
| 2. User input | Phase 2 |
| 3. Integration layer | Phase 3 |
| 4. Recommendation engine | Phase 4 |
| 5. Output display | Phase 5 |

Phases **0** and **6** cover foundation and hardening so the core pipeline is testable and deployable.

Phase **7** covers collaborative development workflow using GitHub.

---

## End-to-End View

```mermaid
flowchart LR
  subgraph P1["Phase 1: Data"]
    DS[(Dataset)] --> ETL[Load / normalize / cache]
  end
  subgraph P2["Phase 2: Preferences"]
    UI[Forms / API schema] --> Prefs[Validated preferences]
  end
  subgraph P3["Phase 3: Integration"]
    Prefs --> Filter[Deterministic filter]
    ETL --> Filter
    Filter --> Ctx[Prompt context builder]
  end
  subgraph P4["Phase 4: LLM"]
    Ctx --> LLM[LLM rank + explain]
  end
  subgraph P5["Phase 5: Display"]
    LLM --> Out[Structured response + UI]
  end
  P1 --> P3
  P2 --> P3
```

---

## Phase 0 — Foundation

**Goal:** Repository layout, runtime, configuration, and contracts so later phases plug in cleanly.

| Item | Description |
|------|-------------|
| **Stack** | Choose language (e.g. Python + FastAPI, or Node) and how you run the app locally. |
| **Configuration** | Environment for Hugging Face paths/cache, LLM provider base URL and API keys, feature flags. |
| **Contracts** | Define JSON schemas (or Pydantic models) for `UserPreferences`, `RestaurantRecord`, `RecommendationItem`, and `RecommendResponse` so Phases 2–5 share one source of truth. |
| **Deliverables** | Runnable skeleton app, `.env.example`, README run instructions. |

**Exit criteria:** App starts; health check endpoint (or equivalent) works without dataset or LLM.

---

## Phase 1 — Data Ingestion & Storage

**Goal:** Ground the system in [ManikaSaini/zomato-restaurant-recommendation](https://huggingface.co/datasets/ManikaSaini/zomato-restaurant-recommendation): load, normalize, and expose a queryable restaurant catalog.

| Item | Description |
|------|-------------|
| **Ingestion** | Download/load dataset (HF `datasets` or Parquet export); handle schema discovery. |
| **Normalization** | Map raw columns to `RestaurantRecord`: name, city/area, cuisines, cost band, rating, optional text fields for tags. |
| **Persistence strategy** | In-memory for MVP, or SQLite/Parquet for faster repeat queries; document refresh policy. |
| **Deliverables** | Module or service: `load_catalog()`, typed records, basic stats (row count, cities) for sanity checks. |

**Exit criteria:** You can list/filter restaurants **without** an LLM using only code and data.

**Depends on:** Phase 0.

---

## Phase 2 — User Preferences Input

**Goal:** Capture structured preferences exactly as specified in the problem statement.

| Item | Description |
|------|-------------|
| **Input surface** | CLI, REST API, or web form—consistent with Phase 0 schemas. |
| **Validation** | Location and cuisine as allowed lists or fuzzy match rules; budget enum; minimum rating bounds; optional tags. |
| **Defaults & errors** | Clear 400 responses or UI messages when constraints are impossible (e.g. no city match). |
| **Deliverables** | `POST /preferences` or equivalent + validation tests. |

**Exit criteria:** Invalid input never reaches the filter; valid payloads serialize to `UserPreferences`.

**Depends on:** Phase 0 (schemas).

---

## Phase 3 — Integration Layer (Filter + Prompt Context)

**Goal:** Deterministic candidate set and a **model-safe** context bundle—no hallucinated facts.

| Item | Description |
|------|-------------|
| **Filtering** | Hard constraints: location, budget band, cuisine (intersection or primary cuisine policy), minimum rating, optional tag rules. |
| **Candidate cap** | Top-N by rating or hybrid score before LLM to control tokens and latency. |
| **Context builder** | Serialize only allowed fields into a fixed template (table or bullets) with explicit instruction: *rank and explain using only this list*. |
| **Deliverables** | `filter_catalog(prefs) -> list[RestaurantRecord]` and `build_llm_context(candidates, prefs) -> str` (or structured messages). |

**Exit criteria:** Same preferences always yield the same candidate IDs (given fixed data version).

**Depends on:** Phases 1–2.

---

## Phase 4 — Recommendation Engine (LLM)

**Goal:** LLM ranks and explains; it does **not** invent restaurants or numeric facts.

| Item | Description |
|------|-------------|
| **Provider** | OpenAI-compatible or other SDK; retries, timeouts, token limits. |
| **Prompting** | System + user messages: output format (JSON preferred) listing `restaurant_id` or name from context, `rank`, `explanation`. |
| **Grounding guardrails** | Post-parse validation: every recommended ID/name must exist in the candidate list; drop or repair invalid rows. |
| **Deliverables** | `recommend(prefs) -> RecommendResponse` wiring filter → context → LLM → validate → map to full records. |

**Exit criteria:** Success criteria from problem statement: grounded recommendations, deterministic filter + LLM for narrative/ranking.

**Depends on:** Phase 3.

---

## Phase 5 — Output Display

**Goal:** Scannable UI or API responses: name, cuisines, rating, estimated cost, AI explanation.

| Item | Description |
|------|-------------|
| **API** | Stable response shape for clients; optional streaming for explanations later. |
| **UI** | Ranked cards or table; loading and empty states (“no restaurants match—relax rating or cuisine”). |
| **Deliverables** | Polished read path from `RecommendResponse` to human-visible layout. |

**Exit criteria:** End-to-end demo: preferences → top-k list with explanations.

**Depends on:** Phase 4.

---

## Phase 6 — Hardening & Operations (Optional but Recommended)

**Goal:** Quality, observability, and safe iteration.

| Item | Description |
|------|-------------|
| **Testing** | Unit tests for filter and validation; golden-file or snapshot tests for prompt shape (redact secrets). |
| **Observability** | Structured logs for filter counts, LLM latency, validation failures. |
| **Cost & safety** | Rate limits, max tokens, optional content filters on user free-text. |
| **Data versioning** | Pin dataset revision or export hash for reproducibility. |

**Exit criteria:** You can debug mismatches between “what user asked” and “what model returned” quickly.

**Depends on:** Phases 1–5.

---

## Phase 7 — Collaborative Development with GitHub

**Goal:** Establish a structured GitHub-based development workflow so the team can collaborate safely, track changes, and ship features without breaking the main branch.

| Item | Description |
|------|-------------|
| **Repository setup** | Single repo with `main` as the protected production branch. All work happens on feature branches; no direct pushes to `main`. |
| **Branching strategy** | Use `feature/<phase>-<short-description>` for new work (e.g. `feature/phase4-groq-retry`), `fix/<description>` for bug fixes, and `chore/<description>` for non-functional changes (docs, deps). |
| **Commit conventions** | Follow Conventional Commits: `feat:`, `fix:`, `docs:`, `chore:`, `test:` prefixes. Keep messages under 72 characters in the subject line; use the body for context. |
| **Pull requests** | Every change goes through a PR. PR title mirrors the commit convention. Description must include: what changed, how to test it, and any env variable additions. |
| **Branch protection rules** | On GitHub → Settings → Branches: require PR review before merge, require status checks to pass (CI), disallow force-push on `main`. |
| **CI with GitHub Actions** | On every PR: run `pip install -r requirements.txt`, lint with `ruff`, and execute `pytest tests/`. Frontend: `npm install && npm run lint && npm run build`. Blocks merge if any step fails. |
| **Secrets management** | Store `GROQ_API_KEY`, `HF_TOKEN`, and any other secrets in GitHub → Settings → Secrets and Variables → Actions. Never commit `.env` (already in `.gitignore`). Reference in workflows as `${{ secrets.GROQ_API_KEY }}`. |
| **Issue tracking** | Use GitHub Issues for bugs and feature requests. Link each PR to its issue with `Closes #<issue-number>` in the PR description for automatic closure on merge. |
| **Releases & tags** | Tag stable milestones: `git tag v0.1.0` after Phase 4 is verified, `v0.2.0` after Phase 5 UI is polished. Push tags with `git push --tags`. Use GitHub Releases to attach release notes. |
| **Deliverables** | `.github/workflows/ci.yml` for automated checks, branch protection enabled, at least one merged PR demonstrating the full workflow. |

**Exit criteria:** No code reaches `main` without a passing CI run and at least one review. Any team member can clone the repo, copy `.env.example` to `.env`, and run the app in under 5 minutes.

**Depends on:** Phase 6 (tests and observability must exist for CI to be meaningful).

---

### Recommended GitHub Actions CI workflow

```yaml
# .github/workflows/ci.yml
name: CI

on:
  pull_request:
    branches: [main]
  push:
    branches: [main]

jobs:
  backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - run: pip install -r requirements.txt
      - run: pip install ruff pytest
      - run: ruff check app/
      - run: pytest tests/ -v
        env:
          ZOMATO_CSV_PATH: tests/fixtures/zomato_sample.csv
          GROQ_API_KEY: ${{ secrets.GROQ_API_KEY }}

  frontend:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: frontend
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: "20"
          cache: "npm"
          cache-dependency-path: frontend/package-lock.json
      - run: npm ci
      - run: npm run lint
      - run: npm run build
```

### Branch naming quick reference

| Type | Pattern | Example |
|------|---------|---------|
| New feature | `feature/<phase>-<desc>` | `feature/phase5-restaurant-card` |
| Bug fix | `fix/<desc>` | `fix/phase3-cuisine-filter` |
| Documentation | `docs/<desc>` | `docs/phase7-github-workflow` |
| Dependency / chore | `chore/<desc>` | `chore/update-fastapi` |
| Hotfix on main | `hotfix/<desc>` | `hotfix/groq-timeout` |

---

```mermaid
flowchart TB
  P0[Phase 0: Foundation]
  P1[Phase 1: Data]
  P2[Phase 2: Preferences]
  P3[Phase 3: Integration]
  P4[Phase 4: LLM]
  P5[Phase 5: Display]
  P6[Phase 6: Hardening]
  P7[Phase 7: GitHub Workflow]
  P0 --> P1
  P0 --> P2
  P1 --> P3
  P2 --> P3
  P3 --> P4
  P4 --> P5
  P5 --> P6
  P6 --> P7
```

---

## Minimal MVP Path

If time is limited, implement **0 → 1 → 2 → 3** first (filter-only recommendations with static explanations or templated text), then add **4** (LLM) and **5** (UI polish). That preserves **grounded, deterministic filtering** early while deferring model complexity.
