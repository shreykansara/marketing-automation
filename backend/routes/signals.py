from fastapi import APIRouter
from backend.services.signals.fetchers import fetch_newsapi, fetch_rss
from backend.services.signals.processor import process_raw_signals
from backend.tasks.signals import run_enrichment_pipeline_sync
from backend.core.db import signals_collection
from backend.core.logger import get_logger

router = APIRouter()
logger = get_logger("routes.signals")

@router.post("/generate")
async def generate_signals():
    """
    Use Case 1: Synchronous Signal Generation.
    Fetch -> Process -> Enforce Unique Hash -> Enrich with AI -> Return Stats
    """
    logger.info("Synchronous signal generation triggered.")
    
    # 1. Fetch from sources
    news_signals = await fetch_newsapi()
    rss_signals = await fetch_rss(["https://techcrunch.com/feed/"])
    all_raw = news_signals + rss_signals
    
    # 2. Process & Store (Raw)
    stats = process_raw_signals(all_raw)
    new_ids = stats.get("new_ids", [])
    
    # 3. Synchronous AI Enrichment (Blocking)
    # The user is okay with the latency.
    for sid in new_ids:
        try:
            run_enrichment_pipeline_sync(sid)
        except Exception as e:
            logger.error(f"Sync enrichment failed for {sid}: {e}")
    
    return {
        "status": "success",
        "ingested": len(all_raw),
        "new_count": stats["new_count"],
        "duplicates_skipped": stats["duplicates"],
        "enriched_count": len(new_ids)
    }

@router.get("/")
async def get_signals():
    """
    Use Case 2: Display signals in decreasing order of relevance.
    """
    signals = list(
        signals_collection
        .find({"status": "enriched"})
        .sort("relevance_score", -1)
    )
    
    for s in signals:
        s["_id"] = str(s["_id"])
    
    return signals
