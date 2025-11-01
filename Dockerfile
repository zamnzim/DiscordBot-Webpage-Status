FROM python:3.11-slim

WORKDIR /app

RUN pip install discord.py aiohttp beautifulsoup4

COPY bot.py .


CMD ["python", "bot.py"]
