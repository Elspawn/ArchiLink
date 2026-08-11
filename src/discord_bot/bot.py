import discord
from discord.ext import commands
from discord_bot import commands as cmd
from discord_bot.events import setup_events
import os

class MultiworldBot(commands.Bot):
    async def setup_hook(self):
        await self.load_extension("discord_bot.commands")
        await self.tree.sync()

def create_bot(logger):

    intents = discord.Intents.default()
    intents.message_content = True
    intents.reactions = True
    bot = MultiworldBot(command_prefix=os.getenv("DISCORD_COMMAND_PREFIX"), intents=intents)
    bot.custom_logger = logger
    bot.app_token = os.getenv("DISCORD_APP_TOKEN")
    setup_events(bot)
    return bot