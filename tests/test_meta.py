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


def test_decay_rate_defaults_to_none(store):
    store.insert("A", "ds1")
    assert store.get_decay_rate("ds1") is None
    assert store.get_decay_rate("missing") is None


def test_set_decay_rate_per_dataset(store):
    store.insert("A", "fast")
    store.insert("B", "slow")
    store.set_decay_rate("fast", 0.05)
    store.set_decay_rate("slow", 0.001)
    assert store.get_decay_rate("fast") == pytest.approx(0.05)
    assert store.get_decay_rate("slow") == pytest.approx(0.001)
    store.set_decay_rate("fast", None)
    assert store.get_decay_rate("fast") is None


def test_set_decay_rate_before_insert_keeps_item_count(store):
    store.set_decay_rate("new", 0.01)
    store.insert("A", "new")
    ds = {d["name"]: d for d in store.list_datasets()}["new"]
    assert ds["item_count"] == 1
    assert ds["decay_rate"] == pytest.approx(0.01)


def test_old_database_gets_decay_rate_column(tmp_path):
    import sqlite3

    db = tmp_path / "old.db"
    conn = sqlite3.connect(db)
    conn.executescript("""
        CREATE TABLE datasets (
            name TEXT PRIMARY KEY, created_at TEXT NOT NULL,
            item_count INTEGER DEFAULT 0
        );
        INSERT INTO datasets VALUES ('legacy', '2026-01-01T00:00:00+00:00', 3);
    """)
    conn.close()
    store = MetaStore(str(db))
    assert store.get_decay_rate("legacy") is None
    store.set_decay_rate("legacy", 0.02)
    assert store.get_decay_rate("legacy") == pytest.approx(0.02)
