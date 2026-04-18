from fastapi import APIRouter
from backend.services.signals.fetchers import fetch_newsapi, fetch_rss
from backend.services.signals.processor import process_raw_signals
from backend.core.db import signals_collection
from backend.core.logger import get_logger

router = APIRouter()
logger = get_logger("routes.signals")


@router.post("/ingest")
async def ingest_signals():
    """Trigger signal ingestion from NewsAPI and RSS."""
    logger.info("Manual ingestion triggered.")
    
    # 1. Fetch signals
    news_signals = await fetch_newsapi()
    rss_signals = await fetch_rss(["https://techcrunch.com/feed/"])
    
    all_raw = news_signals + rss_signals
    
    # 2. Process (hash, store, enqueue async tasks)
    stats = process_raw_signals(all_raw)
    
    return {
        "status": "success",
        "fetch_count": len(all_raw),
        "new_signals": stats["new"],
        "duplicates_skipped": stats["duplicates"]
    }


@router.get("/")
async def get_signals(limit: int = 50, status: str = None):
    """Fetch stored signals with optional status filter."""
    query = {}
    
    if status:
        query["status"] = status
    
    signals = list(
        signals_collection
        .find(query)
        .sort("created_at", -1)
        .limit(limit)
    )
    
    for s in signals:
        s["_id"] = str(s["_id"])
    
    return signals
