from __future__ import annotations

import hashlib
import random

from core.redis_client import get_cached_json, set_cached_json

_model = None
_model_unavailable = False


def _customer_text(conversation: dict) -> str:
    return " ".join(turn["text"] for turn in conversation.get("turns", []) if turn.get("role") == "customer")


def _deterministic_embedding(text: str) -> list[float]:
    seed = int(hashlib.sha256(text.encode("utf-8")).hexdigest()[:16], 16)
    rng = random.Random(seed)
    return [rng.uniform(-1, 1) for _ in range(384)]


def _get_model():
    global _model, _model_unavailable
    if _model_unavailable:
        return None
    if _model is None:
        try:
            from sentence_transformers import SentenceTransformer

            _model = SentenceTransformer("all-MiniLM-L6-v2")
        except Exception:
            _model_unavailable = True
            return None
    return _model


def embed_conversation(conversation: dict) -> list[float]:
    cache_key = f"embed:{conversation.get('conversation_id') or conversation.get('id')}"
    cached = get_cached_json(cache_key)
    if cached:
        return cached
    text = _customer_text(conversation)
    model = _get_model()
    if model is None:
        embedding = _deterministic_embedding(text)
    else:
        try:
            embedding = model.encode(text).astype(float).tolist()
        except Exception:
            embedding = _deterministic_embedding(text)
    set_cached_json(cache_key, embedding)
    return embedding


def embed_batch(conversations: list[dict]) -> list[list[float]]:
    try:
        model = _get_model()
        if model is None:
            return [embed_conversation(conversation) for conversation in conversations]
        texts = [_customer_text(conversation) for conversation in conversations]
        return model.encode(texts).astype(float).tolist()
    except Exception:
        return [embed_conversation(conversation) for conversation in conversations]
