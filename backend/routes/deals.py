from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from datetime import datetime, timezone

from data.db import deals_collection
from services.evaluation import evaluate_deal_state
from services.decision_engine import compute_decision
from services.activation import refine_activation_context
from services.outreach_engine import execute_outreach_generation
from services.priority import prioritize_deals

router = APIRouter(prefix="/api/deals", tags=["deals"])

@router.get("")
def get_deals():
    deals = list(deals_collection.find())
    for deal in deals:
        deal.pop("_id", None)
        
        # 1. EVALUATE STATE
        eval_packet = evaluate_deal_state(deal)
        
        # 2. COMPUTE DECISION (Now memory-aware via deal['decision_history'])
        decision_packet = compute_decision(deal, eval_packet)
        
        # Update deal object with latest adaptive intelligence for frontend
        deal["status"] = eval_packet["status"]
        deal["urgency_score"] = eval_packet["urgency_score"]
        deal["risk_reason"] = eval_packet["risk_reason"]
        
        # Decision logic
        deal["decision"] = decision_packet["decision"]
        deal["next_action"] = decision_packet["reasoning"]
        deal["action_intent"] = decision_packet["action_intent"]
        deal["priority"] = decision_packet["priority"]
        deal["decision_reason"] = decision_packet.get("reason")
        deal["escalate_to"] = decision_packet.get("escalate_to")

    sorted_deals = prioritize_deals(deals)
    return {"data": sorted_deals}

@router.post("/auto-generate")
def auto_generate_deals():
    from services.conversion import convert_leads_to_deals
    result = convert_leads_to_deals()
    return result

@router.post("/{deal_id}/evaluate-and-trigger")
def evaluate_and_trigger(deal_id: str):
    """
    CLOSED-LOOP ORCHESTRATOR 2.0: Adaptive memory-aware execution.
    """
    deal = deals_collection.find_one({"id": deal_id})
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")
        
    # 1. EVALUATE
    eval_packet = evaluate_deal_state(deal)
    
    # 2. DECIDE (Adaptive)
    decision_packet = compute_decision(deal, eval_packet)
    
    # 3. ACTIVATE & EXECUTE (Only if Decision Engine triggers)
    outreach_result = None
    if decision_packet["decision"] == "trigger_outreach":
        # 3. ACTIVATE
        activation_context = refine_activation_context(deal, decision_packet)
        # 4. EXECUTE
        outreach_result = execute_outreach_generation(deal, activation_context)
        
    return {
        "status": "success",
        "evaluation": eval_packet,
        "decision": decision_packet,
        "execution": outreach_result
    }

@router.post("/{deal_id}/action")
def trigger_action(deal_id: str, payload: dict):
    # This remains for manual overrides/simulations in the UI
    deal = deals_collection.find_one({"id": deal_id})
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")
        
    now = datetime.now(timezone.utc).isoformat()
    
    for s in deal.get("stakeholders", []):
         if s.get("contacted") and not s.get("responded"):
              s["responded"] = True
              
    deals_collection.update_one(
        {"id": deal_id}, 
        {"$set": {
            "last_activity": now,
            "stakeholders": deal.get("stakeholders", [])
        }}
    )
    
    return {"status": "success", "message": "Manual mitigation successful."}
