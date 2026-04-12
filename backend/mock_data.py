import datetime

# Mock data simulating a pipeline
def get_current_time():
    return datetime.datetime.now(datetime.timezone.utc)

deals = [
    {
        "id": "D1001",
        "company": "Acme Corp",
        "stage": "Lead",
        "status": "Active",
        "last_activity": (get_current_time() - datetime.timedelta(days=2)).isoformat(),
        "value": 50000,
        "stakeholders": [
            {"role": "CTO", "name": "Alice Smith", "contacted": True, "responded": True, "intent_score": 85},
            {"role": "Business Head", "name": "Bob Jones", "contacted": False, "responded": False, "intent_score": 50}
        ]
    },
    {
        "id": "D1002",
        "company": "Globex Inc",
        "stage": "Negotiation",
        "status": "Active",
        "last_activity": (get_current_time() - datetime.timedelta(days=15)).isoformat(),
        "value": 120000,
        "stakeholders": [
            {"role": "Compliance Officer", "name": "Charlie Brown", "contacted": True, "responded": False, "intent_score": 40},
            {"role": "VP Engineering", "name": "Dana White", "contacted": True, "responded": True, "intent_score": 90}
        ]
    },
    {
        "id": "D1003",
        "company": "Initech",
        "stage": "Signed",
        "status": "Active",
        "last_activity": (get_current_time() - datetime.timedelta(days=1)).isoformat(),
        "value": 200000,
        "stakeholders": [
            {"role": "CTO", "name": "Eve Davis", "contacted": True, "responded": True, "intent_score": 95},
            {"role": "Integration Manager", "name": "Frank Evans", "contacted": False, "responded": False, "intent_score": 80}
        ]
    },
    {
        "id": "D1004",
        "company": "Soylent Corp",
        "stage": "Activation",
        "status": "Active",
        "last_activity": (get_current_time() - datetime.timedelta(days=8)).isoformat(),
        "value": 75000,
        "stakeholders": [
            {"role": "Tech Lead", "name": "Grace Hopper", "contacted": True, "responded": False, "intent_score": 70}
        ]
    },
    {
        "id": "D1005",
        "company": "Massive Dynamic",
        "stage": "Live",
        "status": "Active",
        "last_activity": (get_current_time() - datetime.timedelta(days=3)).isoformat(),
        "value": 300000,
        "stakeholders": [
            {"role": "Product Owner", "name": "Hank Pym", "contacted": True, "responded": True, "intent_score": 100}
        ]
    }
]

templates = {
    "CTO": "Hi {name}, wanted to share technical specs for our integration to unblock your team.",
    "Compliance Officer": "Hello {name}, attaching our SOC2 report and compliance checklist for your review.",
    "Business Head": "Hi {name}, following up to ensure our commercial terms align with your goals.",
    "Integration Manager": "Hi {name}, ready to kick off the integration. Here is the sandbox access."
}
