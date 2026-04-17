from typing import Dict, Any
from datetime import datetime, timezone

def evaluate_deal_state(deal: Dict[str, Any]) -> Dict[str, Any]:
    """
    STATE ASSESSMENT ONLY: Calculates health and urgency metrics.
    No decisions or actions are triggered here.
    """
    status = "Active"
    risk_reason = "No issues detected"
    
    # Generic Activity Tracking
    days_since_activity = 0
    try:
        last_activity_str = deal.get("last_activity")
        if last_activity_str:
            last_activity = datetime.fromisoformat(last_activity_str)
            # Ensure comparison is timezone-aware
            now = datetime.now(timezone.utc)
            days_since_activity = (now - last_activity).days
    except Exception:
        pass
        
    # Urgency Score Calculation (0-100)
    # Factor 1: Deal Value (20%)
    deal_value = deal.get("value", 0)
    val_score = min(20, deal_value / 5000) 
    
    # Factor 2: Signal Weight (30%)
    signals = deal.get("signals", [])
    signal_score = min(30, len(signals) * 5)
    
    # Factor 3: Intent/Decay Score (50%)
    intent_score = deal.get("intent_score", 0)
    # Decay intent score by 5 points per day of inactivity
    decayed_intent = max(0, intent_score - (days_since_activity * 5))
    urgency_base = min(50, decayed_intent / 2)
    
    total_urgency = round(val_score + signal_score + urgency_base)

    # Risk Assessment
    unresponsive_role = None
    for s in deal.get("stakeholders", []):
        if s.get("contacted") and not s.get("responded"):
            unresponsive_role = s["role"]
            break

    if days_since_activity >= 7:
        status = "Stalled"
        risk_reason = f"No activity in {days_since_activity} days"
    elif unresponsive_role:
        status = "At Risk"
        risk_reason = f"{unresponsive_role} not responding"
            
    return {
        "status": status,
        "urgency_score": total_urgency,
        "risk_reason": risk_reason,
        "days_since_activity": days_since_activity,
        "unresponsive_role": unresponsive_role
    }
