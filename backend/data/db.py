import os
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")

# Initialize connection to MongoDB instance
client = MongoClient(MONGO_URI)

# Select database and collection
db = client[DB_NAME]
deals_collection = db["deals"]
signals_collection = db["signals"]
leads_collection = db["leads"]
companies_collection = db["companies"]
sync_state_collection = db["sync_state"]

