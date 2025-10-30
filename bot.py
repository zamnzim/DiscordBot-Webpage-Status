import os
import discord
from discord.ext import commands, tasks
import aiohttp
from bs4 import BeautifulSoup
from urllib.parse import urljoin

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

#Pull Environment Variables
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("DISCORD_CHANNEL_ID"))
WEBSITES = os.getenv("WEBSITES_TO_MONITOR", "").split(",")

message_refs = {}

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    check_websites.start()

@tasks.loop(minutes=5)
async def check_websites():
    channel = bot.get_channel(CHANNEL_ID)
    if not channel:
        print("Channel not found.")
        return

    for url in WEBSITES:
        url = url.strip()
        status, description, favicon_url = await get_website_info(url)
        embed = discord.Embed(title=url, url=url, description=description)
        embed.set_thumbnail(url=favicon_url or "https://via.placeholder.com/150")
        embed.add_field(name="Status", value="🟢 Online" if status else "🔴 Offline", inline=True)

        if url in message_refs:
            await message_refs[url].edit(embed=embed)
        else:
            msg = await channel.send(embed=embed)
            message_refs[url] = msg

# Gets wepsite information and favicon
async def get_website_info(url):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=10) as response:
                html = await response.text()
                soup = BeautifulSoup(html, "html.parser")

                description = soup.find("meta", attrs={"name": "description"})
                desc_text = description["content"] if description else "No description available."

                icon_link = soup.find("link", rel=lambda x: x and "icon" in x.lower())
                if icon_link and icon_link.get("href"):
                    favicon_url = icon_link["href"]
                    favicon_url = urljoin(url, favicon_url)
                else:
                    favicon_url = urljoin(url, "/favicon.ico")

                return True, desc_text, favicon_url
    except Exception:
        return False, "Site unreachable or error occurred.", None

bot.run(DISCORD_TOKEN)
