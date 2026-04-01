import json
from bot.clients import redis
from bot.config import MAX_HISTORY


def get_history(user_id: int) -> list:
    try:
        data = redis.get(f"chat:{user_id}")
        return json.loads(data) if data else []
    except Exception:
        return []


def save_history(user_id: int, history: list) -> None:
    try:
        redis.set(f"chat:{user_id}", json.dumps(history[-MAX_HISTORY:]))
    except Exception:
        pass


def clear_history(user_id: int) -> None:
    try:
        redis.delete(f"chat:{user_id}")
    except Exception:
        pass
