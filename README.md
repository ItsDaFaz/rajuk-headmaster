# rajuk-headmaster

A Discord joke bot that relentlessly tells one specific user to **porte bosho** (go study).

## Rules

| User Status | Behaviour |
|---|---|
| **Offline** | DM sent once daily at 9 AM |
| **Online, no game** | Channel message every 30 minutes |
| **Online, playing a game** | Channel message every 10 minutes |

## Setup

1. **Create a Discord Application & Bot** at <https://discord.com/developers/applications>.
2. Enable the **Presence Intent** and **Server Members Intent** under *Bot → Privileged Gateway Intents*.
3. Invite the bot to your server with at least `Send Messages` and `View Channels` permissions.
4. Copy `.env.example` → `.env` and fill in your values:

   ```
   cp .env.example .env
   ```

   | Variable | Description |
   |---|---|
   | `DISCORD_BOT_TOKEN` | Bot token from the developer portal |
   | `TARGET_USER_ID` | The user ID of the person to annoy |
   | `CHANNEL_ID` | Channel where public reminders are sent |
   | `GUILD_ID` | Your Discord server (guild) ID |

5. Install dependencies and run:

   ```bash
   pip install -r requirements.txt
   python bot.py
   ```

## Notes

- The 9 AM DM uses your machine's **local time** (or the server's timezone if hosted remotely).
- The bot requires the **Presences** and **Server Members** privileged intents to detect online status and game activity.
