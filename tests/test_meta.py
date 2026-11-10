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
