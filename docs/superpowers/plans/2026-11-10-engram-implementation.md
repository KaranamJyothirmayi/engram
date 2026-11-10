# engram Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build `engram`, an installable Python library for AI agent persistent memory featuring Ebbinghaus-inspired memory decay, NetworkX knowledge graph, and ChromaDB vector search.

**Architecture:** A public async API (`remember/recall/improve/prune/forget`) wraps a synchronous `_EngramStore` that coordinates four components — `MetaStore` (SQLite for per-memory metadata + strength values), `MemoryGraph` (NetworkX for entity relationships), `VectorIndex` (ChromaDB for semantic search), and a `DecayEngine` (Ebbinghaus exponential decay). Memory strength scores decay over time and are reinforced on recall.

**Tech Stack:** Python 3.10+, NetworkX ≥3.0, ChromaDB ≥0.4.15, spaCy ≥3.7 (optional), pytest, pytest-asyncio, ruff, GitHub Actions

---

## File Map

| File | Responsibility |
|------|---------------|
| `pyproject.toml` | Package metadata, dependencies, tool config |
| `LICENSE` | Apache 2.0 license text |
| `engram/__init__.py` | Public async API + `_EngramStore` orchestrator |
| `engram/decay.py` | Ebbinghaus strength calculation |
| `engram/meta.py` | SQLite store for memory metadata + strength |
| `engram/graph.py` | NetworkX knowledge graph |
| `engram/vector.py` | ChromaDB vector index wrapper |
| `engram/extractor.py` | Sentence splitting + spaCy entity extraction |
| `tests/test_decay.py` | Unit tests for DecayEngine |
| `tests/test_meta.py` | Unit tests for MetaStore |
| `tests/test_graph.py` | Unit tests for MemoryGraph |
| `tests/test_vector.py` | Unit tests for VectorIndex |
| `tests/test_extractor.py` | Unit tests for Extractor |
| `tests/test_api.py` | Integration tests for public API |
| `examples/quickstart.py` | Runnable demo script |
| `README.md` | Project documentation |
| `CONTRIBUTING.md` | Contributor guide |
| `.github/workflows/ci.yml` | GitHub Actions CI |
| `.github/ISSUE_TEMPLATE/bug_report.md` | Bug issue template |
| `.github/ISSUE_TEMPLATE/feature_request.md` | Feature request template |
| `.github/PULL_REQUEST_TEMPLATE.md` | PR template |

---

### Task 1: Project Scaffold

**Files:**
- Create: `pyproject.toml`
- Create: `LICENSE`
- Create: `.gitignore`
- Create: `engram/__init__.py` (empty stubs)
- Create: `tests/__init__.py`

- [ ] **Step 1: Create pyproject.toml**

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "engram"
version = "0.1.0"
description = "Persistent memory for AI agents — graph-backed, vector-searchable, with biologically-inspired memory decay"
readme = "README.md"
license = {file = "LICENSE"}
requires-python = ">=3.10"
dependencies = [
    "chromadb>=0.4.15",
    "networkx>=3.0",
]

[project.optional-dependencies]
nlp = ["spacy>=3.7"]
dev = [
    "pytest>=7.4",
    "pytest-asyncio>=0.21",
    "ruff>=0.1",
    "spacy>=3.7",
]

[tool.ruff]
line-length = 88
target-version = "py310"

[tool.pytest.ini_options]
asyncio_mode = "auto"
```

- [ ] **Step 2: Download Apache 2.0 LICENSE**

```bash
curl -s https://www.apache.org/licenses/LICENSE-2.0.txt > LICENSE
```

- [ ] **Step 3: Create .gitignore**

```
__pycache__/
*.py[cod]
*.egg-info/
dist/
.venv/
venv/
.pytest_cache/
.ruff_cache/
*.pkl
.DS_Store
```

- [ ] **Step 4: Create empty package files**

```bash
mkdir -p engram tests
touch engram/__init__.py tests/__init__.py
```

- [ ] **Step 5: Install dependencies**

```bash
pip install -e ".[dev]"
```

Expected: `Successfully installed engram-0.1.0` plus all dependencies.

- [ ] **Step 6: Verify install**

```bash
python -c "import engram; print('ok')"
```

Expected: `ok`

- [ ] **Step 7: Commit**

```bash
git add pyproject.toml LICENSE .gitignore engram/ tests/
git commit -m "feat: initial project scaffold"
```

---

### Task 2: DecayEngine

**Files:**
- Create: `engram/decay.py`
- Create: `tests/test_decay.py`

- [ ] **Step 1: Write failing tests**

Create `tests/test_decay.py`:

```python
from datetime import datetime, timedelta, timezone
import pytest


def test_strength_at_zero_elapsed_is_unchanged():
    from engram.decay import current_strength
    now = datetime.now(timezone.utc)
    assert current_strength(1.0, now) == pytest.approx(1.0, abs=0.001)


def test_strength_decays_over_time():
    from engram.decay import current_strength
    past = datetime.now(timezone.utc) - timedelta(hours=200)
    result = current_strength(1.0, past)
    assert result < 0.37  # e^(-0.005 * 200) ≈ 0.368


