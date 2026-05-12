from __future__ import annotations

import json
import urllib.error
import urllib.request


API_URL = "http://localhost:8000"


def request(method: str, path: str, payload=None, timeout: int = 120):
    data = None if payload is None else json.dumps(payload, default=str).encode("utf-8")
    req = urllib.request.Request(
        f"{API_URL}{path}",
        data=data,
        method=method,
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            body = response.read().decode("utf-8")
            return json.loads(body) if body else None
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8")
        raise RuntimeError(f"{method} {path} failed: {exc.code} {detail}") from exc
