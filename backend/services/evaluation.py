from typing import Dict, Any
from datetime import datetime
from services.activation import evaluate_activation_logic
from services.actions import generate_and_score_actions

def evaluate_deal(deal: Dict[str, Any]) -> Dict[str, Any]:
    """
    Unified evaluation pipeline for deal health, activation logic, and actions.
    """
    status = "Active"
    risk_reason = "No issues detected"
    
    # Generic Activity Tracking
    days_since_activity = 0
    try:
        last_activity = datetime.fromisoformat(deal["last_activity"])
        now = datetime.now(last_activity.tzinfo)
        days_since_activity = (now - last_activity).days
    except Exception:
        pass
        
    # Unresponsive stakeholder in general
    unresponsive_role = None
    for s in deal.get("stakeholders", []):
        if s.get("contacted") and not s.get("responded"):
            unresponsive_role = s["role"]
            break

    # Activation Logic for Signed Deals
    is_signed = deal.get("stage") == "Signed"
    activation_bottleneck = False

    if is_signed:
        status, risk_reason, unresponsive_role, activation_bottleneck = evaluate_activation_logic(
            deal, status, risk_reason, unresponsive_role
        )

    # Generic Stall/Risk Logic (only if activation didn't flag a bottleneck)
    if not activation_bottleneck:
        if days_since_activity >= 5:
            status = "Stalled"
            if unresponsive_role:
                risk_reason = f"{unresponsive_role} not responding for {days_since_activity} days"
            else:
                risk_reason = f"No activity in {days_since_activity} days"
        elif unresponsive_role:
            status = "At Risk"
            risk_reason = f"{unresponsive_role} not responding"
            
    # === Next Action Intelligent Scoring System ===
    next_action_str, confidence_score = generate_and_score_actions(
        deal, status, is_signed, unresponsive_role, activation_bottleneck
    )
        
    deal["status"] = status
    deal["risk_reason"] = risk_reason
    deal["next_action"] = next_action_str
    deal["action_confidence"] = confidence_score
    
    return deal
