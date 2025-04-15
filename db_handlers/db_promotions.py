import json
from pathlib import Path

PROMOTIONS_PATH = Path("storage/promotions.json")


def load_active_promotions() -> list[dict]:
    if not PROMOTIONS_PATH.exists():
        return []

    with open(PROMOTIONS_PATH, "r") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            return []

    return [
        promo for promo in data.values()
        if promo.get("active") is True
    ]

