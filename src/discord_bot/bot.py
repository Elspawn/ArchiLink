import discord
from discord.ext import commands
from discord_bot import commands as cmd
from discord_bot.events import setup_events
import os

def create_bot(logger) :
    # Create a single bot instance that will be used for all worlds, and will route messages to the correct world based on the channel they come from

    intents = discord.Intents.default()
    intents.message_content = True
    intents.reactions = True
    
    bot = commands.Bot(command_prefix=os.getenv("DISCORD_COMMAND_PREFIX"), intents=intents)
    bot.custom_logger = logger
    bot.app_token = os.getenv("DISCORD_APP_TOKEN")
    bot.remove_command('help')
    cmd.setup(bot)
    setup_events(bot)
    return bot