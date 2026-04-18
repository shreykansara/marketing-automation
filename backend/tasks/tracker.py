from backend.core.celery_app import celery_app
from backend.services.deals.tracker import fetch_incoming_emails
from backend.core.logger import get_logger

logger = get_logger("tasks.tracker")

@celery_app.task(name="poll_deal_replies_task")
def poll_deal_replies_task():
    """
    Periodic task to check for new email replies and suggest status updates.
    """
    logger.info("Starting periodic IMAP sync...")
    updated_deals = fetch_incoming_emails()
    if updated_deals:
        logger.info(f"Successfully processed replies for: {', '.join(updated_deals)}")
    else:
        logger.info("No new replies detected.")
    return len(updated_deals)
