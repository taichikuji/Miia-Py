"""Minimal async client for AniList media searches."""

from typing import Any, Literal

from aiohttp import ClientError, ClientSession, ClientTimeout

ANILIST_URL = "https://graphql.anilist.co"
MediaType = Literal["ANIME", "MANGA"]

MEDIA_SEARCH = """
query ($search: String!, $type: MediaType!) {
  Page(page: 1, perPage: 1) {
    media(search: $search, type: $type, isAdult: false) {
      title { romaji english native }
      siteUrl
      description(asHtml: false)
      coverImage { large }
      format
      status
      episodes
      averageScore
      genres
    }
  }
}
"""


class AniListError(Exception):
    """AniList could not return a usable response."""

    def __init__(self, message: str, status: int | None = None) -> None:
        self.status = status
        super().__init__(message)


async def search_media(
    session: ClientSession, title: str, media_type: MediaType
) -> dict[str, Any] | None:
    """Return AniList's first safe media match for a title."""
    title = title.strip()
    if not title:
        raise ValueError("An AniList search title is required.")

    try:
        async with session.post(
            ANILIST_URL,
            json={
                "query": MEDIA_SEARCH,
                "variables": {"search": title, "type": media_type},
            },
            timeout=ClientTimeout(total=10),
        ) as response:
            if not 200 <= response.status < 300:
                raise AniListError(
                    f"AniList returned HTTP {response.status}.", response.status
                )
            try:
                payload = await response.json(content_type=None)
            except (TypeError, ValueError) as error:
                raise AniListError("AniList returned invalid JSON.") from error
    except (ClientError, TimeoutError) as error:
        raise AniListError("Could not reach AniList.") from error

    if not isinstance(payload, dict) or payload.get("errors"):
        raise AniListError("AniList rejected the search.")
    data = payload.get("data")
    page = data.get("Page") if isinstance(data, dict) else None
    media = page.get("media") if isinstance(page, dict) else None
    if not isinstance(media, list):
        raise AniListError("AniList returned an unexpected response.")
    return media[0] if media and isinstance(media[0], dict) else None
