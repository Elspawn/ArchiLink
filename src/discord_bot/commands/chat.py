from utils.commands import get_current_player

def setup(bot) :
    
    @bot.command(name='say', help='Send a message to the MultiWorld Client')
    async def say(ctx, *, message: str):
        session, discord_profil = await get_current_player(bot, ctx)
        if session is None or discord_profil is None :
            return
        player = discord_profil.current_slot
        message_to_send = f"[{player.player_name}] {message}"
        bot.custom_logger.info(f"Sending message to MultiWorld Client: {message_to_send}")
        await session.bot_client.say_messages(message_to_send)
