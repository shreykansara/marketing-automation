from fastapi import APIRouter
from backend.core.db import leads_collection

router = APIRouter()

@router.get("/")
async def get_leads():
    """
    Fetch all aggregated leads sorted by intent_score (descending).
    """
    leads = list(
        leads_collection
        .find()
        .sort("intent_score", -1)
    )

    for l in leads:
        l["_id"] = str(l["_id"])
        if "last_activity" in l and l["last_activity"]:
            l["last_activity"] = l["last_activity"].isoformat()
        if "updated_at" in l and l["updated_at"]:
            l["updated_at"] = l["updated_at"].isoformat()
        if "signal_ids" in l and l["signal_ids"]:
            l["signal_ids"] = [str(sid) for sid in l["signal_ids"]]

    return leads
