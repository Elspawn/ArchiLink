import asyncio
from archipelago.bot_client import BotClient
from discord_bot.commands import send_new_items

class WorldManager:
    def __init__(self, discord_bot, logger, datadir="./data"):
        self.worlds = {}  # world_id -> WorldSession
        self.bot = discord_bot
        self.logger = logger
        self.datadir = datadir
        
    async def create_world(self, world_id, config):
        message_queue = asyncio.Queue()
        ping_queue = asyncio.Queue()
        dm_queue = asyncio.Queue()

        bot_client = BotClient(
            config = config,
            message_queue = message_queue,
            ping_queue = ping_queue,
            dm_queue = dm_queue,
            logger = self.logger,
            datadir = self.datadir
        )
        
        session = WorldSession(
            bot = self.bot,
            bot_client = bot_client,
            normal_channel_id = config["DiscordConfig"]["normal_channel_id"],
            ping_channel_id = config["DiscordConfig"]["ping_channel_id"],
            message_queue = message_queue,
            ping_queue = ping_queue,
            dm_queue = dm_queue,
            logger = self.logger
        )
        
        await session.start()
        session.tasks.append(asyncio.create_task(bot_client.run()))
        self.worlds[world_id] = session
        return session
    
    async def stop_world(self, world_id: str):
        session = self.worlds.get(world_id)
        if not session:
            return
        await session.bot_client.stop()
        await session.stop()
        del self.worlds[world_id]
        
    def get_world_from_channel(self, channel_id: int):
        for _ , session in self.worlds.items():
            if channel_id == session.normal_channel_id or channel_id == session.ping_channel_id:
                return session
        return None
        
class WorldSession:

    def __init__(
        self,
        bot,
        bot_client,
        normal_channel_id,
        ping_channel_id,
        message_queue,
        ping_queue,
        dm_queue,
        logger
    ):
        self.bot = bot
        self.bot_client = bot_client
        self.logger = logger
        self.normal_channel_id = normal_channel_id
        self.ping_channel_id = ping_channel_id
        self.message_queue = message_queue
        self.ping_queue = ping_queue
        self.dm_queue = dm_queue
        self.tasks = []
    
    async def discord_sender(self, channel, queue):
        while True:
            msg = await queue.get()
            try:
                await channel.send(msg)
            except Exception as e:
                self.logger.exception(e)
                
    async def dm_sender(self):
        while True:
            player, msg = await self.dm_queue.get()
            try:
                if player.discord_id:
                    if msg == "new_items":
                        await send_new_items(self.bot, self, player.discord_id)
                    else:
                        self.logger.warning(f"Player {player.player_name} has no discord id")
            except Exception as e:
                self.logger.exception(e)
                
    async def start(self):
        normal_channel = self.bot.get_channel(self.normal_channel_id)
        if normal_channel:
            self.tasks.append(asyncio.create_task(self.discord_sender(normal_channel, self.message_queue)))
            
        if self.ping_channel_id:
            ping_channel = self.bot.get_channel(self.ping_channel_id)
            if ping_channel:
                self.tasks.append(asyncio.create_task(self.discord_sender(ping_channel, self.ping_queue)))

        self.tasks.append(asyncio.create_task(self.dm_sender()))
        
    async def stop(self):
        for task in self.tasks:
            task.cancel()
        await asyncio.gather(*self.tasks, return_exceptions=True)