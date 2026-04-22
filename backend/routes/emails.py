from pydantic import BaseModel, Field
from datetime import datetime, timezone
from backend.core.db import emails_collection, companies, leads_collection, deals_collection, logs_collection
from bson import ObjectId
from backend.core.llm import llm_service
from backend.core.auth import get_current_user
from fastapi import APIRouter, HTTPException, Body, Depends
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

@router.get("/")
async def get_emails(current_user: dict = Depends(get_current_user)):
    """
    Use Case 8: Get emails with hydrated company names.
    """
    pipeline = [
        {"$sort": {"timestamp": DESCENDING}},
        {
            "$lookup": {
                "from": "companies",
                "localField": "company_id",
                "foreignField": "_id",
                "as": "company_data"
            }
        },
        {
            "$lookup": {
                "from": "companies",
                "pipeline": [
                    {"$match": {"status": {"$in": ["lead", "deal"]}}},
                    {"$project": {"_id": 1}}
                ],
                "as": "active_pipelines"
            }
        }
    ]
    
    emails = list(emails_collection.aggregate(pipeline))
    
    active_ids = set()
    if emails:
        active_ids = {str(c["_id"]) for c in emails[0].get("active_pipelines", [])}

    for e in emails:
        e["_id"] = str(e["_id"])
        comp = e.get("company_data")
        if comp:
            e["company_name"] = comp[0].get("name")
            e["company_id"] = str(comp[0].get("_id"))
            e["company_status"] = comp[0].get("status")
        else:
            e["company_name"] = None
            e["company_id"] = None
            e["company_status"] = None
        
        e.pop("company_data", None)
        e.pop("active_pipelines", None)
        
        if e.get("timestamp"):
            if isinstance(e["timestamp"], datetime):
                e["timestamp"] = e["timestamp"].isoformat()
        
        e["is_loggable"] = False
        if e.get("company_id") and not e.get("is_logged"):
            if str(e["company_id"]) in active_ids:
                e["is_loggable"] = True
            
    return emails

@router.post("/")
async def save_email(email: EmailCreate, current_user: dict = Depends(get_current_user)):
    """
    Save an email to the database (Browser Extension).
    """
    email_dict = email.dict()
    
    if isinstance(email_dict["timestamp"], str):
        email_dict["timestamp"] = datetime.fromisoformat(email_dict["timestamp"])
    elif email_dict["timestamp"] is None:
        email_dict["timestamp"] = datetime.now(timezone.utc)

    # Automatically try to link to an existing company
    matched_company = companies.find_one({
        "emails": {"$in": [email_dict["sender"], email_dict["receiver"]]}
    })
    
    if matched_company:
        email_dict["company_id"] = matched_company["_id"]
        
    result = emails_collection.insert_one(email_dict)
    
    return {
        "status": "success",
        "email_id": str(result.inserted_id)
    }

@router.patch("/{email_id}/company")
async def link_email_to_company(email_id: str, payload: dict = Body(...), current_user: dict = Depends(get_current_user)):
    """
    Manually tags an unlinked email to a company.
    """
    company_id_str = payload.get("company_id")
    company_email = payload.get("company_email")
    
    if not company_id_str or not company_email:
        raise HTTPException(status_code=400, detail="Missing company_id or company_email")
        
    company = companies.find_one({"_id": ObjectId(company_id_str)})
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
        
    emails_collection.update_one(
        {"_id": ObjectId(email_id)},
        {"$set": {
            "company_id": ObjectId(company_id_str)
        }}
    )
    
    companies.update_one(
        {"_id": ObjectId(company_id_str)},
        {"$addToSet": {"emails": company_email}}
    )
    
    return {"status": "success", "company_name": company.get("name")}

