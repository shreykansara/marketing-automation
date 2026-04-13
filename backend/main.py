from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any
from mock_data import deals, templates
from datetime import datetime, timedelta

app = FastAPI(title="Blostem Pipeline Intelligence")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Since it's MVP
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def evaluate_deal(deal: Dict[str, Any]) -> Dict[str, Any]:
    """
    Unified evaluation pipeline for deal health, activation logic, and actions.
    """
    status = "Active"
    risk_reason = "No issues detected"
    next_action_str = "Monitor deal (no action needed)"
    
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
                status = "At Risk"
                risk_reason = f"{activation_step} delayed due to {bottleneck_role} inactivity ({activation_days} days)"
                unresponsive_role = bottleneck_role  # Focus next_action on this bottleneck role
                activation_bottleneck = True
            elif activation_days > 3:
                status = "Stalled"
                risk_reason = f"{activation_step} delayed due to inactivity ({activation_days} days)"
                activation_bottleneck = True

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
        
    deal["status"] = status
    deal["risk_reason"] = risk_reason
    deal["next_action"] = next_action_str
    deal["action_confidence"] = confidence_score
    
    return deal

@app.get("/api/deals")
def get_deals():
    for deal in deals:
        evaluate_deal(deal)
    return {"data": deals}

@app.get("/api/deals/{deal_id}/actions")
def get_deal_actions(deal_id: str):
    deal = next((d for d in deals if d["id"] == deal_id), None)
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")
    evaluate_deal(deal)
    return {"data": deal}

@app.post("/api/deals/{deal_id}/action")
def trigger_action(deal_id: str, payload: dict):
    deal = next((d for d in deals if d["id"] == deal_id), None)
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")
        
    action_type = payload.get("action_type")
    stakeholder_name = payload.get("stakeholder_name")
    
    if action_type == "follow_up":
        # Simulate follow up
        target_s = None
        for s in deal["stakeholders"]:
            if s["name"] == stakeholder_name:
                target_s = s
                break
                
        if target_s:
            role = target_s["role"]
            template = templates.get(role, f"Hi {target_s['name']}, just following up on our previous conversation.")
            message = template.format(name=target_s["name"])
            # update last activity to now to clear stall
            deal["last_activity"] = datetime.now(datetime.fromisoformat(deal["last_activity"]).tzinfo).isoformat()
            target_s["responded"] = True # simulate they now respond or the risk is mitigated for MVP
            return {"status": "success", "message": f"Simulated outreach sent: '{message}'"}
                
    elif action_type == "send_docs":
        deal["last_activity"] = datetime.now(datetime.fromisoformat(deal["last_activity"]).tzinfo).isoformat()
        return {"status": "success", "message": "Simulated sandbox and docs email sent."}

    # default fallback
    deal["last_activity"] = datetime.now(datetime.fromisoformat(deal["last_activity"]).tzinfo).isoformat()
    return {"status": "success", "message": "Action logged successfully."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
