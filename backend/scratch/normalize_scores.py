from backend.core.db import signals_collection

def convert_scores():
    signals = signals_collection.find({"relevance_score": {"$exists": True}})
    count = 0
    for s in signals:
        try:
            old_score = s["relevance_score"]
            new_score = int(old_score)
            if type(old_score) != int:
                signals_collection.update_one(
                    {"_id": s["_id"]},
                    {"$set": {"relevance_score": new_score}}
                )
                count += 1
        except (ValueError, TypeError):
            # Fallback for truly invalid values
            signals_collection.update_one(
                {"_id": s["_id"]},
                {"$set": {"relevance_score": 0}}
            )
            count += 1
    print(f"Migration complete: Normalized {count} records.")

if __name__ == "__main__":
    convert_scores()
