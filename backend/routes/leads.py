from fastapi import APIRouter, HTTPException, Body, BackgroundTasks
from datetime import datetime, timezone
from bson import ObjectId
from backend.core.db import leads_collection, signals_collection, deals_collection, companies
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

def process_leads_aggregation(unique_companies: list[str]):
    """
    Background worker for lead aggregation.
    """
    for company in unique_companies:
        update_lead_for_company(company)

@router.post("/generate")
async def generate_leads(background_tasks: BackgroundTasks):
    """
    Use Case 3: Generate leads from the signals. 
    Consolidates enriched signals into unique company leads via Background Tasks.
    """
    # 1. Get all unique company names from enriched signals
    enriched_signals = list(signals_collection.find({"status": "enriched"}))
    unique_companies = list(set([
        company 
        for s in enriched_signals 
        for company in s.get("company_names", [])
    ]))
            
    # 2. Trigger aggregation in background
    if unique_companies:
        background_tasks.add_task(process_leads_aggregation, unique_companies)
        
    return {"status": "success", "queued_companies": len(unique_companies)}

@router.get("/")
async def get_leads():
    """
    Use Case 3: Display leads in decreasing order of relevance.
    """
    leads = list(leads_collection.find())
    
    processed_leads = []
    for l in leads:
        l["_id"] = str(l["_id"])
        l["company_id"] = str(l.get("company_id", ""))
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

@router.post("/manual")
async def add_manual_lead(company_name: str = Body(..., embed=True)):
    """
    Manually inject a company into the leads pipeline.
    Ensures Deals exclusivity. Registers company if new.
    """
    company_clean = company_name.strip().lower()
    if not company_clean:
         raise HTTPException(status_code=400, detail="Company name cannot be empty")

    # 1. Check if Deal exists
    deal = deals_collection.find_one({"company": company_clean})
    if deal:
         raise HTTPException(status_code=400, detail="A deal for this company already exists.")

    # 2. Check if Lead already exists
    lead = leads_collection.find_one({"company": company_clean})
    if lead:
         raise HTTPException(status_code=400, detail="A lead for this company already exists.")

    # 3. Create or update Company registry
    company_res = companies.find_one_and_update(
        {"name": company_clean},
        {
            "$set": {
                "is_lead_active": True,
                "is_deal_active": False,
                "is_archived": False
            },
            "$setOnInsert": {"email_ids": [], "first_seen_at": datetime.now(timezone.utc)}
        },
        upsert=True,
        return_document=True
    )
    company_id = company_res["_id"]

    # 4. Insert into Leads
    lead_doc = {
        "company": company_clean,
        "company_id": company_id,
        "signal_ids": [],
        "emails": [],
        "logs": [
            {
                "log_id": str(uuid.uuid4()),
                "timestamp": datetime.now(timezone.utc),
                "type": "MANUAL_LEAD",
                "message": "Manually added to leads pipeline.",
                "metadata": {}
            }
        ]
    }
    leads_collection.insert_one(lead_doc)
    return {"status": "success", "message": "Lead created successfully"}

@router.delete("/{lead_id}")
async def delete_lead(lead_id: str):
    """
    Delete a lead and automatically archive the associated company.
    """
    lead = leads_collection.find_one({"_id": ObjectId(lead_id)})
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
        
    company_id = lead.get("company_id")
    
    # 1. Delete the lead
    leads_collection.delete_one({"_id": ObjectId(lead_id)})
    
    # 2. Archive the company
    if company_id:
        companies.update_one(
            {"_id": ObjectId(company_id)},
            {"$set": {"is_archived": True, "is_lead_active": False}}
        )
        
    return {"status": "success"}
