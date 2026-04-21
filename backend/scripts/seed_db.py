from pymongo import MongoClient
from bson import ObjectId
import datetime
import hashlib
from dotenv import load_dotenv
import os

load_dotenv(os.path.join(os.path.dirname(__file__), '../../.env'))

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
client = MongoClient(MONGO_URI)
db = client.pipeline_db

def get_hash(text):
    return hashlib.sha256(text.encode()).hexdigest()

def seed():
    print("--- Clearing collections...")
    db.companies.delete_many({})
    db.signals.delete_many({})
    db.leads.delete_many({})
    db.deals.delete_many({})
    db.emails.delete_many({})
    db.logs.delete_many({})

    now = datetime.datetime.now()

    # ---------------- COMPANIES ----------------
    jupiter_id = ObjectId()
    federal_id = ObjectId()
    acme_id = ObjectId()
    razorpay_id = ObjectId()

    companies = [
        {"_id": jupiter_id, "name": "Jupiter", "emails": ["founder@jupiter.money"], "status": "deal", "flag": "active", "created_at": now - datetime.timedelta(days=3)},
        {"_id": federal_id, "name": "Federal Bank", "emails": ["outreach@federalbank.co.in"], "status": "deal", "flag": "active", "created_at": now - datetime.timedelta(days=7)},
        {"_id": acme_id, "name": "Acme Corp", "emails": ["contact@acme.com"], "status": "lead", "flag": "active", "created_at": now - datetime.timedelta(days=2)},
        {"_id": razorpay_id, "name": "Razorpay", "emails": ["partnerships@razorpay.com"], "status": "lead", "flag": "active", "created_at": now - datetime.timedelta(days=4)}
    ]
    db.companies.insert_many(companies)

    # ---------------- SIGNALS ----------------
    def create_signal(title, content, company_id, days_ago, score):
        return {
            "_id": ObjectId(),
            "title": title,
            "content": content,
            "source": "NewsAPI",
            "url": f"https://news.example.com/{get_hash(title)[:8]}",
            "company_ids": [company_id],
            "hash": get_hash(title),
            "relevance_score": score,
            "status": "enriched",
            "published_at": now - datetime.timedelta(days=days_ago),
            "created_at": now - datetime.timedelta(days=days_ago)
        }

    signals = [
    create_signal(
        "Jupiter expands fixed deposit offerings through new bank partnerships",
        "Jupiter, the Bengaluru-based neobank, has expanded its fixed deposit marketplace by onboarding multiple partner banks to offer higher-yield deposit products. The move is aimed at strengthening its position in the retail savings segment and improving customer retention through diversified FD options.",
        jupiter_id,
        2,
        92
    ),

    create_signal(
        "Federal Bank explores API-driven KYC infrastructure to streamline onboarding",
        "Federal Bank is reportedly evaluating API-based KYC and onboarding solutions to reduce friction in customer acquisition. The initiative is part of a broader digital transformation strategy focused on improving turnaround times and enabling seamless integration with fintech partners.",
        federal_id,
        5,
        85
    ),

    create_signal(
        "Razorpay begins pilot for deposit products targeting SME customers",
        "Razorpay has initiated a pilot program to offer fixed deposit-like financial products for its SME merchant base. The company is leveraging its existing payments infrastructure to cross-sell treasury and savings products, signaling a deeper move into the banking and deposits ecosystem.",
        razorpay_id,
        3,
        90
    ),

    create_signal(
        "Acme Corp explores fintech partnerships for internal financial tooling",
        "Acme Corp, a mid-sized logistics company, is exploring partnerships with fintech providers to improve its internal financial operations, including payments reconciliation and short-term treasury management. The initiative is still in early evaluation stages with no confirmed integrations.",
        acme_id,
        1,
        60
    ),
]
    db.signals.insert_many(signals)

    # ---------------- LEADS ----------------
    jupiter_lead_id = ObjectId()
    acme_lead_id = ObjectId()
    razorpay_lead_id = ObjectId()

    leads = [
        {"_id": jupiter_lead_id, "company_id": jupiter_id, "relevance_score": 90, "status": "active", "created_at": now - datetime.timedelta(hours=24), "updated_at": now},
        {"_id": acme_lead_id, "company_id": acme_id, "relevance_score": 60, "status": "active", "created_at": now - datetime.timedelta(hours=10), "updated_at": now},
        {"_id": razorpay_lead_id, "company_id": razorpay_id, "relevance_score": 88, "status": "active", "created_at": now - datetime.timedelta(hours=20), "updated_at": now}
    ]
    db.leads.insert_many(leads)

    # ---------------- EMAILS ----------------
    j1, j2, j3 = ObjectId(), ObjectId(), ObjectId()
    f1, f2, f3 = ObjectId(), ObjectId(), ObjectId()

    emails = [
        # Jupiter thread
        {
            "_id": j1,
            "sender": "blostem-sales@blostem.io",
            "receiver": "founder@jupiter.money",
            "subject": "Scaling Jupiter’s Fixed Deposit Infrastructure",
            "body": """Hi Team,

I came across Jupiter’s recent expansion into fixed deposit offerings and your broader push towards strengthening retail banking products.

At Blostem, we provide API-first infrastructure that enables fintech platforms to seamlessly integrate fixed deposit products, automate compliance workflows, and scale banking operations without heavy backend overhead.

Given your current trajectory, I believe there is a strong alignment in helping Jupiter accelerate its FD rollout while maintaining operational efficiency.

Would you be open to a quick discussion this week?

Best regards,
Blostem Team
""",
            "company_id": jupiter_id,
            "timestamp": now - datetime.timedelta(hours=10),
            "is_logged": True
        },
        {
            "_id": j2,
            "sender": "founder@jupiter.money",
            "receiver": "blostem-sales@blostem.io",
            "subject": "Re: Scaling Jupiter’s Fixed Deposit Infrastructure",
            "body": """Hi,

Thanks for reaching out and sharing the details.

We are currently evaluating multiple approaches to strengthen our deposit infrastructure and improve time-to-market for new financial products.

Your API-first model sounds interesting, particularly from a scalability standpoint.

Could you share more detailed documentation or possibly schedule a walkthrough?

Regards,
Jupiter Team
""",
            "company_id": jupiter_id,
            "timestamp": now - datetime.timedelta(hours=7),
            "is_logged": True
        },
        # ⚠️ Latest email NOT logged
        {
            "_id": j3,
            "sender": "blostem-sales@blostem.io",
            "receiver": "founder@jupiter.money",
            "subject": "Re: Scaling Jupiter’s Fixed Deposit Infrastructure",
            "body": """Hi,

Thanks for your response.

I’ve attached a detailed overview of our FD infrastructure APIs along with integration workflows and compliance modules.

We can also tailor the solution based on your internal architecture.

Let me know a suitable time and we can schedule a live demo.

Best,
Blostem Team
""",
            "company_id": jupiter_id,
            "timestamp": now - datetime.timedelta(hours=1),
            "is_logged": False
        },

        # Federal thread
        {
            "_id": f1,
            "sender": "outreach@federalbank.co.in",
            "receiver": "blostem-sales@blostem.io",
            "subject": "API-driven KYC & Deposit Infrastructure",
            "body": """Hello,

As part of our ongoing digital transformation initiatives, we are actively exploring solutions that can enhance our KYC workflows and modernize our deposit infrastructure.

We are particularly interested in API-driven architectures that can integrate with our existing systems while improving onboarding efficiency.

We would appreciate a detailed walkthrough of your platform.

Regards,
Federal Bank Team
""",
            "company_id": federal_id,
            "timestamp": now - datetime.timedelta(hours=20),
            "is_logged": True
        },
        {
            "_id": f2,
            "sender": "blostem-sales@blostem.io",
            "receiver": "outreach@federalbank.co.in",
            "subject": "Re: API-driven KYC & Deposit Infrastructure",
            "body": """Hi,

Thank you for reaching out.

Blostem provides modular APIs that support KYC orchestration, fixed deposit infrastructure, and seamless banking integrations.

Our solutions are designed to work alongside legacy systems while enabling modern digital experiences.

Happy to schedule a demo this week.

Best regards,
Blostem Team
""",
            "company_id": federal_id,
            "timestamp": now - datetime.timedelta(hours=18),
            "is_logged": True
        },
        {
            "_id": f3,
            "sender": "outreach@federalbank.co.in",
            "receiver": "blostem-sales@blostem.io",
            "subject": "Re: API-driven KYC & Deposit Infrastructure",
            "body": """Hi,

This aligns well with what we are looking for.

Let’s proceed with a demo. Please share available slots.

Regards,
Federal Bank
""",
            "company_id": federal_id,
            "timestamp": now - datetime.timedelta(hours=16),
            "is_logged": True
        }
    ]
    db.emails.insert_many(emails)

    # ---------------- DEALS ----------------
    federal_deal_id = ObjectId()
    jupiter_deal_id = ObjectId()

    deals = [
        {
            "_id": federal_deal_id,
            "company_id": federal_id,
            "lead_id": razorpay_lead_id,
            "intent_score": 91,
            "status": "open",
            "last_contacted_at": now - datetime.timedelta(hours=16)
        },
        {
            "_id": jupiter_deal_id,
            "company_id": jupiter_id,
            "lead_id": jupiter_lead_id,
            "intent_score": 89,
            "status": "contacted",
            "last_contacted_at": now - datetime.timedelta(hours=1)
        }
    ]
    db.deals.insert_many(deals)

    # ---------------- LOGS ----------------
    logs = [
        # Federal (deep logs)
        {"entity_id": f1, "timestamp": now - datetime.timedelta(hours=20), "type": "EMAIL", "message": "Inbound inquiry"},
        {"entity_id": federal_deal_id, "timestamp": now - datetime.timedelta(hours=19), "type": "SYSTEM", "message": "Lead evaluated"},
        {"entity_id": federal_deal_id, "timestamp": now - datetime.timedelta(hours=18), "type": "SYSTEM", "message": "Converted to deal"},
        {"entity_id": f2, "timestamp": now - datetime.timedelta(hours=18), "type": "EMAIL", "message": "Response sent"},
        {"entity_id": f3, "timestamp": now - datetime.timedelta(hours=16), "type": "EMAIL", "message": "Demo requested"},
        {"entity_id": federal_deal_id, "timestamp": now - datetime.timedelta(hours=15), "type": "MANUAL", "message": "Demo scheduled"},
        {"entity_id": federal_deal_id, "timestamp": now - datetime.timedelta(hours=12), "type": "SYSTEM", "message": "Intent score updated"},
        {"entity_id": federal_deal_id, "timestamp": now - datetime.timedelta(hours=10), "type": "SYSTEM", "message": "Moved to negotiation"},

        # Jupiter deal logs
        {"entity_id": j1, "timestamp": now - datetime.timedelta(hours=10), "type": "EMAIL", "message": "Outbound email sent"},
        {"entity_id": j2, "timestamp": now - datetime.timedelta(hours=7), "type": "EMAIL", "message": "Reply received"},
        {"entity_id": jupiter_deal_id, "timestamp": now - datetime.timedelta(hours=6), "type": "SYSTEM", "message": "Converted to deal"},
        {"entity_id": jupiter_deal_id, "timestamp": now - datetime.timedelta(hours=2), "type": "MANUAL", "message": "Follow-up prepared"}
        # ⚠️ No log for latest email (j3)
    ]
    db.logs.insert_many(logs)

    print("--- Seeding complete!")

if __name__ == "__main__":
    seed()