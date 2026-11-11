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
    assert results
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


async def test_improve_resets_decayed_siblings_to_full_strength():
    await engram.remember("An older fact.", dataset="science")
    store = engram._get_store()
    old_id = store._meta.get_all_in_dataset("science")[0]["id"]
    store._meta.update_accessed(old_id, 0.1)  # simulate a decayed memory
    await engram.improve("A newly curated fact.", dataset="science")
    refreshed = store._meta.get_by_ids([old_id])[0]
    assert refreshed["strength"] == pytest.approx(1.0)


async def test_recall_with_no_datasets_searches_all():
    await engram.remember("Marie Curie was a physicist.", dataset="science")
    await engram.remember("Paris is in France.", dataset="geography")
    results = await engram.recall("Marie Curie")  # datasets defaults to None
    assert any("Marie Curie" in r["text"] for r in results)


async def test_recall_isolates_by_dataset():
    await engram.remember("Marie Curie was a physicist.", dataset="science")
    await engram.remember("Paris is in France.", dataset="geography")
    results = await engram.recall("Marie Curie", datasets=["geography"])
    assert all(r["dataset"] == "geography" for r in results)


def _age_dataset(dataset: str, hours: int):
    store = engram._get_store()
    past = (datetime.now(timezone.utc) - timedelta(hours=hours)).isoformat()
    store._meta._conn.execute(
        "UPDATE memories SET last_accessed_at = ?, strength = 1.0 WHERE dataset = ?",
        (past, dataset),
    )
    store._meta._conn.commit()


async def test_prune_uses_per_dataset_decay_rate():
    await engram.remember("Fast fading fact.", dataset="fast", decay_rate=0.05)
    await engram.remember("Slow fading fact.", dataset="slow", decay_rate=0.0001)
    _age_dataset("fast", 100)  # e^(-0.05 * 100) ≈ 0.007
    _age_dataset("slow", 100)  # e^(-0.0001 * 100) ≈ 0.99
    assert await engram.prune("fast", threshold=0.5) >= 1
    assert await engram.prune("slow", threshold=0.5) == 0


async def test_recall_uses_per_dataset_decay_rate():
    await engram.remember("The sky is blue.", dataset="slow")
    await engram.set_decay_rate("slow", 0.0)
    _age_dataset("slow", 1000)
    results = await engram.recall("sky", datasets=["slow"])
    assert results[0]["strength"] == pytest.approx(1.0)  # 1.0 undecayed, capped


async def test_set_decay_rate_none_falls_back_to_global():
    await engram.remember("Fact.", dataset="ds", decay_rate=0.0)
    await engram.set_decay_rate("ds", None)
    assert engram._get_store()._meta.get_decay_rate("ds") is None


async def test_negative_decay_rate_is_rejected():
    with pytest.raises(ValueError):
        await engram.remember("Fact.", dataset="bad", decay_rate=-1)
    assert engram._get_store()._meta.get_all_in_dataset("bad") == []
