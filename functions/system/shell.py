import discord
from discord.ext import commands
import subprocess


class miia(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="sh",
                      hidden=True,
                      brief="Load a command",
                      description="Load a command directly from shell")
    @commands.is_owner()
    async def shell(self, ctx, *, command):
        output = subprocess.getoutput(command)
        if output == '':
            output = 'No output available'
        embed = discord.Embed(description=output, color=0xFF3351)
        await ctx.send(embed=embed)

    @shell.error
    async def run_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            await ctx.send(f"You don't have permission, {ctx.author.mention}")
        else:
            raise error


def setup(bot):
    bot.add_cog(miia(bot))
