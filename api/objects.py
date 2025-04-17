import os
import httpx
from dotenv import load_dotenv

load_dotenv()

API_TOKEN = os.getenv("MOYSKLAD_TOKEN")
BASE_URL = os.getenv("BASE_URL")

HEADERS = {
    "Authorization": f"Bearer {API_TOKEN}",
    "Accept-Encoding": "gzip",
    "Content-Type": "application/json"
}


async def get_object_by_url(url):
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=HEADERS)

    if response.status_code == 200:
        data = response.json()
        return dict(data)
    return None


