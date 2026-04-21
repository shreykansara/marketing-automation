import os
import httpx
import hashlib
import datetime
from typing import List, Dict, Any
from backend.core.logger import get_logger

logger = get_logger("fetchers")

class NewsFetcher:
    def __init__(self):
        self._api_key = None
        self.base_url = "https://newsapi.org/v2/everything"
        
    @property
    def api_key(self):
        if not self._api_key:
            key = os.getenv("NEWS_API_KEY")
            if key:
                # Strip dashes just in case the user provided a UUID format
                self._api_key = key.replace("-", "").strip()
        return self._api_key
        
    def _generate_hash(self, text: str) -> str:
        return hashlib.sha256(text.encode()).hexdigest()

    async def fetch_signals(self, queries: List[str] = ["Fintech India", "Banking Technology India"]) -> List[Dict[str, Any]]:
        if not self.api_key:
            logger.error("NEWS_API_KEY not found in environment.")
            return []

        all_signals = []
        async with httpx.AsyncClient() as client:
            for query in queries:
                try:
                    logger.info(f"Fetching signals for query: {query}")
                    response = await client.get(
                        self.base_url,
                        params={
                            "q": query,
                            "apiKey": self.api_key,
                            "pageSize": 5,
                            "sortBy": "publishedAt",
                            "language": "en"
                        }
                    )
                    
                    logger.info(f"Raw API Response for {query}: {response.text}")
                    
                    if response.status_code == 200:
                        data = response.json()
                        articles = data.get("articles", [])
                        
                        for art in articles:
                            # Basic signal structure
                            signal = {
                                "title": art.get("title"),
                                "content": art.get("description") or art.get("content"),
                                "source": art.get("source", {}).get("name", "NewsAPI"),
                                "url": art.get("url"),
                                "published_at": art.get("publishedAt"),
                                "created_at": datetime.datetime.now(),
                                "hash": self._generate_hash(art.get("url", "") + (art.get("title") or "")),
                                "status": "raw",
                                "company_ids": [],
                                "relevance_score": None,
                                "category": "general"
                            }
                            all_signals.append(signal)
                    else:
                        error_data = {}
                        try:
                            error_data = response.json()
                        except:
                            pass
                        logger.error(f"NewsAPI error {response.status_code} for {query}: {error_data.get('message', response.text)}")
                except Exception as e:
                    logger.error(f"Failed to fetch signals for {query}: {str(e)}")
                    
        return all_signals

news_fetcher = NewsFetcher()
