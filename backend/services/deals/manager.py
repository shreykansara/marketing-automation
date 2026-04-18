from datetime import datetime, timezone
from bson import ObjectId
from backend.core.db import leads_collection, deals_collection
from backend.services.deals.scoring import calculate_deal_intent_score

def convert_lead_to_deal(lead_id: str):
    """
    Step 1: Fetch Lead
    Step 2: Calculate Deal Intent Score
    Step 3: Create Deal document
    """
    lead = leads_collection.find_one({"_id": ObjectId(lead_id)})
    if not lead:
        return None
        
    intent_score = calculate_deal_intent_score(lead)
    
    deal_doc = {
        "lead_id": ObjectId(lead_id),
        "company_name": lead.get("company", "Unknown"),
        "intent_score": intent_score,
        "status": "open",
        "last_contacted_at": None,
        "emails_sent": [],
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc)
    }
    
    # Atomic Upsert per lead
    result = deals_collection.update_one(
        {"lead_id": ObjectId(lead_id)},
        {"$set": deal_doc},
        upsert=True
    )
    
    return str(result.upserted_id or deals_collection.find_one({"lead_id": ObjectId(lead_id)})["_id"])

def handle_auto_unarchive(company_name: str):
    """
    Called whenever a new signal is aggregated for a company.
    If a deal exists and is archived, reopen it.
    """
    deals_collection.update_one(
        {"company_name": company_name.lower(), "status": "archived"},
        {"$set": {
            "status": "open",
            "updated_at": datetime.now(timezone.utc)
        }}
    )
