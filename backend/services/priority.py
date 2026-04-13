from typing import List, Dict, Any

def prioritize_deals(deals_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Ranks deals dynamically based on urgency, value, and likelihood of impact.
    """
    max_value = 1
    for d in deals_list:
        val = d.get("value", 0)
        if isinstance(val, str):
            try:
                val = float(val.replace(',', '').replace('$', ''))
            except Exception:
                val = 0
        if val > max_value:
            max_value = val

    for d in deals_list:
        score = 0
        
        # A. Deal Status Weight
        status = d.get("status", "Active")
        if status == "Stalled":
            score += 50
        elif status == "At Risk":
            score += 30
        else:
            score += 10
            
        # B. Deal Value Weight
        val = d.get("value", 0)
        if isinstance(val, str):
            try:
                val = float(val.replace(',', '').replace('$', ''))
            except Exception:
                val = 0
        val_score = (val / max_value) * 30
        score += val_score
        
        # C. Action Confidence
        confidence = d.get("action_confidence", 0)
        score += (confidence * 20)
        
        # D. Activation Stage Weight
        is_signed = d.get("stage") == "Signed"
        act_step_scores = {"API Shared": 5, "Sandbox": 10, "Integration": 15, "Testing": 20, "Live": 25}
        stage_score = act_step_scores.get(d.get("activation_step", "API Shared"), 0) if is_signed else 0
        score += stage_score
        
        score = round(score, 2)
        d["priority_score"] = score
        
        if score >= 70:
            d["priority_level"] = "High"
        elif score >= 40:
            d["priority_level"] = "Medium"
        else:
            d["priority_level"] = "Low"
            
    deals_list.sort(key=lambda x: x.get("priority_score", 0), reverse=True)
    return deals_list
