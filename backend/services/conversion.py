import uuid
from datetime import datetime, timezone
from data.db import leads_collection, deals_collection

def convert_leads_to_deals():
    # 1. Fetch High Intent Leads
    qualified_leads = list(leads_collection.find({"intent_score": {"$gte": 60}}))
    
    deals_created = 0
    skipped_duplicates = 0
    
    for lead in qualified_leads:
        company = lead.get("company")
        
        # 2. Prevent Duplicate Deals
        existing_deal = deals_collection.find_one({"company": company})
        if existing_deal:
            skipped_duplicates += 1
            continue
            
        # 3. Create Deal Structure
        new_deal = {
            "id": str(uuid.uuid4()),
            "company": company,
            "stage": "Lead",
            "value": 50000,
            "last_activity": datetime.now(timezone.utc).isoformat(),
            "activation_step": None,
            "source": "auto_generated",
            "stakeholders": [
                {
                    "role": "CTO",
                    "contacted": False,
                    "responded": False
                },
                {
                    "role": "Compliance",
                    "contacted": False,
                    "responded": False
                },
                {
                    "role": "Business",
                    "contacted": False,
                    "responded": False
                }
            ]
        }
        
        # 4. Insert into database
        deals_collection.insert_one(new_deal)
        deals_created += 1
        
    return {
        "message": "Conversion engine run completed.",
        "deals_created": deals_created,
        "skipped_duplicates": skipped_duplicates
    }
