from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel, Field
from datetime import datetime, timezone
from backend.core.db import emails_collection, companies, leads_collection, deals_collection
import uuid
from bson import ObjectId
from backend.core.llm import llm_service
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
    company_id: Optional[str] = None
    company_name: Optional[str] = None

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
    
    # Pre-cache active companies for efficiency
    active_companies = list(companies.find({"$or": [{"is_lead_active": True}, {"is_deal_active": True}]}, {"_id": 1}))
    active_ids = {str(c["_id"]) for c in active_companies}

    for e in emails:
        e["_id"] = str(e["_id"])
        if e.get("timestamp"):
            if isinstance(e["timestamp"], datetime):
                e["timestamp"] = e["timestamp"].isoformat()
        
        # Determine if it "Needs Logging"
        # 1. Must be associated with a company
        # 2. Must not be logged already
        # 3. That company must have an active pipeline (Lead or Deal)
        e["is_loggable"] = False
        if e.get("company_id") and not e.get("is_logged"):
            if e["company_id"] in active_ids:
                e["is_loggable"] = True
            
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

    # Automatically try to link to an existing company
    from backend.core.db import companies
    
    # Check if either the sender or receiver matches a known company email
    matched_company = companies.find_one({
        "email_ids": {"$in": [email_dict["sender"], email_dict["receiver"]]}
    })
    
    if matched_company:
        email_dict["company_id"] = str(matched_company["_id"])
        email_dict["company_name"] = matched_company.get("name")
        
    result = emails_collection.insert_one(email_dict)
    
    return {
        "status": "success",
        "email_id": str(result.inserted_id)
    }

@router.patch("/{email_id}/company")
async def link_email_to_company(email_id: str, payload: dict = Body(...)):
    """
    Manually tags an unlinked email to a company.
    Expected payload: {"company_id": "...", "company_email": "sender@acme.com"}
    """
    from bson import ObjectId
    from backend.core.db import companies
    
    company_id_str = payload.get("company_id")
    company_email = payload.get("company_email")
    
    if not company_id_str or not company_email:
        raise HTTPException(status_code=400, detail="Missing company_id or company_email")
        
    company = companies.find_one({"_id": ObjectId(company_id_str)})
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
        
    email_doc = emails_collection.find_one({"_id": ObjectId(email_id)})
    if not email_doc:
        raise HTTPException(status_code=404, detail="Email not found")
        
    old_company_id = email_doc.get("company_id")
        
    # 1. Update the email document
    emails_collection.update_one(
        {"_id": ObjectId(email_id)},
        {"$set": {
            "company_id": str(company["_id"]),
            "company_name": company.get("name")
        }}
    )
    
    # 2. Add the remote email to the company's email_ids
    # Note: we explicitly use addToSet to avoid duplicates
    companies.update_one(
        {"_id": ObjectId(company_id_str)},
        {"$addToSet": {"email_ids": company_email}}
    )
    
    # 3. Handle Relinking (Unlink from old company)
    if old_company_id and old_company_id != company_id_str:
        companies.update_one(
            {"_id": ObjectId(old_company_id)},
            {"$pull": {"email_ids": company_email}}
        )
    
    return {"status": "success", "company_name": company.get("name")}

@router.get("/{email_id}/suggest-log")
async def suggest_email_log(email_id: str):
    """
    Use Groq to suggest a log message for this email.
    """
    email = emails_collection.find_one({"_id": ObjectId(email_id)})
    if not email:
        raise HTTPException(status_code=404, detail="Email not found")
        
    suggestion = llm_service.generate_email_log_suggestion(
        email.get("subject", ""), 
        email.get("body", "")
    )
    return {"suggestion": suggestion}

@router.post("/{email_id}/log")
async def confirm_email_log(email_id: str, message: str = Body(..., embed=True)):
    """
    Finalize the log and push it to the active pipeline (Lead or Deal).
    """
    import uuid
    from bson import ObjectId
    from backend.core.db import emails_collection, leads_collection, deals_collection

    email = emails_collection.find_one({"_id": ObjectId(email_id)})
    if not email:
        raise HTTPException(status_code=404, detail="Email not found")
        
    company_id = email.get("company_id")
    if not company_id:
        raise HTTPException(status_code=400, detail="Email not associated with a company")

    # 1. Locate the correct pipeline record
    target_coll = None
    # Check Deals first
    if deals_collection.find_one({"company_id": ObjectId(company_id)}):
        target_coll = deals_collection
    # Then check Leads
    elif leads_collection.find_one({"company_id": ObjectId(company_id)}):
        target_coll = leads_collection
        
    if target_coll is None:
        raise HTTPException(status_code=400, detail="No active pipeline (Lead/Deal) found for this company")

    # 2. Construct the log entry
    log_entry = {
        "log_id": str(uuid.uuid4()),
        "timestamp": datetime.now(timezone.utc),
        "type": "EMAIL_INTERACTION",
        "message": message,
        "metadata": {"email_id": email_id}
    }

    # 3. Batch Update: Add log to pipeline AND mark email as logged
    target_coll.update_one(
        {"company_id": ObjectId(company_id)},
        {"$push": {"logs": log_entry}}
    )

    emails_collection.update_one(
        {"_id": ObjectId(email_id)},
        {"$set": {"is_logged": True}}
    )

    return {"status": "success"}

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
