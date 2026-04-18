import os
from dotenv import load_dotenv
from pymongo import MongoClient, ASCENDING
# Load .env from project root
base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
env_path = os.path.join(base_dir, ".env")
load_dotenv(env_path)

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME", "blostem")

# Initialize connection
client = MongoClient(MONGO_URI)
db = client[DB_NAME]

# Collections
signals_collection = db["signals"]
leads_collection = db["leads"]
companies_collection = db["companies"]
deals_collection = db["deals"]

def init_db():
    """Initialize indexes and TTL."""
    # Signals: Unique hash, 30-day TTL, and optimization indexes
    signals_collection.create_index([("hash", ASCENDING)], unique=True)
    signals_collection.create_index([("created_at", ASCENDING)], expireAfterSeconds=2592000)
    signals_collection.create_index([("company_mentions", ASCENDING)])
    signals_collection.create_index([("category", ASCENDING)])
    
    # Leads: Unique company name
    leads_collection.create_index([("company", ASCENDING)], unique=True)
    
    # Companies: Basic metadata
    companies_collection.create_index([("name", ASCENDING)], unique=True)

    # Deals: Unique lead mapping and searchable columns
    try:
        deals_collection.drop_index("lead_id_1")
    except:
        pass
    deals_collection.create_index([("lead_id", ASCENDING)], unique=True)
    deals_collection.create_index([("company_name", ASCENDING)])
    deals_collection.create_index([("status", ASCENDING)])
    
    print("Database initialized with indexes and TTL logic.")

if __name__ == "__main__":
    init_db()
