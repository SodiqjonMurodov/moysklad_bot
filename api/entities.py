import os
import httpx
import asyncio
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


async def publish_document_with_template(doc_type: str, doc_id: str, template_id: str, extension: str = "pdf"):
    url = f"{BASE_URL}/entity/{doc_type}/{doc_id}/publication"

    payload = {
        "template": {
            "meta": {
                "href": f"{BASE_URL}/entity/{doc_type}/metadata/customtemplate/{template_id}",
                "type": "customtemplate",
                "mediaType": "application/json"
            }
        },
        "extension": extension
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=HEADERS, json=payload)

    if response.status_code == 200:
        data = response.json()
        return data
    else:
        print(f"⚠️ Error: {response.status_code} - {response.text}")
        return None

