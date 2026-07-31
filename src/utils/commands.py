async def get_current_player(bot, ctx):
    session = await check_world_channel(bot, ctx.channel.id)
    if session is None:
        return None, None

    profile = session.bot_client.discord_db.get_discord_profile(ctx.author.id)
    if profile is None or profile.current_slot is None or profile.slots == []:
        await ctx.send("You are not registered to any player. Please register first using `!register <player_name>` command.")
        return session, None

    return session, profile

async def check_world_channel(bot, channel_id) :
    session = bot.world_manager.get_world_from_channel(channel_id)
    if session is None :
        bot.custom_logger.warning(f"Received message from channel {channel_id} but no world is associated to this channel.")
        await bot.get_channel(channel_id).send("This channel is not associated to any world. Please use the commands in the correct channel or create a new world with !newWorld.")
        return None
    return session