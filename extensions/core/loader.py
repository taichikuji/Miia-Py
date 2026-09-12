import logging
from time import localtime, strftime
from typing import TYPE_CHECKING

from discord import Interaction, app_commands
from discord.ext import commands

from extensions.core.analytics import mark_app_command_failed

if TYPE_CHECKING:
    from main import Sakamoto

logger = logging.getLogger(__name__)


class LoaderCog(commands.Cog):
    """Cog for loading, unloading, and reloading extensions."""

    def __init__(self, bot: Sakamoto):
        self.bot = bot

    @app_commands.command(name="load", description="Load an extension.")
    @app_commands.describe(
        extension="Extension path relative to `extensions.`, such as `audio.music`."
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def load(self, interaction: Interaction, extension: str) -> None:
        """Load a bot extension."""
        succeeded = True
        try:
            await self.bot.load_extension(f"extensions.{extension}")
            logger.info(
                "%s loaded at %s.",
                extension,
                strftime("%A, %d %b %Y, %I:%M:%S %p", localtime()),
            )
            description = (
                f":white_check_mark: Loaded extension '{extension}' successfully."
            )
        except commands.ExtensionAlreadyLoaded:
            description = (
                f":information_source: Extension '{extension}' is already loaded."
            )
        except commands.ExtensionNotFound:
            succeeded = False
            description = f":x: Extension '{extension}' not found."
        except commands.ExtensionFailed:
            succeeded = False
            description = f":x: Extension '{extension}' failed to load due to an error."
        except commands.NoEntryPointError:
            succeeded = False
            description = f":x: Extension '{extension}' does not have a setup function."
        except Exception as e:
            succeeded = False
            description = f":x: An unexpected error occurred: {e}"
            logger.error(description)
        await interaction.response.send_message(description, ephemeral=True)
        if not succeeded:
            mark_app_command_failed(interaction)

    @app_commands.command(name="unload", description="Unload an extension.")
    @app_commands.describe(extension="Loaded extension path relative to `extensions.`.")
    @app_commands.checks.has_permissions(administrator=True)
    async def unload(self, interaction: Interaction, extension: str) -> None:
        """Unload a bot extension."""
        succeeded = True
        try:
            await self.bot.unload_extension(f"extensions.{extension}")
            description = (
                f":white_check_mark: Unloaded extension '{extension}' successfully."
            )
        except commands.ExtensionNotLoaded:
            description = f":information_source: Extension '{extension}' is not loaded."
        except Exception as e:
            succeeded = False
            description = f":x: An unexpected error occurred: {e}"
            logger.error(description)
        await interaction.response.send_message(description, ephemeral=True)
        if not succeeded:
            mark_app_command_failed(interaction)

    @app_commands.command(name="reload", description="Reload an extension.")
    @app_commands.describe(extension="Loaded extension path relative to `extensions.`.")
    @app_commands.checks.has_permissions(administrator=True)
    async def reload(self, interaction: Interaction, extension: str) -> None:
        """Reload a bot extension."""
        succeeded = True
        try:
            await self.bot.reload_extension(f"extensions.{extension}")
            logger.info(
                "%s reloaded at %s.",
                extension,
                strftime("%A, %d %b %Y, %I:%M:%S %p", localtime()),
            )
            description = (
                f":white_check_mark: Reloaded extension '{extension}' successfully."
            )
        except commands.ExtensionNotLoaded:
            succeeded = False
            description = f":x: Extension '{extension}' is not loaded."
        except commands.ExtensionNotFound:
            succeeded = False
            description = f":x: Extension '{extension}' not found."
        except commands.ExtensionFailed:
            succeeded = False
            description = (
                f":x: Extension '{extension}' failed to reload due to an error."
            )
        except commands.NoEntryPointError:
            succeeded = False
            description = f":x: Extension '{extension}' does not have a setup function."
        except Exception as e:
            succeeded = False
            description = f":x: An unexpected error occurred: {e}"
            logger.error(description)
        await interaction.response.send_message(description, ephemeral=True)
        if not succeeded:
            mark_app_command_failed(interaction)

    @load.error
    @unload.error
    @reload.error
    async def on_loader_error(
        self, interaction: Interaction, error: app_commands.AppCommandError
    ) -> None:
        """Handle errors for the loader commands."""
        if isinstance(error, app_commands.errors.MissingPermissions):
            await interaction.response.send_message(
                ":x: You need Administrator permissions to run this command.",
                ephemeral=True,
            )
        else:
            logger.error("Unexpected error in command: %s", error)


async def setup(bot: Sakamoto):
    """Add the LoaderCog to the bot."""
    await bot.add_cog(LoaderCog(bot))
