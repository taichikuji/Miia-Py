import discord
import os
import config
from discord.ext import commands
import glob
# start the bot
bot = commands.Bot(command_prefix=commands.when_mentioned_or('?'),
                   description='O-oi, what are you looking at?')

# load modules
# takes 0.010036945343017578 seconds to load 2 modules
# so it's commented out
# for dirpath, dirs, files in os.walk('functions'):
#     for functions in files:
#         pyfile = os.path.join(dirpath, functions)
#         if pyfile.endswith(".py"):
#             module = pyfile.replace('.py', '').replace(os.sep, '.')
#             bot.load_extension(module)
#             print(f'Module {module} loaded!')

# takes 0.007251739501953125 seconds to load 2 modules
# so it's being chosen as the best way to load modules on startup
for functions in glob.iglob('functions/**/*.py', recursive=True):
    module = functions.replace('.py', '').replace(os.sep, '.')
    print(f'Loading module {module}')
    bot.load_extension(module)


@bot.event
async def on_ready():
    # shows text event that bot is starting
    print(f'Miia Online! : {bot.user.name} - {bot.user.id}')
    display = discord.Activity(
        name="?help", type=discord.ActivityType.listening)
    await bot.change_presence(activity=display)

bot.run(config.token, bot=True, reconnect=True)
