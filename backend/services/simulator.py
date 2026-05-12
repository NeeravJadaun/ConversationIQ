from __future__ import annotations

import random
import uuid
from datetime import datetime, timedelta, timezone


OPERATING_PROCEDURES: dict[str, dict] = {
    "OP-01": {
        "name": "Card Lock / Freeze",
        "description": "Locks or freezes active debit and credit cards.",
        "happy_path_intents": ["lock my card", "freeze my card", "block my card", "card stolen", "disable my card"],
        "gap_intents": ["temporarily freeze", "pause my card", "put my card on hold", "suspend card access", "deactivate card for travel"],
        "resolution_rate_target": 0.28,
        "avg_sentiment_drop": 0.65,
    },
    "OP-02": {
        "name": "Password Reset",
        "description": "Resets digital banking credentials after identity verification.",
        "happy_path_intents": ["reset my password", "forgot my password", "can't log in", "change online banking password"],
        "gap_intents": ["reset password without phone", "locked out overseas"],
        "resolution_rate_target": 0.9,
        "avg_sentiment_drop": 0.2,
    },
    "OP-03": {
        "name": "Balance Inquiry",
        "description": "Provides account balance and available funds information.",
        "happy_path_intents": ["check my balance", "available balance", "how much money is in checking", "account balance"],
        "gap_intents": ["pending balance after hotel hold", "available balance before settlement"],
        "resolution_rate_target": 0.93,
        "avg_sentiment_drop": 0.15,
    },
    "OP-04": {
        "name": "Loan Status Check",
        "description": "Checks consumer loan application and payoff status.",
        "happy_path_intents": ["loan application status", "check my auto loan", "mortgage status", "loan payoff amount"],
        "gap_intents": ["conditional approval documents", "why did underwriting pause", "manual review timeline"],
        "resolution_rate_target": 0.71,
        "avg_sentiment_drop": 0.35,
    },
    "OP-05": {
        "name": "Dispute a Transaction",
        "description": "Starts debit and credit card transaction disputes.",
        "happy_path_intents": ["dispute a charge", "fraudulent transaction", "charge I don't recognize", "merchant charged twice"],
        "gap_intents": ["subscription trial converted", "merchant promised refund", "pending transaction dispute", "family member used card"],
        "resolution_rate_target": 0.55,
        "avg_sentiment_drop": 0.55,
    },
    "OP-06": {
        "name": "Transfer Funds",
        "description": "Moves money between internal and eligible external accounts.",
        "happy_path_intents": ["transfer funds", "move money to savings", "send money to checking", "schedule a transfer"],
        "gap_intents": ["same day external transfer limit", "cancel transfer after cutoff"],
        "resolution_rate_target": 0.84,
        "avg_sentiment_drop": 0.25,
    },
    "OP-07": {
        "name": "Update Contact Information",
        "description": "Updates phone, email, and mailing address after verification.",
        "happy_path_intents": ["update my address", "change phone number", "new email address", "change mailing address"],
        "gap_intents": ["change phone without old number", "international address format", "mail forwarding temporary address", "business and personal address mismatch"],
        "resolution_rate_target": 0.32,
        "avg_sentiment_drop": 0.6,
    },
    "OP-08": {
        "name": "Report Lost Card",
        "description": "Reports a missing card and starts replacement workflow.",
        "happy_path_intents": ["lost my card", "replace my card", "can't find debit card", "need a new card"],
        "gap_intents": ["lost card while traveling", "rush replacement overseas", "card lost but recurring charges continue"],
        "resolution_rate_target": 0.76,
        "avg_sentiment_drop": 0.3,
    },
}


def _iso(dt: datetime) -> str:
    return dt.isoformat()


def _turns(op: dict, intent: str, failed: bool, status: str, start: datetime) -> list[dict]:
    customer_openers = [
        f"I need help with this: {intent}.",
        f"Can you help me {intent}?",
        f"I'm trying to {intent} and need this handled today.",
    ]
    turns = [{"role": "customer", "text": random.choice(customer_openers), "timestamp": _iso(start)}]

    if not failed:
        turns.extend(
            [
                {"role": "agent", "text": f"I can help with {op['name'].lower()}. I will verify your identity first.", "timestamp": _iso(start + timedelta(seconds=25))},
                {"role": "customer", "text": "That works. I can confirm the security code you sent.", "timestamp": _iso(start + timedelta(seconds=50))},
                {"role": "agent", "text": "Thanks. I verified the account and completed the request. You will receive a confirmation shortly.", "timestamp": _iso(start + timedelta(seconds=75))},
            ]
        )
        return turns

    turns.extend(
        [
            {"role": "agent", "text": f"I can help with the standard {op['name'].lower()} process. Would you like me to continue with that option?", "timestamp": _iso(start + timedelta(seconds=24))},
            {"role": "customer", "text": "No, that is not exactly what I asked for. I need the temporary or exception case handled.", "timestamp": _iso(start + timedelta(seconds=52))},
            {"role": "agent", "text": "I understand. The available procedure only lets me continue with the standard path.", "timestamp": _iso(start + timedelta(seconds=82))},
            {"role": "customer", "text": "This is not solving it. Please get someone who can handle the situation.", "timestamp": _iso(start + timedelta(seconds=115))},
        ]
    )
    if status == "looped":
        turns.append({"role": "agent", "text": "I can help with the standard option. Would you like to proceed?", "timestamp": _iso(start + timedelta(seconds=145))})
    elif status == "escalated":
        turns.append({"role": "agent", "text": "I will transfer you to a specialist who can review this exception.", "timestamp": _iso(start + timedelta(seconds=145))})
    return turns


def generate_conversation(op_id: str | None = None, force_failure: bool = False) -> dict:
    op_id = op_id or random.choice(list(OPERATING_PROCEDURES))
    op = OPERATING_PROCEDURES[op_id]
    failed = force_failure or random.random() > op["resolution_rate_target"]
    intent = random.choice(op["gap_intents"] if failed else op["happy_path_intents"])

    if not failed:
        status = "resolved"
        sentiment = random.choices(["positive", "neutral"], weights=[0.72, 0.28])[0]
    else:
        status_weights = {
            "OP-01": [0.18, 0.62, 0.2, 0.0],
            "OP-05": [0.15, 0.7, 0.15, 0.0],
            "OP-07": [0.12, 0.28, 0.6, 0.0],
        }.get(op_id, [0.18, 0.38, 0.22, 0.22])
        status = random.choices(["failed", "escalated", "looped", "resolved"], weights=status_weights)[0]
        if force_failure and status == "resolved":
            status = "failed"
        sentiment = random.choices(["negative", "neutral"], weights=[0.72, 0.28])[0]

    start = datetime.now(timezone.utc) - timedelta(minutes=random.randint(0, 60 * 24 * 12))
    turns = _turns(op, intent, status != "resolved", status, start)
    return {
        "conversation_id": str(uuid.uuid4()),
        "op_id": op_id,
        "op_name": op["name"],
        "turns": turns,
        "resolution_status": status,
        "turn_count": len(turns),
        "customer_sentiment": sentiment,
        "intent_detected": intent,
        "timestamp": _iso(start),
        "session_duration_seconds": max(70, len(turns) * random.randint(22, 42)),
    }


def generate_batch(n: int = 500, seed: int = 42) -> list[dict]:
    state = random.getstate()
    random.seed(seed)
    op_ids = list(OPERATING_PROCEDURES)
    try:
        return [generate_conversation(op_ids[i % len(op_ids)]) for i in range(n)]
    finally:
        random.setstate(state)
