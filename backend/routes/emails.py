from fastapi import APIRouter, HTTPException
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
