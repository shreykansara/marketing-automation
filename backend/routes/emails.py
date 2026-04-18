from fastapi import APIRouter
from backend.core.db import emails_collection
from pymongo import DESCENDING

router = APIRouter()

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
            e["timestamp"] = e["timestamp"].isoformat()
            
    return emails
