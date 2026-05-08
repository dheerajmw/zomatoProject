# Edge Cases & Failure Modes

This catalog aligns with the [problem statement](./problemStatement.md) (grounded recommendations, deterministic filtering, end-to-end flow) and the [phase-wise architecture](./phase-wise-architecture.md). Use it for validation rules, tests, and product copy (empty states, errors).

**Legend**

- **Detect:** Where the issue surfaces (phase).
- **Expected behavior:** What the system should do.
- **Why:** Tie to success criteria or operational safety.

---

## Phase 0 — Foundation & contracts

| Edge case | Detect | Expected behavior | Why |
|-----------|--------|-------------------|-----|
| Missing or invalid `LLM_API_KEY` / HF cache path | Startup or first LLM call | Fail fast with a clear config error; do not partially run recommendations. | Avoid silent degradation and mystery 500s. |
| Schema drift: API accepts fields not in `UserPreferences` | Request parsing | Reject unknown fields (strict) or strip and log (lenient)—pick one policy and document it. | Consistent contracts across Phases 2–5. |
| Feature flag: LLM disabled | Config | Route to filter-only or templated explanations; same response shape as LLM path. | MVP path from architecture doc. |

---

## Phase 1 — Data ingestion & catalog

| Edge case | Detect | Expected behavior | Why |
|-----------|--------|-------------------|-----|
| Hugging Face download fails (network, quota) | `load_catalog()` | Surface actionable error; optional retry with backoff; no empty “success” catalog without notice. | User trusts grounding; silent empty data breaks that. |
| Dataset schema differs from assumptions (column rename, missing column) | Load / normalize | Map known aliases; for required fields missing, fail load with schema report or fill with explicit `unknown` policy. | Prevents garbage filtering later. |
| Null / malformed rating or cost | Normalization | Define rules: drop row, or coerce with bounds; never pass `NaN` into comparisons without handling. | Deterministic filter needs defined ordering. |
| Duplicate restaurant names or IDs in source | Ingestion | Deduplicate by stable key if present; else composite key (name + area); document collisions. | LLM grounding by name can attach wrong row if duplicates exist. |
| Extreme cardinality: very long cuisine strings or multiline text | Normalization | Truncate or token-budget fields used in prompts; keep full text only for display if needed. | Token limits and latency (Phase 3–4). |
| Stale cached Parquet vs pinned dataset revision | Ops | Log dataset hash/version in health or metadata endpoint. | Reproducibility (Phase 6). |

---

## Phase 2 — User preferences input

| Edge case | Detect | Expected behavior | Why |
|-----------|--------|-------------------|-----|
| Location not in catalog (typo, unsupported city) | Validation | 400 with suggestion list or fuzzy match threshold; never run filter with a “dead” city silently. | Clear errors per architecture exit criteria. |
| Ambiguous location (“DL” for Delhi) | Validation | Resolve via alias table or fuzzy match; if ambiguous, ask user to disambiguate. | Prevents wrong-city results. |
| Minimum rating above global max (e.g. 5.5) or negative | Validation | Reject with bounds; clamping is a product decision—if you clamp, log it. | Invalid input must not reach filter. |
| Budget enum typo (`mediumd`) | Validation | Reject or normalize with explicit mapping only. | Consistent filter semantics. |
| Cuisine that no restaurant lists (niche tag) | Validation vs filter | Valid request is fine; empty result handled in Phase 3/5—not a validation error unless you maintain an “allowed cuisine” list. | Distinguish bad input from no match. |
| Conflicting optional tags (e.g. “quiet” + “late-night party”) | Validation | Allow (let filter/LLM handle) or reject—document policy. | Avoid undefined UX. |
| Empty body or all-null preferences | Validation | Reject or apply documented defaults; do not imply “no filter” unless that is explicit and safe. | Huge candidate lists blow token budget. |
| Unicode / RTL / emoji in free-text preferences (if supported) | Parsing | Normalize Unicode; set max length; reject control characters. | Safety and stable prompts. |

---

## Phase 3 — Integration (filter + prompt context)

