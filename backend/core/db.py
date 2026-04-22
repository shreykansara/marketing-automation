import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
client = MongoClient(MONGO_URI)
db = client.pipeline_db

# 6-Collection Architecture
companies = db.companies
signals_collection = db.signals
leads_collection = db.leads
deals_collection = db.deals
emails_collection = db.emails
logs_collection = db.logs
users_collection = db.users
invite_codes_collection = db.invite_codes

def init_db():
    try:
        # Ensure unique indexes for de-duplication
        signals_collection.create_index("hash", unique=True)
        companies.create_index("name", unique=True)
        users_collection.create_index("email", unique=True)
        print("Database initialized successfully.")
    except Exception as e:
        print(f"Database initialization failed: {e}")
