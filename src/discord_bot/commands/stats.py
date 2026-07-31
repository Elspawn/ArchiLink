from utils.commands import get_current_player, check_world_channel
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import matplotlib.cm as cm
from io import BytesIO
import discord

def setup(bot):
    
    @bot.command(name='wastedOnArchipelago')
    async def wastedOnArchipelago(ctx) :
        session, discord_profil = await get_current_player(bot, ctx)
        if session is None or discord_profil is None :
            return
        player = discord_profil.current_slot
        time_played = player.time_played
        hours = int(time_played // 3600)
        minutes = int((time_played % 3600) // 60)
        seconds = int(time_played % 60)
        await ctx.send(f"You have wasted {hours} hours, {minutes} minutes and {seconds} seconds in this Archipelago Multiworld.")

    @bot.command(name='deaths')
    async def deaths(ctx) :
        session, discord_profil = await get_current_player(bot, ctx)
        if session is None or discord_profil is None :
            return
        player = discord_profil.current_slot
        await ctx.send(f"You have died {len(player.deaths)} times.")

    @bot.command(name='deathgraph')
    async def deathgraph(ctx) :
        session, discord_profil = await get_current_player(bot, ctx)
        if session is None or discord_profil is None :
            return
        player = discord_profil.current_slot
        if player.deaths == [] :
            await ctx.send(f"You have not died yet. Congratulations !")
        else :
            deaths_minutes = [t / 60 for t in player.deaths]
            cumulative_deaths = list(range(1, len(deaths_minutes) + 1))
            deaths_minutes = [0] + deaths_minutes
            cumulative_deaths = [0] + cumulative_deaths
            plt.figure(figsize=(10,5))
            plt.step(deaths_minutes, cumulative_deaths, where='post')
            plt.scatter(deaths_minutes, cumulative_deaths)
            plt.title(f'{player.player_name} death graph')
            plt.xlabel('Time played (minutes)')
            plt.ylabel('Number of Deaths')
            buf = BytesIO()
            plt.savefig(buf, format='png')
            buf.seek(0)
            await ctx.send(file=discord.File(buf, filename='death_graph.png'))
                
    @bot.command(name='globaldeaths')
    async def globaldeaths(ctx) :
        session = await check_world_channel(bot, ctx.channel.id)
        if session is None :
            return
        deaths_dict = {}
        for player in session.bot_client.player_db.get_all_players() :
            deaths_dict[player.player_name] = len(player.deaths)
        plt.figure(figsize=(10,5))
        plt.bar(deaths_dict.keys(), deaths_dict.values())
        plt.title('Global Deaths')
        plt.xlabel('Player')
        plt.ylabel('Number of Deaths')
        plt.xticks(rotation=45)
        buf = BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        await ctx.send(file=discord.File(buf, filename='global_deaths.png'))
        
    @bot.command(name='progressGraph')
    async def progress_graph(ctx):
        session = await check_world_channel(bot, ctx.channel.id)
        if session is None :
            return
        percentage_dict = {}; checks_dict = {}
        for player in session.bot_client.player_db.get_all_players() :
            if player.total_locations <= 0 :
                await ctx.send(f"Error retrieving total locations for player {player.player_name}. Cannot compute progress graph.\n\
Ask an admin to run !computeChecks command first.")
                return
            percentage = (player.checked_locations / player.total_locations * 100) if player.total_locations > 0 else 0
            checks_dict[player.player_name] = player.checked_locations
            percentage_dict[player.player_name] = percentage
        num_players = len(percentage_dict)
        plt.figure(figsize=(max(10, num_players*0.5), 8))
        values = list(percentage_dict.values())
        norm = mcolors.Normalize(vmin=0, vmax=100)
        cmap = cm.get_cmap('coolwarm')
        colors = [cmap(norm(v)) for v in values]
        bars = plt.bar(percentage_dict.keys(), percentage_dict.values(), color=colors)
        # Add value labels on top of bars
        for bar, player_name in zip(bars, percentage_dict.keys()):
            height = bar.get_height()
            plt.text(
                bar.get_x() + bar.get_width() / 2,
                height + 1,
                str(checks_dict[player_name]),
                ha='center',
                va='bottom',
                fontsize=9
            )
        plt.title('Progress Graph')
        plt.xlabel('Player')
        plt.ylabel('Percentage of checked locations')
        plt.xticks(rotation=45)
        buf = BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        await ctx.send(file=discord.File(buf, filename='progress_graph.png'))
