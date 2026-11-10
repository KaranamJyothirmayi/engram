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
