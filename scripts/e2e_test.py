from __future__ import annotations

import base64
import hashlib
import json
import os
import pathlib
import socket
import struct
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "backend"))

from http_utils import request  # noqa: E402
from services.simulator import generate_batch, generate_conversation  # noqa: E402


def _read_ws_frame(sock: socket.socket) -> str:
    first = sock.recv(2)
    if len(first) < 2:
        return ""
    length = first[1] & 127
    if length == 126:
        length = struct.unpack(">H", sock.recv(2))[0]
    elif length == 127:
        length = struct.unpack(">Q", sock.recv(8))[0]
    payload = sock.recv(length)
    return payload.decode("utf-8")


def _ws_connect() -> socket.socket:
    sock = socket.create_connection(("localhost", 8000), timeout=5)
    key = base64.b64encode(os.urandom(16)).decode("ascii")
    request_text = (
        "GET /ws/live HTTP/1.1\r\n"
        "Host: localhost:8000\r\n"
        "Upgrade: websocket\r\n"
        "Connection: Upgrade\r\n"
        f"Sec-WebSocket-Key: {key}\r\n"
        "Sec-WebSocket-Version: 13\r\n\r\n"
    )
    sock.sendall(request_text.encode("ascii"))
    response = sock.recv(1024)
    if b"101 Switching Protocols" not in response:
        raise RuntimeError("WebSocket upgrade failed")
    sock.settimeout(5)
    return sock


def _status(score: float) -> str:
    if score >= 80:
        return "HEALTHY"
    if score >= 60:
        return "WARNING"
    return "CRITICAL"


def main() -> None:
    print("=== ConversationIQ E2E Test ===")

    conversations = generate_batch(500)
    print("✅ Step 1 passed: Generated 500 conversations")

    start = time.perf_counter()
    result = request("POST", "/api/conversations/ingest/batch", conversations)
    elapsed_ms = (time.perf_counter() - start) * 1000
    assert result["inserted"] == 500
    print(f"✅ Step 2 passed: Ingested 500 conversations (avg {elapsed_ms / 5:.0f}ms/batch)")

    procedures = request("GET", "/api/procedures")
    assert len(procedures) == 8 and all(op["conversation_count"] > 0 for op in procedures)
    print("✅ Step 3 passed: All 8 OPs scored")

    weak = [op for op in procedures if op["health_score"] < 80]
    assert len(weak) >= 3
    weak_text = ", ".join(f"{op['id']} ({op['health_score']})" for op in weak[:3])
    print(f"✅ Step 4 passed: {weak_text} in warning/critical")

    clusters = request("POST", "/api/clusters/recompute")
    print("✅ Step 5 passed: Clustering complete")
    assert len(clusters) >= 5
    print(f"✅ Step 6 passed: {len(clusters)} clusters found")

    recs = []
    for op in sorted(procedures, key=lambda item: item["health_score"])[:2]:
        recs.append(request("POST", "/api/recommendations/generate", {"op_id": op["id"]}))
    print("✅ Step 7 passed: Recommendations generated")
    assert all(rec["recommendation_text"] and rec["priority"] in {"high", "medium", "low"} for rec in recs)
    print("✅ Step 8 passed: Recommendations have valid content")

    sock = _ws_connect()
    _read_ws_frame(sock)
    request("POST", "/api/conversations/ingest", generate_conversation("OP-01", force_failure=True))
    pushed = _read_ws_frame(sock)
    sock.close()
    assert "new_conversation" in pushed
    print("✅ Step 9 passed: WebSocket push received")

    procedures = request("GET", "/api/procedures")
    print("✅ Step 10: Health Score Summary:")
    for op in procedures:
        print(f"   {op['id']} {op['name']:<28} {op['health_score']:>5.1f}  {_status(op['health_score'])}")


if __name__ == "__main__":
    main()
