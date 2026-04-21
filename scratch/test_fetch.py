import asyncio
import os
from dotenv import load_dotenv
from backend.services.signals.fetchers import news_fetcher

load_dotenv()

async def test():
    print(f"API KEY: {os.getenv('NEWS_API_KEY')[:5]}...")
    signals = await news_fetcher.fetch_signals()
    print(f"Fetched {len(signals)} signals.")
    for s in signals[:2]:
        print(f"- {s['title']}")

if __name__ == "__main__":
    asyncio.run(test())
