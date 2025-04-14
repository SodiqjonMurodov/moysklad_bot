import json
from datetime import datetime
from pathlib import Path
import aiofiles

DB_PATH = Path("storage/auth_users.json")
DB_PATH.parent.mkdir(parents=True, exist_ok=True)


async def load_users() -> dict:
    if not DB_PATH.exists():
        async with aiofiles.open(DB_PATH, "w") as f:
            await f.write(json.dumps({}))

    async with aiofiles.open(DB_PATH, "r") as f:
        content = await f.read()
        return json.loads(content or "{}")


async def save_users(data: dict):
    async with aiofiles.open(DB_PATH, "w") as f:
        await f.write(json.dumps(data, indent=4))


async def is_user_authenticated(chat_id: int) -> bool:
    users = await load_users()
    return str(chat_id) in users


async def set_user_authenticated(chat_id: int, user_data: dict):
    now = datetime.now().isoformat()
    users = await load_users()

    if str(chat_id) in users:
        user_data["created_at"] = users[str(chat_id)].get("created_at", now)
    else:
        user_data["created_at"] = now

    user_data["updated_at"] = now
    users[str(chat_id)] = user_data
    await save_users(users)


async def get_user_data(chat_id: int) -> dict:
    users = await load_users()
    return users.get(str(chat_id), {})
