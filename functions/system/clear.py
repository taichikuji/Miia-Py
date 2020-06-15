import discord
from discord.ext import commands


class miia(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="clear",
                      brief="Remove one or more messages",
                      description="Remove one or more messages previously, by default it removes 2 messages")
    @commands.has_guild_permissions(manage_messages=True)
    async def clear(self, ctx, amount=2):
        await ctx.channel.purge(limit=amount)

    @clear.error
    async def run_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send(f"You don't have permission, {ctx.author.mention}")
        else:
            raise error


def setup(bot):
    bot.add_cog(miia(bot))
