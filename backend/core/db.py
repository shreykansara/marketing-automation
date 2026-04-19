import os
from dotenv import load_dotenv
from pymongo import MongoClient, ASCENDING

# Load .env from project root
base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
env_path = os.path.join(base_dir, ".env")
load_dotenv(env_path)

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME", "pipeline_db")

# Initialize connection
client = MongoClient(MONGO_URI)
db = client[DB_NAME]

# Collections
signals_collection = db["signals"]
leads_collection = db["leads"]
deals_collection = db["deals"]
emails_collection = db["emails"]
companies = db["companies"]

def init_db():
    """Initialize indexes and TTL according to new 5-collection schema."""
    
    # 1. Signals: Unique hash, 5-day TTL
    signals_collection.create_index([("hash", ASCENDING)], unique=True)
    # Maintain internal created_at for TTL, as 'published' might be older than 5 days
    try:
        signals_collection.drop_index("created_at_1")
    except:
        pass
    signals_collection.create_index([("created_at", ASCENDING)], expireAfterSeconds=432000)
    signals_collection.create_index([("company_names", ASCENDING)])
    signals_collection.create_index([("category", ASCENDING)])
    
    # 2. Leads: Unique company name + Relational link
    leads_collection.create_index([("company", ASCENDING)], unique=True)
    leads_collection.create_index([("company_id", ASCENDING)])
    
    # 3. Deals: Unique company name mapping + Relational link
    deals_collection.create_index([("company", ASCENDING)], unique=True)
    deals_collection.create_index([("company_id", ASCENDING)])

    # 4. Emails: Unified lookup
    emails_collection.create_index([("sender", ASCENDING)])
    emails_collection.create_index([("receiver", ASCENDING)])
    emails_collection.create_index([("timestamp", ASCENDING)])
    emails_collection.create_index([("is_logged", ASCENDING)])
    
    # 5. Companies: Unified point of truth
    companies.create_index([("name", ASCENDING)], unique=True)
    companies.create_index([("email_ids", ASCENDING)])
    
    print("Database structure refactored. 5 collections initialized with indexes.")

if __name__ == "__main__":
    init_db()
