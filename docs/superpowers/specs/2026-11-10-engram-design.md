# engram — Design Spec

**Date:** 2026-11-10  
**Status:** Approved

---

## Project Identity

| | |
|---|---|
| **Name** | `engram` |
| **Tagline** | Persistent memory for AI agents — graph-backed, vector-searchable, with biologically-inspired memory decay |
| **License** | Apache 2.0 |
| **Python** | 3.10+ |
| **Install** | `pip install engram` |

---

## Goals

- Build a functional, installable Python library that gives AI agents persistent memory **with time-aware decay**
- Implement the Ebbinghaus forgetting curve so memory strength degrades over time and gets reinforced on recall
- Demonstrate open-source project structure: README, CONTRIBUTING.md, CI, issue templates, PR templates
- Pre-create GitHub issues sized for contributor-level work (friends/colleagues can contribute)

---

## Key Differentiator — Memory Decay (Ebbinghaus Forgetting Curve)

Most AI memory systems treat all stored facts as equally important forever. `engram` models memory the way human brains work: memory **fades over time** unless reinforced.

Every memory item has a `strength` value (0.0–1.0) that decays exponentially based on elapsed time since it was last accessed:

```
strength(t) = initial_strength × e^(−decay_rate × hours_elapsed)
```

- `remember()` stores a memory at full strength (1.0)
- `recall()` **reinforces** retrieved memories (boosts their strength), and ranks results by `relevance_score × strength`
- `improve()` resets strength to 1.0 (correction = full reinforcement)
- A new `prune(dataset, threshold)` function removes memories below a strength threshold
- `recall()` results include a `strength` field so agents can see how "fresh" a memory is

**Why this matters:** an agent that remembered something 6 months ago and never referenced it again should trust it less than something recalled last week. This is genuinely useful and is not present in existing tools.

---

## Architecture

```
User/Agent
    │
    ▼
engram API (remember / recall / improve / forget / prune)
    │
    ├── MemoryGraph (NetworkX)      ← stores entities + relationships
    ├── VectorIndex (ChromaDB)      ← semantic search over memory
    ├── DecayEngine                 ← Ebbinghaus strength scoring
    └── MetaStore (SQLite)          ← dataset registry, timestamps, strength values
```

### Components

**MemoryGraph (NetworkX)**  
Stores extracted entities as nodes and their relationships as directed edges. Each node carries a `content` attribute (the raw sentence it came from) and a `dataset` tag for scoped deletion.

**VectorIndex (ChromaDB)**  
Stores text chunks as embeddings using ChromaDB's default embedding model (sentence-transformers). Each embedding is tagged with `dataset` metadata for filtered recall.

**MetaStore (SQLite via sqlite3)**  
A lightweight registry tracking datasets, item counts, and — critically — per-memory `strength`, `last_accessed_at`, and `created_at` timestamps. This is the source of truth for the decay engine.

---

## Core API

```python
import engram

# Store content (starts at full strength 1.0)
await engram.remember("Marie Curie was born in Warsaw.", dataset="science")

# Retrieve context (reinforces retrieved items; results ranked by relevance × strength)
results = await engram.recall("Where was Marie Curie born?", datasets=["science"])
# [{"text": "...", "score": 0.91, "strength": 0.87, "dataset": "science", "related": [...]}]

# Correct or enrich existing memory (resets strength to 1.0)
await engram.improve("Marie Curie won two Nobel Prizes.", dataset="science")

# Remove weak/stale memories below a strength threshold
await engram.prune(dataset="science", threshold=0.2)

# Delete a dataset entirely
await engram.forget(dataset="science")
```

### Function Contracts

| Function | Input | Output | Side Effects |
|---|---|---|---|
| `remember(text, dataset)` | str, str | None | Adds graph nodes/edges + vector embeddings, strength=1.0 |
| `recall(query, datasets)` | str, list[str] | list[dict] | Boosts strength of returned items |
| `improve(text, dataset)` | str, str | None | Appends to dataset, resets strength to 1.0 |
| `prune(dataset, threshold)` | str, float | int (removed count) | Deletes items below strength threshold |
| `forget(dataset)` | str | None | Deletes all graph nodes, vectors, metadata |

### `recall` result shape

```python
[
  {
    "text": "Marie Curie was born in Warsaw.",
    "score": 0.91,          # vector similarity
    "strength": 0.87,       # current decay-adjusted strength
    "dataset": "science",
    "related": ["Warsaw is the capital of Poland."]
  }
]
```

---

## DecayEngine

The `DecayEngine` computes current memory strength on demand using the Ebbinghaus formula:

```python
import math
from datetime import datetime, timezone

DECAY_RATE = 0.005  # configurable; default gives ~50% strength after ~6 days

def current_strength(initial_strength: float, last_accessed_at: datetime) -> float:
    hours = (datetime.now(timezone.utc) - last_accessed_at).total_seconds() / 3600
    return initial_strength * math.exp(-DECAY_RATE * hours)

def reinforce(current: float, boost: float = 0.3) -> float:
    return min(1.0, current + boost)
```

`DECAY_RATE` is configurable via `ENGRAM_DECAY_RATE` env var so contributors can experiment with different curves.

---

## Entity Extraction

For the initial implementation, use **spaCy `en_core_web_sm`** to extract named entities (PERSON, GPE, ORG, etc.) from ingested text. Each sentence is also stored as a full-text node regardless of entity extraction, so nothing is lost if spaCy finds no entities.

Fallback: if spaCy is not installed, store the full sentence as a single node.

