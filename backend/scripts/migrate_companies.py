import os
import sys
from datetime import datetime, timezone

# Add backend to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
    sys.path.append(project_root)

from backend.core.db import companies_collection, leads_collection, deals_collection, emails_collection

def migrate():
    print("Starting migration to 'companies' collection...")
    
    # 1. Process Deals
    deals = list(deals_collection.find())
    print(f"Processing {len(deals)} deals...")
    for deal in deals:
        company_name = deal.get("company")
        email_refs = deal.get("emails", [])
        
        # Fetch actual email addresses
        email_docs = list(emails_collection.find({"_id": {"$in": email_refs}}))
        email_ids = set()
        for doc in email_docs:
            if doc.get("sender"): email_ids.add(doc["sender"])
            if doc.get("receiver"): email_ids.add(doc["receiver"])
        
        companies_collection.update_one(
            {"name": company_name},
            {
                "$set": {
                    "is_deal_active": True,
                    "is_lead_active": False,
                    "email_ids": list(email_ids)
                }
            },
            upsert=True
        )
        print(f"  - Migrated deal: {company_name}")

    # 2. Process Leads
    leads = list(leads_collection.find())
    print(f"Processing {len(leads)} leads...")
    for lead in leads:
        company_name = lead.get("company")
        
        # Check if already handled by deal (Mutual Exclusivity)
        if companies_collection.find_one({"name": company_name, "is_deal_active": True}):
            print(f"  - Skipping lead (already active deal): {company_name}")
            continue

        email_refs = lead.get("emails", [])
        email_docs = list(emails_collection.find({"_id": {"$in": email_refs}}))
        email_ids = set()
        for doc in email_docs:
            if doc.get("sender"): email_ids.add(doc["sender"])
            if doc.get("receiver"): email_ids.add(doc["receiver"])

        companies_collection.update_one(
            {"name": company_name},
            {
                "$set": {
                    "is_deal_active": False,
                    "is_lead_active": True,
                    "email_ids": list(email_ids)
                }
            },
            upsert=True
        )
        print(f"  - Migrated lead: {company_name}")

    print("Migration complete.")

if __name__ == "__main__":
    migrate()
