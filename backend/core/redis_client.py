import json
from typing import Any

import redis

from core.config import get_settings


_client: redis.Redis | None = None


def get_redis_client() -> redis.Redis | None:
    global _client
    if _client is not None:
        return _client

    try:
        _client = redis.Redis.from_url(get_settings().redis_url, decode_responses=True)
        _client.ping()
        return _client
    except Exception:
        _client = None
        return None


def publish(channel: str, payload: dict[str, Any]) -> None:
    client = get_redis_client()
    if client is None:
        return
    try:
        client.publish(channel, json.dumps(payload, default=str))
    except Exception:
        return


def get_cached_json(key: str) -> Any | None:
    client = get_redis_client()
    if client is None:
        return None
    try:
        value = client.get(key)
        return json.loads(value) if value else None
    except Exception:
        return None


def set_cached_json(key: str, value: Any, ttl_seconds: int = 3600) -> None:
    client = get_redis_client()
    if client is None:
        return
    try:
        client.setex(key, ttl_seconds, json.dumps(value))
    except Exception:
        return