def test_strength_scales_with_initial():
    from engram.decay import current_strength
    past = datetime.now(timezone.utc) - timedelta(hours=100)
    full = current_strength(1.0, past)
    half = current_strength(0.5, past)
    assert half == pytest.approx(full * 0.5, rel=0.01)


def test_reinforce_adds_boost():
    from engram.decay import reinforce
    assert reinforce(0.5) == pytest.approx(0.8, abs=0.001)


def test_reinforce_caps_at_one():
    from engram.decay import reinforce
    assert reinforce(0.9) == 1.0
    assert reinforce(1.0) == 1.0
```

- [ ] **Step 2: Run tests to confirm they fail**

```bash
pytest tests/test_decay.py -v
```

Expected: `ModuleNotFoundError: No module named 'engram.decay'`

- [ ] **Step 3: Implement decay.py**

Create `engram/decay.py`:

```python
import math
import os
from datetime import datetime, timezone

DECAY_RATE = float(os.environ.get("ENGRAM_DECAY_RATE", "0.005"))


def current_strength(initial_strength: float, last_accessed_at: datetime) -> float:
    hours = (datetime.now(timezone.utc) - last_accessed_at).total_seconds() / 3600
    return initial_strength * math.exp(-DECAY_RATE * hours)


def reinforce(current: float, boost: float = 0.3) -> float:
    return min(1.0, current + boost)
```

- [ ] **Step 4: Run tests to confirm they pass**

```bash
pytest tests/test_decay.py -v
```

Expected: `5 passed`

- [ ] **Step 5: Commit**

```bash
git add engram/decay.py tests/test_decay.py
git commit -m "feat: add DecayEngine with Ebbinghaus formula"
```

---

### Task 3: MetaStore

**Files:**
- Create: `engram/meta.py`
- Create: `tests/test_meta.py`

- [ ] **Step 1: Write failing tests**

Create `tests/test_meta.py`:

```python
import pytest
from engram.meta import MetaStore


@pytest.fixture
def store():
    return MetaStore()  # :memory: SQLite


def test_insert_returns_uuid(store):
    memory_id = store.insert("Hello world", "test")
    assert isinstance(memory_id, str) and len(memory_id) == 36


def test_get_by_ids_returns_row(store):
    memory_id = store.insert("Hello world", "test")
    rows = store.get_by_ids([memory_id])
    assert len(rows) == 1
    assert rows[0]["text"] == "Hello world"
    assert rows[0]["dataset"] == "test"
    assert rows[0]["strength"] == pytest.approx(1.0)


def test_update_accessed_changes_strength(store):
    memory_id = store.insert("Hello", "test")
    store.update_accessed(memory_id, 0.7)
    assert store.get_by_ids([memory_id])[0]["strength"] == pytest.approx(0.7)


def test_get_all_in_dataset(store):
    store.insert("A", "test")
    store.insert("B", "test")
    store.insert("C", "other")
    assert len(store.get_all_in_dataset("test")) == 2


def test_delete_by_ids(store):
    id1 = store.insert("A", "test")
    id2 = store.insert("B", "test")
    store.delete_by_ids([id1])
    assert store.get_by_ids([id1]) == []
    assert len(store.get_by_ids([id2])) == 1


def test_delete_dataset(store):
    store.insert("A", "test")
    store.insert("B", "test")
    store.delete_dataset("test")
    assert store.get_all_in_dataset("test") == []


def test_list_datasets(store):
    store.insert("A", "ds1")
    store.insert("B", "ds2")
    names = [d["name"] for d in store.list_datasets()]
    assert "ds1" in names and "ds2" in names
```

- [ ] **Step 2: Run tests to confirm they fail**

```bash
pytest tests/test_meta.py -v
```

Expected: `ModuleNotFoundError: No module named 'engram.meta'`

- [ ] **Step 3: Implement meta.py**

Create `engram/meta.py`:

```python
import sqlite3
import uuid
from datetime import datetime, timezone


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


