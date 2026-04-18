import os
import httpx
import feedparser
from datetime import datetime, timezone
from dateutil import parser as date_parser
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type
from backend.core.logger import get_logger

logger = get_logger("signals.fetchers")

RETRY_EXCEPTIONS = (httpx.RequestError, httpx.TimeoutException)

@retry(wait=wait_exponential(multiplier=1, min=2, max=10), stop=stop_after_attempt(3), retry=retry_if_exception_type(RETRY_EXCEPTIONS))
async def _fetch_url(url: str, params: dict = None) -> httpx.Response:
    async with httpx.AsyncClient(timeout=10.0) as client:
        return await client.get(url, params=params)

async def fetch_newsapi(q: str = "funding OR raises") -> list[dict]:
    api_key = os.getenv("NEWS_API_KEY")
    if not api_key:
        logger.error("NEWS_API_KEY is missing")
        return []

    url = "https://newsapi.org/v2/everything"
    params = {"q": q, "language": "en", "sortBy": "publishedAt", "pageSize": 20, "apiKey": api_key}
    
    try:
        resp = await _fetch_url(url, params)
        resp.raise_for_status()
        articles = resp.json().get("articles", [])
        
        signals = []
        for a in articles:
            signals.append({
                "title": a.get("title"),
                "content": a.get("description"),
                "url": a.get("url"),
                "source": a.get("source", {}).get("name", "NewsAPI"),
                "published_at": a.get("publishedAt")
            })
        return signals
    except Exception as e:
        logger.error(f"NewsAPI fetch error: {e}")
        return []

async def fetch_rss(feeds: list[str]) -> list[dict]:
    all_signals = []
    async with httpx.AsyncClient(timeout=10.0) as client:
        for url in feeds:
            try:
                resp = await client.get(url)
                resp.raise_for_status()
                feed = feedparser.parse(resp.content)
                for entry in feed.entries:
                    all_signals.append({
                        "title": entry.get("title"),
                        "content": entry.get("description"),
                        "url": entry.get("link"),
                        "source": feed.feed.get("title", "RSS"),
                        "published_at": entry.get("published") or entry.get("updated")
                    })
            except Exception as e:
                logger.error(f"RSS fetch error for {url}: {e}")
    return all_signals
