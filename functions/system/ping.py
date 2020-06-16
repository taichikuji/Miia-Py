from discord import Embed
from discord.ext import commands


class miia(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="ping",
                      brief="Show Miia's Latency",
                      description="Show Miia's Latency in ms")
    async def ping(self, ctx):
        embed = Embed(color=self.bot.color)
        latency = f'Latency: **{round(self.bot.latency * 1000)}** ms'
        embed.description = latency
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(miia(bot))
