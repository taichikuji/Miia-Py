import discord
from discord.ext import commands
from platform import python_version, system, machine
import aiohttp


class miia(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="info",
                      brief="Show information about the bot",
                      description="Show information about the bot, versions of dependencies, uptime or memory usage of the bot!")
    async def info(self, ctx):
        embed = await self.create_embed(ctx)
        await ctx.send(embed=embed)

    async def create_embed(self, ctx):
        # creation of embed with all important info
        em = {
            "title": "Bot's info",
            "description": "Hello hello! I'm [Miia](https://github.com/taichikuji/Miia-Py). Here's some information regarding me and my dependencies!",
            "color": 0xFF3351,
            "thumbnail": {"url": str(self.bot.user.avatar_url)},
            "fields": [{"name": "Versions",
                        "value":
                        f"**Python**: {python_version()}\n"
                        f"**Miia-Py**: bruh\n"
                        f"**Discord.py**: {discord.__version__}\n"
                        f"**Aiohttp**: {aiohttp.__version__}"},
                       {"name": "OS",
                        "value": f"**{system()}**: {machine()}",
                        "inline": True},
                       {"name": "Uptime",
                        "value": await self.uptime(),
                        "inline": True},
                       {"name": "Average load",
                        "value": await self.load(),
                        "inline": True}],
            "footer": {"text": f"Made by {self.bot.get_user(id=199632174603829249)}",
                       "icon_url": f"{self.bot.get_user(id=199632174603829249).avatar_url}"}
        }
        embed = discord.Embed.from_dict(em)
        return embed

    async def uptime(self):
        uptime = None
        with open("/proc/uptime", "r") as f:
            uptime = f.read().split(" ")[0].strip()
        uptime = int(float(uptime))
        uptime_hours = uptime // 3600
        uptime_minutes = (uptime % 3600) // 60
        uptime = f"{str(uptime_hours)} hours, {str(uptime_minutes)} minutes"
        return uptime

    async def load(self):
        with open("/proc/loadavg", "r") as f:
            load = f.read().strip()
        return load


def setup(bot):
    bot.add_cog(miia(bot))
