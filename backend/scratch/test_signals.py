import sys
import os
import argparse
from backend.core.db import signals_collection, leads_collection, db
from backend.services.signals.processor import process_raw_signals

# Sample data with a duplicate
test_data = [
    {
        "title": "NVIDIA raises $500M funding for AI expansion",
        "content": "NVIDIA announced major funding for AI development",
        "url": "https://test.com/nv-1",
        "source": "NewsAPI"
    },
    {
        "title": "NVIDIA raises $500M funding for AI expansion",
        "content": "NVIDIA announced major funding for AI development",
        "url": "https://test.com/nv-1",
        "source": "NewsAPI"
    },
    {
        "title": "NVIDIA hiring aggressively for AI engineers",
        "content": "NVIDIA expanding hiring in AI teams",
        "url": "https://test.com/nv-2",
        "source": "RSS"
    },
    {
        "title": "Apple launches new product line",
        "content": "Apple introduces new devices",
        "url": "https://test.com/apple-1",
        "source": "TechCrunch"
    }
]

def main():
    parser = argparse.ArgumentParser(description="Test Signal Pipeline")
    parser.add_argument("--reset", action="store_true", help="Reset Database")
    args = parser.parse_args()

    if args.reset:
        print("[RESET] Dropping signals and leads collections...")
        db.drop_collection("signals")
        db.drop_collection("leads")
        # Ensure indexes are re-created
        from backend.core.db import init_db, DB_NAME
        print(f"[INFO] Active Database: {DB_NAME}")
        init_db()

    print("\n[START] Processing raw signals...")
    results = process_raw_signals(test_data)
    
    print("\n[SUMMARY]")
    print(f"New Signals: {results.get('new')}")
    print(f"Duplicates Blocked: {results.get('duplicates')}")
    
    print("\n[DB CHECK]")
    sig_count = signals_collection.count_documents({})
    lead_count = leads_collection.count_documents({})
    print(f"Total Signals in DB: {sig_count}")
    print(f"Total Leads in DB: {lead_count}")

    print("\n[SAMPLE CHECK]")
    for sig in signals_collection.find().limit(3):
        print(f"Signal: {sig.get('title')}")
        print(f" - Category: {sig.get('category')}")
        print(f" - Relevance Score: {sig.get('relevance_score')}")
        print(f" - Companies: {sig.get('company_mentions')}")

if __name__ == "__main__":
    main()
