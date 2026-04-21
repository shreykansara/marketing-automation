from fastapi import APIRouter, HTTPException, Body
from backend.core.db import leads_collection, signals_collection, companies, logs_collection
from bson import ObjectId
from datetime import datetime, timezone
from pymongo import DESCENDING

router = APIRouter()

@router.post("/generate")
async def generate_leads():
    """
    Aggregation pipeline: Enriched signals -> Centralized Leads.
    """
    signals = list(signals_collection.find({"status": "enriched"}))
    leads_count = 0
    
    for s in signals:
        for company_id in s.get("company_ids", []):
            # Check exclusivity
            company = companies.find_one({"_id": company_id})
            if not company or company.get("status") == "deal":
                continue
                
            # Upsert Lead
            leads_collection.update_one(
                {"company_id": company_id},
                {
                    "$set": {
                        "relevance_score": int(s.get("relevance_score", 0)),
                        "status": "active",
                        "updated_at": datetime.now(timezone.utc)
                    },
                    "$setOnInsert": {
                        "created_at": datetime.now(timezone.utc)
                    }
                },
                upsert=True
            )
            
            # Update company status if null
            if not company.get("status"):
                companies.update_one({"_id": company_id}, {"$set": {"status": "lead"}})
                
            # Log the discovery
            logs_collection.update_one(
                {
                    "entity_id": company_id, # Temporary until we have lead_id
                    "type": "SIGNAL",
                    "message": f"Signaled identified: {s['title']}"
                },
                {"$set": {"timestamp": datetime.now(timezone.utc)}},
                upsert=True
            )
            leads_count += 1
            
    return {"leads_aggregated": leads_count}

@router.get("/")
async def get_leads():
    """
    Use Case 4: Display leads with hydrated company info and metrics.
    """
    pipeline = [
        {"$match": {"status": "active"}},
        {
            "$lookup": {
                "from": "companies",
                "localField": "company_id",
                "foreignField": "_id",
                "as": "company_data"
            }
        },
        {"$unwind": "$company_data"},
        {
            "$lookup": {
                "from": "signals",
                "localField": "company_id",
                "foreignField": "company_ids",
                "as": "signals"
            }
        },
        {
            "$lookup": {
                "from": "logs",
                "localField": "_id",
                "foreignField": "entity_id",
                "as": "logs"
            }
        },
        {
            "$lookup": {
                "from": "emails",
                "localField": "company_id",
                "foreignField": "company_id",
                "as": "emails"
            }
        }
    ]
    
    leads = list(leads_collection.aggregate(pipeline))
    
    for l in leads:
        l["_id"] = str(l["_id"])
        l["company_id"] = str(l["company_id"])
        l["company_name"] = l["company_data"].get("name")
        l.pop("company_data", None)
        
        for s in l.get("signals", []):
            s["_id"] = str(s["_id"])
            s["company_ids"] = [str(cid) for cid in s.get("company_ids", [])]
            
        for log in l.get("logs", []):
            log["_id"] = str(log["_id"])
            log["entity_id"] = str(log["entity_id"])
            if log.get("timestamp"):
                log["timestamp"] = log["timestamp"].isoformat()

        for email in l.get("emails", []):
            email["_id"] = str(email["_id"])
            if email.get("company_id"): email["company_id"] = str(email["company_id"])
                
    return leads

@router.post("/manual")
async def add_manual_lead(payload: dict = Body(...)):
    company_name = payload.get("company_name")
    if not company_name:
        raise HTTPException(status_code=400, detail="Company name required")
        
    # Resolve company
    company = companies.find_one({"name": company_name})
    if not company:
        res = companies.insert_one({
            "name": company_name,
            "emails": [],
            "status": "lead",
            "flag": "active"
        })
        company_id = res.inserted_id
    else:
        if company.get("status") == "deal":
            raise HTTPException(status_code=400, detail="Company is already in the deal pipeline")
        company_id = company["_id"]
        companies.update_one({"_id": company_id}, {"$set": {"status": "lead", "flag": "active"}})

    # Create Lead
    leads_collection.update_one(
        {"company_id": company_id},
        {
            "$set": {
                "relevance_score": 50, 
                "status": "active",
                "updated_at": datetime.now(timezone.utc)
            },
            "$setOnInsert": {
                "created_at": datetime.now(timezone.utc)
            }
        },
        upsert=True
    )
    
    return {"status": "success"}

@router.delete("/{lead_id}")
async def delete_lead(lead_id: str):
    lead = leads_collection.find_one({"_id": ObjectId(lead_id)})
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
        
    # Restore company to null status and archive
    companies.update_one(
        {"_id": lead["company_id"]},
        {"$set": {"status": None, "flag": "archived"}}
    )
    
    leads_collection.delete_one({"_id": ObjectId(lead_id)})
    return {"status": "success"}

@router.post("/{lead_id}/logs")
async def add_lead_log(lead_id: str, message: str = Body(..., embed=True)):
    log_entry = {
        "entity_id": ObjectId(lead_id),
        "timestamp": datetime.now(timezone.utc),
        "type": "MANUAL",
        "message": message
    }
    logs_collection.insert_one(log_entry)
    return {"status": "success"}

@router.delete("/{lead_id}/logs/{log_id}")
async def delete_lead_log(lead_id: str, log_id: str):
    logs_collection.delete_one({"_id": ObjectId(log_id)})
    return {"status": "success"}
