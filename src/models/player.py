from models.item import Item

PLAYER_COLORS = [
    "30", # Black
    "31", # Red
    "32", # Green
    "33", # Yellow
    "34", # Blue
    "35", # Purple
    "36", # Cyan
]

RESTRICTED_COLORS = [
    "32", # Green
    "35", # Purple
    "36", # Cyan    
]

class Player:
    def __init__(self, player_slot, player_game, player_name, discord_id=None, color_restricted=False):
        self.player_slot = player_slot
        self.player_game = player_game
        self.player_name = player_name
        self.discord_id = discord_id
        self.new_items = []
        self.todolist = []
        self.allow_ping = True
        if color_restricted:
            self.color = RESTRICTED_COLORS[int(player_slot) % len(RESTRICTED_COLORS)]
        else:
            self.color = PLAYER_COLORS[int(player_slot) % len(PLAYER_COLORS)]
        self.name_colored = f"\u001b[0;{self.color}m{self.player_name}\u001b[0m"
        self.is_playing = False
        self.time_joined = 0.0
        self.time_played = 0.0 # seconds
        self.get_new_items_auto = True # TODO: add this in the configuration file
        self.deaths = []
        self.total_locations = 0
        self.checked_locations = 0

    def save(self):
        return {
            "player_slot": self.player_slot,
            "player_game": self.player_game,
            "player_name": self.player_name,
            "discord_id": self.discord_id,
            "new_items": [item.save() for item in self.new_items],
            "todolist": [item.save() for item in self.todolist],
            "allow_ping": self.allow_ping,
            "time_played": self.time_played,
            "get_new_items_auto": self.get_new_items_auto,
            "deaths": self.deaths,
            "total_locations": self.total_locations,
            "checked_locations": self.checked_locations
        }
    
    @staticmethod
    def load(data : dict) -> 'Player' :
        player = Player(
            player_slot=data["player_slot"],
            player_game=data["player_game"],
            player_name=data["player_name"],
            discord_id=data["discord_id"]
        )
        player.color = PLAYER_COLORS[int(player.player_slot) % len(PLAYER_COLORS)]
        player.name_colored = f"{player.color}{player.player_name}\u001b[0m"
        player.new_items = [Item.load(item_data) for item_data in data.get("new_items", [])]
        player.todolist = [Item.load(item_data) for item_data in data.get("todolist", [])]
        player.allow_ping = data.get("allow_ping", True)
        player.time_played = data.get("time_played", 0.0)
        player.get_new_items_auto = data.get("get_new_items_auto", True)
        player.is_playing = False
        player.time_joined = 0.0
        player.deaths = data.get("deaths", [])
        player.total_locations = data.get("total_locations", 0)
        player.checked_locations = data.get("checked_locations", 0)
        return player