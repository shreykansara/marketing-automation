from backend.core.db import emails_collection, companies
from bson import ObjectId

def debug_emails():
    print("--- Debugging Emails with is_logged=False ---")
    emails = list(emails_collection.find({"is_logged": False}))
    print(f"Found {len(emails)} emails with is_logged=False\n")
    
    for email in emails:
        email_id = str(email["_id"])
        subject = email.get("subject", "No Subject")
        company_id = email.get("company_id")
        
        print(f"Email ID: {email_id}")
        print(f"Subject: {subject}")
        print(f"Company ID: {company_id}")
        
        if company_id:
            company = companies.find_one({"_id": ObjectId(company_id)})
            if company:
                status = company.get("status")
                print(f"Linked Company: {company.get('name')}")
                print(f"Company Status: {status}")
                
                is_loggable = False
                if status in ["lead", "deal"]:
                    is_loggable = True
                print(f"Is Loggable (Logic): {is_loggable}")
            else:
                print("Linked Company NOT FOUND in database.")
        else:
            print("No Company ID linked to this email.")
        print("-" * 40)

if __name__ == "__main__":
    debug_emails()
