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

def evaluate_stall_risk(deal: Dict[str, Any]) -> str:
    """
    Rule-based Stall Detection System
    If no activity for 7 days -> 'Stalled'
    If no response from a contacted stakeholder -> 'At Risk'
    Else -> 'Active'
    """
    try:
        last_activity = datetime.fromisoformat(deal["last_activity"])
        now = datetime.now(last_activity.tzinfo)
        if (now - last_activity).days >= 7:
            return "Stalled"
    except Exception:
        pass
    
    for stakeholder in deal.get("stakeholders", []):
        if stakeholder["contacted"] and not stakeholder["responded"]:
            return "At Risk"
            
    return "Active"

def determine_next_action(deal: Dict[str, Any]) -> List[Dict[str, str]]:
    """
    Next Best Action Engine
    """
    actions = []
    
    if deal["stage"] == "Signed":
        has_integration_manager = any(s["role"] == "Integration Manager" for s in deal["stakeholders"])
        if not has_integration_manager:
            actions.append({"type": "identify_stakeholder", "message": "Identify Integration Manager to start technical kickoff."})
        else:
            actions.append({"type": "send_docs", "message": "Send sandbox access and integration docs."})
            
    # Check for unresponsive stakeholders
    for s in deal["stakeholders"]:
        if s["contacted"] and not s["responded"]:
            actions.append({"type": "follow_up", "message": f"Follow up with {s['role']} ({s['name']}) - no response.", "stakeholder_name": s["name"], "role": s["role"]})
            
    # Check if newly in Negotiation
    if deal["stage"] == "Negotiation":
        has_compliance = any(s["role"] == "Compliance Officer" for s in deal["stakeholders"])
        if not has_compliance:
            actions.append({"type": "schedule_call", "message": "Schedule a compliance review block."})
            
    if not actions:
        if deal["stage"] == "Lead":
            actions.append({"type": "outreach", "message": "Send initial value proposition to Business Head."})
        else:
            actions.append({"type": "monitor", "message": "Engagement is healthy. No immediate action required."})
            
    return actions

@app.get("/api/deals")
def get_deals():
    for deal in deals:
        deal["status"] = evaluate_stall_risk(deal)
        deal["next_actions"] = determine_next_action(deal)
    return {"data": deals}

@app.get("/api/deals/{deal_id}/actions")
def get_deal_actions(deal_id: str):
    deal = next((d for d in deals if d["id"] == deal_id), None)
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")
    deal["status"] = evaluate_stall_risk(deal)
    actions = determine_next_action(deal)
    return {"data": actions}

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
