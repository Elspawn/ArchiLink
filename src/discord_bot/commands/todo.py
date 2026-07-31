
from utils.commands import get_current_player
from utils.name_finder import resolve_item
from discord_bot.texts_flavors import get_empty_todolist_flavor, get_todolist_flavor, get_clear_todolist_flavor, get_wishlist_flavor
from utils.ansi import AnsiTable, AnsiText

def setup(bot):
    
    @bot.command(name="wish", description="Add an item to your wishlist list. Only if item has been hinted before.")
    async def wish(ctx, *, item_name: str) :
        session, discord_profil = await get_current_player(bot, ctx)
        if session is None or discord_profil is None :
            return
        player = discord_profil.current_slot
        hints = await session.bot_client.retrieve_available_hints(player.player_slot)
        hints_to_get = hints["to_get"]
        wishlist = []
        for other_player in session.bot_client.player_db.get_all_players() :
            async with session.bot_client.lock:
                for item in other_player.todolist:
                    if item.player_recieving.player_name == player.player_name :
                        wishlist.append(item)
        # Remove items from hints_to_get that are already in wishlist
        # Remove if item_name and location_name are the same
        hints_to_get = [item for item in hints_to_get if not any(item.item_name == w.item_name and item.location_name == w.location_name for w in wishlist)]
        item = resolve_item(item_name, hints_to_get)
        if item is not None :
            player_sending = item.player_sending
            async with session.bot_client.lock:
                player_sending.todolist.append(item)
            await ctx.send(f"Item {item.item_name} added to your wishlist.")
        else :
            await ctx.send(f"Item {item_name} not found in your hint list. Please check the spelling and try again. You can use `!allhints` command to see all the items you can add to your wishlist.")
        
    @bot.command(name='todo')
    async def todo(ctx) :
        session, discord_profil = await get_current_player(bot, ctx)
        if session is None or discord_profil is None :
            return
        player = discord_profil.current_slot
        if player.todolist == [] :
            flavor = get_empty_todolist_flavor()
            await ctx.send(f"{player.player_name} : {flavor}")
        else :
            bot.custom_logger.info(f"Player found : {player.player_name} with {len(player.todolist)} items in todo list.")
            async with session.bot_client.lock:
                items = list(player.todolist)
            flavor = get_todolist_flavor()
            table = AnsiTable(title=get_todolist_flavor(), headers=["For", "Item", "Location"])
            for item in items :
                table.add_row(
                    AnsiText(item.player_recieving.player_name, color=item.player_recieving.color), 
                    AnsiText(item.item_name),
                    AnsiText(item.location_name)
                )
            await table.send(ctx)
 
    @bot.command(name="clearTodo")
    async def clear_todo(ctx) :
        session, discord_profil = await get_current_player(bot, ctx)
        if session is None or discord_profil is None :
            return
        player = discord_profil.current_slot
        async with session.bot_client.lock:
            player.todolist.clear()
        msg = get_clear_todolist_flavor()
        await ctx.send(msg)

    @bot.command(name='removeTodo')
    async def remove_todo(ctx, *, item_name: str) :
        session, discord_profil = await get_current_player(bot, ctx)
        if session is None or discord_profil is None :
            return
        player = discord_profil.current_slot
        async with session.bot_client.lock:
            item_to_remove = None
            for item in player.todolist :
                if item.item_name.lower() == item_name.lower() :
                    item_to_remove = item
                    break
            if item_to_remove is None :
                await ctx.send(f"Item {item_name} not found in your todo list.")
            else :
                player.todolist.remove(item_to_remove)
                await ctx.send(f"Item {item_name} removed from your todo list.")

    @bot.command(name='wishlist')
    async def wishlist(ctx) :
        session, discord_profil = await get_current_player(bot, ctx)
        if session is None or discord_profil is None :
            return
        player = discord_profil.current_slot
        session.bot_client.logger.info(f"Wishlist command called for player {player.player_name}")
        wishlist = []
        for other_player in session.bot_client.player_db.get_all_players() :
            async with session.bot_client.lock:
                for item in other_player.todolist:
                    if item.player_recieving.player_name == player.player_name :
                        wishlist.append(item)
        if wishlist == [] :
            await ctx.send(f"You do not have any item in your wishlist.")
        else :
            flavor = get_wishlist_flavor()
            table = AnsiTable(title=flavor, headers=["From", "Item", "Location"])
            for item in wishlist :
                table.add_row(
                    AnsiText(item.player_sending.player_name, color=item.player_sending.color), 
                    AnsiText(item.item_name),
                    AnsiText(item.location_name)
                )
            await table.send(ctx)