from archipelago.tracker_client import TrackerClient
import asyncio
import json
import os
import sys

async def is_admin(ctx, bot):
    return ctx.author.id in bot.admins

def is_running_in_docker() -> bool:
    if os.path.exists('/local_path/.dockerenv') or os.path.exists('/.dockerenv'):
        return True
    try:
        with open('/proc/self/cgroup', 'r') as f:
            if 'docker' in f.read():
                return True
    except Exception:
        pass
        
    return False

def setup_admin_commands(bot):
    
    @bot.command(name='admin', help='Admin command')
    async def admin_command(ctx):
        if ctx.channel is not None and ctx.channel.id != bot.normal_channel_id:
            return
        if not await is_admin(ctx, bot):
            return
        await ctx.send('This is an admin command.')
    
    @bot.command(name='computeChecks')
    async def compute_checks(ctx):
        if ctx.channel is not None and ctx.channel.id != bot.normal_channel_id:
            return
        if not await is_admin(ctx, bot):
            return
        await ctx.send("Computing checks for all players. This may take a while...")
        try:
            for player in bot.bot_client.player_db.get_all_players():
                bot.logger.info(f"Computing checks for player {player.player_name}")
                tracker_client = TrackerClient(bot.config, bot.bot_client.logger, player.player_name)
                asyncio.create_task(tracker_client.run())
                await tracker_client.finished_event.wait()
                player.total_locations = tracker_client.total_locations
                player.checked_locations = tracker_client.checked_locations
            bot.logger.info("Checks computed for all players")
            await ctx.send("Checks computed for all players.")
        except Exception as e:
            bot.logger.error(f"Error computing checks: {e}")
            await ctx.send("An error occurred while computing checks. Please try again later.")

    @bot.command(name='setport')
    async def set_port(ctx, new_port: int):
        if ctx.channel is not None and ctx.channel.id != bot.normal_channel_id:
            return
        if not await is_admin(ctx, bot):
            return
        try:
            ctx.bot.config["ArchipelagoConfig"]["client_port"] = new_port
            
            with open("config.json", "w") as f:
                json.dump(ctx.bot.config, f, indent=4)
            await ctx.send(f"Port configured to {new_port} and saved to config.json.")

            if hasattr(ctx.bot, 'player_db') and ctx.bot.player_db:
                ctx.bot.player_db.players = {}
                if hasattr(ctx.bot.player_db, 'save_db'):
                    data_directory = ctx.bot.config["DatabaseConfig"]["data_directory"]
                    ctx.bot.player_db.save_db(f"{data_directory}/players.json")
                await ctx.send("Local player database cleared.")

            if hasattr(ctx.bot, 'archipelago_client') and ctx.bot.archipelago_client:
                client = ctx.bot.archipelago_client
                
                if hasattr(client, 'client_port'):
                    client.client_port = new_port
                
                if hasattr(client, 'auto_reconnect'):
                    client.auto_reconnect = True
                
                if hasattr(client, 'socket') and client.socket:
                    await ctx.send("Reconnecting to the new Archipelago room...")
                    await client.socket.close()
                else:
                    await ctx.send("Port saved, but active connection socket was not found to auto-reconnect.")
            else:
                await ctx.send("Port saved, but Archipelago client instance was not found.")

        except Exception as e:
            bot.logger.error(f"Error changing port: {e}")
            await ctx.send(f"Error changing port: {str(e)}")
    
    @bot.command(name='restart')
    async def restart_bot(ctx):
        if ctx.channel is not None and ctx.channel.id != bot.normal_channel_id:
            return
        if not await is_admin(ctx, bot):
            return
        
        in_docker = is_running_in_docker()

        if in_docker:
            await ctx.send("Docker detected. Closing connections and shutting down (Docker will restart the container).")
            bot.logger.info("Shutdown order received from Discord (Docker environment). Exiting cleanly.")
            await bot.close()
            os._exit(0) 
        else:
            await ctx.send("Standard Python environment detected. Rebooting application process...")
            bot.logger.info("Restart order received from Discord (Python environment). Executing os.execv.")
            os.execv(sys.executable, ['python'] + sys.argv)

    @bot.command(name='disconnect')
    async def disconnect_archipelago(ctx):
        if ctx.channel is not None and ctx.channel.id != bot.normal_channel_id:
            return
        if not await is_admin(ctx, bot):
            return
        try:
            if hasattr(ctx.bot, 'archipelago_client') and ctx.bot.archipelago_client:
                client = ctx.bot.archipelago_client
                
                if hasattr(client, 'auto_reconnect'):
                    client.auto_reconnect = False
                
                if hasattr(client, 'socket') and client.socket:
                    await ctx.send("Disconnecting from Archipelago server...")
                    await client.socket.close()
                    await ctx.send("Archipelago client disconnected. Bot remains active on Discord.")
                else:
                    await ctx.send("No active Archipelago connection socket found.")
            else:
                await ctx.send("Archipelago client instance not found.")
        except Exception as e:
            bot.logger.error(f"Error disconnecting client: {e}")
            await ctx.send(f"Error disconnecting: {str(e)}")
