import discord
from discord.ext import commands


class miia(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="testing",
                      brief="Show Miia's Latency",
                      description="Show Miia's Latency in ms")
    async def testing(self, ctx):
        embed = discord.Embed(color=0xFF3351)
        latency = '''
                  Lorem ipsum dolor sit amet,
                  consectetur adipiscing elit,
                  sed do eiusmod tempor incididunt
                  ut labore et dolore magna aliqua.
                  '''
        embed.description = latency
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(miia(bot))
