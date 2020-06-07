import discord
from discord.ext import commands
import subprocess


class shell(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="sh", hidden=True)
    @commands.is_owner()
    async def shell(self, ctx, *, command):
        output = subprocess.getoutput(command)
        if output is '':
            output = 'No output available'
        embed = discord.Embed(color=0xFF3351)
        embed.description = output
        await ctx.send(embed=embed)

    @shell.error
    async def run_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            await ctx.send(f"You don't have permission, {ctx.author.mention}")
        else:
            raise error


def setup(bot):
    bot.add_cog(shell(bot))
