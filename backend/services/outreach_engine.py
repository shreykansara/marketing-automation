import uuid
from datetime import datetime, timezone
import logging
from typing import Dict, Any, List
from data.db import outreach_sequences_collection, deals_collection

logger = logging.getLogger("outreach_engine")

# Base templates mapped by action intent
TEMPLATES = {
    "re_engagement": "Noticed we haven't heard back on the {trigger}. Is there anything specific we can resolve for your team?",
    "nurture": "Thinking about your {trigger} milestone. Thought you'd find this relevant to your GTM strategy.",
    "manual_intervention": "Internal alert regarding {company} expansion. Immediate stakeholder alignment required."
}

def execute_outreach_generation(deal: Dict[str, Any], activation_context: Dict[str, Any]) -> Dict[str, Any]:
    """
    OUTREACH EXECUTION LAYER 2.0: History-Aware execution.
    Appends to decision_history and generates messaging.
    """
    company = deal.get("company")
    deal_id = deal.get("id")
    intent = activation_context.get("intent")
    target_role = activation_context.get("target_role")
    channel = activation_context.get("channel")
    
    # 1. Calculate attempt number from history
    history = deal.get("decision_history", [])
    attempt_number = len([e for e in history if e.get("intent") == intent]) + 1
    
    # 2. Identify Trigger from Signals
    signals = deal.get("signals", [])
    best_signal = signals[0] if signals else {}
    trigger = best_signal.get("signal_type", "market activity")
    
    # 3. Select and Fill Template
    template = TEMPLATES.get(intent, "Following up regarding your latest activity.")
    message = template.format(trigger=trigger, company=company)
    
    # 4. Build 2-Step Sequence
    sequence_id = str(uuid.uuid4())
    sequence = [
        {"day": 0, "type": channel, "message": message},
        {"day": 2, "type": "follow_up", "message": "Quick check-in on the previous note — any updates on your side?"}
    ]
    
    outreach_doc = {
        "id": sequence_id,
        "company": company,
        "deal_id": deal_id,
        "target_persona": target_role,
        "intent": intent,
        "channel": channel,
        "sequence": sequence,
        "status": "pending_delivery",
        "attempt_number": attempt_number,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    # 5. Persistent Decision History (The Memory)
    history_entry = {
        "id": sequence_id,
        "action": "trigger_outreach",
        "intent": intent,
        "target_role": target_role,
        "attempt_number": attempt_number,
        "timestamp": outreach_doc["created_at"],
        "outcome": "pending",
        "reason": activation_context.get("reason", "manual_trigger")
    }
    
    # Atomically update the deal with the new history entry
    deals_collection.update_one(
        {"id": deal_id},
        {"$push": {"decision_history": history_entry}}
    )
    
    # 6. Store outreach sequence doc
    outreach_sequences_collection.replace_one(
        {"deal_id": deal_id, "intent": intent},
        outreach_doc,
        upsert=True
    )
    
    logger.info(f"Generated outreach attempt #{attempt_number} for {company} (Intent: {intent})")
    
    return outreach_doc
