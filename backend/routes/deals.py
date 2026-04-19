import uuid
from fastapi import APIRouter, HTTPException, Body
from typing import List, Optional
from bson import ObjectId
from datetime import datetime, timezone
from backend.core.db import deals_collection, leads_collection, signals_collection, emails_collection
from backend.core.llm import llm_service
from backend.core.logger import get_logger

router = APIRouter()
logger = get_logger("routes.deals")

def calculate_deal_relevance(deal, mode="weighted"):
    """
    Complex Relevance Calculation.
    mode 'weighted': (0.7 * LLM_Log_Score) + (0.3 * Avg_Signal_Score)
    mode 'logs_only': (1.0 * LLM_Log_Score)
    """
    # 1. Capture Log Score via LLM
    logs = deal.get("logs", [])
    log_score = llm_service.score_deal_logs(logs) if logs else 0
    
    if mode == "logs_only":
        return log_score
    
    # 2. Capture Signal Score (Need to fetch original company signals for the score)
    # Note: Signals IDs are dropped on promotion, so we fetch by company name
    company = deal.get("company")
    signals = list(signals_collection.find({"company_names": company, "status": "enriched"}))
    
    if not signals:
        signal_avg = 0
    else:
        scores = [s.get("relevance_score", 0) for s in signals]
        signal_avg = sum(scores) / len(scores)
        
    # 3. Weighted Average (70/30)
    final_score = (0.7 * log_score) + (0.3 * signal_avg)
    return round(final_score, 2)

@router.get("/")
async def get_deals():
    """
    Use Case 4: Display deals in decreasing order of relevance (Weighted).
    """
    deals = list(deals_collection.find())
    
    processed_deals = []
    for d in deals:
        d["_id"] = str(d["_id"])
        d["company_id"] = str(d.get("company_id", ""))
        d["emails"] = [str(eid) for eid in d.get("emails", [])]
        d["relevance"] = calculate_deal_relevance(d, mode="weighted")
        processed_deals.append(d)
        
    processed_deals.sort(key=lambda x: x["relevance"], reverse=True)
    return processed_deals

@router.get("/relevance-logs")
async def get_deals_by_logs():
    """
    Use Case 7: Display deals in decreasing order of relevance (Logs-only).
    """
    deals = list(deals_collection.find())
    
    processed_deals = []
    for d in deals:
        d["_id"] = str(d["_id"])
        d["company_id"] = str(d.get("company_id", ""))
        d["relevance"] = calculate_deal_relevance(d, mode="logs_only")
        processed_deals.append(d)
        
    processed_deals.sort(key=lambda x: x["relevance"], reverse=True)
    return processed_deals

@router.post("/promote")
async def promote_lead(lead_id: str = Body(..., embed=True)):
    """
    Use Case 5: Promote leads to deals.
    Moves data, retains emails/logs, drops signal_ids, deletes lead.
    """
    lead = leads_collection.find_one({"_id": ObjectId(lead_id)})
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
        
    company = lead.get("company")
    company_id = lead.get("company_id")
    
    # 1. Prepare Deal Document
    deal_doc = {
        "company": company,
        "company_id": company_id,
        "emails": lead.get("emails", []),
        "logs": lead.get("logs", []),
        "intent_score": 0, # To be updated via routes
    }
    
    # Append promotion event to logs
    deal_doc["logs"].append({
        "timestamp": datetime.now(timezone.utc),
        "type": "PROMOTED_TO_DEAL",
        "message": "Lead successfully promoted to active pipeline deal.",
        "metadata": {}
    })
    
    # 2. Insert into Deals
    deals_collection.update_one(
        {"company": company},
        {"$set": deal_doc},
        upsert=True
    )
    
    # Update Company Record (Mutual Exclusivity: lead=False, deal=True)
    from backend.core.db import companies
    companies.update_one(
        {"name": company},
        {
            "$set": {
                "is_lead_active": False,
                "is_deal_active": True
            }
        },
        upsert=True
    )
    
    # 3. Delete Lead
    leads_collection.delete_one({"_id": ObjectId(lead_id)})
    
    return {"status": "success", "company": company}

@router.post("/manual")
async def add_manual_deal(company_name: str = Body(..., embed=True)):
    """
    Manually inject a company into the deals pipeline.
    If it's already a lead, it will be automatically promoted.
    """
    company_clean = company_name.strip().lower()
    if not company_clean:
         raise HTTPException(status_code=400, detail="Company name cannot be empty")

    # 1. Check if Deal exists
    deal = deals_collection.find_one({"company": company_clean})
    if deal:
         raise HTTPException(status_code=400, detail="A deal for this company already exists.")

    # 2. Check if Lead exists (promotes if true)
    lead = leads_collection.find_one({"company": company_clean})
    
    # 3. Create or update Company registry
    from backend.core.db import companies
    company_res = companies.find_one_and_update(
        {"name": company_clean},
        {
            "$set": {
                "is_lead_active": False,
                "is_deal_active": True,
                "is_archived": False
            },
            "$setOnInsert": {"email_ids": [], "first_seen_at": datetime.now(timezone.utc)}
        },
        upsert=True,
        return_document=True
    )
    company_id = company_res["_id"]

    # 4. Insert into Deals
    deal_doc = {
        "company": company_clean,
        "company_id": company_id,
        "emails": lead.get("emails", []) if lead else [],
        "logs": lead.get("logs", []) if lead else [],
        "intent_score": 0
    }
    
    deal_doc["logs"].append({
        "log_id": str(uuid.uuid4()),
        "timestamp": datetime.now(timezone.utc),
        "type": "MANUAL_DEAL",
        "message": "Manually added to deals pipeline" + (" (promoted from lead)." if lead else "."),
        "metadata": {}
    })
    
    deals_collection.insert_one(deal_doc)
    
    if lead:
        leads_collection.delete_one({"_id": lead["_id"]})
        
    return {"status": "success", "message": "Deal created successfully"}

@router.delete("/{deal_id}")
async def delete_deal(deal_id: str):
    """
    Delete a deal and automatically archive the associated company.
    """
    deal = deals_collection.find_one({"_id": ObjectId(deal_id)})
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")
        
    company_id = deal.get("company_id")
    
    # 1. Delete the deal
    deals_collection.delete_one({"_id": ObjectId(deal_id)})
    
    # 2. Archive the company
    if company_id:
        from backend.core.db import companies
        companies.update_one(
            {"_id": ObjectId(company_id)},
            {"$set": {"is_archived": True, "is_deal_active": False}}
        )
        
    return {"status": "success"}
