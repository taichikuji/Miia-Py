from discord import Embed
from discord.ext import commands


class api(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name = "commit",
        brief = "Show a random funny commit message",
        description = "Show a random funny commit message from WhatTheCommit's site",
        usage = "`commit`"
    )
    async def commit(self, ctx):
        async with self.bot.session.get("http://whatthecommit.com/index.txt") as api_result:
            await ctx.send(embed = \
                Embed(description = (await api_result.text()), color = self.bot.color)
            )


def setup(bot):
    bot.add_cog(api(bot))
