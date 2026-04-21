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

def init_db():
    # Ensure unique indexes for de-duplication
    signals_collection.create_index("hash", unique=True)
    companies.create_index("name", unique=True)
