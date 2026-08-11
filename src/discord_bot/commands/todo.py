
from utils.commands import get_current_player
from utils.name_finder import resolve_item
from discord_bot.texts_flavors import get_empty_todolist_flavor, get_todolist_flavor, get_clear_todolist_flavor, get_wishlist_flavor
from utils.ansi import AnsiTable, AnsiText
from discord.ext import commands
from discord import app_commands
import discord

class TodoCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    async def _wish(self, channel_id, author, item_name) :
        session, discord_profil = await get_current_player(self.bot, channel_id, author)
        if session is None or discord_profil is None :
            return "No session or discord profile found. Please make sure you are in a valid game session and registered."
        player = discord_profil.current_slot
        hints = await session.bot_client.retrieve_available_hints(player.player_slot)
        hints_to_get = hints["to_get"]
        hints_to_send = hints["to_send"]
        wishlist = []
        for other_player in session.bot_client.player_db.get_all_players() :
            async with session.bot_client.lock:
                for item in other_player.todolist:
                    if item.player_recieving.player_name == player.player_name :
                        wishlist.append(item)
        # Remove items from hints_to_get that are already in wishlist
        # Remove if item_name and location_name are the same
        hints_to_get = [item for item in hints_to_get if not any(item.item_name == w.item_name and item.location_name == w.location_name for w in wishlist)]
        hints_to_send = [item for item in hints_to_send if not any(item.item_name == w.item_name and item.location_name == w.location_name for w in wishlist)]
        hints_to_send = [item for item in hints_to_send if item.player_recieving.player_name == player.player_name]
        all_hints = hints_to_get + hints_to_send
        item = resolve_item(item_name, all_hints)
        if item is not None :
            player_sending = item.player_sending
            async with session.bot_client.lock:
                player_sending.todolist.append(item)
            return f"Item {item.item_name} added to your wishlist."
        else :
            return f"Item {item_name} not found in your hint list. Please check the spelling and try again. You can use `!allhints` command to see all the items you can add to your wishlist."
            
    async def _todo(self, channel_id, author) :
        session, discord_profil = await get_current_player(self.bot, channel_id, author)
        if session is None or discord_profil is None :
            return "No session or discord profile found. Please make sure you are in a valid game session and registered."
        player = discord_profil.current_slot
        if player.todolist == [] :
            flavor = get_empty_todolist_flavor()
            return f"{player.player_name} : {flavor}"
        else :
            self.bot.custom_logger.info(f"Player found : {player.player_name} with {len(player.todolist)} items in todo list.")
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
            return await table.format_messages()
            
    async def _clearTodo(self, channel_id, author) :
        session, discord_profil = await get_current_player(self.bot, channel_id, author)
        if session is None or discord_profil is None :
            return "No session or discord profile found. Please make sure you are in a valid game session and registered."
        player = discord_profil.current_slot
        async with session.bot_client.lock:
            player.todolist.clear()
        msg = get_clear_todolist_flavor()
        return msg
        
    async def _removeTodo(self, channel_id, author, item_name) :
        session, discord_profil = await get_current_player(self.bot, channel_id, author)
        if session is None or discord_profil is None :
            return "No session or discord profile found. Please make sure you are in a valid game session and registered."
        player = discord_profil.current_slot
        async with session.bot_client.lock:
            item_to_remove = None
            for item in player.todolist :
                if item.item_name.lower() == item_name.lower() :
                    item_to_remove = item
                    break
            if item_to_remove is None :
                return f"Item {item_name} not found in your todo list."
            else :
                player.todolist.remove(item_to_remove)
                return f"Item {item_name} removed from your todo list."

    async def _wishlist(self, channel_id, author) :
        session, discord_profil = await get_current_player(self.bot, channel_id, author)
        if session is None or discord_profil is None :
            return "No session or discord profile found. Please make sure you are in a valid game session and registered."
        player = discord_profil.current_slot
        session.bot_client.logger.info(f"Wishlist command called for player {player.player_name}")
        wishlist = []
        for other_player in session.bot_client.player_db.get_all_players() :
            async with session.bot_client.lock:
                for item in other_player.todolist:
                    if item.player_recieving.player_name == player.player_name :
                        wishlist.append(item)
        if wishlist == [] :
            return "You do not have any item in your wishlist."
        else :
            flavor = get_wishlist_flavor()
            table = AnsiTable(title=flavor, headers=["From", "Item", "Location"])
            for item in wishlist :
                table.add_row(
                    AnsiText(item.player_sending.player_name, color=item.player_sending.color), 
                    AnsiText(item.item_name),
                    AnsiText(item.location_name)
                )
            return await table.format_messages()
    # ============================================================
    # Prefix commands
    # ============================================================
    
    @commands.command(name="wish", description="Add an item to your wishlist list. Only if item has been hinted before.")
    async def wish(self, ctx, *, item_name: str) :
        message = await self._wish(ctx.channel.id, ctx.author, item_name)
        if message:
            await ctx.send(message)

    @commands.command(name='todo')
    async def todo(self, ctx) :
        messages = await self._todo(ctx.channel.id, ctx.author)
        if isinstance(messages, str):
            await ctx.send(messages)
        else:
            for msg in messages:
                await ctx.send(msg)
                
    @commands.command(name="clearTodo")
    async def clear_todo(self, ctx) :
        message = await self._clearTodo(ctx.channel.id, ctx.author)
        if message:
            await ctx.send(message)

    @commands.command(name='removeTodo')
    async def remove_todo(self, ctx, *, item_name: str) :
        message = await self._removeTodo(ctx.channel.id, ctx.author, item_name)
        if message:
            await ctx.send(message)

    @commands.command(name='wishlist')
    async def wishlist(self, ctx) :
        messages = await self._wishlist(ctx.channel.id, ctx.author)
        if messages is None:
            await ctx.send("An error occurred while retrieving your wishlist. Please try again later.")
        elif isinstance(messages, str):
            await ctx.send(messages)
        else:
            for msg in messages:
                await ctx.send(msg)

    # ============================================================
    # Slash commands
    # ============================================================
    
    @app_commands.command(name="wish", description="Add an item to your wishlist list. Only if item has been hinted before.")
    async def wish_slash(self, interaction: discord.Interaction, item_name: str) :
        message = await self._wish(interaction.channel.id, interaction.user, item_name)
        if message:
            await interaction.response.send_message(message)

    @app_commands.command(name='todo', description="Display your todo list.")
    async def todo_slash(self, interaction: discord.Interaction) :
        messages = await self._todo(interaction.channel.id, interaction.user)
        if messages is None:
            await interaction.response.send_message("An error occurred while retrieving your todo list. Please try again later.")
        elif isinstance(messages, str):
            await interaction.response.send_message(messages)
        else:
            for msg in messages:
                await interaction.response.send_message(msg)

    @app_commands.command(name="cleartodo", description="Clear your todo list.")
    async def clear_todo_slash(self, interaction: discord.Interaction) :
        message = await self._clearTodo(interaction.channel.id, interaction.user)
        if message:
            await interaction.response.send_message(message)

    @app_commands.command(name='removetodo', description="Remove an item from your todo list.")
    async def remove_todo_slash(self, interaction: discord.Interaction, item_name: str) :
        message = await self._removeTodo(interaction.channel.id, interaction.user, item_name)
        if message:
            await interaction.response.send_message(message)

    @app_commands.command(name='wishlist', description="Display your wishlist.")
    async def wishlist_slash(self, interaction: discord.Interaction) :
        messages = await self._wishlist(interaction.channel.id, interaction.user)
        if messages is None:
            await interaction.response.send_message("An error occurred while retrieving your wishlist. Please try again later.")
        if isinstance(messages, str):
            await interaction.response.send_message(messages)
        else:
            await interaction.response.send_message(messages[0])
            for msg in messages[1:]:
                await interaction.channel.send(msg)
        
async def setup(bot):
    await bot.add_cog(TodoCog(bot))