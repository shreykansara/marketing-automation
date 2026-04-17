import asyncio
import os
import sys
from dotenv import load_dotenv

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

load_dotenv(dotenv_path='backend/.env')

from services.signal_engine.ingestion.fetchers import fetch_newsapi, fetch_rss

async def main():
    print("Testing concurrent ingestion...")
    import time
    start_time = time.time()
    
    # Run fetchers concurrently
    news_task = asyncio.create_task(fetch_newsapi())
    rss_task = asyncio.create_task(fetch_rss())
    
    news_signals, rss_signals = await asyncio.gather(news_task, rss_task)
    
    end_time = time.time()
    
    print(f"\nResults:")
    print(f"NewsAPI signals: {len(news_signals)}")
    print(f"RSS signals: {len(rss_signals)}")
    print(f"Total time taken: {end_time - start_time:.2f} seconds")
    
    if len(news_signals) > 0 or len(rss_signals) > 0:
        print("\nSUCCESS: Signals fetched successfully.")
    else:
        print("\nWARNING: No signals fetched. Check your NewsAPI key and internet connection.")

if __name__ == "__main__":
    asyncio.run(main())
