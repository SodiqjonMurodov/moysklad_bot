import json

from datetime import datetime
from pathlib import Path

DB_PATH = Path("storage/auth_users.json")
DB_PATH.parent.mkdir(parents=True, exist_ok=True)


def load_users() -> dict:
    if not DB_PATH.exists():
        with open(DB_PATH, "w") as f:
            json.dump({}, f)

    with open(DB_PATH, "r") as f:
        return json.load(f)


def save_users(data: dict):
    with open(DB_PATH, "w") as f:
        json.dump(data, f, indent=4)


def is_user_authenticated(chat_id: int) -> bool:
    users = load_users()
    return str(chat_id) in users


def set_user_authenticated(chat_id: int, user_data: dict):
    now = datetime.now().isoformat()
    users = load_users()

    if str(chat_id) in users:
        user_data["created_at"] = users[str(chat_id)].get("created_at", now)
    else:
        user_data["created_at"] = now

    user_data["updated_at"] = now
    users[str(chat_id)] = user_data
    save_users(users)


def get_user_data(chat_id: int) -> dict:
    users = load_users()
    return users.get(str(chat_id), {})
