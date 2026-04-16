from fastapi import APIRouter, BackgroundTasks
from data.db import signals_collection
from services.signal_engine.processor import run_ingestion_pipeline_async

router = APIRouter(prefix="/api/signals", tags=["signals"])

@router.get("")
def get_signals():
    # Fetch all signals from the database
    signals = list(signals_collection.find().sort("timestamp", -1))
    
    # Remove the internal MongoDB ObjectId before returning
    for signal in signals:
        signal.pop("_id", None)
        
    return {"data": signals}

@router.post("/ingest")
async def trigger_ingestion():
    # Trigger the ingestion process manually using the real pipeline
    result = await run_ingestion_pipeline_async()
    return result
