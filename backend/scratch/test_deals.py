import os
from bson import ObjectId
from backend.core.db import leads_collection, deals_collection, signals_collection
from backend.services.deals.manager import convert_lead_to_deal
from backend.services.leads.aggregator import update_lead_for_company
from backend.services.deals.outreach import generate_outreach_email

def main():
    print("[TEST] Starting Deal Engine Verification...")
    
    # 1. Get a sample lead (should exist from previous tests)
    lead = leads_collection.find_one({"company": "nvidia"})
    if not lead:
        print("[ERROR] No lead found for 'nvidia'. Run test_signals first.")
        return
    
    lead_id = str(lead["_id"])
    print(f"[STEP 1] Found lead for {lead['company']} (id: {lead_id})")
    
    # 2. Convert Lead to Deal
    deal_id = convert_lead_to_deal(lead_id)
    print(f"[STEP 2] Converted to Deal (id: {deal_id})")
    
    # 3. Verify Deal data
    deal = deals_collection.find_one({"_id": ObjectId(deal_id)})
    print(f"[STEP 3] Deal Status: {deal['status']}, Intent Score: {deal['intent_score']}")
    
    # 4. Test Manual Archive
    deals_collection.update_one({"_id": ObjectId(deal_id)}, {"$set": {"status": "archived"}})
    print(f"[STEP 4] Deal manually archived.")
    
    # 5. Test Auto-Unarchive Hook
    # Simulate a new signal arriving for NVIDIA
    print(f"[STEP 5] Simulating new signal aggregation for NVIDIA...")
    update_lead_for_company("nvidia")
    
    # Check if unarchived
    deal = deals_collection.find_one({"_id": ObjectId(deal_id)})
    print(f"[STEP 5 RESULT] Deal status after aggregation: {deal['status']}")
    
    # 6. Test AI Outreach Generation
    print("[STEP 6] Testing AI Outreach generation...")
    context = "NVIDIA just announced major AI expansion."
    email = generate_outreach_email("NVIDIA", context)
    print(f"[STEP 6 RESULT] Generated Subject: {email.get('subject')}")
    print(f"[STEP 6 RESULT] Generated Body First Line: {email.get('body').split('.')[0]}...")

if __name__ == "__main__":
    main()
