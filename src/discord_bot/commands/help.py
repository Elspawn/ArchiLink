from utils.commands import check_world_channel

def setup(bot):
    
    @bot.command(name='help')
    async def help(ctx, command: str = None):
        session = await check_world_channel(bot, ctx.channel.id)
        if session is None :
            msg = (
                "**Available commands**\n\n"
                "`!newWorld` - Create and initialize a new Archipelago multiworld.\n"
                "This command can be used in any channel and allows you to set up a new multiworld session with interactive configuration or by uploading a `config.json` file.\n\n"
                "`!deleteWorld` - Delete the multiworld associated with the current channel.\n"
                "This command stops the bot from tracking the multiworld in this channel and removes all related data, but does not affect the actual Archipelago session.\n"
                "If admins are configured in the world, only admins can use this command."
                "`!fastConfig` - Quickly create a new multiworld with minimal configuration.\n"
                "This command can be used in any channel and allows you to set up a new multiworld session with default settings, providing only the ip and port (optionnal password).\n"
                "Example: `!fastConfig 127.0.0.1 38281 mypassword`"
            )
            await ctx.send(msg)
            return
        
        commands_help = {
            "register": {
                "usage": "`!register <player_name>`",
                "description": "Link your Discord account to a player.",
                "details": (
                    "You will receive notifications about this player's items and gain access "
                    "to player-specific commands.\n\n"
                    "Example:\n"
                    "`!register Alice`"
                )
            },
            "unregister": {
                "usage": "`!unregister [player_name]`",
                "description": "Unlink your account from one or more players.",
                "details": (
                    "If no player is specified, you will be unregistered from all registered players.\n\n"
                    "Examples:\n"
                    "`!unregister`\n"
                    "`!unregister Alice`"
                )
            },
            "players": {
                "usage": "`!players`",
                "description": "Display all players in the multiworld.",
                "details": "Useful to verify the exact spelling of player names."
            },
            "current": {
                "usage": "`!current`",
                "description": "Display your currently tracked player.",
                "details": (
                    "This player is used by commands such as "
                    "`!todo`, `!wishlist`, `!hint`, and `!new`."
                )
            },
            "switch": {
                "usage": "`!switch [player_name]`",
                "description": "Change your tracked player.",
                "details": (
                    "Without arguments, switches to the next registered player.\n"
                    "With a player name, directly switches to that player.\n\n"
                    "Examples:\n"
                    "`!switch`\n"
                    "`!switch Alice`"
                )
            },
            "hint": {
                "usage": "`!hint <text>`",
                "description": "Send a hint request to the tracker.",
                "details": (
                    "Recognized hints may provide interactions such as "
                    "adding items to your todo list.\n\n"
                    "Example:\n"
                    "`!hint City Crest`"
                )
            },
            "new": {
                "usage": "`!new`",
                "description": "Check newly received items.",
                "details": (
                    "Displays items received since your last check. "
                    "Results are sent through DM."
                )
            },
            "todo": {
                "usage": "`!todo`",
                "description": "Display your todo list.",
                "details": (
                    "Shows the items currently tracked for your active player."
                )
            },
            "cleartodo": {
                "usage": "`!clearTodo`",
                "description": "Clear your todo list.",
                "details": "Removes every item from your current todo list."
            },
            "removetodo": {
                "usage": "`!removeTodo <item_name>`",
                "description": "Remove an item from your todo list.",
                "details": (
                    "Example:\n"
                    "`!removeTodo Hookshot`"
                )
            },
            "wishlist": {
                "usage": "`!wishlist`",
                "description": "Display items other players marked for you.",
                "details": (
                    "Shows all wishlist items targeting your currently tracked player."
                )
            },
            "say": {
                "usage": "`!say <message>`",
                "description": "Send a message to the MultiWorld Client.",
                "details": (
                    "The message will be sent as if it was from your currently tracked player.\n\n"
                    "Example:\n"
                    "`!say Hello everyone!`"
                )
            },
            "enableping": {
                "usage": "`!enableping`",
                "description": "Enable todo notifications.",
                "details": (
                    "You will be pinged when another player finds an item "
                    "present in your todo list."
                )
            },
            "disableping": {
                "usage": "`!disableping`",
                "description": "Disable todo notifications.",
                "details": "Stops ping notifications from the bot."
            },
            "enablenewitems": {
                "usage": "`!enablenewitems`",
                "description": "Enable automatic new item notifications.",
                "details": (
                    "You will automatically receive newly collected items "
                    "via DM when connecting to the game."
                )
            },
            "disablenewitems": {
                "usage": "`!disablenewitems`",
                "description": "Disable automatic new item notifications.",
                "details": (
                    "You will need to use `!new` manually to check received items."
                )
            },
            "wastedonarchipelago": {
                "usage": "`!wastedOnArchipelago`",
                "description": "Display your total playtime.",
                "details": "Shows the total time spent in the multiworld session."
            },
            "deaths": {
                "usage": "`!deaths`",
                "description": "Display your total death count.",
                "details": "Shows how many times you died during the session."
            },
            "deathgraph": {
                "usage": "`!deathgraph`",
                "description": "Generate a death progression graph.",
                "details": "Displays cumulative deaths over time."
            },
            "globaldeaths": {
                "usage": "`!globaldeaths`",
                "description": "Compare deaths between all players.",
                "details": "Generates a comparative graph for every player."
            },
            "progressgraph": {
                "usage": "`!progressGraph`",
                "description": "Generate a progression graph.",
                "details": (
                    "Displays progression information for all players "
                    "(checks found, completion percentage, etc.)."
                )
            },
            "help": {
                "usage": "`!help [command]`",
                "description": "Display help information.",
                "details": (
                    "Use without arguments to list all commands or specify "
                    "a command for detailed help."
                )
            }
        }

        if command is None:
            msg = (
                "**Available commands**\n\n"

                "**Player management**\n"
                "`!register <player>`\n"
                "`!unregister [player]`\n"
                "`!players`\n"
                "`!current`\n"
                "`!switch [player]`\n\n"

                "**Hints & progression**\n"
                "`!hint <text>`\n"
                "`!todo`\n"
                "`!clearTodo`\n"
                "`!removeTodo <item>`\n"
                "`!wishlist`\n"
                "`!new`\n"
                "`!say <message>`\n\n"

                "**Statistics**\n"
                "`!wastedOnArchipelago`\n"
                "`!deaths`\n"
                "`!deathgraph`\n"
                "`!globaldeaths`\n"
                "`!progressGraph`\n\n"

                "**Notifications**\n"
                "`!enableping`\n"
                "`!disableping`\n"
                "`!enablenewitems`\n"
                "`!disablenewitems`\n\n"

                "Use `!help <command>` for detailed information about a specific command."
            )
            await ctx.send(msg)
            return

        command = command.lower()

        if command not in commands_help:
            await ctx.send(
                f"Command `{command}` not found. Use `!help` to see all available commands."
            )
            return

        data = commands_help[command]

        msg = (
            f"**{data['usage']}**\n\n"
            f"{data['description']}\n\n"
            f"{data['details']}"
        )

        await ctx.send(msg)
