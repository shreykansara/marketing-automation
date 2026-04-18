from bson import ObjectId
from datetime import datetime, timezone
from backend.core.celery_app import celery_app
from backend.core.db import signals_collection
from backend.core.llm import llm_service
from backend.core.logger import get_logger
from backend.services.leads.aggregator import update_lead_for_company

logger = get_logger("tasks.signals")

@celery_app.task(name="generate_embedding_task")
def generate_embedding_task(signal_id: str):
    """
    Step 2: Generate embedding for the signal.
    """
    try:
        print(f"[TASK START] generate_embedding_task: {signal_id}")
        signal = signals_collection.find_one({"_id": ObjectId(signal_id)})
        if not signal: 
            print(f"[ERROR] Signal {signal_id} not found")
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
        
        print(f"[TASK END] generate_embedding_task: {signal_id}")
        
        # Next step: Enrichment
        enrich_signal_task.delay(signal_id)
        
    except Exception as e:
        logger.error(f"Embedding generation failed for {signal_id}: {e}")
        print(f"[TASK ERROR] generate_embedding_task: {e}")

@celery_app.task(name="enrich_signal_task")
def enrich_signal_task(signal_id: str):
    """
    Step 3: Extract company mentions and category using LLM.
    """
    try:
        print(f"[TASK START] enrich_signal_task: {signal_id}")
        print(f"[ENRICH START] {signal_id}")
        
        signal = signals_collection.find_one({"_id": ObjectId(signal_id)})
        if not signal:
            print(f"[ERROR] Signal {signal_id} not found")
            return
            
        # Step 3: Extract structured data
        text = f"{signal.get('title', '')}\n{signal.get('content', '')}"
        schema = {
            "companies": ["string"], # Match user's expected output example
            "category": "string",
            "relevance_score": "number"
        }
        
        try:
            enrichment = llm_service.extract_structured(text, schema)
        except Exception as e:
            print(f"[ERROR] LLM FAILED: {e}")
            return
        
        # 4. Weighted Relevance Scoring (Module 1 Logic)
        weights = {
            "funding": 40,
            "acquisition": 35,
            "partnership": 30,
            "product_launch": 25,
            "hiring": 20
        }
        
        category = (enrichment.get("category") or "general").lower().strip()
        # Use user-provided weights, fallback to LLM's guess if not in table but present
        base_score = weights.get(category, enrichment.get("relevance_score", 5))
        
        update_data = {
            "company_mentions": enrichment.get("companies", []),
            "category": category,
            "relevance_score": base_score,
            "status": "enriched"
        }
        
        signals_collection.update_one(
            {"_id": ObjectId(signal_id)},
            {"$set": update_data}
        )
        
        # Step 4: Incremental Lead Aggregation
        companies = update_data.get("company_mentions", [])
        for company in companies:
            if company:
                update_lead_for_company(company)
        
        print(f"[AGGREGATION DONE] {signal_id}")
        print(f"[TASK END] enrich_signal_task: {signal_id}")
        
    except Exception as e:
        logger.error(f"Enrichment task failed for {signal_id}: {e}")
        print(f"[TASK ERROR] enrich_signal_task: {e}")

