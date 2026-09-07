import logging
from asyncio import Lock
from html.parser import HTMLParser
from time import monotonic
from typing import TYPE_CHECKING, Any, Literal

from aiohttp import ClientError, ClientSession, ClientTimeout
from discord import Embed, Interaction, app_commands
from discord.ext import commands

try:
    from ._anilist_test_headers import HEADERS as LOCAL_TEST_HEADERS
except ModuleNotFoundError:
    LOCAL_TEST_HEADERS = None

if TYPE_CHECKING:
    from main import Sakamoto

logger = logging.getLogger(__name__)

if LOCAL_TEST_HEADERS:
    logger.warning(
        "Using local AniList test headers; do not deploy this configuration."
    )

ANILIST_URL = "https://graphql.anilist.co"
MediaType = Literal["ANIME", "MANGA"]
SearchType = Literal["ANIME", "MANGA", "CHARACTER"]

# ANILIST REQUEST POLICY
# AniList is a shared, rate-limited service currently operating with reduced capacity.
# Every new command must reuse cached reads, coalesce equivalent requests, request only
# fields it displays, and avoid retries during outages or rate limits. Pagination must
# cache fetched pages instead of requesting them again when users navigate backwards.
# Prefer slightly stale public catalogue data over avoidable upstream traffic.
CACHE_TTL_SECONDS = 15 * 60
CACHE_LIMIT = 256
DESCRIPTION_LIMIT = 500

MEDIA_SEARCH = """
query ($search: String!, $type: MediaType!) {
  Page(page: 1, perPage: 1) {
    media(search: $search, type: $type, isAdult: false) {
      title { romaji english native }
      siteUrl
      description(asHtml: false)
      coverImage { large }
      bannerImage
      format
      status
      episodes
      chapters
      volumes
      averageScore
      genres
    }
  }
}
"""

CHARACTER_SEARCH = """
query ($search: String!) {
  Page(page: 1, perPage: 1) {
    characters(search: $search) {
      name { full native }
      siteUrl
      description(asHtml: false)
      image { large }
      gender
      age
      favourites
    }
  }
}
"""


class AniListError(Exception):
    """AniList could not return a usable response."""

    def __init__(self, message: str, status: int | None = None) -> None:
        self.status = status
        super().__init__(message)


class _DescriptionParser(HTMLParser):
    """Turn AniList's lightweight description HTML into Discord-safe text."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "br":
            self.parts.append("\n")

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.handle_starttag(tag, attrs)

    def handle_data(self, data: str) -> None:
        if self.parts and self.parts[-1].endswith("\n") and data.startswith("\n"):
            data = data[1:]
        self.parts.append(data)


def _clean_description(value: Any) -> str:
    parser = _DescriptionParser()
    parser.feed(str(value or "No synopsis available."))
    parser.close()
    description = "".join(parser.parts).strip() or "No synopsis available."
    while "\n\n\n" in description:
        description = description.replace("\n\n\n", "\n\n")
    if len(description) <= DESCRIPTION_LIMIT:
        return description

    shortened = description[: DESCRIPTION_LIMIT - 1].rstrip()
    word_end = max(shortened.rfind(" "), shortened.rfind("\n"))
    if word_end > 0:
        shortened = shortened[:word_end].rstrip()
    return f"{shortened}…"


async def _request(
    session: ClientSession, query: str, variables: dict[str, str]
) -> dict[str, Any]:
    try:
        async with session.post(
            ANILIST_URL,
            json={"query": query, "variables": variables},
            headers=LOCAL_TEST_HEADERS,
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
    return payload


def _first_page_result(payload: dict[str, Any], field: str) -> dict[str, Any] | None:
    data = payload.get("data")
    page = data.get("Page") if isinstance(data, dict) else None
    results = page.get(field) if isinstance(page, dict) else None
    if not isinstance(results, list):
        raise AniListError("AniList returned an unexpected response.")
    return results[0] if results and isinstance(results[0], dict) else None


async def search_media(
    session: ClientSession, title: str, media_type: MediaType
) -> dict[str, Any] | None:
    """Return AniList's first safe media match for a title."""
    title = title.strip()
    if not title:
        raise ValueError("An AniList search title is required.")
    payload = await _request(
        session, MEDIA_SEARCH, {"search": title, "type": media_type}
    )
    return _first_page_result(payload, "media")


