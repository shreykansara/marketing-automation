import os
import sys
from bson import ObjectId

# Ensure we can import from backend
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.core.db import leads_collection, deals_collection, companies_collection

def migrate():
    print("Starting relational migration...")
    
    # 1. Process Leads
    leads = list(leads_collection.find({"company_id": {"$exists": False}}))
    print(f"Found {len(leads)} leads needing linkage.")
    
    for lead in leads:
        company_name = lead.get("company")
        if not company_name:
            continue
            
        # Ensure company exists in registry
        company = companies_collection.find_one({"name": company_name})
        if not company:
            # Create if missing (defensive)
            res = companies_collection.insert_one({"name": company_name, "email_ids": []})
            company_id = res.inserted_id
        else:
            company_id = company["_id"]
            
        leads_collection.update_one(
            {"_id": lead["_id"]},
            {"$set": {"company_id": company_id}}
        )
        
    # 2. Process Deals
    deals = list(deals_collection.find({"company_id": {"$exists": False}}))
    print(f"Found {len(deals)} deals needing linkage.")
    
    for deal in deals:
        company_name = deal.get("company")
        if not company_name:
            continue
            
        company = companies_collection.find_one({"name": company_name})
        if not company:
            res = companies_collection.insert_one({"name": company_name, "email_ids": []})
            company_id = res.inserted_id
        else:
            company_id = company["_id"]
            
        deals_collection.update_one(
            {"_id": deal["_id"]},
            {"$set": {"company_id": company_id}}
        )

    print("Migration complete. All Leads and Deals linked to Companies registry.")

if __name__ == "__main__":
    migrate()
