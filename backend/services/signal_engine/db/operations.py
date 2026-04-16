from datetime import datetime, timezone
from bson import ObjectId
from data.db import companies_collection, signals_collection, sync_state_collection
from services.signal_engine.utils.text_utils import normalize_company

def upsert_company(name: str) -> str:
    """
    If exists -> update last_seen
    If not -> create new
    Return string ID
    """
    normalized_name = normalize_company(name)
    now = datetime.now(timezone.utc).isoformat()
    
    company = companies_collection.find_one({"normalized_name": normalized_name})
    
    if company:
        companies_collection.update_one(
            {"_id": company["_id"]},
            {
                "$set": {"last_seen": now},
                "$inc": {"signals_count": 1}
            }
        )
        return str(company["_id"])
    else:
        result = companies_collection.insert_one({
            "name": name,
            "normalized_name": normalized_name,
            "aliases": [normalized_name],
            "created_at": now,
            "last_seen": now,
            "signals_count": 1
        })
        return str(result.inserted_id)

def is_duplicate_signal(fingerprint: str) -> bool:
    """
    Check if fingerprint exists in DB
    """
    count = signals_collection.count_documents({"fingerprint": fingerprint}, limit=1)
    return count > 0

def store_signal(signal_data: dict) -> None:
    """
    Store signal in DB
    """
    signals_collection.insert_one(signal_data)
    
def get_last_fetched_timestamp(source: str) -> str | None:
    state = sync_state_collection.find_one({"source": source})
    if state:
        return state.get("last_fetched_timestamp")
    return None

def set_last_fetched_timestamp(source: str, timestamp: str) -> None:
    sync_state_collection.update_one(
        {"source": source},
        {"$set": {"last_fetched_timestamp": timestamp}},
        upsert=True
    )
