from world.world_manager import WorldManager
from world.world import WorldConfigSelection
from utils.config import check_config
from discord_bot.bot import create_bot
from dotenv import load_dotenv
import discord
import asyncio
import logging
import json
import os

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("ArchiLink")
# Put discord logger to warning to avoid cluttering the console with discord debug messages
logging.getLogger("discord").setLevel(logging.WARNING) 

async def main():
    # Load .env file
    load_dotenv()
    
    datadir = os.getenv("DATA_DIRECTORY", "data")
    os.makedirs(datadir, exist_ok=True)
    discord_bot = create_bot(logger)
    world_manager = WorldManager(discord_bot, logger, datadir)
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
        valid = check_config(data)
        if not valid :
            await ctx.send("Invalid configuration, world creation cancelled. Please try again.")
            return
        
        # Create a unique world ID 
        dt = discord.utils.utcnow()
        world_id = f"{ctx.author.id}_{int(discord.utils.time_snowflake(dt))}"
        world_data_dir = os.path.join(datadir, world_id)
        os.makedirs(world_data_dir, exist_ok=True)
        try:
            await world_manager.create_world(world_data_dir, data)
            await ctx.send(f"World created. You can now use the commands to interact with your world in the configured channel.")
        except Exception as e:
            logger.error(f"Error creating world: {e}")
            await ctx.send(f"An error occurred while creating the world. Please try again later.")
    
    try :
        await asyncio.gather(
            asyncio.create_task(discord_bot.start(os.getenv("DISCORD_APP_TOKEN")))
        )
    
    finally :
        logger.info("Shutting down, stopping all worlds...")
        await world_manager.stop_all_worlds()
        await discord_bot.close()
        
    
if __name__ == "__main__":
    asyncio.run(main())