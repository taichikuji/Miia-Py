from time import localtime, strftime

from discord.ext import commands


class miia(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name="load",
        brief="Load an extension",
        description="Load an extension",
        usage="`load <folder.file>`",
    )
    @commands.is_owner()
    async def load(self, ctx, *, extension):
        try:
            self.bot.load_extension(f"functions.{extension}")
            print(
                f"{extension} loaded at {strftime('%A, %d %b %Y, %I:%M:%S %p', localtime())}."
            )
            description = ":o: It's working! The module is up and running!"
        except commands.ExtensionAlreadyLoaded:
            description = (
                ":ok_hand: Don't worry about it. The module is already loaded!"
            )
        except commands.ExtensionNotFound:
            description = (
                ":x: Uh oh... This is weird, it seems i can't find the module?"
            )
        except commands.ExtensionFailed:
            description = ":x: Uh oh... I could find the module, but it gives me an error. Maybe try looking at the logs or asking my darling?"
        except commands.NoEntryPointError:
            description = ":x: This module can't load because it doesn't have a setup function. Try adding it and load it again!"
        await ctx.send(description)

    @commands.command(
        name="unload",
        brief="Unload an extension",
        description="Unload an extension",
        usage="`unload <folder.file>`",
    )
    @commands.is_owner()
    async def unload(self, ctx, *, extension):
        try:
            self.bot.unload_extension(f"functions.{extension}")
            description = ":o: It's working! The module is disconnected!"
        except commands.ExtensionNotLoaded:
            description = (
                ":ok_hand: Don't worry about it. The module is already unloaded!"
            )
        await ctx.send(description)

    @commands.command(
        name="reload",
        brief="Reload an extension",
        description="Reload an extension",
        usage="`reload <folder.file>`",
    )
    @commands.is_owner()
    async def reload(self, ctx, *, extension):
        try:
            self.bot.reload_extension(f"functions.{extension}")
            print(
                f"{extension} reloaded at {strftime('%A, %d %b %Y, %I:%M:%S %p', localtime())}."
            )
            description = (
                ":o: It's working! The module has been restarted successfully!"
            )
        except commands.ExtensionNotLoaded:
            description = ":x: Uh oh... I couldn't reload this module"
        except commands.ExtensionNotFound:
            description = (
                ":x: Uh oh... This is weird, it seems i can't find the module?"
            )
        except commands.ExtensionFailed:
            description = ":x: Uh oh... I could find the module, but it gives me an error. Maybe try looking at the logs or asking my darling?"
        except commands.NoEntryPointError:
            description = ":x: This module can't load because it doesn't have a setup function. Try adding it and load it again!"
        await ctx.send(description)


def setup(bot):
    bot.add_cog(miia(bot))