@router.post("/{email_id}/log")
async def confirm_email_log(email_id: str, message: str = Body(..., embed=True), current_user: dict = Depends(get_current_user)):
    """
    Finalize the log and push it to the active pipeline (Lead or Deal).
    """
    email = emails_collection.find_one({"_id": ObjectId(email_id)})
    if not email:
        raise HTTPException(status_code=404, detail="Email not found")
        
    company_id = email.get("company_id")
    if not company_id:
        raise HTTPException(status_code=400, detail="Email not associated with a company")

    company = companies.find_one({"_id": ObjectId(company_id)})
    if not company or not company.get("status"):
         raise HTTPException(status_code=400, detail="No active pipeline (Lead/Deal) found for this company")

    status = company["status"]
    if status == "lead":
        target_doc = leads_collection.find_one({"company_id": company["_id"]})
        field_to_set = "lead_id"
    else:
        target_doc = deals_collection.find_one({"company_id": company["_id"]})
        field_to_set = "deal_id"

    if not target_doc:
        raise HTTPException(status_code=404, detail=f"Pipeline entity for {status} not found")

    entity_id = target_doc["_id"]

    log_entry = {
        "entity_id": entity_id,
        "timestamp": datetime.now(timezone.utc),
        "type": "EMAIL",
        "message": message,
        "metadata": {"email_id": ObjectId(email_id)}
    }

    logs_collection.insert_one(log_entry)
    
    emails_collection.update_one(
        {"_id": ObjectId(email_id)},
        {"$set": {"is_logged": True, field_to_set: entity_id}}
    )

    return {"status": "success"}

@router.post("/generate")
async def generate_ai_email(recipient_email: str = Body(..., embed=True), current_user: dict = Depends(get_current_user)):
    """
    Generate an AI outreach email for a recipient contextually.
    If company not in database, generate a cold outreach draft.
    """
    print(f"[DEBUG] Generating AI email for: {recipient_email}")
    company = companies.find_one({"emails": {"$in": [recipient_email]}})
    
    # helper to get a nice name from email if company unknown
    def get_fallback_name(email):
        try:
            parts = email.split('@')[-1].split('.')
            domain = parts[0].lower()
            
            # Generic domains should not be used as company names
            generic_domains = ["gmail", "yahoo", "outlook", "hotmail", "icloud", "me", "live"]
            if domain in generic_domains:
                return "your company"
                
            return domain.capitalize() if domain else "your company"
        except:
            return "your company"

    if not company:
        # Scenario 2: Fallback to cold outreach generation
        fallback_name = get_fallback_name(recipient_email)
        generation = llm_service.generate_cold_outreach(recipient_email, fallback_name)
        return {
            "status": "success",
            "company": fallback_name,
            "current_state_detected": "cold_outreach",
            "generated": generation
        }
        
    status = company.get("status")
    if not status:
         # Internal company but no pipeline, still do cold outreach
         generation = llm_service.generate_cold_outreach(recipient_email, company["name"])
         return {
            "status": "success",
            "company": company["name"],
            "current_state_detected": "internal_no_pipeline",
            "generated": generation
         }

    if status == "lead":
        target = leads_collection.find_one({"company_id": company["_id"]})
    else:
        target = deals_collection.find_one({"company_id": company["_id"]})

    if not target:
        # Fallback if pipeline data missing
        generation = llm_service.generate_cold_outreach(recipient_email)
        return {
            "status": "success",
            "company": company["name"],
            "current_state_detected": f"missing_{status}_data",
            "generated": generation
        }

    logs = list(logs_collection.find({"entity_id": target["_id"]}).sort("timestamp", DESCENDING).limit(10))
    log_texts = [l["message"] for l in logs]

    generation = llm_service.generate_outreach_email(log_texts, status, company["name"])
    
    return {
        "status": "success",
        "company": company["name"],
        "current_state_detected": status,
        "generated": generation
    }

@router.delete("/{email_id}")
async def delete_email(email_id: str, current_user: dict = Depends(get_current_user)):
    """
    Delete an email from the database.
    """
    result = emails_collection.delete_one({"_id": ObjectId(email_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Email not found")
    return {"status": "success"}
