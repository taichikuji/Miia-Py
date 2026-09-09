import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from extensions.integrations import _kitsu_fallback as kitsu


class DummyResponse:
    def __init__(self, payload):
        self.payload = payload
        self.status = 200

    async def __aenter__(self):
        return self

    async def __aexit__(self, *_args):
        return None

    async def json(self, **_kwargs):
        return self.payload


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("media_type", "resource", "count_field", "result_field"),
    [
        ("ANIME", "anime", "episodeCount", "episodes"),
        ("MANGA", "manga", "chapterCount", "chapters"),
    ],
)
async def test_search_media_normalizes_kitsu_records(
    media_type, resource, count_field, result_field
):
    attributes = {
        "slug": "cowboy-bebop",
        "canonicalTitle": "Cowboy Bebop",
        "titles": {"en": "Cowboy Bebop", "ja_jp": "カウボーイビバップ"},
        "synopsis": "Space bounty hunters.",
        "posterImage": {"large": "https://example.test/poster.jpg"},
        "coverImage": {"large": "https://example.test/banner.jpg"},
        "subtype": "TV",
        "status": "finished",
        "averageRating": "82.27",
        count_field: 26,
    }
    payload = {"data": [{"type": resource, "attributes": attributes}]}
    session = SimpleNamespace(get=MagicMock(return_value=DummyResponse(payload)))

    payload = await kitsu.search_media(session, "Cowboy Bebop", media_type, 5)
    [result] = payload["data"]["Page"]["media"]

    assert result["_provider"] == "Kitsu"
    assert result["title"]["romaji"] == "Cowboy Bebop"
    assert result["title"]["native"] == "カウボーイビバップ"
    assert result["siteUrl"] == f"https://kitsu.io/{resource}/cowboy-bebop"
    assert result["description"] == "Space bounty hunters."
    assert result["coverImage"]["large"] == "https://example.test/poster.jpg"
    assert result["bannerImage"] == "https://example.test/banner.jpg"
    assert result["averageScore"] == 82
    assert result[result_field] == 26
    request = session.get.call_args
    assert request.args == (f"{kitsu.KITSU_URL}/{resource}",)
    assert request.kwargs["params"]["filter[text]"] == "Cowboy Bebop"
    assert count_field in request.kwargs["params"][f"fields[{resource}]"].split(",")
    assert request.kwargs["timeout"].total == 10


@pytest.mark.asyncio
async def test_search_media_rejects_malformed_response():
    session = SimpleNamespace(get=MagicMock(return_value=DummyResponse({"data": {}})))

    with pytest.raises(kitsu.KitsuError, match="unexpected response"):
        await kitsu.search_media(session, "Berserk", "MANGA", 5)
