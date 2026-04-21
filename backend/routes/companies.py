from fastapi import APIRouter, HTTPException, Body
from backend.core.db import companies, leads_collection, deals_collection
from bson import ObjectId

router = APIRouter()

@router.get("/")
async def get_companies():
    """
    Get all companies with their registry status.
    """
    res = list(companies.find())
    for c in res:
        c["_id"] = str(c["_id"])
    return res

@router.patch("/{company_id}/emails")
async def update_company_emails(company_id: str, payload: dict = Body(...)):
    email_ids = payload.get("email_ids", [])
    companies.update_one(
        {"_id": ObjectId(company_id)},
        {"$set": {"emails": email_ids}}
    )
    return {"status": "success"}

@router.patch("/{company_id}/archive")
async def toggle_archive(company_id: str, payload: dict = Body(...)):
    is_archived = payload.get("is_archived", True)
    flag = "archived" if is_archived else "active"
    
    # Update Company
    companies.update_one(
        {"_id": ObjectId(company_id)},
        {"$set": {"flag": flag, "status": None}}
    )
    
    # Purge from pipelines
    leads_collection.delete_one({"company_id": ObjectId(company_id)})
    deals_collection.delete_one({"company_id": ObjectId(company_id)})
    
    return {"status": "success"}