async def search_character(session: ClientSession, name: str) -> dict[str, Any] | None:
    """Return AniList's first character match for a name."""
    name = name.strip()
    if not name:
        raise ValueError("An AniList character name is required.")
    payload = await _request(session, CHARACTER_SEARCH, {"search": name})
    return _first_page_result(payload, "characters")


def _label(value: Any) -> str:
    if not value:
        return "—"
    return " ".join(
        word if word in {"TV", "OVA", "ONA"} else word.title()
        for word in str(value).split("_")
    )


def media_embed(
    media: dict[str, Any], media_type: MediaType, color: int, *, cached: bool = False
) -> Embed:
    """Build a compact, linked embed for one anime or manga result."""
    titles = media.get("title")
    if not isinstance(titles, dict):
        titles = {}
    title = (
        titles.get("romaji")
        or titles.get("english")
        or titles.get("native")
        or f"Unknown {media_type.lower()}"
    )
    description = _clean_description(media.get("description"))

    site_url = media.get("siteUrl")
    embed = Embed(
        title=title[:256],
        url=site_url if isinstance(site_url, str) else None,
        description=description,
        color=color,
    )
    score = media.get("averageScore")
    metrics = [("⭐ Score", f"{score}/100" if isinstance(score, int) else "—")]
    if media_type == "ANIME":
        metrics.extend(
            (
                ("🎬 Episodes", str(media.get("episodes") or "—")),
                ("📡 Status", _label(media.get("status"))),
            )
        )
    else:
        metrics.extend(
            (
                (
                    "📚 Ch / Vol",
                    f"{media.get('chapters') or '—'} / {media.get('volumes') or '—'}",
                ),
                ("📡 Status", _label(media.get("status"))),
            )
        )
    for name, value in metrics:
        embed.add_field(name=name, value=value, inline=True)

    footer = [_label(media.get("format"))]
    genres = media.get("genres")
    if isinstance(genres, list) and genres:
        footer.extend(map(str, genres))
    embed.set_footer(text=" • ".join(footer)[:2048])

    cover = media.get("coverImage")
    cover_url = cover.get("large") if isinstance(cover, dict) else None
    if isinstance(cover_url, str):
        embed.set_thumbnail(url=cover_url)
    banner_url = media.get("bannerImage")
    if isinstance(banner_url, str):
        embed.set_image(url=banner_url)
    author = "AniList • Cached" if cached else "AniList"
    embed.set_author(name=author, url="https://anilist.co/")
    return embed


def character_embed(
    character: dict[str, Any], color: int, *, cached: bool = False
) -> Embed:
    """Build a compact, linked embed for one character result."""
    names = character.get("name")
    if not isinstance(names, dict):
        names = {}
    title = names.get("full") or names.get("native") or "Unknown character"
    site_url = character.get("siteUrl")
    embed = Embed(
        title=str(title)[:256],
        url=site_url if isinstance(site_url, str) else None,
        description=_clean_description(character.get("description")),
        color=color,
    )
    favourites = character.get("favourites")
    metrics = (
        ("⚧ Gender", str(character.get("gender") or "—")),
        ("🎂 Age", str(character.get("age") or "—")),
        (
            "❤️ Favourites",
            f"{favourites:,}" if isinstance(favourites, int) else "—",
        ),
    )
    for name, value in metrics:
        embed.add_field(name=name, value=value, inline=True)

    native_name = names.get("native")
    footer = "Character"
    if isinstance(native_name, str) and native_name != title:
        footer = f"{footer} • {native_name}"
    embed.set_footer(text=footer[:2048])

    image = character.get("image")
    image_url = image.get("large") if isinstance(image, dict) else None
    if isinstance(image_url, str):
        embed.set_thumbnail(url=image_url)
    author = "AniList • Cached" if cached else "AniList"
    embed.set_author(name=author, url="https://anilist.co/")
    return embed


