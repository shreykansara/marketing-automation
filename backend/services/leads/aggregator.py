import uuid
from datetime import datetime, timezone
from backend.core.db import signals_collection, leads_collection, deals_collection

def update_lead_for_company(company: str):
    """
    Refactored Lead Aggregator (v3): 
    - Enforces uniqueness per company.
    - Strictly prevents lead creation if a deal exists.
    - Adds unique UUIDs to log entries for specific deletion support.
    """
    company_clean = company.strip().lower()
    
    # 1. EXCLUSIVITY CHECK: No lead if a Deal exists
    if deals_collection.find_one({"company": company_clean}):
        return

    # 2. Find all enriched signals for this company
    signals = list(signals_collection.find({
        "status": "enriched",
        "company_names": company.strip()
    }))

    if not signals:
        return

    signal_ids = [s["_id"] for s in signals]
    existing_lead = leads_collection.find_one({"company": company_clean})

    from backend.core.db import companies
    
    # Update/Create Company Record (Mutual Exclusivity: lead=True, deal=False)
    # Block lead creation if the company is archived
    company_record = companies.find_one({"name": company_clean})
    if company_record and company_record.get("is_archived"):
        return

    company_res = companies.find_one_and_update(
        {"name": company_clean},
        {
            "$set": {
                "is_lead_active": True,
                "is_deal_active": False
            },
            "$setOnInsert": {
                "email_ids": [],
                "is_archived": False
            }
        },
        upsert=True,
        return_document=True
    )
    company_id = company_res["_id"]

    if existing_lead:
        # Update existing lead signal set and ensure company_id is linked
        leads_collection.update_one(
            {"company": company_clean},
            {
                "$set": {
                    "signal_ids": signal_ids,
                    "company_id": company_id
                }
            }
        )
    else:
        # Create unique lead entry with relational link
        lead_doc = {
            "company": company_clean,
            "company_id": company_id,
            "signal_ids": signal_ids,
            "emails": [],
            "logs": [
                {
                    "log_id": str(uuid.uuid4()),
                    "timestamp": datetime.now(timezone.utc),
                    "type": "LEAD_CREATED",
                    "message": f"Initial lead aggregation with {len(signals)} signals.",
                    "metadata": {"initial_count": len(signals)}
                }
            ]
        }
        leads_collection.insert_one(lead_doc)
