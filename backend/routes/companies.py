from fastapi import APIRouter, HTTPException, Body
from typing import List
from bson import ObjectId
from backend.core.db import companies, leads_collection, deals_collection
from backend.core.logger import get_logger

router = APIRouter()
logger = get_logger("routes.companies")

@router.get("/")
async def get_companies():
    """
    List all companies in the registry.
    """
    comps = list(companies.find().sort("name", 1))
    for c in comps:
        c["_id"] = str(c["_id"])
    return comps

@router.patch("/{company_id}/emails")
async def update_company_emails(company_id: str, email_ids: List[str] = Body(..., embed=True)):
    """
    Manually update the email list for a company.
    """
    try:
        result = companies.update_one(
            {"_id": ObjectId(company_id)},
            {"$set": {"email_ids": email_ids}}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Company not found")
            
        return {"status": "success", "updated_count": result.modified_count}
    except Exception as e:
        logger.error(f"Failed to update company emails: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.patch("/{company_id}/archive")
async def toggle_company_archive(company_id: str, is_archived: bool = Body(..., embed=True)):
    """
    Toggle the archive status of a company.
    If archived, delete active leads and deals associated with it.
    """
    try:
        update_data = {"is_archived": is_archived}
        if is_archived:
            update_data["is_lead_active"] = False
            update_data["is_deal_active"] = False

        result = companies.update_one(
            {"_id": ObjectId(company_id)},
            {"$set": update_data}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Company not found")

        # If we are archiving, purge it from Leads and Deals
        if is_archived:
            leads_collection.delete_one({"company_id": ObjectId(company_id)})
            deals_collection.delete_one({"company_id": ObjectId(company_id)})

        return {"status": "success", "is_archived": is_archived}
    except Exception as e:
        logger.error(f"Failed to toggle archive status: {e}")
        raise HTTPException(status_code=500, detail=str(e))
