import imaplib
import email
import os
from datetime import datetime, timezone
from bson import ObjectId
from backend.core.db import deals_collection, emails_collection
from backend.core.llm import llm_service
from backend.core.logger import get_logger

logger = get_logger("services.tracker")

def fetch_incoming_emails():
    """
    Connected IMAP Refactor (v2): Saves replies to 'emails' and logs them to Deals.
    """
    imap_host = os.getenv("IMAP_HOST", "imap.gmail.com")
    username = os.getenv("SMTP_USER")
    password = os.getenv("SMTP_PASS")

    if not all([username, password]):
        logger.error("IMAP credentials missing in .env")
        return []

    try:
        mail = imaplib.IMAP4_SSL(imap_host)
        mail.login(username, password)
        mail.select("inbox")

        # Fetch UNSEEN emails
        status, response = mail.search(None, '(UNSEEN)')
        
        new_replies = []
        for num in response[0].split():
            status, data = mail.fetch(num, '(RFC822)')
            msg = email.message_from_bytes(data[0][1])
            
            from_email = email.utils.parseaddr(msg['From'])[1].lower()
            to_email = username.lower()
            subject = msg['Subject']
            
            # Extract body
            body = ""
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == "text/plain":
                        payload = part.get_payload(decode=True)
                        if payload:
                            body = payload.decode()
                        break
            else:
                payload = msg.get_payload(decode=True)
                if payload:
                    body = payload.decode()

            # 1. Save to master 'emails' collection first
            email_doc = {
                "sender": from_email,
                "receiver": to_email,
                "cc": [],
                "bcc": [],
                "subject": subject,
                "body": body,
                "timestamp": datetime.now(timezone.utc),
                "is_logged": False # To be updated once matched
            }
            insert_result = emails_collection.insert_one(email_doc)
            email_id = insert_result.inserted_id

            # 2. Match to a deal
            # Logic: Find a deal where we previously sent an email TO this sender.
            # We search for an email in 'emails' where sender=username and receiver=from_email,
            # then find the deal that includes that email ID.
            
            prev_outreach = emails_collection.find_one({
                "sender": username.lower(),
                "receiver": from_email
            })
            
            if prev_outreach:
                matching_deal = deals_collection.find_one({"emails": prev_outreach["_id"]})
                
                if matching_deal:
                    logger.info(f"Matched reply from {from_email} to deal {matching_deal['company']}")
                    
                    # Sentiment analysis for status suggestion (still used for logs)
                    analysis = llm_service.analyze_deal_status(body, "open") # Defaulting current status as it's derived
                    
                    # 3. Update the Deal record
                    deals_collection.update_one(
                        {"_id": matching_deal["_id"]},
                        {
                            "$push": {
                                "emails": email_id,
                                "logs": {
                                    "timestamp": datetime.now(timezone.utc),
                                    "type": "REPLY_RECEIVED",
                                    "message": f"Received reply from {from_email}. AI Suggestion: {analysis.get('suggested_status')}",
                                    "metadata": {
                                        "email_id": str(email_id),
                                        "suggested_status": analysis.get("suggested_status"),
                                        "reason": analysis.get("reason")
                                    }
                                }
                            }
                        }
                    )
                    
                    # Mark email as successfully logged
                    emails_collection.update_one({"_id": email_id}, {"$set": {"is_logged": True}})
                    new_replies.append(matching_deal["company"])

        mail.logout()
        return new_replies

    except Exception as e:
        logger.error(f"IMAP sync failed: {e}")
        return []
