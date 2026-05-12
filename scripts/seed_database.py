from __future__ import annotations

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "backend"))

from services.simulator import generate_batch  # noqa: E402
from http_utils import API_URL, request  # noqa: E402


def main() -> None:
    print(f"Seeding ConversationIQ API at {API_URL}")
    conversations = generate_batch(500)
    result = request("POST", "/api/conversations/ingest/batch", conversations)
    print(f"Seeded {result['inserted']} conversations")
    print(f"Status mix: {result['by_status']}")


if __name__ == "__main__":
    main()
