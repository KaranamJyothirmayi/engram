import pytest

import engram


TEXTS = [
    "The sky is blue.",
    "Water freezes at zero degrees.",
    "Paris is in France.",
    "Mount Everest is the tallest mountain.",
    "The Amazon is the largest river by discharge.",
    "The Great Wall of China is in Asia.",
]


@pytest.fixture(autouse=True)
def fresh_store(tmp_path):
    engram.configure(tmp_path)
    yield
    engram.reset()


@pytest.fixture()
async def populated(tmp_path):
    for text in TEXTS:
        await engram.remember(text, dataset="facts")


async def test_recall_default_returns_results(populated):
    results = await engram.recall("geography", datasets=["facts"])
    assert isinstance(results, list)


async def test_recall_limit_caps_result_count(populated):
    results = await engram.recall("geography", datasets=["facts"], limit=2)
    assert len(results) <= 2


async def test_recall_limit_one(populated):
    results = await engram.recall("water", datasets=["facts"], limit=1)
    assert len(results) == 1


async def test_recall_offset_skips_top_results(populated):
    all_results = await engram.recall("geography", datasets=["facts"])
    offset_results = await engram.recall("geography", datasets=["facts"], offset=1)
    if len(all_results) > 1:
        assert offset_results[0]["text"] == all_results[1]["text"]


async def test_recall_offset_beyond_results_returns_empty(populated):
    results = await engram.recall("geography", datasets=["facts"], offset=1000)
    assert results == []


async def test_recall_limit_and_offset_together(populated):
    page1 = await engram.recall("geography", datasets=["facts"], limit=2, offset=0)
    page2 = await engram.recall("geography", datasets=["facts"], limit=2, offset=2)
    page1_texts = {r["text"] for r in page1}
    page2_texts = {r["text"] for r in page2}
    assert page1_texts.isdisjoint(page2_texts)


async def test_recall_limit_none_returns_all(populated):
    no_limit = await engram.recall("geography", datasets=["facts"], limit=None)
    with_limit = await engram.recall("geography", datasets=["facts"], limit=100)
    assert len(no_limit) == len(with_limit)


async def test_recall_zero_offset_same_as_no_offset(populated):
    without = await engram.recall("water", datasets=["facts"])
    with_zero = await engram.recall("water", datasets=["facts"], offset=0)
    assert [r["text"] for r in without] == [r["text"] for r in with_zero]
