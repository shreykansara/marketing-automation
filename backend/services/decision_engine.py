import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List

logger = logging.getLogger("decision_engine")

def compute_decision(deal: Dict[str, Any], evaluation_packet: Dict[str, Any]) -> Dict[str, Any]:
    """
    ADAPTIVE BRAIN 2.0: History-Aware Decisioning.
    Consumes: State Assessment + Decision History.
    Produces: Adaptive Decision with Reasons and Escalation Targets.
    """
    health = evaluation_packet.get("status", "Active")
    urgency = evaluation_packet.get("urgency_score", 0)
    risk_reason = evaluation_packet.get("risk_reason", "")
    history = deal.get("decision_history", [])
    
    # Defaults
    decision = "no_action"
    intent = None
    priority = "Low"
    reason = "monitoring_default"
    escalate_to = None

    # --- 1. SUCCESS AWARENESS (Global check) ---
    # If any outreach was replied to in the last 7 days, suppress all automation
    recent_replies = [e for e in history if e.get("outcome") == "replied"]
    if recent_replies:
        latest_reply_ts = datetime.fromisoformat(recent_replies[-1]["timestamp"])
        if (datetime.now(timezone.utc) - latest_reply_ts).days < 7:
            return {
                "decision": "no_action",
                "action_intent": None,
                "priority": "Low",
                "reason": "recent_engagement_detected",
                "reasoning": "Engagement detected within the last 7 days. Manual handling preferred."
            }

    # --- 2. INTENT DETERMINATION ---
    # Determine the primary intent we WANT to act on based on state
    if health == "Stalled" and urgency >= 70:
        intent = "re_engagement"
        priority = "High"
    elif health == "At Risk":
        intent = "manual_intervention"
        priority = "Medium"
    elif health == "Active" and urgency >= 80:
        intent = "nurture"
        priority = "High"
    elif health == "Stalled":
        intent = "re_engagement"
        priority = "Low"
    
    if not intent:
         return {
            "decision": "no_action",
            "action_intent": None,
            "priority": "Low",
            "reason": "state_stable",
            "reasoning": f"Deal is {health} with urgency {urgency}. No trigger conditions met."
        }

    # --- 3. ADAPTIVE RULES (PER INTENT) ---
    intent_history = [e for e in history if e.get("intent") == intent]
    
    # A. Intent-Aware Cooldown (72 Hours)
    if intent_history:
        last_attempt_ts = datetime.fromisoformat(intent_history[-1]["timestamp"])
        if (datetime.now(timezone.utc) - last_attempt_ts) < timedelta(hours=72):
            return {
                "decision": "delay_action",
                "action_intent": intent,
                "priority": "Low",
                "reason": "cooldown_active",
                "reasoning": f"Outreach for '{intent}' was attempted within the last 72 hours. Suppression active."
            }
            
    # B. Failure-Based Escalation (2+ Ignored)
    ignored_count = len([e for e in intent_history if e.get("outcome") == "ignored"])
    if ignored_count >= 2:
        return {
            "decision": "escalate",
            "action_intent": intent,
            "priority": "High",
            "reason": "failure_threshold_reached",
            "escalate_to": "senior_sales",
            "reasoning": f"{ignored_count} ignored attempts for '{intent}' intent. Pivoting to senior sales lead."
        }

    # C. Stalled Deadlock Detection (10+ days since activity, no outreach in 5 days)
    days_stalled = evaluation_packet.get("days_since_activity", 0)
    last_any_outreach = datetime.fromisoformat(history[-1]["timestamp"]) if history else datetime.min.replace(tzinfo=timezone.utc)
    
    if health == "Stalled" and days_stalled >= 10:
        if (datetime.now(timezone.utc) - last_any_outreach) > timedelta(days=5):
            return {
                "decision": "escalate",
                "action_intent": intent,
                "priority": "High",
                "reason": "stalled_deadlock_detected",
                "escalate_to": "manual_queue",
                "reasoning": f"Deal stalled for {days_stalled} days with no recent engagement attempts. Manual intervention required."
            }

    # --- 4. DEFAULT EXECUTION (If no rules suppressed/escalated) ---
    logger.info(f"Decision Engine for {deal.get('company')}: Triggering {intent}")
    
    return {
        "decision": "trigger_outreach",
        "action_intent": intent,
        "priority": priority,
        "reason": "trigger_condition_met",
        "reasoning": f"Deal is {health} with urgency {urgency}. Initiating '{intent}' outreach."
    }
