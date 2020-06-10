import discord
import os
import config
from discord.ext import commands
import glob

# Starts Miia
bot = commands.Bot(command_prefix=commands.when_mentioned_or('?'),
                   description='O-oi, what are you looking at?')

# Load modules
# Takes 0.010036945343017578 seconds to load 2 modules
# So it's commented out
# for dirpath, dirs, files in os.walk('functions'):
#     for functions in files:
#         pyfile = os.path.join(dirpath, functions)
#         if pyfile.endswith(".py"):
#             module = pyfile.replace('.py', '').replace(os.sep, '.')
#             bot.load_extension(module)
#             print(f'Module {module} loaded!')

# Takes 0.007251739501953125 seconds to load 2 modules
# So it's being chosen as the best way to load modules on startup
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
    await bot.change_presence(activity=display)


@commands.command(name="close",
                  hidden=False,
                  brief="Shutdown the bot")
@commands.is_owner()
# This closes the bot completely, be careful when executing it!
# It is highly suggested that you create a systemd job that restarts the bot automatically
async def close(self, ctx):
    await ctx.send(":snake: Going to sleep!")
    await ctx.bot.close()

bot.run(config.token, bot=True, reconnect=True)
