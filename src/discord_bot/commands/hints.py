from utils.ansi import AnsiTable, AnsiText
from utils.commands import get_current_player
from utils.colors import get_ansi_color_from_flag
from archipelago.hint_client import HintClient
import asyncio
import re

ANSI_ESCAPE = re.compile(r'\x1b\[[0-9;]*m')

def strip_ansi(s):
    return ANSI_ESCAPE.sub('', s)

def ansi_ljust(s, width):
    return s + " " * (width - len(strip_ansi(s)))

def setup(bot):
    
    @bot.command(name='hint')
    async def hint(ctx, *, hint: str):
        bot.custom_logger.info(f"Hint command called with hint : {hint}")
        session, discord_profil = await get_current_player(bot, ctx)
        if session is None or discord_profil is None :
            return
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
                        await ctx.send(message)
                        continue
                    button = Button(item, session.bot_client)
                    message = await ctx.send(message, view=button)
                    button.message = message
                except :
                    await ctx.send(message)
            # Terminate hint client
            await hint_client_instance.stop()
        except Exception as e :
            session.bot_client.logger.error(f"Error sending hint: {e}")
            await ctx.send(f"An error occurred while sending the hint. Please try again later.")

    @bot.command(name='allhints', description="Get all hints available for the current player.")
    async def allhints(ctx):
        session, discord_profil = await get_current_player(bot, ctx)
        if session is None or discord_profil is None :
            return
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
        await table.send(ctx)
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
        await table.send(ctx)