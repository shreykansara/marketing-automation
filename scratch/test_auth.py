import httpx
import sys

BASE_URL = "http://127.0.0.1:8000/api/auth"

def test_auth():
    print("--- Starting Auth Verification ---")
    
    # 1. Test Login
    print("\n[1] Testing Login...")
    login_data = {
        "username": "test.automation@blostem.ai",
        "password": "blostem2026"
    }
    
    try:
        with httpx.Client(timeout=60.0) as client:
            # OAuth2PasswordRequestForm uses form data
            response = client.post(f"{BASE_URL}/login", data=login_data)
            
            if response.status_code == 200:
                print("[SUCCESS] Login Successful!")
                token_data = response.json()
                access_token = token_data["access_token"]
                print(f"Token received (truncated): {access_token[:20]}...")
            else:
                print(f"[FAIL] Login Failed: {response.status_code}")
                print(response.text)
                return

            # 2. Test /me endpoint (Protected)
            print("\n[2] Testing Protected /me endpoint...")
            headers = {"Authorization": f"Bearer {access_token}"}
            response = client.get(f"{BASE_URL}/me", headers=headers)
            
            if response.status_code == 200:
                user_data = response.json()
                print(f"[SUCCESS] Protected Access Successful!")
                print(f"User retrieved: {user_data.get('email')} ({user_data.get('full_name')})")
            else:
                print(f"[FAIL] Protected Access Failed: {response.status_code}")
                print(response.text)
                
            # 3. Test Registration (Invalid/Used Code)
            print("\n[3] Testing Registration with invalid invite code...")
            reg_data = {
                "email": "another@blostem.ai",
                "password": "password123",
                "full_name": "Another User",
                "invite_code": "INVALID-CODE"
            }
            response = client.post(f"{BASE_URL}/register", json=reg_data)
            if response.status_code == 400:
                print("[SUCCESS] Registration correctly rejected invalid code (400 Bad Request)")
            else:
                print(f"[FAIL] Registration behavior unexpected: {response.status_code}")

    except Exception as e:
        print(f"[ERROR] Error during verification: {str(e)}")

if __name__ == "__main__":
    test_auth()
