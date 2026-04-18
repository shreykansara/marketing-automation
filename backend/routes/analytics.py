from fastapi import APIRouter
from backend.core.db import signals_collection, leads_collection, deals_collection
from datetime import datetime, timezone, timedelta
from bson import ObjectId
from backend.routes.leads import derive_lead_fields
from backend.routes.deals import derive_deal_status

router = APIRouter()

@router.get("/stats")
async def get_stats():
    # 1. Counts
    total_signals = signals_collection.count_documents({})
    total_leads = leads_collection.count_documents({})
    total_deals = deals_collection.count_documents({})
    
    # 2. Fetch and Process All Leads for Alerts (High Intent)
    all_leads = list(leads_collection.find())
    processed_leads = []
    for l in all_leads:
        l["_id"] = str(l["_id"])
        derive_lead_fields(l)
        processed_leads.append(l)
    
    # Sort and take top 5
    processed_leads.sort(key=lambda x: x.get("intent_score", 0), reverse=True)
    high_intent_leads = processed_leads[:5]
    
    # 3. Fetch and Process All Deals for Health and Follow-ups
    all_deals = list(deals_collection.find())
    now = datetime.now(timezone.utc)
    follow_up_threshold = now - timedelta(hours=48)
    
    healthy = 0
    stagnant = 0
    at_risk = 0
    follow_up_deals = []
    
    for d in all_deals:
        d["_id"] = str(d["_id"])
        status = derive_deal_status(d)
        d["status"] = status
        
        # Determine last activity from logs
        logs = d.get("logs", [])
        last_activity_time = logs[-1].get("timestamp") if logs else None
        if last_activity_time and last_activity_time.tzinfo is None:
            last_activity_time = last_activity_time.replace(tzinfo=timezone.utc)
            
        if status in ["open", "contacted", "replied"]:
            # Health Calculation
            if not last_activity_time:
                at_risk += 1
            else:
                diff = now - last_activity_time
                if diff < timedelta(hours=24):
                    healthy += 1
                elif diff < timedelta(hours=72):
                    stagnant += 1
                else:
                    at_risk += 1
            
            # Follow-up Alerts
            if status in ["contacted", "replied"] and last_activity_time and last_activity_time < follow_up_threshold:
                d["last_activity"] = last_activity_time.isoformat()
                follow_up_deals.append(d)

    return {
        "counts": {
            "signals": total_signals,
            "leads": total_leads,
            "deals": total_deals
        },
        "health": {
            "healthy": healthy,
            "stagnant": stagnant,
            "at_risk": at_risk
        },
        "alerts": {
            "high_intent": high_intent_leads,
            "follow_up": follow_up_deals
        }
    }
