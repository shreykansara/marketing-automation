from fastapi import APIRouter, HTTPException
from data.db import outreach_sequences_collection

router = APIRouter(prefix="/api/outreach", tags=["outreach"])

@router.get("/sequences")
def get_all_sequences():
    """Returns all generated outreach sequences."""
    sequences = list(outreach_sequences_collection.find())
    for seq in sequences:
        seq.pop("_id", None)
    return {"data": sequences}

@router.post("/generate")
def generate_outreach(payload: dict = None):
    """
    DEPRECATED: System now uses surgical evaluate-and-trigger per deal.
    """
    return {
        "status": "deprecated",
        "message": "Bulk generation is deprecated. Use /api/deals/{id}/evaluate-and-trigger for adaptive execution."
    }
