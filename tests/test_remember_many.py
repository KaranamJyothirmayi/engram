import pytest

import engram


@pytest.fixture(autouse=True)
def fresh_store(tmp_path):
    engram.configure(tmp_path)
    yield
    engram.reset()


async def test_remember_many_stores_all_texts():
    count = await engram.remember_many([
        "The sky is blue.",
        "Water freezes at zero degrees.",
        "Paris is in France.",
    ], dataset="science")
    assert count == 3
    datasets = await engram.list_datasets()
    assert any(d["name"] == "science" and d["item_count"] == 3 for d in datasets)


async def test_remember_many_empty_list_stores_nothing():
    count = await engram.remember_many([], dataset="test")
    assert count == 0
    assert await engram.list_datasets() == []


async def test_remember_many_skips_blank_strings():
    count = await engram.remember_many(
        ["Valid sentence.", "", "   ", "Another valid sentence."],
        dataset="test",
    )
    assert count == 2


async def test_remember_many_results_are_recallable():
    await engram.remember_many([
        "Marie Curie discovered polonium.",
        "She was born in Warsaw.",
    ], dataset="science")
    results = await engram.recall("Marie Curie birthplace", datasets=["science"])
    assert any("Warsaw" in r["text"] for r in results)


async def test_remember_many_respects_strength():
    count = await engram.remember_many(
        ["Low priority note."], dataset="notes", strength=0.3
    )
    assert count == 1
    store = engram._get_store()
    rows = store._meta.get_all_in_dataset("notes")
    assert all(abs(r["strength"] - 0.3) < 0.001 for r in rows)


async def test_remember_many_invalid_strength_raises():
    with pytest.raises(ValueError):
        await engram.remember_many(["Some text."], dataset="test", strength=1.5)


async def test_remember_many_multi_sentence_text():
    count = await engram.remember_many(
        ["First sentence. Second sentence."], dataset="test"
    )
    assert count == 2


async def test_remember_many_isolated_per_dataset():
    await engram.remember_many(["Fact A.", "Fact B."], dataset="ds1")
    await engram.remember_many(["Fact C."], dataset="ds2")
    datasets = {d["name"]: d["item_count"] for d in await engram.list_datasets()}
    assert datasets["ds1"] == 2
    assert datasets["ds2"] == 1
