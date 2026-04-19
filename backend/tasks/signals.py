from bson import ObjectId
from datetime import datetime, timezone
from backend.core.celery_app import celery_app
from backend.core.db import signals_collection, companies
from backend.core.llm import llm_service
from backend.core.logger import get_logger

logger = get_logger("tasks.signals")

def run_enrichment_pipeline_sync(signal_id: str):
    """
    Synchronous execution of the entire signal intelligence pipeline.
    Used by the POST /signals/generate endpoint.
    """
    generate_embedding_task(signal_id, sync=True)
    enrich_signal_task(signal_id, sync=True)

@celery_app.task(name="generate_embedding_task")
def generate_embedding_task(signal_id: str, sync: bool = False):
    """
    Step 2: Generate embedding for the signal.
    """
    try:
        signal = signals_collection.find_one({"_id": ObjectId(signal_id)})
        if not signal: 
            return
        
        text = f"{signal.get('title', '')} {signal.get('content', '')}"
        embedding = llm_service.get_embedding(text)
        
        signals_collection.update_one(
            {"_id": ObjectId(signal_id)},
            {"$set": {
                "embedding": embedding,
                "status": "embedded"
            }}
        )
        
        if not sync:
            enrich_signal_task.delay(signal_id)
        
    except Exception as e:
        logger.error(f"Embedding generation failed for {signal_id}: {e}")

@celery_app.task(name="enrich_signal_task")
def enrich_signal_task(signal_id: str, sync: bool = False):
    """
    Step 3: Extract company mentions and category using LLM.
    """
    try:
        signal = signals_collection.find_one({"_id": ObjectId(signal_id)})
        if not signal:
            return
            
        text = f"{signal.get('title', '')}\n{signal.get('content', '')}"
        schema = {
            "companies": ["string"],
            "category": "string",
            "relevance_score": "number"
        }
        
        try:
            enrichment = llm_service.extract_structured(text, schema)
        except Exception as e:
            logger.error(f"LLM Extraction failed for {signal_id}: {e}")
            signals_collection.update_one(
                {"_id": ObjectId(signal_id)},
                {"$set": {
                    "status": "enrichment_failed",
                    "error_log": str(e)
                }}
            )
            return
        
        category = (enrichment.get("category") or "general").lower().strip()
        
        try:
            base_score = int(enrichment.get("relevance_score", 0))
        except (ValueError, TypeError):
            base_score = 0
        
        company_names = enrichment.get("companies", [])
        
        # 1. Update centralized 'companies' collection
        for name in company_names:
            company_clean = name.strip().lower()
            if not company_clean:
                continue
                
            companies.update_one(
                {"name": company_clean},
                {
                    "$setOnInsert": {
                        "name": company_clean,
                        "first_seen_at": datetime.now(timezone.utc),
                        "email_ids": []
                    }
                },
                upsert=True
            )

        # 2. Update the original signal
        update_data = {
            "company_names": company_names,
            "category": category,
            "relevance_score": base_score,
            "status": "enriched",
            "error_log": None # Clear any previous errors on success
        }
        
        signals_collection.update_one(
            {"_id": ObjectId(signal_id)},
            {"$set": update_data}
        )
        
    except Exception as e:
        logger.error(f"Enrichment task critical failure for {signal_id}: {e}")
        signals_collection.update_one(
            {"_id": ObjectId(signal_id)},
            {"$set": {"status": "enrichment_failed", "error_log": str(e)}}
        )
