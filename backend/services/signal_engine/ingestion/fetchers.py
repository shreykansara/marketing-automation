import os
import httpx
import feedparser
from datetime import datetime, timezone
from dateutil import parser as date_parser
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type
from dotenv import load_dotenv
from services.signal_engine.utils.logger import get_logger

load_dotenv()
logger = get_logger("signal_engine.fetchers")

# Define exceptions to retry on.
RETRY_EXCEPTIONS = (httpx.RequestError, httpx.TimeoutException)

@retry(wait=wait_exponential(multiplier=1, min=2, max=10), stop=stop_after_attempt(3), retry=retry_if_exception_type(RETRY_EXCEPTIONS))
async def _fetch_url_async(url: str, params: dict = None, headers: dict = None) -> httpx.Response:
    async with httpx.AsyncClient(timeout=10.0) as client:
        # Sanitize logs by removing apiKey from the URL representation if present
        log_url = url
        if params and "apiKey" in params:
            params_copy = params.copy()
            params_copy["apiKey"] = "REDACTED"
            # httpx doesn't have a simple way to get URL with redacted params without building it
        
        return await client.get(url, params=params, headers=headers)

async def _fetch_single_rss_async(feed_url: str, last_fetched: str | None = None) -> list[dict]:
    """Helper to fetch and parse a single RSS feed asynchronously."""
    last_fetched_dt = date_parser.parse(last_fetched).astimezone(timezone.utc) if last_fetched else None
    
    try:
        response = await _fetch_url_async(feed_url)
        response.raise_for_status()
        
        # Use response.content (bytes) so feedparser can detect encoding from XML prolog correctly
        feed = feedparser.parse(response.content)
        source_name = feed.feed.title if hasattr(feed, "feed") and hasattr(feed.feed, "title") else "RSS"
        
        signals = []
        for entry in feed.entries:
            # Determine published date
            pub_date_raw = entry.get('published') or entry.get('updated')
            pub_date_dt = None
            
            if pub_date_raw:
                try:
                    pub_date_dt = date_parser.parse(pub_date_raw).astimezone(timezone.utc)
                except Exception:
                    pass
            
            if not pub_date_dt:
                pub_date_dt = datetime.now(timezone.utc)
                
            # Idempotency check using datetime objects
            if last_fetched_dt and pub_date_dt <= last_fetched_dt:
                continue

            pub_date_iso = pub_date_dt.strftime('%Y-%m-%dT%H:%M:%SZ')
            title = entry.get('title', '')
            description = entry.get('description', '')
            
            # Strip HTML from description
            import re
            description = re.sub('<[^<]+?>', '', description)
            
            signals.append({
                "text": f"{title}. {description}",
                "source": f"RSS: {source_name}",
                "source_priority": 0.7,
                "source_url": entry.get('link'),
                "timestamp": pub_date_iso
            })
        return signals
    except Exception as e:
        # Avoid logging full URL if it might contain secrets (though RSS usually doesn't)
        logger.error(f"Error fetching RSS: {e}")
        return []

async def fetch_newsapi(last_fetched: str | None = None) -> list[dict]:
    api_key = os.getenv("NEWS_API_KEY")
    last_fetched_dt = date_parser.parse(last_fetched).astimezone(timezone.utc) if last_fetched else None

    if not api_key:
        logger.error("NEWS_API_KEY is not set. Check your .env file.")
        return []
    else:
        logger.debug(f"NEWS_API_KEY found (length: {len(api_key)})")
        
    logger.info("Fetching signals from NewsAPI...")
    url = "https://newsapi.org/v2/everything"
    params = {
        "q": "(funding OR raises OR secures OR launches OR partnership)",
        "language": "en",
        "sortBy": "publishedAt",
        "pageSize": 50,
        "apiKey": api_key
    }
    
    try:
        # Use _fetch_url_async which handles retries
        response = await _fetch_url_async(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        articles = data.get("articles", [])
        signals = []
        
        for article in articles:
            pub_date_raw = article.get("publishedAt")
            pub_date_dt = None
            
            if pub_date_raw:
                try:
                    pub_date_dt = date_parser.parse(pub_date_raw).astimezone(timezone.utc)
                except Exception:
                    pass
            
            if last_fetched_dt and pub_date_dt and pub_date_dt <= last_fetched_dt:
                continue

            timestamp = pub_date_dt.strftime('%Y-%m-%dT%H:%M:%SZ') if pub_date_dt else datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
            
            signals.append({
                "text": f"{article.get('title', '')}. {article.get('description', '')}",
                "source": "NewsAPI",
                "source_priority": 0.9,
                "source_url": article.get("url"),
                "timestamp": timestamp
            })
            
        logger.info(f"Fetched {len(signals)} new signals from NewsAPI.")
        return signals
        
    except Exception as e:
        # Catch errors but ensure we don't leak the apiKey from the parameters if raised in exception
        msg = str(e)
        if api_key in msg:
            msg = msg.replace(api_key, "REDACTED")
        logger.error(f"Error in fetch_newsapi: {msg}")
        return []

import asyncio

async def fetch_rss(last_fetched: str | None = None) -> list[dict]:
    logger.info("Fetching signals from RSS feeds...")
    rss_feeds = [
        "https://techcrunch.com/feed/",
        "https://feeds.feedburner.com/venturebeat/SZYF"
    ]
    
    tasks = [_fetch_single_rss_async(url, last_fetched) for url in rss_feeds]
    results = await asyncio.gather(*tasks)
    return [item for sublist in results for item in sublist]
