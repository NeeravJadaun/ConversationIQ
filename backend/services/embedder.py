from __future__ import annotations

import hashlib
import random

from core.redis_client import get_cached_json, set_cached_json

_model = None


def _customer_text(conversation: dict) -> str:
    return " ".join(turn["text"] for turn in conversation.get("turns", []) if turn.get("role") == "customer")


def _deterministic_embedding(text: str) -> list[float]:
    seed = int(hashlib.sha256(text.encode("utf-8")).hexdigest()[:16], 16)
    rng = random.Random(seed)
    return [rng.uniform(-1, 1) for _ in range(384)]


def _get_model():
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer

        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model


def embed_conversation(conversation: dict) -> list[float]:
    cache_key = f"embed:{conversation.get('conversation_id') or conversation.get('id')}"
    cached = get_cached_json(cache_key)
    if cached:
        return cached
    text = _customer_text(conversation)
    try:
        embedding = _get_model().encode(text).astype(float).tolist()
    except Exception:
        embedding = _deterministic_embedding(text)
    set_cached_json(cache_key, embedding)
    return embedding


def embed_batch(conversations: list[dict]) -> list[list[float]]:
    try:
        texts = [_customer_text(conversation) for conversation in conversations]
        return _get_model().encode(texts).astype(float).tolist()
    except Exception:
        return [embed_conversation(conversation) for conversation in conversations]
