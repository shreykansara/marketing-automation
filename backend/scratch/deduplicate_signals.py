import os
import sys
from pymongo import MongoClient, ASCENDING

# Ensure we can import from backend
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.core.db import signals_collection

def deduplicate():
    print("Scanning for duplicate signal hashes...")
    
    pipeline = [
        {"$group": {
            "_id": "$hash",
            "count": {"$sum": 1},
            "ids": {"$push": "$_id"}
        }},
        {"$match": {"count": {"$gt": 1}}}
    ]
    
    duplicates = list(signals_collection.aggregate(pipeline))
    print(f"Found {len(duplicates)} duplicate hashes.")
    
    total_removed = 0
    for doc in duplicates:
        # Keep the first one, remove the rest
        to_remove = doc['ids'][1:]
        res = signals_collection.delete_many({"_id": {"$in": to_remove}})
        total_removed += res.deleted_count
        
    print(f"Deduplication complete. Removed {total_removed} documents.")

if __name__ == "__main__":
    deduplicate()
