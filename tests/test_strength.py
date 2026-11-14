import pytest

import engram


@pytest.fixture(autouse=True)
def fresh_store(tmp_path):
    engram.configure(tmp_path)
    yield
    engram.reset()


@pytest.mark.parametrize("strength", [0.0, 0.5, 1.0])
async def test_initial_strength_applies_to_every_sentence(strength):
    await engram.remember("The sky is blue. Grass is green.", strength=strength)
    rows = engram._get_store()._meta.get_all_in_dataset("default")
    assert len(rows) == 2
    assert all(row["strength"] == strength for row in rows)


async def test_default_strength_is_unchanged():
    await engram.remember("An ordinary memory.")
    assert engram._get_store()._meta.get_all_in_dataset("default")[0]["strength"] == 1.0


@pytest.mark.parametrize("strength", [-0.1, 1.1, float("nan"), float("inf"), -float("inf")])
async def test_invalid_strength_does_not_store_anything(strength):
    with pytest.raises(ValueError, match="strength"):
        await engram.remember("A rejected memory.", strength=strength)
    assert await engram.list_datasets() == []


async def test_initial_strength_affects_pruning():
    await engram.remember("A low priority fact.", dataset="notes", strength=0.1)
    await engram.remember("An important fact.", dataset="notes")
    assert await engram.prune("notes", threshold=0.2) == 1
    rows = engram._get_store()._meta.get_all_in_dataset("notes")
    assert [row["text"] for row in rows] == ["An important fact."]


def test_meta_insert_preserves_supplied_strength():
    meta = engram._get_store()._meta
    memory_id = meta.insert("A fact.", "notes", strength=0.25)
    assert meta.get_by_ids([memory_id])[0]["strength"] == 0.25
