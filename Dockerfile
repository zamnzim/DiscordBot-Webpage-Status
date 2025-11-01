FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install discord.py aiohttp beautifulsoup4

COPY bot.py .

CMD ["python", "bot.py"]