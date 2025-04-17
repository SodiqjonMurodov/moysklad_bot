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


async def get_demands_by_counterparty(counterparty_id: str):
    url = f"{BASE_URL}/entity/demand"

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=HEADERS)

    if response.status_code == 200:
        data = response.json()
        rows = data.get("rows", [])
        filtered_rows = []

        for row in rows:
            if row["agent"]["meta"]["href"] == f"{BASE_URL}/entity/counterparty/{counterparty_id}" and row["applicable"] == True:
                filtered_rows.append(row)
        return filtered_rows
    return None


async def get_positions_from_demand(doc_id):
    url = f"{BASE_URL}/entity/demand/{doc_id}/positions"

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=HEADERS)

    if response.status_code == 200:
        data = response.json()
        rows = data.get("rows", [])
        return rows
    return []
