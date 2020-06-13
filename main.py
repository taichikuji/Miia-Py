import discord
import os
import config
from discord.ext import commands
import glob
import aiohttp

# Starts Miia
bot = commands.Bot(command_prefix=commands.when_mentioned_or('?'),
                   description='O-oi, what are you looking at?')


async def create_aiohttp_session(bot):
    bot.session = aiohttp.ClientSession(loop=bot.loop)

for functions in glob.iglob('functions/**/*.py', recursive=True):
    module = functions.replace('.py', '').replace(os.sep, '.')
    print(f'Loading module {module}')
    bot.load_extension(module)


@bot.event
async def on_ready():
    # Shows text event that bot is starting
    print(f'Miia Online! : {bot.user.name} - {bot.user.id}')
    display = discord.Activity(
        name="?help", type=discord.ActivityType.listening)
    bot.loop.create_task(create_aiohttp_session(bot))
    await bot.change_presence(activity=display)


bot.run(config.token, bot=True, reconnect=True)
