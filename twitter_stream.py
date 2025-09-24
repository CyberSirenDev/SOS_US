import os
import aiohttp
import asyncio
from dotenv import load_dotenv

load_dotenv()
BEARER_TOKEN = os.getenv('AAAAAAAAAAAAAAAAAAAAAOhk4QEAAAAAm5Dh9yWwD1oqPuoiNR%2FcOK83egk%3DlVGJ6UHNFhkzHW4d0yw2LCnbe0SP7yqDgsWbvKcSAwz0aqWBjv')

STREAM_URL = "https://api.twitter.com/2/tweets/search/stream"

async def stream_tweets():
    headers = {
        "Authorization": f"Bearer {BEARER_TOKEN}",
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(STREAM_URL, headers=headers) as resp:
            async for line in resp.content:
                if line:
                    tweet = line.decode('utf-8').strip()
                    print("New Tweet:", tweet)  # Here, send to your analyzer

# To run:
# asyncio.run(stream_tweets())