---

## Data Flow

### `remember(text, dataset)`
1. Split text into sentences
2. For each sentence: extract entities with spaCy
3. Add sentence as a node in MemoryGraph; add entity nodes; add edges (sentence → entity)
4. Upsert sentence into ChromaDB with `dataset` metadata
5. Insert row into MetaStore: `(id, dataset, text, strength=1.0, created_at=now, last_accessed_at=now)`

### `recall(query, datasets)`
1. Query ChromaDB for top-5 matches filtered by `datasets`
2. For each match, fetch its MetaStore row; compute `current_strength` via DecayEngine
3. Look up its node in MemoryGraph and collect 1-hop neighbors
4. Re-rank results by `vector_score × current_strength`
5. Update `last_accessed_at` and `strength = reinforce(current_strength)` in MetaStore for each returned item
6. Return ranked list of `{text, score, strength, dataset, related}`

### `improve(text, dataset)`
Calls `remember(text, dataset)` then resets `strength=1.0`, `last_accessed_at=now` for all items in the dataset.

### `prune(dataset, threshold=0.2)`
1. Fetch all MetaStore rows for `dataset`
2. Compute `current_strength` for each
3. Delete rows (+ graph nodes + ChromaDB entries) where `strength < threshold`
4. Return count of removed items

### `forget(dataset)`
1. Remove all MemoryGraph nodes tagged with `dataset`
2. Delete ChromaDB collection entries where `dataset` metadata matches
3. Delete all MetaStore rows for `dataset`

---

## Persistence

- ChromaDB stores data in `~/.engram/chroma/` by default (configurable via `ENGRAM_HOME` env var)
- NetworkX graph is serialized to `~/.engram/graph.pkl` on each write
- SQLite DB lives at `~/.engram/meta.db`

---

## Repository Structure

```
engram/
├── engram/
│   ├── __init__.py          ← public API (remember, recall, improve, forget, prune)
│   ├── graph.py             ← MemoryGraph (NetworkX)
│   ├── vector.py            ← VectorIndex (ChromaDB)
│   ├── decay.py             ← DecayEngine (Ebbinghaus formula)
│   ├── meta.py              ← MetaStore (SQLite)
│   └── extractor.py         ← entity extraction (spaCy)
├── tests/
│   ├── test_remember.py
│   ├── test_recall.py
│   ├── test_decay.py
│   └── test_forget.py
├── examples/
│   └── quickstart.py
├── .github/
│   ├── workflows/
│   │   └── ci.yml           ← lint (ruff) + tests (pytest) on every PR
│   ├── ISSUE_TEMPLATE/
│   │   ├── bug_report.md
│   │   └── feature_request.md
│   └── PULL_REQUEST_TEMPLATE.md
├── CONTRIBUTING.md
├── README.md
├── LICENSE                  ← Apache 2.0
└── pyproject.toml
```

---

## Dependencies

```toml
[project.dependencies]
chromadb = ">=0.4"
networkx = ">=3.0"
spacy = ">=3.7"   # optional but recommended
```

spaCy model (`en_core_web_sm`) is downloaded as a post-install step documented in the README.

---

## MetaStore Schema

```sql
CREATE TABLE memories (
    id          TEXT PRIMARY KEY,   -- UUID
    dataset     TEXT NOT NULL,
    text        TEXT NOT NULL,
    strength    REAL DEFAULT 1.0,
    created_at  TEXT NOT NULL,      -- ISO 8601 UTC
    last_accessed_at TEXT NOT NULL  -- ISO 8601 UTC
);

CREATE TABLE datasets (
    name        TEXT PRIMARY KEY,
    created_at  TEXT NOT NULL,
    item_count  INTEGER DEFAULT 0
);
```

---

## Open-Source Infrastructure

### README sections
- Badges (CI status, PyPI version, license)
- One-paragraph description
- Quick install + 5-line quickstart
- API reference table
- Contributing section linking to CONTRIBUTING.md

### CONTRIBUTING.md
- How to fork and clone
- How to set up the dev environment (`pip install -e ".[dev]"`)
- How to run tests (`pytest`)
- How to open a PR
- Code style (ruff for linting)

### GitHub Actions CI (`ci.yml`)
- Triggers on: push to `main`, all PRs
- Steps: checkout → install deps → ruff lint → pytest

---

## Pre-Created GitHub Issues (for contributors)

| # | Title | Label |
|---|---|---|
| 1 | Add a REST API with FastAPI | `enhancement`, `good first issue` |
| 2 | Add a CLI (`engram remember/recall/forget/prune`) | `enhancement`, `good first issue` |
| 3 | Add file ingestion support (.txt, .pdf) | `enhancement`, `good first issue` |
| 4 | Add an MCP server for Claude/Cursor integration | `enhancement` |
| 5 | Add `list_datasets()` function | `enhancement`, `good first issue` |
| 6 | Improve test coverage | `testing`, `good first issue` |
| 7 | Add a TypeScript/JavaScript client SDK | `enhancement` |
| 8 | Make decay rate configurable per-dataset (not just global) | `enhancement`, `good first issue` |

---

## Out of Scope (v1)

- Web UI
- Multi-user / auth
- Cloud hosting
- Streaming recall
- LLM-based entity extraction (spaCy only for now)
- Spaced repetition scheduling (future: could schedule when to re-surface fading memories)

---

## Versioning & Release

- Tag `v0.1.0` on GitHub after the initial working implementation
- Use semantic versioning going forward
- GitHub Release notes should describe what's included and what's planned
