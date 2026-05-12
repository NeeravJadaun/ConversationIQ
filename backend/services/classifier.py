import json

from openai import OpenAI

from core.config import get_settings
from services.simulator import OPERATING_PROCEDURES


def _text(conversation: dict) -> str:
    return " ".join(turn["text"].lower() for turn in conversation.get("turns", []))


def mock_classify_conversation(conversation: dict) -> dict:
    text = _text(conversation)
    op = OPERATING_PROCEDURES.get(conversation.get("op_id"), {})
    intent = conversation.get("intent_detected") or "unknown customer request"
    gap_hit = next((phrase for phrase in op.get("gap_intents", []) if phrase in text or phrase == intent), None)
    happy_hit = next((phrase for phrase in op.get("happy_path_intents", []) if phrase in text or phrase == intent), None)
    failed_status = conversation.get("resolution_status") in {"failed", "escalated", "looped"}
    handled = bool(happy_hit) and not failed_status and not gap_hit
    return {
        "intent_detected": gap_hit or happy_hit or intent,
        "op_handled_correctly": handled,
        "failure_reason": None if handled else "missing intent path" if gap_hit else "procedure did not resolve customer request",
        "suggested_intent_label": (gap_hit or happy_hit or intent).lower(),
    }


def classify_conversation(conversation: dict) -> dict:
    settings = get_settings()
    if not settings.openai_api_key:
        return mock_classify_conversation(conversation)

    client = OpenAI(api_key=settings.openai_api_key)
    prompt = {
        "conversation": conversation,
        "schema": {
            "intent_detected": "string",
            "op_handled_correctly": "boolean",
            "failure_reason": "string|null",
            "suggested_intent_label": "string",
        },
    }
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "You are a quality analyst for a banking AI assistant. Analyze this conversation and determine: (1) what the customer's core intent was, (2) whether the AI agent handled it correctly according to standard banking procedures, (3) if it failed, the precise reason why. Return only valid JSON matching the schema provided.",
            },
            {"role": "user", "content": json.dumps(prompt, default=str)},
        ],
        response_format={"type": "json_object"},
    )
    return json.loads(response.choices[0].message.content or "{}")
