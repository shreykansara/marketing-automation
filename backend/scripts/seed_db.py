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
    # --- 1. SEED COMPANIES (Fintech & Banking Niche) ---
    company_data = [
        {"name": "jupiter neobank", "is_lead_active": True, "is_deal_active": False, "is_archived": False, "email_ids": ["founder@jupiter.money"], "first_seen_at": datetime.now(timezone.utc) - timedelta(days=5)},
        {"name": "federal bank", "is_lead_active": False, "is_deal_active": True, "is_archived": False, "email_ids": ["digital.assets@federalbank.co.in"], "first_seen_at": datetime.now(timezone.utc) - timedelta(days=12)},
        {"name": "fi money", "is_lead_active": True, "is_deal_active": False, "is_archived": False, "email_ids": ["partnerships@fi.care"], "first_seen_at": datetime.now(timezone.utc) - timedelta(days=3)},
        {"name": "indwealth", "is_lead_active": False, "is_deal_active": True, "is_archived": False, "email_ids": ["wealth.ops@indwealth.in"], "first_seen_at": datetime.now(timezone.utc) - timedelta(days=20)},
        {"name": "razorpayx", "is_lead_active": True, "is_deal_active": False, "is_archived": False, "email_ids": ["banking@razorpay.com"], "first_seen_at": datetime.now(timezone.utc) - timedelta(days=2)},
        {"name": "dbs bank india", "is_lead_active": False, "is_deal_active": False, "is_archived": False, "email_ids": ["innovation@dbs.com"], "first_seen_at": datetime.now(timezone.utc)}
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
    print(f"✓ {len(company_data)} Fintech/Banking Companies seeded.")

    # --- 2. SEED SIGNALS (Investment & Banking Intent) ---
    signals = [
        {"title": "Jupiter Neobank seeking higher yield FD partners for its pro users", "company_names": ["jupiter neobank"], "category": "expansion", "relevance_score": 95, "status": "enriched", "created_at": datetime.now(timezone.utc) - timedelta(hours=4)},
        {"title": "Federal Bank looking to digitize its fixed deposit distribution layer", "company_names": ["federal bank"], "category": "product_launch", "relevance_score": 98, "status": "enriched", "created_at": datetime.now(timezone.utc) - timedelta(days=1)},
        {"title": "Fi Money partnership with ICICI for high-frequency smart deposits", "company_names": ["fi money"], "category": "partnership", "relevance_score": 88, "status": "enriched", "created_at": datetime.now(timezone.utc) - timedelta(hours=10)},
        {"title": "INDWealth hiring wealth managers to scale its fixed-income vertical", "company_names": ["indwealth"], "category": "hiring", "relevance_score": 82, "status": "enriched", "created_at": datetime.now(timezone.utc) - timedelta(days=2)},
        {"title": "RazorpayX exploring neo-banking full-stack infrastructure integration", "company_names": ["razorpayx"], "category": "expansion", "relevance_score": 92, "status": "enriched", "created_at": datetime.now(timezone.utc) - timedelta(hours=1)},
        {"title": "DBS Bank India to invest $100M in digital banking infrastructure", "company_names": ["dbs bank india"], "category": "funding", "relevance_score": 85, "status": "enriched", "created_at": datetime.now(timezone.utc) - timedelta(hours=12)}
    ]
    
    for s in signals:
        s["hash"] = generate_hash(s["title"])
        db.signals.update_one({"hash": s["hash"]}, {"$set": s}, upsert=True)
    print("✓ Industry-niche Signals seeded.")

    # --- 3. SEED EMAILS (Professional, Long Bodies) ---
    emails_data = [
        # Federal Bank (Deal thread)
        {
            "sender": "digital.assets@federalbank.co.in", 
            "receiver": "sales@blostem.io", 
            "subject": "Inquiry regarding FD Distribution Middleware", 
            "body": "Dear Blostem Team,\n\nI am writing to you from the Digital Assets team at Federal Bank. We recently came across your middleware solution for API-based Fixed Deposit distribution and found it quite compelling.\n\nCurrently, our bank is looking to modernize our legacy deposit systems and expand our reach through third-party fintech associations. We would like to understand how your platform handles real-time reconciliation and automated interest rate synchronization across multiple partner interfaces.\n\nCould we schedule a discovery call for later this week to discuss a potential integration pilot? Looking forward to hearing from you.\n\nBest Regards,\nPraveen Kumar\nSenior VP - Digital Banking, Federal Bank", 
            "timestamp": datetime.now(timezone.utc) - timedelta(days=5), 
            "is_logged": True, 
            "company_name": "federal bank"
        },
        {
            "sender": "sales@blostem.io", 
            "receiver": "digital.assets@federalbank.co.in", 
            "subject": "Re: Inquiry regarding FD Distribution Middleware", 
            "body": "Dear Praveen,\n\nThank you for reaching out. We are quite familiar with Federal Bank's impressive digital roadmap and would be thrilled to support your modernization initiatives.\n\nRegarding your question on reconciliation: Blostem's engine uses a proprietary double-entry ledger system that ensures zero-latency sync between the core banking system (CBS) and the partner frontend. We also support dynamic rate-push capabilities through our unified API endpoint.\n\nI have attached our technical architecture whitepaper for your preliminary review. Would Thursday at 11 AM IST work for a brief demonstration?\n\nBest Regards,\nSales Engineering Team\nBlostem Infrastructure", 
            "timestamp": datetime.now(timezone.utc) - timedelta(days=4), 
            "is_logged": True, 
            "company_name": "federal bank"
        },
        {
            "sender": "digital.assets@federalbank.co.in", 
            "receiver": "sales@blostem.io", 
            "subject": "Re: Inquiry regarding FD Distribution Middleware", 
            "body": "Hello Team,\n\nThursday at 11 AM works perfectly. I will also be inviting our CTO and Head of Compliance to the call as we'd like to dive deeper into the security protocols and PII handling during the transit.\n\nCould you also prepare a brief overview of your current NBFC partnerships? We are interested in how you manage cross-institutional deposit flows. See you on Thursday.\n\nRegards,\nPraveen Kumar", 
            "timestamp": datetime.now(timezone.utc) - timedelta(days=1), 
            "is_logged": False, 
            "company_name": "federal bank"
        },

        # INDWealth (Deal thread)
        {
            "sender": "wealth.ops@indwealth.in", 
            "receiver": "sales@blostem.io", 
            "subject": "Optimizing Fixed Income returns via Blostem APIs", 
            "body": "Hi Blostem,\n\nWe are currently scaling our 'Fixed Income' vertical at INDWealth and are looking to integrate a more diverse range of Bank FDs for our premium users. \n\nWe require an infrastructure that allows for a seamless, one-click investment experience without redirecting users to external banking portals. Does your API suite support end-to-end KYC data transmission and nomination management as per RBI guidelines?\n\nWe are looking to move quickly on this as part of our quarterly roadmap. Please let us know your availability.\n\nBest,\nOperations Lead, INDWealth", 
            "timestamp": datetime.now(timezone.utc) - timedelta(days=2), 
            "is_logged": False, 
            "company_name": "indwealth"
        },

        # Jupiter (Lead inquiry)
        {
            "sender": "founder@jupiter.money", 
            "receiver": "sales@blostem.io", 
            "subject": "Exploring Infrastructure for Digital Deposits", 
            "body": "Hey Team,\n\nHope you're doing well. I noticed Blostem has been working on some interesting FD distribution tech for Neobanks. At Jupiter, we're constantly looking to improve the savings yield for our community.\n\nI'd like to understand how your platform manages the 'Switching' logic—allowing users to move from lower-yield savings to higher-yield FDs with zero friction. If your tech can handle the heavy lifting on the backend integration with our partner banks, we should definitely talk.\n\nLet me know who the right person is to spearhead this from your end.\n\nCheers,\nJitendra", 
            "timestamp": datetime.now(timezone.utc) - timedelta(hours=10), 
            "is_logged": False, 
            "company_name": "jupiter neobank"
        }
    ]
    
    email_ids_map = {}
    for m in emails_data:
        m["company_id"] = str(comp_map[m["company_name"]])
        res = db.emails.insert_one(m)
        if m["company_name"] not in email_ids_map:
            email_ids_map[m["company_name"]] = []
        email_ids_map[m["company_name"]].append(res.inserted_id)
    print(f"✓ {len(emails_data)} Professional Emails seeded.")

    # --- 4. UPDATE LEADS ---
    leads_list = ["jupiter neobank", "fi money", "razorpayx"]
    for company in leads_list:
        related_signals = list(db.signals.find({"company_names": company}, {"_id": 1}))
        db.leads.update_one({"company": company}, {"$set": {
            "company": company,
            "company_id": comp_map[company],
            "signal_ids": [s["_id"] for s in related_signals],
            "emails": email_ids_map.get(company, []),
            "logs": [{"log_id": str(uuid.uuid4()), "timestamp": datetime.now(timezone.utc), "type": "SYSTEM", "message": "High-relevance banking signal detected. Lead created.", "metadata": {}}]
        }}, upsert=True)
    print("✓ Leads synchronized.")

    # --- 5. UPDATE DEALS ---
    deals_config = [
        {"name": "federal bank", "status": "contacted", "intent": 98, "suggestion": "negotiation"},
        {"name": "indwealth", "status": "replied", "intent": 85, "suggestion": "engaged"}
    ]
    for d in deals_config:
        db.deals.update_one({"company": d["name"]}, {"$set": {
            "company": d["name"],
            "company_id": comp_map[d["name"]],
            "status": d["status"],
            "intent_score": d["intent"],
            "emails": email_ids_map.get(d["name"], []),
            "emails_received": [
                {"from": e["sender"], "body": e["body"], "timestamp": e["timestamp"].isoformat()} 
                for e in emails_data if e["company_name"] == d["name"] and e["sender"] != "sales@blostem.io"
            ],
            "status_suggestion": {"suggested_status": d["suggestion"], "reason": "Technical inquiry indicates deep evaluation state.", "timestamp": datetime.now(timezone.utc).isoformat()}
        }}, upsert=True)
    print("✓ Deals synchronized.")

    print("\n--- Seeding Complete! ---")
    print("Blostem is now loaded with high-quality, professional Fintech/Banking data.")

if __name__ == "__main__":
    seed()
