import discord
from discord.ext import commands


class ping(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="ping",
                      brief="Show Miia's Latency")
    async def ping(self, ctx):
        embed = discord.Embed(color=0xFF3351)
        latency = f'Latency: **{round(self.bot.latency * 1000)}** ms'
        embed.description = latency
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(ping(bot))
