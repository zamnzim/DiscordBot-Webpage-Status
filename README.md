# DiscordBot-Webpage-Status
A Discord bot that monitors the online status of websites, displays their metadata, and updates their status periodically using embedded messages.

All website data is stored in a SQL database with Message ID and Channel ID. The Bot will periodicaly scape the databse and vailidate if the website is accessable or not and update the status message.

![Example Running](https://github.com/user-attachments/assets/f1ffce23-eb3f-47f9-b313-0faf2f06a139)

# Docker Run
```
docker run -d \
  --name discordbot-webpage-status \
  --restart unless-stopped \
  -e DISCORD_TOKEN=your_discord_bot_token_here \
  -it websites-data:/app/data \
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
