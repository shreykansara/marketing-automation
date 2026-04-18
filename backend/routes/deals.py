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
    
    # 1. Prepare Deal Document
    deal_doc = {
        "company": company,
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
    
    # 3. Delete Lead
    leads_collection.delete_one({"_id": ObjectId(lead_id)})
    
    return {"status": "success", "company": company}
