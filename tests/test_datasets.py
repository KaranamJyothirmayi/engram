import pytest

import engram


@pytest.fixture(autouse=True)
def fresh_store(tmp_path):
    engram.configure(tmp_path)
    yield
    engram.reset()


async def test_list_datasets_empty_store():
    assert await engram.list_datasets() == []


async def test_list_datasets_reports_names_and_item_counts():
    await engram.remember("The sky is blue.", dataset="science")
    await engram.remember("Water freezes at zero degrees.", dataset="science")
    await engram.remember("Paris is in France.", dataset="geography")

    datasets = await engram.list_datasets()

    assert {row["name"]: row["item_count"] for row in datasets} == {
        "science": 2,
        "geography": 1,
    }


async def test_list_datasets_excludes_forgotten_dataset():
    await engram.remember("A temporary fact.", dataset="temporary")
    await engram.remember("A lasting fact.", dataset="lasting")

    await engram.forget("temporary")

    datasets = await engram.list_datasets()
    assert [(row["name"], row["item_count"]) for row in datasets] == [("lasting", 1)]


async def test_list_datasets_counts_remaining_memories_after_pruning():
    await engram.remember("An old fact. A fresh fact.", dataset="science")
    store = engram._get_store()
    old = store._meta.get_all_in_dataset("science")[0]
    store._meta.update_accessed(old["id"], 0.1)

    assert await engram.prune("science", threshold=0.2) == 1

    datasets = await engram.list_datasets()
    assert [(row["name"], row["item_count"]) for row in datasets] == [("science", 1)]
