from bson import ObjectId
import datetime
from backend.core.db import signals_collection, companies
from backend.core.llm import llm_service
from backend.core.logger import get_logger

logger = get_logger("signal_task")

class SignalPipeline:
    async def process_signal(self, signal_id: ObjectId):
        """
        Enriches a raw signal using AI and resolves companies.
        """
        signal = signals_collection.find_one({"_id": signal_id})
        if not signal:
            logger.error(f"Signal {signal_id} not found.")
            return

        logger.info(f"Processing signal: {signal.get('title')}")
        
        # 1. AI Enrichment
        context = f"Title: {signal.get('title')}\nContent: {signal.get('content')}"
        schema = {
            "companies": ["company name"],
            "category": "funding|partnership|product_launch|expansion|regulatory|hiring|general",
            "relevance_score": 0
        }
        
        try:
            enrichment = llm_service.extract_structured(context, schema)
            
            # 2. Resolve Companies
            company_ids = []
            extracted_names = enrichment.get("companies", [])
            
            for name in extracted_names:
                # Normalize name (basic)
                norm_name = name.strip()
                if not norm_name: continue
                
                co = companies.find_one({"name": {"$regex": f"^{norm_name}$", "$options": "i"}})
                if not co:
                    logger.info(f"Creating new company from signal: {norm_name}")
                    res = companies.insert_one({
                        "name": norm_name,
                        "emails": [],
                        "status": None,
                        "flag": "active",
                        "created_at": datetime.datetime.now()
                    })
                    company_ids.append(res.inserted_id)
                else:
                    company_ids.append(co["_id"])

            # 3. Update Signal
            signals_collection.update_one(
                {"_id": signal_id},
                {
                    "$set": {
                        "company_ids": company_ids,
                        "category": enrichment.get("category", "general"),
                        "relevance_score": enrichment.get("relevance_score", 0),
                        "status": "enriched",
                        "updated_at": datetime.datetime.now()
                    }
                }
            )

            # 4. Automate Lead Discovery
            for company_id in company_ids:
                co = companies.find_one({"_id": company_id})
                if not co or co.get("status") == "deal":
                    continue
                
                # Check if it was already a lead. If not, promote it.
                if co.get("status") != "lead":
                    companies.update_one({"_id": company_id}, {"$set": {"status": "lead"}})
                
                # Upsert Lead record
                from backend.core.db import leads_collection, logs_collection
                from datetime import timezone
                
                now = datetime.datetime.now(timezone.utc)
                leads_collection.update_one(
                    {"company_id": company_id},
                    {
                        "$set": {
                            "relevance_score": int(enrichment.get("relevance_score", 0)),
                            "status": "active",
                            "updated_at": now
                        },
                        "$setOnInsert": {
                            "created_at": now
                        }
                    },
                    upsert=True
                )

                # Log discovery
                logs_collection.update_one(
                    {
                        "entity_id": company_id,
                        "type": "SIGNAL",
                        "message": f"Signal identified: {signal['title']}"
                    },
                    {"$set": {"timestamp": datetime.datetime.now(timezone.utc)}},
                    upsert=True
                )

            logger.info(f"Signal {signal_id} enriched and leads updated successfully.")
            
        except Exception as e:
            logger.error(f"Failed to enrich signal {signal_id}: {str(e)}")
            signals_collection.update_one(
                {"_id": signal_id},
                {"$set": {"status": "failed", "error": str(e)}}
            )

signal_pipeline = SignalPipeline()