class AniListCog(commands.Cog):
    """Search AniList's public catalogue."""

    def __init__(self, bot: Sakamoto) -> None:
        self.bot = bot
        self.search_cache: dict[
            tuple[SearchType, str], tuple[float, dict[str, Any] | None]
        ] = {}
        self.search_lock = Lock()

    async def _cached_search(
        self, query: str, search_type: SearchType
    ) -> tuple[dict[str, Any] | None, bool]:
        key = (search_type, " ".join(query.casefold().split()))
        if (cached := self.search_cache.get(key)) and cached[0] > monotonic():
            return cached[1], True

        async with self.search_lock:
            if (cached := self.search_cache.get(key)) and cached[0] > monotonic():
                return cached[1], True
            result = (
                await search_character(self.bot.session, query)
                if search_type == "CHARACTER"
                else await search_media(self.bot.session, query, search_type)
            )
            now = monotonic()
            self.search_cache = {
                cache_key: value
                for cache_key, value in self.search_cache.items()
                if value[0] > now
            }
            while len(self.search_cache) >= CACHE_LIMIT:
                self.search_cache.pop(next(iter(self.search_cache)))
            self.search_cache[key] = (now + CACHE_TTL_SECONDS, result)
            return result, False

    @app_commands.command(name="anime", description="Search AniList for an anime.")
    @app_commands.describe(query="Anime title to search for.")
    async def anime(self, interaction: Interaction, query: str) -> None:
        await self._search_command(interaction, query, "ANIME")

    @app_commands.command(name="manga", description="Search AniList for a manga.")
    @app_commands.describe(query="Manga title to search for.")
    async def manga(self, interaction: Interaction, query: str) -> None:
        await self._search_command(interaction, query, "MANGA")

    @app_commands.command(
        name="character", description="Search AniList for a character."
    )
    @app_commands.describe(query="Character name to search for.")
    async def character(self, interaction: Interaction, query: str) -> None:
        await self._search_command(interaction, query, "CHARACTER")

    async def _search_command(
        self, interaction: Interaction, query: str, search_type: SearchType
    ) -> None:
        label = search_type.lower()
        query = query.strip()
        if not query:
            query_kind = "name" if search_type == "CHARACTER" else "title"
            await interaction.response.send_message(
                f":x: Enter a {label} {query_kind} to search for.", ephemeral=True
            )
            return
        if self.bot.session is None:
            await interaction.response.send_message(
                ":x: The bot's HTTP session is not ready. Please try again later.",
                ephemeral=True,
            )
            return

        await interaction.response.defer()
        try:
            result, cached = await self._cached_search(query, search_type)
        except AniListError as error:
            logger.warning(
                "AniList %s search failed with status %s", label, error.status
            )
            message = (
                ":x: AniList has temporarily disabled its API. Please try again later."
                if error.status == 403
                else ":x: AniList is unavailable. Please try again later."
            )
            await interaction.followup.send(message, ephemeral=True)
            return

        if result is None:
            await interaction.followup.send(
                f":mag: No {label} found for `{query}`.", ephemeral=True
            )
            return
        embed = (
            character_embed(result, self.bot.color, cached=cached)
            if search_type == "CHARACTER"
            else media_embed(result, search_type, self.bot.color, cached=cached)
        )
        await interaction.followup.send(embed=embed)


async def setup(bot: Sakamoto) -> None:
    """Add the AniList cog to the bot."""
    await bot.add_cog(AniListCog(bot))
