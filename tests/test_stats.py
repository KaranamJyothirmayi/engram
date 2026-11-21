import pytest

import engram


@pytest.fixture(autouse=True)
def fresh_store(tmp_path):
    engram.configure(tmp_path)
    yield
    engram.reset()


async def test_stats_returns_none_for_empty_dataset():
    assert await engram.stats("empty") is None


async def test_stats_returns_none_before_any_remember():
    assert await engram.stats("default") is None


async def test_stats_has_required_fields():
    await engram.remember("The sky is blue.", dataset="science")
    result = await engram.stats("science")
    assert result is not None
    for key in ("name", "count", "avg_strength", "min_strength", "max_strength",
                "oldest_memory", "newest_memory"):
        assert key in result, f"missing key: {key}"


async def test_stats_name_matches_dataset():
    await engram.remember("Paris is in France.", dataset="geo")
    result = await engram.stats("geo")
    assert result["name"] == "geo"


async def test_stats_count_matches_stored_sentences():
    await engram.remember("Sentence one. Sentence two.", dataset="test")
    result = await engram.stats("test")
    assert result["count"] == 2


async def test_stats_strength_bounds():
    await engram.remember("The sky is blue.", dataset="test")
    await engram.remember("Water is wet.", dataset="test")
    result = await engram.stats("test")
    assert result["min_strength"] <= result["avg_strength"] <= result["max_strength"]
    assert 0.0 <= result["min_strength"] <= 1.0
    assert 0.0 <= result["max_strength"] <= 1.0


async def test_stats_oldest_before_newest():
    await engram.remember("First memory.", dataset="test")
    await engram.remember("Second memory.", dataset="test")
    result = await engram.stats("test")
    assert result["oldest_memory"] <= result["newest_memory"]


async def test_stats_isolated_per_dataset():
    await engram.remember("Science fact.", dataset="science")
    await engram.remember("Geography fact.", dataset="geography")
    s = await engram.stats("science")
    g = await engram.stats("geography")
    assert s["name"] == "science"
    assert g["name"] == "geography"
    assert s["count"] == 1
    assert g["count"] == 1
