from utils.commands import get_current_player
from discord.ext import commands
from discord import app_commands
import discord

class ChatCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    async def _say(self, channel_id: int, message: str, author) :
        session, discord_profil = await get_current_player(self.bot, channel_id, author)
        if session is None or discord_profil is None :
            return "No session or discord profile found. Please make sure you are in a valid game session and registered."
        player = discord_profil.current_slot
        message_to_send = f"[{player.player_name}] {message}"
        self.bot.custom_logger.info(f"Sending message to MultiWorld Client: {message_to_send}")
        await session.bot_client.say_messages(message_to_send)
        return "Message sent successfully."
        
    @commands.command(name='say', help='Send a message to the MultiWorld Client')
    async def say(self, ctx, *, message: str):
        response = await self._say(ctx.channel.id, message, ctx.author)
        await ctx.send(response)

    @app_commands.command(name='say', description='Send a message to the MultiWorld Client')
    async def say_slash(self, interaction: discord.Interaction, message: str):
        await interaction.response.defer()
        response = await self._say(interaction.channel.id, message, interaction.user)
        await interaction.followup.send(response)

async def setup(bot):
    await bot.add_cog(ChatCog(bot))
