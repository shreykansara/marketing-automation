from backend.core.db import signals_collection, companies
from bson import ObjectId
from fastapi import APIRouter, HTTPException, BackgroundTasks
from backend.services.signals.fetchers import news_fetcher
from backend.tasks.signals import signal_pipeline

router = APIRouter()

@router.post("/generate")
async def generate_signals(background_tasks: BackgroundTasks):
    """
    Real-time signal ingestion from NewsAPI.
    """
    raw_signals = await news_fetcher.fetch_signals()
    
    saved_count = 0
    for s in raw_signals:
        try:
            # Atomic insertion with hash uniqueness check
            res = signals_collection.insert_one(s)
            saved_count += 1
            # Queue for enrichment
            background_tasks.add_task(signal_pipeline.process_signal, res.inserted_id)
        except:
            pass # Duplicate signal
            
    return {"ingested_count": saved_count, "message": f"Successfully ingested {saved_count} new market signals."}

@router.post("/{signal_id}/retry")
async def retry_signal(signal_id: str, background_tasks: BackgroundTasks):
    """
    Manually retry enrichment for a failed or raw signal.
    """
    obj_id = ObjectId(signal_id)
    signal = signals_collection.find_one({"_id": obj_id})
    if not signal:
        raise HTTPException(status_code=404, detail="Signal not found")
        
    signals_collection.update_one({"_id": obj_id}, {"$set": {"status": "processing"}})
    background_tasks.add_task(signal_pipeline.process_signal, obj_id)
    
    return {"status": "queued"}

@router.get("/")
async def get_signals():
    """
    Use Case 2: Display signals with hydrated company names.
    Includes raw and failed signals.
    """
    pipeline = [
        # Show all signals now
        {"$sort": {"relevance_score": -1}},
        {
            "$lookup": {
                "from": "companies",
                "localField": "company_ids",
                "foreignField": "_id",
                "as": "companies_data"
            }
        }
    ]
    
    signals = list(signals_collection.aggregate(pipeline))
    
    for s in signals:
        s["_id"] = str(s["_id"])
        s["company_ids"] = [str(cid) for cid in s.get("company_ids", [])]
        s["company_names"] = [c.get("name") for c in s.get("companies_data", [])]
        s.pop("companies_data", None)
    
    return signals
