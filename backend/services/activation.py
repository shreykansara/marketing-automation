from typing import Dict, Any, Tuple
from datetime import datetime

def evaluate_activation_logic(deal: Dict[str, Any], current_status: str, current_risk_reason: str, current_unresponsive_role: str) -> Tuple[str, str, str, bool]:
    """
    Evaluates activation specific logic for signed deals.
    Returns: (status, risk_reason, unresponsive_role, activation_bottleneck)
    """
    if "activation_step" not in deal:
        deal["activation_step"] = "API Shared"
    if "activation_last_updated" not in deal:
        deal["activation_last_updated"] = deal["last_activity"]

    activation_step = deal["activation_step"]
    
    activation_days = 0
    try:
        act_updated = datetime.fromisoformat(deal["activation_last_updated"])
        now_act = datetime.now(act_updated.tzinfo)
        activation_days = (now_act - act_updated).days
    except Exception:
        pass

    activation_bottleneck = False
    
    if activation_step != "Live":
        # Map responsible roles
        responsible_roles = []
        if activation_step == "API Shared":
            responsible_roles = ["Business Head", "Integration Manager"]
        elif activation_step in ["Sandbox", "Integration"]:
            responsible_roles = ["CTO"]
        elif activation_step == "Testing":
            responsible_roles = ["CTO", "Compliance Officer"]

        # Check for stakeholder bottleneck specific to this activation step
        bottleneck_role = None
        for role in responsible_roles:
            for s in deal.get("stakeholders", []):
                if s.get("role") == role and s.get("contacted") and not s.get("responded"):
                    bottleneck_role = role
                    break
            if bottleneck_role:
                break

        if bottleneck_role:
            current_status = "At Risk"
            current_risk_reason = f"{activation_step} delayed due to {bottleneck_role} inactivity ({activation_days} days)"
            current_unresponsive_role = bottleneck_role  # Focus next_action on this bottleneck role
            activation_bottleneck = True
        elif activation_days > 3:
            current_status = "Stalled"
            current_risk_reason = f"{activation_step} delayed due to inactivity ({activation_days} days)"
            activation_bottleneck = True

    return current_status, current_risk_reason, current_unresponsive_role, activation_bottleneck