| Edge case | Detect | Expected behavior | Why |
|-----------|--------|-------------------|-----|
| Zero candidates after filters | Post-filter | Do not call LLM with empty context; return structured empty result + UX copy to relax constraints. | Saves cost; matches “no match” success path. |
| Exactly one candidate | Post-filter | Still run LLM only if you need narrative; or short-circuit with templated explanation—document choice. | Latency and cost. |
| Thousands of candidates before cap | Pre-cap | Apply deterministic sort + `top_n` before LLM; log pre/post counts. | Token limits and deterministic filter. |
| Cuisine matching policy unclear (“Italian” vs “Italian, Pizza”) | Filter | Define: substring, token set, primary cuisine only—same inputs → same IDs. | Determinism requirement. |
| Budget band overlaps raw cost (boundary values) | Filter | Document inclusive/exclusive boundaries; add tests at edges. | Avoid off-by-one surprises. |
| Optional tags not present in data | Filter | Tags may be no-ops unless mapped to columns; document so users are not misled. | Grounding: do not fake tag fulfillment in filter. |
| Identical ratings → sort tie-break | Ordering | Secondary key (name, id) for stable ordering. | Same prefs → same candidate order. |

---

## Phase 4 — LLM recommendation engine

| Edge case | Detect | Expected behavior | Why |
|-----------|--------|-------------------|-----|
| LLM returns restaurant not in candidate list | Post-parse validation | Drop invalid rows; if too few remain, retry once with stricter prompt or fall back to deterministic top-k + templated blurb. | **Grounding** success criterion. |
| LLM copies a name with typo vs catalog | Validation | Fuzzy match within candidates with threshold; else treat as invalid. | User sees correct row data. |
| Duplicate ranks or missing ranks | Parse | Normalize ranks 1..k or reject and repair. | Stable display. |
| Valid JSON wrapped in markdown fences | Parse | Strip fences; on failure, retry or use structured output API if available. | Robustness. |
| LLM timeout / rate limit / empty response | Provider errors | Retry with backoff; then degrade to ranked list without AI explanation with clear flag `explanation_unavailable`. | Availability without inventing content. |
| LLM invents numeric rating or price | Narrative check | Display numbers only from `RestaurantRecord`; strip or ignore model-supplied metrics in UI. | **No fake attributes** criterion. |
| Candidate list near token limit | Pre-call | Shrink fields in context or reduce N; never truncate mid-row silently without knowing. | Avoid broken prompts. |
| Harmful or off-topic user content in optional text | Moderation | Optional filter or block; refuse and log policy event. | Safety (Phase 6). |

---

## Phase 5 — Output display

| Edge case | Detect | Expected behavior | Why |
|-----------|--------|-------------------|-----|
| Partial failure: filter OK, LLM failed | Response assembly | Show restaurants with `explanation` null and inline message. | Clear, scannable results still. |
| Long explanations overflow UI | Render | Clamp with expand/collapse; preserve full text in API. | UX polish. |
| Missing image or optional field in data | Render | Placeholder; do not break layout. | Resilient UI. |
| Screen reader / keyboard-only | UI | Rank and headings reflect order; explanations associated with each item. | Accessibility baseline. |

---

## Phase 6 — Hardening & operations

| Edge case | Detect | Expected behavior | Why |
|-----------|--------|-------------------|-----|
| Concurrent requests, same user spamming | Gateway / app | Rate limit; idempotency optional for same payload. | Cost control. |
| PII in logs (raw prompts with addresses) | Logging | Redact or hash; log candidate IDs not full free-text if sensitive. | Privacy. |
| Clock skew / retries double-charging LLM | Idempotency | Optional request id dedup at application layer. | Cost. |

---

## Cross-phase scenarios (integration tests)

These exercise the full pipeline from [problem statement](./problemStatement.md):

1. **Happy path:** Known city + cuisine + moderate rating → non-empty list, explanations reference only returned names.
2. **No match:** Absurd min rating for city → empty list, no LLM call (if policy), helpful copy.
3. **Huge match:** Many rows → cap applied, response size stable, latency under threshold.
4. **LLM hallucination injection (test double):** Model returns fake venue → validator removes it; user still sees grounded rows.
5. **Cold start:** First request after deploy triggers dataset load; second is fast (cache warm).

---

## Traceability matrix

| Theme | Problem statement | Primary phases |
|--------|-------------------|----------------|
| Grounded recommendations (no fabricated venues) | Success criteria | 1, 3, 4 |
| Deterministic filter | Success criteria | 1, 2, 3 |
| LLM for ranking + explanation only | Workflow §4 | 3, 4 |
| Clear results + empty states | Workflow §5 | 2, 3, 5 |
| Config & safety | Implicit | 0, 4, 6 |

---

## Related documents

- [Problem statement](./problemStatement.md)
- [Phase-wise architecture](./phase-wise-architecture.md)
