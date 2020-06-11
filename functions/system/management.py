import discord
from discord.ext import commands


class management(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="close",
                      aliases=['shutdown', 'sleep'],
                      brief="Shutdown the bot")
    @commands.is_owner()
    # This closes the bot completely, be careful when executing it!
    # It is highly suggested that you create a systemd job that restarts the bot automatically
    async def close(self, ctx):
        await ctx.send(":snake: Going to sleep!")
        await ctx.bot.close()


def setup(bot):
    bot.add_cog(management(bot))
