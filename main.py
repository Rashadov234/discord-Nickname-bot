import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

load_dotenv()

# Bot setup
intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Map alliance role names to tags
# CUSTOMIZE THIS WITH YOUR ALLIANCE NAMES AND TAGS
ALLIANCE_TAGS = {
    "RoK": "[RoK]",
    "E84": "[E84]",
    "LOK": "[LOK]",
    # Add more alliances as needed
}


@bot.event
async def on_ready():
    print(f"✅ Bot logged in as {bot.user}")
    print(f"📡 Watching for role changes...")


@bot.event
async def on_member_update(before, after):
    """Triggered when a member's info changes (including roles)"""

    # Check if roles actually changed
    if before.roles == after.roles:
        return

    # Check if member gained a new role
    new_roles = set(after.roles) - set(before.roles)

    if not new_roles:
        return

    # Look for alliance roles
    for role in new_roles:
        if role.name in ALLIANCE_TAGS:
            tag = ALLIANCE_TAGS[role.name]

            # Get the member's current server nickname
            # If they have a server nickname, use it; otherwise use their Discord username
            current_name = after.nick if after.nick else after.name

            # Remove any existing tags from their current name (in case they had one)
            # This prevents double-tagging
            for existing_tag in ALLIANCE_TAGS.values():
                if current_name.startswith(existing_tag):
                    current_name = current_name[len(existing_tag) :].strip()
                    break

            # Create new nickname with tag
            new_nick = f"{tag} {current_name}"

            # Discord has 32 char limit for nicknames
            if len(new_nick) > 32:
                new_nick = new_nick[:32]

            try:
                await after.edit(nick=new_nick)
                print(f"✏️  Changed {after.display_name}'s nickname to: {new_nick}")
            except discord.Forbidden:
                print(
                    f"❌ Missing permission to change nickname for {after.display_name}"
                )
            except Exception as e:
                print(f"❌ Error changing nickname: {e}")

            return  # Only handle first alliance role


# Run the bot
if __name__ == "__main__":
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        print("❌ DISCORD_TOKEN not found")
    else:
        bot.run(token)
