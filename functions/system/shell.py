from discord import Embed
from discord.ext import commands
from subprocess import getoutput


class miia(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name = "sh",
        aliases = ['shell', 'bash', 'zsh'],
        hidden = True,
        brief = "Load a command",
        description = "Load a command directly from shell",
        usage = "`sh | shell | bash | zsh <command>`"
    )
    @commands.is_owner()
    async def shell(self, ctx, *, command):
        output = getoutput(command)
        if output == '':
            output = 'No output available'
        embed = Embed(description = output, color = self.bot.color)
        await ctx.send(embed = embed)

    @shell.error
    async def run_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            await ctx.send(f"You don't have permission, {ctx.author.mention}")
        else:
            raise error


def setup(bot):
    bot.add_cog(miia(bot))
