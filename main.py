from glob import iglob
from os import sep

from config import TOKEN
from aiohttp import ClientSession
from discord import Activity, ActivityType, Intents
from discord.ext import commands


class miiapy(commands.AutoShardedBot):
    def __init__(self):
        super().__init__(
            command_prefix=commands.when_mentioned_or("?"),
            description="O-oi, what are you looking at?",
            case_insensitive=True,
            intents=Intents.all(),
        )
        self.BOT_TOKEN = TOKEN
        self.session = None
        self.color = 0xFF3351
        self.owner_id = 199632174603829249

        for functions in iglob("functions/**/*.py", recursive=True):
            module = functions.replace(".py", "").replace(sep, ".")
            try:
                self.load_extension(module)
                print(f"Module {module} loaded")
            except ImportError:
                print(f"Failed to import {module}")
            except commands.errors.ExtensionFailed:
                print(f"{module} extension failed")
            except Exception:
                print(f"Unexpected exception related with {module}")

    async def create_aiohttp_session(self):
        self.session = ClientSession(loop=self.loop)
        # Created aiohttp ClientSession

    async def on_ready(self):
        display = Activity(name="?help", type=ActivityType.listening)
        self.loop.create_task(self.create_aiohttp_session())
        # Create ClientSession task set
        await self.change_presence(activity=display)
        print(f"Miia Online! : {self.user.name} - {self.user.id}")

    async def close(self):
        await self.session.close()
        await super().close()

    def run(self):
        try:
            super().run(self.BOT_TOKEN, bot=True, reconnect=True)
        except TypeError:
            print("An unexpected keyword argument was received.")
        except Exception:
            print("Uh oh something broke, the bot can't start!")


if __name__ == "__main__":
    miiapy().run()
