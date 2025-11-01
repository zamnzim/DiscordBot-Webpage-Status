import discord
from discord.ext import commands, tasks
import aiohttp
from bs4 import BeautifulSoup
import sqlite3
import os
import logging
from urllib.parse import urljoin

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# SQLite setup
DB_PATH = "data/websites.db"
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS websites (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    url TEXT UNIQUE,
    description TEXT,
    favicon TEXT,
    message_id INTEGER,
    channel_id INTEGER
)
""")
conn.commit()

@bot.event
async def on_ready():
    logger.info(f"Logged in as {bot.user}")
    update_status.start()

@bot.command()
async def webstatus(ctx, url: str):
    try:
        await ctx.message.delete()
    except Exception as e:
        logger.warning(f"Failed to delete command message: {e}")

    cursor.execute("SELECT * FROM websites WHERE url = ?", (url,))
    if cursor.fetchone():
        await ctx.send("This website is already being monitored.", delete_after=5)
        return

    status, description, favicon = await scrape_site(url)

    if not description:
        prompt = await ctx.send("I couldn't find a description. Please reply with one.")
        try:
            msg = await bot.wait_for("message", timeout=30.0, check=lambda m: m.author == ctx.author and m.channel == ctx.channel)
            description = msg.content
            await msg.delete()
            await prompt.delete()
        except Exception as e:
            logger.warning(f"No description provided for {url}: {e}")
            await prompt.edit(content="No description provided. Skipping.")
            return

    if not favicon or not await is_valid_image(favicon):
        prompt = await ctx.send("I couldn't find a valid favicon. Please reply with a direct image URL (e.g. https://example.com/favicon.png).")
        try:
            msg = await bot.wait_for("message", timeout=30.0, check=lambda m: m.author == ctx.author and m.channel == ctx.channel)
            favicon = msg.content
            await msg.delete()
            await prompt.delete()
        except Exception as e:
            logger.warning(f"No favicon provided for {url}: {e}")
            await prompt.edit(content="No favicon provided. Using placeholder.")
            favicon = "https://static.thenounproject.com/png/4830268-200.png"

    embed = discord.Embed(title=url, url=url, description=description)
    embed.set_thumbnail(url=favicon)
    embed.add_field(name="Status", value="🟢 Online" if status else "🔴 Offline", inline=True)

    message = await ctx.send(embed=embed)

    cursor.execute("INSERT INTO websites (url, description, favicon, message_id, channel_id) VALUES (?, ?, ?, ?, ?)",
                   (url, description, favicon, message.id, ctx.channel.id))
    conn.commit()
    logger.info(f"Started monitoring {url}")

@bot.command()
async def nowebstatus(ctx, url: str):
    cursor.execute("SELECT message_id, channel_id FROM websites WHERE url = ?", (url,))
    row = cursor.fetchone()

    if not row:
        await ctx.send("That website isn't being monitored.", delete_after=5)
        return

    message_id, channel_id = row
    channel = bot.get_channel(channel_id)

    try:
        message = await channel.fetch_message(message_id)
        await message.delete()
    except Exception as e:
        logger.error(f"Failed to delete message for {url}: {e}")

    cursor.execute("DELETE FROM websites WHERE url = ?", (url,))
    conn.commit()

    await ctx.send(f"Stopped monitoring {url}.", delete_after=5)
    logger.info(f"Stopped monitoring {url}")

@bot.command()
async def clearwebstatus(ctx):
    cursor.execute("SELECT message_id, channel_id FROM websites")
    rows = cursor.fetchall()

    for message_id, channel_id in rows:
        channel = bot.get_channel(channel_id)
        if channel:
            try:
                message = await channel.fetch_message(message_id)
                await message.delete()
            except Exception as e:
                logger.error(f"Failed to delete message {message_id}: {e}")

    cursor.execute("DELETE FROM websites")
    conn.commit()

    await ctx.send("All monitored websites have been cleared.", delete_after=5)
    logger.info("Cleared all monitored websites")

#Scrape website for description and favicon
async def scrape_site(url):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=10) as response:
                html = await response.text()
                soup = BeautifulSoup(html, "html.parser")

                meta = soup.find("meta", attrs={"name": "description"})
                description = meta["content"] if meta and meta.get("content") else None

                icon = soup.find("link", rel=lambda x: x and "icon" in x.lower())
                favicon = icon["href"] if icon and icon.get("href") else None
                if favicon:
                    favicon = urljoin(url, favicon)
                    if not await is_valid_image(favicon):
                        favicon = None

                if not favicon:
                    fallback = urljoin(url, "/favicon.ico")
                    if await is_valid_image(fallback):
                        favicon = fallback

                return True, description, favicon
    except Exception as e:
        logger.warning(f"Failed to scrape {url}: {e}")
        return False, None, None

#Checks whether the favicon is a vailid image
async def is_valid_image(url):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=5) as response:
                content_type = response.headers.get("Content-Type", "")
                return response.status == 200 and "image" in content_type
    except:
        return False

@tasks.loop(minutes=5)
async def update_status():
    cursor.execute("SELECT url, description, favicon, message_id, channel_id FROM websites")
    for url, description, favicon, message_id, channel_id in cursor.fetchall():
        status, _, _ = await scrape_site(url)
        channel = bot.get_channel(channel_id)
        if not channel:
            continue
        try:
            message = await channel.fetch_message(message_id)
            embed = discord.Embed(title=url, url=url, description=description)
            embed.set_thumbnail(url=favicon or "https://static.thenounproject.com/png/778835-200.png")
            embed.add_field(name="Status", value="🟢 Online" if status else "🔴 Offline", inline=True)
            await message.edit(embed=embed)
            logger.info(f"Updated status for {url}")
        except Exception as e:
            logger.error(f"Failed to update {url}: {e}")

bot.run(os.getenv("DISCORD_TOKEN"))