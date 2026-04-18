from collections import defaultdict
from datetime import datetime, timezone
from backend.core.db import signals_collection, leads_collection
from backend.services.leads.scoring import calculate_intent_score
from backend.services.deals.manager import handle_auto_unarchive

def get_priority(score):
    if score >= 70:
        return "high"
    elif score >= 40:
        return "medium"
    return "low"

def update_lead_for_company(company: str):
    """
    Minimal Lead Aggregation: Update company lead based on enriched signals.
    """
    company_clean = company.strip()
    
    # Simple matching: company name must be in company_mentions list
    signals = list(signals_collection.find({
        "status": "enriched",
        "company_mentions": company_clean
    }))

    if not signals:
        return

    categories = defaultdict(int)
    for s in signals:
        cat = (s.get("category") or "general").lower().strip()
        categories[cat] += 1

    lead_doc = {
        "company": company_clean.lower(),
        "signal_ids": [s["_id"] for s in signals],
        "signal_count": len(signals),
        "categories": dict(categories),
        "last_activity": max(s["created_at"] for s in signals),
        "status": "active",
        "updated_at": datetime.now(timezone.utc)
    }
    
    # Calculate score
    lead_doc["intent_score"] = calculate_intent_score(lead_doc)
    lead_doc["priority"] = get_priority(lead_doc["intent_score"])

    leads_collection.update_one(
        {"company": company_clean.lower()},
        {"$set": lead_doc},
        upsert=True
    )
    
    # Module 3: Auto-unarchive deal if it exists
    handle_auto_unarchive(company_clean)
