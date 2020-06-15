import discord
from discord.ext import commands


class api(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="commit",
                      brief="Show a random funny commit message",
                      description="Show a random funny commit message from WhatTheCommit's site")
    async def commit(self, ctx):
        async with self.bot.session.get("http://whatthecommit.com/index.txt") as api_result:
            embed = discord.Embed(description=(await api_result.text()), color=0xFF3351)
            await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(api(bot))
