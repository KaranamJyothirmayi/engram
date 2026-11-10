# engram — Design Spec

**Date:** 2026-11-10  
**Status:** Approved

---

## Project Identity

| | |
|---|---|
| **Name** | `engram` |
| **Tagline** | Persistent memory for AI agents — graph-backed, vector-searchable, local-first |
| **License** | Apache 2.0 |
| **Python** | 3.10+ |
| **Install** | `pip install engram` |

---

## Goals

- Build a functional, installable Python library that gives AI agents persistent memory
- Demonstrate open-source project structure: README, CONTRIBUTING.md, CI, issue templates, PR templates
- Pre-create GitHub issues sized for contributor-level work (friends/colleagues can contribute)

---

## Architecture

```
User/Agent
    │
    ▼
engram API (remember / recall / improve / forget)
    │
    ├── MemoryGraph (NetworkX)      ← stores entities + relationships
    ├── VectorIndex (ChromaDB)      ← semantic search over memory
    └── MetaStore (SQLite)          ← dataset registry, timestamps, config
```

### Components

**MemoryGraph (NetworkX)**  
Stores extracted entities as nodes and their relationships as directed edges. Each node carries a `content` attribute (the raw sentence it came from) and a `dataset` tag for scoped deletion.

**VectorIndex (ChromaDB)**  
Stores text chunks as embeddings using ChromaDB's default embedding model (sentence-transformers). Each embedding is tagged with `dataset` metadata for filtered recall.

**MetaStore (SQLite via sqlite3)**  
A lightweight registry tracking datasets (name, created_at, item count). Used by `forget()` to enumerate what to delete and by `list_datasets()` (future contributor issue).

---

## Core API

```python
import engram

# Store content
await engram.remember("Marie Curie was born in Warsaw.", dataset="science")

# Retrieve context
results = await engram.recall("Where was Marie Curie born?", datasets=["science"])

# Correct or enrich existing memory
await engram.improve("Marie Curie won two Nobel Prizes.", dataset="science")

# Delete a dataset
await engram.forget(dataset="science")
```

### Function Contracts

| Function | Input | Output | Side Effects |
|---|---|---|---|
| `remember(text, dataset)` | str, str | None | Adds graph nodes/edges + vector embeddings |
| `recall(query, datasets)` | str, list[str] | list[dict] | None |
| `improve(text, dataset)` | str, str | None | Appends to existing dataset |
| `forget(dataset)` | str | None | Deletes graph nodes, vectors, metadata |

### `recall` result shape

```python
[
  {
    "text": "Marie Curie was born in Warsaw.",
    "score": 0.91,
    "dataset": "science",
    "related": ["Warsaw is the capital of Poland."]  # graph neighbors
  }
]
```

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
5. Update MetaStore (increment item count or insert dataset row)

### `recall(query, datasets)`
1. Query ChromaDB for top-5 matches filtered by `datasets`
2. For each match, look up its node in MemoryGraph and collect 1-hop neighbors
3. Return ranked list of `{text, score, dataset, related}`

### `improve(text, dataset)`
Calls `remember(text, dataset)` — the dataset already exists, so this just appends.

### `forget(dataset)`
1. Remove all MemoryGraph nodes tagged with `dataset`
2. Delete ChromaDB collection entries where `dataset` metadata matches
3. Delete dataset row from MetaStore

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
│   ├── __init__.py          ← public API (remember, recall, improve, forget)
│   ├── graph.py             ← MemoryGraph (NetworkX)
│   ├── vector.py            ← VectorIndex (ChromaDB)
│   ├── meta.py              ← MetaStore (SQLite)
│   └── extractor.py         ← entity extraction (spaCy)
├── tests/
│   ├── test_remember.py
│   ├── test_recall.py
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
| 2 | Add a CLI (`engram remember/recall/forget`) | `enhancement`, `good first issue` |
| 3 | Add file ingestion support (.txt, .pdf) | `enhancement`, `good first issue` |
| 4 | Add an MCP server for Claude/Cursor integration | `enhancement` |
| 5 | Add `list_datasets()` function | `enhancement`, `good first issue` |
| 6 | Improve test coverage | `testing`, `good first issue` |
| 7 | Add a TypeScript/JavaScript client SDK | `enhancement` |

---

## Out of Scope (v1)

- Web UI
- Multi-user / auth
- Cloud hosting
- Streaming recall
- LLM-based entity extraction (spaCy only for now)
