from fastapi import APIRouter
from data.db import signals_collection
from services.ingestion import run_ingestion

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
def trigger_ingestion():
    # Trigger the ingestion process manually
    result = run_ingestion()
    
    # We remove the MongoDB ObjectId from the generated signals mapping just in case
    for signal in result["signals"]:
        if "_id" in signal:
            signal.pop("_id", None)
            
    return result
