from typing import Dict, Any, List

def refine_activation_context(deal: Dict[str, Any], decision_packet: Dict[str, Any]) -> Dict[str, Any]:
    """
    ACTIVATION LAYER: Refines execution context (who/where).
    Only runs after a decision is made.
    """
    decision = decision_packet.get("decision")
    intent = decision_packet.get("action_intent")
    
    # Identify target stakeholders based on role importance and intent
    # Default personas for MVP
    personas = ["CTO", "CMO", "Compliance Officer"]
    
    target_role = None
    channel = "email"
    
    # Logic: Match intent to role
    if intent == "re_engagement":
        # Target whoever is unresponsive or the primary (CTO)
        target_role = "CTO"
        for s in deal.get("stakeholders", []):
            if s.get("contacted") and not s.get("responded"):
                target_role = s["role"]
                break
    elif intent == "nurture":
        target_role = "CMO"
        channel = "linkedin"
    elif intent == "manual_intervention":
        target_role = "Business Head"
        channel = "direct_call"
        
    # Check if target role exists in stakeholders
    stakeholder_exists = any(s.get("role") == target_role for s in deal.get("stakeholders", []))
    
    return {
        "target_role": target_role,
        "channel": channel,
        "is_ready": stakeholder_exists,
        "intent": intent,
        "priority": decision_packet.get("priority", "Low")
    }
