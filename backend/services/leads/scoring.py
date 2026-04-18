from datetime import datetime, timezone

WEIGHTS = {
    "funding": 40,
    "acquisition": 35,
    "partnership": 30,
    "product_launch": 25,
    "hiring": 20,
    "expansion": 20,
    "technology": 10,
    "general": 5
}

def calculate_intent_score(lead: dict) -> int:
    """
    Hardened Intent Scoring: Calculates a prioritized score for a company lead.
    Clamped at 100.
    """
    # 1. Category contribution (Normalized keys)
    category_score = sum(
        WEIGHTS.get(cat.lower().strip(), 5) * count
        for cat, count in lead.get("categories", {}).items()
    )

    # 2. Signal volume contribution
    signal_score = lead.get("signal_count", 0) * 5

    # 3. Recency contribution (Safe datetime handling)
    last_activity = lead.get("last_activity")
    if isinstance(last_activity, str):
        try:
            last_activity = datetime.fromisoformat(last_activity.replace("Z", "+00:00"))
        except ValueError:
            last_activity = None

    if not last_activity:
        recency_score = 0
    else:
        # Ensure last_activity is timezone-aware for comparison if it's utc
        if last_activity.tzinfo is None:
            last_activity = last_activity.replace(tzinfo=timezone.utc)
        
        now = datetime.now(timezone.utc)
        days_old = (now - last_activity).days
        recency_score = max(0, 30 - days_old)

    # 4. Final calculation and clamping
    total_score = category_score + signal_score + recency_score
    return min(total_score, 100)
