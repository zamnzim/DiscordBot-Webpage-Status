# DiscordBot-Webpage-Status
A Discord bot that monitors the online status of websites, displays their metadata, and updates their status periodically using embedded messages.

All website data is stored in a SQLite database, including the message ID and channel ID. The bot periodically scans the database, checks if each website is accessible, and updates the corresponding status message in Discord.

![Example Running](https://github.com/user-attachments/assets/f1ffce23-eb3f-47f9-b313-0faf2f06a139)

# Bot Commands
| Comand | Dscription | Example Usage |
| -------- | ---------- |---------- |
| !webstatus | Adds website to databse | !webstatus https://github.com
| !nowebstatus| Reomove website from databse. Deletes message from server. | !nowebstatus https://github.com
| !clearwebstatus | Delete all monitored websites from database and server | !clearwebstatus

> ⚠️ **Note:** All websites must be in the format `https://website.com`

# Usage
When you add a website using `!webstatus`, the bot will scrape the website metadata and retrieve its description and favicon.

- If no description is available, the bot will prompt you to provide one.
- If no favicon is available or valid, the bot will ask you to provide a direct `.png` image URL.

> ⚠️ **Note:** The favicon URL must point directly to a `.png` image file.

> ⚠️ **Note:** This tends to fail with google websites. Currently working on a fix. The script thinks the google favicon is valid but no image is availble.

# Docker Run
```
docker run -d \
  --name discordbot-webpage-status \
  --restart unless-stopped \
  -e DISCORD_TOKEN=your_discord_bot_token_here \
  -v websites-data:/app/data \
  ghcr.io/zamnzim/discordbot-webpage-status:latest
```
# Docker Compose
```yaml
services:
  discordbot-webpage-status:
    image: ghcr.io/zamnzim/discordbot-webpage-status:latest
    container_name: discordbot-webpage-status
    environment:
      - DISCORD_TOKEN=your_discord_bot_token_here
    volumes:
      - websites-data:/app/data #Location for SQL Database
    restart: unless-stopped

volumes:
  websites-data:
```
