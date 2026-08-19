from utils.ansi import AnsiTable, AnsiText
from utils.commands import get_current_player
from utils.colors import get_ansi_color_from_flag
from archipelago.hint_client import HintClient
from models.button import Button
import asyncio
import re
from discord.ext import commands
from discord import app_commands
import discord

ANSI_ESCAPE = re.compile(r'\x1b\[[0-9;]*m')

def strip_ansi(s):
    return ANSI_ESCAPE.sub('', s)

def ansi_ljust(s, width):
    return s + " " * (width - len(strip_ansi(s)))

async def autocomplete_hint(interaction: discord.Interaction, current: str):
    session, discord_profil = await get_current_player(interaction.client, interaction.channel.id, interaction.user)
    if session is None or discord_profil is None :
        return []
    player = discord_profil.current_slot
    game_playing = player.player_game
    all_items = session.bot_client.datapackage["data"]["games"][game_playing]["id_to_item_name"].values()
    filtered_items = [item for item in all_items if current.lower() in item.lower()]
    # Limit the number of suggestions to 25 (Discord's limit for autocomplete)
    filtered_items = filtered_items[:25]
    return [app_commands.Choice(name=item, value=item) for item in filtered_items]

class HintCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    async def _hint(self, channel_id, author, hint: str):
        session, discord_profil = await get_current_player(self.bot, channel_id, author)
        if session is None or discord_profil is None :
            return "No session or discord profile found. Please make sure you are in a valid game session and registered."
        player = discord_profil.current_slot
        try :
            hint_client_instance = HintClient(player.player_name, 
                                            player.player_game, 
                                            hint, 
                                            session.bot_client,
                                            session.bot_client.config)
            asyncio.create_task(hint_client_instance.run())
            await hint_client_instance.finished_event.wait()
            # Send all messages in the queue :
            while not hint_client_instance.discord_bot_queue.empty() :
                message = await hint_client_instance.discord_bot_queue.get()
                try :
                    message, item = message
                    if "(found)" in message : # Do not add the possibility to add to todo list if already found
                        await self.bot.get_channel(channel_id).send(message)
                        continue
                    button = Button(item, session.bot_client)
                    message = await self.bot.get_channel(channel_id).send(message, view=button)
                    button.message = message
                except :
                    await self.bot.get_channel(channel_id).send(message)
            # Terminate hint client
            await hint_client_instance.stop()
        except Exception as e :
            session.bot_client.logger.error(f"Error sending hint: {e}")
            return "An error occurred while sending the hint. Please try again later."
        return "Hint sent successfully."
            
    async def _allhints(self, channel_id, author):
        session, discord_profil = await get_current_player(self.bot, channel_id, author)
        if session is None or discord_profil is None :
            return "No session or discord profile found. Please make sure you are in a valid game session and registered."
        player = discord_profil.current_slot     
        hints = await session.bot_client.retrieve_available_hints(player.player_slot)
        hints_to_send = hints["to_send"]; hints_to_get = hints["to_get"]
        table = AnsiTable(
            title="Here is a list of all the hints available for you (what other players can send you):", 
            headers=["You", "Item", "Sender", "Location"]
        )
        for item in hints_to_get :
            table.add_row(
                AnsiText(player.player_name, color=player.color), 
                AnsiText(item.item_name),
                AnsiText(item.player_sending.player_name, color=item.player_sending.color),
                AnsiText(item.location_name)
            )
        messages1 = await table.format_messages()
        table = AnsiTable(
            title="Here are all the items you can send to other players:", 
            headers=["You", "Item", "Receiver", "Location"]
        )
        for item in hints_to_send :
            table.add_row(
                AnsiText(player.player_name, color=player.color), 
                AnsiText(item.item_name),
                AnsiText(item.player_recieving.player_name, color=item.player_recieving.color),
                AnsiText(item.location_name)
            )
        messages2 = await table.format_messages()
        return messages1, messages2
        
    # ============================================================
    # Prefix commands
    # ============================================================
    
    @commands.command(name='hint', description="Send a hint to the MultiWorld Client.")
    async def hint(self, ctx, *, hint: str):
        response = await self._hint(ctx.channel.id, ctx.author, hint)
        await ctx.send(response)

    @commands.command(name='allhints', description="Get all hints available for the current player.")
    async def allhints(self, ctx):
        response = await self._allhints(ctx.channel.id, ctx.author)
        if isinstance(response, str):
            await ctx.send(response)
        elif isinstance(response, tuple):
            messages1, messages2 = response
            for msg in messages1:
                await ctx.send(msg)
            for msg in messages2:
                await ctx.send(msg)
    # ============================================================
    # Slash commands
    # ============================================================
    
    #TODO: Add autocomplete for the hint parameter, to suggest items that are in the game.
    @app_commands.command(name='hint', description="Send a hint to the MultiWorld Client.")
    @app_commands.describe(hint="The item you want to get a hint for.")
    @app_commands.autocomplete(hint=autocomplete_hint)
    async def hint_slash(self, interaction: discord.Interaction, hint: str):
        await interaction.response.defer()
        response = await self._hint(interaction.channel.id, interaction.user, hint)
        await interaction.response.followup.send(response)

    @app_commands.command(name='allhints', description="Get all hints available for the current player.")
    async def allhints_slash(self, interaction: discord.Interaction):
        await interaction.response.defer()
        response = await self._allhints(interaction.channel.id, interaction.user)
        if isinstance(response, str):
            await interaction.response.followup.send(response)
        elif isinstance(response, tuple):
            messages1, messages2 = response
            await interaction.response.followup.send(messages1[0])
            for msg in messages1[1:]:
                await interaction.channel.send(msg)
            for msg in messages2:
                await interaction.channel.send(msg)
        
async def setup(bot):
    await bot.add_cog(HintCog(bot))