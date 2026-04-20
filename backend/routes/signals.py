from fastapi import APIRouter, BackgroundTasks
from bson import ObjectId
from backend.services.signals.fetchers import fetch_newsapi, fetch_rss
from backend.services.signals.processor import process_raw_signals
from backend.tasks.signals import run_enrichment_pipeline_sync, process_enrichment_queue
from backend.core.db import signals_collection
from backend.core.logger import get_logger

router = APIRouter()
logger = get_logger("routes.signals")

@router.post("/generate")
async def generate_signals(background_tasks: BackgroundTasks):
    """
    Synchronous Signal Generation + Background AI Enrichment.
    1. Fetch new news/rss.
    2. Identify stalled signals for recovery.
    3. Trigger background enrichment.
    """
    logger.info("Signal generation + Auto-Recovery triggered.")
    
    # 1. Fetch & Store New
    news_signals = await fetch_newsapi()
    rss_signals = await fetch_rss(["https://techcrunch.com/feed/"])
    all_raw = news_signals + rss_signals
    stats = process_raw_signals(all_raw)
    new_ids = stats.get("new_ids", [])
    
    # 2. Identify Stalled Signals (Self-Healing)
    stalled_docs = list(signals_collection.find({
        "status": {"$in": ["raw", "embedded", "enrichment_failed"]}
    }))
    stalled_ids = [str(d["_id"]) for d in stalled_docs]
    
    # Combine lists for enrichment attempt
    to_enrich = list(set(new_ids + stalled_ids))
    
    # 3. Offload AI Enrichment to Background
    if to_enrich:
        background_tasks.add_task(process_enrichment_queue, to_enrich)
    
    return {
        "status": "success",
        "ingested": len(all_raw),
        "new_count": stats["new_count"],
        "duplicates_skipped": stats["duplicates"],
        "background_queue_count": len(to_enrich)
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
