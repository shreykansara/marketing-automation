from datetime import datetime, timezone
from pymongo.errors import DuplicateKeyError
from backend.core.db import signals_collection
from backend.core.logger import get_logger
from backend.services.signals.utils import generate_signal_hash, clean_text
from backend.tasks.signals import generate_embedding_task

logger = get_logger("signals.processor")

def process_raw_signals(raw_signals: list[dict]):
    """
    Pipeline: Normalize -> Hash -> Store -> Return IDs (for sync processing)
    """
    processed_count = 0
    duplicate_count = 0
    new_ids = []
    
    for raw in raw_signals:
        title = clean_text(raw.get("title", ""))
        content = clean_text(raw.get("content", ""))
        url = raw.get("url", "")
        source = raw.get("source", "Unknown")
        
        if not title:
            continue
            
        # 1. Generate SHA-256 Hash
        sig_hash = generate_signal_hash(title, url, content)
        
        # 2. Prepare Base Schema
        signal_doc = {
            "title": title,
            "content": content,
            "url": url,
            "source": source,
            "hash": sig_hash,
            "company_names": [],
            "category": "pending",
            "relevance_score": 0,
            "published": raw.get("published_at"),
            "created_at": datetime.now(timezone.utc),
            "status": "raw" 
        }
        
        # 3. Store
        try:
            result = signals_collection.insert_one(signal_doc)
            signal_id = result.inserted_id
            new_ids.append(str(signal_id))
            processed_count += 1
            
            # Note: We don't delay the task here anymore if we want the route to be sync.
            # The route will handle the sequential calls.
            
        except DuplicateKeyError:
            duplicate_count += 1
            continue
        except Exception as e:
            logger.error(f"INSERT ERROR: {e}")
            continue
            
    logger.info(f"Ingestion complete: {processed_count} new, {duplicate_count} duplicates.")
    return {"new_count": processed_count, "new_ids": new_ids, "duplicates": duplicate_count}
