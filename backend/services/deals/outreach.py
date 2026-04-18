import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timezone
from bson import ObjectId
from backend.core.llm import llm_service
from backend.core.db import deals_collection, emails_collection

def generate_outreach_email(company: str, context: str):
    """
    (Placeholder) AI logic for email generation remains similar but uses the new schema.
    """
    # ... logic for prompt etc ...
    return {
        "subject": f"Follow-up: {company} context",
        "body": f"Hi team at {company},\n\nI noticed some interesting developments in your space and would love to connect.\n\nBest regards,\n[Your Name]"
    }

def send_email_smtp(to_email: str, subject: str, body: str):
    """
    Send email via SMTP using environment variables.
    """
    smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", 587))
    smtp_user = os.getenv("SMTP_USER")
    smtp_pass = os.getenv("SMTP_PASS")
    
    if not all([smtp_user, smtp_pass]):
        print("[ERROR] SMTP credentials missing in .env")
        return False
        
    try:
        msg = MIMEMultipart()
        msg['From'] = smtp_user
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        
        server = smtplib.SMTP(smtp_host, smtp_port)
        server.starttls()
        server.login(smtp_user, smtp_pass)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f"[ERROR] SMTP send failed: {e}")
        return False

def record_outreach(deal_id: str, to: str, subject: str, body: str):
    """
    Refactored Outreach Recorder: Saves to the 'emails' collection and updates Deal logs.
    """
    smtp_user = os.getenv("SMTP_USER", "unknown@sender")
    
    # 1. Create the Email document
    email_doc = {
        "sender": smtp_user,
        "receiver": to,
        "cc": [],
        "bcc": [],
        "subject": subject,
        "body": body,
        "timestamp": datetime.now(timezone.utc),
        "is_logged": True # We are logging it right now
    }
    
    result = emails_collection.insert_one(email_doc)
    email_id = result.inserted_id
    
    # 2. Update the Deal record
    deals_collection.update_one(
        {"_id": ObjectId(deal_id)},
        {
            "$push": {
                "emails": email_id,
                "logs": {
                    "timestamp": datetime.now(timezone.utc),
                    "type": "OUTREACH_SENT",
                    "message": f"Sent outreach email to {to}.",
                    "metadata": {"email_id": str(email_id), "subject": subject}
                }
            }
        }
    )
    
    return str(email_id)
