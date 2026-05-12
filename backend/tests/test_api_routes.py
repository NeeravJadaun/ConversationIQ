from services.simulator import generate_batch, generate_conversation


def test_ingest_single_conversation(client):
    response = client.post("/api/conversations/ingest", json=generate_conversation("OP-01"))
    assert response.status_code == 201
    assert response.json()["op_id"] == "OP-01"


def test_get_all_procedures(client):
    response = client.get("/api/procedures")
    assert response.status_code == 200
    assert len(response.json()) == 8


def test_get_procedure_detail(client):
    client.post("/api/conversations/ingest", json=generate_conversation("OP-01"))
    response = client.get("/api/procedures/OP-01")
    assert response.status_code == 200
    assert "breakdown" in response.json()


def test_batch_ingest_updates_health_score(client):
    before = next(op for op in client.get("/api/procedures").json() if op["id"] == "OP-05")["health_score"]
    batch = [generate_conversation("OP-05", force_failure=True) for _ in range(20)]
    client.post("/api/conversations/ingest/batch", json=batch)
    after = next(op for op in client.get("/api/procedures").json() if op["id"] == "OP-05")["health_score"]
    assert after <= before or after < 80


def test_websocket_connection(client):
    with client.websocket_connect("/ws/live") as websocket:
        websocket.receive_json()
        client.post("/api/conversations/ingest", json=generate_conversation("OP-01"))
        message = websocket.receive_json()
        assert message["type"] == "new_conversation"


def test_generate_recommendation(client):
    client.post("/api/conversations/ingest/batch", json=generate_batch(20))
    response = client.post("/api/recommendations/generate", json={"op_id": "OP-01"})
    assert response.status_code == 200
    body = response.json()
    assert body["priority"] in {"high", "medium", "low"}
    assert body["recommendation_text"]
