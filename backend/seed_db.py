from data.mock_data import deals
from data.db import deals_collection

def seed_database():
    deals_collection.delete_many({})  # Clear existing collection to avoid duplicates during seeding
    if deals:
        deals_collection.insert_many(deals)
        print(f"Successfully seeded {len(deals)} deals into MongoDB.")
    else:
        print("No deals found to seed.")

if __name__ == "__main__":
    seed_database()
