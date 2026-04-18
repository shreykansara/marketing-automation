import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timezone
from backend.core.llm import llm_service
from backend.core.db import deals_collection

def generate_outreach_email(company: str, context: str):
    try:
        result = llm_service.extract_structured(prompt, schema)
        if not result.get("subject") or not result.get("body"):
             raise ValueError("Incomplete AI response")
        return result
    except Exception as e:
        print(f"[LLM ERROR] {e}")
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
    Record sent email in the deal document.
    """
    from bson import ObjectId
    deals_collection.update_one(
        {"_id": ObjectId(deal_id)},
        {
            "$push": {"emails_sent": {
                "to": to,
                "subject": subject,
                "body": body,
                "timestamp": datetime.now(timezone.utc)
            }},
            "$set": {
                "status": "contacted",
                "last_contacted_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc)
            }
        }
    )
