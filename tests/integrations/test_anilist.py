import asyncio
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from extensions.integrations import anilist


def _make_cog():
    return anilist.AniListCog(SimpleNamespace(session=object(), color=0x123456))


@pytest.mark.asyncio
async def test_cache_normalizes_queries_and_keeps_empty_results(monkeypatch):
    now = [0.0]
    calls = []

    async def search(_session, title, media_type):
        calls.append((title, media_type))
        return None if len(calls) == 1 else {"id": 1}

    monkeypatch.setattr(anilist, "monotonic", lambda: now[0])
    monkeypatch.setattr(anilist, "search_media", search)
    cog = _make_cog()

    assert await cog._cached_search("Cowboy  Bebop", "ANIME") is None
    assert await cog._cached_search(" cowboy bebop ", "ANIME") is None
    assert len(calls) == 1

    now[0] = anilist.CACHE_TTL_SECONDS + 1
    assert await cog._cached_search("cowboy bebop", "ANIME") == {"id": 1}
    assert len(calls) == 2


@pytest.mark.asyncio
async def test_cache_coalesces_concurrent_equivalent_searches(monkeypatch):
    started = asyncio.Event()
    release = asyncio.Event()
    calls = 0
    result = {"id": 1}

    async def search(_session, _title, _media_type):
        nonlocal calls
        calls += 1
        started.set()
        await release.wait()
        return result

    monkeypatch.setattr(anilist, "search_media", search)
    cog = _make_cog()

    first = asyncio.create_task(cog._cached_search("Frieren", "ANIME"))
    await started.wait()
    second = asyncio.create_task(cog._cached_search(" frieren ", "ANIME"))
    await asyncio.sleep(0)
    release.set()

    assert await asyncio.gather(first, second) == [result, result]
    assert calls == 1


@pytest.mark.asyncio
async def test_cache_does_not_store_failures(monkeypatch):
    calls = 0
    result = {"id": 1}

    async def search(_session, _title, _media_type):
        nonlocal calls
        calls += 1
        if calls == 1:
            raise anilist.AniListError("unavailable", 503)
        return result

    monkeypatch.setattr(anilist, "search_media", search)
    cog = _make_cog()

    with pytest.raises(anilist.AniListError):
        await cog._cached_search("Frieren", "ANIME")
    assert await cog._cached_search("Frieren", "ANIME") == result
    assert calls == 2


@pytest.mark.asyncio
async def test_cache_stays_bounded(monkeypatch):
    monkeypatch.setattr(anilist, "monotonic", lambda: 0.0)
    monkeypatch.setattr(
        anilist, "search_media", lambda *_args: asyncio.sleep(0, result={"id": 999})
    )
    cog = _make_cog()
    cog.search_cache = {
        ("ANIME", f"title {index}"): (100.0, {"id": index})
        for index in range(anilist.CACHE_LIMIT)
    }

    await cog._cached_search("New title", "ANIME")

    assert len(cog.search_cache) == anilist.CACHE_LIMIT
    assert ("ANIME", "title 0") not in cog.search_cache
    assert ("ANIME", "new title") in cog.search_cache