class MetaStore:
    def __init__(self, db_path: str = ":memory:"):
        self._conn = sqlite3.connect(db_path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._init_schema()

    def _init_schema(self):
        self._conn.executescript("""
            CREATE TABLE IF NOT EXISTS memories (
                id               TEXT PRIMARY KEY,
                dataset          TEXT NOT NULL,
                text             TEXT NOT NULL,
                strength         REAL DEFAULT 1.0,
                created_at       TEXT NOT NULL,
                last_accessed_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS datasets (
                name       TEXT PRIMARY KEY,
                created_at TEXT NOT NULL,
                item_count INTEGER DEFAULT 0
            );
        """)
        self._conn.commit()

    def insert(self, text: str, dataset: str) -> str:
        memory_id = str(uuid.uuid4())
        now = _now()
        self._conn.execute(
            "INSERT INTO memories (id, dataset, text, strength, created_at, last_accessed_at)"
            " VALUES (?, ?, ?, 1.0, ?, ?)",
            (memory_id, dataset, text, now, now),
        )
        self._conn.execute(
            "INSERT OR IGNORE INTO datasets (name, created_at, item_count) VALUES (?, ?, 0)",
            (dataset, now),
        )
        self._conn.execute(
            "UPDATE datasets SET item_count = item_count + 1 WHERE name = ?",
            (dataset,),
        )
        self._conn.commit()
        return memory_id

    def get_by_ids(self, ids: list[str]) -> list[dict]:
        if not ids:
            return []
        placeholders = ",".join("?" * len(ids))
        rows = self._conn.execute(
            f"SELECT * FROM memories WHERE id IN ({placeholders})", ids
        ).fetchall()
        return [dict(r) for r in rows]

    def update_accessed(self, memory_id: str, new_strength: float):
        self._conn.execute(
            "UPDATE memories SET last_accessed_at = ?, strength = ? WHERE id = ?",
            (_now(), new_strength, memory_id),
        )
        self._conn.commit()

    def get_all_in_dataset(self, dataset: str) -> list[dict]:
        rows = self._conn.execute(
            "SELECT * FROM memories WHERE dataset = ?", (dataset,)
        ).fetchall()
        return [dict(r) for r in rows]

    def delete_by_ids(self, ids: list[str]):
        if not ids:
            return
        placeholders = ",".join("?" * len(ids))
        self._conn.execute(
            f"DELETE FROM memories WHERE id IN ({placeholders})", ids
        )
        self._conn.commit()

    def delete_dataset(self, dataset: str):
        self._conn.execute("DELETE FROM memories WHERE dataset = ?", (dataset,))
        self._conn.execute("DELETE FROM datasets WHERE name = ?", (dataset,))
        self._conn.commit()

    def list_datasets(self) -> list[dict]:
        return [dict(r) for r in self._conn.execute("SELECT * FROM datasets").fetchall()]
```

- [ ] **Step 4: Run tests to confirm they pass**

```bash
pytest tests/test_meta.py -v
```

Expected: `7 passed`

- [ ] **Step 5: Commit**

```bash
git add engram/meta.py tests/test_meta.py
git commit -m "feat: add MetaStore with SQLite persistence"
```

---

### Task 4: MemoryGraph

**Files:**
- Create: `engram/graph.py`
- Create: `tests/test_graph.py`

- [ ] **Step 1: Write failing tests**

Create `tests/test_graph.py`:

```python
import pytest
from engram.graph import MemoryGraph


@pytest.fixture
def graph():
    return MemoryGraph()  # no path = no disk persistence


def test_add_memory_node_exists(graph):
    graph.add_memory("mem-1", "test", ["Marie Curie", "Warsaw"])
    assert graph._g.has_node("mem-1")


def test_add_memory_creates_entity_nodes(graph):
    graph.add_memory("mem-1", "test", ["Marie Curie"])
    assert graph._g.has_node("entity:marie curie")


def test_add_memory_creates_edges(graph):
    graph.add_memory("mem-1", "test", ["Marie Curie"])
    assert graph._g.has_edge("mem-1", "entity:marie curie")


def test_get_related_returns_connected_memories(graph):
    graph.add_memory("mem-1", "test", ["Marie Curie"])
    graph.add_memory("mem-2", "test", ["Marie Curie"])
    assert "mem-2" in graph.get_related("mem-1")


def test_get_related_empty_for_unknown(graph):
    assert graph.get_related("nonexistent") == []


def test_remove_by_dataset(graph):
    graph.add_memory("mem-1", "test", [])
    graph.add_memory("mem-2", "other", [])
    graph.remove_by_dataset("test")
    assert not graph._g.has_node("mem-1")
    assert graph._g.has_node("mem-2")


def test_remove_by_ids(graph):
    graph.add_memory("mem-1", "test", [])
    graph.add_memory("mem-2", "test", [])
    graph.remove_by_ids(["mem-1"])
    assert not graph._g.has_node("mem-1")
    assert graph._g.has_node("mem-2")
```

- [ ] **Step 2: Run tests to confirm they fail**

```bash
pytest tests/test_graph.py -v
```

Expected: `ModuleNotFoundError: No module named 'engram.graph'`

- [ ] **Step 3: Implement graph.py**

Create `engram/graph.py`:

```python
import pickle
from pathlib import Path

import networkx as nx


class MemoryGraph:
    def __init__(self, graph_path: str | None = None):
        self._path = graph_path
        if graph_path and Path(graph_path).exists():
            with open(graph_path, "rb") as f:
                self._g: nx.DiGraph = pickle.load(f)
        else:
            self._g = nx.DiGraph()

    def add_memory(self, memory_id: str, dataset: str, entities: list[str]):
        self._g.add_node(memory_id, kind="memory", dataset=dataset)
        for entity in entities:
            entity_id = f"entity:{entity.lower()}"
            self._g.add_node(entity_id, kind="entity", text=entity)
            self._g.add_edge(memory_id, entity_id)
        self._save()

    def get_related(self, memory_id: str) -> list[str]:
        if memory_id not in self._g:
            return []
        related: set[str] = set()
        for entity_id in self._g.successors(memory_id):
            for pred in self._g.predecessors(entity_id):
                if pred != memory_id and self._g.nodes[pred].get("kind") == "memory":
                    related.add(pred)
        return list(related)

    def remove_by_dataset(self, dataset: str):
        to_remove = [
            n for n, d in self._g.nodes(data=True) if d.get("dataset") == dataset
        ]
        self._g.remove_nodes_from(to_remove)
        self._save()

    def remove_by_ids(self, ids: list[str]):
        self._g.remove_nodes_from([i for i in ids if i in self._g])
        self._save()

    def _save(self):
        if self._path:
            with open(self._path, "wb") as f:
                pickle.dump(self._g, f)
```

- [ ] **Step 4: Run tests to confirm they pass**

```bash
pytest tests/test_graph.py -v
```

Expected: `7 passed`

- [ ] **Step 5: Commit**

```bash
git add engram/graph.py tests/test_graph.py
git commit -m "feat: add MemoryGraph with NetworkX"
```

---

### Task 5: VectorIndex

**Files:**
- Create: `engram/vector.py`
- Create: `tests/test_vector.py`

- [ ] **Step 1: Write failing tests**

Create `tests/test_vector.py`:

```python
import pytest
from engram.vector import VectorIndex


@pytest.fixture
def index():
    return VectorIndex()  # ephemeral ChromaDB


def test_upsert_and_search(index):
    index.upsert("mem-1", "Marie Curie was born in Warsaw", "science")
    results = index.search("Who is Marie Curie?", datasets=["science"])
    assert len(results) >= 1
    assert results[0]["id"] == "mem-1"


def test_search_filters_by_dataset(index):
    index.upsert("mem-1", "Marie Curie was born in Warsaw", "science")
    index.upsert("mem-2", "The Eiffel Tower is in Paris", "geography")
    results = index.search("Marie Curie", datasets=["science"])
    ids = [r["id"] for r in results]
    assert "mem-1" in ids
    assert "mem-2" not in ids


def test_search_returns_score_between_0_and_1(index):
    index.upsert("mem-1", "The sky is blue", "test")
    results = index.search("sky color", datasets=["test"])
    assert 0.0 <= results[0]["score"] <= 1.0


def test_search_empty_collection_returns_empty(index):
    assert index.search("anything", datasets=["test"]) == []


def test_delete_by_dataset(index):
    index.upsert("mem-1", "Hello", "test")
    index.delete_by_dataset("test")
    assert index.search("Hello", datasets=["test"]) == []


def test_delete_by_ids(index):
    index.upsert("mem-1", "Hello", "test")
    index.upsert("mem-2", "World", "test")
    index.delete_by_ids(["mem-1"])
    ids = [r["id"] for r in index.search("Hello", datasets=["test"])]
    assert "mem-1" not in ids
```

- [ ] **Step 2: Run tests to confirm they fail**

```bash
pytest tests/test_vector.py -v
```

Expected: `ModuleNotFoundError: No module named 'engram.vector'`

- [ ] **Step 3: Implement vector.py**

Create `engram/vector.py`:

```python
import chromadb


class VectorIndex:
    def __init__(self, persist_directory: str | None = None):
        if persist_directory:
            self._client = chromadb.PersistentClient(path=persist_directory)
        else:
            self._client = chromadb.EphemeralClient()
        self._collection = self._client.get_or_create_collection(
            "engram",
            metadata={"hnsw:space": "cosine"},
        )

    def upsert(self, memory_id: str, text: str, dataset: str):
        self._collection.upsert(
            ids=[memory_id],
            documents=[text],
            metadatas=[{"dataset": dataset}],
        )

    def search(self, query: str, datasets: list[str] | None, top_k: int = 5) -> list[dict]:
        count = self._collection.count()
        if count == 0:
            return []
        where = {"dataset": {"$in": datasets}} if datasets else None
        results = self._collection.query(
            query_texts=[query],
            n_results=min(top_k, count),
            where=where,
        )
        return [
            {"id": id_, "text": doc, "score": max(0.0, 1.0 - dist)}
            for id_, doc, dist in zip(
                results["ids"][0],
                results["documents"][0],
                results["distances"][0],
            )
        ]

    def delete_by_dataset(self, dataset: str):
        results = self._collection.get(where={"dataset": dataset})
        if results["ids"]:
            self._collection.delete(ids=results["ids"])

    def delete_by_ids(self, ids: list[str]):
        if ids:
            self._collection.delete(ids=ids)
```

- [ ] **Step 4: Run tests to confirm they pass**

```bash
pytest tests/test_vector.py -v
```

Expected: `6 passed`

Note: the first run downloads ChromaDB's default embedding model (~50 MB). Subsequent runs are fast.

- [ ] **Step 5: Commit**

```bash
git add engram/vector.py tests/test_vector.py
git commit -m "feat: add VectorIndex with ChromaDB cosine similarity"
```

---

### Task 6: Extractor

**Files:**
- Create: `engram/extractor.py`
- Create: `tests/test_extractor.py`

- [ ] **Step 1: Write failing tests**

Create `tests/test_extractor.py`:

```python
from engram.extractor import extract, split_sentences


def test_split_sentences_basic():
    result = split_sentences("Hello world. This is a test.")
    assert len(result) == 2
    assert result[0] == "Hello world."
    assert result[1] == "This is a test."


def test_split_sentences_single():
    assert split_sentences("Just one sentence") == ["Just one sentence"]


def test_split_empty_string():
    assert split_sentences("") == []


def test_extract_returns_sentences_and_entities():
    sentences, entities = extract("Marie Curie was born in Warsaw.")
    assert "Marie Curie was born in Warsaw." in sentences
    assert isinstance(entities, list)


def test_extract_multiple_sentences():
    sentences, _ = extract("The cat sat. The dog ran.")
    assert len(sentences) == 2


def test_extract_empty_string():
    sentences, entities = extract("")
    assert sentences == [] and entities == []
```

- [ ] **Step 2: Run tests to confirm they fail**

```bash
pytest tests/test_extractor.py -v
```

Expected: `ModuleNotFoundError: No module named 'engram.extractor'`

- [ ] **Step 3: Implement extractor.py**

Create `engram/extractor.py`:

```python
import re


def split_sentences(text: str) -> list[str]:
    if not text.strip():
        return []
    parts = re.split(r'(?<=[.!?])\s+', text.strip())
    return [p.strip() for p in parts if p.strip()]


def extract(text: str) -> tuple[list[str], list[str]]:
    sentences = split_sentences(text)
    if not sentences:
        return [], []
    try:
        import spacy
        try:
            nlp = spacy.load("en_core_web_sm")
        except OSError:
            return sentences, []
        entities: list[str] = []
        for sent in sentences:
            doc = nlp(sent)
            entities.extend([ent.text for ent in doc.ents])
        return sentences, list(set(entities))
    except ImportError:
        return sentences, []
```

- [ ] **Step 4: Run tests to confirm they pass**

```bash
pytest tests/test_extractor.py -v
```

Expected: `6 passed`

- [ ] **Step 5: Commit**

```bash
git add engram/extractor.py tests/test_extractor.py
git commit -m "feat: add Extractor with sentence splitting and optional spaCy NER"
```

---

### Task 7: Public API + EngramStore

**Files:**
- Modify: `engram/__init__.py`
- Create: `tests/test_api.py`

- [ ] **Step 1: Write failing integration tests**

Create `tests/test_api.py`:

```python
from datetime import datetime, timedelta, timezone
import pytest
import engram


@pytest.fixture(autouse=True)
def fresh_store(tmp_path):
    engram.configure(tmp_path)
    yield
    engram.reset()


async def test_remember_and_recall():
    await engram.remember("Marie Curie was born in Warsaw.", dataset="science")
    results = await engram.recall("Where was Marie Curie born?", datasets=["science"])
    assert len(results) >= 1
    assert any("Marie Curie" in r["text"] for r in results)


async def test_recall_result_has_required_fields():
    await engram.remember("The sky is blue.", dataset="test")
    results = await engram.recall("sky", datasets=["test"])
    r = results[0]
    assert all(k in r for k in ("text", "score", "strength", "dataset", "related"))


async def test_recall_reinforces_strength():
    await engram.remember("The sky is blue.", dataset="test")
    store = engram._get_store()
    rows = store._meta.get_all_in_dataset("test")
    store._meta.update_accessed(rows[0]["id"], 0.5)
    results = await engram.recall("sky", datasets=["test"])
    assert results[0]["strength"] > 0.5


async def test_forget_removes_dataset():
    await engram.remember("Some fact.", dataset="temp")
    await engram.forget("temp")
    assert await engram.recall("Some fact", datasets=["temp"]) == []


async def test_prune_removes_weak_memories():
    await engram.remember("Old fact.", dataset="test")
    store = engram._get_store()
    far_past = (datetime.now(timezone.utc) - timedelta(hours=10000)).isoformat()
    store._meta._conn.execute(
        "UPDATE memories SET last_accessed_at = ?, strength = 1.0 WHERE dataset = ?",
        (far_past, "test"),
    )
    store._meta._conn.commit()
    removed = await engram.prune("test", threshold=0.5)
    assert removed >= 1


async def test_improve_adds_content():
    await engram.remember("Marie Curie.", dataset="science")
    await engram.improve("Marie Curie won two Nobel Prizes.", dataset="science")
    results = await engram.recall("Nobel Prize", datasets=["science"])
    assert any("Nobel" in r["text"] for r in results)


async def test_recall_empty_store_returns_empty():
    assert await engram.recall("anything", datasets=["nonexistent"]) == []
```

- [ ] **Step 2: Run tests to confirm they fail**

```bash
pytest tests/test_api.py -v
```

Expected: errors since `__init__.py` is empty.

- [ ] **Step 3: Implement engram/__init__.py**

```python
from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path

from .decay import current_strength, reinforce
from .extractor import extract
from .graph import MemoryGraph
from .meta import MetaStore
from .vector import VectorIndex

_ENGRAM_HOME = Path(os.environ.get("ENGRAM_HOME", Path.home() / ".engram"))


class _EngramStore:
    def __init__(self, home: Path | None = None):
        if home:
            home.mkdir(parents=True, exist_ok=True)
            meta_path = str(home / "meta.db")
            graph_path = str(home / "graph.pkl")
            vector_path = str(home / "chroma")
        else:
            meta_path = ":memory:"
            graph_path = None
            vector_path = None
        self._meta = MetaStore(meta_path)
        self._graph = MemoryGraph(graph_path)
        self._vector = VectorIndex(vector_path)

    def remember(self, text: str, dataset: str) -> None:
        sentences, entities = extract(text)
        for sentence in sentences:
            memory_id = self._meta.insert(sentence, dataset)
            self._vector.upsert(memory_id, sentence, dataset)
            self._graph.add_memory(memory_id, dataset, entities)

    def recall(self, query: str, datasets: list[str] | None = None) -> list[dict]:
        hits = self._vector.search(query, datasets)
        results = []
        for hit in hits:
            rows = self._meta.get_by_ids([hit["id"]])
            if not rows:
                continue
            row = rows[0]
            last = datetime.fromisoformat(row["last_accessed_at"])
            strength = current_strength(row["strength"], last)
            related_ids = self._graph.get_related(hit["id"])
            related_texts = [
                r["text"] for r in self._meta.get_by_ids(related_ids)
            ] if related_ids else []
            new_strength = reinforce(strength)
            self._meta.update_accessed(hit["id"], new_strength)
            results.append({
                "text": row["text"],
                "score": round(hit["score"] * strength, 4),
                "strength": round(new_strength, 4),
                "dataset": row["dataset"],
                "related": related_texts,
            })
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def improve(self, text: str, dataset: str) -> None:
        self.remember(text, dataset)
        for row in self._meta.get_all_in_dataset(dataset):
            self._meta.update_accessed(row["id"], 1.0)

    def prune(self, dataset: str, threshold: float = 0.2) -> int:
        rows = self._meta.get_all_in_dataset(dataset)
        weak_ids = [
            row["id"]
            for row in rows
            if current_strength(
                row["strength"],
                datetime.fromisoformat(row["last_accessed_at"]),
            ) < threshold
        ]
        if weak_ids:
            self._meta.delete_by_ids(weak_ids)
            self._vector.delete_by_ids(weak_ids)
            self._graph.remove_by_ids(weak_ids)
        return len(weak_ids)

    def forget(self, dataset: str) -> None:
        self._meta.delete_dataset(dataset)
        self._vector.delete_by_dataset(dataset)
        self._graph.remove_by_dataset(dataset)


_store: _EngramStore | None = None


def _get_store() -> _EngramStore:
    global _store
    if _store is None:
        _store = _EngramStore(_ENGRAM_HOME)
    return _store


def configure(home: str | Path | None = None) -> None:
    global _store
    _store = _EngramStore(Path(home) if home else None)


def reset() -> None:
    global _store
    _store = None


async def remember(text: str, dataset: str = "default") -> None:
    _get_store().remember(text, dataset)


async def recall(query: str, datasets: list[str] | None = None) -> list[dict]:
    return _get_store().recall(query, datasets)


async def improve(text: str, dataset: str = "default") -> None:
    _get_store().improve(text, dataset)


async def prune(dataset: str = "default", threshold: float = 0.2) -> int:
    return _get_store().prune(dataset, threshold)


async def forget(dataset: str) -> None:
    _get_store().forget(dataset)
```

- [ ] **Step 4: Run all tests**

```bash
pytest -v
```

Expected: all tests pass across all files.

- [ ] **Step 5: Run linter**

```bash
ruff check engram/ tests/
```

Expected: no errors. Fix any reported before continuing.

- [ ] **Step 6: Commit**

```bash
git add engram/__init__.py tests/test_api.py
git commit -m "feat: wire up EngramStore and public async API"
```

---

### Task 8: Quickstart Example

**Files:**
- Create: `examples/quickstart.py`

- [ ] **Step 1: Create examples/quickstart.py**

```python
"""Run with: python examples/quickstart.py"""
import asyncio
from pathlib import Path
import engram

engram.configure(Path.home() / ".engram-quickstart")


async def main():
    print("Storing memories...")
    await engram.remember(
        "Marie Curie was born in Warsaw, Poland in 1867.",
        dataset="science",
    )
    await engram.remember(
        "Marie Curie won the Nobel Prize in Physics in 1903 and Chemistry in 1911.",
        dataset="science",
    )
    await engram.remember(
        "Warsaw is the capital and largest city of Poland.",
        dataset="geography",
    )

    print("\nRecalling about Marie Curie...")
    results = await engram.recall(
        "Tell me about Marie Curie's achievements",
        datasets=["science"],
    )
    for r in results:
        print(f"  [{r['strength']:.2f}] {r['text']}")
        if r["related"]:
            print(f"    Related: {r['related']}")

    print("\nImproving memory with new info...")
    await engram.improve(
        "Marie Curie was the first woman to win a Nobel Prize.",
        dataset="science",
    )

    print("\nPruning faded memories (threshold=0.01)...")
    removed = await engram.prune(dataset="science", threshold=0.01)
    print(f"  Removed {removed} weak memories")

    print("\nForgetting geography dataset...")
    await engram.forget(dataset="geography")
    results = await engram.recall("Warsaw", datasets=["geography"])
    print(f"  Results after forget: {len(results)} (expected 0)")


asyncio.run(main())
```

- [ ] **Step 2: Run the quickstart to verify end-to-end**

```bash
python examples/quickstart.py
```

Expected: prints memory results without errors.

- [ ] **Step 3: Commit**

```bash
git add examples/
git commit -m "docs: add quickstart example"
```

---

### Task 9: README

**Files:**
- Create: `README.md`

- [ ] **Step 1: Create README.md**

```markdown
# engram

> Persistent memory for AI agents — graph-backed, vector-searchable, with biologically-inspired memory decay.

[![CI](https://github.com/YOUR_USERNAME/engram/actions/workflows/ci.yml/badge.svg)](https://github.com/YOUR_USERNAME/engram/actions/workflows/ci.yml)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://python.org)

## What is engram?

Most AI memory tools store facts forever with equal weight. **engram** is different: memory fades over time unless reinforced — modelled on the [Ebbinghaus forgetting curve](https://en.wikipedia.org/wiki/Forgetting_curve).

Every stored memory has a **strength** that decays exponentially with elapsed time and gets boosted every time it's recalled. Old, unused memories become weak candidates for pruning. Frequently-accessed memories stay strong.

## Install

```bash
pip install engram
```

For named-entity extraction (improves relationship linking):

```bash
pip install "engram[nlp]"
python -m spacy download en_core_web_sm
```

## Quick Start

```python
import asyncio
import engram

async def main():
    await engram.remember("Marie Curie was born in Warsaw.", dataset="science")

    results = await engram.recall(
        "Where was Marie Curie born?",
        datasets=["science"],
    )
    for r in results:
        print(f"[{r['strength']:.2f}] {r['text']}")

    # Remove memories that have faded below 20% strength
    removed = await engram.prune(dataset="science", threshold=0.2)

asyncio.run(main())
```

## API

| Function | Description |
|---|---|
| `remember(text, dataset)` | Store text as memory (strength = 1.0) |
| `recall(query, datasets)` | Search memories; reinforces what's returned |
| `improve(text, dataset)` | Add content and reset all dataset strengths to 1.0 |
| `prune(dataset, threshold)` | Remove memories below strength threshold |
| `forget(dataset)` | Delete all memories in a dataset |

## How Memory Decay Works

```
strength(t) = S₀ × e^(−k × hours_elapsed)
```

- Default decay rate `k = 0.005` (~50% strength after ~6 days of no access)
- `recall()` reinforces retrieved memories (+0.3, capped at 1.0)
- Configure: `ENGRAM_DECAY_RATE=0.002 python your_script.py`

## Architecture

```
engram API (remember / recall / improve / prune / forget)
    ├── MemoryGraph (NetworkX)    ← entity relationship graph
    ├── VectorIndex (ChromaDB)   ← semantic similarity search
    ├── DecayEngine              ← Ebbinghaus strength scoring
    └── MetaStore (SQLite)       ← metadata + per-memory strength
```

Data stored in `~/.engram/` by default. Override: `ENGRAM_HOME=/path/to/dir`

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Good first issues are labeled
[`good first issue`](https://github.com/YOUR_USERNAME/engram/issues?q=label%3A%22good+first+issue%22).

## License

Apache 2.0 — see [LICENSE](LICENSE).
```

- [ ] **Step 2: Replace both `YOUR_USERNAME` placeholders with your real GitHub username**

- [ ] **Step 3: Commit**

```bash
git add README.md
git commit -m "docs: add README with quickstart, API reference, and architecture"
```

---

### Task 10: CONTRIBUTING.md

**Files:**
- Create: `CONTRIBUTING.md`

- [ ] **Step 1: Create CONTRIBUTING.md**

```markdown
# Contributing to engram

Thank you for your interest! Here's everything you need to get started.

## Setup

```bash
git clone https://github.com/YOUR_USERNAME/engram.git
cd engram
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
pytest -v                      # all tests should pass
```

Optional spaCy support:

```bash
pip install ".[nlp]"
python -m spacy download en_core_web_sm
```

## Code Style

```bash
ruff check engram/ tests/    # lint
ruff format engram/ tests/   # auto-format
```

CI fails on ruff errors.

## Making a Contribution

1. Pick an issue (look for `good first issue` labels)
2. Create a branch: `git checkout -b feat/your-feature`
3. Write tests first, then implementation (TDD)
4. Run `pytest -v` and `ruff check` — both must pass
5. Open a PR against `main` and reference the issue (`Closes #N`)

## PR Guidelines

- One feature or fix per PR
- Tests required for all new code
- Update README if public API changes

## Questions

Open a [GitHub Discussion](https://github.com/YOUR_USERNAME/engram/discussions) or comment on the issue.
```

- [ ] **Step 2: Replace `YOUR_USERNAME` with your real GitHub username**

- [ ] **Step 3: Commit**

```bash
git add CONTRIBUTING.md
git commit -m "docs: add CONTRIBUTING guide"
```

---

### Task 11: GitHub Actions CI

**Files:**
- Create: `.github/workflows/ci.yml`

- [ ] **Step 1: Create the workflow**

```bash
mkdir -p .github/workflows
```

Create `.github/workflows/ci.yml`:

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.10", "3.11", "3.12"]

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}

      - name: Install dependencies
        run: pip install -e ".[dev]"

      - name: Lint
        run: ruff check engram/ tests/

      - name: Test
        run: pytest -v
```

- [ ] **Step 2: Commit**

```bash
git add .github/workflows/ci.yml
git commit -m "ci: add GitHub Actions CI for lint and tests on Python 3.10–3.12"
```

---

### Task 12: Issue Templates + PR Template

**Files:**
- Create: `.github/ISSUE_TEMPLATE/bug_report.md`
- Create: `.github/ISSUE_TEMPLATE/feature_request.md`
- Create: `.github/PULL_REQUEST_TEMPLATE.md`

- [ ] **Step 1: Create bug report template**

Create `.github/ISSUE_TEMPLATE/bug_report.md`:

```markdown
---
name: Bug report
about: Something is broken
labels: bug
---

## Describe the bug

A clear description of what's wrong.

## Steps to reproduce

```python
import engram
# minimal code to reproduce
```

## Expected behaviour

What should happen.

## Actual behaviour

What happens instead (include the full traceback if applicable).

## Environment

- Python version:
- engram version:
- OS:
```

- [ ] **Step 2: Create feature request template**

Create `.github/ISSUE_TEMPLATE/feature_request.md`:

```markdown
---
name: Feature request
about: Suggest a new feature or improvement
labels: enhancement
---

## What problem does this solve?

Describe the gap this feature addresses.

## Proposed solution

What you'd like to see added or changed.

## Alternatives considered

Any other approaches you thought about.
```

- [ ] **Step 3: Create PR template**

Create `.github/PULL_REQUEST_TEMPLATE.md`:

```markdown
## What does this PR do?

Brief description of the change.

## Related issue

Closes #

## Checklist

- [ ] Tests added for all new code
- [ ] `pytest -v` passes
- [ ] `ruff check engram/ tests/` passes
- [ ] README updated if public API changed
```

- [ ] **Step 4: Commit**

```bash
git add .github/
git commit -m "docs: add issue templates and PR template"
```

---

### Task 13: Push to GitHub, Create Issues, Tag v0.1.0

- [ ] **Step 1: Create a public GitHub repo named `engram`**

Go to github.com → New repository → Name: `engram` → Public → **do not** initialize with README.

- [ ] **Step 2: Push**

```bash
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/engram.git
git push -u origin main
```

- [ ] **Step 3: Create 8 GitHub issues**

Go to Issues → New issue for each row:

| Title | Labels | Description |
|---|---|---|
| Add a REST API with FastAPI | `enhancement`, `good first issue` | Expose `remember`, `recall`, `improve`, `prune`, `forget` over HTTP. Entry point: `uvicorn engram.server:app`. |
| Add a CLI (engram remember/recall/forget/prune) | `enhancement`, `good first issue` | Add CLI using `argparse` so users can run `engram remember "..."` from the terminal. |
| Add file ingestion (.txt, .pdf) | `enhancement`, `good first issue` | Add `ingest(path, dataset)` that reads a file and calls `remember()`. Use `pypdf` for PDFs. |
| Add an MCP server for Claude/Cursor | `enhancement` | Expose engram as an MCP server so it works as a memory tool in Claude, Cursor, and Cline. |
| Add list_datasets() function | `enhancement`, `good first issue` | `engram.list_datasets()` returns all dataset names and item counts from MetaStore. |
| Improve test coverage | `testing`, `good first issue` | Add edge case tests: empty datasets, multi-sentence remember, recall with no matches, prune with all memories strong. |
| Add a TypeScript/JS client SDK | `enhancement` | TypeScript client wrapping the REST API (depends on issue #1). |
| Make decay rate configurable per-dataset | `enhancement`, `good first issue` | Allow passing `decay_rate` to `remember()`, stored per-dataset in MetaStore. |

- [ ] **Step 4: Tag v0.1.0**

```bash
git tag v0.1.0
git push origin v0.1.0
```

- [ ] **Step 5: Create GitHub Release**

Go to Releases → Draft a new release → Tag: `v0.1.0` → Title: `v0.1.0 — Initial release`

Body:
```
## What's included

- `remember(text, dataset)` — store memory at full strength (1.0)
- `recall(query, datasets)` — semantic search ranked by relevance × current strength; reinforces retrieved memories
- `improve(text, dataset)` — add content and reset dataset strength to 1.0
- `prune(dataset, threshold)` — remove memories that have decayed below threshold
- `forget(dataset)` — delete a dataset entirely

## How memory decay works

Each memory has a strength that decays as `S₀ × e^(−k × t)` (Ebbinghaus forgetting curve).
Default `k = 0.005` (~50% strength after 6 days). Configure via `ENGRAM_DECAY_RATE` env var.

## What's next

See open issues: REST API, CLI, file ingestion, MCP server, per-dataset decay rates.
```

- [ ] **Step 6: Verify CI passes**

GitHub → Actions tab → confirm the CI workflow passes on `main` across all three Python versions.

- [ ] **Step 7: Final local check**

```bash
pytest -v && ruff check engram/ tests/
```

Expected: all tests pass, no lint errors.
