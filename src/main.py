from world.world_manager import WorldManager
from world.world import WorldConfigSelection
from archipelago.bot_client import BotClient
from discord_bot.bot import create_bot
from utils.config import load_config
import discord
import asyncio
import logging
import json

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("ArchiLink")
# Put discord logger to warning to avoid cluttering the console with discord debug messages
logging.getLogger("discord").setLevel(logging.WARNING) 

async def main():
    config = load_config() # TODO : adapt to new config structure
    
    discord_bot = create_bot(config, logger)
    world_manager = WorldManager(discord_bot, logger)
    discord_bot.world_manager = world_manager # Give the bot a reference to the world manager so it can route messages to the correct world based on the channel they come from
    
    # Add command to create a new world :
    @discord_bot.command(name="newWorld", help="Create a new world. Usage: !newWorld")
    async def new_world(ctx):
        data = {}
        view = WorldConfigSelection(author=ctx.author, data=data)
        await ctx.send(
            "Click to configure your world",
            view=view
        )
        await view.wait()
        if data == {}: # TODO check against reference config to make sure it's not just empty but actually invalid
            await ctx.send("Configuration cancelled or timed out.")
            return
        
        # Create a unique world ID 
        dt = discord.utils.utcnow()
        world_id = f"{ctx.author.id}_{int(discord.utils.time_snowflake(dt))}"
        try:
            session = await world_manager.create_world(world_id, data)
            await ctx.send(f"World created. You can now use the commands to interact with your world in the configured channel.")
        except Exception as e:
            logger.error(f"Error creating world: {e}")
            await ctx.send(f"An error occurred while creating the world. Please try again later.")
        
    await asyncio.gather(
        asyncio.create_task(discord_bot.start(config["DiscordConfig"]["app_token"]))
    )
    
if __name__ == "__main__":
    asyncio.run(main())