from datetime import datetime, timezone
import uuid
import random
from data.db import signals_collection

def generate_mock_signals():
    """Generates mock market signals."""
    companies = ["Acme Corp", "TechNova", "Global Industries", "Stark Enterprises", "Wayne Tech"]
    signal_types = ["funding", "hiring", "product"]
    
    signals = []
    # Generate 5-10 random signals
    for _ in range(random.randint(5, 10)):
        sig_type = random.choice(signal_types)
        company = random.choice(companies)
        
        description = ""
        if sig_type == "funding":
            description = f"{company} just raised a $50M Series B round."
        elif sig_type == "hiring":
            description = f"{company} is rapidly hiring for their enterprise sales team."
        else:
            description = f"{company} announced a new AI-powered product line."
            
        signal = {
            "id": str(uuid.uuid4()),
            "company": company,
            "signal_type": sig_type,
            "description": description,
            "source": random.choice(["TechCrunch", "LinkedIn", "Press Release", "Twitter"]),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        signals.append(signal)
    return signals

def run_ingestion():
    """
    Simulates fetching market signals and inserting them into the database.
    Clears existing signals for testing purposes to prevent duplicate runaway growth.
    """
    signals = generate_mock_signals()
    
    # Optional: Clear existing signals to keep the demo clean
    # signals_collection.delete_many({})
    
    if signals:
        signals_collection.insert_many(signals)
        
    return {"message": f"Successfully ingested {len(signals)} signals.", "signals": signals}
