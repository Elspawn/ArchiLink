def setup_events(bot):
    @bot.event
    async def on_ready():
        if not bot.world_manager.loaded:
            await bot.world_manager.load_worlds()
            bot.world_manager.loaded = True
            bot.custom_logger.info(f"{len(bot.world_manager.worlds)} worlds loaded, ready to accept commands.")