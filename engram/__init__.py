from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path

from .decay import current_strength, reinforce
from .extractor import extract
from .graph import MemoryGraph
from .meta import MetaStore
from .vector import VectorIndex

# Evaluated once at import time; set ENGRAM_HOME before importing engram.
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
        """Add new content to a dataset and refresh the whole dataset.

        Calling improve signals that the dataset is being actively curated,
        so every memory in it is reset to full strength (1.0) — not just the
        newly added text. This deliberately resets Ebbinghaus decay for the
        dataset. Use recall (which only reinforces what it returns) if you
        want decay to remain in effect.
        """
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

    def list_memories(
        self,
        dataset: str,
        min_strength: float | None = None,
        max_strength: float | None = None,
    ) -> list[dict]:
        rows = self._meta.get_all_in_dataset(dataset)
        results = []
        for row in rows:
            strength = current_strength(
                row["strength"],
                datetime.fromisoformat(row["last_accessed_at"]),
            )
            if min_strength is not None and strength < min_strength:
                continue
            if max_strength is not None and strength > max_strength:
                continue
            results.append({
                "id": row["id"],
                "text": row["text"],
                "strength": strength,
                "dataset": row["dataset"],
                "last_accessed_at": row["last_accessed_at"],
            })
        return results


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

async def list_memories(
    dataset: str = "default",
    min_strength: float | None = None,
    max_strength: float | None = None,
) -> list[dict]:
    return _get_store().list_memories(dataset, min_strength, max_strength)

async def list_datasets() -> list[dict]:
    """Return dataset metadata, including each dataset's name and item count."""
    return _get_store()._meta.list_datasets()
