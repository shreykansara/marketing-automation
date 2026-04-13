from typing import Dict, Any, Tuple

def generate_and_score_actions(deal: Dict[str, Any], status: str, is_signed: bool, unresponsive_role: str, activation_bottleneck: bool) -> Tuple[str, float]:
    """
    Intelligent Scoring System for next actions.
    Returns: (next_action_str, confidence_score)
    """
    candidates = []
    
    # 1. Base weights for dynamic scoring
    deal_value = deal.get("value", 0)
    if isinstance(deal_value, str):
        try:
            deal_value = float(deal_value.replace(',', '').replace('$', ''))
        except Exception:
            deal_value = 0
            
    val_score = min(20, deal_value / 10000) # up to 20 pts
    
    status_score = 0
    if status == "Stalled": status_score = 30
    elif status == "At Risk": status_score = 20
    
    act_step_scores = {"API Shared": 5, "Sandbox": 10, "Integration": 15, "Testing": 20, "Live": 25}
    stage_score = act_step_scores.get(deal.get("activation_step", "API Shared"), 0) if is_signed else 0
    
    base_score = val_score + status_score + stage_score

    def add_candidate(description: str, role_weight: int, extra_points: int, direct_bottleneck: bool = False):
        score = base_score + role_weight + extra_points
        if direct_bottleneck:
            score += 25  # High priority for direct bottlenecks
        candidates.append({"description": description, "score": score})

    # Generate Candidate Actions based on conditions
    has_compliance = any(s.get("role") == "Compliance Officer" for s in deal.get("stakeholders", []))
    compliance_needs_contact = any(s.get("role") == "Compliance Officer" and not s.get("contacted") for s in deal.get("stakeholders", []))
    
    if unresponsive_role:
        role_wt = 20 if unresponsive_role == "CTO" else 15 if unresponsive_role in ["Compliance Officer", "Business Head"] else 5
        add_candidate(f"Follow up with {unresponsive_role}", role_wt, 5, activation_bottleneck)
        if unresponsive_role == "CTO":
            add_candidate("Escalate to Business Head", 15, 0)
            add_candidate("Resend technical documentation", 10, -5)
            
    if not has_compliance or compliance_needs_contact:
        add_candidate("Schedule compliance call", 15, 10, False)
        add_candidate("Share regulatory documents", 10, 5, False)
        
    if activation_bottleneck:
        add_candidate("Send API / integration docs", 10, 5, True)
        add_candidate("Request integration update", 10, 0, True)
        
    if status == "Stalled" and not candidates:
        add_candidate("Follow up on deal", 5, 0)
        
    if status == "Active" and not candidates:
        add_candidate("Monitor deal (no action needed)", 0, 0)

    if not candidates:
        candidates.append({"description": "Monitor deal (no action needed)", "score": 0})
        
    # Select Best Action
    best_candidate = max(candidates, key=lambda x: x["score"])
    
    next_action_str = best_candidate["description"]
    confidence_score = round(min(1.0, max(0.1, best_candidate["score"] / 100.0)), 2)
    
    return next_action_str, confidence_score
