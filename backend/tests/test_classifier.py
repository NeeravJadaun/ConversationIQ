from services.classifier import classify_conversation
from services.simulator import generate_conversation


def test_mock_classifier_returns_correct_schema():
    result = classify_conversation(generate_conversation("OP-01"))
    assert set(result) == {"intent_detected", "op_handled_correctly", "failure_reason", "suggested_intent_label"}


def test_happy_path_classified_correct():
    convo = generate_conversation("OP-01")
    convo["resolution_status"] = "resolved"
    convo["intent_detected"] = "lock my card"
    convo["turns"][0]["text"] = "I need to lock my card."
    assert classify_conversation(convo)["op_handled_correctly"] is True


def test_gap_intent_classified_failed():
    convo = generate_conversation("OP-01", force_failure=True)
    convo["intent_detected"] = "put my card on hold"
    convo["turns"][0]["text"] = "I need to put my card on hold while I travel."
    assert classify_conversation(convo)["op_handled_correctly"] is False
