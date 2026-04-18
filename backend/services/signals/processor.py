from datetime import datetime, timezone
from pymongo.errors import DuplicateKeyError
from backend.core.db import signals_collection
from backend.core.logger import get_logger
from backend.services.signals.utils import generate_signal_hash, clean_text
from backend.tasks.signals import generate_embedding_task

logger = get_logger("signals.processor")

def process_raw_signals(raw_signals: list[dict]):
    """
    Pipeline: Normalize -> Hash -> Store -> Enqueue
    """
    processed_count = 0
    duplicate_count = 0
    
    for raw in raw_signals:
        title = clean_text(raw.get("title", ""))
        content = clean_text(raw.get("content", ""))
        url = raw.get("url", "")
        source = raw.get("source", "Unknown")
        
        if not title:
            continue
            
        # 1. Generate SHA-256 Hash
        sig_hash = generate_signal_hash(title, url, content)
        print(f"[HASH GENERATED] {sig_hash}")
        
        # 2. Prepare Base Schema (Aligned with Module 1)
        signal_doc = {
            "title": title,
            "content": content,
            "url": url,
            "source": source,
            "hash": sig_hash,
            "company_mentions": [],   # To be enriched
            "category": "pending",     # To be enriched
            "relevance_score": 0,      # To be enriched
            "published_at": raw.get("published_at"),
            "created_at": datetime.now(timezone.utc),
            "status": "raw" 
        }
        
        # 3. Store (Atomic Unique Check)
        try:
            result = signals_collection.insert_one(signal_doc)
            signal_id = result.inserted_id
            processed_count += 1
            print(f"[INSERT SUCCESS] id={signal_id}")
            
            # 4. Enqueue Intelligence Pipeline
            try:
                generate_embedding_task.delay(str(signal_id))
            except Exception as e:
                logger.error(f"CELERY DISPATCH FAILED: {e}")
            
        except DuplicateKeyError:
            duplicate_count += 1
            print(f"[DUPLICATE] hash={sig_hash}")
            continue
        except Exception as e:
            logger.error(f"INSERT ERROR: {e}")
            continue
            
    logger.info(f"Ingestion complete: {processed_count} new, {duplicate_count} duplicates.")
    return {"new": processed_count, "duplicates": duplicate_count}
