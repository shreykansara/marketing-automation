import sys
import os
import asyncio
from datetime import datetime, timezone
from bson import ObjectId

# Add project root to sys.path
sys.path.append(os.getcwd())

from backend.routes.emails import confirm_email_log

async def main():
    email_id = "69e470e1bcec5a0966157a40"
    message = "Test diagnostic log message"
    
    print(f"Testing confirm_email_log with email_id: {email_id}")
    
    try:
        # We manually call it. Since it's an async function, we await it.
        # Note: In FastAPI, the 'message' argument is usually extracted from the Body.
        # Here we just pass it directly.
        result = await confirm_email_log(email_id, message)
        print(f"Result: {result}")
    except Exception as e:
        import traceback
        print(f"Caught Exception: {type(e).__name__}: {str(e)}")
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
