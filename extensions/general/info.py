import time
from typing import TYPE_CHECKING

from discord import Embed, Interaction, app_commands
from discord.ext import commands

if TYPE_CHECKING:
    from main import Sakamoto


class InfoCog(commands.Cog):
    """Cog that reports project information and uptime."""

    def __init__(self, bot: Sakamoto):
        self.bot = bot

    @app_commands.command(
        name="info",
        description="Learn about Sakamoto and check its uptime.",
    )
    async def info(self, interaction: Interaction):
        """Send the bot information embed."""
        embed = self.create_embed()
        await interaction.response.send_message(embed=embed)

    def create_embed(self):
        """Build the bot information embed."""
        embed_data = {
            "title": ":information_source: About Sakamoto",
            "description": "A voice-first Discord bot for small-to-medium communities.",
            "color": self.bot.color,
            "fields": [
                {
                    "name": "Uptime",
                    "value": self.uptime(),
                    "inline": True,
                },
                {
                    "name": "Project",
                    "value": "[GitHub](https://github.com/taichikuji/Sakamoto)",
                    "inline": True,
                },
            ],
        }
        return Embed.from_dict(embed_data)

    def uptime(self):
        """Return the bot uptime."""
        uptime_seconds = int(time.monotonic() - self.bot.started_at)
        uptime_hours = uptime_seconds // 3600
        uptime_minutes = (uptime_seconds % 3600) // 60
        return f"{uptime_hours}h {uptime_minutes}m"


async def setup(bot: Sakamoto):
    """Add the InfoCog to the bot."""
    await bot.add_cog(InfoCog(bot))
