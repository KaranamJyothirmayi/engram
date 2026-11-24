import pytest

import engram
from engram.decay import RECALL_BOOST


@pytest.fixture(autouse=True)
def fresh_store(tmp_path):
    engram.configure(tmp_path)
    yield
    engram.reset()


async def test_default_boost_increases_strength():
    await engram.remember("The sky is blue.", dataset="test")
    store = engram._get_store()
    rows = store._meta.get_all_in_dataset("test")
    store._meta.update_accessed(rows[0]["id"], 0.5)

    results = await engram.recall("sky", datasets=["test"])
    assert results[0]["strength"] > 0.5


async def test_default_boost_value_is_point_three(tmp_path):
    engram.configure(tmp_path)
    await engram.remember("The sky is blue.", dataset="test")
    store = engram._get_store()
    rows = store._meta.get_all_in_dataset("test")
    store._meta.update_accessed(rows[0]["id"], 0.5)

    results = await engram.recall("sky", datasets=["test"])
    assert abs(results[0]["strength"] - min(1.0, 0.5 + RECALL_BOOST)) < 0.01


async def test_configure_custom_boost(tmp_path):
    engram.configure(tmp_path, recall_boost=0.1)
    await engram.remember("The sky is blue.", dataset="test")
    store = engram._get_store()
    rows = store._meta.get_all_in_dataset("test")
    store._meta.update_accessed(rows[0]["id"], 0.5)

    results = await engram.recall("sky", datasets=["test"])
    assert abs(results[0]["strength"] - 0.6) < 0.01


async def test_boost_zero_leaves_strength_unchanged(tmp_path):
    engram.configure(tmp_path, recall_boost=0.0)
    await engram.remember("Water is wet.", dataset="test")
    store = engram._get_store()
    rows = store._meta.get_all_in_dataset("test")
    store._meta.update_accessed(rows[0]["id"], 0.4)

    results = await engram.recall("water", datasets=["test"])
    assert abs(results[0]["strength"] - 0.4) < 0.01


async def test_boost_caps_at_one(tmp_path):
    engram.configure(tmp_path, recall_boost=0.9)
    await engram.remember("Paris is in France.", dataset="test")
    store = engram._get_store()
    rows = store._meta.get_all_in_dataset("test")
    store._meta.update_accessed(rows[0]["id"], 0.8)

    results = await engram.recall("Paris", datasets=["test"])
    assert results[0]["strength"] == 1.0


async def test_configure_boost_persists_across_recalls(tmp_path):
    engram.configure(tmp_path, recall_boost=0.2)
    await engram.remember("Marie Curie.", dataset="test")
    store = engram._get_store()
    rows = store._meta.get_all_in_dataset("test")
    store._meta.update_accessed(rows[0]["id"], 0.3)

    r1 = await engram.recall("Marie Curie", datasets=["test"])
    assert abs(r1[0]["strength"] - 0.5) < 0.01

    r2 = await engram.recall("Marie Curie", datasets=["test"])
    assert abs(r2[0]["strength"] - 0.7) < 0.01
