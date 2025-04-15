import json
from pathlib import Path

NEWS_PATH = Path("storage/news.json")


def load_news() -> list[dict]:
    if not NEWS_PATH.exists():
        return []

    with open(NEWS_PATH, "r") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            return []

    return [new for new in data.values()]

