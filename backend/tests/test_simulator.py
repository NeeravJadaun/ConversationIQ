from collections import defaultdict

from services.simulator import generate_batch, generate_conversation


def test_generate_conversation_returns_valid_schema():
    convo = generate_conversation("OP-01")
    for key in ["conversation_id", "op_id", "op_name", "turns", "resolution_status", "turn_count", "customer_sentiment", "intent_detected", "timestamp", "session_duration_seconds"]:
        assert key in convo
    assert convo["resolution_status"] in {"resolved", "escalated", "looped", "failed"}
    assert convo["customer_sentiment"] in {"positive", "neutral", "negative"}


def test_generate_batch_correct_count():
    assert len(generate_batch(100)) == 100


def test_failure_distribution_realistic():
    batch = generate_batch(500)
    totals = defaultdict(int)
    failures = defaultdict(int)
    escalations = defaultdict(int)
    for convo in batch:
        totals[convo["op_id"]] += 1
        if convo["resolution_status"] != "resolved":
            failures[convo["op_id"]] += 1
        if convo["resolution_status"] == "escalated":
            escalations[convo["op_id"]] += 1
    assert sum(1 for op_id in totals if failures[op_id] / totals[op_id] > 0.1) >= 3
    assert any(escalations[op_id] / totals[op_id] > 0.3 for op_id in totals)
    assert all(failures[op_id] / totals[op_id] < 1 for op_id in totals)


def test_gap_intents_cause_failures():
    conversations = [generate_conversation("OP-01", force_failure=True) for _ in range(50)]
    assert all(convo["resolution_status"] != "resolved" for convo in conversations)
