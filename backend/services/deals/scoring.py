from datetime import datetime, timezone
from backend.core.db import signals_collection

# Strategic weights for deal prioritization
DEAL_WEIGHTS = {
    "funding": 30,
    "acquisition": 35,
    "partnership": 30,
    "product_launch": 25,
    "hiring": 20,
    "general": 5
}

def calculate_deal_intent_score(lead_doc: dict) -> int:
    """
    Refactored Deal Scoring (v2): Derives intent from associated signals 
    since leads no longer store redundant metric fields.
    """
    signal_ids = lead_doc.get("signal_ids", [])
    if not signal_ids:
        return 0

    # 1. Fetch associated signals to compute metrics
    signals = list(signals_collection.find({"_id": {"$in": signal_ids}}))
    
    categories = {}
    last_activity = None
    for s in signals:
        cat = s.get("category", "general")
        categories[cat] = categories.get(cat, 0) + 1
        
        created = s.get("created_at")
        if created:
            if not last_activity or created > last_activity:
                last_activity = created

    # 2. Signal Contribution (Weighted)
    # Priority for 'funding' and 'hiring' as per previous requirements
    signal_score = (
        categories.get("funding", 0) * 30 +
        categories.get("hiring", 0) * 20
    )
    
    # Add other categories with base weights
    for cat, count in categories.items():
        if cat not in ["funding", "hiring"]:
            signal_score += DEAL_WEIGHTS.get(cat.lower(), 5) * count

    # 3. Recency Factor
    if not last_activity:
        recency_factor = 0
    else:
        if last_activity.tzinfo is None:
            last_activity = last_activity.replace(tzinfo=timezone.utc)
        
        now = datetime.now(timezone.utc)
        days_old = (now - last_activity).days
        recency_factor = max(0, 40 - days_old) # Scaled freshness bonus

    return min(100, int(signal_score + recency_factor))
