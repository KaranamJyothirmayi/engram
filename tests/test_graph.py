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
