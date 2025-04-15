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


async def check_counterparty_by_phone(phone: str) -> dict | None:
    url = f"{BASE_URL}/entity/counterparty"
    params = {
        "filter": f"phone={phone}"
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=HEADERS, params=params)

    if response.status_code == 200:
        data = response.json()
        rows = data.get("rows", [])
        if rows:
            return rows[0]  # Birinchi topilgan kontragentni qaytaradi
    return None


async def add_counterparty_to_group(counterparty: dict, tag_name: str):
    url = f"{BASE_URL}/entity/counterparty/{counterparty['id']}"
    existing_tags = counterparty.get("tags", [])
    updated_tags = existing_tags + [tag_name] if tag_name not in existing_tags else existing_tags

    data = {
        "tags": updated_tags
    }

    async with httpx.AsyncClient() as client:
        response = await client.put(url, json=data, headers=HEADERS)

    return response.json()


async def create_counterparty(phone: str, name: str):
    url = f"{BASE_URL}/entity/counterparty"
    data = {
        "name": name,
        "phone": phone,
        "tags": ["telebot"]
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=HEADERS, json=data)

    if response.status_code not in [200, 201]:
        print(f"Yaratishda xatolik: {response.status_code} - {response.text}")
        return None

    return response.json()


async def get_balance_counterparty(counterparty_id: str):
    url = f"{BASE_URL}/report/counterparty/{counterparty_id}"

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=HEADERS)

    if response.status_code == 200:
        return response.json()
    return None



