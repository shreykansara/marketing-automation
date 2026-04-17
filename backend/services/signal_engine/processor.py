import asyncio
from datetime import datetime, timezone
import uuid

from services.signal_engine.utils.logger import get_logger
from services.signal_engine.utils.text_utils import extract_company, normalize_company, generate_fingerprint
from services.signal_engine.classifier.rules import classify_text
from services.signal_engine.db.operations import upsert_company, is_duplicate_signal, store_signal, get_last_fetched_timestamp, set_last_fetched_timestamp
from services.signal_engine.ingestion.fetchers import fetch_newsapi, fetch_rss

logger = get_logger("signal_engine.processor")

def process_signal(raw_item: dict) -> dict | None:
    """
    Process a raw fetched item:
    1. Extract company
    2. Normalize company
    3. Upsert company
    4. Classify text
    5. Generate fingerprint
    6. Deduplicate
    7. Store signal
    """
    text = raw_item.get("text", "")
    source = raw_item.get("source", "Unknown")
    timestamp = raw_item.get("timestamp")
    source_priority = raw_item.get("source_priority", 0.5)
    source_url = raw_item.get("source_url")
    
    # 1. Extract company
    company_name = extract_company(text)
    if not company_name or company_name == "Unknown":
        logger.info(f"Using fallback entity for signal from {source} - extracted: '{company_name}'")
        company_name = company_name or "Unknown"
        
    # 2. Normalize and 3. Upsert company
    company_id = upsert_company(company_name)
    normalized_name = normalize_company(company_name)
    
    # 4. Classify text
    signal_types = classify_text(text)
    if not signal_types:
        logger.debug(f"Signal has no matched types, storing as low confidence: {text[:50]}...")
    
    # 5. Generate fingerprint
    fingerprint = generate_fingerprint(company_name, text)
    
    # 6. Check duplicate
    if is_duplicate_signal(fingerprint):
        logger.debug(f"Duplicate signal detected for {company_name} - Fingerprint {fingerprint}")
        return None
        
    # 7. Store signal
    signal_data = {
        "id": str(uuid.uuid4()),
        "company_id": str(company_id),
        "company_name": company_name,
        "company_normalized": normalized_name,
        "signal_types": signal_types,
        "raw_text": text,
        "source": source,
        "source_priority": source_priority,
        "source_url": source_url,
        "timestamp": timestamp,
        "fingerprint": fingerprint,
        "confidence": 0.8 if signal_types else 0.2,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    store_signal(signal_data)
    logger.info(f"Ingested new signal for {company_name} from {source}")
    
    # We remove _id because MongoDB adds it during insert_one but it's not JSON serializable easily if returned directly
    signal_data.pop("_id", None)
    return signal_data

async def run_ingestion_pipeline_async() -> dict:
    """
    Main orchestrator for fetching and processing.
    """
    logger.info("Starting run_ingestion_pipeline...")
    
    # Get last fetched states
    news_last_fetched = get_last_fetched_timestamp("newsapi")
    rss_last_fetched = get_last_fetched_timestamp("rss")
    
    # Fetch data concurrently
    news_task = asyncio.create_task(fetch_newsapi(news_last_fetched))
    rss_task = asyncio.create_task(fetch_rss(rss_last_fetched))
    
    news_signals, rss_signals = await asyncio.gather(news_task, rss_task)
    
    all_raw_signals = news_signals + rss_signals
    
    processed_count = 0
    new_signals = []
    
    for raw in all_raw_signals:
        result = process_signal(raw)
        if result:
            new_signals.append(result)
            processed_count += 1
            
    # Update max timestamp for idempotency
    if news_signals:
        max_ts = max([s["timestamp"] for s in news_signals])
        set_last_fetched_timestamp("newsapi", max_ts)
        
    if rss_signals:
        max_ts = max([s["timestamp"] for s in rss_signals])
        set_last_fetched_timestamp("rss", max_ts)
            
    logger.info(f"Pipeline completed. Processed {processed_count} new signals out of {len(all_raw_signals)} raw fetched.")
    
    return {
        "message": f"Successfully ingested {processed_count} new signals.",
        "processed_count": processed_count,
        "signals": new_signals
    }

def run_ingestion_pipeline_sync() -> dict:
    """
    Sync wrapper to be called from FastAPI endpoints without blocking event loop 
    if ran in threadpool, or just using asyncio.run. Fast API endpoints can be async.
    We will just use this to cleanly run it if someone wants a sync version.
    """
    return asyncio.run(run_ingestion_pipeline_async())
