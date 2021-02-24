from discord import Embed
from os import getpid
from discord.ext import commands
from platform import python_version, system, machine
from psutil import Process


class miia(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="info",
                      brief="Show information about the bot",
                      description="Show information about the bot, versions of dependencies, uptime or memory usage of the bot!",
                      usage="`info`")
    async def info(self, ctx):
        embed = await self.create_embed(ctx)
        await ctx.send(embed=embed)

    async def create_embed(self, ctx):
        # creation of embed with all important info
        em = {
            "title": "Bot's info",
            "description": "Oh, you wanna know more about me? I'm [Miia](https://github.com/taichikuji/Miia-Py). Here's some information regarding me and my dependencies!",
            "color": self.bot.color,
            "thumbnail": {"url": str(self.bot.user.avatar_url)},
            "fields": [{"name": "Bot version",
                        "value": f"**Python**: {python_version()}\n"
                                f"**Miia-Py**: 0.1.8\n",
                        "inline": True},
                       {"name": "OS",
                        "value": f"**{system()}**: {machine()}"},
                       {"name": "Uptime",
                        "value": await self.uptime(),
                        "inline": True},
                       {"name": "Memory",
                        "value": await self._get_mem_usage(),
                        "inline": True}],
            "footer": {"text": f"Made by {self.bot.get_user(id=self.bot.owner_id)}",
                       "icon_url": f"{self.bot.get_user(id=self.bot.owner_id).avatar_url}"}
        }
        embed = Embed.from_dict(em)
        return embed

    @staticmethod
    async def _get_mem_usage():
        mem_usage = float(Process(
            getpid()).memory_info().rss)/1000000
        return str(round(mem_usage, 2)) + " MB"

    async def uptime(self):
        uptime = None
        with open("/proc/uptime", "r") as f:
            uptime = f.read().split(" ")[0].strip()
        uptime = int(float(uptime))
        uptime_hours = uptime // 3600
        uptime_minutes = (uptime % 3600) // 60
        uptime = f"{str(uptime_hours)} hours, {str(uptime_minutes)} minutes"
        return uptime


def setup(bot):
    bot.add_cog(miia(bot))
