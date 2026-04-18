import uuid
from fastapi import APIRouter, HTTPException, Body
from datetime import datetime, timezone
from bson import ObjectId
from backend.core.db import leads_collection, signals_collection
from backend.services.leads.aggregator import update_lead_for_company

router = APIRouter()

def derive_lead_relevance(lead):
    """
    Helper to calculate lead relevance based on associated signal scores.
    """
    signal_ids = lead.get("signal_ids", [])
    if not signal_ids:
        return 0
    
    signals = list(signals_collection.find({"_id": {"$in": signal_ids}}))
    if not signals:
        return 0
    
    scores = [s.get("relevance_score", 0) for s in signals]
    return sum(scores) / len(scores)

@router.post("/generate")
async def generate_leads():
    """
    Use Case 3: Generate leads from the signals. 
    Consolidates enriched signals into unique company leads.
    """
    # 1. Get all unique company names from enriched signals
    enriched_signals = list(signals_collection.find({"status": "enriched"}))
    unique_companies = set()
    for s in enriched_signals:
        for company in s.get("company_names", []):
            unique_companies.add(company)
            
    # 2. Trigger aggregation for each company
    for company in unique_companies:
        update_lead_for_company(company)
        
    return {"status": "success", "processed_companies": len(unique_companies)}

@router.get("/")
async def get_leads():
    """
    Use Case 3: Display leads in decreasing order of relevance.
    """
    leads = list(leads_collection.find())
    
    processed_leads = []
    for l in leads:
        l["_id"] = str(l["_id"])
        l["signal_ids"] = [str(sid) for sid in l["signal_ids"]]
        l["emails"] = [str(eid) for eid in l.get("emails", [])]
        
        # Calculate relevance
        l["relevance"] = derive_lead_relevance(l)
        processed_leads.append(l)
        
    # Sort by relevance desc
    processed_leads.sort(key=lambda x: x["relevance"], reverse=True)
    return processed_leads

@router.patch("/{lead_id}/logs")
async def add_lead_log(lead_id: str, message: str = Body(..., embed=True)):
    """
    Use Case 6: Update Leads (Add log).
    """
    log_entry = {
        "log_id": str(uuid.uuid4()),
        "timestamp": datetime.now(timezone.utc),
        "type": "MANUAL_UPDATE",
        "message": message,
        "metadata": {}
    }
    
    result = leads_collection.update_one(
        {"_id": ObjectId(lead_id)},
        {"$push": {"logs": log_entry}}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Lead not found")
        
    return {"status": "success", "log_id": log_entry["log_id"]}

@router.delete("/{lead_id}/logs/{log_id}")
async def delete_lead_log(lead_id: str, log_id: str):
    """
    Use Case 6: Update Leads (Delete specific log).
    """
    result = leads_collection.update_one(
        {"_id": ObjectId(lead_id)},
        {"$pull": {"logs": {"log_id": log_id}}}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Lead not found")
        
    return {"status": "success"}
