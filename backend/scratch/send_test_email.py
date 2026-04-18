import os
import sys
from dotenv import load_dotenv

# Ensure we can import from backend
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.services.deals.outreach import send_email_smtp

def test_delivery():
    target = "shreyhiralkansara@gmail.com"
    subject = "[TEST] Blostem Intelligence: SMTP Connection Successful"
    body = "Greetings,\n\nThis is a diagnostic email from the Blostem Intelligence Platform to verify your SMTP relay. If you are reading this, your email engine is fully operational.\n\nBest,\nYour AI SDR"
    
    print(f"Attempting to send test email to {target}...")
    success = send_email_smtp(target, subject, body)
    
    if success:
        print("SUCCESS: Email dispatched.")
    else:
        print("FAILURE: Verify SMTP_USER and SMTP_PASS in .env. Note: Google requires an 'App Password', not your regular login password.")

if __name__ == "__main__":
    test_delivery()
