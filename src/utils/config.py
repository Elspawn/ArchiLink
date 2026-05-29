def check_config(data) -> bool :
    # Check if all required fields are present
    required_fields = [
        "ArchipelagoConfig",
        "DiscordConfig",
        "AdvancedConfig"
    ]
    for field in required_fields:
        if field not in data:
            return False
        
    # Check if all required subfields are present
    archipelago_config_fields = [
        "client_url",
        "client_port",
        "password",
        "bot_slot",
        "self_hosted"
    ]
    for field in archipelago_config_fields:
        if field not in data["ArchipelagoConfig"]:
            return False
        
    discord_config_fields = [
        "normal_channel_id",
        "ping_channel_id",
        "admin_ids"
    ]
    for field in discord_config_fields:
        if field not in data["DiscordConfig"]:
            return False
        
    advanced_config_fields = [
        "custom_deathlink_flavor",
        "auto_ping_new_items"
    ]    
    for field in advanced_config_fields:
        if field not in data["AdvancedConfig"]:
            return False
        
    return True