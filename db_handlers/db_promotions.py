import json
from pathlib import Path

PROMOTIONS_PATH = Path("storage/promotions.json")


async def load_promotions(is_active=True) -> list[dict]:
    if not PROMOTIONS_PATH.exists():
        return []

    with open(PROMOTIONS_PATH, "r") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            return []

    if is_active:
        return [promo for promo in data.values() if promo.get("active") is True]
    else:
        return data

async def get_promotion():
    promos = load_promotions(is_active=False)



