import discord
import os
import config
from discord.ext import commands
import glob
import aiohttp


class miiapy(commands.AutoShardedBot):
    def __init__(self):
        super().__init__(command_prefix=commands.when_mentioned_or('?'),
                         description='O-oi, what are you looking at?',
                         fetch_offline_members=False)
        self.bot_token = config.token
        self.session = None

        for functions in glob.iglob('functions/**/*.py', recursive=True):
            module = functions.replace('.py', '').replace(os.sep, '.')
            try:
                self.load_extension(module)
                print(f'Module {module} loaded')
            except:
                print(f'Failed to load {module}')

    async def create_aiohttp_session(self):
        self.session = aiohttp.ClientSession(loop=self.loop)
        # Created aiohttp ClientSession

    async def on_ready(self):
        display = discord.Activity(
            name="?help", type=discord.ActivityType.listening)
        self.loop.create_task(self.create_aiohttp_session())
        # Create ClientSession task set
        await self.change_presence(activity=display)
        print(f'Miia Online! : {self.user.name} - {self.user.id}')

    async def close(self):
        await self.session.close()
        await super().close()

    def run(self):
        try:
            super().run(self.bot_token, bot=True, reconnect=True)
        except:
            print("Uh oh something broke, the bot can't start!")


if __name__ == '__main__':
    miiapy().run()
