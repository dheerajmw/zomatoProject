# Problem Statement: AI-Powered Restaurant Recommendation System

**Context:** Zomato-inspired use case.

Build an **AI-powered restaurant recommendation service** that suggests restaurants from structured data and uses a **large language model (LLM)** to produce personalized, natural-language explanations and rankings.

---

## Objective

Deliver an application that:

- Accepts **user preferences** (location, budget, cuisine, minimum rating, and optional constraints such as family-friendly or quick service).
- Uses a **real-world restaurant dataset** for factual grounding.
- Calls an **LLM** to rank options and explain *why* each pick fits the user.
- Presents **clear, scannable results** in the UI or API response.

---

## System Workflow

### 1. Data ingestion

- Load and preprocess the Zomato-style dataset from Hugging Face:  
  [ManikaSaini/zomato-restaurant-recommendation](https://huggingface.co/datasets/ManikaSaini/zomato-restaurant-recommendation)
- Normalize and retain fields you need for filtering and display, for example: restaurant name, area/city, cuisines, approximate cost, ratings, and any other columns useful for preference matching.

### 2. User input

Collect structured preferences, for example:

- **Location** (e.g., Delhi, Bangalore)
- **Budget band** (low / medium / high)
- **Cuisine** (e.g., Italian, Chinese)
- **Minimum rating**
- **Optional tags** (e.g., family-friendly, quick service)

### 3. Integration layer

- **Filter** the dataset to a candidate set that matches hard constraints (location, budget, cuisine, minimum rating).
- **Shape** that subset into a compact, model-friendly structure (tables or bullet lists) for the prompt.
- **Design prompts** so the LLM reasons over *only* the provided candidates, ranks them, and avoids inventing venues or facts not in the data.

### 4. Recommendation engine

Use the LLM to:

- **Rank** restaurants within the filtered set.
- **Explain** each recommendation in plain language (fit to budget, cuisine, rating, and optional preferences).
- Optionally **summarize** trade-offs when no option is a perfect match.

### 5. Output display

Present the top recommendations in a consistent, user-friendly layout, for example:

| Field | Purpose |
|--------|---------|
| Restaurant name | Identity |
| Cuisine(s) | Match to taste |
| Rating | Quality signal |
| Estimated cost | Budget alignment |
| AI explanation | Why this pick fits the user |

---

## Success criteria (suggested)

- Recommendations are **grounded** in the dataset (no fabricated restaurants).
- Filtering is **deterministic**; the LLM adds **ranking and narrative**, not fake attributes.
- The flow is **end-to-end**: ingest → preferences → filter → LLM → display.
