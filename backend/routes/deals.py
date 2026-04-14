from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from datetime import datetime

from data.db import deals_collection
from services.evaluation import evaluate_deal
from services.priority import prioritize_deals

router = APIRouter(prefix="/api/deals", tags=["deals"])

@router.get("")
def get_deals():
    deals = list(deals_collection.find())
    for deal in deals:
        deal.pop("_id", None)
        evaluate_deal(deal)
    sorted_deals = prioritize_deals(deals)
    return {"data": sorted_deals}

@router.post("/{deal_id}/action")
def trigger_action(deal_id: str, payload: dict):
    deal = deals_collection.find_one({"id": deal_id})
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")
        
    # Simply simulate risk mitigation by resetting last_activity
    deal["last_activity"] = datetime.now(datetime.fromisoformat(deal["last_activity"]).tzinfo).isoformat()
    
    # If the logic targeted an unresponsive stakeholder, we inherently clear their response lock to demonstrate AI impact
    for s in deal.get("stakeholders", []):
         if s.get("contacted") and not s.get("responded"):
              s["responded"] = True
              
    deals_collection.update_one(
        {"id": deal_id}, 
        {"$set": {
            "last_activity": deal["last_activity"],
            "stakeholders": deal.get("stakeholders", [])
        }}
    )
    
    # Re-fetch updated deal and pass through evaluate_deal
    updated_deal = deals_collection.find_one({"id": deal_id})
    updated_deal.pop("_id", None)
    evaluate_deal(updated_deal)
              
    return {"status": "success", "message": "Action configured successfully and risks mitigated."}
