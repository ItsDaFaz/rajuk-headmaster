import discord
from discord.ext import commands, tasks
import datetime
import os
from dotenv import load_dotenv

load_dotenv()

# ──────────────────────────────────────────────
# Configuration – fill these in or set via .env
# ──────────────────────────────────────────────
BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
TARGET_USER_ID = int(os.getenv("TARGET_USER_ID", "000000000000000000"))
CHANNEL_ID = int(os.getenv("CHANNEL_ID", "000000000000000000"))
GUILD_ID = int(os.getenv("GUILD_ID", "000000000000000000"))

MESSAGE = "porte bosho"  # "go study"

# ──────────────────────────────────────────────
# Bot setup
# ──────────────────────────────────────────────
intents = discord.Intents.default()
intents.members = True
intents.presences = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)


# ──────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────
def get_target_member() -> discord.Member | None:
    """Resolve the target user as a Member of the configured guild."""
    guild = bot.get_guild(GUILD_ID)
    if guild is None:
        return None
    return guild.get_member(TARGET_USER_ID)


def is_playing_game(member: discord.Member) -> bool:
    """Return True if the member has a game / rich-presence activity."""
    if member.activities:
        for activity in member.activities:
            if isinstance(activity, (discord.Game, discord.Activity)):
                if activity.type in (
                    discord.ActivityType.playing,
                    discord.ActivityType.streaming,
                ):
                    return True
    return False


# ──────────────────────────────────────────────
# Scheduled loops
# ──────────────────────────────────────────────

@tasks.loop(minutes=1)
async def heartbeat():
    """
    Runs every minute and decides what to do based on the target user's
    current presence.

    • Offline  → handled by daily_dm (fires at 9 AM)
    • Online / Idle / DND, NO game  → message channel every 30 min
    • Online / Idle / DND, WITH game → message channel every 10 min
    """
    member = get_target_member()
    if member is None:
        return

    # Skip if user is offline – the daily_dm loop handles that case
    if member.status == discord.Status.offline:
        return

    now = datetime.datetime.now()
    channel = bot.get_channel(CHANNEL_ID)
    if channel is None:
        print(f"[WARNING] Could not find channel {CHANNEL_ID}")
        return

    playing = is_playing_game(member)

    if playing:
        # Every 10 minutes  →  fire when minute is divisible by 10
        if now.minute % 10 == 0:
            await channel.send(f"<@{TARGET_USER_ID}>, {MESSAGE}")
            print(f"[{now}] Sent 10-min reminder (playing a game)")
    else:
        # Every 30 minutes  →  fire when minute is 0 or 30
        if now.minute % 30 == 0:
            await channel.send(f"<@{TARGET_USER_ID}>, {MESSAGE}")
            print(f"[{now}] Sent 30-min reminder (online, no game)")


@tasks.loop(time=datetime.time(hour=9, minute=0, second=0))
async def daily_dm():
    """
    Fires once a day at 09:00 (server/local time).
    If the target user is offline, send them a DM.
    """
    member = get_target_member()
    if member is None:
        # Can't resolve member – try fetching user directly for DM
        try:
            user = await bot.fetch_user(TARGET_USER_ID)
        except discord.NotFound:
            print("[WARNING] Target user not found via API")
            return
    else:
        if member.status != discord.Status.offline:
            # They're online – the heartbeat loop already handles this
            return
        user = member

    try:
        await user.send(MESSAGE)
        print(f"[{datetime.datetime.now()}] Sent daily 9 AM DM (user offline)")
    except discord.Forbidden:
        print("[WARNING] Cannot DM target user (DMs might be closed)")


# ──────────────────────────────────────────────
# Events
# ──────────────────────────────────────────────

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    print(f"Target user : {TARGET_USER_ID}")
    print(f"Channel     : {CHANNEL_ID}")
    print(f"Guild       : {GUILD_ID}")
    print("─" * 40)

    if not heartbeat.is_running():
        heartbeat.start()
    if not daily_dm.is_running():
        daily_dm.start()


# ──────────────────────────────────────────────
# Run
# ──────────────────────────────────────────────
if __name__ == "__main__":
    bot.run(BOT_TOKEN)
