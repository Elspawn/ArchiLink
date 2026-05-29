import discord
from discord.ext import commands
from discord_bot.commands import setup_commands
from discord_bot.admin_commands import setup_admin_commands

def create_bot(config, logger) :
    # Create a single bot instance that will be used for all worlds, and will route messages to the correct world based on the channel they come from

    intents = discord.Intents.default()
    intents.message_content = True
    intents.reactions = True
    
    bot = commands.Bot(command_prefix=config["DiscordConfig"]["command_prefix"], intents=intents)
    bot.custom_logger = logger
    bot.app_token = config["DiscordConfig"]["app_token"]
    bot.admins = config["DiscordConfig"]["admin_ids"]
    if bot.admins == [] or bot.admins is None:
        bot.custom_logger.warning("No admin IDs specified in config. Everyone will be able to use admin commands.")
    bot.config = config
    bot.remove_command('help')
    setup_commands(bot)
    setup_admin_commands(bot)
    return bot