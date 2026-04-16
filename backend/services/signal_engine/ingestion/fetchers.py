import os
import httpx
import feedparser
from datetime import datetime, timezone
from dateutil import parser as date_parser
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type
from services.signal_engine.utils.logger import get_logger

logger = get_logger("signal_engine.fetchers")

# Define exceptions to retry on.
RETRY_EXCEPTIONS = (httpx.RequestError, httpx.TimeoutException)

@retry(wait=wait_exponential(multiplier=1, min=2, max=10), stop=stop_after_attempt(3), retry=retry_if_exception_type(RETRY_EXCEPTIONS))
async def _fetch_url_async(url: str, params: dict = None, headers: dict = None) -> httpx.Response:
    async with httpx.AsyncClient(timeout=10.0) as client:
        return await client.get(url, params=params, headers=headers)

@retry(wait=wait_exponential(multiplier=1, min=2, max=10), stop=stop_after_attempt(3))
def _fetch_rss_sync(url: str):
    return feedparser.parse(url)

async def fetch_newsapi(last_fetched: str | None = None) -> list[dict]:
    api_key = os.getenv("NEWS_API_KEY")
    if not api_key:
        logger.error("NEWS_API_KEY is not set. Skipping NewsAPI fetch.")
        return []
        
    logger.info("Fetching signals from NewsAPI...")
    
    url = "https://newsapi.org/v2/everything"
    
    # We query important keywords in the business world rather than generic
    query = "(funding OR raises OR secures OR launches OR partnership)"
    
    params = {
        "q": query,
        "language": "en",
        "sortBy": "publishedAt",
        "pageSize": 50,
        "apiKey": api_key
    }
    
    # If we have a last fetched timestamp, we only fetch newer if API supports it, 
    # but NewsAPI free tier limits 'from' parameter. We will just use it to filter post-fetch.
    
    try:
        response = await _fetch_url_async(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        articles = data.get("articles", [])
        signals = []
        
        for article in articles:
            pub_date = article.get("publishedAt")
            
            # Idempotency check client-side
            if last_fetched and pub_date:
                try:
                    if date_parser.parse(pub_date) <= date_parser.parse(last_fetched):
                        continue
                except Exception:
                    pass

            text_content = f"{article.get('title', '')}. {article.get('description', '')}"
            
            signals.append({
                "text": text_content,
                "source": "NewsAPI",
                "source_priority": 0.9,
                "source_url": article.get("url"),
                "timestamp": pub_date or datetime.now(timezone.utc).isoformat()
            })
            
        logger.info(f"Fetched {len(signals)} new signals from NewsAPI.")
        return signals
        
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error from NewsAPI: {e}")
        return []
    except Exception as e:
        logger.error(f"Unexpected error in fetch_newsapi: {e}")
        return []


async def fetch_rss(last_fetched: str | None = None) -> list[dict]:
    logger.info("Fetching signals from RSS feeds...")
    
    rss_feeds = [
        "https://techcrunch.com/feed/",
        "https://www.prweb.com/rss2/tech.xml"
    ]
    
    signals = []
    
    for feed_url in rss_feeds:
        try:
            feed = _fetch_rss_sync(feed_url)
            source_name = feed.feed.title if hasattr(feed, "feed") and hasattr(feed.feed, "title") else "RSS"
            
            for entry in feed.entries:
                # Need to determine published date
                pub_date_raw = None
                if hasattr(entry, 'published'):
                    pub_date_raw = entry.published
                elif hasattr(entry, 'updated'):
                    pub_date_raw = entry.updated
                    
                pub_date = None
                if pub_date_raw:
                    try:
                        pub_date = date_parser.parse(pub_date_raw).astimezone(timezone.utc).isoformat()
                    except Exception:
                        pass
                
                if not pub_date:
                    pub_date = datetime.now(timezone.utc).isoformat()
                    
                # Idempotency check
                if last_fetched and pub_date:
                    try:
                        if date_parser.parse(pub_date) <= date_parser.parse(last_fetched):
                            continue
                    except Exception:
                        pass

                title = entry.title if hasattr(entry, 'title') else ''
                description = entry.description if hasattr(entry, 'description') else ''
                
                # Strip HTML from description using basic regex
                import re
                description = re.sub('<[^<]+?>', '', description)
                
                text_content = f"{title}. {description}"
                
                signals.append({
                    "text": text_content,
                    "source": f"RSS: {source_name}",
                    "source_priority": 0.7,
                    "source_url": entry.link if hasattr(entry, 'link') else None,
                    "timestamp": pub_date
                })
                
        except Exception as e:
            logger.error(f"Error fetching RSS {feed_url}: {e}")
            
    logger.info(f"Fetched {len(signals)} new signals from RSS feeds.")
    return signals
