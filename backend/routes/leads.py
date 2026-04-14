from fastapi import APIRouter
from data.db import leads_collection
from services.lead_engine import generate_leads

router = APIRouter(prefix="/api/leads", tags=["leads"])

@router.get("")
def get_leads():
    # Fetch all leads, sorted by intent_score descending
    leads = list(leads_collection.find().sort("intent_score", -1))
    
    # Remove internal MongoDB ID
    for lead in leads:
        lead.pop("_id", None)
        
    return {"data": leads}

@router.post("/generate")
def trigger_lead_generation():
    # Run the aggregation logic
    result = generate_leads()
    return result
