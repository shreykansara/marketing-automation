import asyncio
import os
import httpx
from dotenv import load_dotenv

# Path to .env
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
env_path = os.path.join(base_dir, ".env")
load_dotenv(env_path)

async def test():
    api_key = os.getenv("NEWS_API_KEY")
    if api_key:
        api_key = api_key.replace("-", "").strip()
    
    print(f"API KEY: {api_key}")
    
    url = "https://newsapi.org/v2/everything"
    params = {
        "q": "Fintech India",
        "apiKey": api_key,
        "pageSize": 5,
        "sortBy": "publishedAt",
        "language": "en"
    }
    
    async with httpx.AsyncClient() as client:
        res = await client.get(url, params=params)
        print(f"Status: {res.status_code}")
        print(f"Body: {res.text}")

if __name__ == "__main__":
    asyncio.run(test())
