async def get_current_player(bot, channel_id, author):
    session = await check_world_channel(bot, channel_id)
    if session is None:
        return None, None

    profile = session.bot_client.discord_db.get_discord_profile(author.id)
    if profile is None or profile.current_slot is None or profile.slots == []:
        return session, None
    return session, profile

async def check_world_channel(bot, channel_id) :
    session = bot.world_manager.get_world_from_channel(channel_id)
    if session is None :
        bot.custom_logger.warning(f"Received message from channel {channel_id} but no world is associated to this channel.")
        await bot.get_channel(channel_id).send("This channel is not associated to any world. Please use the commands in the correct channel or create a new world with !newWorld.")
        return None
    return session