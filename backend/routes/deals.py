from fastapi import APIRouter, HTTPException, Body
from typing import List, Optional
from bson import ObjectId
from backend.core.db import deals_collection, leads_collection
from backend.services.deals.manager import convert_lead_to_deal
from backend.services.deals.outreach import generate_outreach_email, send_email_smtp, record_outreach
from backend.core.logger import get_logger

router = APIRouter()
logger = get_logger("routes.deals")

@router.post("/convert")
async def convert_lead(lead_id: str = Body(..., embed=True)):
    """Convert a qualified lead into a deal."""
    deal_id = convert_lead_to_deal(lead_id)
    if not deal_id:
        raise HTTPException(status_code=404, detail="Lead not found")
    return {"status": "success", "deal_id": deal_id}

@router.get("/")
async def list_deals(status: Optional[str] = None):
    """List all deals, optionally filtered by status."""
    query = {}
    if status:
        query["status"] = status
        
    deals = list(deals_collection.find(query).sort("updated_at", -1))
    for d in deals:
        d["_id"] = str(d["_id"])
        d["lead_id"] = str(d["lead_id"])
    return deals

@router.get("/{deal_id}")
async def get_deal(deal_id: str):
    """Fetch details of a single deal."""
    deal = deals_collection.find_one({"_id": ObjectId(deal_id)})
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")
    deal["_id"] = str(deal["_id"])
    deal["lead_id"] = str(deal["lead_id"])
    return deal

@router.post("/{deal_id}/generate-outreach")
async def generate_outreach(deal_id: str):
    """Generate a personalized AI outreach email."""
    deal = deals_collection.find_one({"_id": ObjectId(deal_id)})
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")
    
    # Get context from signals (first 3)
    lead = leads_collection.find_one({"_id": deal["lead_id"]})
    context = f"Company focuses on {', '.join(lead.get('categories', {}).keys())}."
    
    email_data = generate_outreach_email(deal["company_name"], context)
    return email_data

@router.post("/{deal_id}/send-outreach")
async def send_outreach(
    deal_id: str, 
    to_email: str = Body(...),
    subject: str = Body(...),
    body: str = Body(...)
):
    """Send outreach email and record it."""
    success = send_email_smtp(to_email, subject, body)
    if success:
        record_outreach(deal_id, to_email, subject, body)
        return {"status": "success"}
    else:
        # Fallback: Still record it as record but mark failure? 
        # For now, just error out
        raise HTTPException(status_code=500, detail="Failed to send email via SMTP")

@router.patch("/{deal_id}/status")
async def update_status(deal_id: str, status: str = Body(..., embed=True)):
    """Manually update deal status (e.g., archive, close)."""
    valid_statuses = ["open", "contacted", "replied", "closed", "archived"]
    if status not in valid_statuses:
        raise HTTPException(status_code=400, detail="Invalid status")
        
    deals_collection.update_one(
        {"_id": ObjectId(deal_id)},
        {"$set": {"status": status, "updated_at": datetime.now(timezone.utc)}}
    )
    return {"status": "success"}
