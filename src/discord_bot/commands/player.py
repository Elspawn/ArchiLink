from utils.commands import check_world_channel, get_current_player
from utils.name_finder import resolve_player_name
from models.discord_profil import DiscordProfile


def setup(bot):
    
    @bot.command(name='players')
    async def players(ctx):
        session = await check_world_channel(bot, ctx.channel.id)
        if session is None :
            return
        players = session.bot_client.player_db.get_all_players_names()
        await ctx.send(f"Players in this multiworld are : {', '.join(players)}")
    
    @bot.command(name='register')
    async def register(ctx, *, player_name: str) :
        session = await check_world_channel(bot, ctx.channel.id)
        if session is None :
            return
        # Check if player name is valid
        player_name = resolve_player_name(player_name, session.bot_client.player_db.get_all_players_names())
        if player_name is None :
            await ctx.send(f"Player name {player_name} not found. Please check the spelling and try again.\n\
Available player names are : {', '.join(session.bot_client.player_db.get_all_players_names())}")
        elif session.bot_client.player_db.get_player_by_name(player_name).discord_id is not None :
            player = session.bot_client.player_db.get_player_by_name(player_name)
            if player.discord_id == ctx.author.id :
                await ctx.send(f"You are already registered to player {player_name}.")
            else :
                await ctx.send(f"Player {player_name} is already registered by {player.discord_id}.\nIf you think this is an error, please contact the administrator.")
        else :
            discord_profil = session.bot_client.discord_db.get_discord_profile(ctx.author.id)
            if discord_profil is None :
                discord_profil = DiscordProfile(ctx.author.name, ctx.author.id)
            player = session.bot_client.player_db.get_player_by_name(player_name)
            # Link player and discord profile
            discord_profil.slots.append(player)
            discord_profil.current_slot = player
            session.bot_client.discord_db.add_discord_profile(discord_profil)
            session.bot_client.player_db.set_discord_id(player, discord_profil.id)
            await ctx.send(f"Player {player_name} successfully registered to discord user {ctx.author.name}#{ctx.author.discriminator}.\n\
You are currently registered to : {', '.join([p.player_name for p in discord_profil.slots])}")

    @bot.command(name='unregister')
    async def unregister(ctx, *, player_name: str = None) :
        session, discord_profil = await get_current_player(bot, ctx)
        if session is None or discord_profil is None :
            return
        registered_players = [p.player_name for p in discord_profil.slots] if discord_profil else []
        if registered_players == [] :
            await ctx.send(f"You are not registered to any player. Please register first using `!register <player_name>` command.")
            return
        player_name = resolve_player_name(player_name, registered_players) if player_name else None
        if player_name is not None and player_name not in registered_players :
            await ctx.send(f"You are not registered to player {player_name}. You are currently registered to : {', '.join(registered_players)}.")
        elif player_name is not None and player_name in registered_players :
            player = session.bot_client.player_db.get_player_by_name(player_name)
            # Unlink player and discord profile
            discord_profil.slots.remove(player)
            session.bot_client.player_db.set_discord_id(player, None)
            await ctx.send(f"Player {player_name} successfully unregistered from discord user {ctx.author.name}#{ctx.author.discriminator}.")
        else :
            # Unregister from all players
            for player in discord_profil.slots:
                session.bot_client.player_db.set_discord_id(player, None)
            discord_profil.slots.clear()
            await ctx.send(f"All players successfully unregistered from discord user {ctx.author.name}#{ctx.author.discriminator}.")


    @bot.command(name='current')
    async def current(ctx) :
        session, discord_profil = await get_current_player(bot, ctx)
        if session is None or discord_profil is None :
            return
        else :
            current_player = discord_profil.current_slot
            await ctx.send(f"You are currently tracking {current_player.player_name}. Use `!switch` command to switch to another player if you are registered to multiple players.")

    @bot.command(name='switch')
    async def switch(ctx, *, player_name: str = None) :
        session, discord_profil = await get_current_player(bot, ctx)
        if session is None or discord_profil is None :
            return
        if player_name == None :
            # Switch to next slot in the list
            current_player = discord_profil.current_slot
            if current_player is None :
                discord_profil.current_slot = discord_profil.slots[0]
                await ctx.send(f"Successfully switched to player {discord_profil.slots[0].player_name}.")
            else :
                current_index = discord_profil.slots.index(current_player)
                next_index = (current_index + 1) % len(discord_profil.slots)
                discord_profil.current_slot = discord_profil.slots[next_index]
                await ctx.send(f"Successfully switched to player {discord_profil.slots[next_index].player_name}.")
        elif player_name not in [p.player_name for p in discord_profil.slots] :
            await ctx.send(f"You are not registered to player {player_name}. You are currently registered to : {', '.join([p.player_name for p in discord_profil.slots])}.")
        else :
            player = session.bot_client.player_db.get_player_by_name(player_name)
            discord_profil.current_slot = player
            await ctx.send(f"Successfully switched to player {player_name}.")

    @bot.command(name='setcolor', help='Set your preferred color.')
    async def setcolor(ctx, color: str):
        session, discord_profil = await get_current_player(bot, ctx)
        if session is None or discord_profil is None :
            return
        player = discord_profil.current_slot
        colors = {
            "black": "\u001b[30m",
            "red": "\u001b[31m",
            "green": "\u001b[32m",
            "yellow": "\u001b[33m",
            "blue": "\u001b[34m",
            "magenta": "\u001b[35m",
            "cyan": "\u001b[36m",
            "white": "\u001b[37m",
        }
        if color.lower() not in colors:
            await ctx.send(f"Invalid color : {color}. Please choose from: black, red, green, yellow, blue, magenta, cyan, white.")
            return
        player.color = colors[color.lower()]
        player.name_colored = f"{player.color}{player.player_name}\u001b[0m"
        await ctx.send(f"Your preferred color has been set to {color}.")
