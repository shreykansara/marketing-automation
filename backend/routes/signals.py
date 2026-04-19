from fastapi import APIRouter
from bson import ObjectId
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
    Synchronous Signal Generation + Auto-Recovery.
    1. Fetch new news/rss.
    2. Identify stalled signals for retry.
    3. Process new and recovered signals.
    """
    logger.info("Signal generation + Auto-Recovery triggered.")
    
    # 1. Fetch & Store New
    news_signals = await fetch_newsapi()
    rss_signals = await fetch_rss(["https://techcrunch.com/feed/"])
    all_raw = news_signals + rss_signals
    stats = process_raw_signals(all_raw)
    new_ids = stats.get("new_ids", [])
    
    # 2. Identify Stalled Signals (Self-Healing)
    # Recover any that are not 'enriched' or 'pending' (Wait, category was pending, status was embedded/raw)
    stalled_docs = list(signals_collection.find({
        "status": {"$in": ["raw", "embedded", "enrichment_failed"]}
    }))
    stalled_ids = [str(d["_id"]) for d in stalled_docs]
    
    # Combine lists for enrichment attempt
    to_enrich = list(set(new_ids + stalled_ids))
    
    # 3. Synchronous AI Enrichment
    for sid in to_enrich:
        try:
            run_enrichment_pipeline_sync(sid)
        except Exception as e:
            logger.error(f"Recovery enrichment failed for {sid}: {e}")
    
    # 4. Final Count of Enriched Signals
    # (Checking those that were actually part of this session's enrichment attempt)
    final_enriched = signals_collection.count_documents({
        "_id": {"$in": [ObjectId(sid) for sid in to_enrich]},
        "status": "enriched"
    })
    
    return {
        "status": "success",
        "ingested": len(all_raw),
        "new_count": stats["new_count"],
        "duplicates_skipped": stats["duplicates"],
        "enriched_count": final_enriched
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
