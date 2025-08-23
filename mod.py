import discord
import logging
import os
from discord.ext import commands
from keep_alive import keep_alive  # Replit keep-alive server
from datetime import timedelta
from discord.ext import commands
from penalties import penalty_schedule
from collections import defaultdict

violation_counts = defaultdict(int)
violations = defaultdict(list)  # user_id -> list of timestamps

# Intents setup
intents = discord.Intents.default()
intents.message_content = True
intents.messages = True
intents.guilds = True
intents.members = True

client = commands.Bot(command_prefix="!", intents=intents)

def run_bot():
    client.run(os.getenv("DISCORD_BOT_TOKEN"))


@client.event
async def on_ready():
    print(f"✅ Logged in as {client.user}")

# Add your moderation logic here...

duration = timedelta(minutes=1)
async def handle_violation(message):
    guild = message.guild
    user = message.author

    # Fetch full Member object
    member = guild.get_member(user.id)
    if not member:
        logging.warning(f"Could not fetch member object for {user}")
        return

    violation_counts[user.id] += 1
    count = violation_counts[user.id]

    # Escalation logic
    if count >= 3:
        duration = timedelta(days=1)
        reason = f"Used banned words {count} times — escalated to 1-day timeout."
    else:
        duration = timedelta(minutes=1)
        reason = f"Used Racial Slurs — {count} violation(s)."

    try:
        await member.timeout(duration, reason=reason)
        logging.info(f"Timed out {member} for {duration}. Reason: {reason}")
    except discord.Forbidden:
        logging.error(f"Missing permissions to timeout {member}")
    except Exception as e:
        logging.error(f"Failed to timeout {member}: {e}")

    # Optional mod log
    log_channel = discord.utils.get(guild.text_channels, name="logs")
    if log_channel:
        await log_channel.send(
            f"⛔ {member.mention} timed out for {duration}.\nReason: {reason}"
        )

violations = defaultdict(list)  # user_id -> list of timestamps

# Logging setup
logging.basicConfig(level=logging.INFO)

bot = commands.Bot(command_prefix="!", intents=intents)

# 🚫 Slur detection logic
def contains_slur(text):
    slurs = ["nigga", "nigger", "nword", "n-word", "chink", "fatass"]
    return any(word in text.lower() for word in slurs)

# 🔁 Message replacement logic
def escape_discord_formatting(text):
    return (
        text.replace("*", "\\*")
            .replace("_", "\\_")
            .replace("`", "\\`")
            .replace("~", "\\~")
            .replace("@", "@\u200b")  # Prevent mentions like @everyone
    )

async def replace_message(message):
    try:
        await message.delete()
        logging.info(f"Deleted message from {message.author} in #{message.channel}")
        await handle_violation(message)

        # 🔒 Send detailed violation summary to logs only
        sanitized_content = escape_discord_formatting(message.content)
        violation_summary = (
            f"⚠️ Violation detected:\n"
            f"User: **{message.author.display_name}**\n"
            f"Message: \"{sanitized_content}\"\n"
            f"Action: Message deleted due to prohibited language."
        )

        # Send to mod-logs channel (replace with actual name or ID)
        log_channel = discord.utils.get(message.guild.text_channels, name="logs")
        if log_channel:
            await log_channel.send(violation_summary)
            logging.info(f"Sent violation summary to #{log_channel.name}")
        else:
            logging.warning("mod-logs channel not found — cannot log violation")

        # 📢 Public-facing notice
        public_notice = (
            f"⚠️ Your message in **#{message.channel}** was removed because it contained language that is not allowed in this server.\n"
            "Please review the server rules to avoid future violations."
        )
        await message.channel.send(f"{message.author.mention} {public_notice}")
        logging.info(f"Sent public reminder to {message.author}")

        # 📬 Attempt DM
        try:
            await message.author.send(public_notice)
            logging.info(f"Also sent DM to {message.author}")
        except discord.Forbidden:
            logging.warning(f"Could not DM {message.author} — DMs may be disabled.")

    except Exception as e:
        logging.error(f"Failed to replace message from {message.author}: {e}")


# 📩 Handle new messages
@bot.event
async def on_message(message):
    if message.author.bot:
        return
    if contains_slur(message.content):
        await replace_message(message)
        return
    await bot.process_commands(message)

# ✏️ Handle message edits
@bot.event
async def on_message_edit(before, after):
    if after.author.bot:
        return
    if contains_slur(after.content):
        await replace_message(after)

# ✅ Bot ready
@bot.event
async def on_ready():
    logging.info(f"Bot connected as {bot.user}")

# 🧪 Example command
@bot.command()
async def ping(ctx):
    await ctx.send("Pong!")

# 🔄 Keep-alive for Replit
keep_alive()

# 🚀 Start bot
bot.run(os.getenv("DISCORD_BOT_TOKEN"))