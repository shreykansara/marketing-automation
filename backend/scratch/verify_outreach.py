from data.db import leads_collection, deals_collection
from services.conversion import convert_leads_to_deals
import logging

logging.basicConfig(level=logging.INFO)

# 1. Update Acme Corp lead with high intent and some signals
dummy_signals = [
    {"signal_type": "funding", "description": "Acme Corp raised $100M Series C", "timestamp": "2026-04-15T12:00:00Z"},
    {"signal_type": "hiring", "description": "Acme Corp hiring 50 new engineers", "timestamp": "2026-04-16T10:00:00Z"}
]

leads_collection.update_one(
    {"company": "Acme Corp"},
    {"$set": {"intent_score": 85, "signals": dummy_signals}}
)

print("Updated Acme Corp lead.")

# 2. Run conversion
deals_collection.delete_many({}) # Clean start for test
res = convert_leads_to_deals()
print(f"Conversion result: {res}")

# 3. Test Outreach Engine
from services.outreach_engine import bulk_generate_outreach
outreach_res = bulk_generate_outreach()
print(f"Outreach generation count: {len(outreach_res)}")
if outreach_res:
    print(f"First outreach persona: {outreach_res[0]['personas'][0]['role']}")
    print(f"First outreach message: {outreach_res[0]['personas'][0]['sequence'][0]['message']}")
