from datetime import datetime, timezone
from bson import ObjectId
from backend.core.db import leads_collection, deals_collection
from backend.services.deals.scoring import calculate_deal_intent_score

def convert_lead_to_deal(lead_id: str):
    """
    Refactored Deal Manager (v2): Converts a lead into a deal using the company name as the link.
    Deletes the lead upon successful conversion.
    """
    lead = leads_collection.find_one({"_id": ObjectId(lead_id)})
    if not lead:
        return None
        
    company_name = lead.get("company", "unknown").lower()
    
    # Calculate initial deal intent score
    intent_score = calculate_deal_intent_score(lead)
    
    # Transfer existing emails and logs from lead to deal
    emails = lead.get("emails", [])
    logs = lead.get("logs", [])
    
    # Append the conversion event to logs
    logs.append({
        "timestamp": datetime.now(timezone.utc),
        "type": "DEAL_CONVERTED",
        "message": f"Lead for {company_name} converted to a Deal. Lead document deleted.",
        "metadata": {"previous_lead_id": lead_id}
    })
    
    deal_doc = {
        "company": company_name,
        "emails": emails,
        "intent_score": intent_score,
        "logs": logs
    }
    
    # Create or update deal
    result = deals_collection.update_one(
        {"company": company_name},
        {"$set": deal_doc},
        upsert=True
    )
    
    deal_id = str(result.upserted_id or deals_collection.find_one({"company": company_name})["_id"])
    
    # CRITICAL: Delete the lead document after successful deal creation
    leads_collection.delete_one({"_id": ObjectId(lead_id)})
    
    return deal_id

def handle_auto_unarchive(company_name: str):
    """
    Reactivates a deal by logging an 'OPEN' event if new signals arrive.
    Note: 'archived' status is now derived from the absence of recent 'OPEN' logs 
    or a specific 'ARCHIVED' log type at the end of the array.
    """
    company_clean = company_name.lower()
    # Find the deal to see if it needs reopening
    deal = deals_collection.find_one({"company": company_clean})
    if not deal:
        return

    # In the new log-driven status model, we reopen by pushing a new log entry.
    deals_collection.update_one(
        {"company": company_clean},
        {
            "$push": {
                "logs": {
                    "timestamp": datetime.now(timezone.utc),
                    "type": "DEAL_REOPENED",
                    "message": "Deal automatically reopened due to incoming market signals.",
                    "metadata": {"trigger": "aggregator"}
                }
            }
        }
    )
