from utils.ansi import AnsiTable, AnsiText
from utils.commands import get_current_player

async def send_new_items(bot, session, player) :
    user = await bot.fetch_user(player.discord_id)
    if user.dm_channel is None :
        await user.create_dm() 
    if player is None :
        session.bot_client.logger.error(f"Player with discord id {player.discord_id} not found.")
        return
    elif len(player.new_items) == 0 :
        session.bot_client.logger.info(f"Player found : {player.player_name} but no new items to send.")
        # DM player if no new items, to avoid spamming the channel
        await user.dm_channel.send("You have not received any new items since the last time you checked.")
    else :
        session.bot_client.logger.info(f"Player found : {player.player_name} with {len(player.new_items)} new items to send.")
        async with session.bot_client.lock:
            items = list(player.new_items)
            player.new_items.clear()
            
        table = AnsiTable(title="New Items Received", headers=["You", "Item", "Sender", "Location"])
        for item in items :
            table.add_row(
                AnsiText(player.player_name, color=player.color), 
                AnsiText(item.item_name),
                AnsiText(item.player_sending.player_name, color=item.player_sending.color),
                AnsiText(item.location_name)
            )
        await table.send(user.dm_channel)

def setup(bot):
    
    @bot.command(name='new')
    async def new(ctx, all: str = None) :
        session, discord_profil = await get_current_player(bot, ctx)
        if session is None or discord_profil is None :
            return
        if all == "all" :
            for player in discord_profil.slots :
                await send_new_items(bot, session, player)
        else :
            current_player = discord_profil.current_slot
            await send_new_items(bot, session, current_player)

    @bot.command(name='enableping')
    async def enableping(ctx) :
        session, discord_profil = await get_current_player(bot, ctx)
        if session is None or discord_profil is None :
            return
        registered_players = [p.player_name for p in discord_profil.slots] if discord_profil else []
        if registered_players == [] :
            await ctx.send(f"You are not registered to any player. Please register first usign `!register <name>` command.")
        else :
            for player in discord_profil.slots :
                player.allow_ping = True
            await ctx.send(f"This discord bot will now ping you when another player finds an item relevant to your todo list.")

    @bot.command(name='disableping')
    async def disableping(ctx) :
        session, discord_profil = await get_current_player(bot, ctx)
        if session is None or discord_profil is None :
            return
        registered_players = [p.player_name for p in discord_profil.slots] if discord_profil else []
        if registered_players == [] :
            await ctx.send(f"You are not registered to any player. Please register first usign `!register <name>` command.")
        else :
            for player in discord_profil.slots :
                player.allow_ping = False
            await ctx.send(f"This discord bot won't bother you anymore with pings")
            
    @bot.command(name='enablenewitems')
    async def enablenewitems(ctx) :
        session, discord_profil = await get_current_player(bot, ctx)
        if session is None or discord_profil is None :
            return
        registered_players = [p.player_name for p in discord_profil.slots] if discord_profil else []
        if registered_players == [] :
            await ctx.send(f"You are not registered to any player. Please register first usign `!register <name>` command.")
        else :
            for player in discord_profil.slots :
                player.get_new_items_auto = True
            await ctx.send(f"You will now receive new items automatically in DM as soon as you start playing.")
            
    @bot.command(name='disablenewitems')
    async def disablenewitems(ctx) :
        session, discord_profil = await get_current_player(bot, ctx)
        if session is None or discord_profil is None :
            return
        registered_players = [p.player_name for p in discord_profil.slots] if discord_profil else []
        if registered_players == [] :
            await ctx.send(f"You are not registered to any player. Please register first usign `!register <name>` command.")
        else :
            for player in discord_profil.slots :
                player.get_new_items_auto = False
            await ctx.send(f"You will now have to use `!new` command to check for new items received since the last time you checked.")
