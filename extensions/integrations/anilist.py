"""Discord command for searching anime on AniList."""

import logging
from typing import TYPE_CHECKING, Any

from discord import Embed, Interaction, app_commands
from discord.ext import commands

from ._anilist_client import AniListError, search_media

if TYPE_CHECKING:
    from main import Sakamoto

logger = logging.getLogger(__name__)


def _label(value: Any) -> str:
    return str(value).replace("_", " ").title() if value else "—"


def anime_embed(media: dict[str, Any], color: int) -> Embed:
    """Build a compact, linked embed for one anime result."""
    titles = media.get("title")
    if not isinstance(titles, dict):
        titles = {}
    title = (
        titles.get("romaji")
        or titles.get("english")
        or titles.get("native")
        or "Unknown anime"
    )
    description = str(media.get("description") or "No synopsis available.").strip()
    if len(description) > 1000:
        description = f"{description[:999].rstrip()}…"

    site_url = media.get("siteUrl")
    embed = Embed(
        title=title[:256],
        url=site_url if isinstance(site_url, str) else None,
        description=description,
        color=color,
    )
    score = media.get("averageScore")
    embed.add_field(
        name="Details",
        value="\n".join(
            (
                f"Format: {_label(media.get('format'))}",
                f"Status: {_label(media.get('status'))}",
                f"Episodes: {media.get('episodes') or '—'}",
                f"Score: {f'{score}/100' if isinstance(score, int) else '—'}",
            )
        ),
    )
    genres = media.get("genres")
    if isinstance(genres, list) and genres:
        embed.add_field(name="Genres", value=", ".join(map(str, genres))[:1024])

    cover = media.get("coverImage")
    cover_url = cover.get("large") if isinstance(cover, dict) else None
    if isinstance(cover_url, str):
        embed.set_thumbnail(url=cover_url)
        embed.add_field(
            name="Artwork", value=f"[Open cover image]({cover_url})", inline=False
        )
    embed.set_author(name="AniList", url="https://anilist.co/")
    return embed


class AniListCog(commands.Cog):
    """Search AniList's public catalogue."""

    def __init__(self, bot: Sakamoto) -> None:
        self.bot = bot

    @app_commands.command(name="anime", description="Search AniList for an anime.")
    @app_commands.describe(query="Anime title to search for.")
    async def anime(self, interaction: Interaction, query: str) -> None:
        query = query.strip()
        if not query:
            await interaction.response.send_message(
                ":x: Enter an anime title to search for.", ephemeral=True
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
            media = await search_media(self.bot.session, query, "ANIME")
        except AniListError as error:
            logger.warning("AniList anime search failed with status %s", error.status)
            message = (
                ":x: AniList has temporarily disabled its API. Please try again later."
                if error.status == 403
                else ":x: AniList is unavailable. Please try again later."
            )
            await interaction.followup.send(message, ephemeral=True)
            return

        if media is None:
            await interaction.followup.send(
                f":mag: No anime found for `{query}`.", ephemeral=True
            )
            return
        await interaction.followup.send(embed=anime_embed(media, self.bot.color))


async def setup(bot: Sakamoto) -> None:
    """Add the AniList cog to the bot."""
    await bot.add_cog(AniListCog(bot))
