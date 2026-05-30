# Docker Setup Guide

> ⚠️ This setup process has only been tested a limited number of times. If you encounter any issues, please open an issue or contact me directly.

## 1. Create a Discord Bot

Before running ArchiLink, you need to create a Discord bot and invite it to your server.

Follow the **"Create a Discord Bot"** section of the main setup guide:

https://github.com/TanguyBod/ArchiLink/blob/main/docs/setup.md

Complete **steps 1 to 4** under **Create a Discord Bot**, then stop before the **Setup the Archipelago MultiWorld** section.

Once your bot is online and has been added to your server, continue with the Docker installation below.

---

## 2. Clone the Repository

Clone the project to your machine:

```bash
git clone https://github.com/TanguyBod/ArchiLink.git
```

Then move into the project directory:

```bash
cd ArchiLink
```

---

## 3. Configure Environment Variables

Create a `.env` file at the root of the project.

You can either:

* Rename `.env.template` to `.env`
* Or create a new `.env` file and copy the contents of `.env.template`

Fill in the following values:

```env
DISCORD_APP_TOKEN=your_discord_bot_token
DISCORD_COMMAND_PREFIX=! 
DATA_DIRECTORY=/path/to/worlds/data
```

### Variables description

| Variable                 | Description                                                              |
| ------------------------ | ------------------------------------------------------------------------ |
| `DISCORD_APP_TOKEN`      | The Discord bot token obtained during bot creation.                      |
| `DISCORD_COMMAND_PREFIX` | The prefix used for bot commands (for example `!`).                      |
| `DATA_DIRECTORY`         | Directory where ArchiLink will store world data and configuration files. |

---

## 4. Build and Start the Container

From the root of the project, run:

```bash
docker compose up -d
```

This command will:

* Build the Docker image
* Create the required containers
* Start ArchiLink in the background

You can verify that everything is running correctly with:

```bash
docker compose ps
```

To view the logs:

```bash
docker compose logs -f
```

---

## 5. You're Ready!

Your bot should now be online and ready to track Archipelago multiworlds.

You can verify that everything works by using one of the bot commands in your Discord server.

Have fun!
