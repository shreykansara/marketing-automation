import logging
from datetime import datetime, timezone
from typing import Dict, Any
from data.db import deals_collection, outreach_sequences_collection

logger = logging.getLogger("feedback_loop")

VALID_OUTCOMES = ["pending", "opened", "replied", "ignored", "bounced"]

def process_interaction_feedback(deal_id: str, outcome: str, outreach_id: str = None) -> Dict[str, Any]:
    """
    FEEDBACK LOOP 2.0: Adaptive update.
    Updates deal state AND decision history in the deals collection.
    Standardized Outcomes: pending, opened, replied, ignored, bounced.
    """
    if outcome not in VALID_OUTCOMES:
        logger.warning(f"Invalid outcome: {outcome}. Defaulting to 'ignored'.")
        outcome = "ignored"

    now = datetime.now(timezone.utc).isoformat()
    
    # 1. Update the outreach sequence collection (existing collection)
    q = {"deal_id": deal_id}
    if outreach_id:
        q["id"] = outreach_id
    else:
        q["status"] = "pending_delivery"
        
    outreach_sequences_collection.update_many(
        q,
        {"$set": {"status": "completed", "outcome": outcome, "updated_at": now}}
    )
    
    # 2. Update Deal Decision History (Adaptive Layer)
    # We find the deal, find the history entry with status 'pending', and update it.
    # or if outreach_id is provided, match by that.
    
    dec_hist_q = {"id": deal_id}
    update_q = {}
    
    if outcome == "replied":
        # Reset unresponsive roles for evaluation
        update_q["$set"] = {
            "last_activity": now,
            "stakeholders.$[].responded": True
        }
    else:
        update_q["$set"] = {"last_activity": now}
        
    # Standardize the history update: find the entry in decision_history that matches and set its outcome
    # If no ID provided, we target the latest entry.
    
    # First, fetch the deal to find the right history entry index
    deal = deals_collection.find_one({"id": deal_id})
    if deal and "decision_history" in deal:
        history = deal["decision_history"]
        # Update the most recent 'pending' entry or the one matching outreach_id
        for i, entry in enumerate(reversed(history)):
            real_idx = len(history) - 1 - i
            if (outreach_id and entry.get("id") == outreach_id) or (not outreach_id and entry.get("outcome") == "pending"):
                history[real_idx]["outcome"] = outcome
                history[real_idx]["updated_at"] = now
                update_q["$set"]["decision_history"] = history
                break

    deals_collection.update_one({"id": deal_id}, update_q)
    
    logger.info(f"Feedback Loop: Outcome '{outcome}' processed for deal {deal_id}. History synchronized.")
    return {"status": "success", "processed_at": now}

def simulate_feedback_loop():
    """
    Refined Mock runner.
    """
    pending = list(outreach_sequences_collection.find({"status": "pending_delivery"}))
    for p in pending:
        import random
        r = random.random()
        if r > 0.8: outcome = "replied"
        elif r > 0.5: outcome = "opened"
        else: outcome = "ignored"
        
        process_interaction_feedback(p["deal_id"], outcome, p.get("id"))
