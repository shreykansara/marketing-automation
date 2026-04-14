from datetime import datetime
from data.db import signals_collection, leads_collection

def compute_recency_score(latest_date_str: str) -> int:
    try:
        # Expected format: ISO 8601 string
        latest_date = datetime.fromisoformat(latest_date_str)
        # Use timezone-unaware if it's not provided, but usually it's in UTC.
        # It's safer to compare it properly or just use a basic delta.
        now = datetime.now(latest_date.tzinfo)
        delta_days = (now - latest_date).days
        
        if delta_days <= 2:
            return 20
        elif delta_days <= 7:
            return 10
        else:
            return 5
    except Exception:
        # Fallback if timestamp format is unexpected
        return 5

def generate_leads():
    # Fetch all signals from DB
    signals = list(signals_collection.find())
    
    # Group signals by company
    grouped_signals = {}
    for signal in signals:
        signal.pop("_id", None) # Clean ObjectId
        company = signal.get("company")
        if not company:
            continue
            
        if company not in grouped_signals:
            grouped_signals[company] = []
        grouped_signals[company].append(signal)

    # Calculate metrics and store
    upserted_count = 0
    for company, company_signals in grouped_signals.items():
        signal_count = len(company_signals)
        signal_types = len(set(s.get("signal_type") for s in company_signals if s.get("signal_type")))
        
        # Sort by timestamp descending to find latest
        # Handle missing timestamps safely
        sorted_signals = sorted(
            company_signals, 
            key=lambda x: x.get("timestamp", ""), 
            reverse=True
        )
        latest_str = sorted_signals[0].get("timestamp", "")
        recency_score = compute_recency_score(latest_str) if latest_str else 0
        
        # Intent score rule logic
        raw_intent_score = (signal_count * 10) + (signal_types * 15) + recency_score
        intent_score = min(raw_intent_score, 100)
        
        # Build lead payload
        lead_data = {
            "company": company,
            "signals": sorted_signals, # Store all associated signals
            "intent_score": intent_score,
            "last_updated": datetime.now().isoformat()
        }
        
        # Upsert rule
        leads_collection.update_one(
            {"company": company},
            {"$set": lead_data},
            upsert=True
        )
        upserted_count += 1
        
    return {"message": "Leads generated successfully", "total_leads_processed": upserted_count}
