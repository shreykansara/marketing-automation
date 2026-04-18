from datetime import datetime, timezone

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
    Module 3 Scoring:
    intent_score = funding_signal * 30 + hiring_signal * 20 + recency_factor
    """
    categories = lead_doc.get("categories", {})
    
    # 1. Signal Contribution
    # User specifically mentioned funding*30 and hiring*20
    signal_score = (
        categories.get("funding", 0) * 30 +
        categories.get("hiring", 0) * 20
    )
    
    # Add other categories with base weights
    for cat, count in categories.items():
        if cat not in ["funding", "hiring"]:
            signal_score += DEAL_WEIGHTS.get(cat.lower(), 5) * count

    # 2. Recency Factor
    last_activity = lead_doc.get("last_activity")
    if not last_activity:
        recency_factor = 0
    else:
        if isinstance(last_activity, str):
            try:
                last_activity = datetime.fromisoformat(last_activity.replace("Z", "+00:00"))
            except:
                last_activity = None
        
        if last_activity:
            if last_activity.tzinfo is None:
                last_activity = last_activity.replace(tzinfo=timezone.utc)
            
            now = datetime.now(timezone.utc)
            days_old = (now - last_activity).days
            recency_factor = max(0, 40 - days_old) # Up to 40 points for freshness
        else:
            recency_factor = 0

    return min(100, signal_score + recency_factor)
