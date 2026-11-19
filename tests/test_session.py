import asyncio

import pytest

import engram


@pytest.fixture(autouse=True)
def reset_store():
    engram.reset()
    yield
    engram.reset()


async def test_session_exposes_memory_api_and_resets(tmp_path):
    async with engram.session(home=tmp_path) as mem:
        assert mem is engram
        await mem.remember("The sky is blue.", dataset="science")
        assert (await mem.recall("sky", datasets=["science"]))[0]["dataset"] == "science"
        assert (await mem.list_datasets())[0]["item_count"] == 1
    assert engram._store is None
    assert (tmp_path / "meta.db").exists()


async def test_session_resets_on_exception(tmp_path):
    with pytest.raises(RuntimeError, match="block failed"):
        async with engram.session(tmp_path):
            raise RuntimeError("block failed")
    assert engram._store is None


async def test_session_resets_on_task_cancellation(tmp_path):
    entered = asyncio.Event()

    async def run():
        async with engram.session(tmp_path):
            entered.set()
            await asyncio.Event().wait()

    task = asyncio.create_task(run())
    await entered.wait()
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task
    assert engram._store is None


async def test_sequential_default_sessions_do_not_share_memories():
    async with engram.session() as mem:
        await mem.remember("A temporary fact.", dataset="notes")
    async with engram.session() as mem:
        assert await mem.list_datasets() == []
        assert await mem.recall("fact") == []
    assert engram._store is None
