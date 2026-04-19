from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel, Field
from datetime import datetime, timezone
from backend.core.db import emails_collection
from pymongo import DESCENDING
from typing import Optional

router = APIRouter()

class EmailCreate(BaseModel):
    sender: str
    receiver: str
    subject: str
    body: str
    timestamp: Optional[datetime] = Field(default_factory=lambda: datetime.now(timezone.utc))
    is_logged: bool = False

@router.get("/")
async def get_emails():
    """
    Use Case 8: Get emails and display on the UI sorted by date (latest first).
    """
    emails = list(
        emails_collection
        .find()
        .sort("timestamp", DESCENDING)
    )
    
    for e in emails:
        e["_id"] = str(e["_id"])
        if e.get("timestamp"):
            if isinstance(e["timestamp"], datetime):
                e["timestamp"] = e["timestamp"].isoformat()
            
    return emails

@router.post("/")
async def save_email(email: EmailCreate):
    """
    New Endpoint: Save an email to the database.
    Used by the Browser Extension.
    """
    email_dict = email.dict()
    
    # Ensure timestamp is datetime object for Mongo
    if isinstance(email_dict["timestamp"], str):
        email_dict["timestamp"] = datetime.fromisoformat(email_dict["timestamp"])
    elif email_dict["timestamp"] is None:
        email_dict["timestamp"] = datetime.now(timezone.utc)

    result = emails_collection.insert_one(email_dict)
    
    return {
        "status": "success",
        "email_id": str(result.inserted_id)
    }

@router.post("/generate")
async def generate_ai_email(recipient_email: str = Body(..., embed=True)):
    """
    New Endpoint: Generate an AI outreach email for a recipient.
    Used by the Browser Extension's 'Compose' mode.
    """
    from backend.core.db import leads_collection, deals_collection
    from backend.core.llm import llm_service

    # 1. Identify the company by recipient_email
    # Search for any email document involving this recipient
    matching_emails = list(emails_collection.find({
        "$or": [{"sender": recipient_email}, {"receiver": recipient_email}]
    }))
    
    if not matching_emails:
        raise HTTPException(status_code=404, detail="Recipient not found in our communications history.")
        
    email_ids = [e["_id"] for e in matching_emails]

    # 2. Find associated lead or deal
    target = deals_collection.find_one({"emails": {"$in": email_ids}})
    if not target:
        target = leads_collection.find_one({"emails": {"$in": email_ids}})
        
    if not target:
        raise HTTPException(status_code=404, detail="No lead or deal associated with this recipient found.")

    # 3. Gather Context
    company_name = target.get("company", "Valued Partner")
    logs = target.get("logs", [])
    current_status = target.get("status", "Unknown")

    # 4. Generate AI Email
    generation = llm_service.generate_outreach_email(logs, current_status, company_name)
    
    return {
        "status": "success",
        "company": company_name,
        "current_state_detected": current_status,
        "generated": generation
    }
