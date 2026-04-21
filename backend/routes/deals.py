from fastapi import APIRouter, HTTPException, Body
from backend.core.db import deals_collection, leads_collection, companies, logs_collection, emails_collection
from bson import ObjectId
from datetime import datetime, timezone

router = APIRouter()

@router.get("/")
async def get_deals():
    """
    Use Case 5: Pipeline with Hydrated Data.
    """
    pipeline = [
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
    
    deals = list(deals_collection.aggregate(pipeline))
    
    for d in deals:
        d["_id"] = str(d["_id"])
        d["company_id"] = str(d["company_id"])
        if d.get("lead_id"):
            d["lead_id"] = str(d["lead_id"])
        d["company_name"] = d["company_data"].get("name")
        d.pop("company_data", None)
        
        for log in d.get("logs", []):
            log["_id"] = str(log["_id"])
            log["entity_id"] = str(log["entity_id"])
            if log.get("timestamp"):
                log["timestamp"] = log["timestamp"].isoformat()
                
        for email in d.get("emails", []):
            email["_id"] = str(email["_id"])
            if email.get("company_id"): email["company_id"] = str(email["company_id"])
            if email.get("deal_id"): email["deal_id"] = str(email["deal_id"])
            if email.get("lead_id"): email["lead_id"] = str(email["lead_id"])

    return deals

@router.post("/promote")
async def promote_lead(payload: dict = Body(...)):
    lead_id = payload.get("lead_id")
    if not lead_id:
        raise HTTPException(status_code=400, detail="lead_id required")
        
    lead = leads_collection.find_one({"_id": ObjectId(lead_id)})
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
        
    # 1. Create Deal
    deal_entry = {
        "company_id": lead["company_id"],
        "lead_id": lead["_id"],
        "intent_score": lead.get("relevance_score", 50),
        "status": "open",
        "stage_history": [
            {
                "from": "lead",
                "to": "open",
                "timestamp": datetime.now(timezone.utc),
                "reason": "Promoted from lead pipeline"
            }
        ]
    }
    deal_res = deals_collection.insert_one(deal_entry)
    deal_id = deal_res.inserted_id
    
    # 2. Update Company Status
    companies.update_one({"_id": lead["company_id"]}, {"$set": {"status": "deal"}})
    
    # 3. Migrate/Link Logs & Emails
    # We update entity_id for logs that pointed to the lead
    logs_collection.update_many(
        {"entity_id": ObjectId(lead_id)},
        {"$set": {"entity_id": deal_id, "migrated_from_lead": True}}
    )
    
    emails_collection.update_many(
        {"lead_id": ObjectId(lead_id)},
        {"$set": {"deal_id": deal_id}}
    )
    
    # 4. Remove Lead document
    leads_collection.delete_one({"_id": ObjectId(lead_id)})
    
    return {"status": "success", "deal_id": str(deal_id)}

@router.post("/manual")
async def add_manual_deal(payload: dict = Body(...)):
    company_name = payload.get("company_name")
    if not company_name:
        raise HTTPException(status_code=400, detail="Company name required")
        
    company = companies.find_one({"name": company_name})
    if not company:
        res = companies.insert_one({
            "name": company_name,
            "emails": [],
            "status": "deal",
            "flag": "active"
        })
        company_id = res.inserted_id
    else:
        company_id = company["_id"]
        # If it was a lead, we might want to promote it instead, but keep it simple
        if company.get("status") == "lead":
             # Trigger promotion path logic if needed, but for manual registry:
             pass 
        companies.update_one({"_id": company_id}, {"$set": {"status": "deal", "flag": "active"}})

    deals_collection.update_one(
        {"company_id": company_id},
        {
            "$set": {
                "intent_score": 50,
                "status": "open"
            },
            "$push": {
                "stage_history": {
                    "to": "open",
                    "timestamp": datetime.now(timezone.utc),
                    "reason": "Manual Registration"
                }
            }
        },
        upsert=True
    )
    return {"status": "success"}

@router.delete("/{deal_id}")
async def delete_deal(deal_id: str):
    deal = deals_collection.find_one({"_id": ObjectId(deal_id)})
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")
        
    companies.update_one(
        {"_id": deal["company_id"]},
        {"$set": {"status": None, "flag": "archived"}}
    )
    
    deals_collection.delete_one({"_id": ObjectId(deal_id)})
    return {"status": "success"}
