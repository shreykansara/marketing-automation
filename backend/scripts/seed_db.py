import os
import uuid
import hashlib
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv
from pymongo import MongoClient

# 1. Load Environment & Connect
base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
load_dotenv(os.path.join(base_dir, ".env"))

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME", "pipeline_db")

client = MongoClient(MONGO_URI)
db = client[DB_NAME]

print(f"--- Seeding Database: {DB_NAME} ---")

def generate_hash(text):
    return hashlib.md5(text.encode()).hexdigest()

def seed():
    # --- 1. SEED COMPANIES ---
    company_data = [
        {"name": "innovate ai", "is_lead_active": True, "is_deal_active": False, "is_archived": False, "email_ids": ["ceo@innovate-ai.io"], "first_seen_at": datetime.now(timezone.utc) - timedelta(days=5)},
        {"name": "green energy corp", "is_lead_active": False, "is_deal_active": True, "is_archived": False, "email_ids": ["procurement@ge-corp.com"], "first_seen_at": datetime.now(timezone.utc) - timedelta(days=10)},
        {"name": "fintech global", "is_lead_active": True, "is_deal_active": False, "is_archived": False, "email_ids": ["support@fintech-global.net"], "first_seen_at": datetime.now(timezone.utc) - timedelta(days=2)},
        {"name": "cyber-shield", "is_lead_active": False, "is_deal_active": True, "is_archived": False, "email_ids": ["security@cybershield.com", "billing@cybershield.com"], "first_seen_at": datetime.now(timezone.utc) - timedelta(days=15)},
        {"name": "logistics-flow", "is_lead_active": True, "is_deal_active": False, "is_archived": False, "email_ids": ["ops@logi-flow.com"], "first_seen_at": datetime.now(timezone.utc) - timedelta(days=1)},
        {"name": "cloud-nest", "is_lead_active": True, "is_deal_active": False, "is_archived": False, "email_ids": ["eng@cloudnest.com"], "first_seen_at": datetime.now(timezone.utc) - timedelta(days=3)}
    ]
    
    comp_map = {}
    for c in company_data:
        res = db.companies.find_one_and_update(
            {"name": c["name"]},
            {"$set": c},
            upsert=True,
            return_document=True
        )
        comp_map[c["name"]] = res["_id"]
    print(f"✓ {len(company_data)} Companies seeded.")

    # --- 2. SEED SIGNALS ---
    signals = [
        {"title": "Innovate AI hiring VP of Sales", "company_names": ["innovate ai"], "category": "hiring", "relevance_score": 85, "status": "enriched", "created_at": datetime.now(timezone.utc) - timedelta(hours=2)},
        {"title": "Cyber-Shield raises $50M Series C", "company_names": ["cyber-shield"], "category": "fundraising", "relevance_score": 95, "status": "enriched", "created_at": datetime.now(timezone.utc) - timedelta(days=1)},
        {"title": "Logistics-Flow seeking automation partners", "company_names": ["logistics-flow"], "category": "partnership", "relevance_score": 75, "status": "enriched", "created_at": datetime.now(timezone.utc) - timedelta(hours=10)},
        {"title": "Cloud-Nest hiring 40+ DevOps engineers", "company_names": ["cloud-nest"], "category": "hiring", "relevance_score": 88, "status": "enriched", "created_at": datetime.now(timezone.utc) - timedelta(hours=1)},
        {"title": "Fintech Global expanding to APAC region", "company_names": ["fintech global"], "category": "expansion", "relevance_score": 70, "status": "enriched", "created_at": datetime.now(timezone.utc)}
    ]
    
    for s in signals:
        s["hash"] = generate_hash(s["title"])
        db.signals.update_one({"hash": s["hash"]}, {"$set": s}, upsert=True)
    print("✓ Signals seeded.")

    # --- 3. SEED EMAILS (The NEW Stuff) ---
    emails_data = [
        # Emails for Green Energy Corp (Deal - 3 emails)
        {"sender": "procurement@ge-corp.com", "receiver": "me@blostem.io", "subject": "Automated Fleet Management Proposal", "body": "Hi, we saw your platform's capabilities. Can you send over a proposal for 500 vehicles?", "timestamp": datetime.now(timezone.utc) - timedelta(days=2), "is_logged": True, "company_name": "green energy corp"},
        {"sender": "me@blostem.io", "receiver": "procurement@ge-corp.com", "subject": "Re: Automated Fleet Management Proposal", "body": "Absolutely. I've attached our specialized pricing for large-scale fleets.", "timestamp": datetime.now(timezone.utc) - timedelta(days=1), "is_logged": True, "company_name": "green energy corp"},
        {"sender": "procurement@ge-corp.com", "receiver": "me@blostem.io", "subject": "Re: Automated Fleet Management Proposal", "body": "The pricing looks fair. We need to discuss the integration timeline next week.", "timestamp": datetime.now(timezone.utc) - timedelta(hours=5), "is_logged": False, "company_name": "green energy corp"},
        
        # Emails for Cyber-Shield (Deal - 3 emails)
        {"sender": "security@cybershield.com", "receiver": "me@blostem.io", "subject": "Compliance inquiry", "body": "Do you support automated SOC2 audit trails for outreach tracking?", "timestamp": datetime.now(timezone.utc) - timedelta(days=3), "is_logged": True, "company_name": "cyber-shield"},
        {"sender": "me@blostem.io", "receiver": "security@cybershield.com", "subject": "Re: Compliance inquiry", "body": "Yes, every action is hashed and stored in our immutable audit collection.", "timestamp": datetime.now(timezone.utc) - timedelta(days=2), "is_logged": True, "company_name": "cyber-shield"},
        {"sender": "security@cybershield.com", "receiver": "me@blostem.io", "subject": "Re: Compliance inquiry", "body": "Great. Please send the security whitepaper for our review.", "timestamp": datetime.now(timezone.utc) - timedelta(days=1), "is_logged": False, "company_name": "cyber-shield"},
        
        # Lead Emails (1 each)
        {"sender": "ceo@innovate-ai.io", "receiver": "me@blostem.io", "subject": "Interested in sales automation", "body": "We are scaling our sales team and looking for tools to automate signal detection.", "timestamp": datetime.now(timezone.utc) - timedelta(days=1), "is_logged": False, "company_name": "innovate ai"},
        {"sender": "support@fintech-global.net", "receiver": "me@blostem.io", "subject": "Expansion plans", "body": "Heard about your APAC market intelligence data. Would like to learn more.", "timestamp": datetime.now(timezone.utc) - timedelta(hours=12), "is_logged": False, "company_name": "fintech global"},
        {"sender": "ops@logi-flow.com", "receiver": "me@blostem.io", "subject": "Partnership opportunity", "body": "We are evaluating new partners for our supply chain intelligence stack.", "timestamp": datetime.now(timezone.utc) - timedelta(hours=18), "is_logged": False, "company_name": "logistics-flow"},
        {"sender": "eng@cloudnest.com", "receiver": "me@blostem.io", "subject": "DevOps outreach", "body": "I'm interested in how your engine tracks engineering hiring signals so accurately.", "timestamp": datetime.now(timezone.utc) - timedelta(hours=2), "is_logged": False, "company_name": "cloud-nest"}
    ]
    
    email_ids_map = {} # company_name -> [ids]
    for m in emails_data:
        m["company_id"] = str(comp_map[m["company_name"]])
        res = db.emails.insert_one(m)
        if m["company_name"] not in email_ids_map:
            email_ids_map[m["company_name"]] = []
        email_ids_map[m["company_name"]].append(res.inserted_id)
    print(f"✓ {len(emails_data)} Emails seeded and linked.")

    # --- 4. SEED LEADS ---
    for company in ["innovate ai", "fintech global", "logistics-flow", "cloud-nest"]:
        related_signals = list(db.signals.find({"company_names": company}, {"_id": 1}))
        db.leads.update_one({"company": company}, {"$set": {
            "company": company,
            "company_id": comp_map[company],
            "signal_ids": [s["_id"] for s in related_signals],
            "emails": email_ids_map.get(company, []),
            "logs": [{"log_id": str(uuid.uuid4()), "timestamp": datetime.now(timezone.utc), "type": "SYSTEM", "message": "Initial outreach detected.", "metadata": {}}]
        }}, upsert=True)
    print("✓ Leads updated with email links.")

    # --- 5. SEED DEALS ---
    deals_config = [
        {"name": "green energy corp", "status": "negotiation", "intent": 95, "suggestion": "closing"},
        {"name": "cyber-shield", "status": "discovery", "intent": 88, "suggestion": "proposal"}
    ]
    for d in deals_config:
        db.deals.update_one({"company": d["name"]}, {"$set": {
            "company": d["name"],
            "company_id": comp_map[d["name"]],
            "status": d["status"],
            "intent_score": d["intent"],
            "emails": email_ids_map.get(d["name"], []),
            # Display format emails_received for UI
            "emails_received": [
                {"from": e["sender"], "body": e["body"], "timestamp": e["timestamp"].isoformat()} 
                for e in emails_data if e["company_name"] == d["name"] and e["sender"] != "me@blostem.io"
            ],
            "status_suggestion": {"suggested_status": d["suggestion"], "reason": "Consistent high-intent interactions.", "timestamp": datetime.now(timezone.utc).isoformat()}
        }}, upsert=True)
    print("✓ Deals updated with email threads.")

    print("\n--- Seeding Complete! ---")
    print("Blostem is now loaded with a cross-industry intelligence and communication dataset.")

if __name__ == "__main__":
    seed()
