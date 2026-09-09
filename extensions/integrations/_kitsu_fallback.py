"""Kitsu-owned media fallback transport and response normalization.

This module contains every Kitsu-specific URL, request rule, error, and
JSON:API field mapping. It translates Kitsu responses into the AniList
GraphQL response shape consumed by the shared parser.
"""

from typing import Any, Literal

from aiohttp import ClientError, ClientSession, ClientTimeout

# Kitsu-owned protocol constants and supported media scope.
KITSU_URL = "https://kitsu.io/api/edge"
MediaType = Literal["ANIME", "MANGA"]


class KitsuError(Exception):
    """Kitsu could not return a usable fallback response."""

    def __init__(self, message: str, status: int | None = None) -> None:
        self.status = status
        super().__init__(message)


async def search_media(
    session: ClientSession,
    query: str,
    media_type: MediaType,
    limit: int,
) -> dict[str, Any]:
    """Search Kitsu and translate its records into an AniList Page response."""
    resource = media_type.lower()
    # Keep fallback payloads limited to fields already displayed by the bot.
    fields = (
        "slug,canonicalTitle,titles,synopsis,posterImage,coverImage,subtype,"
        "status,averageRating,"
        + ("episodeCount" if media_type == "ANIME" else "chapterCount,volumeCount")
    )
    try:
        async with session.get(
            f"{KITSU_URL}/{resource}",
            params={
                "filter[text]": query,
                "page[limit]": str(limit),
                f"fields[{resource}]": fields,
            },
            headers={
                "Accept": "application/vnd.api+json",
                "Content-Type": "application/vnd.api+json",
            },
            timeout=ClientTimeout(total=10),
        ) as response:
            if not 200 <= response.status < 300:
                raise KitsuError(
                    f"Kitsu returned HTTP {response.status}.", response.status
                )
            try:
                payload = await response.json(content_type=None)
            except (TypeError, ValueError) as error:
                raise KitsuError("Kitsu returned invalid JSON.") from error
    except (ClientError, TimeoutError) as error:
        raise KitsuError("Could not reach Kitsu.") from error

    data = payload.get("data") if isinstance(payload, dict) else None
    if not isinstance(data, list):
        raise KitsuError("Kitsu returned an unexpected response.")

    # Normalize here so no Kitsu-specific JSON:API shape leaks into AniList code.
    results: list[dict[str, Any]] = []
    for item in data:
        attributes = item.get("attributes") if isinstance(item, dict) else None
        if not isinstance(attributes, dict):
            raise KitsuError("Kitsu returned an unexpected response.")
        titles = attributes.get("titles")
        if not isinstance(titles, dict):
            titles = {}
        try:
            score = round(float(attributes["averageRating"]))
        except KeyError, TypeError, ValueError:
            score = None
        slug = attributes.get("slug")
        poster = attributes.get("posterImage")
        banner = attributes.get("coverImage")
        results.append(
            {
                "_provider": "Kitsu",
                "title": {
                    "romaji": attributes.get("canonicalTitle"),
                    "english": titles.get("en"),
                    "native": titles.get("ja_jp"),
                },
                "siteUrl": (
                    f"https://kitsu.io/{resource}/{slug}"
                    if isinstance(slug, str)
                    else None
                ),
                "description": attributes.get("synopsis"),
                "coverImage": poster if isinstance(poster, dict) else None,
                "bannerImage": banner.get("large")
                if isinstance(banner, dict)
                else None,
                "format": attributes.get("subtype"),
                "status": attributes.get("status"),
                "episodes": attributes.get("episodeCount"),
                "chapters": attributes.get("chapterCount"),
                "volumes": attributes.get("volumeCount"),
                "averageScore": score,
            }
        )
    # The shared AniList Page parser now handles responses from either provider.
    return {"data": {"Page": {"media": results}}}
